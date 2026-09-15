"""Browser QA using Playwright as a DEVELOPMENT tool, never a game dependency.

The restricted test environment blocks navigation to all URLs and has no hardware
GPU. We load the actual single-file HTML with set_content. A clearly isolated
in-memory localStorage fixture supplies a test origin's storage contract.
Paired access waits for the new seat-commit state instead of requiring instant teleportation. Continuous software-WebGL is checked separately; this suite freezes ONLY the
renderer between actual rendered keyframes so input/simulation/DOM checks are not
timed by the software GPU. Native browser persistence and Safari are not claimed.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'qa/v09/legacy';OUT.mkdir(parents=True,exist_ok=True)
HTML=(ROOT/'index.html').read_text()
FIXTURE="""(() => {const data=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false,volume:0,touch:null})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>data.has(k)?data.get(k):null,setItem:(k,v)=>data.set(k,String(v)),removeItem:k=>data.delete(k),clear:()=>data.clear()}});})();"""
results=[];errors=[];requests=[]
def check(name,condition):
    assert condition,name
    results.append({'check':name,'passed':True});print('PASS',name,flush=True)
def load(browser,width,height,touch=False):
    context=browser.new_context(viewport={'width':width,'height':height},device_scale_factor=1,has_touch=touch,is_mobile=touch)
    page=context.new_page()
    page.on('pageerror',lambda e: errors.append(str(e)))
    page.on('console',lambda m: errors.append(m.text) if m.type=='error' else None)
    page.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
    page.set_content(HTML.replace('<script>','<script>'+FIXTURE,1),wait_until='load')
    page.wait_for_function('!!window.DC_APP || !document.getElementById("error").hidden',timeout=30000)
    page.evaluate('DC_APP.renderer.humanReady')
    check('WebGL2 boot '+str(width),page.evaluate('!!window.DC_APP && DC_APP.renderer.gl.getError()===0'))
    page.evaluate('window.realRender=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};')
    return context,page
def capture(page,name,high=False):
    # Legacy campaign/UI regression uses the economical shader path.
    # reactive_browser.py and continuous_reactive.py cover balanced/high rendering.
    if high:
        page.evaluate("DC_APP.renderer.quality='eco';DC_APP.renderer.rain=0;DC_APP.renderer.bloom=0;DC_APP.renderer.resize();")
    page.wait_for_timeout(500)  # Let camera damping and HUD catch up before a keyframe.
    page.evaluate('realRender(DC_APP.sim)')
    if name in ['05-dialogue.png','08-mobile-landscape.png']:page.screenshot(path=str(OUT/name))
    check('Rendered frame '+name,page.evaluate('DC_APP.renderer.gl.getError()===0'))
def reset_player(page,x,z):
    page.evaluate('''({x,z})=>{const a=DC_APP;a.sim.cancelAccess(true);if(a.sim.player.car!==null){a.sim.actor().speed=0;a.sim.actor().parked=true;}Object.assign(a.sim.player,{x,z,car:null,y:0,vy:0,vx:0,vz:0,transition:null,dodge:0,stagger:0});a.renderer.camera.initialized=false;a.renderer.camera.yaw=0;a.sim.pin=null;a.sim.events=[];}''',{'x':x,'z':z})
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
    context,page=load(browser,960,640)
    capture(page,'01-menu.png',True)
    page.click('#start');page.click('#dismissTutorial')
    reset_player(page,-4,8)  # v0.4 cars are now solid; locomotion fixture uses an unobstructed lane.
    page.keyboard.down('w');page.wait_for_function('DC_APP.sim.player.z>10',timeout=15000);page.keyboard.up('w')
    check('W moves the on-foot player',page.evaluate('DC_APP.sim.player.z>10'))
    reset_player(page,5,8)
    page.keyboard.press('f');page.wait_for_function('DC_APP.sim.player.car===0&&!DC_APP.sim.access',timeout=18000);check('F enters the nearby vehicle',page.evaluate('DC_APP.sim.player.car===0'))
    page.keyboard.down('w');page.wait_for_function('DC_APP.sim.actor().speed>10 && DC_APP.sim.player.z>18',timeout=15000);page.keyboard.up('w')
    check('W accelerates the actual simulation',page.evaluate('DC_APP.sim.actor().speed>10 && DC_APP.sim.player.z>18'))
    page.keyboard.down('d');page.wait_for_function('DC_APP.sim.actor().yaw<-.1',timeout=15000);page.keyboard.up('d')
    check('D steers right',page.evaluate('DC_APP.sim.actor().yaw<-.1'))
    capture(page,'02-driving.png',True)
    page.keyboard.down('Space');page.wait_for_function('Math.abs(DC_APP.sim.actor().speed)<.8',timeout=15000);page.keyboard.up('Space');page.keyboard.press('f');page.wait_for_function('DC_APP.sim.player.car===null&&!DC_APP.sim.access',timeout=18000)
    check('Brake then F exits safely',page.evaluate('DC_APP.sim.player.car===null'))
    page.keyboard.press('Escape');t=page.evaluate('DC_APP.sim.time');page.wait_for_timeout(400)
    check('Pause stops simulation time',page.evaluate('DC_APP.sim.time')==t)
    capture(page,'03-pause.png')
    page.click('#resume');page.keyboard.press('m');check('M opens the map',page.evaluate("DC_APP.mode==='map'"))
    page.locator('#citymap').click(position={'x':260,'y':170});check('Map click sets a GPS point',page.evaluate('DC_APP.sim.pin!==null'))
    capture(page,'04-map.png')
    page.click('#clearPin');check('GPS clear works',page.evaluate('DC_APP.sim.pin===null'))
    page.click('#closeMap');reset_player(page,13,20);page.keyboard.press('e')
    check('Phone opens the actual story dialogue',page.evaluate("DC_APP.mode==='dialog' && DC_APP.sim.awaitingStory===0"))
    capture(page,'05-dialogue.png')
    page.locator('#dialogOptions button').first.click();check('Story confirmation advances the chapter',page.evaluate('DC_APP.sim.story===1'))
    reset_player(page,5,8);page.evaluate('Object.assign(DC_APP.sim.cars[0],{x:5,z:11,yaw:0,speed:0,parked:true,driver:null})');page.keyboard.press('f');page.wait_for_function('DC_APP.sim.story===2&&!DC_APP.sim.access',timeout=18000)
    check('Entering a car advances the vehicle chapter',page.evaluate('DC_APP.sim.story===2'))
    reset_player(page,168,96);page.keyboard.press('e');page.locator('#dialogOptions button').first.click()
    check('Picking up the file triggers police heat',page.evaluate('DC_APP.sim.story===3 && DC_APP.sim.wanted>0'))
    reset_player(page,-84,264);page.keyboard.press('e');check('Wanted refuge is blocked',page.evaluate("DC_APP.mode==='play'"))
    page.evaluate('DC_APP.sim.heat=0;DC_APP.sim.wanted=0');page.keyboard.press('e');page.locator('#dialogOptions button').first.click()
    check('Unwanted refuge advances to transmission',page.evaluate('DC_APP.sim.story===4'))
    reset_player(page,252,-72);page.keyboard.press('e');page.wait_for_function('DC_APP.sim.upload>1',timeout=15000)
    check('Terminal transmission advances with game time',page.evaluate('DC_APP.sim.uploading && DC_APP.sim.upload>1'))
    page.evaluate('DC_APP.sim.missions(12);DC_APP.processEvents()')
    check('Transmission activates the final escape',page.evaluate('DC_APP.sim.story===5 && DC_APP.sim.wanted>0'))
    reset_player(page,-252,-156);page.evaluate('DC_APP.sim.heat=0;DC_APP.sim.wanted=0');page.keyboard.press('e');page.locator('#dialogOptions button').first.click()
    check('Public ending completes the story',page.evaluate("DC_APP.sim.story===6 && DC_APP.sim.ending==='publicado'"))
    page.evaluate('DC_APP.sim.free=true');reset_player(page,0,-72);page.keyboard.press('e');check('Repeatable delivery can be accepted',page.evaluate('DC_APP.sim.job?.type==="delivery"'))
    goal=page.evaluate('DC_APP.sim.job.points[0]');reset_player(page,goal['x'],goal['z']);page.wait_for_timeout(100)
    check('Delivery arrival pays the reward',page.evaluate('DC_APP.sim.job===null && DC_APP.sim.stats.jobs===1'))
    page.keyboard.press('Escape');page.click('#saveGame');cash=page.evaluate('DC_APP.sim.cash')
    check('Save writes a validated snapshot',page.evaluate("JSON.parse(localStorage.getItem('distrito-cero:save:v1')).version===1"))
    page.click('#mainMenu');page.click('#continue');check('Continue restores the snapshot',page.evaluate('DC_APP.sim.cash')==cash)
    page.keyboard.press('p');check('P opens photo mode',page.evaluate("DC_APP.mode==='photo'"));capture(page,'06-photo.png',True);page.click('#exitPhoto')
    context.close()
    context,page=load(browser,390,844,True)
    page.click('#start');page.click('#dismissTutorial')
    check('Touch controls automatically enabled',page.evaluate('document.body.classList.contains("touch")'))
    for id in ['touchCar','touchAction','touchBrake','joystick','pauseButton','mapButton']:
        hit=page.evaluate('''id=>{let e=document.getElementById(id),r=e.getBoundingClientRect(),h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth&&r.bottom<=innerHeight&&(h===e||e.contains(h));}''',id)
        check('Portrait control reachable: '+id,hit)
    reset_player(page,-4,8)
    joy=page.locator('#joystick').bounding_box();x=joy['x']+joy['width']/2;y=joy['y']+joy['height']/2
    cdp=context.new_cdp_session(page);cdp.send('Input.dispatchTouchEvent',{'type':'touchStart','touchPoints':[{'x':x,'y':y-25,'id':1}]});page.wait_for_function('DC_APP.sim.player.z>9',timeout=15000);cdp.send('Input.dispatchTouchEvent',{'type':'touchEnd','touchPoints':[]})
    check('Touch joystick moves the player',page.evaluate('DC_APP.sim.player.z>9'))
    check('Touch end clears joystick state',page.evaluate('DC_APP.stick.x===0 && DC_APP.stick.y===0'))
    reset_player(page,5,8)
    await_box=page.locator('#touchCar').bounding_box();page.touchscreen.tap(await_box['x']+await_box['width']/2,await_box['y']+await_box['height']/2)
    page.wait_for_function('DC_APP.sim.player.car===0&&!DC_APP.sim.access',timeout=18000)
    check('Touch SUBIR enters a car',page.evaluate('DC_APP.sim.player.car===0'))
    capture(page,'07-mobile-portrait.png',True)
    page.set_viewport_size({'width':844,'height':390});page.wait_for_timeout(150)
    for id in ['touchCar','touchAction','touchBrake','joystick','pauseButton','mapButton']:
        hit=page.evaluate('''id=>{let e=document.getElementById(id),r=e.getBoundingClientRect(),h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth&&r.bottom<=innerHeight&&(h===e||e.contains(h));}''',id)
        check('Landscape control reachable: '+id,hit)
    capture(page,'08-mobile-landscape.png',True)
    page.click('#pauseButton');check('Touch pause reachable and functional',page.evaluate("DC_APP.mode==='pause'"))
    context.close();browser.close()
check('No uncaught JS or WebGL console errors',not errors)
check('No external requests from the game',not requests)
report={'environment':'Chromium / software WebGL2 / Xvfb / injected HTML / isolated test-storage fixture','native_safari_tested':False,'native_persistence_tested':False,'errors':errors,'requests':requests,'checks':results}
(OUT/'browser-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print('TOTAL',len(results),'checks passed',flush=True)
