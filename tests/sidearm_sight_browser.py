"""Prepared production-renderer eye/sight contact and action continuity.
Fixtures are not native persistence, physical optics or hardware frame timings.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json,os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1]
O=Path(os.environ.get('DC_SIGHT_OUTPUT',str(R/('qa/v020/sight' if os.environ.get('DC_QA_RUN_ID') else 'artifacts/sight-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')))))
O.mkdir(parents=True,exist_ok=False)
html=Path(os.environ.get('DC_SIGHT_HTML',str(R/'index.html'))).read_text();sha=hashlib.sha256(html.encode()).hexdigest()
comparison=bool(os.environ.get('DC_SIGHT_HTML'));checks=[];errors=[];requests=[];cases=[]
FIX="""(()=>{const m=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',rain:false,bloom:false,sound:false})]]);window.qaSightStore=m;Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}});})();"""
def ck(name,value):
 checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True)
 if not comparison:assert value,name
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(**launch_options());p=b.new_page(viewport={'width':820,'height':680});p.set_default_timeout(45000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=120000);p.wait_for_function('!!window.DC_APP',timeout=120000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Embedded skin maps decode in the production renderer',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3'))
  p.click('#start');p.fill('#characterName','Referencia ocular');p.fill('#newSaveName','Inspección aislada');p.click('#commitCreator');p.click('#dismissTutorial')
  for helper in ['manual_frames.js','sidearm_sight.js']:p.add_script_tag(content=(R/'tools/qa'/helper).read_text())
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,r=a.renderer;DC_MANUAL_FRAMES.start(a);s.free=true;s.wanted=s.heat=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach(c=>Object.assign(c,{x:5000,z:5000,driver:null}));s.dynamics.props=[];Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0});r.rain=r.bloom=0;r.daylight=.67;r.previewStudio=false;r.fovOverride=.62;r.lightTime=-1;
   const draw=r.drawEquipment;r.drawEquipment=function(s,m,e){window.qaSightMount=m;return draw.call(this,s,m,e);};window.sightStoreBefore=JSON.stringify([...qaSightStore]);}''')
  css=p.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
  for item in ['pistol','revolver']:
   for pose in ['neutral','crouch','up','down']:
    v=p.evaluate('''c=>{const a=DC_APP,s=a.sim,r=a.renderer;s.equipWeapon(c.item);DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.equipment.handling.kick=0;s.time=1.25;s.player.crouch=c.pose==='crouch'?1:0;s.appearance.neckLength=c.pose==='up'?1:c.pose==='down'?-1:0;s.equipment.aimWeight=1;s.equipment.pitch=c.pose==='up'?.3:c.pose==='down'?-.3:0;s.equipment.reloading=0;r.motionTracker.clear();r.motionScene=s;
     r.camera.target=[4.015,1.40-s.player.crouch*.22,36.25];r.camera.eye=[5.6,1.54-s.player.crouch*.22,36.9];DC_MANUAL_FRAMES.draw(a);
     return DC_SIDEARM_SIGHT_QA.inspect(s,{mount:qaSightMount,pose:{matrices:r.heroPalette,rootY:r.motionDebug.rootY,scale:1}});}''',{'item':item,'pose':pose})
    cases.append({'name':item+'-'+pose,**v});ck(item+' '+pose+' posed eye aligns with visible sights',v['error']<.010);ck(item+' '+pose+' has a forward sight and reachable palms',v['behind']>.16 and all(e<.012 for e in v['contacts'].values()))
    p.screenshot(path=str(O/(item+'-'+pose+'.png')))
    if pose=='neutral':
     p.evaluate('''()=>{const r=DC_APP.renderer;r.camera.eye=[3.9,1.55,37.85];DC_MANUAL_FRAMES.draw(DC_APP);}''');p.screenshot(path=str(O/(item+'-front.png')))
  p.evaluate('''()=>{const s=DC_APP.sim;s.equipWeapon('pistol');DC.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;s.appearance.neckLength=0;s.player.crouch=0;s.equipment.pitch=0;s.equipment.reloading=0;s.equipment.aimWeight=1;s.equipment.handling.kick=0;s.equipment.ammo.pistol.loaded=0;window.sightReserve=s.equipment.ammo.pistol.reserve;s.reloadWeapon();window.sightLast=null;window.sightMaxStep=0;}''')
  for block in range(10):
   p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<15;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=DC.Equipment.mount(s);if(sightLast)sightMaxStep=Math.max(sightMaxStep,Math.hypot(...m.origin.map((x,j)=>x-sightLast[j])));sightLast=m.origin;}DC_MANUAL_FRAMES.draw(a);}''')
   if block in [0,2,4,9]:p.screenshot(path=str(O/f'reload-{block}.png'))
  ck('Reload mount moves continuously at native simulation steps',p.evaluate('sightMaxStep<.03'))
  ck('Reload transfers ammunition once and returns to the eye reference',p.evaluate('DC_APP.sim.equipment.ammo.pistol.loaded===12&&DC_APP.sim.equipment.ammo.pistol.reserve===sightReserve-12&&DC_SIDEARM_SIGHT_QA.inspect(DC_APP.sim).error<.003'))
  # Test the visual firing impulse independently of a prepared target hit.
  v=p.evaluate('''()=>{const s=DC_APP.sim;s.equipment.handling.kick=0;s.equipment.handling.velocity=0;const before=DC.Equipment.mount(s);s.equipment.shotSerial++;DC.WeaponHandling.step(s,1/60);DC_MANUAL_FRAMES.draw(DC_APP);return qaSightMount.muzzle[1]-before.muzzle[1];}''')
  ck('Recoil rises instead of dropping to the old unaligned pose',v>.002)
  p.screenshot(path=str(O/'recoil.png'))
  css.evaluate('(e)=>e.remove()');p.evaluate('DC_APP.setMode("play")');p.keyboard.press('Tab');p.wait_for_function('DC_APP.mode==="arsenal"')
  ck('Translucent selector remains paused and blocks game actions',p.evaluate('getComputedStyle(document.getElementById("arsenal")).backgroundColor.startsWith("rgba")&&!DC_APP.sim.equipment.trigger'))
  p.keyboard.press('Escape');ck('Closing selection does not restore a trigger or aiming request',p.evaluate('!DC_APP.sim.equipment.trigger&&!DC_APP.sim.equipment.aiming&&DC_APP.sim.equipment.charge===0'))
  ck('Visual inspection never overwrites the saved catalogue',p.evaluate('JSON.stringify([...qaSightStore])===sightStoreBefore'))
  ck('No JavaScript or graphics exceptions or external requests',not errors and not requests)
  b.close()
finally:
 report={'sha256':sha,'checks':checks,'errors':errors,'requests':requests,'cases':cases,'nativeStorage':False,'physicalGpu':False,'comparisonOnly':comparison,'note':'Actual eye-mesh bounds, production-renderer palette and visible sight top surfaces. Prepared camera/time; no optical physics, first-person aim or full anatomical acceptance.'}
 (O/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 if os.environ.get('DC_QA_RUN_ID'):(O.parent/'sidearm-sight.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print(json.dumps({'checks':len(checks),'pass':sum(c['pass'] for c in checks),'output':str(O)}),flush=True)
