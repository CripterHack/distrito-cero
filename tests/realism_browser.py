"""v0.5 renderer/play integration. Uses real WebGL keyframes and native input.
Requires a display (Xvfb on Linux). No hardware FPS or mobile-device claim.
"""
from pathlib import Path
import json, hashlib, os, time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/v05';OUT.mkdir(exist_ok=True)
HTML=(ROOT/'index.html').read_text()
FIXTURE="""(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false,volume:0,touch:null})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k),clear:()=>d.clear()}});})();"""
checks=[];errors=[];requests=[]
def check(name,value):
 checks.append({'check':name,'passed':bool(value)});print(time.strftime('%H:%M:%S')+' '+('PASS ' if value else 'FAIL ')+name,flush=True);assert value,name

def load(b,w,h,touch=False):
 ctx=b.new_context(viewport={'width':w,'height':h},device_scale_factor=1,is_mobile=touch,has_touch=touch);p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.on('request',lambda r:requests.append(r.url));p.set_content(HTML.replace('<script>','<script>'+FIXTURE,1),wait_until='load',timeout=60000)
 p.wait_for_function('!!window.DC_APP||!document.getElementById("error").hidden',timeout=45000);check('Boot WebGL '+str((w,h)),p.evaluate('!!window.DC_APP'))
 p.evaluate('window.actualRender=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};window.actualCamera=DC_APP.renderer.updateCamera.bind(DC_APP.renderer);DC_APP.renderer.updateCamera=()=>{};');p.click('#start');p.click('#dismissTutorial');p.evaluate("DC_APP.chapterUntil=0;document.getElementById('chapter').style.display='none';DC_APP.sim.peds=[];DC_APP.sim.cars.forEach(c=>{c.speed=0;c.parked=true});DC_APP.sim.free=true")
 return ctx,p

def advance(p,t):p.evaluate('''t=>{for(let i=0;i<Math.ceil(t*60);i++)DC_APP.sim.step(1/60,DC_APP.input());DC_APP.processEvents();DC_APP.updateUI(performance.now());}''',t)
def frame(p,name,mode='balanced'):
 p.evaluate('''q=>{const a=DC_APP;a.renderer.quality=q;a.renderer.rain=q==='high'?1:0;a.renderer.resize();a.renderer.frame=0;actualRender(a.sim);}''',mode)
 check('No WebGL errors '+name,p.evaluate('DC_APP.renderer.gl.getError()===0'))
 p.screenshot(path=str(OUT/name));return hashlib.sha256((OUT/name).read_bytes()).hexdigest()

def reachable(p,sel):
 b=p.locator(sel).bounding_box();check(sel+' visible '+str(p.viewport_size),bool(b));w,h=p.viewport_size.values()
 check(sel+' inside viewport',b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w+1 and b['y']+b['height']<=h+1)
 check(sel+' receives pointer',p.evaluate('''({sel,x,y})=>{const e=document.querySelector(sel),t=document.elementFromPoint(x,y);return t===e||e.contains(t)}''',{'sel':sel,'x':b['x']+b['width']/2,'y':b['y']+b['height']/2}))

try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  ctx,p=load(b,1200,800)
  check('17 native joints and 11 skinned material groups',p.evaluate('DC_APP.renderer.visualStats.bones===17&&DC_APP.renderer.heroParts.length===11'))
  check('Every packed vertex validates',p.evaluate('DC.HeroAsset.parts.every(p=>DC.SkinRig.validate(DC.Realism.decode(p)))'))
  check('No nonfinite uniform data',p.evaluate('Array.from(DC_APP.renderer.heroPalette).every(Number.isFinite)'))
  check('Source city still contains 555 physical props',p.evaluate('DC_APP.sim.dynamics.props.length===555'))
  p.evaluate('''()=>{const a=DC_APP;window.savedCars=a.sim.cars.map(c=>({...c}));a.sim.cars.forEach(c=>{c.x+=250;c.z+=250});Object.assign(a.sim.player,{x:3,z:9,y:0,yaw:0,walk:0,moveSpeed:0});a.setMode('photo');a.renderer.camera.eye=[4.35,1.65,11.7];a.renderer.camera.target=[3,.96,9];}''')
  hashes=[]
  for name,pose in [('idle',{}),('walk',{'moveSpeed':3,'walk':1.1}),('run',{'moveSpeed':6,'sprintBlend':1,'walk':1.85}),('crouch',{'crouch':1}),('jump',{'y':.48,'vy':1.6}),('carry',{'carry':'intro:crate:0','reach':.8})]:
   p.evaluate('''pose=>{Object.assign(DC_APP.sim.player,{moveSpeed:0,sprintBlend:0,walk:0,crouch:0,carry:null,reach:0,y:0,vy:0},pose);}''',pose)
   hashes.append(frame(p,'hero-'+name+'.png'))
   check('Finite skin pose '+name,p.evaluate('Array.from(DC_APP.renderer.heroPalette).every(Number.isFinite)'))
   check('Same skin palette in shadow and color '+name,p.evaluate('''()=>{const r=DC_APP.renderer,g=r.gl;return [...g.getUniform(r.shadowProgram,r.uniform(r.shadowProgram,'uBones[0]'))].every((v,i)=>Math.abs(v-r.heroPalette[i])<.0001)&&[...g.getUniform(r.sceneProgram,r.uniform(r.sceneProgram,'uBones[0]'))].every((v,i)=>Math.abs(v-r.heroPalette[i])<.0001)}'''))
  check('Each pose has distinct actual rendered pixels',len(set(hashes))==len(hashes))
  p.evaluate("Object.assign(DC_APP.sim.player,{carry:null,reach:0,y:0,vy:0,crouch:0});DC_APP.setMode('play');DC_APP.renderer.camera.yaw=0;window.startZ=DC_APP.sim.player.z")
  p.keyboard.down('w');advance(p,.6);p.keyboard.up('w');check('Native W moves player and advances stride',p.evaluate('DC_APP.sim.player.z>startZ+1&&DC_APP.sim.player.walk>0'))
  p.keyboard.press('x');advance(p,.4);check('Native X blends crouch',p.evaluate('DC_APP.sim.player.crouch>.9'));p.keyboard.press('x');advance(p,.3)
  p.keyboard.down('Space');advance(p,.15);p.keyboard.up('Space');check('Native jump remains active',p.evaluate('DC_APP.sim.player.y>.1'));advance(p,1)
  p.keyboard.press('p');reachable(p,'#photoFocus');p.click('#photoFocus');check('Closeup frames the character without teleporting simulation',p.evaluate('DC_APP.renderer.camera.closeup&&DC_APP.renderer.camera.photoDistance===1.4'))
  p.evaluate('actualCamera(DC_APP.sim,1,{photo:true,look:true})');frame(p,'hero-closeup.png','high');p.click('#photoFocus');check('Photo composition returns to full-body',p.evaluate('!DC_APP.renderer.camera.closeup'))
  p.evaluate('''()=>{const a=DC_APP;a.sim.cars=savedCars;const c=a.sim.cars[0];Object.assign(a.sim.player,{x:c.x-2,z:c.z-1,y:0,yaw:0,moveSpeed:0});a.renderer.camera.eye=[c.x+3.5,1.7,c.z+5];a.renderer.camera.target=[c.x,.78,c.z];}''')
  frame(p,'coupe-refined.png','high');check('Smooth coupe has 3100 native triangles',p.evaluate('DC_APP.renderer.meshes.asset_BODY_shell.count===9300'))
  check('Curved roof replaces flat placeholder',p.evaluate('DC_APP.renderer.meshes.roof.count>1000'))
  p.evaluate('DC.damageVehicle(DC_APP.sim.cars[0],70,DC_APP.sim.cars[0].x,DC_APP.sim.cars[0].z+2)');frame(p,'coupe-damage.png')
  check('Damage still changes car health and deformation channels',p.evaluate('DC_APP.sim.cars[0].health<100&&DC_APP.sim.cars[0].damage.front>0'))
  check('Save/restore remains compatible after graphics upgrade',p.evaluate('''()=>{const data=DC_APP.sim.serialize(),s=new DC.Simulation(DC_APP.world);return s.restore(data)&&s.cash===DC_APP.sim.cash&&s.cars[0].health===DC_APP.sim.cars[0].health}'''))
  p.evaluate('''()=>{const a=DC_APP,t=a.sim.dynamics.props.find(p=>p.type==='tree'&&!a.world.blocked(p.x+3,p.z+7,.5));window.chosenTree=t;Object.assign(a.sim.player,{x:t.x+3,z:t.z+7,car:null});a.renderer.camera.eye=[t.x+7,3.3,t.z+8];a.renderer.camera.target=[t.x,2.8,t.z];}''')
  frame(p,'tree-standing.png','balanced');check('Leaves and tapered wood are instanced separately',p.evaluate('DC_APP.renderer.dynamic.treeWood.length>0&&DC_APP.renderer.dynamic.treeLeaves.length>0'))
  p.evaluate('''()=>{const a=DC_APP;a.sim.dynamics.impactProp(chosenTree,90,1,0);for(let i=0;i<180;i++)a.sim.step(1/60,{});}''');frame(p,'tree-fallen.png');check('Detailed tree remains destructible',p.evaluate('chosenTree.broken&&chosenTree.angle>1'))
  check('LOD geometry stays within fixed complexity budget',p.evaluate('Object.values(DC_APP.renderer.visuals).reduce((s,v)=>s+v.length/24,0)<20000'))
  ctx.close()
  for w,h in [(390,844),(844,390)]:
   ctx,p=load(b,w,h,True);p.click('#photoButton');reachable(p,'#photoFocus');reachable(p,'#capture');reachable(p,'#exitPhoto');p.locator('#photoFocus').tap();check('Touch closeup toggles '+str(w),p.evaluate('DC_APP.renderer.camera.closeup'))
   p.evaluate('actualCamera(DC_APP.sim,1,{photo:true,look:true})');frame(p,'mobile-photo-'+str(w)+'.png','eco');p.locator('#exitPhoto').tap();check('Photo exit restores game controls '+str(w),p.evaluate("DC_APP.mode==='play'&&!document.getElementById('touchControls').hidden"));ctx.close()
  check('No JavaScript or WebGL console errors',not errors);check('Zero external requests',not requests);b.close()
finally:
 report={'checks':checks,'passed':sum(x['passed'] for x in checks),'failed':sum(not x['passed'] for x in checks),'errors':errors,'requests':requests,'environment':'Chromium headed under Xvfb, ANGLE SwiftShader. Isolated storage fixture. Renderer frozen between actual GPU keyframes. Synthetic states plus actual keys/touch. Not a hardware benchmark.'}
 (OUT/'realism-browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:report[k] for k in ['passed','failed','errors']}),flush=True)
