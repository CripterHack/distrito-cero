"""Production-renderer sidearm hand contact. Prepared scenes, clock and storage fixture.
Not clinical hand geometry, complete autocolllision or a hardware benchmark.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1]
O=Path(os.environ.get('DC_SIDEARM_OUTPUT',str(R/('qa/v019/sidearm-support' if os.environ.get('DC_QA_RUN_ID') else 'artifacts/sidearms-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')))))
O.mkdir(parents=True,exist_ok=False)
html=Path(os.environ.get('DC_SIDEARM_HTML',str(R/'index.html'))).read_text();sha=hashlib.sha256(html.encode()).hexdigest()
comparison=bool(os.environ.get('DC_SIDEARM_HTML'));checks=[];errors=[];requests=[];cases=[]
FIX="""(()=>{const m=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',rain:false,bloom:false,sound:false})]]);window.qaSupportStorage=m;Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}});})();"""
def ck(name,value):
 checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True)
 if not comparison:assert value,name
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(**launch_options());p=b.new_page(viewport={'width':800,'height':720});p.set_default_timeout(45000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=120000);p.wait_for_function('!!window.DC_APP',timeout=120000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Three embedded skin textures decode in the production renderer',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3'))
  p.click('#start');p.fill('#characterName','Contacto entre manos');p.fill('#newSaveName','Prueba aislada');p.click('#commitCreator');p.click('#dismissTutorial')
  for helper in ['manual_frames.js','finger_surfaces.js','hand_support_surfaces.js']:p.add_script_tag(content=(R/'tools/qa'/helper).read_text())
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,r=a.renderer;DC_MANUAL_FRAMES.start(a);s.free=true;s.wanted=s.heat=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach(c=>Object.assign(c,{x:5000,z:5000,driver:null}));s.dynamics.props=[];Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0});r.motionTracker.clear();r.motionScene=s;r.rain=r.bloom=0;r.daylight=.67;r.previewStudio=false;r.fovOverride=.62;r.lightTime=-1;
   const draw=r.drawEquipment;r.drawEquipment=function(s,m,e){window.qaSupportMount=m;return draw.call(this,s,m,e);};window.storageBefore=JSON.stringify([...qaSupportStorage]);}''')
  css=p.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
  for item in ['pistol','revolver']:
   for pose in ['aim','use','crouch']:
    v=p.evaluate('''c=>{const a=DC_APP,s=a.sim,r=a.renderer;s.equipWeapon(c.item);DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.equipment.handling.triggerWeight=c.pose==='use'?1:0;s.time=1.25;s.player.crouch=c.pose==='crouch'?1:0;s.equipment.aimWeight=1;s.equipment.pitch=c.pose==='crouch'?.3:0;s.equipment.reloading=0;r.motionTracker.clear();r.motionScene=s;DC_MANUAL_FRAMES.draw(a);
     const m=qaSupportMount,palm=m.palmContacts.L,offset=m.direction([-.20,-.16,.24]);r.camera.target=[palm.x+.03,palm.y-.015,palm.z+.03];r.camera.eye=r.camera.target.map((n,i)=>n+offset[i]);DC_MANUAL_FRAMES.draw(a);
     const q={matrices:r.heroPalette,rootY:r.motionDebug.rootY,scale:1},rendered={mount:qaSupportMount,pose:q};return{hands:DC_HAND_SUPPORT_QA.report(s,rendered).values,prop:Object.fromEntries(['index','middle','ring','little','thumb'].map(f=>[f,DC_FINGER_QA.stats(s,'L',f,'grip',rendered)])),frame:r.frame,contacts:r.equipmentStats.contacts};}''',{'item':item,'pose':pose})
    name=item+'-'+pose;cases.append({'name':name,**v})
    ck(name+' skin remains outside the opposing digit envelopes',all(d['min']>-.002 for d in v['hands'].values()))
    ck(name+' support skin remains outside the handle',all(d['min']>-.003 for d in v['prop'].values()))
    p.screenshot(path=str(O/(name+'.png')))
  ck('Rendered palm contacts stay reachable in every sampled pose',all(v['contacts'] and all(c['reachError']<.012 for c in v['contacts'].values()) for v in cases))
  # Native reload simulation, with a settled ready/aim pose. No global RAF replacement.
  p.evaluate('''()=>{const s=DC_APP.sim;s.equipWeapon('pistol');DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.player.crouch=0;s.equipment.ammo.pistol.loaded=0;s.equipment.reloading=0;s.equipment.aiming=true;s.equipment.aimWeight=1;window.reserveBefore=s.equipment.ammo.pistol.reserve;s.reloadWeapon();window.lastSupport=null;window.maxSupportStep=0;}''')
  for block in range(12):
   p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<15;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=DC.Equipment.mount(s),v=Object.values(m.grips.L.fingers).flat().concat(m.grips.L.thumbOpposition||[0,0,0]);if(lastSupport)maxSupportStep=Math.max(maxSupportStep,...v.map((n,j)=>Math.abs(n-lastSupport[j])));lastSupport=v;}DC_MANUAL_FRAMES.draw(a);}''')
   if block in [0,2,4,6,11]:p.screenshot(path=str(O/f'reload-{block:02}.png'))
  ck('Support hand returns without a discrete finger pose jump',p.evaluate('maxSupportStep<.25'))
  ck('Ammunition transfers once using the existing reload logic',p.evaluate('DC_APP.sim.equipment.reloading===0&&DC_APP.sim.equipment.ammo.pistol.loaded===12&&DC_APP.sim.equipment.ammo.pistol.reserve===reserveBefore-12'))
  ck('Presentation never overwrites the saved catalogue',p.evaluate('JSON.stringify([...qaSupportStorage])===storageBefore'))
  css.evaluate('(e)=>e.remove()');p.evaluate('DC_APP.setMode("play")');p.keyboard.press('Tab');p.wait_for_function('DC_APP.mode==="arsenal"')
  ck('Translucent equipment selector still blocks and overlays the game',p.evaluate('getComputedStyle(document.getElementById("arsenal")).backgroundColor.startsWith("rgba")&&DC_APP.mode==="arsenal"'))
  p.keyboard.press('Escape');p.keyboard.press('b');p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<90;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}DC_MANUAL_FRAMES.draw(a);}''')
  ck('Optics retain their previously verified palm contacts',p.evaluate('Object.values(DC_APP.renderer.equipmentStats.contacts).every(c=>c.reachError<.012)'))
  ck('No runtime JavaScript errors or external resource requests',not errors and not requests)
  b.close()
finally:
 report={'sha256':sha,'checks':checks,'errors':errors,'requests':requests,'cases':cases,'nativeStorage':False,'physicalGpu':False,'comparisonOnly':comparison,'note':'Prepared camera and clock. Quantized skin samples against independent opposite-digit envelopes and fictional prop proxy, not all inter-hand topology. Renderer frame completion is checked.'}
 (O/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if os.environ.get('DC_QA_RUN_ID'):(O.parent/'sidearm-support.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'checks':len(checks),'pass':sum(c['pass']for c in checks),'output':str(O)}),flush=True)
