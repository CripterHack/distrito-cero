from pathlib import Path
import os,json
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v017';os.environ['DISPLAY']=':99'
FIX="""(()=>{window.testStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore.get(k)||null,setItem:(k,v)=>testStore.set(k,String(v)),removeItem:k=>testStore.delete(k)}});})();"""
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1100,'height':760});page.on('pageerror',lambda e:print('ERROR',e,flush=True));page.on('console',lambda e:print('CONSOLE',e.text,flush=True)if e.type=='error'else None)
 page.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIX,1),timeout=90000);page.wait_for_function('!!window.DC_APP',timeout=90000);page.evaluate('DC_APP.renderer.humanReady');print('BOOT',page.evaluate('({mode:DC_APP.mode,gl:DC_APP.renderer.gl.getError()})'),flush=True)
 page.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}')
 page.click('#start');page.click('#commitCreator');page.click('#dismissTutorial');page.keyboard.press('Tab');page.screenshot(path=str(O/'arsenal-first.png'));print('ARSENAL',page.locator('.weapon-card').count(),flush=True)
 page.click('[data-weapon="gauss"]');page.click('#commitEquipment');page.evaluate('''()=>{const a=DC_APP,s=a.sim;s.free=true;s.heat=s.wanted=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach((c,i)=>Object.assign(c,{x:-290,z:-300-i*5,parked:true,speed:0}));Object.assign(s.player,{x:4,z:36,yaw:0,car:null});a.renderer.camera.yaw=0;a.renderer.camera.weaponPitch=0;a.renderer.daylight=.68;a.renderer.updateCamera(s,0);drawActual(s);}''');page.screenshot(path=str(O/'gauss-first.png'));print('GUN',page.evaluate('({mode:DC_APP.mode,eq:DC_APP.sim.equipment,parts:DC_APP.renderer.equipmentStats,gl:DC_APP.renderer.gl.getError()})'),flush=True)
 page.keyboard.down('j');page.wait_for_function('DC_APP.sim.equipment.charge>.9');page.evaluate('drawActual(DC_APP.sim)');page.screenshot(path=str(O/'gauss-charge-first.png'));page.keyboard.up('j');page.wait_for_function('DC_APP.sim.equipment.shots===1');print('SHOT',page.evaluate('({shots:DC_APP.sim.equipment.shots,ammo:DC_APP.sim.equipment.ammo.gauss})'),flush=True)
 page.keyboard.press('b');page.keyboard.press('z');page.wait_for_function('DC_APP.sim.equipment.aiming');page.evaluate('drawActual(DC_APP.sim)');page.screenshot(path=str(O/'optics-first.png'));print('OPTIC',page.evaluate('({fov:DC_APP.renderer.fovOverride,gl:DC_APP.renderer.gl.getError()})'),flush=True)
 b.close()
