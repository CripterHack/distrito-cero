"""Unmodified WebGL render loop + live input during an actual police collision.
No renderer, simulation or storage mocks. SwiftShader is not a hardware benchmark.
"""
from pathlib import Path
import json
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/v03';errors=[]
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':640,'height':400})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
 page.set_content((ROOT/'index.html').read_text(),wait_until='load');page.wait_for_function('!!window.DC_APP')
 page.evaluate("DC_APP.renderer.quality='eco';DC_APP.renderer.rain=0;DC_APP.renderer.bloom=0;DC_APP.renderer.resize();")
 page.click('#start');page.click('#dismissTutorial')
 before=page.evaluate('''()=>{
 const a=DC_APP,s=a.sim,cop=s.cars.find(c=>c.police);s.cars=[s.cars[0],cop];s.peds=[];s.free=true;
 Object.assign(s.cars[0],{x:4,z:0,yaw:0,speed:0,parked:false});Object.assign(cop,{x:4,z:3,yaw:Math.PI,speed:0,parked:false});
 Object.assign(s.player,{x:4,z:0,car:0,yaw:0});s.addHeat(40);a.chapterUntil=0;a.toastUntil=0;a.toastQueue=[];
 return {frame:a.renderer.frame,time:s.time,x:s.player.x,z:s.player.z};}''')
 page.keyboard.down('s');page.keyboard.down('d')
 page.wait_for_function('(t)=>DC_APP.sim.time>t+1.8',arg=before['time'],timeout=30000)
 page.keyboard.up('s');page.keyboard.up('d')
 after=page.evaluate('({frame:DC_APP.renderer.frame,time:DC_APP.sim.time,x:DC_APP.sim.player.x,z:DC_APP.sim.player.z,car:DC_APP.sim.player.car,speed:DC_APP.sim.actor().speed,bust:DC_APP.sim.bust,glError:DC_APP.renderer.gl.getError()})')
 assert after['frame']>before['frame']+5,after
 assert after['car']==0 and after['speed'] < -4 and after['bust']<.2,after
 assert after['glError']==0 and not errors,errors
 # Actual rendered capture after the verified manoeuvre. No simulation or renderer replacement.
 page.set_viewport_size({'width':1280,'height':800})
 page.evaluate("DC_APP.renderer.quality='balanced';DC_APP.renderer.rain=1;DC_APP.renderer.bloom=1;DC_APP.renderer.resize();DC_APP.updateUI(performance.now());")
 page.wait_for_timeout(1200);page.screenshot(path=str(OUT/'16-police-live.png'))
 b.close()
report={'passed':True,'before':before,'after':after,'errors':errors,'renderer_replaced':False,'simulation_replaced':False,'storage_replaced':False,'environment':'Chromium / Xvfb / SwiftShader. Initial 640x400 eco. Final screenshot 1280x800 balanced, rain/reflections enabled. Not a hardware performance benchmark.'}
(OUT/'police-continuous-report.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
