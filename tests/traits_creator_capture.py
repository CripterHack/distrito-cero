"""Capture the real creator controls and scene after selecting a new style."""
from pathlib import Path
import os,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v016';os.environ.setdefault('DISPLAY',':99')
FIX="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,v)}});})();"""
errors=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1280,'height':900})
 p.on('pageerror',lambda e:errors.append(str(e)));p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
 p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.loop=()=>{}');p.click('#start');p.select_option('#characterHairStyle','8');p.select_option('#characterFocus','neck');p.fill('#characterName','Alex');p.fill('#newSaveName','Alex · Rasgos')
 p.evaluate("""()=>{const a=DC_APP;a.creator.animate=false;a.creator.elapsed=1;a.renderer.quality='high';a.fitCreator();DC.IdentityApp.prototype.loop.call(a,performance.now());a.renderer.camera.eye=[.23,1.65,.90];a.renderer.camera.target=[0,1.515,0];a.renderer.frame=0;drawActual(a.creator.preview);document.getElementById('characterNeckLength').closest('label').scrollIntoView({block:'start'});}""")
 p.screenshot(path=str(O/'editor-rasgos.png'),timeout=45000);d=p.evaluate('({gl:DC_APP.renderer.gl.getError(),look:DC_APP.creator.look,options:document.getElementById("characterHairStyle").options.length})');d.update(errors=errors,sha256=hashlib.sha256((R/'index.html').read_bytes()).hexdigest());(O/'editor-capture.json').write_text(json.dumps(d,indent=2));print(d);assert d['gl']==0 and not errors;b.close()
