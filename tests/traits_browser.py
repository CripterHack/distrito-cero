"""Rasgos acceptance using production DOM/shaders and deterministic WebGL keyframes.
Memory storage fixture, not a claim of native file:// persistence.
"""
from pathlib import Path
import os,json,hashlib,time
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v016';os.environ.setdefault('DISPLAY',':99');checks=[];errors=[];requests=[]
html=(R/'index.html').read_text();FIX='''(()=>{window.testStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore.get(k)||null,setItem:(k,v)=>testStore.set(k,String(v)),removeItem:k=>testStore.delete(k)}});})();'''
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(('PASS 'if v else'FAIL ')+n,flush=True);assert v,n
def slide(p,id,v):p.locator('#'+id).evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));}',v)
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  p=b.new_page(viewport={'width':1100,'height':800});p.set_default_timeout(25000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
  ck('WebGL boots with fitted rig and modular hairstyles',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}');p.click('#start');p.click('#previewMotion')
  ck('Eleven real hair choices in the creator',p.locator('#characterHairStyle option').count()==11)
  before=p.evaluate('DC_APP.sim.serialize()')
  for style in range(11):
   p.select_option('#characterHairStyle',str(style));p.evaluate('drawActual(DC_APP.creator.preview)')
   ck('Style '+str(style)+' reaches shader and selected geometry',p.evaluate('(s)=>DC_APP.renderer.appearancePixels[2]===s&&DC_APP.renderer.hairParts.has(s+":0")&&DC_APP.renderer.gl.getError()===0',style))
  ck('Hair cache is bounded by style/LOD',p.evaluate('DC_APP.renderer.hairParts.size<=33&&DC.HairGeometry.cacheSize()<=33'))
  ck('Bald selection does not remove eyebrows',p.evaluate('DC_APP.renderer.lodParts[0].find(p=>p.name==="hair").vertices>0'))
  p.select_option('#characterHairStyle','8');slide(p,'characterNeckLength',-80);slide(p,'characterHairVolume',65);p.uncheck('#characterBrowMatch');p.evaluate('drawActual(DC_APP.creator.preview)')
  ck('New independent traits reach per-actor GPU row',p.evaluate('Math.abs(DC_APP.renderer.appearancePixels[4]+.8)<1e-5&&Math.abs(DC_APP.renderer.appearancePixels[5]-.65)<1e-5&&DC_APP.renderer.appearancePixels[6]===0'))
  ck('Shorter bind rig is used by the real renderer',p.evaluate('Math.abs(DC_APP.renderer.motionDebug.neckDrop-.0546)<1e-5'))
  ck('Editor does not mutate active gameplay',p.evaluate('DC_APP.sim.serialize()')==before)
  gpu=p.evaluate((R/'tests/traits_gpu.js').read_text());(O/'gpu-transform-feedback.json').write_text(json.dumps(gpu,indent=2))
  ck('432 production GPU transforms agree with fitted CPU coordinates',gpu['maxPositionError']<2e-6)
  ck('Production normal transform agrees with numeric derivatives',gpu['maxNormalError']<.003)
  ck('Transform feedback has no GL error',gpu['gl']==0)
  # Restore texture bindings after the independent feedback program.
  p.evaluate('drawActual(DC_APP.creator.preview)')
  p.fill('#characterName','Ícaro');p.fill('#newSaveName','Rasgos · noche');p.click('#commitCreator');p.click('#dismissTutorial');p.keyboard.press('Escape');sid=p.evaluate('DC_APP.activeSlot.id')
  ck('Named slot serializes style, volume, brows and neck length',p.evaluate('DC_APP.getStore().active().data.identity.look.hairStyle===8&&DC_APP.sim.appearance.neckLength===-.8&&!DC_APP.sim.appearance.browMatch'))
  p.click('#editAppearance');p.select_option('#characterHairStyle','10');slide(p,'characterNeckLength',100);p.click('#compareAppearance');p.click('#commitCreator')
  ck('Apply from comparison commits draft instead of comparison image',p.evaluate('DC_APP.sim.appearance.hairStyle===10&&DC_APP.sim.appearance.neckLength===1'))
  p.click('#editAppearance');p.select_option('#characterHairStyle','3');p.click('#closeCreator');ck('Cancel leaves previous hairstyle intact',p.evaluate('DC_APP.sim.appearance.hairStyle===10'))
  p.click('#pauseSaves');p.click('#libraryNew');p.fill('#characterName','Luna');p.fill('#newSaveName','Rasgos · campo');p.select_option('#characterHairStyle','9');slide(p,'characterNeckLength',0);p.click('#commitCreator');p.click('#dismissTutorial');p.keyboard.press('Escape');second=p.evaluate('DC_APP.activeSlot.id')
  p.click('#pauseSaves');p.click('[data-slot="'+sid+'"] .slot-load')
  ck('Loading first named slot restores its own appearance',p.evaluate('DC_APP.sim.characterName==="Ícaro"&&DC_APP.sim.appearance.hairStyle===10&&DC_APP.sim.appearance.neckLength===1'))
  p.keyboard.press('Escape');p.click('#pauseSaves');p.click('[data-slot="'+second+'"] .slot-load')
  ck('Loading second slot restores a different hairstyle',p.evaluate('DC_APP.sim.characterName==="Luna"&&DC_APP.sim.appearance.hairStyle===9'))
  p.keyboard.press('Escape');p.click('#pauseSaves')
  with p.expect_download() as dl:p.click('#libraryExportAll')
  bundle=json.loads(Path(dl.value.path()).read_text());ck('Real downloaded backup contains both hairstyles',sorted(x['data']['identity']['look']['hairStyle']for x in bundle['slots'])==[9,10])
  p.click('#closeLibrary');p.click('#editAppearance')
  for w,h in [(390,844),(844,390)]:
   p.set_viewport_size({'width':w,'height':h});p.wait_for_timeout(100)
   for field in ['characterHairStyle','characterNeckLength','characterHairVolume','characterBrowMatch']:
    e=p.locator('#'+field);e.scroll_into_view_if_needed()
    ck('Control '+field+' reachable at '+str(w),e.evaluate('(e)=>{const r=e.getBoundingClientRect();return r.width>0&&r.x>=0&&r.right<=innerWidth+1&&r.y>=0&&r.bottom<=innerHeight+1;}'))
   p.select_option('#characterHairStyle','7');slide(p,'characterNeckLength',-50);p.evaluate('drawActual(DC_APP.creator.preview)');p.screenshot(path=str(O/('creator-'+str(w)+'.png')),timeout=60000)
   ck('Responsive creator renders selected style '+str(w),p.evaluate('DC_APP.renderer.gl.getError()===0'))
  ck('No JavaScript or shader exceptions',not errors);ck('No external network requests',not requests);b.close()
finally:
 report={'sha256':hashlib.sha256(html.encode()).hexdigest(),'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'checks':checks,'errors':errors,'requests':requests,'fixture':'DOM interactions with isolated memory storage and real WebGL keyframes; continuous suite run separately.'}
 (O/'traits-browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
