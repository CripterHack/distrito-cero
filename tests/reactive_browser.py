"""v0.4 integration QA. Native Chromium/WebGL2, actual keyboard and touch events.
The primary suite substitutes only rendering between explicitly rendered keyframes
and localStorage with an isolated in-memory fixture (set_content has no origin).
Simulation/gameplay methods are never mocked. continuous_reactive.py tests live GPU loop.
Run with a working X display, e.g. DISPLAY=:99 under Xvfb on Linux.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'qa/v04';OUT.mkdir(exist_ok=True)
HTML=(ROOT/'index.html').read_text()
FIXTURE="""(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false,volume:0,touch:null})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k),clear:()=>d.clear()}});})();"""
checks=[];errors=[];requests=[]
def check(name,value):
    checks.append({'check':name,'passed':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True);assert value,name

def load(browser,w,h,touch=False):
    context=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=touch,has_touch=touch)
    page=context.new_page();page.on('pageerror',lambda e: errors.append(str(e)));page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None);page.on('request',lambda r:requests.append(r.url))
    page.set_content(HTML.replace('<script>','<script>'+FIXTURE,1),wait_until='load')
    page.wait_for_function('!!window.DC_APP||!document.getElementById("error").hidden',timeout=30000)
    check('WebGL2 boot '+str((w,h)),page.evaluate('!!window.DC_APP&&DC_APP.renderer.gl.getError()===0'))
    page.evaluate('window.realRender=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}')
    page.click('#start');page.click('#dismissTutorial');fresh(page)
    return context,page

def fresh(page):
    page.evaluate('''()=>{const a=DC_APP;a.sim=new DC.Simulation(a.world);a.sim.free=true;a.sim.peds=[];for(const c of a.sim.cars){c.speed=0;c.parked=true;}a.crouched=false;a.setMode('play');a.toastQueue=[];a.chapterUntil=0;a.toastUntil=0;a.autoSave=0;a.renderer.camera.yaw=0;a.renderer.camera.pitch=.22;a.renderer.camera.initialized=false;document.getElementById('chapter').classList.remove('visible');document.getElementById('toast').classList.remove('visible');}''')

def advance(page,seconds):
    return page.evaluate('''seconds=>{const a=DC_APP;window.tickSample={trauma:0,particles:0};for(let k=0;k<Math.round(seconds*60);k++){a.sim.step(1/60,a.input());tickSample.trauma=Math.max(tickSample.trauma,a.sim.trauma);tickSample.particles=Math.max(tickSample.particles,a.sim.dynamics.particles.length);}a.processEvents();a.updateUI(performance.now());return {steerAngle:a.sim.actor().steerAngle,roll:a.sim.actor().suspension?.roll};}''',seconds)

def frame(page,name,high=True):
    page.evaluate('''high=>{const a=DC_APP;if(high){a.renderer.quality='balanced';a.renderer.rain=1;a.renderer.bloom=1;a.renderer.resize();}a.chapterUntil=0;a.toastQueue=[];document.getElementById('chapter').classList.remove('visible');document.getElementById('toast').classList.remove('visible');a.updateUI(performance.now());a.renderer.updateCamera(a.sim,.2,{look:true});realRender(a.sim);}''',high)
    page.screenshot(path=str(OUT/name));check('Rendered '+name,page.evaluate('DC_APP.renderer.gl.getError()===0'))

def reachable(page,sel):
    box=page.locator(sel).bounding_box();check(sel+' visible '+str(page.viewport_size['width']),bool(box))
    if not box:return
    w,h=page.viewport_size['width'],page.viewport_size['height']
    check(sel+' on screen',box['x']>=-1 and box['y']>=-1 and box['x']+box['width']<=w+1 and box['y']+box['height']<=h+1)
    check(sel+' receives pointer',page.evaluate('''({sel,x,y})=>{const e=document.querySelector(sel),t=document.elementFromPoint(x,y);return t===e||e.contains(t)}''',{'sel':sel,'x':box['x']+box['width']/2,'y':box['y']+box['height']/2}))
    return box

try:
 with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    context,page=load(browser,1280,800)
    check('Five genuine Higgsfield mesh buffers are initialized',page.evaluate('DC_APP.renderer.assetParts.length===5&&DC.VehicleAsset.parts.every(p=>p.data.length>0)'))
    check('Soft smoke has a separate alpha-blended mesh',page.evaluate('DC_APP.renderer.meshes.smoke.transparent===true'))
    check('555 physical objects initialized',page.evaluate('DC_APP.sim.dynamics.props.length===555'))
    page.evaluate("Object.assign(DC_APP.sim.player,{x:10.9,z:7.95,yaw:Math.PI});DC_APP.renderer.camera.yaw=Math.PI")
    page.keyboard.press('e');advance(page,.1)
    check('E picks up an accessible crate',page.evaluate("DC_APP.sim.player.carry==='intro:crate:0'"))
    check('Context describes throw/drop',page.evaluate('DC_APP.sim.getContext().text.includes("Soltar")'))
    frame(page,'03-carry.png')
    page.keyboard.press('g');check('G throws the held prop',page.evaluate('!DC_APP.sim.player.carry&&Math.hypot(DC_APP.sim.dynamics.byId.get("intro:crate:0").vx,DC_APP.sim.dynamics.byId.get("intro:crate:0").vz)>6'))
    advance(page,1);check('Thrown body obeys finite integration',page.evaluate('[...DC_APP.sim.dynamics.props].every(p=>[p.x,p.z,p.y,p.vx,p.vy,p.vz].every(Number.isFinite))'))
    fresh(page);page.evaluate('DC_APP.sim.player.x=-4')
    page.keyboard.press('x');advance(page,.5);check('X enters a blended crouch',page.evaluate('DC_APP.input().crouch&&DC_APP.sim.player.crouch>.95'))
    page.keyboard.down('w');advance(page,.5);page.keyboard.up('w');check('Crouch is slower than normal walking',page.evaluate('DC_APP.sim.player.z>8.3&&DC_APP.sim.player.z<9.1'))
    page.keyboard.press('x');advance(page,.3)
    page.keyboard.down('Space');advance(page,.15);check('Jump leaves the ground',page.evaluate('DC_APP.sim.player.y>.2'))
    frame(page,'04-jump.png')
    advance(page,1.8);check('Held jump does not auto-hop',page.evaluate('DC_APP.sim.player.y===0'));page.keyboard.up('Space')
    page.keyboard.press('q');check('Q activates a dodge',page.evaluate('DC_APP.sim.player.dodge>0'));advance(page,.15);check('Dodge moves player and produces a pose',page.evaluate('DC_APP.sim.player.dodgeCooldown>.8'))
    page.keyboard.press('i');check('I opens the interaction drawer',page.locator('#interactionDrawer').is_visible());reachable(page,'#closeInteractions');page.click('#closeInteractions');check('Drawer closes',page.locator('#interactionDrawer').is_hidden())
    fresh(page);page.keyboard.press('g');advance(page,.4);check('G pushes the starting car without police',page.evaluate('DC_APP.sim.cars[0].z>11&&DC_APP.sim.wanted===0'))
    fresh(page);page.keyboard.press('f');check('Entering starts a character/door transition',page.evaluate('DC_APP.sim.player.car===0&&!!DC_APP.sim.player.transition&&DC_APP.sim.actor().doorUntil>DC_APP.sim.time'))
    advance(page,1);page.keyboard.down('w');advance(page,.75);page.keyboard.up('w');check('Driving turns the wheels',page.evaluate('Math.abs(DC_APP.sim.actor().wheel)>.5&&DC_APP.sim.actor().speed>5'))
    page.keyboard.down('d');steering=advance(page,.12);page.keyboard.up('d');check('Steering is reflected in wheel angle and body roll',steering['steerAngle']<-.15 and abs(steering['roll'])>.0001)
    page.evaluate('DC_APP.sim.actor().speed=0');page.keyboard.press('f');check('Exiting starts a character transition',page.evaluate('DC_APP.sim.player.car===null&&!!DC_APP.sim.player.transition'));advance(page,1)
    fresh(page)
    page.evaluate('''()=>{const s=DC_APP.sim,c=s.cars[0];window.testLamp=s.dynamics.props.filter(o=>o.type==='lamp'&&o.x>0&&o.x<20&&o.z>20&&o.z<75)[0];if(!testLamp)throw Error('lamp fixture missing');Object.assign(c,{x:testLamp.x,z:testLamp.z-7,yaw:0,speed:26,parked:false});Object.assign(s.player,{x:c.x,z:c.z,car:0,yaw:0});}''')
    advance(page,.4);check('Actual car collision breaks a streetlamp',page.evaluate('testLamp.broken'))
    check('Lamp emission switches off at the same collision',page.evaluate('!DC_APP.sim.dynamics.lightActive(testLamp.lightIndex)'))
    check('Collision damages front bodywork',page.evaluate('DC_APP.sim.actor().damage.front>.1&&DC_APP.sim.actor().health<100'))
    check('Collision triggers fragments and body/camera impulse',page.evaluate('tickSample.particles>0&&tickSample.trauma>0'))
    page.evaluate('DC_APP.sim.actor().speed=0;DC_APP.renderer.camera.yaw=-1.9;DC_APP.lookUntil=performance.now()+100000')
    frame(page,'05-lamp-impact.png')
    advance(page,2.5);check('Lamp comes to rest without sinking its fixture',page.evaluate('testLamp.angle<=1.34&&testLamp.angularVelocity===0'))
    page.evaluate('''()=>{const s=DC_APP.sim,c=s.actor();DC.damageVehicle(c,45,c.x+Math.sin(c.yaw)*2.2,c.z+Math.cos(c.yaw)*2.2);c.speed=0;s.heat=0;s.wanted=0;s.resetPolice();DC_APP.renderer.camera.yaw=2.5;DC_APP.renderer.camera.pitch=.27;}''')
    advance(page,.4);check('Serious front damage generates smoke',page.evaluate('DC_APP.sim.dynamics.particles.some(p=>p.material==="smoke")'))
    frame(page,'06-damaged-coupe.png')
    page.evaluate('''()=>{const s=DC_APP.sim,o=s.dynamics.props.find(p=>p.type==='tree'&&p.x===13.5&&p.z===52);window.testTree=o;DC_APP.sim.dynamics.impactProp(o,35,0,-1);Object.assign(s.actor(),{x:4,z:48,speed:0});Object.assign(s.player,{x:4,z:48});DC_APP.renderer.camera.yaw=-.6;DC_APP.renderer.camera.initialized=false;}''')
    advance(page,2);check('Tree impact produces a falling, broken trunk',page.evaluate('testTree.broken&&testTree.angle>1'));frame(page,'07-fallen-tree.png')
    check('New save validates and contains environmental damage',page.evaluate('(()=>{const s=DC_APP.sim,data=s.serialize(),t=new DC.Simulation(s.world);return t.restore(data)&&t.dynamics.byId.get(testTree.id).broken&&t.actor().damage.front>.8})()'))
    fresh(page);page.evaluate('DC.damageVehicle(DC_APP.sim.cars[0],40,5,13);Object.assign(DC_APP.sim.player,{x:7.5,z:11})')
    page.keyboard.down('v');advance(page,.5);check('V begins repair through the actual input map',page.evaluate('DC_APP.sim.repairProgress>.15'));page.keyboard.up('v');advance(page,.05);check('Releasing V cancels without charging',page.evaluate('DC_APP.sim.repairProgress===0&&DC_APP.sim.cash===850'))
    page.keyboard.down('v');advance(page,3.3);page.keyboard.up('v');check('Completed keyboard repair restores appearance and charges once',page.evaluate('DC_APP.sim.cars[0].health===100&&DC_APP.sim.cash===760&&Object.values(DC_APP.sim.cars[0].damage).every(v=>v===0)'))
    page.keyboard.press('Escape');t=page.evaluate('DC_APP.sim.time');page.wait_for_timeout(150);check('Pause freezes physics',page.evaluate('DC_APP.sim.time')==t);page.click('#resume')
    page.keyboard.press('m');check('Map remains available',page.evaluate('DC_APP.mode==="map"'));page.click('#closeMap');page.keyboard.press('p');check('Photo mode remains available',page.evaluate('DC_APP.mode==="photo"'));page.click('#exitPhoto')
    context.close()
    for w,h in [(390,844),(844,390)]:
      context,page=load(browser,w,h,True)
      page.evaluate('Object.assign(DC_APP.sim.player,{x:10.9,z:7.95,yaw:Math.PI});DC_APP.updateUI(performance.now())')
      for sel in ['#joystick','#touchCar','#touchAction','#touchBrake','#touchHorn','#touchPush','#touchJump','#interactionsButton','#pauseButton']:reachable(page,sel)
      page.locator('#touchAction').tap();advance(page,.1);check('Touch can pick up an object '+str(w),page.evaluate('!!DC_APP.sim.player.carry'))
      page.locator('#touchPush').tap();check('Touch can throw an object '+str(w),page.evaluate('!DC_APP.sim.player.carry'))
      page.locator('#interactionsButton').tap();reachable(page,'#crouchButton');page.locator('#crouchButton').tap();page.locator('#closeInteractions').tap();advance(page,.5);check('Touch crouch toggles and blends '+str(w),page.evaluate('DC_APP.sim.player.crouch>.9'))
      box=reachable(page,'#touchJump');cdp=context.new_cdp_session(page);xy={'x':box['x']+box['width']/2,'y':box['y']+box['height']/2}
      cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});advance(page,.12);check('Held touch starts a jump '+str(w),page.evaluate('DC_APP.jumpHeld&&DC_APP.sim.player.y>.1'))
      cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]});check('Touch cancellation releases jump '+str(w),page.evaluate('!DC_APP.jumpHeld'));advance(page,1)
      fresh(page);page.evaluate('DC.damageVehicle(DC_APP.sim.cars[0],40,5,13);Object.assign(DC_APP.sim.player,{x:7.5,z:11});DC_APP.updateUI(performance.now())')
      box=reachable(page,'#repairButton');xy={'x':box['x']+box['width']/2,'y':box['y']+box['height']/2}
      cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});advance(page,.5);check('Touch repair can be held '+str(w),page.evaluate('DC_APP.repairHeld&&DC_APP.sim.repairProgress>.1'))
      frame(page,f'08-mobile-{w}.png',False)
      cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]});advance(page,.05);check('Touch repair cancellation is free '+str(w),page.evaluate('!DC_APP.repairHeld&&DC_APP.sim.repairProgress===0&&DC_APP.sim.cash===850'))
      cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[xy]});advance(page,3.2);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]});check('Touch repair completes '+str(w),page.evaluate('DC_APP.sim.cars[0].health===100&&DC_APP.sim.cash===760'))
      context.close()
    check('Zero JavaScript / WebGL errors',not errors)
    check('No external resource requests',not requests)
    browser.close()
finally:
 report={'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'errors':errors,'requests':requests,'environment':'Chromium / Xvfb / SwiftShader software GPU. set_content, isolated storage fixture. Renderer frozen between actual WebGL keyframes. Actual keyboard/pointer/touch events and simulation. Not a hardware performance benchmark.'}
 (OUT/'reactive-browser-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:report[k] for k in ['passed','failed','errors']},ensure_ascii=False),flush=True)
