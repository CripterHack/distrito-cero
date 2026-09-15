"""Fresh renderer context per posed review. The paired animation and meshes are production code."""
from pathlib import Path
import json,os,sys,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v012';name=sys.argv[1] if len(sys.argv)>1 else 'driver';tag=os.environ.get('DC_REVIEW_TAG','');os.environ.setdefault('DISPLAY',':99')
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);page=b.new_page(viewport={'width':int(os.environ.get('DC_REVIEW_WIDTH','1120')),'height':int(os.environ.get('DC_REVIEW_HEIGHT','740'))});errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.set_content(Path(os.environ.get('DC_REVIEW_HTML',str(R/'index.html'))).read_text().replace('<script>','<script>'+FIXTURE,1),timeout=90000);page.wait_for_function('!!window.DC_APP',timeout=90000)
 page.evaluate('DC_APP.renderer.humanReady');
 page.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.renderer.updateCamera=()=>{};DC_APP.loop=()=>{};')
 page.click('#start');page.click('#commitCreator');page.click('#dismissTutorial')
 page.evaluate("""()=>{const a=DC_APP,s=a.sim,r=a.renderer;s.free=true;s.wanted=0;s.heat=0;for(let i=0;i<s.cars.length;i++)Object.assign(s.cars[i],{x:300+i*6,z:0,parked:true,speed:0});s.peds.forEach(n=>n.hidden=true);const c=s.cars[1];Object.assign(c,{x:4,z:40,yaw:0,parked:false,driver:DC.driverProfile(c),health:100,stolen:false,owned:false});Object.assign(s.player,{x:1.75,z:40.1,car:null,y:0,yaw:Math.PI/2,vx:0,vz:0});a.setMode('photo');r.daylight=.69;r.rain=0;document.getElementById('toast').style.display='none';document.getElementById('chapter').style.display='none';r.camera.eye=[-.7,1.75,43.6];r.camera.target=[3.75,1,39.8];}""")
 if name in ['open','pull','release','enter','exit']:
  page.evaluate("DC_APP.sim.interact('car')")
  if name=='exit':page.evaluate('const s=DC_APP.sim;for(let i=0;i<300;i++)s.step(1/60,{});s.interact("car")')
  page.evaluate("""name=>{const s=DC_APP.sim,a=s.access;const elapsed=a.approach+({open:.32,pull:1.08,release:1.70,enter:2.23,exit:.90}[name]);for(let i=0;i<Math.ceil(elapsed*60);i++)s.step(1/60,{});DC_APP.renderer.camera.eye=[-3.5,2.4,43.6];DC_APP.renderer.camera.target=[2.1,1.0,40];}""",name)
 elif name in ['full','body-profile','run','crouch','hand','hand-grip']:
  page.evaluate("DC_APP.sim.cars[1].x=200;Object.assign(DC_APP.sim.player,{x:4,z:40,yaw:0,walk:0,moveSpeed:0,grip:0});DC_APP.sim.time=1;DC_APP.renderer.camera.eye=[4.20,1.19,42.9];DC_APP.renderer.camera.target=[4,.98,40];")
  if name=='body-profile':page.evaluate("DC_APP.renderer.camera.eye=[7.3,1.25,40.20]")
  if name=='run':page.evaluate("Object.assign(DC_APP.sim.player,{walk:4.35,moveSpeed:6.2,sprintBlend:1,grip:undefined});DC_APP.renderer.camera.eye=[6.2,1.37,42.6]")
  if name=='crouch':page.evaluate("DC_APP.sim.player.crouch=1;DC_APP.sim.player.grip=undefined;DC_APP.renderer.camera.eye=[5.8,1.10,42.5];DC_APP.renderer.camera.target=[4,.66,40]")
  if name in ['hand','hand-grip']:
   page.evaluate("""close=>{const s=DC_APP.sim;s.player.grip=close?1:0;const q=DC.SkinRig.pose(s.player,s.time),h=DC.SkinRig.handPoint(q,s.player,'R');DC_APP.renderer.camera.eye=[h.x+.32,h.y-.039,h.z+.26];DC_APP.renderer.camera.target=[h.x-.013,h.y-.085,h.z+.005];}""",name=='hand-grip')
 elif name=='head':
  page.evaluate("DC_APP.sim.cars[1].x=200;Object.assign(DC_APP.sim.player,{x:4,z:40,yaw:0});DC_APP.renderer.camera.eye=[4.46,1.67,41.14];DC_APP.renderer.camera.target=[4,1.49,40];")
 elif name in ['portrait','profile','blink','night','threequarter']:
  page.evaluate("DC_APP.sim.cars[1].x=200;Object.assign(DC_APP.sim.player,{x:4,z:40,yaw:0,walk:0,moveSpeed:0});DC_APP.renderer.camera.eye=[4.15,1.72,40.57];DC_APP.renderer.camera.target=[4,1.66,40];DC_APP.sim.time=1;")
  if name=='blink':page.evaluate('DC_APP.sim.time=.085')
  if name=='night':page.evaluate('DC_APP.renderer.daylight=0')
  if name=='threequarter':page.evaluate("DC_APP.renderer.camera.eye=[4.30,1.75,40.64]")
  if name=='profile':page.evaluate("DC_APP.renderer.camera.eye=[4.6,1.72,40.13]")
 elif name=='cast':
  page.evaluate("""()=>{const s=DC_APP.sim;for(let i=0;i<4;i++){const n=s.peds[i];Object.assign(n,{hidden:false,x:i*1.05+2.2,z:40.6,skin:DC.driverProfile(s.cars[i+1]).skin,coat:DC.driverProfile(s.cars[i+1]).coat,police:i===3,y:0,yaw:Math.PI*.06,walk:i*1.7,moveSpeed:i%2?1.3:0,speed:0});}s.cars[1].x=10;s.player.x=1;DC_APP.renderer.camera.eye=[3,2.45,47];DC_APP.renderer.camera.target=[3.4,1.15,40];}""")
 elif name=='police':page.evaluate('const c=DC_APP.sim.cars[1];c.police=true;c.driver=DC.driverProfile(c);')
 page.evaluate('DC_APP.renderer.syncSectors(25);DC_APP.renderer.frame=0;drawActual(DC_APP.sim)');report=page.evaluate('({stats:DC_APP.renderer.castStats,visual:DC_APP.renderer.visualStats,textures:DC_APP.renderer.humanTextureStatus,access:DC_APP.sim.access?.kind,phase:DC_APP.sim.accessPlayerPose()?.accessPhase,gl:DC_APP.renderer.gl.getError()})');report['errors']=errors;report['source_sha256']=hashlib.sha256(Path(os.environ.get('DC_REVIEW_HTML',str(R/'index.html'))).read_bytes()).hexdigest();print(json.dumps(report),flush=True);page.screenshot(path=str(O/('review-'+tag+name+'.png')),timeout=45000);(O/('review-'+tag+name+'.json')).write_text(json.dumps(report,indent=2));b.close()
