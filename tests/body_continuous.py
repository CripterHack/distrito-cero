"""Real requestAnimationFrame, simulation, camera, input and rendering. No replaced methods.
Initial positions are prepared to reproduce the scenario. Isolated test localStorage.
"""
from pathlib import Path
import os,json,time,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v010';os.environ.setdefault('DISPLAY',':99')
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
checks=[];errors=[];requests=[]
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(time.strftime('%H:%M:%S'),('PASS 'if v else'FAIL ')+n,flush=True);assert v,n
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':680,'height':440});p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None);p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000);p.wait_for_function('!!window.DC_APP',timeout=60000);p.click('#start');p.click('#dismissTutorial')
  p.evaluate('DC_APP.renderer.humanReady');ck('All three embedded maps load during native loop',p.evaluate('DC_APP.renderer.humanTextureStatus.loaded===3&&DC_APP.renderer.humanTextureStatus.failed===0'));
  ck('Live game boot',p.evaluate('DC_APP.renderer.gl.getError()===0'))
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
 report={'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'checks':checks,'errors':errors,'requests':requests,'observed':locals().get('info'),'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'environment':'Chromium Xvfb SwiftShader 680x440. Unmodified RAF/camera/render/simulation with prepared initial poses and native keys. Isolated test storage. Not a hardware FPS benchmark.'};(O/'body-continuous.json').write_text(json.dumps(report,indent=2));print('RESULT',report['passed'],report['failed'],flush=True)
