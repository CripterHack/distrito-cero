"""CONTACT-05: real selection keys, canonical renderer and explicit visual handoff.
Prepared scene and 60 Hz time, Storage fixture. Not a human playtest or GPU FPS.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, html, json, math, os, struct, sys
from playwright.sync_api import sync_playwright
from qa_support import launch_options

R=Path(__file__).resolve().parents[1]
O=R/'qa/v020/handoff'
checks,errors,requests,cases,actions=[],[],[],[],[]
sha=hashlib.sha256((R/'index.html').read_bytes()).hexdigest()
FIX="""(()=>{window.qaLongarmStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>qaLongarmStore.get(k)||null,setItem:(k,v)=>qaLongarmStore.set(k,String(v)),removeItem:k=>qaLongarmStore.delete(k)}});})();"""

def ck(name,ok):
    checks.append({'name':name,'pass':bool(ok)})
    print(('PASS ' if ok else 'FAIL ')+name,flush=True)

def distance(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))

def capture(page,name,record):
    path=O/'images'/(name+'.png');page.screenshot(path=str(path),timeout=120000)
    raw=path.read_bytes()
    if raw[:8]!=b'\x89PNG\r\n\x1a\n' or struct.unpack('>II',raw[16:24])!=(820,680):
        raise ValueError('Invalid handoff screenshot')
    record.update(image='images/'+path.name,imageSha256=hashlib.sha256(raw).hexdigest())

info={};status='failed'
try:
    assert os.environ.get('DC_QA_ORIGIN','fixture')=='fixture'
    O.mkdir(parents=True,exist_ok=False);(O/'images').mkdir()
    with sync_playwright() as pw:
        browser=pw.chromium.launch(**launch_options())
        try:
            page=browser.new_page(viewport={'width':820,'height':680});page.set_default_timeout(45000)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
            page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
            page.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIX,1),timeout=120000)
            page.wait_for_function('!!window.DC_APP',timeout=120000);page.evaluate('DC_APP.renderer.humanReady')
            ck('Canonical renderer decodes embedded skin maps',page.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3'))
            page.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
            for helper in ('manual_frames.js','sidearm_sight.js','stock_clearance.js','longarm_contact.js','longarm_stage.js'):
                page.add_script_tag(content=(R/'tools/qa'/helper).read_text())
            info={'browser':browser.version,**page.evaluate('DC_LONGARM_STAGE.init()')}
            pairs=[('rifle','smg'),('smg','rifle'),('shotgun','sniper'),('sniper','shotgun')]
            for start,target in pairs:
                before=page.evaluate('s=>DC_LONGARM_STAGE.beginSwitch(s)',start)
                capture(page,start+'-'+target+'-before',before)
                key=page.evaluate('id=>DC.Equipment.get(id).key',target)
                page.locator('body').click(position={'x':2,'y':2})
                page.keyboard.press('Digit'+key)
                first=page.evaluate('DC_LONGARM_STAGE.switchObservation()')
                label=page.evaluate('document.getElementById("weaponMode").textContent')
                rows=[first];capture(page,start+'-'+target+'-00',first)
                for frame in range(1,31):
                    row=page.evaluate('DC_LONGARM_STAGE.tickSwitch()');rows.append(row)
                    # Every rendered instant for one clip; keyframes for the rest.
                    if start=='rifle' or frame in (3,6,12,18,24,30):
                        capture(page,start+'-'+target+f'-{frame:02}',row)
                jumps=[max(distance(a['palms'][k],b['palms'][k]) for k in (0,1)) for a,b in zip([before]+rows,rows)]
                ck(start+' -> '+target+' uses the real selection key and clears firing inputs',first['item']==target and not first['trigger'] and all(r['ammo']==before['ammo'] and r['shots']==before['shots'] for r in rows))
                ck(start+' -> '+target+' keeps rendered palms continuous and returns to the existing mount',jumps[0]<1e-4 and max(jumps)<.030 and rows[-1]['handoff'] is None and rows[-1]['displayItem']==target and rows[-1]['origin']==rows[-1]['gameplayOrigin'] and 'CAMBIANDO' in label)
                ck(start+' -> '+target+' preserves sampled skin clearance and bone reach',all(r['actors']>=1 and max(r['palmErrors'].values())<.012 and max(r['segmentErrors'].values())<1e-6 and min(r['clearance'][p]['distance'] for p in ('face','jacket'))>=-.002 for r in rows))
                cases.append({'from':start,'to':target,'before':before,'frames':rows,'maximumPalmStep':max(jumps),'initialPalmStep':jumps[0],'label':label})
                page.evaluate('DC_LONGARM_STAGE.endSwitch()')
            # The new selection must never fire with the previous model/muzzle.
            page.evaluate('DC_LONGARM_STAGE.beginSwitch("rifle")');key=page.evaluate('DC.Equipment.get("sniper").key');page.keyboard.press('Digit'+key)
            first=page.evaluate('DC_LONGARM_STAGE.switchObservation()');page.keyboard.down('KeyJ')
            fired=page.evaluate('DC_LONGARM_STAGE.tickSwitch()');page.keyboard.up('KeyJ')
            actions.append({'action':'fire','before':first,'after':fired})
            ck('Immediate firing takes precedence over cosmetic transfer without delaying the shot',fired['shots']==first['shots']+1 and fired['displayItem']=='sniper' and fired['origin']==fired['gameplayOrigin'] and fired['handoff'] is None and 'CAMBIANDO' not in fired['hudMode'])
            page.evaluate('DC_LONGARM_STAGE.endSwitch()')
            ck('Prepared keyboard scenes leave the original simulation and Storage intact',page.evaluate('DC_LONGARM_STAGE.pristine()'))
            ck('No renderer exceptions or external requests',not errors and not requests)
            status='passed' if all(c['pass'] for c in checks) else 'failed'
        finally:
            browser.close()
except Exception as exc:
    errors.append(str(exc));print('ERROR',repr(exc),flush=True)
finally:
    O.parent.mkdir(parents=True,exist_ok=True)
    report={'suite':'handoff','status':status,'sha256':sha,'at':datetime.now(timezone.utc).isoformat(),'info':info,'checks':checks,'errors':errors,'requests':requests,'cases':cases,'actions':actions,'nativeStorage':False,'physicalGpu':False,'scope':'Four docked family switches from settled aim, one firing interruption; 60 Hz prepared simulation, vertex samples, no collision or artistic guarantee.'}
    (O.parent/'equipment-handoff.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if O.exists():
        figures=[]
        for c in cases:
            for i,row in enumerate([c['before']]+c['frames']):
                if 'image' in row: figures.append('<figure><img loading="lazy" src="'+html.escape(row['image'])+'"><figcaption>'+html.escape(f'{c["from"]} → {c["to"]}, frame {i-1}, visible {row["displayItem"]}')+'</figcaption></figure>')
        (O/'index.html').write_text('<!doctype html><meta charset="utf-8"><title>Equipment handoff evidence</title><style>body{font:16px system-ui}main{display:grid;grid-template-columns:repeat(2,minmax(0,1fr))}img{max-width:100%}</style><h1>Canonical handoff evidence</h1><p>Prepared 60 Hz scene. Not physical FPS or a human playtest.</p><main>'+''.join(figures)+'</main>')
    print('RESULT',status,len(checks),flush=True)
if status!='passed':sys.exit(1)
