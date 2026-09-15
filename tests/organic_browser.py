"""v0.13 acceptance: creator, appearance migration, DQ upload and library filters.
Real WebGL keyframes and DOM events; memory storage fixture. Not a hardware FPS test.
"""
from pathlib import Path
import json,os,time,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v013';os.environ.setdefault('DISPLAY',':99')
source=Path(os.environ.get('DC_TEST_HTML',str(R/'index.html')));html=source.read_text();checks=[];errors=[];requests=[]
FIX="""(()=>{window.testStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore.get(k)||null,setItem:(k,v)=>testStore.set(k,String(v)),removeItem:k=>testStore.delete(k)}});})();"""
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(('PASS 'if v else'FAIL ')+n,flush=True);assert v,n
def slider(p,id,value):p.locator('#'+id).evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));}',value)
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1120,'height':800});p.set_default_timeout(15000)
  p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content(html.replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady');p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}');p.click('#start')
  ck('Neck control exists in initial selection',p.locator('#characterNeck').count()==1)
  original=p.evaluate('DC_APP.sim.serialize()');draft=p.evaluate('DC_APP.creator.look');slider(p,'characterNeck',75);ck('Neck control updates only draft',p.evaluate('DC_APP.creator.look.neck===.75')and p.evaluate('DC_APP.sim.serialize()')==original)
  p.select_option('#characterFocus','neck');p.wait_for_timeout(100);p.evaluate('drawActual(DC_APP.creator.preview)')
  ck('Neck customization uploaded to GPU instance',abs(p.evaluate('DC_APP.renderer.appearancePixels[3]')-.75)<1e-6)
  ck('DQ deformation is the production crowd path',p.evaluate('DC_APP.renderer.visualStats.skinning==="dual-quaternion"&&DC_APP.renderer.dualPixels.length===49*8*128'))
  ck('Uploaded first bone quaternion is normalized',p.evaluate('Math.abs(Math.hypot(...DC_APP.renderer.dualPixels.slice(0,4))-1)<.00001'))
  ck('No shader error in neck inspection',p.evaluate('DC_APP.renderer.gl.getError()===0'))
  p.click('#compareAppearance');ck('Compare shows initial appearance without replacing draft',p.evaluate('DC_APP.creator.preview.appearance.neck===0&&DC_APP.creator.look.neck===.75&&DC_APP.creator.comparing'))
  p.click('#compareAppearance');ck('Compare returns to unchanged draft',p.evaluate('DC_APP.creator.preview.appearance.neck===.75&&!DC_APP.creator.comparing'))
  p.select_option('#characterLight','side');ck('Lateral inspection changes only studio lighting',p.evaluate('DC_APP.renderer.daylight===.14&&DC_APP.creator.preview.world.lights.length===2'))
  p.select_option('#characterLight','neutral');p.select_option('#characterFocus','hands');p.select_option('#characterPose','grip');p.wait_for_function('DC_APP.creator.preview.player.grip===.82',timeout=15000);state=p.evaluate('({grip:DC_APP.creator.preview.player.grip,gl:DC_APP.renderer.gl.getError()})');print('GRIP PRE',state,flush=True);assert state['gl']==0,state;p.evaluate('drawActual(DC_APP.creator.preview)');ck('Hand inspection renders articulated grip',p.evaluate('DC_APP.creator.preview.player.grip===.82&&DC_APP.renderer.gl.getError()===0'))
  p.screenshot(path=str(O/'editor-hand.png'),timeout=45000)
  p.select_option('#characterPose','walk');p.select_option('#characterTempo','0.25');p.wait_for_function('Math.abs(DC_APP.creator.preview.player.moveSpeed-1.4)<.1',timeout=20000)
  ck('Slow-motion selector is editor-only',p.evaluate('document.getElementById("characterTempo").value==="0.25"')and p.evaluate('DC_APP.sim.serialize()')==original)
  p.select_option('#characterFocus','feet');p.evaluate('drawActual(DC_APP.creator.preview)')
  ck('Foot inspection focuses legs and uses contact-aware rig',p.evaluate('DC_APP.creator.focus==="feet"&&DC_APP.renderer.motionDebug.feet.L!==null&&DC_APP.renderer.gl.getError()===0'))
  ck('Preview uses no false world-space locks for treadmill animation',p.evaluate('DC_APP.renderer.motionDebug.motion.inPlace&&DC_APP.renderer.motionDebug.motion.feet.L===null'))
  p.select_option('#characterTempo','1');p.select_option('#characterPose','run');p.wait_for_function('DC_APP.creator.preview.player.sprintBlend>.97',timeout=15000);p.evaluate('drawActual(DC_APP.creator.preview)')
  ck('Running arm articulation is no longer a nearly straight elbow',p.evaluate('DC.SkinRig.pose(DC_APP.creator.preview.player,2).pose.left.elbow>.8'))
  p.select_option('#characterPose','seated');p.wait_for_function('DC_APP.creator.preview.player.seated',timeout=15000);p.evaluate('drawActual(DC_APP.creator.preview)')
  ck('Seated inspection has real wrist targets and no floor contacts',p.evaluate('DC_APP.creator.preview.player.handTargets.R&&DC_APP.renderer.motionDebug.feet.L===null&&DC_APP.renderer.gl.getError()===0'))
  p.select_option('#characterPose','reach');p.wait_for_function('DC_APP.creator.preview.player.reach>.98&&DC_APP.creator.preview.player.seatBlend<.01',timeout=15000);p.evaluate('drawActual(DC_APP.creator.preview)')
  ck('Reach inspection extends just the selected arm without state mutation',p.evaluate('DC_APP.creator.preview.player.handTargets.R&&!DC_APP.creator.preview.player.handTargets.L&&DC_APP.renderer.gl.getError()===0')and p.evaluate('DC_APP.sim.serialize()')==original)
  p.select_option('#characterPose','idle');p.select_option('#characterFocus','full');p.wait_for_function('DC_APP.creator.preview.player.reach<.01',timeout=15000)
  ck('All inspection poses return to a neutral stance',p.evaluate('DC_APP.creator.preview.player.seatBlend<.01&&!DC_APP.creator.preview.player.handTargets'))
  p.fill('#characterName','Río');p.fill('#newSaveName','Ruta de Río');p.click('#commitCreator');ck('Commit preserves named slot and new neck field',p.evaluate('DC_APP.getStore().active().data.identity.look.neck===.75&&DC_APP.sim.characterName==="Río"'))
  ck('World camera and lighting restore after studio',p.evaluate('!DC_APP.renderer.previewStudio&&DC_APP.creator===null&&DC_APP.renderer.daylight!==.50'))
  p.click('#dismissTutorial');p.keyboard.press('Escape');p.click('#editAppearance');slider(p,'characterNeck',-80);p.click('#closeCreator');ck('Cancel restores previous identity exactly',p.evaluate('DC_APP.sim.appearance.neck===.75'))
  p.evaluate('const a=DC_APP,s=a.sim.serialize();delete s.identity.look.neck;s.identity.name="Nácar";s.cash=420;s.story=4;a.getStore().create("Bosque",s,{activate:false});s.story=1;s.identity.name="Sol";a.getStore().create("Ciudad",s,{activate:false});');p.click('#pauseSaves')
  before=p.evaluate('DC_APP.getStore().raw()');p.fill('#librarySearch','nacar');ck('Search folds accent and includes character name',p.locator('.save-card').count()==1 and p.locator('.slot-name').input_value()=='Bosque')
  p.fill('#librarySearch','sin coincidencias');ck('No-match message does not say catalogue is empty',p.locator('.save-card').count()==0 and 'No hay coincidencias' in p.locator('#saveCards').inner_text());ck('Backup remains available for filtered-out saves',p.locator('#libraryExportAll').is_enabled())
  p.fill('#librarySearch','');p.select_option('#librarySort','name');ck('Name order works',p.locator('.slot-name').first.input_value()=='Bosque');p.select_option('#librarySort','progress');ck('Progress order works',p.locator('.slot-name').first.input_value()=='Bosque');ck('Viewing/filtering never changes saved bytes',p.evaluate('DC_APP.getStore().raw()')==before)
  p.screenshot(path=str(O/'library.png'),timeout=45000)
  p.locator('.slot-load').first.click();ck('Older v0.11 identity migrates missing neck to neutral',p.evaluate('DC_APP.sim.characterName==="Nácar"&&DC_APP.sim.appearance.neck===0&&DC_APP.sim.cash===420'))
  p.keyboard.press('Escape');p.click('#editAppearance');p.select_option('#characterFocus','neck');slider(p,'characterNeck',-75);p.click('#compareAppearance');p.click('#commitCreator');ck('Apply from comparison saves draft not temporary comparison',p.evaluate('DC_APP.sim.appearance.neck===-.75&&DC_APP.getStore().active().data.identity.look.neck===-.75'))
  ck('No JavaScript/WebGL errors',not errors);ck('No external requests',not requests);b.close()
finally:
 report={'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'checks':checks,'errors':errors,'requests':requests,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'environment':'Chromium Xvfb SwiftShader. Keyframe rendering with renderer parked between captures; actual DOM input. Isolated memory storage, not persistence after browser restart.'};(O/os.environ.get('DC_TEST_REPORT','organic-browser.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
