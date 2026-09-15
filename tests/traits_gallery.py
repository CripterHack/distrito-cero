"""Real WebGL gallery: all selectable hairstyles, identical lighting and camera."""
from pathlib import Path
import os,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1]; O=R/'qa/v016'; os.environ.setdefault('DISPLAY',':99')
FIX="""(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
source=R/'index.html'; reports=[]; errors=[]; requests=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1120,'height':800},device_scale_factor=1.5)
 p.on('pageerror',lambda e:errors.append(str(e))); p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
 p.set_content(source.read_text().replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
 p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.loop=()=>{}');p.click('#start');p.wait_for_timeout(100)
 p.add_style_tag(content='.preview-label,.preview-controls,.preview-hint,.preview-overline{visibility:hidden!important}')
 p.evaluate("""()=>{const a=DC_APP,c=a.creator,s=c.preview,r=a.renderer;c.animate=false;c.elapsed=1;s.time=1;Object.assign(s.player,{walk:0,moveSpeed:0,yaw:0,grip:0,crouch:0});s.setIdentity('Alex',{...DC.Appearance.default(),skin:1,hair:1,coat:1,build:0});r.quality='balanced';r.daylight=.5;a.fitCreator();r.camera.eye=[.20,1.67,.76];r.camera.target=[0,1.59,-.005];}""")
 for i in range(11):
  data=p.evaluate("""i=>{const a=DC_APP,s=a.creator.preview,r=a.renderer;s.appearance.hairStyle=i;r.frame=0;drawActual(s);return{style:i,label:DC.Appearance.hairstyles[i],gl:r.gl.getError(),camera:{eye:r.camera.eye,target:r.camera.target},stats:r.castStats};}""",i)
  p.locator('#creatorViewport').screenshot(path=str(O/f'hair-{i:02d}.png'),timeout=45000)
  reports.append(data); print('CAPTURE',i, data['gl'],flush=True); assert data['gl']==0
 b.close()
(O/'hair-gallery-report.json').write_text(json.dumps({'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'screens':reports,'errors':errors,'requests':requests,'scope':'Actual production WebGL. Identical prepared camera and light. Static pose, not a benchmark.'},ensure_ascii=False,indent=2))
assert not errors and not requests
