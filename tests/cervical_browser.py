"""v0.14 acceptance, genuine DOM + WebGL frames. Memory fixture, not native persistence."""
from pathlib import Path
import os,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v014';os.environ.setdefault('DISPLAY',':99');checks=[];errors=[];requests=[]
html=(R/'index.html').read_text()
FIX='''(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();'''
def ck(name,v):
 checks.append({'name':name,'pass':bool(v)});print(('PASS 'if v else'FAIL ')+name,flush=True);assert v,name
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  p=b.new_page(viewport={'width':1120,'height':800});p.set_default_timeout(25000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Production WebGL boot',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}');p.click('#start')
  base=p.evaluate('DC_APP.sim.serialize()');ck('Creator retains both neck study options',p.locator('#characterPose option[value=neck]').count()==1 and p.locator('#characterPose option[value=nod]').count()==1)
  for pose,field in [('neck','lookYaw'),('nod','lookPitch')]:
   p.select_option('#characterPose',pose);p.select_option('#characterFocus','neck');p.wait_for_function('f=>Number.isFinite(DC_APP.creator.preview.player[f])',arg=field)
   p.evaluate('drawActual(DC_APP.creator.preview)')
   ck('Studio '+pose+' updates production rig',p.evaluate('f=>Math.abs(DC.SkinRig.pose(DC_APP.creator.preview.player,DC_APP.creator.preview.time).cervical[f==="lookYaw"?"yaw":"pitch"])>.001',field))
   ck('Studio '+pose+' has no render error',p.evaluate('DC_APP.renderer.gl.getError()===0'))
   ck('Studio '+pose+' leaves active gameplay unchanged',p.evaluate('DC_APP.sim.serialize()')==base)
  p.select_option('#characterPose','idle');p.wait_for_function('DC_APP.creator.preview.player.lookYaw===undefined&&DC_APP.creator.preview.player.lookPitch===undefined')
  ck('Leaving neck study clears its orientation overrides',p.evaluate('DC_APP.creator.preview.player.lookRoll===undefined'))
  p.evaluate('drawActual(DC_APP.creator.preview)');gpu=p.evaluate((R/'tests/cervical_gpu.js').read_text());(O/'gpu-transform-feedback.json').write_text(json.dumps(gpu,indent=2))
  ck('Actual vertex shader agrees with CPU for 16 neck/collar cases',gpu['maxPositionError']<.00001 and gpu['gl']==0)
  ck('Cervical surface normals agree with morph Jacobian',gpu['maxNormalError']<.001)
  for neck in [-100,100,0]:
   p.locator('#characterNeck').evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));}',neck);p.evaluate('drawActual(DC_APP.creator.preview)')
   ck('Extremum '+str(neck)+' still renders DQ and correct appearance',p.evaluate('(x)=>DC_APP.renderer.gl.getError()===0&&Math.abs(DC_APP.renderer.appearancePixels[3]-x/100)<.0001',neck))
  p.fill('#characterName','Río');p.fill('#newSaveName','Cervical · revisión');p.click('#commitCreator');p.click('#dismissTutorial');p.keyboard.press('Escape');p.click('#editAppearance');p.select_option('#characterPose','neck');p.wait_for_function('Number.isFinite(DC_APP.creator.preview.player.lookYaw)');p.click('#closeCreator')
  ck('Cancel preserves named saved character',p.evaluate('DC_APP.sim.characterName==="Río"&&DC_APP.getStore().active().name==="Cervical · revisión"'))
  ck('Neck study parameters are not saved into gameplay',p.evaluate('DC_APP.sim.player.lookYaw===undefined'))
  p.click('#editAppearance');p.select_option('#characterFocus','neck');p.select_option('#characterPose','nod');p.wait_for_function('Number.isFinite(DC_APP.creator.preview.player.lookPitch)');p.evaluate('drawActual(DC_APP.creator.preview)');p.screenshot(path=str(O/'editor-cervical.png'),timeout=45000)
  ck('No uncaught JavaScript or WebGL errors',not errors);ck('No external requests',not requests);b.close()
finally:
 report={'sha256':hashlib.sha256(html.encode()).hexdigest(),'passed':sum(x['pass']for x in checks),'failed':sum(not x['pass']for x in checks),'checks':checks,'errors':errors,'requests':requests,'fixture':'Isolated memory storage, parked renderer between real WebGL keyframes. GPU test executes unmodified production vertex shader via transform feedback.'}
 (O/'cervical-browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
