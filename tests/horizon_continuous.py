"""Real animation loop + keyboard crossing original boundary and streamed sector seam.
Only initial positions are prepared. Neither renderer, camera nor step is replaced.
"""
from pathlib import Path
import os,json,time
from playwright.sync_api import sync_playwright
os.environ.setdefault('DISPLAY',':99');ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/v07'
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
checks=[];errors=[];requests=[]
def check(name,value):
 checks.append({'name':name,'pass':bool(value)});print(time.strftime('%H:%M:%S'),('PASS' if value else 'FAIL'),name,flush=True);assert value,name
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  p=b.new_page(viewport={'width':640,'height':420});p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);p.on('request',lambda r:requests.append(r.url))
  p.set_content((ROOT/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000);p.wait_for_function('!!window.DC_APP',timeout=45000);p.click('#start');p.click('#dismissTutorial')
  check('Live WebGL boot',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,c=s.cars[0];s.free=true;s.player.car=0;Object.assign(c,{x:412,z:4,yaw:Math.PI/2,speed:11});Object.assign(s.player,{x:c.x,z:c.z,yaw:c.yaw});for(const v of s.cars.slice(1)){v.x=-240;v.z=-300;v.parked=true;v.speed=0;}a.renderer.camera.initialized=false;window.firstFrame=a.frameCount;window.startDistance=s.stats.distance;}''')
  p.keyboard.down('w');p.wait_for_function('DC_APP.sim.player.x>433',timeout=60000);p.keyboard.up('w')
  check('Continuous keyboard drives beyond old city',p.evaluate('DC_APP.sim.player.x>433'))
  check('Renderer and simulation both advanced',p.evaluate('DC_APP.frameCount>firstFrame+4&&DC_APP.sim.stats.distance>startDistance+18'))
  p.keyboard.down('Space');p.wait_for_timeout(700);p.keyboard.up('Space')
  p.evaluate('''()=>{const a=DC_APP,s=a.sim,c=s.actor();Object.assign(c,{x:664,z:4,yaw:Math.PI/2,speed:11});Object.assign(s.player,{x:c.x,z:c.z,yaw:c.yaw});s.syncRegion();a.renderer.camera.initialized=false;window.generationBefore=a.world.generation;}''')
  p.keyboard.down('w');p.wait_for_function('DC_APP.sim.player.x>690',timeout=60000);p.keyboard.up('w')
  check('Live sector boundary changes world generation',p.evaluate('DC_APP.world.generation>generationBefore'))
  p.wait_for_function('DC_APP.renderer.streamStats.pending===0',timeout=30000)
  check('Streaming fills all 25 slots without permanent growth',p.evaluate('DC_APP.renderer.streamStats.loaded===25&&DC_APP.world.chunks.size<=64&&DC_APP.world.cells.size<=768'))
  check('No GL error after buffer turnover',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  p.keyboard.down('Space');p.wait_for_function('Math.abs(DC_APP.sim.actor().speed)<.9',timeout=30000);p.keyboard.up('Space');p.keyboard.press('Escape');p.click('#openMapPause');check('Mappable world while far from starting block',p.evaluate('DC_APP.mode==="map"&&DC_APP.sim.player.x>690'))
  p.click('[data-destination="farmland"]');check('Atlas travel operates with actual loop running',p.evaluate('DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z).type==="farmland"'))
  # Travel only works when stopped. At this point the car can still be moving, so stop first if refused.
  p.keyboard.press('Escape') if p.evaluate('DC_APP.mode')=='play' else None
  check('No JavaScript errors during streamed drive',not errors);check('No network requests',not requests)
  info=p.evaluate('({position:DC_APP.sim.player,stream:DC_APP.renderer.streamStats,frameCount:DC_APP.frameCount,worldGeneration:DC_APP.world.generation})')
  b.close()
finally:
 report={'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'checks':checks,'errors':errors,'requests':requests,'observed':locals().get('info'), 'environment':'Xvfb Chromium SwiftShader 640x420. Active requestAnimationFrame and native keyboard. Prepared initial positions. Isolated memory save storage because navigation is blocked by lab policy. No hardware FPS claim.'};(OUT/'continuous-horizon.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
