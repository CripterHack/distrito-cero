"""#6: production renderer plus native equipment interpolation at 1/60 simulation steps.
The clock, camera and world placement are prepared, not a physical-GPU benchmark.
Storage is an explicit fixture. Native persistence is verified by its separate suite.
"""
from pathlib import Path
from datetime import datetime, timezone
import os, json, hashlib
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1]
O=R/('qa/v019/optical-shoulder' if os.environ.get('DC_QA_RUN_ID') else 'artifacts/optical-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
O.mkdir(parents=True,exist_ok=False)
report=O.parent/'optical-shoulder.json';checks=[];errors=[];requests=[];samples=[]
sha=hashlib.sha256((R/'index.html').read_bytes()).hexdigest()
FIX="""(()=>{const m=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}})})();"""
def ck(name,value):
 checks.append({'name':name,'pass':bool(value)});print(('PASS ' if value else 'FAIL ')+name,flush=True);assert value,name
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(**launch_options());p=b.new_page(viewport={'width':720,'height':720});p.set_default_timeout(45000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
  p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIX,1),timeout=120000);p.wait_for_function('!!window.DC_APP',timeout=120000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Production renderer boots with all three embedded skin maps',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3&&DC_APP.graphics.state==="ready"'))
  p.click('#start');p.fill('#characterName','Postura óptica');p.fill('#newSaveName','Trayectoria');p.click('#commitCreator');p.click('#dismissTutorial')
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,r=a.renderer;a.stopFrame();s.free=true;s.wanted=s.heat=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach(c=>Object.assign(c,{x:5000,z:5000,driver:null}));s.dynamics.props=[];Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0});r.motionTracker.clear();r.motionScene=s;r.rain=r.bloom=0;r.daylight=.67;r.previewStudio=false;r.fovOverride=.62;r.lightTime=-1;r.camera.eye=[5.2,1.13,38.2];r.camera.target=[4,1.08,36];}''')
  p.add_style_tag(content='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}')
  finite=True;contacts=True;gl_ok=True
  for crouch in [0,1]:
   p.evaluate('''c=>{const a=DC_APP,s=a.sim;s.equipWeapon('unarmed');s.equipWeapon('binoculars');s.equipment.handling.ready=1;s.player.crouch=c;s.time=1.25;s.equipment.aimWeight=0;window.inventory=JSON.stringify(DC.Equipment.snapshot(s.equipment));window.previousElbows=null;const y=1.08-c*.22;a.renderer.camera.target=[4,y,36];a.renderer.camera.eye=[5.2,y+.06,38.2];}''',crouch)
   worst_raise=0;worst_lower=0;above=0
   for block in range(10):
    v=p.evaluate('''block=>{const a=DC_APP,s=a.sim,D=DC;let worst=0,above=-1,finite=true;for(let k=0;k<15;k++){
     const i=block*15+k;s.time+=1/60;s.equipmentStep(1/60,{aim:i<75});const m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=D.SkinRig.pose(n,s.time),point=name=>{const j=D.SkinRig.ids[name];return D.SkinRig.transform(q.matrices.subarray(j*16,j*16+16),D.SkinRig.bones[j][2]);};
     const elbows=['L','R'].map(side=>point('forearm'+side));if(previousElbows)for(let j=0;j<2;j++)worst=Math.max(worst,Math.hypot(...elbows[j].map((v,d)=>v-previousElbows[j][d])));window.previousElbows=elbows;
     if(i===74)above=Math.max(...['L','R'].map(side=>point('forearm'+side)[1]-point('hand'+side)[1]));finite=finite&&Array.from(q.matrices).every(Number.isFinite);
    }a.renderer.render(s);a.renderer.gl.finish();return{worst,above,finite,gl:a.renderer.gl.getError(),contacts:a.renderer.equipmentStats.contacts,aim:s.equipment.aimWeight};}''',block)
    samples.append({'crouch':crouch,'block':block,**v});finite=finite and v['finite'];gl_ok=gl_ok and v['gl']==0;contacts=contacts and bool(v['contacts']) and all(c['reachError']<.012 and c['orientationError']<1e-4 for c in v['contacts'].values())
    if block<5:worst_raise=max(worst_raise,v['worst'])
    else:worst_lower=max(worst_lower,v['worst'])
    if block==4:above=v['above']
    if block in [0,3,4,5,9]:p.screenshot(path=str(O/f'c{crouch}-phase{block}.png'))
   ck(f'Optical raise has no elbow inversion at crouch={crouch}',worst_raise<.045)
   ck(f'Optical lower remains continuous at crouch={crouch}',worst_lower<.045)
   ck(f'Raised elbows remain below wrists at crouch={crouch}',above<.02)
   ck(f'Optical cycle leaves inventory and zoom intact at crouch={crouch}',p.evaluate('JSON.stringify(DC.Equipment.snapshot(DC_APP.sim.equipment))===inventory'))
  ck('Every rendered sample retains oriented hand contacts and finite matrices',finite and contacts and gl_ok)
  p.evaluate('''()=>{const s=DC_APP.sim;s.equipWeapon('rifle');s.equipment.handling.ready=1;s.player.crouch=0;s.equipment.ammo.rifle.loaded=5;window.beforeAmmo=s.equipment.ammo.rifle.reserve;s.reloadWeapon();}''')
  for block in range(12):
   p.evaluate('''()=>{const a=DC_APP,s=a.sim;for(let i=0;i<15;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}a.renderer.render(s);a.renderer.gl.finish();}''')
   if block in [2,5,11]:p.screenshot(path=str(O/f'rifle-reload-{block}.png'))
  ck('Firearm reload still transfers ammunition once with reachable support',p.evaluate('''()=>{const a=DC_APP,s=a.sim;return s.equipment.ammo.rifle.loaded===30&&s.equipment.ammo.rifle.reserve===beforeAmmo-25&&s.equipment.reloading===0&&Object.values(a.renderer.equipmentStats.contacts).every(c=>c.reachError<.012)&&a.renderer.gl.getError()===0;}'''))
  b.close()
 ck('HTML is unchanged by inspection',hashlib.sha256((R/'index.html').read_bytes()).hexdigest()==sha)
 ck('No JavaScript or console errors',not errors)
 ck('No external requests from the runtime',not requests)
finally:
 report.write_text(json.dumps({'sha256':sha,'checks':checks,'errors':errors,'requests':requests,'samples':samples,'nativeStorage':False,'physicalGpu':False,'timeControlled':True},ensure_ascii=False,indent=2)+'\n')
 print('REPORT',report,flush=True)
