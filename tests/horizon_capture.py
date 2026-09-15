"""Single fresh context per reviewed biome, to isolate SwiftShader captures."""
from pathlib import Path
import os,json,sys,time
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'qa/v07';os.environ.setdefault('DISPLAY',':99');name=sys.argv[1] if len(sys.argv)>1 else 'future'
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1120,'height':720});errs=[];p.on('pageerror',lambda e:errs.append(str(e)))
 p.set_content((ROOT/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000);p.wait_for_function('!!window.DC_APP',timeout=60000)
 p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.renderer.updateCamera=()=>{};');p.click('#start');p.click('#dismissTutorial');p.evaluate("DC_APP.sim.free=true;document.getElementById('chapter').style.display='none';document.getElementById('toast').style.display='none';")
 p.evaluate('''name=>{const a=DC_APP,s=a.sim;const car=s.cars[0];car.speed=0;Object.assign(s.player,{x:car.x-2,z:car.z});s.interact('car');s.player.transition=null;const dest=a.world.destinations().find(d=>d.id===name);s.travel(dest.x,dest.z);a.setMode('photo');const p=s.player,extra=name==='farmland'||name==='village';a.renderer.camera.eye=[p.x+(extra?38:-7),extra?22:13,p.z-(extra?45:29)];a.renderer.camera.target=[p.x+(extra?32:15),extra?3:12,p.z+35];a.renderer.daylight=.78;a.renderer.rain=0;a.renderer.quality='balanced';a.renderer.resize();a.renderer.syncSectors(25);a.renderer.frame=0;drawActual(s);}''',name)
 print('render',name,p.evaluate('({gl:DC_APP.renderer.gl.getError(),stats:DC_APP.renderer.streamStats,position:DC_APP.sim.player.x})'),flush=True)
 p.screenshot(path=str(OUT/('region-'+name+'.png')),timeout=60000)
 data=p.evaluate('({seed:DC_APP.world.seed,region:DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z),stats:DC_APP.renderer.streamStats,gl:DC_APP.renderer.gl.getError()})');data['errors']=errs;data['capture']='Actual WebGL with prepared photo camera, no generated illustration';(OUT/('capture-'+name+'.json')).write_text(json.dumps(data,indent=2,ensure_ascii=False));print('SAVED',name,flush=True);b.close()
