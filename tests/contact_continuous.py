"""Real requestAnimationFrame, simulation, camera, input and rendering. No replaced methods.
Initial positions are prepared to reproduce the scenario. Isolated test localStorage.
"""
from pathlib import Path
import os,json,time,hashlib
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1];O=R/'qa/v019'
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
checks=[];errors=[];requests=[]
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(time.strftime('%H:%M:%S'),('PASS 'if v else'FAIL ')+n,flush=True);assert v,n
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(**launch_options());p=b.new_page(viewport={'width':680,'height':440});p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None);p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000);p.wait_for_function('!!window.DC_APP',timeout=60000);p.click('#start');p.click('#commitCreator');p.click('#dismissTutorial')
  p.evaluate('DC_APP.renderer.humanReady');ck('All three embedded maps load during native loop',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3&&DC_APP.renderer.humanTextureStatus.failed===0'));
  ck('Live game boot',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  # Equip and use through native input with the renderer and RAF still running.
  p.evaluate("""()=>{const a=DC_APP,s=a.sim;s.free=true;s.heat=s.wanted=0;s.cars.forEach((c,i)=>Object.assign(c,{x:-260,z:-300-i*5,parked:true,speed:0}));s.peds.forEach(n=>n.hidden=true);Object.assign(s.player,{x:4,z:36,yaw:0,car:null});Object.assign(s.cars[1],{x:4,z:56,yaw:0,parked:true,health:100,damage:{front:0,rear:0,left:0,right:0}});a.renderer.camera.yaw=0;a.renderer.daylight=.66;window.nativeFrames=a.frameCount;window.nativeTime=s.time;}""")
  p.keyboard.press('9');p.evaluate('DC_APP.renderer.camera.weaponPitch=-.026');p.wait_for_function('DC_APP.renderer.equipmentStats.selected==="gauss"',timeout=30000)
  ck('Native numeric selection draws Gauss',p.evaluate('DC_APP.sim.equipment.selected==="gauss"&&DC_APP.renderer.equipmentView'))
  p.keyboard.down('z');p.keyboard.up('z');p.keyboard.down('j');p.wait_for_function('DC_APP.sim.equipment.charge>.95',timeout=30000)
  ck('Gauss charges in untouched simulation loop',p.evaluate('DC_APP.sim.equipment.ammo.gauss.loaded===3'))
  p.keyboard.up('j');p.wait_for_function('DC_APP.sim.equipment.shots===1',timeout=30000)
  ck('Native release fires and damages target',p.evaluate('DC_APP.sim.equipment.ammo.gauss.loaded===2&&DC_APP.sim.cars[1].health<100'))
  p.wait_for_function('DC_APP.sim.equipment.cooldown===0');p.keyboard.press('0');p.wait_for_timeout(100);p.keyboard.press('j');p.wait_for_function('DC_APP.sim.equipment.shots===2',timeout=30000)
  ck('EMP pulse works through a short real key press',p.evaluate('DC_APP.sim.equipment.ammo.emp.loaded===0'))
  ck('EMP produces a finite electronic timer',p.evaluate('DC_APP.sim.cars.some(c=>c.empUntil>DC_APP.sim.time)'))
  p.keyboard.press('b');p.keyboard.press('z');p.wait_for_function('DC_APP.sim.equipment.aiming&&DC_APP.renderer.fovOverride<.7',timeout=30000);old=p.evaluate('DC_APP.renderer.fovOverride');p.keyboard.press('Equal');p.wait_for_function('DC_APP.sim.equipment.zoom===1&&DC_APP.renderer.fovOverride<.35',timeout=30000);
  ck('Binocular zoom changes live camera projection',p.evaluate('DC_APP.renderer.fovOverride')<old)
  p.evaluate('DC_APP.renderer.camera.weaponPitch=-.10');p.wait_for_function('DC_APP.sim.equipment.ray.direction[1]<-.08',timeout=30000);p.keyboard.press('h');p.wait_for_function('!!DC_APP.sim.pin',timeout=30000)
  ck('Live optical observation marks a visible location',p.evaluate('DC_APP.sim.pin.z>DC_APP.sim.player.z'))
  p.keyboard.press('Tab');ck('Selector pauses and disarms held inputs',p.evaluate('DC_APP.mode==="arsenal"&&!DC_APP.sim.equipment.aiming'));p.keyboard.press('Escape');p.keyboard.press('Backquote');p.wait_for_function('!DC_APP.renderer.equipmentView',timeout=30000)
  ck('Returning to hands free restores original view',p.evaluate('DC_APP.renderer.fovOverride===null'))
  ck('Native loop continues across all equipment modes',p.evaluate('DC_APP.frameCount>nativeFrames&&DC_APP.sim.time>nativeTime+2'))
  p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.free=true;s.heat=s.wanted=0;for(let i=0;i<s.cars.length;i++)Object.assign(s.cars[i],{x:-260,z:-300-i*5,parked:true,speed:0});s.peds.forEach(n=>n.hidden=true);const c=s.cars[1];Object.assign(c,{x:4,z:40,yaw:0,speed:0,parked:true,owned:false,stolen:false,driver:DC.driverProfile(c)});Object.assign(s.player,{x:1.75,z:40.1,yaw:Math.PI/2,car:null});a.renderer.camera.initialized=false;a.renderer.camera.yaw=Math.PI/2;a.renderer.daylight=.6;window.startFrame=a.frameCount;window.startTime=s.time;}''')
  p.keyboard.press('f');ck('Actual key begins extraction, not instant car access',p.evaluate('DC_APP.sim.access?.kind==="extract"&&DC_APP.sim.player.car===null'))
  p.wait_for_function('DC_APP.sim.access&&DC_APP.sim.access.elapsed>DC_APP.sim.access.approach+.55',timeout=60000)
  ck('Renderer uses independent actor palettes during extraction',p.evaluate('DC_APP.renderer.castStats.drivers>0&&DC_APP.renderer.castStats.actors>=2'))
  p.wait_for_function('DC_APP.sim.player.car===1&&!DC_APP.sim.access',timeout=60000)
  ck('Paired action completes in untouched loop',p.evaluate('DC_APP.sim.cars[1].driver===null&&DC_APP.sim.peds.filter(n=>n.evicted).length===1'))
  ck('Real simulation time and frames advanced',p.evaluate('DC_APP.frameCount>startFrame+30&&DC_APP.sim.time>startTime+3'))
  ck('No GL error after seat transfer',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  p.keyboard.down('w');p.wait_for_function('DC_APP.sim.actor().speed>7&&DC_APP.sim.player.z>44',timeout=60000);p.keyboard.up('w');ck('Newly occupied vehicle accelerates',p.evaluate('DC_APP.sim.player.z>44'))
  p.keyboard.down('Space');p.wait_for_function('Math.abs(DC_APP.sim.actor().speed)<.4',timeout=60000);p.keyboard.up('Space');p.keyboard.press('f');p.wait_for_function('DC_APP.sim.player.car===null&&!DC_APP.sim.access',timeout=60000);ck('Live exit restores on-foot control',p.evaluate('DC_APP.sim.player.car===null'))
  start=p.evaluate('({x:DC_APP.sim.player.x,z:DC_APP.sim.player.z})');p.keyboard.down('w');p.wait_for_function('p=>DC.distance(DC_APP.sim.player,p)>1',arg=start,timeout=30000);p.keyboard.up('w');ck('Natural locomotion continues after exit',p.evaluate('DC_APP.sim.player.walk>0'));p.screenshot(path=str(O/'continuous-exit.png'),timeout=60000)
  # Prepared seam position for continuous-world regression, not a claim of driving the whole distance.
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,c=s.cars[0];s.heat=s.wanted=0;s.player.car=0;Object.assign(c,{x:664,z:4,yaw:Math.PI/2,speed:10,parked:false,driver:null});Object.assign(s.player,{x:c.x,z:c.z,yaw:c.yaw});s.syncRegion();a.renderer.camera.initialized=false;window.generationBefore=a.world.generation;}''')
  p.keyboard.down('w');p.wait_for_function('DC_APP.sim.player.x>690',timeout=60000);p.keyboard.up('w');ck('Continuous drive crosses streamed sector seam',p.evaluate('DC_APP.world.generation>generationBefore'));p.wait_for_function('DC_APP.renderer.streamStats.pending===0',timeout=60000)
  ck('World and crowd GPU allocations remain bounded',p.evaluate('DC_APP.renderer.streamStats.loaded===25&&DC_APP.world.chunks.size<=64&&DC_APP.renderer.castStats.paletteRows<=128'))
  p.keyboard.down('Space');p.wait_for_function('Math.abs(DC_APP.sim.actor().speed)<.4',timeout=60000);p.keyboard.up('Space');p.keyboard.press('m');p.click('[data-destination="future"]');ck('Atlas works with native loop',p.evaluate('DC_APP.mode==="play"&&DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z).type==="future"'))
  p.wait_for_function('DC_APP.renderer.streamStats.pending===0',timeout=60000);ck('Final rendering without GL errors',p.evaluate('DC_APP.renderer.gl.getError()===0'));ck('No JavaScript or shader exceptions',not errors);ck('No external requests',not requests)
  info=p.evaluate('({stats:DC_APP.renderer.castStats,frameCount:DC_APP.frameCount,stream:DC_APP.renderer.streamStats,position:{x:DC_APP.sim.player.x,z:DC_APP.sim.player.z}})');b.close()
finally:
 report={'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'checks':checks,'errors':errors,'requests':requests,'observed':locals().get('info'),'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'environment':'Chromium Xvfb SwiftShader 680x440. Unmodified RAF/camera/render/simulation with prepared initial poses and native keys. Isolated test storage. Not a hardware FPS benchmark.'};(O/'arsenal-continuous.json').write_text(json.dumps(report,indent=2));print('RESULT',report['passed'],report['failed'],flush=True)
