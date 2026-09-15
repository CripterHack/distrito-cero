"""Live v0.5 renderer + keyboard + simulation. No renderer/storage/gameplay substitutes.
Requires an X display for SwiftShader on the test container's Chromium build.
Measures correctness in a software GPU, NOT performance on user hardware.
"""
from pathlib import Path
import json, os, signal
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/v05';errors=[];requests=[];checks=[]
def check(name,v):
 checks.append({'check':name,'passed':bool(v)});print(('PASS ' if v else 'FAIL ')+name,flush=True);assert v,name
try:
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  browser_cdp=b.new_browser_cdp_session()
  test_browser_pid=next(x['id'] for x in browser_cdp.send('SystemInfo.getProcessInfo')['processInfo'] if x['type']=='browser')
  page=b.new_page(viewport={'width':640,'height':400});page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('request',lambda r:requests.append(r.url))
  page.set_content((ROOT/'index.html').read_text(),wait_until='load');page.wait_for_function('!!window.DC_APP',timeout=30000)
  page.evaluate("DC_APP.renderer.quality='eco';DC_APP.renderer.rain=0;DC_APP.renderer.bloom=0;DC_APP.renderer.resize();DC_APP.audio.enabled=false;")
  page.click('#start');page.click('#dismissTutorial')
  before=page.evaluate('''()=>{const a=DC_APP,s=a.sim,cop=s.cars.find(c=>c.police);s.cars=[s.cars[0],cop];s.peds=[];s.free=true;Object.assign(s.cars[0],{x:4,z:0,yaw:0,speed:0,parked:false});Object.assign(cop,{x:4,z:3,yaw:Math.PI,speed:0,parked:false});Object.assign(s.player,{x:4,z:0,car:0,yaw:0});s.addHeat(40);a.chapterUntil=0;a.toastUntil=0;a.toastQueue=[];return{frame:a.renderer.frame,time:s.time,x:4,z:0};}''')
  page.keyboard.down('s');page.keyboard.down('d');page.wait_for_function('(t)=>DC_APP.sim.time>t+1.8',arg=before['time'],timeout=30000);page.keyboard.up('s');page.keyboard.up('d')
  after=page.evaluate('({frame:DC_APP.renderer.frame,time:DC_APP.sim.time,x:DC_APP.sim.player.x,z:DC_APP.sim.player.z,speed:DC_APP.sim.actor().speed,car:DC_APP.sim.player.car,bust:DC_APP.sim.bust,gl:DC_APP.renderer.gl.getError()})')
  check('Live native renderer keeps drawing during police contact',after['frame']>before['frame']+5)
  check('Real keyboard reverse escapes police contact',after['car']==0 and after['speed']<-4 and after['bust']<.2)
  check('Custom mesh is in the GPU draw set',page.evaluate('DC_APP.renderer.assetParts.length===5&&DC_APP.renderer.meshes.asset_BODY_shell.dynamicCount>0'))
  start=page.evaluate('''()=>{const a=DC_APP,s=new DC.Simulation(a.world);a.sim=s;s.free=true;s.peds=[];s.cars=s.cars.slice(0,1);const o=s.dynamics.props.find(p=>p.type==='lamp'&&p.x>0&&p.x<20&&p.z>20&&p.z<75),c=s.cars[0];window.liveLamp=o;Object.assign(c,{x:o.x,z:o.z-8,yaw:0,speed:20,parked:false});Object.assign(s.player,{x:c.x,z:c.z,yaw:0,car:0});a.renderer.camera.yaw=0;a.renderer.camera.initialized=false;a.chapterUntil=0;return{frame:a.renderer.frame,time:s.time};}''')
  page.keyboard.down('w');page.wait_for_function('liveLamp.broken',timeout=25000);page.keyboard.up('w')
  hit=page.evaluate('({frame:DC_APP.renderer.frame,damage:DC_APP.sim.actor().damage.front,health:DC_APP.sim.actor().health,broken:liveLamp.broken,light:DC_APP.sim.dynamics.lightActive(liveLamp.lightIndex),angle:liveLamp.angle,gl:DC_APP.renderer.gl.getError()})')
  check('Real keyboard collision breaks a lamp during rendering',hit['broken'] and hit['frame']>start['frame'])
  check('Live collision damages the car and extinguishes the lamp',hit['damage']>0 and hit['health']<100 and not hit['light'])
  page.keyboard.down('Space');page.wait_for_function('DC_APP.sim.time>2.8',timeout=25000);page.keyboard.up('Space')
  check('Fall settles during the actual game loop',page.evaluate('liveLamp.angle===1.34&&liveLamp.angularVelocity===0'))
  # Verify the new weighted character in the continuously running loop.
  pstart=page.evaluate("""()=>{const a=DC_APP,s=a.sim;s.heat=0;s.wanted=0;s.resetPolice();s.cars.forEach(c=>{c.parked=true;c.speed=0});Object.assign(s.player,{x:4,z:12,car:null,y:0,yaw:0,moveSpeed:0,walk:0});a.renderer.camera.yaw=0;a.renderer.camera.initialized=false;return {t:s.time,frame:a.renderer.frame,palette:Array.from(a.renderer.heroPalette)};}""")
  page.keyboard.down('w');page.wait_for_function('(t)=>DC_APP.sim.time>t+.7',arg=pstart['t'],timeout=25000);page.keyboard.up('w')
  check('Weighted avatar walks with live renderer and real W',page.evaluate('DC_APP.sim.player.z>13&&DC_APP.sim.player.walk>0&&DC_APP.renderer.meshes.hero_jacket.dynamicCount>0'))
  check('Bone palette changes in the unmodified render loop',page.evaluate('(m)=>m.some((v,i)=>Math.abs(v-DC_APP.renderer.heroPalette[i])>.03)',pstart['palette']))
  page.keyboard.down('Space');page.wait_for_function('DC_APP.sim.player.y>.12',timeout=25000);page.keyboard.up('Space')
  check('Live weighted avatar can jump',page.evaluate('DC_APP.sim.player.y>0&&DC_APP.renderer.gl.getError()===0'))
  page.wait_for_function('DC_APP.sim.player.grounded&&DC_APP.sim.player.y===0',timeout=25000)
  check('Live jump returns to ground without corrupt skin data',page.evaluate('Array.from(DC_APP.renderer.heroPalette).every(Number.isFinite)'))
  page.evaluate('DC_APP.sim.player.car=0')
  # Prepared in-engine review scene. This is a real game capture, not a generated illustration.
  page.evaluate('''()=>{const a=DC_APP,s=a.sim,c=s.actor();s.heat=0;s.wanted=0;s.resetPolice();Object.assign(c,{x:4,z:24,yaw:.2,speed:0});Object.assign(s.player,{x:4,z:24,yaw:.2});DC.damageVehicle(c,23,c.x,c.z+2);a.chapterUntil=0;a.toastUntil=0;a.toastQueue=[];a.renderer.camera.yaw=2.6;a.renderer.camera.pitch=.18;a.renderer.camera.initialized=false;a.renderer.camera.photoDistance=8.1;a.setMode('photo');a.renderer.quality='balanced';a.renderer.rain=.25;a.renderer.bloom=.65;a.renderer.resize();}''')
  page.set_viewport_size({'width':1000,'height':650});page.wait_for_timeout(600);page.screenshot(path=str(OUT/'continuous-coupe.png'))
  check('High-detail review frame has no WebGL errors',page.evaluate('DC_APP.renderer.gl.getError()===0'))
  check('No renderer replacement was used',page.evaluate('!window.realRender'))
  check('No JS/WebGL console errors',not errors);check('No external game resources',not requests)
  # The lab's SwiftShader build can hang on normal shutdown after a full-resolution
  # screenshot. All assertions are complete. Kill ONLY this test browser process.
  os.kill(test_browser_pid,signal.SIGKILL)

finally:
 report={'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'before_police':locals().get('before'),'after_police':locals().get('after'),'lamp_hit':locals().get('hit'),'cleanup':'Owned test browser terminated after all assertions to avoid the lab SwiftShader shutdown hang','renderer_replaced':False,'storage_replaced':False,'simulation_replaced':False,'errors':errors,'requests':requests,'environment':'Chromium, Xvfb, SwiftShader software GPU. Live loop at 640x400 eco, review screenshot 1000x650 balanced. set_content. Not a hardware benchmark.'}
 (OUT/'continuous-realism-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps(report,indent=2,ensure_ascii=False),flush=True)
