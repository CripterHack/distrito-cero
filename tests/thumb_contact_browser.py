"""Thumb opposition surfaces in the production renderer. Prepared scenes and clock.
No hardware FPS claim. Uses an explicit storage fixture, not native persistence.
A baseline HTML can be captured separately via DC_THUMB_HTML for visual review.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1]
O=Path(os.environ.get('DC_THUMB_OUTPUT', str(R/('qa/v019/thumb-contact' if os.environ.get('DC_QA_RUN_ID') else 'artifacts/thumbs-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')))))
O.mkdir(parents=True,exist_ok=False)
html=Path(os.environ.get('DC_THUMB_HTML',str(R/'index.html'))).read_text()
sha=hashlib.sha256(html.encode()).hexdigest();checks=[];errors=[];requests=[];samples=[]
comparison=bool(os.environ.get('DC_THUMB_HTML'))
FIX="""(()=>{const m=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',rain:false,bloom:false,sound:false})]]);window.qaFingerStorage=m;Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}});})();"""
def ck(name,value):
 checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True)
 if not comparison: assert value,name
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(**launch_options());p=browser.new_page(viewport={'width':720,'height':720});p.set_default_timeout(45000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=120000);p.wait_for_function('!!window.DC_APP',timeout=120000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Production renderer decodes all three embedded skin maps',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3'))
  p.click('#start');p.fill('#characterName','Contacto digital');p.fill('#newSaveName','Prueba de dedos');p.click('#commitCreator');p.click('#dismissTutorial')
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,r=a.renderer;a.stopFrame();s.free=true;s.wanted=s.heat=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach(c=>Object.assign(c,{x:5000,z:5000,driver:null}));s.dynamics.props=[];Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0});r.motionTracker.clear();r.motionScene=s;r.rain=r.bloom=0;r.daylight=.67;r.previewStudio=false;r.fovOverride=.62;r.lightTime=-1;
   const draw=r.drawEquipment;r.drawEquipment=function(s,m,e){window.qaDrawnMount=m;return draw.call(this,s,m,e);};
   window.storageBefore=JSON.stringify([...qaFingerStorage]);}''')
  p.add_script_tag(content=(R/'tools/qa/finger_surfaces.js').read_text())
  css=p.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
  cases=[('rifle','R','grip',0),('rifle','L','fore',0),('rifle','L','magazine',.5),('pistol','L','pistolMagazine',.5),('gauss','R','grip',0),('emp','L','magazine',.5)]
  for item,side,volume,progress in cases:
   value=p.evaluate('''c=>{const a=DC_APP,s=a.sim,r=a.renderer;s.equipWeapon(c.item);s.equipment.handling.ready=1;s.time=1.25;s.player.crouch=0;s.equipment.aimWeight=1;s.equipment.pitch=0;s.equipment.reloading=c.progress?(1-c.progress)*DC.Equipment.get(c.item).reload:0;r.motionTracker.clear();r.motionScene=s;
    r.render(s);let m=qaDrawnMount,palm=m.palmContacts[c.side],offset=m.direction([c.side==='R'?.30:-.30,.19,-.19]);r.camera.target=[palm.x,palm.y-.015,palm.z+.01];r.camera.eye=r.camera.target.map((v,i)=>v+offset[i]);r.render(s);r.gl.finish();
    const q={matrices:r.heroPalette,rootY:r.motionDebug.rootY,scale:1},names=['thumb'];return{minimums:Object.fromEntries(names.map(n=>[n,DC_FINGER_QA.stats(s,c.side,n,c.volume,{mount:qaDrawnMount,pose:q})])),gl:r.gl.getError(),contacts:r.equipmentStats.contacts,frame:r.frame};}''',{'item':item,'side':side,'volume':volume,'progress':progress})
   name=f'{item}-{side}-{volume}';samples.append({'name':name,**value})
   ck(name+' rendered skin stays outside the contact volume',all(v['min']>-.003 and v['min']<.009 for v in value['minimums'].values()))
   p.screenshot(path=str(O/(name+'.png')))
  ck('All sampled draws retain finite oriented palm contacts and no WebGL errors',all(v['gl']==0 and v['contacts'] and all(c['reachError']<.012 for c in v['contacts'].values()) for v in samples))
  # Check authored phases and native inventory transfer, not only static keyframes.
  p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.equipWeapon('rifle');s.equipment.handling.ready=1;s.equipment.aimWeight=1;s.equipment.aiming=true;s.equipment.ammo.rifle.loaded=4;window.ammoBefore=s.equipment.ammo.rifle.reserve;s.equipment.reloading=0;s.reloadWeapon();window.lastThumb=null;window.maxThumbStep=0;}''')
  for block in range(12):
   v=p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<15;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=DC.Equipment.mount(s),q=DC.SkinRig.pose(DC.WeaponHandling.actor(s.player,m,s.equipment),s.time),f=DC.SkinRig.fingers.L.find(f=>f.name==='thumb'),j=DC.SkinRig.ids[f.bones[2]],v=DC.SkinRig.transform(q.matrices.subarray(j*16,j*16+16),f.tip);v[1]+=q.rootY;if(lastThumb)maxThumbStep=Math.max(maxThumbStep,Math.hypot(...v.map((x,i)=>x-lastThumb[i])));lastThumb=v;}a.renderer.render(s);a.renderer.gl.finish();return a.renderer.gl.getError();}''')
   assert v==0
   if block in [0,2,4,6,8,11]:p.screenshot(path=str(O/f'reload-{block:02}.png'))
  ck('Reload thumb tip follows a continuous trajectory at native time steps',p.evaluate('maxThumbStep<.035'))
  ck('Reload still transfers ammunition once and returns to support',p.evaluate('DC_APP.sim.equipment.ammo.rifle.loaded===30&&DC_APP.sim.equipment.ammo.rifle.reserve===ammoBefore-26&&DC_APP.sim.equipment.reloading===0'))
  css.evaluate('(e)=>e.remove()')
  p.evaluate('DC_APP.setMode("play")');p.keyboard.press('Tab');p.wait_for_function('DC_APP.mode==="arsenal"')
  ck('Translucent selector remains above the real scene',p.evaluate('getComputedStyle(document.getElementById("arsenal")).backgroundColor.startsWith("rgba")'))
  p.keyboard.press('Escape');p.keyboard.press('b');p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<60;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}a.renderer.render(s);a.renderer.gl.finish();}''')
  ck('Binoculars preserve their previous contact and optical posture',p.evaluate('DC_APP.sim.equipment.selected==="binoculars"&&Object.values(DC_APP.renderer.equipmentStats.contacts).every(c=>c.reachError<.012)&&DC_APP.renderer.gl.getError()===0'))
  ck('Presentation inspection never writes the saved catalogue',p.evaluate('JSON.stringify([...qaFingerStorage])===storageBefore'))
  ck('Existing four finger contact profiles are preserved and reused',p.evaluate('DC.WeaponHandling.contactFitStats?DC.WeaponHandling.contactFitStats().cached===4:false'))
  ck('No JavaScript errors or external runtime requests',not errors and not requests)
  browser.close()
finally:
 report={'sha256':sha,'checks':checks,'errors':errors,'requests':requests,'samples':samples,'nativeStorage':False,'physicalGpu':False,'comparisonOnly':comparison,'note':'Prepared time/camera; DQ skin samples use the actual palette and mount passed to the production renderer. Thumb surfaces and existing DQ palette. Prepared scene/time, not gameplay FPS or full hand self-collision.'}
 (O.parent/'thumb-contact.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'checks':len(checks),'pass':sum(c['pass']for c in checks),'output':str(O)}),flush=True)
