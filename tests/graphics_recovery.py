"""Issue #4: actual WEBGL_lose_context events, production reconstruction and native RAF.
Local fallback injects an explicit storage fixture; CI can use the portable QA adapter.
Prepared world states are not a performance benchmark or a full playthrough.
"""
from pathlib import Path
import json, hashlib, os
from playwright.sync_api import sync_playwright
from qa_support import launch_options
R=Path(__file__).resolve().parents[1]
O=Path(os.environ.get('DC_QA_REPORT_DIR',str(R/('qa/v019' if os.environ.get('DC_QA_RUN_ID') else 'artifacts/recovery-local'))));O.mkdir(parents=True,exist_ok=True)
checks=[];errors=[];requests=[]
FIX="""(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);window.qaStorage=d;Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(('PASS ' if v else 'FAIL ')+n,flush=True);assert v,n
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(**launch_options())
  p=browser.new_page(viewport={'width':740,'height':550});p.set_default_timeout(45000)
  p.on('pageerror',lambda e:(errors.append(str(e)),print('PAGEERROR',e,flush=True)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
  p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
  ck('Recovery controller boots with the native game loop',p.evaluate('DC_APP.graphics.state==="ready"&&DC_APP.frameRequest!=null'))
  p.click('#start');p.fill('#characterName','Recuperación');p.fill('#newSaveName','Prueba de contexto');p.click('#commitCreator');p.click('#dismissTutorial')
  p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.free=true;s.heat=s.wanted=0;s.cash=987;s.cars.forEach((c,i)=>Object.assign(c,{x:-250,z:-300-i*5,parked:true,speed:0}));s.peds.forEach(n=>n.hidden=true);Object.assign(s.player,{x:4,z:36,yaw:0,car:null});a.renderer.camera.yaw=0;a.renderer.daylight=.65;a.sim.equipWeapon('gauss');a.save(false);window.sameSim=s;window.savedBytes=a.getStore().raw();}''')
  p.keyboard.down('j');p.wait_for_function('DC_APP.sim.equipment.charge>.25');
  p.evaluate('''()=>{window.oldRenderer=DC_APP.renderer;window.ext=oldRenderer.gl.getExtension('WEBGL_lose_context');window.epochFrame=DC_APP.frameCount;ext.loseContext();}''')
  p.wait_for_function('DC_APP.graphics.state==="lost"')
  ck('Actual loss event pauses drawing and simulation',p.evaluate('DC_APP.mode==="recovering"&&DC_APP.frameRequest===null&&oldRenderer.disposed&&oldRenderer.resources.stats().total===0'))
  ck('Direct render while lost cannot build sectors or mutate the retired generation',p.evaluate("""()=>{const r=oldRenderer,f=r.frame,sim=DC_APP.sim,before=JSON.stringify(sim.serialize());return r.render(sim)===false&&r.frame===f&&r.sectorGPU.size===0&&JSON.stringify(sim.serialize())===before;}"""))
  p.keyboard.up('j');p.evaluate('window.lossTime=DC_APP.sim.time;window.lossFrame=DC_APP.frameCount;window.shots=DC_APP.sim.equipment.shots;window.ammo=JSON.stringify(DC_APP.sim.equipment.ammo)')
  p.keyboard.press('j');p.keyboard.press('f');p.wait_for_timeout(160)
  ck('Inputs cannot fire or enter cars behind the recovery dialog',p.evaluate('DC_APP.sim.time===lossTime&&DC_APP.frameCount===lossFrame&&DC_APP.sim.equipment.shots===shots&&!DC_APP.sim.access'))
  ck('Held Gauss charge was cancelled without spending ammo',p.evaluate('DC_APP.sim.equipment.charge===0&&JSON.stringify(DC_APP.sim.equipment.ammo)===ammo'))
  p.keyboard.press('Tab');ck('Keyboard focus remains inside recovery dialog',p.evaluate('document.getElementById("graphicsRecovery").contains(document.activeElement)'))
  with p.expect_download() as download:p.click('#recoveryExport')
  file=O/'exported-session.json';download.value.save_as(file);data=json.loads(file.read_text());ck('Live JSON export is usable while graphics are lost',data['format']=='distrito-cero-slot' and data['data']['cash']==987)
  file.unlink()
  ck('Existing catalogue was not overwritten by loss or export',p.evaluate('DC_APP.getStore().raw()===savedBytes'))
  p.screenshot(path=str(O/'recovery-panel.png'))
  p.evaluate('ext.restoreContext()');p.wait_for_function('DC_APP.graphics.state==="recovered"',timeout=90000)
  ck('Restore rebuilds resources and all embedded skin maps',p.evaluate('DC_APP.renderer!==oldRenderer&&DC_APP.renderer.humanTextureStatus.loaded===3&&DC_APP.renderer.resources.stats().total>0&&DC_APP.renderer.gl.getError()===0'))
  ck('A stale renderer stays inert after the context has been restored',p.evaluate("""()=>{const r=DC_APP.renderer,before=r.resources.stats().total,f=oldRenderer.frame;return oldRenderer.render(DC_APP.sim)===false&&oldRenderer.syncSectors(2)===false&&oldRenderer.frame===f&&r.resources.stats().total===before&&r.gl.getError()===0;}"""))
  ck('New generation still renders a real frame after rejecting a stale draw',p.evaluate("""()=>{const r=DC_APP.renderer,f=r.frame;r.render(DC_APP.sim);r.gl.finish();return r.frame===f+1&&r.gl.getError()===0;}"""))
  ck('Same simulation and active identity survived restoration',p.evaluate('DC_APP.sim===sameSim&&DC_APP.sim.cash===987&&DC_APP.sim.characterName==="Recuperación"&&DC_APP.getStore().raw()===savedBytes'))
  ck('No simulation resumes until explicit acknowledgement',p.evaluate('DC_APP.mode==="recovering"&&DC_APP.sim.time===lossTime&&DC_APP.frameRequest===null'))
  p.click('#recoveryResume');p.wait_for_function('DC_APP.frameCount>lossFrame+2')
  ck('One native frame chain resumes without reactivating trigger',p.evaluate('DC_APP.mode==="play"&&DC_APP.frameRequest!=null&&DC_APP.sim.equipment.shots===shots&&DC_APP.graphics.state==="ready"'))
  ck('Repeated scheduling cannot add a second app RAF',p.evaluate('(()=>{const a=DC_APP,n=a.frameRequest;a.scheduleFrame();a.scheduleFrame();return a.frameRequest===n;})()'))
  p.screenshot(path=str(O/'restored-world.png'))
  # Warm matching asset/sector sets before comparing recovery generations.
  p.keyboard.press('Tab');p.evaluate('window.counts0=DC_APP.renderer.resources.stats().counts;window.r0=DC_APP.renderer;window.ext=r0.gl.getExtension("WEBGL_lose_context");ext.loseContext()')
  p.wait_for_function('DC_APP.graphics.state==="lost"');p.evaluate('ext.restoreContext()');p.wait_for_function('DC_APP.graphics.state==="recovered"',timeout=90000)
  ck('Repeated loss disposes the previous generation without live GPU handles',p.evaluate('r0.resources.stats().total===0&&r0.disposed&&DC_APP.recoveryStats.restores===2'))
  p.click('#recoveryResume');ck('Translucent equipment selector is restored with pending choice intact',p.evaluate('DC_APP.mode==="arsenal"&&!document.getElementById("arsenal").hidden'))
  p.keyboard.press('Escape');p.keyboard.press('Backquote');p.wait_for_timeout(80);p.keyboard.press('Escape');p.evaluate('DC_APP.openCreator(false,true)');p.wait_for_function('DC_APP.mode==="creator"')
  p.fill('#characterName','Borrador conservado');p.evaluate('''()=>{DC_APP.creator.look.hairStyle=8;DC_APP.previewChanged();DC_APP.creator.animate=false;window.draft=DC_APP.creator;window.draftTime=draft.elapsed;window.ext=DC_APP.renderer.gl.getExtension('WEBGL_lose_context');ext.loseContext();}''')
  p.wait_for_function('DC_APP.graphics.state==="lost"');p.set_viewport_size({'width':390,'height':844})
  ck('Recovery controls remain visible at phone width',p.locator('#recoveryRetry').is_visible() and p.locator('#recoveryDraft').is_visible())
  with p.expect_download() as dl:p.click('#recoveryDraft')
  f=O/'draft.json';dl.value.save_as(f);d=json.loads(f.read_text());ck('Unsaved appearance draft can also be exported',d['name']=='Borrador conservado' and d['appearance']['hairStyle']==8);f.unlink()
  p.evaluate('ext.restoreContext()');p.wait_for_function('DC_APP.graphics.state==="recovered"',timeout=90000);p.click('#recoveryResume')
  ck('Creator identity and unsaved draft survive actual context replacement',p.evaluate('DC_APP.mode==="creator"&&DC_APP.creator===draft&&DC_APP.creator.look.hairStyle===8&&document.getElementById("characterName").value==="Borrador conservado"'))
  p.click('#closeCreator');ck('Cancelling recovered draft leaves session identity unchanged',p.evaluate('DC_APP.sim.characterName==="Recuperación"&&DC_APP.sim.appearance.hairStyle!==8'))
  p.set_viewport_size({'width':740,'height':550});p.evaluate('DC_APP.setMode("pause");DC_APP.renderer.render(DC_APP.sim);DC_APP.renderer.gl.finish()')
  p.screenshot(path=str(O/'restored-game.png'))
  # An injected builder failure tests the product fallback, not a claim of a driver defect.
  p.evaluate('''()=>{window.buildOriginal=DC_APP.graphics.hooks.build;DC_APP.graphics.hooks.build=async()=>{throw Error('Controlled rebuild failure');};DC_APP.graphics.lose();}''');p.click('#recoveryRetry');p.wait_for_function('DC_APP.graphics.state==="failed"')
  ck('Failed reconstruction stays blocked and offers export',p.evaluate('DC_APP.frameRequest===null&&!document.getElementById("recoveryExport").hidden'))
  p.evaluate('()=>{DC_APP.graphics.hooks.build=buildOriginal;}');p.click('#recoveryRetry');p.wait_for_function('DC_APP.graphics.state==="recovered"',timeout=90000);p.click('#recoveryResume')
  ck('An explicit retry recovers after a controlled failure',p.evaluate('DC_APP.mode==="pause"&&DC_APP.sim===sameSim&&DC_APP.sim.cash===987'))
  ck('No shader or JavaScript errors in completed recovery paths',not errors);ck('No external runtime requests',not requests)
  observed=p.evaluate('({losses:DC_APP.recoveryStats.losses,restores:DC_APP.recoveryStats.restores,resources:DC_APP.renderer.resources.stats(),sectors:DC_APP.renderer.streamStats,frameCount:DC_APP.frameCount})');browser.close()
finally:
 result={'checks':checks,'passed':sum(c['pass'] for c in checks),'errors':errors,'requests':requests,'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'observed':locals().get('observed'),'environment':'Chromium SwiftShader, real context events and native RAF. Prepared state, explicit in-memory storage fixture. Not physical GPU performance.'}
 (O/'graphics-recovery.json').write_text(json.dumps(result,indent=2));print('RESULT',result['passed'],len(checks),flush=True)
