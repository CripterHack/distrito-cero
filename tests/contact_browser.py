"""v0.19 acceptance: real WebGL keyframes, isolated localStorage, explicit simulation ticks.
The continuous suite separately retains RAF and unmodified renderer/camera/simulation.
"""
from pathlib import Path
import os, json, hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; O=R/'qa/v019'; os.environ.setdefault('DISPLAY',':99')
HTML=(R/'index.html').read_text(); checks=[]; errors=[]; requests=[]
FIX="""(()=>{window.testStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore.get(k)||null,setItem:(k,v)=>testStore.set(k,String(v)),removeItem:k=>testStore.delete(k)}});})();"""
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)}); print(('PASS ' if v else 'FAIL ')+n,flush=True); assert v,n

def tick(p,n=1,draw=False):
 try:
  p.evaluate('''({n,draw})=>{const a=DC_APP,s=a.sim;for(let i=0;i<n;i++)if(a.mode==='play'){s.step(1/60,a.input());a.renderer.updateCamera(s,1/60);}a.updateUI(performance.now());if(draw){a.renderer.render(s);a.renderer.gl.finish();}}''',{'n':n,'draw':draw})
 except Exception:
  state=p.evaluate('''()=>{const r=DC_APP.renderer,g=r.gl;return {contextLost:g.isContextLost(),error:g.getError(),current:!!g.getParameter(g.CURRENT_PROGRAM),scene:g.isProgram(r.sceneProgram),frame:r.frame,equipment:r.equipmentStats,mode:DC_APP.mode}}''')
  (O/'context-diagnostic.json').write_text(json.dumps(state,indent=2)); print('DIAGNOSTIC',state['contextLost'],state['error'],state['current'],flush=True)
  raise

def visible_hit(p,id):
 return p.evaluate('''id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth+.5&&r.bottom<=innerHeight+.5&&(h===e||e.contains(h));}''',id)

try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':900,'height':640});p.set_default_timeout(30000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text) if e.type=='error' else None);p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
  p.set_content(HTML.replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady');p.evaluate('window.requestAnimationFrame=()=>0;DC_APP.renderer.canvas.addEventListener("webglcontextlost",()=>console.error("contextlost: software GPU"))');p.wait_for_timeout(100)
  p.click('#start');p.fill('#characterName','Vega');p.fill('#newSaveName','Manejo y contacto');p.click('#commitCreator');p.click('#dismissTutorial')
  p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.free=true;s.heat=s.wanted=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach((c,i)=>Object.assign(c,{x:-270,z:-300-i*6,parked:true,speed:0}));Object.assign(s.player,{x:4,z:36,yaw:0,car:null,walk:0,moveSpeed:0,health:100,y:0});a.renderer.camera.yaw=0;a.renderer.camera.weaponPitch=-.025;a.renderer.daylight=.67;a.renderer.rain=0;}''')
  p.keyboard.press('9');tick(p,45,True)
  ck('Actual renderer uses oriented contacts for both hands',p.evaluate('Object.values(DC_APP.renderer.equipmentStats.contacts).every(c=>c.reachError<.012&&c.orientationError<.0001)'))
  ck('Palmar anchors are exposed independently of wrists',p.evaluate('!!DC_APP.renderer.equipmentStats.palms.L&&!!DC_APP.renderer.equipmentStats.palms.R'))
  ck('Skin-rig palm references coincide with actual renderer contacts',p.evaluate('''()=>{const a=DC_APP,r=a.renderer,q={matrices:r.heroPalette,scale:1,rootY:r.motionDebug.rootY},n=a.sim.player;return ['L','R'].every(k=>{const p=DC.SkinRig.palmPoint(q,n,k),t=r.equipmentStats.palms[k];return Math.hypot(p.x-t.x,p.y-t.y,p.z-t.z)<.012;});}'''))
  p.keyboard.press('z');tick(p,45,True)
  # Same gameplay view must remain beneath the translucent selector, even though inputs cancel.
  p.evaluate('window.camBefore=JSON.stringify(DC_APP.renderer.camera);window.fovBefore=DC_APP.renderer.fovOverride;window.mountBefore=DC.Equipment.mount(DC_APP.sim);window.ammoBefore=JSON.stringify(DC.Equipment.snapshot(DC_APP.sim.equipment));window.tBefore=DC_APP.sim.time')
  p.keyboard.press('Tab');tick(p,30,True)
  ck('Selector is a modal layered above the world canvas',p.locator('#arsenal').get_attribute('aria-modal')=='true' and p.locator('#world').is_visible())
  ck('World time stays paused while selector is open',p.evaluate('DC_APP.sim.time===tBefore'))
  ck('Camera and projection do not jump when opening',p.evaluate('JSON.stringify(DC_APP.renderer.camera)===camBefore&&DC_APP.renderer.fovOverride===fovBefore'))
  ck('Weapon pose is frozen before cancelling aim and trigger',p.evaluate('DC_APP.renderer.frozenHandling&&JSON.stringify(DC_APP.renderer.frozenHandling.mount.origin)===JSON.stringify(mountBefore.origin)'))
  ck('Ammunition is not changed by open or cancellation',p.evaluate('JSON.stringify(DC.Equipment.snapshot(DC_APP.sim.equipment))===ammoBefore'))
  styles=p.evaluate('''()=>Object.fromEntries(['arsenal','panel','card','detail','footer'].map(k=>{const e=k==='arsenal'?document.getElementById(k):document.querySelector(k==='panel'?'.arsenal-panel':k==='card'?'.weapon-card':k==='detail'?'.weapon-detail':'.arsenal-footer');const s=getComputedStyle(e);return[k,{background:s.backgroundColor,image:s.backgroundImage,opacity:s.opacity,blur:s.backdropFilter}];}))''')
  ck('Overlay alpha leaves the game readable beneath',styles['arsenal']['background'].startswith('rgba') and float(styles['arsenal']['background'].split(',')[-1].rstrip(')'))<=.25)
  ck('Main panel itself is translucent',styles['panel']['background'].startswith('rgba') and float(styles['panel']['background'].split(',')[-1].rstrip(')'))<.5)
  ck('Transparency is not applied to text or entire dialog',all(v['opacity']=='1' for v in styles.values()))
  ck('Cards and detail no longer have opaque backgrounds', 'rgba' in styles['card']['image'] and 'rgba' in styles['detail']['image'])
  p.screenshot(path=str(O/'selector-desktop.png'),timeout=90000)
  p.focus('#closeArsenal');p.keyboard.press('Shift+Tab');ck('Reverse Tab stays inside selector',p.evaluate('document.activeElement.id==="commitEquipment"'));p.keyboard.press('Tab');ck('Tab cycles back to the close button',p.evaluate('document.activeElement.id==="closeArsenal"'))
  p.keyboard.press('j');p.keyboard.press('f');p.keyboard.press('m');tick(p,10)
  ck('Gameplay keys cannot shoot or access vehicles behind the modal',p.evaluate('DC_APP.mode==="arsenal"&&DC_APP.sim.equipment.shots===0&&!DC_APP.sim.access'))
  p.click('[data-weapon="rifle"]');ck('Preview selection does not change equipped model',p.evaluate('DC_APP.sim.equipment.selected==="gauss"'))
  p.click('#commitEquipment');tick(p,40,True)
  ck('Confirm equips and releases the frozen pose',p.evaluate('DC_APP.sim.equipment.selected==="rifle"&&!DC_APP.renderer.frozenHandling&&DC_APP.mode==="play"'))
  ck('Equip click does not leak through to fire',p.evaluate('DC_APP.sim.equipment.shots===0'))
  ck('Focus returns to game after confirmation',p.evaluate('document.activeElement.id==="world"'))
  p.evaluate('DC_APP.sim.equipment.ammo.rifle.loaded=7');p.keyboard.press('l');tick(p,55,True)
  ck('Reload detaches the single visible magazine',p.evaluate('DC_APP.renderer.equipmentStats.magazine.offset[1]<-.12&&DC_APP.renderer.equipmentStats.phase==="Recargar"'))
  ck('Reload has a reachable supporting wrist orientation',p.evaluate('DC_APP.renderer.equipmentStats.contacts.L.reachError<.012'))
  p.evaluate('window.reloadRemainder=DC_APP.sim.equipment.reloading');p.keyboard.press('Tab');tick(p,80,True)
  ck('Opening selector pauses the current reload',p.evaluate('DC_APP.sim.equipment.reloading===reloadRemainder'))
  p.keyboard.press('Escape');tick(p,110,True)
  ck('Reload resumes and fills once after closing',p.evaluate('DC_APP.sim.equipment.reloading===0&&DC_APP.sim.equipment.ammo.rifle.loaded===30&&DC_APP.sim.equipment.ammo.rifle.reserve===127'))
  # Sample anatomy/weapon surfaces in moving and crouched poses, not only pivots at rest.
  contact_check=0
  for i in range(18):
   error=p.evaluate('''i=>{const a=DC_APP,s=a.sim,r=a.renderer;s.player.moveSpeed=i<9?3:0;s.player.walk+=.2;s.player.crouch=i>=9?1:0;s.equipment.pitch=Math.sin(i)*.35;s.time+=1/60;r.render(s);r.gl.finish();const q={matrices:r.heroPalette,scale:1,rootY:r.motionDebug.rootY};let max=0;for(const k of['L','R']){const p=DC.SkinRig.palmPoint(q,s.player,k),t=r.equipmentStats.palms[k];max=Math.max(max,Math.hypot(p.x-t.x,p.y-t.y,p.z-t.z));}return max;}''',i)
   contact_check=max(contact_check,error);p.wait_for_timeout(20)
  p.evaluate('Object.assign(DC_APP.sim.player,{moveSpeed:0,crouch:0,walk:0});DC_APP.sim.equipment.pitch=0')
  ck('Animated/crouched renderer maintains palmar contacts',contact_check<.012)
  p.evaluate('DC_APP.selectEquipment("pistol")');tick(p,50,True);p.keyboard.press('z');tick(p,50,True)
  ck('Sidearm aiming extends the dominant hand forward',p.evaluate('DC_APP.renderer.equipmentStats.hands.R.z-DC_APP.sim.player.z>.39'))
  ck('Aimed primary index remains relaxed without fire input',p.evaluate('DC_APP.renderer.equipmentStats.grips.R.fingers.index.reduce((s,v)=>s+v,0)<.5'))
  p.evaluate('DC_APP.selectEquipment("rifle")');tick(p,45,True);p.keyboard.press('z');tick(p,50,True)
  ck('Aimed stock and articulated shoulder share a close brace',p.evaluate('DC_APP.renderer.equipmentStats.brace.error<.035'))
  p.evaluate('DC_APP.sim.equipment.ammo.rifle.loaded=8;DC_APP.sim.reloadWeapon();DC_APP.sim.equipment.reloading=DC.Equipment.get("rifle").reload*.48;DC_APP.renderer.render(DC_APP.sim)')
  ck('Magazine has a visible cant during handling',p.evaluate('Math.abs(DC_APP.renderer.equipmentStats.magazine.rotation[2])>.1'))
  ck('Recarga has a distinct extraction phase',p.evaluate('DC_APP.renderer.equipmentStats.reloadStage==="Extraer"'))
  p.evaluate('DC_APP.sim.equipment.reloading=0;DC_APP.sim.equipment.reloadId=null')
  # All equipment still renders with the new contact convention.
  for wid in ['pistol','revolver','smg','shotgun','sniper','launcher','grenade','baton','blade','emp','binoculars']:
   p.evaluate('id=>DC_APP.selectEquipment(id)',wid);tick(p,35,True)
   ck('Shared model and reachable contact: '+wid,p.evaluate('DC_APP.renderer.gl.getError()===0&&Object.values(DC_APP.renderer.equipmentStats.contacts||{}).every(c=>c.reachError<.012)'))
  p.evaluate('DC_APP.selectEquipment("rifle")');tick(p,40);p.keyboard.press('z');tick(p,45,True)
  p.evaluate('window.visibleAim=DC_APP.sim.equipment.aimWeight');p.keyboard.press('Tab');p.keyboard.press('Escape')
  ck('Closing selector preserves the visible aim blend',p.evaluate('Math.abs(DC_APP.sim.equipment.aimWeight-visibleAim)<.001'))
  tick(p,1,True);ck('Returning from selector lowers smoothly with no revived aim or trigger',p.evaluate('!DC_APP.sim.equipment.aiming&&!DC_APP.sim.equipment.trigger&&DC_APP.sim.equipment.aimWeight>0&&DC_APP.sim.equipment.aimWeight<visibleAim'))
  p.evaluate('DC_APP.selectEquipment("emp")')
  ck('New equipment is initialized in its lowered presentation before rendering',p.evaluate('DC_APP.sim.equipment.handling.item==="emp"&&DC_APP.sim.equipment.handling.ready===0'))
  p.keyboard.press('9');tick(p,40);p.keyboard.down('j');tick(p,45);p.keyboard.press('Tab');p.keyboard.up('j');p.keyboard.press('Escape');tick(p,4)
  ck('Cancelling a held Gauss charge never fires',p.evaluate('DC_APP.sim.equipment.shots===0&&DC_APP.sim.equipment.charge===0'))
  for width,height in[(390,844),(844,390)]:
   p.set_viewport_size({'width':width,'height':height});p.evaluate('DC_APP.setTouch(true)');tick(p,2,True);p.click('#openArsenal');tick(p,2,True)
   ck(f'Touch close and confirm reachable {width}',visible_hit(p,'closeArsenal') and visible_hit(p,'commitEquipment'))
   p.locator('[data-group="Tecnología"]').scroll_into_view_if_needed();p.click('[data-group="Tecnología"]');p.click('[data-weapon="emp"]');p.screenshot(path=str(O/f'selector-{width}.png'),timeout=90000)
   p.click('#commitEquipment');tick(p,40,True);ck(f'Touch selection retains playability {width}',p.evaluate('DC_APP.mode==="play"&&DC_APP.sim.equipment.selected==="emp"'))
  ck('No JS or shader error',not errors);ck('No external resource requests',not requests);ck('No final GL error',p.evaluate('DC_APP.renderer.gl.getError()===0'));b.close()
finally:
 report={'passed':sum(c['pass'] for c in checks),'failed':sum(not c['pass'] for c in checks),'checks':checks,'errors':errors,'requests':requests,'styles':locals().get('styles'),'sha256':hashlib.sha256(HTML.encode()).hexdigest(),'environment':'Chromium Xvfb SwiftShader. Explicit simulation ticks, real WebGL frames. In-memory storage fixture, mobile emulation. No physical GPU or persistence claim.'}
 (O/'handling-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print('RESULT',report['passed'],report['failed'],flush=True)
