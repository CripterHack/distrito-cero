"""v0.17 browser acceptance: native DOM inputs, explicit steps and real WebGL keyframes.
This suite pauses RAF scheduling after boot. See arsenal_continuous.py for the native loop.
"""
from pathlib import Path
import os,json,hashlib,time
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v018';os.environ.setdefault('DISPLAY',':99');checks=[];errors=[];requests=[]
HTML=(R/'index.html').read_text()
FIX="""(()=>{window.testStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore.get(k)||null,setItem:(k,v)=>testStore.set(k,String(v)),removeItem:k=>testStore.delete(k)}});})();"""
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(('PASS 'if v else'FAIL ')+n,flush=True);assert v,n

def tick(p,n=1,draw=False):
 return p.evaluate('''({n,draw})=>{const a=DC_APP,s=a.sim;for(let i=0;i<n;i++){if(a.mode==='play')s.step(1/60,a.input());a.renderer.updateCamera(s,1/60,{menu:a.mode==='menu',photo:a.mode==='photo'});}a.processEvents();a.updateUI(performance.now());if(draw)a.renderer.render(s);return {shots:s.equipment.shots,gl:a.renderer.gl.getError()};}''',{'n':n,'draw':draw})

def scene(p):
 p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.free=true;s.story=0;s.heat=s.wanted=0;s.time=7;s.shotHeatUntil=0;for(let i=0;i<s.cars.length;i++)Object.assign(s.cars[i],{x:-260,z:-300-i*5,parked:true,speed:0,empUntil:0});s.peds.forEach(n=>n.hidden=true);Object.assign(s.player,{x:4,z:36,yaw:0,car:null,y:0,health:100,vx:0,vz:0,actualSpeed:0,moveSpeed:0,carry:null});s.access=null;s.equipment.cooldown=0;s.equipment.reloading=0;s.weaponEffects=[];s.weaponProjectiles=[];a.renderer.camera.yaw=0;a.renderer.camera.weaponPitch=-.03;a.renderer.daylight=.68;a.renderer.rain=0;a.chapterUntil=0;document.getElementById('chapter').classList.remove('visible');a.toastQueue=[];a.toastUntil=0;document.getElementById('toast').classList.remove('visible');a.setMode('play');}''');tick(p,2)

def equip(p,id):
 p.keyboard.press('Tab');p.click('[data-weapon="'+id+'"]');p.click('#commitEquipment');tick(p,2)

def shot(p,id):
 equip(p,id);p.evaluate('DC_APP.renderer.camera.weaponPitch=-.03');tick(p,3);p.keyboard.down('j');tick(p,100 if id=='gauss'else 1);p.keyboard.up('j');tick(p,1,True)

def hit(p,id):
 return p.evaluate('''id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return !e.hidden&&r.width>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth+.1&&r.bottom<=innerHeight+.1&&(h===e||e.contains(h));}''',id)

try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1100,'height':760});p.set_default_timeout(25000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda e:errors.append(e.text)if e.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content(HTML.replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady');p.evaluate('window.requestAnimationFrame=()=>0');p.wait_for_timeout(160)
  ck('Boot uses actual v0.17 simulation and renderer',p.evaluate('DC_APP.sim instanceof DC.EquipmentSimulation&&DC_APP.renderer instanceof DC.EquipmentRenderer'))
  ck('Character creator and library still available',p.locator('#start').is_visible()and p.locator('#landingSaves').is_visible())
  p.click('#start');p.fill('#characterName','Ícaro');p.fill('#newSaveName','Arsenal · noche');p.select_option('#characterHairStyle','8');p.click('#commitCreator');p.click('#dismissTutorial');scene(p)
  ck('New named story begins with hands free',p.evaluate('DC_APP.sim.equipment.selected==="unarmed"&&DC_APP.sim.appearance.hairStyle===8'))
  p.keyboard.press('Tab');ck('Tab opens accessible selector and pauses simulation',p.evaluate('DC_APP.mode==="arsenal"')and p.locator('#arsenal').get_attribute('aria-modal')=='true');ck('All fourteen catalogue entries present',p.locator('.weapon-card').count()==14)
  before=p.evaluate('DC_APP.sim.serialize()');p.click('[data-weapon="gauss"]');ck('Pending choice does not equip or spend resources',p.evaluate('DC_APP.sim.serialize()')==before);p.keyboard.press('Escape');ck('Closing cancels choice',p.evaluate('DC_APP.sim.equipment.selected==="unarmed"&&DC_APP.mode==="play"'))
  p.keyboard.press('Tab');p.click('[data-group="Tecnología"]');ck('Technology filter exposes Gauss and EMP',p.locator('.weapon-card').count()==2);p.click('[data-weapon="gauss"]');p.screenshot(path=str(O/'01-selector.png'));p.click('#commitEquipment');tick(p,3,True)
  ck('Selection equips the real Gauss model',p.evaluate('DC_APP.renderer.equipmentStats.selected==="gauss"&&DC_APP.renderer.equipmentStats.triangles>1000'))
  ck('Selecting from UI cannot discharge a weapon',p.evaluate('DC_APP.sim.equipment.shots===0'))
  p.keyboard.down('j');tick(p,105,True);ck('Gauss charges while held without consuming cell',p.evaluate('DC_APP.sim.equipment.charge===1&&DC_APP.sim.equipment.ammo.gauss.loaded===3'));p.screenshot(path=str(O/'02-charge.png'));p.keyboard.up('j');tick(p,1,True)
  ck('Gauss release consumes exactly one cell and emits trail',p.evaluate('DC_APP.sim.equipment.shots===1&&DC_APP.sim.equipment.ammo.gauss.loaded===2&&DC_APP.sim.weaponEffects.some(f=>f.kind==="gauss")'))
  tick(p,70);p.keyboard.down('j');tick(p,55);p.keyboard.press('Escape');p.keyboard.up('j');ck('Pause cancels stored charge',p.evaluate('DC_APP.sim.equipment.charge===0&&DC_APP.mode==="pause"'));p.click('#resume');tick(p,2);ck('Resuming does not release the cancelled charge',p.evaluate('DC_APP.sim.equipment.shots===1'))
  tick(p,60);p.keyboard.down('j');tick(p,60);p.evaluate('window.dispatchEvent(new Event("blur"))');p.keyboard.up('j');ck('Window focus loss clears charge and pauses',p.evaluate('DC_APP.sim.equipment.charge===0&&DC_APP.mode==="pause"'));p.click('#resume');tick(p,3);ck('Focus return cannot fire the old press',p.evaluate('DC_APP.sim.equipment.shots===1'))
  scene(p);equip(p,'pistol');p.evaluate('DC_APP.renderer.camera.weaponPitch=-.035;Object.assign(DC_APP.sim.cars[1],{x:4,z:58,yaw:Math.PI,health:100,damage:{front:0,rear:0,left:0,right:0}})');tick(p,3);p.mouse.click(550,340);tick(p,1)
  # A complete click between simulation ticks must not be lost (short mouse click test).
  ck('Fast native mouse click is captured once',p.evaluate('DC_APP.sim.equipment.ammo.pistol.loaded===11'))
  ck('Aimed shot damages the visible vehicle zone',p.evaluate('DC_APP.sim.cars[1].health<100&&DC_APP.sim.cars[1].damage.front>0'))
  tick(p,20);p.mouse.down(button='left');tick(p,70);p.mouse.up(button='left');tick(p,1);ck('Holding semiautomatic trigger does not repeat shots',p.evaluate('DC_APP.sim.equipment.ammo.pistol.loaded===10'))
  p.keyboard.press('l');tick(p,90);ck('Reload completes and preserves total ammunition',p.evaluate('DC_APP.sim.equipment.ammo.pistol.loaded===12&&DC_APP.sim.equipment.ammo.pistol.reserve===94'))
  before=p.evaluate('DC_APP.renderer.camera.yaw');p.mouse.move(550,350);p.mouse.down(button='right');p.mouse.move(630,380,steps=3);tick(p,3);ck('Right drag aims and adjusts camera yaw and pitch',p.evaluate('DC_APP.sim.equipment.aiming&&DC_APP.renderer.camera.weaponPitch<-.05')and p.evaluate('DC_APP.renderer.camera.yaw')!=before);p.mouse.up(button='right');tick(p,2);ck('Right release ends held aim',p.evaluate('!DC_APP.sim.equipment.aiming'))
  scene(p);equip(p,'smg');p.keyboard.down('j');tick(p,30);p.keyboard.up('j');tick(p,1);ck('Automatic weapon repeats at a bounded cadence',p.evaluate('DC_APP.sim.equipment.ammo.smg.loaded>=22&&DC_APP.sim.equipment.ammo.smg.loaded<=25'))
  scene(p);equip(p,'emp');p.evaluate('''()=>{const s=DC_APP.sim;Object.assign(s.cars[1],{x:4,z:48,yaw:0,speed:3,police:true,stolen:false,health:85,parked:false});Object.assign(s.cars[2],{x:4,z:120,yaw:0,health:100});window.lamp= s.dynamics.props.find(p=>p.type==='lamp'&&DC.distance(p,s.player)<26&&!p.broken);window.lampHealth=lamp?.health;}''');p.keyboard.down('j');tick(p,1,True);p.keyboard.up('j');ck('EMP pulse disables nearby car without health damage',p.evaluate('DC_APP.sim.cars[1].empUntil>DC_APP.sim.time&&DC_APP.sim.cars[1].health===85'));ck('Distant car remains unaffected',p.evaluate('!(DC_APP.sim.cars[2].empUntil>DC_APP.sim.time)'));ck('Nearby lamp interruption does not destroy it',p.evaluate('!!lamp&&lamp.empUntil>DC_APP.sim.time&&lamp.health===lampHealth&&!lamp.broken'));ck('EMP does not clear the police alert',p.evaluate('DC_APP.sim.heat>0'));p.screenshot(path=str(O/'03-emp.png'))
  p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.player.car=1;s.player.x=s.cars[1].x;s.player.z=s.cars[1].z;s.cars[1].speed=0;}''');p.keyboard.down('w');tick(p,80,True);p.keyboard.up('w');ck('Disabled engine cannot accelerate from rest',p.evaluate('DC_APP.sim.cars[1].speed===0'));ck('Disabled headlight source is absent in production shader',p.evaluate('DC_APP.renderer.gl.getUniform(DC_APP.renderer.sceneProgram,DC_APP.renderer.uniform(DC_APP.renderer.sceneProgram,"uHeadPos"))[1]===-1000'));ck('Weapons are visually holstered while driving',p.evaluate('document.getElementById("weaponReticle").hidden'))
  tick(p,460);ck('EMP timer expires instead of becoming permanent damage',p.evaluate('DC_APP.sim.cars[1].empUntil<DC_APP.sim.time&&lamp.empUntil<DC_APP.sim.time'))
  scene(p);equip(p,'launcher');p.keyboard.down('j');tick(p,1,True);p.keyboard.up('j');ck('Launcher creates a moving projectile',p.evaluate('DC_APP.sim.weaponProjectiles[0]?.kind==="rocket"'));tick(p,20);ck('Rocket travels instead of a hitscan only',p.evaluate('DC_APP.sim.weaponProjectiles[0]?.position[2]>45'))
  scene(p);equip(p,'grenade');p.keyboard.down('j');tick(p,1);p.keyboard.up('j');tick(p,90,True);ck('Grenade survives before its fuse expires',p.evaluate('DC_APP.sim.weaponProjectiles.length===1'));tick(p,60,True);ck('Grenade detonates after fuse with bounded blast effect',p.evaluate('DC_APP.sim.weaponProjectiles.length===0&&DC_APP.sim.weaponEffects.some(f=>f.kind==="blast")'))
  scene(p);p.keyboard.press('b');tick(p,3);p.keyboard.press('z');tick(p,3);p.evaluate('DC_APP.renderer.camera.weaponPitch=-.14');tick(p,3,True);ck('Optics activate without weapon fire or ammo consumption',p.evaluate('DC_APP.sim.equipment.aiming&&DC_APP.sim.equipment.selected==="binoculars"')and p.locator('#opticsOverlay').is_visible());base=p.evaluate('DC_APP.renderer.fovOverride');p.mouse.wheel(0,-150);tick(p,2);p.mouse.wheel(0,-150);tick(p,2,True);ck('Mouse wheel changes real FOV to 8×',p.evaluate('DC_APP.sim.equipment.zoom===2&&DC_APP.renderer.fovOverride')<base)
  ck('Ground measurement does not dereference an absent object',p.evaluate('DC_APP.sim.aimTrace().hit?.type==="ground"')and not errors);p.keyboard.press('h');tick(p,1);ck('Observed surface creates GPS pin',p.evaluate('!!DC_APP.sim.pin&&DC_APP.sim.pin.z>DC_APP.sim.player.z+10'));p.screenshot(path=str(O/'04-optics.png'))
  p.keyboard.press('z');tick(p,2);ck('Leaving optics restores nonzoom view',p.evaluate('DC_APP.renderer.fovOverride>1&&!DC_APP.sim.equipment.aiming'));p.keyboard.press('Backquote');tick(p,2);ck('Hands-free returns original camera and interaction controls',p.evaluate('DC_APP.sim.equipment.selected==="unarmed"&&!DC_APP.renderer.equipmentView&&DC_APP.renderer.fovOverride===null'))
  # Save two inventory states through actual named-slot UI.
  equip(p,'gauss');p.evaluate('DC_APP.sim.equipment.ammo.gauss.loaded=1');p.keyboard.press('Escape');p.click('#saveGame');sid=p.evaluate('DC_APP.activeSlot.id');p.click('#pauseSaves');p.click('#libraryNew');p.fill('#newSaveName','Arsenal · campo');p.fill('#characterName','Luna');p.click('#commitCreator');p.click('#dismissTutorial');equip(p,'emp');p.keyboard.press('Escape');p.click('#saveGame');second=p.evaluate('DC_APP.activeSlot.id');p.click('#pauseSaves');p.click('[data-slot="'+sid+'"] .slot-load');ck('Loading first slot restores its own Gauss ammunition',p.evaluate('DC_APP.sim.equipment.selected==="gauss"&&DC_APP.sim.equipment.ammo.gauss.loaded===1'))
  p.keyboard.press('Escape');p.click('#pauseSaves');p.click('[data-slot="'+second+'"] .slot-load');ck('Loading second slot restores its own EMP',p.evaluate('DC_APP.sim.equipment.selected==="emp"&&DC_APP.sim.characterName==="Luna"'));p.keyboard.press('Escape');p.click('#pauseSaves')
  with p.expect_download() as dl:p.click('#libraryExportAll')
  exported=json.loads(Path(dl.value.path()).read_text());ck('Downloaded catalogue contains both equipment inventories',sorted(x['data']['equipment']['selected']for x in exported['slots'])==['emp','gauss']);p.click('#closeLibrary');p.click('#resume');scene(p)
  # All inventory render batches use finite geometry; arms reach the weapon's actual grip.
  for id in ['baton','blade','pistol','revolver','smg','shotgun','rifle','sniper','launcher','grenade','gauss','emp','binoculars']:
   p.evaluate('(id)=>DC_APP.selectEquipment(id)',id);tick(p,2,True);ck('Shared weapon model renders '+id,p.evaluate('DC_APP.renderer.gl.getError()===0&&DC_APP.renderer.equipmentStats.parts>0'))
  ck('Geometry allocation remains bounded',p.evaluate('DC_APP.renderer.equipmentMeshes.size===14'))
  # Touch layouts and pointer cancellation.
  for w,h in [(390,844),(844,390)]:
   p.set_viewport_size({'width':w,'height':h});p.evaluate('DC_APP.setTouch(true)');scene(p);equip(p,'gauss');tick(p,2,True)
   for id in ['openArsenal','touchFire','touchAim','touchCar','joystick','pauseButton']:
    ck('Touch target reachable '+str(w)+' '+id,hit(p,id))
   p.locator('#touchFire').dispatch_event('pointerdown',{'pointerId':91,'pointerType':'touch','bubbles':True});tick(p,50);ck('Touch hold charges Gauss '+str(w),p.evaluate('DC_APP.sim.equipment.charge>.4'))
   p.locator('#touchFire').dispatch_event('pointercancel',{'pointerId':91,'pointerType':'touch','bubbles':True});tick(p,2);ck('Touch cancellation cannot release Gauss '+str(w),p.evaluate('DC_APP.sim.equipment.charge===0&&!DC_APP.weaponPointers.size'))
   p.click('#openArsenal');p.click('[data-group="Tecnología"]');p.click('[data-weapon="emp"]');ck('Mobile selector confirm is reachable '+str(w),hit(p,'commitEquipment'));p.screenshot(path=str(O/('05-selector-'+str(w)+'.png')));p.click('#commitEquipment');tick(p,2,True)
  ck('No JavaScript or shader exceptions',not errors);ck('No external network requests',not requests);b.close()
finally:
 report={'sha256':hashlib.sha256(HTML.encode()).hexdigest(),'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'checks':checks,'errors':errors,'requests':requests,'environment':'Chromium Xvfb SwiftShader. Native keyboard/mouse/DOM inputs and explicit simulation/WebGL frames. Memory localStorage fixture. RAF scheduling paused after boot; native loop tested separately.'};(O/'arsenal-browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
