"""v0.3 encounter integration and responsive UI checks.
Playwright is a development tool only. Real simulation, keyboard and pointer input.
SwiftShader rendering is paused between explicitly rendered screenshot keyframes.
No gameplay method is mocked. set_content is used because navigation is restricted.
"""
from pathlib import Path
import json, sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v04';OUT.mkdir(exist_ok=True)
SHARD=sys.argv[1] if len(sys.argv)>1 else 'all'
if SHARD not in ['all','desktop','390','844']:raise SystemExit('Use all, desktop, 390 or 844')
HTML=(ROOT/'index.html').read_text()
FIXTURE="""(()=>{const data=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false,volume:0,touch:null})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,String(v)),removeItem:k=>data.delete(k)}});})();"""
checks=[];errors=[];requests=[]
def check(name,condition):
    checks.append({'check':name,'passed':bool(condition)})
    print(('PASS ' if condition else 'FAIL ')+name,flush=True)
    assert condition,name

def load(browser,w,h,touch=False):
    context=browser.new_context(viewport={'width':w,'height':h},device_scale_factor=1,has_touch=touch,is_mobile=touch)
    page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
    page.on('request',lambda r:requests.append(r.url))
    page.set_content(HTML.replace('<script>','<script>'+FIXTURE,1),wait_until='load')
    page.wait_for_function('!!window.DC_APP || !document.getElementById("error").hidden')
    check(f'WebGL2 boot {w}x{h}',page.evaluate('!!window.DC_APP && DC_APP.renderer.gl.getError()===0'))
    page.evaluate('window.realRender=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}')
    page.click('#start');page.click('#dismissTutorial')
    return context,page

def scene(page,mode='stationary'):
    page.evaluate('''mode=>{
      const a=DC_APP,s=new DC.Simulation(a.world),cop=s.cars.find(c=>c.police);
      s.free=true;s.story=3;s.peds=[];s.cars=[s.cars[0],cop];
      Object.assign(s.cars[0],{x:4,z:0,yaw:0,speed:0,parked:false});
      Object.assign(cop,{x:4,z:6,yaw:Math.PI,speed:0,parked:false});
      Object.assign(s.player,{x:4,z:0,yaw:0,car:0});
      if(mode==='front')cop.z=3;
      if(mode==='rear')Object.assign(cop,{z:-3,yaw:0,speed:10});
      if(mode==='foot'){s.player.car=null;s.cars[0].x=40;cop.z=-3;cop.yaw=0;}
      s.addHeat(40);a.sim=s;a.setMode('play');a.sim.events=[];a.toastQueue=[];a.toastUntil=0;a.chapterUntil=0;
      document.getElementById('toast').classList.remove('visible');document.getElementById('chapter').classList.remove('visible');
      a.renderer.camera.initialized=false;a.renderer.camera.yaw=0;a.renderer.camera.pitch=.22;a.autoSave=0;
      a.renderer.updateCamera(s,1);a.updateUI(performance.now());
    }''',mode)

def frame(page,name):
    page.evaluate('DC_APP.updateUI(performance.now());DC_APP.renderer.updateCamera(DC_APP.sim,.3);realRender(DC_APP.sim)')
    page.screenshot(path=str(OUT/name))
    check('WebGL frame '+name,page.evaluate('DC_APP.renderer.gl.getError()===0'))

def reachable(page,selector,label):
    box=page.locator(selector).bounding_box()
    check(label+' visible',bool(box))
    check(label+' inside viewport',box['x']>=0 and box['y']>=0 and box['x']+box['width']<=page.viewport_size['width']+1 and box['y']+box['height']<=page.viewport_size['height']+1)
    hit=page.evaluate('''({s,x,y})=>{const el=document.querySelector(s),top=document.elementFromPoint(x,y);return top===el||el.contains(top)}''',{'s':selector,'x':box['x']+box['width']/2,'y':box['y']+box['height']/2})
    check(label+' receives pointer input',hit)
    return box

try:
 with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    if SHARD in ['all','desktop']:
      context,page=load(browser,1280,800)
      scene(page,'front');page.keyboard.down('s');page.keyboard.down('d');page.wait_for_timeout(1700);page.keyboard.up('s');page.keyboard.up('d')
      check('Reverse and steering escape a front bumper contact',page.evaluate('DC_APP.sim.player.car===0 && DC_APP.sim.actor().speed<-4 && DC_APP.sim.bust<.3'))
      frame(page,'11-police-breakaway.png')
      scene(page,'rear');page.keyboard.down('w');page.wait_for_timeout(2000);page.keyboard.up('w')
      check('Accelerate away after a police rear-end impact',page.evaluate('DC_APP.sim.actor().speed>12 && DC_APP.sim.player.car===0 && DC_APP.sim.heat===40'))
      scene(page,'foot');page.keyboard.down('w');page.keyboard.down('Shift');page.wait_for_timeout(1500);page.keyboard.up('w');page.keyboard.up('Shift')
      check('Sprinting near police does not advance capture',page.evaluate('DC_APP.sim.player.z>6 && DC_APP.sim.bust<.1 && DC_APP.sim.cash===850'))
      scene(page);page.keyboard.down('r');page.wait_for_timeout(550)
      check('Keyboard R advances deliberate surrender',page.evaluate('DC_APP.sim.policeState.surrender>.25 && DC_APP.sim.wanted>0'))
      page.keyboard.up('r');page.wait_for_timeout(100)
      check('Releasing R cancels surrender without a charge',page.evaluate('DC_APP.sim.policeState.surrender===0 && DC_APP.sim.cash===850'))
      page.keyboard.down('r');page.keyboard.down('w');page.wait_for_timeout(300);page.keyboard.up('r');page.keyboard.up('w')
      check('Accelerating cancels surrender',page.evaluate('DC_APP.sim.policeState.surrender===0'))
      scene(page);page.keyboard.down('r');page.wait_for_timeout(300);page.keyboard.press('Escape');page.keyboard.up('r')
      check('Opening pause clears held surrender',page.evaluate('DC_APP.sim.policeState.surrender===0 && DC_APP.mode==="pause"'))
      page.click('#resume');scene(page);page.keyboard.down('r');page.wait_for_timeout(2200);page.keyboard.up('r')
      check('Completed surrender costs $150 and keeps chapter 3',page.evaluate('DC_APP.sim.wanted===0 && DC_APP.sim.cash===700 && DC_APP.sim.story===3 && DC_APP.sim.player.car===null'))
      check('Encounter panel closes after surrender',page.locator('#policePanel').is_hidden())
      scene(page);page.wait_for_timeout(200);page.evaluate('DC_APP.sim.bust=.32');frame(page,'12-police-capture.png')
      check('Capture meter exposes an accessible value',page.evaluate('+document.getElementById("captureProgress").getAttribute("aria-valuenow")>0'))
      box=reachable(page,'#surrenderButton','Desktop surrender button')
      page.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2);page.mouse.down();page.wait_for_timeout(450)
      check('Mouse holding surrender advances progress',page.evaluate('DC_APP.sim.policeState.surrender>.2'))
      page.mouse.up();page.wait_for_timeout(100)
      check('Mouse release cancels the countdown',page.evaluate('DC_APP.sim.policeState.surrender===0'))
      scene(page);page.wait_for_timeout(150)
      known=page.evaluate('({...DC_APP.sim.policeState.lastSeen})')
      page.evaluate('Object.assign(DC_APP.sim.actor(),{x:84,z:84,speed:0});Object.assign(DC_APP.sim.player,{x:84,z:84,actualSpeed:0});DC_APP.sim.bust=0')
      page.wait_for_timeout(400)
      check('Losing sight enters search instead of updating hidden coordinates',page.evaluate('DC_APP.sim.getPoliceStatus().phase==="search" && DC_APP.sim.policeState.lastSeen.x<10'))
      check('Search progress is visible and surrender hidden out of range',page.locator('#searchWrap').is_visible() and page.locator('#surrenderButton').is_hidden())
      frame(page,'13-police-search.png');page.keyboard.press('m');frame(page,'14-police-search-map.png');page.click('#closeMap')
      page.evaluate('Object.assign(DC_APP.sim.cars[1],{x:84,z:92,speed:0,yaw:Math.PI})');page.wait_for_timeout(200)
      check('Visual reacquisition resets search countdown',page.evaluate('DC_APP.sim.seen && DC_APP.sim.unseen===0 && DC_APP.sim.policeState.lastSeen.x===84'))
      scene(page);page.wait_for_timeout(7000)
      check('Refusing to move still results in capture, with story retained',page.evaluate('DC_APP.sim.wanted===0 && DC_APP.sim.cash===550 && DC_APP.sim.story===3'))
      context.close()
    for w,h in [(390,844),(844,390)]:
      if SHARD not in ['all',str(w)]:continue
      context,page=load(browser,w,h,True);scene(page);page.wait_for_timeout(120)
      box=reachable(page,'#surrenderButton',f'Mobile surrender {w}x{h}')
      for sel in ['#joystick','#touchBrake','#touchCar','#touchAction','#pauseButton']:
        reachable(page,sel,f'{sel} {w}x{h}')
      frame(page,f'15-police-mobile-{w}.png')
      cdp=context.new_cdp_session(page);x=box['x']+box['width']/2;y=box['y']+box['height']/2
      cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]});page.wait_for_timeout(450)
      check(f'Native touch hold advances surrender {w}',page.evaluate('DC_APP.sim.policeState.surrender>.15'))
      cdp.send('Input.dispatchTouchEvent',{'type':'touchCancel','touchPoints':[]});page.wait_for_timeout(120)
      check(f'Pointer cancellation clears surrender {w}',page.evaluate('DC_APP.sim.policeState.surrender===0 && !DC_APP.surrenderHeld'))
      # A second real touch completes the interaction.
      cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y}]});page.wait_for_timeout(2200)
      cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
      check(f'Native touch can complete surrender {w}',page.evaluate('DC_APP.sim.wanted===0 && DC_APP.sim.cash===700'))
      context.close()
    check('No JavaScript or WebGL console errors',not errors)
    check('Game made no external resource requests',not requests)
    browser.close()
finally:
 report={'checks':checks,'passed':sum(c['passed'] for c in checks),'failed':sum(not c['passed'] for c in checks),'errors':errors,'requests':requests,'environment':'Chromium / Xvfb / SwiftShader, set_content; real simulation and controls; keyframe renderer, in-memory storage fixture'}
 (OUT/('police-browser-'+SHARD+'-report.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False))
 print(json.dumps({'passed':report['passed'],'failed':report['failed'],'errors':errors},ensure_ascii=False),flush=True)
