"""Prepared reload checkpoints, observed through production RAF/UI at native HTTP.
No manual frames, parked renderer, synthetic Storage or replacement input handler.
"""
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime, timezone
import hashlib, json, os, sys
from playwright.sync_api import sync_playwright
from qa_support import launch_options
from native_support import game_origin

R = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(R))
from tools.qa.reload_contract import pause_errors, completion_errors
from tools.qa.reload_progress import write_progress

O = R / 'qa/v020/reload'
O.mkdir(parents=True, exist_ok=True)
checks, errors, requests, cases, captures = [], [], [], [], []
info = {'nativeStorage': False}
expected = json.loads((R / 'build-info.json').read_text())
SETTINGS = "localStorage.setItem('distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false}))"
NATIVE = "localStorage instanceof Storage && /native code/.test(Storage.prototype.setItem.toString())"
# These observers only delegate and record. In particular, neither changes RAF,
# the simulation clock, event arguments, render output or input ownership.
OBSERVE = """() => {
 const a=DC_APP,s=a.sim,r=a.renderer,q=window.DC_RELOAD_QA={draws:0,completed:0};
 const emit=s.emit;
 s.emit=function(...args){if(args[0]==='sound'&&args[1]==='reloadDone')q.completed++;return emit.apply(this,args);};
 const draw=r.drawEquipment;
 r.drawEquipment=function(sim,m,e){const result=draw.call(this,sim,m,e);q.draws++;
  q.rendered={selected:e.selected,magazine:JSON.parse(JSON.stringify(m.magazine)),
   instances:Object.fromEntries(this.equipmentMeshes.get(e.selected).map(p=>[p.key,this.dynamic[p.key].length/16]))};return result;};
 q.snapshot=()=>{const e=s.equipment;return {mode:a.mode,frame:a.frameCount,time:s.time,
  selected:e.selected,remaining:e.reloading,reloadId:e.reloadId,ammo:DC.Equipment.snapshot(e).ammo,
  shots:e.shots,charge:e.charge,trigger:e.trigger,aiming:e.aiming,
  inputs:!!(a.weaponKeys.size||a.weaponPointers.size||a.fireQueued||a.aimToggle),
  completed:q.completed,glError:r.gl.getError(),frozen:!!r.frozenHandling,
  rendered:q.rendered,draws:q.draws};};
} """
PREPARE = """c => {
 const a=DC_APP,s=a.sim,r=a.renderer,q=DC_RELOAD_QA,w=DC.Equipment.get(c.item);
 if(a.mode!=='pause')throw Error('Prepare only a paused scenario');
 a.clearWeaponInput();a.autoSave=0;s.equipment.reloading=0;s.equipment.reloadId=null;
 s.equipWeapon(c.item);DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;
 Object.assign(s.equipment,{aimWeight:1,pitch:0,recoil:0,cooldown:0});
 Object.assign(s.equipment.ammo[c.item],{loaded:Math.max(0,w.mag-2),reserve:c.fraction<.5?5:1});
 s.free=true;s.wanted=s.heat=0;s.peds.forEach(n=>n.hidden=true);
 s.cars.forEach(car=>Object.assign(car,{x:5000,z:5000,driver:null}));s.dynamics.props=[];
 Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0,crouch:0});
 r.motionTracker.clear();r.motionScene=s;r.camera.yaw=0;r.camera.weaponPitch=0;
 r.camera.eye=[5.6,1.54,36.9];r.camera.target=[4.015,1.4,36.25];
 q.completed=0;
 if(c.reload){if(!s.reloadWeapon())throw Error('Prepared reload did not start');s.equipment.reloading=w.reload*(1-c.fraction);}
 const draw=q.draws;a.renderDirty=true;
 return {capacity:w.mag,duration:w.reload,draw,seed:s.world?.seed||a.world.seed};
} """


def ck(name, faults):
    """One fixed-contract check per scenario; retain detailed failure evidence."""
    checks.append({'name': name, 'pass': not faults, 'failures': faults})
    print(('FAIL ' if faults else 'PASS ') + name, flush=True)
    # A killed producer cannot execute finally. Preserve its completed cases in
    # a separate journal, never the canonical report required for acceptance.
    write_progress(O.parent / 'reload.progress.json', {
        'sha256': expected['htmlSha256'], 'runId': os.environ.get('DC_QA_RUN_ID'),
        'expectedChecks': 31, 'checks': checks, 'cases': cases, 'captures': captures,
        'errors': errors, 'requests': requests, 'physicalGpu': False,
        'nativePersistence': False, 'preparedWorld': True, 'preparedTimers': True,
        'clockMode': 'production RAF and simulation',
        'observedUtc': datetime.now(timezone.utc).isoformat(), **info})
    assert not faults, name + ': ' + ', '.join(faults)


def snapshot(p):
    return p.evaluate('DC_RELOAD_QA.snapshot()')


def draw_ready(p, after):
    p.wait_for_function('n=>DC_RELOAD_QA.draws>n&&!DC_APP.renderDirty', arg=after)


def capture(p, name):
    filename = name + '.png'
    p.screenshot(path=str(O / filename))
    captures.append(filename)


def prepare(p, item, fraction=0, reload=True):
    config = p.evaluate(PREPARE, {'item': item, 'fraction': fraction, 'reload': reload})
    draw_ready(p, config['draw'])
    return config, snapshot(p)


def pause(p):
    if p.evaluate('DC_APP.mode') == 'play':
        p.keyboard.press('Escape')
    p.wait_for_function('DC_APP.mode==="pause"')


def open_paused(p):
    before = snapshot(p)
    p.click('#pauseArsenal')
    p.wait_for_function('DC_APP.mode==="arsenal"')
    draw_ready(p, before['draws'])
    return snapshot(p)


def wait_live(p, state):
    p.wait_for_function('n=>DC_APP.frameCount>=n+3', arg=state['frame'])


def wait_complete(p, start):
    p.wait_for_function('t=>DC_APP.mode==="play"&&DC_APP.sim.time>=t&&DC_APP.sim.equipment.reloading===0',
                        arg=start['time'] + start['remaining'] + .12)
    return snapshot(p)


def check_same(before, after, keys):
    return [key + ' changed' for key in keys if before[key] != after[key]]


browser = None
try:
    assert os.environ.get('DC_QA_ORIGIN') == 'http', 'This suite requires the HTTP contract'
    with game_origin(R) as origin, sync_playwright() as pw:
        browser = pw.chromium.launch(**launch_options())
        context = browser.new_context(viewport={'width': 1100, 'height': 760})
        context.add_init_script(SETTINGS)
        p = context.new_page()
        p.set_default_timeout(45000)
        p.on('pageerror', lambda error: errors.append(str(error)))
        p.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        p.on('request', lambda request: requests.append(request.url) if request.url.startswith(('http:', 'https:')) and urlsplit(request.url).netloc != urlsplit(origin).netloc else None)
        response = p.goto(origin, wait_until='domcontentloaded', timeout=120000)
        p.wait_for_function('!!window.DC_APP', timeout=120000)
        p.evaluate('DC_APP.renderer.humanReady')
        info.update(browser=browser.version, viewport={'width': 1100, 'height': 760}, originMode='HTTP loopback', nativeStorage=p.evaluate(NATIVE))
        ck('Reload suite serves the canonical HTML over HTTP', [] if response.status == 200 and hashlib.sha256(response.body()).hexdigest() == expected['htmlSha256'] else ['HTML mismatch'])
        ck('Reload suite retains native Web Storage', [] if info['nativeStorage'] else ['Storage was replaced'])
        p.click('#start')
        p.fill('#characterName', 'Recarga QA')
        p.fill('#newSaveName', 'Recargas nativas aisladas')
        p.click('#commitCreator')
        p.click('#dismissTutorial')
        pause(p)
        saved = p.evaluate('DC_APP.getStore().raw()')
        p.evaluate(OBSERVE)

        for item in ('rifle', 'revolver', 'shotgun'):
            for fraction in (0, .14, .30, .52, .72, .90, .999):
                name = f'{item}-pause-{fraction:.3f}'
                config, start = prepare(p, item, fraction)
                before = open_paused(p)
                p.keyboard.down('j')  # ignored by the modal's actual capture handler
                wait_live(p, before)
                capture(p, name)
                after = snapshot(p)
                faults = pause_errors(before, after)
                faults += check_same(start, before, ('time', 'remaining', 'ammo', 'reloadId', 'shots'))
                p.keyboard.press('Escape')
                p.wait_for_function('DC_APP.mode==="pause"')
                closed = snapshot(p)
                faults += check_same(start, closed, ('time', 'remaining', 'ammo', 'reloadId', 'shots'))
                if closed['frozen'] or closed['inputs'] or closed['charge'] or closed['trigger']:
                    faults.append('selector close did not cancel safely')
                p.click('#resume')
                final = wait_complete(p, start)
                faults += completion_errors(start, final, config['capacity'])
                p.keyboard.up('j')
                cases.append({'name': name, 'fraction': fraction, 'seed': config['seed'], 'start': start, 'before': before, 'after': after, 'closed': closed, 'final': final, 'failures': faults})
                ck(name + ' freezes and completes once', faults)
                pause(p)

        for item in ('rifle', 'revolver', 'shotgun'):
            name = item + '-keyboard-return'
            config, initial = prepare(p, item, reload=False)
            p.click('#resume')
            p.keyboard.press('l')
            p.wait_for_function('DC_APP.sim.equipment.reloading>0')
            p.keyboard.down('j')
            p.keyboard.press('Tab')
            p.wait_for_function('DC_APP.mode==="arsenal"&&!DC_APP.renderDirty')
            before = snapshot(p)
            wait_live(p, before)
            capture(p, name)
            after = snapshot(p)
            faults = pause_errors(before, after)
            if before['remaining'] <= 0 or before['ammo'] != initial['ammo']:
                faults.append('keyboard checkpoint missed the active reload')
            p.keyboard.press('Escape')
            final = wait_complete(p, before)
            faults += completion_errors(before, final, config['capacity'])
            p.keyboard.up('j')
            p.keyboard.press('j')
            p.wait_for_function('n=>DC_APP.sim.equipment.shots>n', arg=final['shots'])
            fresh = snapshot(p)
            if fresh['shots'] != final['shots'] + 1 or fresh['ammo'][item]['loaded'] != final['ammo'][item]['loaded'] - 1:
                faults.append('fresh key press did not produce exactly one shot')
            cases.append({'name': name, 'observedFraction': 1 - before['remaining'] / config['duration'], 'before': before, 'after': after, 'final': final, 'fresh': fresh, 'failures': faults})
            ck(name + ' blocks held input but accepts a new press', faults)
            pause(p)

        for target in ('binoculars', 'gauss'):
            name = 'switch-rifle-to-' + target
            config, start = prepare(p, 'rifle', .52)
            open_paused(p)
            p.keyboard.down('j')
            p.click('[data-weapon="' + target + '"]')
            p.click('#commitEquipment')
            p.wait_for_function('DC_APP.mode==="pause"')
            p.click('#resume')
            final = wait_complete(p, start)
            faults = completion_errors(start, final, config['capacity'], selected=target)
            capture(p, name)
            p.keyboard.up('j')
            pause(p)
            open_paused(p)
            p.click('[data-weapon="rifle"]')
            p.click('#commitEquipment')
            p.click('#resume')
            p.wait_for_function('t=>DC_APP.sim.time>t', arg=final['time'] + config['duration'] + .12)
            returned = snapshot(p)
            faults += completion_errors(start, returned, config['capacity'], selected='rifle')
            cases.append({'name': name, 'start': start, 'final': final, 'returned': returned, 'failures': faults})
            ck(name + ' discards reload without a deferred transfer', faults)
            pause(p)

        config, start = prepare(p, 'gauss', reload=False)
        p.click('#resume')
        p.keyboard.down('j')
        p.wait_for_function('DC_APP.sim.equipment.charge>.3')
        charged = snapshot(p)
        p.keyboard.press('Tab')
        p.wait_for_function('DC_APP.mode==="arsenal"&&!DC_APP.renderDirty')
        before = snapshot(p)
        wait_live(p, before)
        capture(p, 'gauss-cancel')
        after = snapshot(p)
        faults = pause_errors(before, after)
        p.keyboard.up('j')
        p.keyboard.press('Escape')
        p.wait_for_function('t=>DC_APP.sim.time>t', arg=before['time'] + 1.7)
        final = snapshot(p)
        if final['shots'] != start['shots'] or final['ammo'] != start['ammo'] or final['charge'] or final['trigger'] or final['inputs']:
            faults.append('cancelled Gauss charge fired or resumed')
        cases.append({'name': 'gauss-cancel', 'charged': charged, 'before': before, 'after': after, 'final': final, 'failures': faults})
        ck('Gauss charge is cancelled through the selector before release', faults)
        pause(p)
        ck('Reload scenarios never overwrite the saved native catalogue', [] if p.evaluate('DC_APP.getStore().raw()') == saved else ['saved catalogue changed'])
        ck('No runtime errors, graphics errors or external requests', [] if not errors and not requests and p.evaluate('DC_APP.renderer.gl.getError()') == 0 else ['unexpected error or request'])
        browser.close()
        browser = None
except Exception as error:
    errors.append(str(error))
    raise
finally:
    if browser:
        try:
            browser.close()
        except Exception:
            pass
    report = {'sha256': hashlib.sha256((R / 'index.html').read_bytes()).hexdigest(),
              'runId': os.environ.get('DC_QA_RUN_ID'), 'checks': checks, 'errors': errors,
              'requests': requests, 'cases': cases, 'captures': captures, 'build': expected,
              'physicalGpu': False, 'nativePersistence': False, 'preparedWorld': True,
              'preparedTimers': True, 'clockMode': 'production RAF and simulation',
              'note': 'Synthetic saved game, prepared scenes and checkpoints. Inputs use production browser handlers. This is not an uninterrupted playthrough, physical-input/Pointer Lock certification, restart-persistence test or physical GPU benchmark.',
              'finishedUtc': datetime.now(timezone.utc).isoformat(), **info}
    (O.parent / 'reload.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
