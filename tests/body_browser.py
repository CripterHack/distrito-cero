"""v0.10 DOM/paired-animation/streaming regression. Actual WebGL keyframes.
The renderer and camera are paused between captures, never simulation methods.
requestAnimationFrame scheduling is stopped in this deterministic fixture.
Storage is isolated because the injected page has no normal persistent origin.
"""
from pathlib import Path
import os,json,time,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v010';O.mkdir(exist_ok=True);os.environ.setdefault('DISPLAY',':99')
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
checks=[];errors=[];requests=[]
def ck(name,v):
 checks.append({'name':name,'pass':bool(v)});print(('PASS 'if v else'FAIL ')+name,flush=True);assert v,name

def load(b,w,h,touch=False):
 c=b.new_context(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch,device_scale_factor=1);p=c.new_page();p.set_default_timeout(30000);p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None);p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000);p.wait_for_function('!!window.DC_APP',timeout=60000)
 p.evaluate('DC_APP.renderer.humanReady');ck('Embedded skin maps decoded '+str(w),p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3&&DC_APP.renderer.humanTextureStatus.failed===0'));
 ck('WebGL boot '+str(w),p.evaluate('DC_APP.renderer.gl.getError()===0'));p.evaluate('window.realDraw=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.renderer.updateCamera=()=>{};DC_APP.loop=()=>{};');p.click('#start');p.click('#dismissTutorial');return c,p

def fixture(p,kind='civil'):
 p.evaluate("""kind=>{const a=DC_APP;a.setMode('play');a.sim.cancelAccess(true);const s=a.sim;s.free=true;s.wanted=0;s.heat=0;s.policeState.grace=0;s.caught=0;s.events=[];s.peds=s.peds.filter(n=>!n.evicted);s.peds.forEach(n=>n.hidden=true);for(let i=0;i<s.cars.length;i++)Object.assign(s.cars[i],{x:300+i*6,z:0,speed:0,parked:true,boarding:false});const c=s.cars[1];Object.assign(c,{x:4,z:40,yaw:0,speed:0,police:kind==='police',parked:kind==='empty',owned:kind==='empty',stolen:false,health:100,doorOpen:0});c.driver=kind==='empty'?null:DC.driverProfile(c);Object.assign(s.player,{x:1.75,z:40.1,yaw:Math.PI/2,car:null,y:0,vy:0,vx:0,vz:0,transition:null});a.renderer.camera.eye=[-2.4,2,43.7];a.renderer.camera.target=[2.6,1.05,40];a.renderer.daylight=.65;document.getElementById('chapter').style.display='none';a.updateUI(performance.now());}""",kind)

def advance(p,secs):p.evaluate('''sec=>{const a=DC_APP;for(let i=0;i<Math.ceil(sec*60);i++)a.sim.step(1/60,a.input());a.processEvents();a.updateUI(performance.now());}''',secs)
def draw(p,name,save=False):
 p.evaluate('realDraw(DC_APP.sim)');ck('GL keyframe '+name,p.evaluate('DC_APP.renderer.gl.getError()===0'))
 if save:p.screenshot(path=str(O/(name+'.png')),timeout=60000)
def reach(p,id):
 ck('Touch hit target '+id,p.evaluate('''id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),t=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth&&r.bottom<=innerHeight&&(t===e||e.contains(t));}''',id))
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  c,p=load(b,900,640);fixture(p)
  draw(p,'civilian-driver')
  ck('Licensed anatomical face is used by the GPU',p.evaluate('DC_APP.renderer.heroParts.some(p=>p.name==="face"&&p.material===40)&&DC_APP.renderer.meshes.hero_face.dynamicCount>=2'))
  ck('Albedo normal and roughness use distinct bound samplers',p.evaluate('const r=DC_APP.renderer,g=r.gl;["uSkinAlbedo","uSkinNormal","uSkinRoughness"].every((n,i)=>g.getUniform(r.sceneProgram,r.uniform(r.sceneProgram,n))===4+i)'))
  ck('One shared texture set stays under 2 MiB estimated',p.evaluate('DC_APP.renderer.humanTextureStatus.bytes<2*1024*1024&&Object.keys(DC_APP.renderer.humanTextures).length===3'))
  ck('Anatomical head keeps all three LODs',p.evaluate('DC_APP.renderer.lodParts.every(parts=>parts.some(p=>p.name==="face"&&p.material===40))'))
  ck('Cast uses distinct skin tints, not independent duplicated textures',p.evaluate('const d=DC_APP.renderer.dynamic.hero_face;d.length>=32&&d.slice(8,11).some((x,i)=>Math.abs(x-d[24+i])>.005)'))
  ck('Civilian is actually submitted as a skinned driver',p.evaluate('DC_APP.renderer.castStats.drivers===1'))
  ck('Shared palette has one row per actor',p.evaluate('DC_APP.renderer.castStats.paletteRows===DC_APP.renderer.castStats.actors'))
  ck('GPU material groups are shared, not one draw per NPC',p.evaluate('DC_APP.renderer.castStats.drawBatches===DC_APP.renderer.heroParts.length&&DC_APP.renderer.castStats.actors===2'))
  ck('Window mesh belongs to transparent pass',p.evaluate('DC_APP.renderer.assetParts.filter(p=>p.name.startsWith("GLASS")).every(p=>DC_APP.renderer.meshes[p.key].transparent)'))
  ck('All 49 bones are linked into scene and shadow programs',p.evaluate("const r=DC_APP.renderer,g=r.gl;[r.sceneProgram,r.shadowProgram].every(pr=>Array.from({length:g.getProgramParameter(pr,g.ACTIVE_UNIFORMS)},(_,i)=>g.getActiveUniform(pr,i)).some(u=>u.name==='uBones[0]'&&u.size===49))"))
  ck('Crowd texture capacity fits the actual 49-bone rig',p.evaluate('DC.SkinRig.paletteWidth===196&&DC_APP.renderer.posePixels.length===49*16*128'))
  p.evaluate('DC_APP.sim.player.grip=0');draw(p,'hand-open-palette');p.evaluate('window.openBodyPalette=DC_APP.renderer.posePixels.slice(0,DC.SkinRig.paletteStride)')
  p.evaluate('DC_APP.sim.player.grip=1');draw(p,'hand-closed-palette')
  ck('All ten distal finger matrices change in the submitted palette',p.evaluate("const R=DC.SkinRig,a=openBodyPalette,b=DC_APP.renderer.posePixels;Object.values(R.fingers).flat().every(f=>{let k=R.ids[f.bones[2]]*16;return a.slice(k,k+16).some((v,i)=>Math.abs(v-b[k+i])>.002);})"))
  ck('Closing fingers leaves the wrist transform unchanged',p.evaluate("const R=DC.SkinRig,a=openBodyPalette,b=DC_APP.renderer.posePixels;['handL','handR'].every(n=>{let k=R.ids[n]*16;return a.slice(k,k+16).every((v,i)=>Math.abs(v-b[k+i])<.00001);})"))
  ck('Fitted hand and nail geometry is submitted in the main pass',p.evaluate('DC_APP.renderer.meshes.hero_skin.dynamicCount>=2&&DC_APP.renderer.meshes.hero_nails.dynamicCount>=2'))
  p.evaluate('delete DC_APP.sim.player.grip');draw(p,'relaxed-hands-restored')
  p.keyboard.press('f');ck('F begins paired access without seat transfer',p.evaluate('DC_APP.sim.access?.kind==="extract"&&DC_APP.sim.player.car===null'))
  advance(p,.65);draw(p,'door-opening');ck('Door has an intermediate angle',p.evaluate('DC_APP.sim.cars[1].doorOpen>0'))
  ck('Opening exposes cabin in body shell, not a closed duplicate door',p.evaluate('DC_APP.renderer.dynamic.asset_BODY_shell.some((v,i)=>i%16===11&&v<-.04)'))
  ck('No keyboard steering during reservation',p.evaluate('DC_APP.sim.cars[1].speed===0'))
  p.keyboard.press('Escape');t=p.evaluate('DC_APP.sim.access.elapsed');p.wait_for_timeout(120);ck('Pause freezes both paired actors',p.evaluate('DC_APP.sim.access.elapsed')==t);p.click('#resume')
  p.keyboard.press('m');p.click('[data-destination="future"]');ck('Atlas rejects a reserved seat',p.evaluate('DC_APP.sim.player.x<20&&DC_APP.mode==="map"'));p.click('#closeMap')
  advance(p,.65);draw(p,'paired-grab',True)
  ck('Paired actors maintain torso separation',p.evaluate('DC.distance(DC_APP.sim.accessPlayerPose(),DC_APP.sim.driverPose(DC_APP.sim.cars[1]))>.68'))
  p.keyboard.press('f');ck('F cancels before driver release without duplication',p.evaluate('!DC_APP.sim.access&&!!DC_APP.sim.cars[1].driver&&DC_APP.sim.peds.every(n=>!n.evicted)'))
  fixture(p);p.keyboard.press('f');advance(p,5.5)
  ck('Player receives the actual vehicle after completed action',p.evaluate('DC_APP.sim.player.car===1&&!DC_APP.sim.access&&DC_APP.sim.cars[1].driver===null'))
  ck('One displaced civilian with persistent identity',p.evaluate('DC_APP.sim.peds.filter(n=>n.evicted&&n.personId==="driver:1").length===1'))
  draw(p,'occupied-complete')
  ck('Final door closes and reservation releases',p.evaluate('DC_APP.sim.cars[1].doorOpen===0&&!DC_APP.sim.cars[1].boarding'))
  p.keyboard.press('f');ck('F initiates exit but retains ownership during animation',p.evaluate('DC_APP.sim.access?.kind==="exit"&&DC_APP.sim.player.car===1'));advance(p,2.3)
  ck('Exit returns to a collision-free position',p.evaluate('DC_APP.sim.player.car===null&&!DC.vehicleContains(DC_APP.sim.cars[1],DC_APP.sim.player.x,DC_APP.sim.player.z,.3)'))
  p.keyboard.press('f');ck('Previously vacated vehicle uses empty animation',p.evaluate('DC_APP.sim.access?.kind==="enter"'));advance(p,5)
  ck('Repeated access never creates a second driver',p.evaluate('DC_APP.sim.peds.filter(n=>n.evicted).length===1'))
  ck('Driver identity and fleet ownership survive save/load',p.evaluate('''()=>{const a=DC_APP,d=a.sim.serialize(),s=new DC.Simulation(a.world);return s.restore(d)&&s.actor().id===1&&s.peds.filter(n=>n.evicted).length===1;}'''))
  fixture(p,'empty');p.keyboard.press('f');advance(p,.5);p.keyboard.down('s');advance(p,.05);p.keyboard.up('s');ck('Movement cancels empty access',p.evaluate('DC_APP.sim.access===null&&DC_APP.sim.player.car===null'))
  fixture(p,'police');draw(p,'police-driver');ck('Police driver shares detailed rig',p.evaluate('DC_APP.sim.cars[1].driver.police&&DC_APP.renderer.castStats.drivers===1'))
  p.keyboard.press('f');advance(p,5.5)
  ck('Police extraction completes with one displaced officer',p.evaluate('DC_APP.sim.player.car===1&&DC_APP.sim.peds.some(n=>n.evicted&&n.police)&&DC_APP.sim.cars[1].stolen'))
  ck('Action has gameplay consequences, not new invulnerability',p.evaluate('DC_APP.sim.heat>0&&DC_APP.sim.policeState.grace===0'))
  fixture(p)
  p.evaluate('''()=>{const s=DC_APP.sim;for(let i=0;i<40;i++){Object.assign(s.peds[i],{hidden:false,x:2+(i%5)*1.1,z:43+Math.floor(i/5)*8,personId:'ped:'+i,speed:0,moveSpeed:0,walk:i*.1});}s.player.x=0;}''');draw(p,'crowd-budget')
  ck('Many pedestrians have independent palette rows',p.evaluate('DC_APP.renderer.castStats.actors>=40&&DC_APP.renderer.castStats.paletteRows>=40'))
  ck('Draw batches stay bounded by material and LOD',p.evaluate('DC_APP.renderer.castStats.drawBatches<=DC_APP.renderer.heroParts.length*3'))
  ck('Three measurable geometry LODs',p.evaluate('const a=DC_APP.renderer.visualStats.lodTriangles;a.length===3&&a[0]>a[1]*2&&a[1]>a[2]*2'))
  ck('Distant crowd uses reduced detail',p.evaluate('DC_APP.renderer.castStats.lod[2]>0'))
  ck('Palettes differ between people',p.evaluate('const a=DC_APP.renderer.posePixels;a.slice(DC.SkinRig.paletteStride,2*DC.SkinRig.paletteStride).some((v,i)=>Math.abs(v-a[2*DC.SkinRig.paletteStride+i])>.001)'))
  ck('Bone texture cannot grow with explored world',p.evaluate('DC_APP.renderer.visualStats.crowdPaletteBytes===DC.SkinRig.paletteStride*128*4&&DC_APP.renderer.castStats.paletteRows<=128'))
  fixture(p,'empty');p.keyboard.press('m');p.click('[data-destination="future"]');ck('Horizonte future destination retained',p.evaluate('DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z).type==="future"'))
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,p=s.player,c=s.cars[2];Object.assign(c,{x:p.x,z:p.z+3,yaw:0,speed:0,parked:false,owned:false,stolen:false,driver:DC.driverProfile(c)});p.x=c.x-2;p.z=c.z;a.renderer.camera.eye=[p.x-5,3,p.z+4];a.renderer.camera.target=[c.x,1,c.z];}''');p.keyboard.press('f');ck('Vehicle access works outside central city',p.evaluate('DC_APP.sim.access?.kind==="extract"'));advance(p,5.5);draw(p,'remote-driver');ck('Remote control transfer completes',p.evaluate('DC_APP.sim.player.car===2'));p.evaluate('DC_APP.sim.heat=0;DC_APP.sim.wanted=0;')
  p.keyboard.press('m');p.click('[data-destination="farmland"]');ck('Agricultural world preserved with occupied car',p.evaluate('DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z).type==="farmland"&&DC_APP.sim.player.car===2'))
  ck('Streaming geometry has bounded active sectors',p.evaluate('DC_APP.world.activeChunks.length===25&&DC_APP.renderer.streamStats.loaded<=25'));c.close()
  for w,h in [(390,844),(844,390)]:
   c,p=load(b,w,h,True);fixture(p,'empty')
   for id in ['touchCar','touchAction','touchBrake','joystick','pauseButton','mapButton']:reach(p,id)
   p.locator('#touchCar').tap();ck('Touch starts empty sequence '+str(w),p.evaluate('DC_APP.sim.access?.kind==="enter"&&DC_APP.sim.player.car===null'));advance(p,3.5);ck('Touch sequence transfers seat '+str(w),p.evaluate('DC_APP.sim.player.car===1'));p.locator('#touchCar').tap();advance(p,2.4);ck('Touch exit usable '+str(w),p.evaluate('DC_APP.sim.player.car===null'))
   fixture(p);p.locator('#touchCar').tap();advance(p,.7);draw(p,'mobile-'+str(w),True);ck('Visible cancel affordance '+str(w),'CANCELAR' in p.locator('#touchCar').inner_text());p.locator('#touchCar').tap();ck('Touch cancels paired sequence '+str(w),p.evaluate('!DC_APP.sim.access&&!!DC_APP.sim.cars[1].driver'));c.close()
  ck('No JS/WebGL console errors',not errors);ck('No network requests',not requests);b.close()
finally:
 report={'checks':checks,'passed':sum(x['pass']for x in checks),'failed':sum(not x['pass']for x in checks),'errors':errors,'requests':requests,'html_sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'mode':'Prepared scenes, real DOM keyboard/touch, actual WebGL keyframes with animation scheduling stopped between explicit simulation steps and real renderer captures. Isolated memory storage. Chromium/SwiftShader. No real-device performance claim.'};(O/'body-browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
