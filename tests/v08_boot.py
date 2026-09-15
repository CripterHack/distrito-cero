"""Single fresh context per reviewed biome, to isolate SwiftShader captures."""
from pathlib import Path
import os,json,sys,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/v07';os.environ.setdefault('DISPLAY',':99');name=sys.argv[1] if len(sys.argv)>1 else 'future'
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':900,'height':640});errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
 p.set_content((ROOT/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000)
 p.wait_for_function('!!window.DC_APP',timeout=60000)
 p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.renderer.updateCamera=()=>{};')
 p.click('#start');p.click('#dismissTutorial')
 p.evaluate("const a=DC_APP,s=a.sim;s.free=true;document.getElementById('chapter').style.display='none';document.getElementById('toast').style.display='none';a.setMode('photo');a.renderer.camera.eye=[s.player.x+1.7,1.50,s.player.z+2.9];a.renderer.camera.target=[s.player.x,1.30,s.player.z];a.renderer.daylight=.60;a.renderer.rain=0;drawActual(s)")
 print(p.evaluate('({cast:DC_APP.renderer.castStats,visual:DC_APP.renderer.visualStats,gl:DC_APP.renderer.gl.getError()})'),errs,flush=True)
 p.screenshot(path=str(ROOT/'qa/v08/before-refine.png'),timeout=60000)
 b.close()
