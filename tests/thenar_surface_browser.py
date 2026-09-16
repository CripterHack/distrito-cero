"""Prepared WebGL evidence of the full palm/thumb band. Storage fixture, not FPS.
An explicit baseline HTML records the original failing measurements for comparison.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1]
O=Path(os.environ.get('DC_THENAR_OUTPUT',str(R/('qa/v019/thenar' if os.environ.get('DC_QA_RUN_ID') else 'artifacts/thenar-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')))))
O.mkdir(parents=True,exist_ok=False)
html=Path(os.environ.get('DC_THENAR_HTML',str(R/'index.html'))).read_text();sha=hashlib.sha256(html.encode()).hexdigest()
comparison=bool(os.environ.get('DC_THENAR_HTML'));checks=[];errors=[];requests=[];cases=[]
FIX="""(()=>{const m=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',rain:false,bloom:false,sound:false})]]);window.qaThenarStorage=m;Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}});})();"""
def ck(name,value):
 checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True)
 if not comparison:assert value,name
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(**launch_options());p=b.new_page(viewport={'width':800,'height':720});p.set_default_timeout(45000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=120000);p.wait_for_function('!!window.DC_APP',timeout=120000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Three embedded skin maps decode in the actual renderer',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3'))
  p.click('#start');p.fill('#characterName','Palma y pulgar');p.fill('#newSaveName','Prueba aislada');p.click('#commitCreator');p.click('#dismissTutorial')
  for h in ['manual_frames.js','finger_surfaces.js','thenar_surfaces.js']:p.add_script_tag(content=(R/'tools/qa'/h).read_text())
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,r=a.renderer;DC_MANUAL_FRAMES.start(a);s.free=true;s.wanted=s.heat=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach(c=>Object.assign(c,{x:5000,z:5000,driver:null}));s.dynamics.props=[];Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0});r.motionTracker.clear();r.motionScene=s;r.rain=r.bloom=0;r.daylight=.67;r.previewStudio=false;r.fovOverride=.62;r.lightTime=-1;const draw=r.drawEquipment;r.drawEquipment=function(s,m,e){window.qaThenarMount=m;return draw.call(this,s,m,e)};window.storageBefore=JSON.stringify([...qaThenarStorage]);}''')
  css=p.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
  definitions=[('rifle','L','fore',0,0),('rifle','L','fore',0,1),('rifle','L','magazine',.5,0),('pistol','L','pistolMagazine',.5,0),('pistol','R','grip',0,0),('pistol','L','grip',0,0)]
  for item,side,key,progress,crouch in definitions:
   v=p.evaluate('''c=>{const a=DC_APP,s=a.sim,r=a.renderer;s.equipWeapon(c.item);DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.time=1.25;s.player.crouch=c.crouch;s.equipment.aiming=true;s.equipment.aimWeight=1;s.equipment.pitch=c.crouch?.3:0;s.equipment.reloading=c.progress?(1-c.progress)*DC.Equipment.get(c.item).reload:0;r.motionTracker.clear();r.motionScene=s;DC_MANUAL_FRAMES.draw(a);
    const m=qaThenarMount,palm=m.palmContacts[c.side],offset=m.direction([c.side==='R'?.19:-.19,-.19,.23]);r.camera.target=[palm.x,palm.y-.012,palm.z+.015];r.camera.eye=r.camera.target.map((v,i)=>v+offset[i]);DC_MANUAL_FRAMES.draw(a);
    const q={matrices:r.heroPalette,rootY:r.motionDebug.rootY,scale:1},rendered={mount:qaThenarMount,pose:q};return{surface:DC_THENAR_QA.stats(s,c.side,c.key,rendered),frame:r.frame,contacts:r.equipmentStats.contacts,camera:{eye:r.camera.eye.slice(),target:r.camera.target.slice()}};}''',{'item':item,'side':side,'key':key,'progress':progress,'crouch':crouch})
   name=f'{item}-{side}-{key}-c{crouch}';cases.append({'name':name,**v});ck(name+' full thenar band remains outside the prop within 1 mm tolerance',v['surface']['min']>-.001);p.screenshot(path=str(O/(name+'.png')))
  ck('Fixed surface cohort includes the same 806 left and 803 right vertices',p.evaluate('DC_THENAR_QA.samples.L.length===806&&DC_THENAR_QA.samples.R.length===803'))
  ck('All inspected palms preserve reachable original contact targets',all(v['contacts'] and all(c['reachError']<.012 for c in v['contacts'].values())for v in cases))
  p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.equipWeapon('rifle');DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.player.crouch=0;s.equipment.aiming=true;s.equipment.aimWeight=1;s.equipment.reloading=0;s.equipment.ammo.rifle.loaded=4;window.reserveBefore=s.equipment.ammo.rifle.reserve;s.reloadWeapon();window.lastPalm=null;window.maxPalmStep=0;}''')
  for block in range(12):
   p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<15;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=DC.Equipment.mount(s),q=DC.SkinRig.pose(DC.WeaponHandling.actor(s.player,m,s.equipment),s.time),dq=DC.DualQuaternion.pack(q.matrices),v=DC_THENAR_QA.samples.L[400];const point=DC.DualQuaternion.transform(dq,v.p,v.j,v.w);if(lastPalm)maxPalmStep=Math.max(maxPalmStep,Math.hypot(...point.map((v,k)=>v-lastPalm[k])));lastPalm=point;}DC_MANUAL_FRAMES.draw(a);}''')
   if block in[0,2,4,6,11]:p.screenshot(path=str(O/f'reload-{block:02}.png'))
  ck('Settled native reload retains continuous sampled surface travel',p.evaluate('maxPalmStep<.035'))
  ck('Reload keeps the original single ammunition transfer',p.evaluate('DC_APP.sim.equipment.reloading===0&&DC_APP.sim.equipment.ammo.rifle.loaded===30&&DC_APP.sim.equipment.ammo.rifle.reserve===reserveBefore-26'))
  css.evaluate('(e)=>e.remove()');p.evaluate('DC_APP.setMode("play")');p.keyboard.press('Tab');p.wait_for_function('DC_APP.mode==="arsenal"')
  ck('Equipment selector still overlays and pauses the scene',p.evaluate('getComputedStyle(document.getElementById("arsenal")).backgroundColor.startsWith("rgba")'))
  p.keyboard.press('Escape');p.keyboard.press('b');p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<90;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}DC_MANUAL_FRAMES.draw(a);}''')
  ck('Binoculars still draw with their established palm contacts',p.evaluate('Object.values(DC_APP.renderer.equipmentStats.contacts).every(c=>c.reachError<.012)'))
  ck('Surface inspection does not overwrite the saved catalogue',p.evaluate('JSON.stringify([...qaThenarStorage])===storageBefore'))
  ck('No runtime exceptions or external requests',not errors and not requests)
  b.close()
finally:
 report={'sha256':sha,'checks':checks,'errors':errors,'requests':requests,'cases':cases,'nativeStorage':False,'physicalGpu':False,'comparisonOnly':comparison,'note':'Prepared cameras and clock, fixed geometric cohort (no influence threshold), actual renderer DQ palette. Cosmetic proxies, not general self-collision.'}
 (O/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if os.environ.get('DC_QA_RUN_ID'):(O.parent/'thenar.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'checks':len(checks),'passed':sum(c['pass']for c in checks),'output':str(O)}),flush=True)
