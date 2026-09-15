"""Current-release acceptance: real DOM input and WebGL keyframes, isolated storage fixture.
Renderer alone is parked between keyframes to avoid timing the software GPU.
A separate identity_continuous.py tests the unmodified loop. No native file storage claim.
"""
from pathlib import Path
import json,os,hashlib,time
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v014';os.environ.setdefault('DISPLAY',':99')
HTML=(R/'index.html').read_text();checks=[];errors=[];requests=[];pages=0
FIXTURE='''(()=>{window.testStore=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>testStore.get(k)||null,setItem:(k,v)=>testStore.set(k,String(v)),removeItem:k=>testStore.delete(k)}});})();'''
def ck(n,v):
 checks.append({'name':n,'pass':bool(v)});print(time.strftime('%H:%M:%S'),('PASS 'if v else'FAIL ')+n,flush=True);assert v,n
def load(b,w=1120,h=760,touch=False,extra=''):
 global pages
 pages+=1;c=b.new_context(viewport={'width':w,'height':h},has_touch=touch,device_scale_factor=1,is_mobile=touch);p=c.new_page();p.set_default_timeout(30000)
 p.on('pageerror',lambda e:errors.append(str(e)));p.on('console',lambda m:errors.append(m.text)if m.type=='error'else None);p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
 p.set_content(HTML.replace('<script>','<script>'+FIXTURE+extra,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady');p.evaluate('window.renderKeyframe=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}');return c,p
def frame(p,name):
 p.wait_for_timeout(130);p.evaluate('renderKeyframe(DC_APP.creator?.preview||DC_APP.sim)');ck('WebGL keyframe '+name,p.evaluate('DC_APP.renderer.gl.getError()===0'));p.screenshot(path=str(O/(name+'.png')),timeout=60000)
def slider(p,id,v):p.locator('#'+id).evaluate('(e,v)=>{e.value=v;e.dispatchEvent(new Event("input",{bubbles:true}));}',v)
def card(s):return '[data-slot="'+s+'"]'
def modal(p,selector,accept):
 p.once('dialog',lambda d:d.accept()if accept else d.dismiss());p.click(selector)
def import_obj(p,obj,name='importada.json'):
 p.locator('#saveFile').set_input_files({'name':name,'mimeType':'application/json','buffer':json.dumps(obj).encode()});p.wait_for_timeout(250)
def hit(p,id):return p.evaluate('''id=>{const e=document.getElementById(id),r=e.getBoundingClientRect(),h=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return r.width>0&&r.x>=0&&r.y>=0&&r.right<=innerWidth+.1&&r.bottom<=innerHeight+.1&&(h===e||e.contains(h));}''',id)
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  c,p=load(b)
  ck('Landing offers creator and named library',p.locator('#start').is_visible()and p.locator('#landingSaves').is_visible())
  p.click('#start');ck('New story enters creator before gameplay',p.evaluate('DC_APP.mode==="creator"&&!DC_APP.started'))
  ck('Draft uses a separate simulation and world',p.evaluate('DC_APP.creator.preview!==DC_APP.sim&&DC_APP.creator.preview.world!==DC_APP.world'))
  ck('Four selectable presets',p.locator('.preset-choice').count()==4)
  p.click('#previewMotion');ck('Pose pause supported',p.evaluate('!DC_APP.creator.animate'))
  p.fill('#characterName','Noa');p.fill('#newSaveName','Noa · La primera noche');p.click('[data-preset="2"]');slider(p,'characterBuild',64);slider(p,'characterFace',-52)
  p.select_option('#characterHairStyle','2');p.locator('[data-key="skin"][data-value="2"]').click();p.locator('[data-key="eyes"][data-value="2"]').click();p.locator('[data-key="hair"][data-value="1"]').click();p.locator('[data-key="coat"][data-value="0"]').click();p.locator('[data-key="pants"][data-value="1"]').click()
  ck('Controls update distinct whitelisted appearance',p.evaluate('DC_APP.creator.preview.characterName==="Noa"&&DC_APP.creator.look.build===.64&&DC_APP.creator.look.face===-.52&&DC_APP.creator.look.eyes===2'))
  before=p.evaluate('DC_APP.creator.yaw');p.click('#previewRight');ck('Orbit button changes preview yaw',p.evaluate('DC_APP.creator.yaw')!=before)
  p.click('#previewLeft');p.locator('#creatorForm').evaluate('e=>e.scrollTop=0');frame(p,'01-editor')
  ck('Actor appearance reaches GPU',p.evaluate('Math.abs(DC_APP.renderer.appearancePixels[0]-.64)<.001&&DC_APP.renderer.appearancePixels[2]===2'))
  p.click('#previewFrame');frame(p,'02-editor-face');p.click('#previewFrame')
  ck('Blank character name blocks creation',not (p.fill('#characterName',' ')or p.click('#commitCreator')or p.evaluate('DC_APP.mode!=="creator"')))
  p.fill('#characterName','Noa');p.fill('#newSaveName',' ');p.click('#commitCreator');ck('Blank save name blocks creation',p.evaluate('DC_APP.mode==="creator"&&DC_APP.getStore().list().length===0'))
  p.fill('#newSaveName','Noa · La primera noche');p.click('#commitCreator');p.wait_for_function('DC_APP.mode==="play"');p.click('#dismissTutorial');p.keyboard.press('Escape')
  a=p.evaluate('DC_APP.activeSlot.id');look=p.evaluate('DC_APP.sim.appearance');ck('New slot contains selected identity',p.evaluate('DC_APP.getStore().active().data.identity.name==="Noa"&&DC_APP.sim.appearance.hairStyle===2'))
  ck('Renderer leaves studio and canvas fills viewport',p.evaluate('!DC_APP.renderer.previewStudio&&!DC_APP.creator&&document.getElementById("world").getBoundingClientRect().width===innerWidth'))
  p.evaluate('DC_APP.sim.cash=1299;DC_APP.sim.story=2');p.click('#saveGame');p.click('#editAppearance');p.click('[data-preset="3"]');p.fill('#characterName','Descartar')
  ck('Editing does not alter current session before apply',p.evaluate('DC_APP.sim.characterName==="Noa"&&DC_APP.sim.cash===1299'))
  p.keyboard.press('Escape');ck('Escape cancels draft even in text field',p.evaluate('DC_APP.mode==="pause"&&DC_APP.sim.characterName==="Noa"'));ck('Cancel keeps exact appearance',p.evaluate('DC_APP.sim.appearance')==look)
  p.click('#editAppearance');p.fill('#characterName','Noa Río');p.select_option('#characterHairStyle','1');p.click('#commitCreator');ck('Apply updates active save identity',p.evaluate('DC_APP.getStore().active().data.identity.name==="Noa Río"&&DC_APP.mode==="pause"'))
  p.click('#pauseSaves');p.click('#libraryNew');p.click('[data-preset="1"]');p.fill('#characterName','Luz');p.fill('#newSaveName','Luz · Horizonte');p.click('#commitCreator');p.click('#dismissTutorial');p.keyboard.press('Escape');p.evaluate('DC_APP.sim.cash=2345');p.click('#saveGame');bid=p.evaluate('DC_APP.activeSlot.id')
  ck('Second creation preserves first slot',p.evaluate('DC_APP.getStore().list().length===2')and a!=bid)
  ck('First slot keeps its own mission and money',p.evaluate('(id)=>{const s=DC_APP.getStore().get(id);return s.data.cash===1299&&s.data.story===2&&s.data.identity.name==="Noa Río"}',a))
  p.click('#pauseSaves');p.click(card(a)+' .slot-load');ck('Loading A restores its appearance and progress',p.evaluate('DC_APP.sim.characterName==="Noa Río"&&DC_APP.sim.cash===1299&&DC_APP.sim.story===2'))
  p.keyboard.press('Escape');p.click('#pauseSaves');p.click(card(bid)+' .slot-load');ck('Loading B restores its independent progress',p.evaluate('DC_APP.sim.characterName==="Luz"&&DC_APP.sim.cash===2345'))
  p.keyboard.press('Escape');p.click('#pauseSaves');p.locator(card(a)+' input').fill('Ruta rural · Noa');p.click(card(a)+' .slot-name-row button');ck('Rename retains identity and snapshot',p.evaluate('(id)=>{const s=DC_APP.getStore().get(id);return s.name==="Ruta rural · Noa"&&s.data.identity.name==="Noa Río"&&s.data.cash===1299}',a))
  p.click(card(a)+' .slot-duplicate');ck('Duplicate has its own id without switching live game',p.evaluate('DC_APP.getStore().list().length===3&&DC_APP.sim.characterName==="Luz"'))
  p.fill('#copySaveName','Luz · Cruce alternativo');p.click('#librarySaveCopy');dup=p.evaluate('DC_APP.activeSlot.id');ck('Save as copy creates and activates independent branch',p.evaluate('DC_APP.getStore().get(DC_APP.activeSlot.id).name==="Luz · Cruce alternativo"&&DC_APP.getStore().list().length===4'))
  frame(p,'03-library')
  modal(p,card(dup)+' .slot-delete',False);ck('Deletion cancelled leaves slot intact',p.evaluate('id=>!!DC_APP.getStore().get(id)',dup))
  modal(p,card(dup)+' .slot-delete',True);ck('Delete active detaches current session, no resurrection',p.evaluate('DC_APP.detached&&DC_APP.activeSlot===null&&DC_APP.getStore().list().length===3'))
  ck('Detached autosave does not recreate deleted slot',p.evaluate('DC_APP.save(false)===false&&DC_APP.getStore().list().length===3'))
  # Actual browser download events for saved snapshot and multi-slot backup.
  with p.expect_download() as dl:p.click(card(a)+' .slot-export')
  snap=json.loads(Path(dl.value.path()).read_text());ck('Per-slot JSON has name and appearance',snap['format']=='distrito-cero-slot'and snap['name']=='Ruta rural · Noa'and snap['data']['identity']['name']=='Noa Río')
  with p.expect_download() as dl:p.click('#libraryExportAll')
  group=json.loads(Path(dl.value.path()).read_text());ck('Bulk backup contains all saved slots',group['format']=='distrito-cero-collection'and len(group['slots'])==3)
  prior=p.evaluate('DC_APP.getStore().raw()');import_obj(p,{'version':999},'rota.json');ck('Invalid import does not write any slot',p.evaluate('DC_APP.getStore().raw()')==prior)
  bad=json.loads(json.dumps(group));bad['slots'][1]['data']['identity']['look']['build']=10;import_obj(p,bad);ck('Bulk import all-or-nothing validation',p.evaluate('DC_APP.getStore().raw()')==prior)
  import_obj(p,snap);ck('Import appends instead of overwriting',p.evaluate('DC_APP.getStore().list().length===4'))
  legacy=dict(snap['data']);del legacy['identity'];import_obj(p,legacy,'Anterior v0.10.json');ck('Legacy JSON import receives default identity',p.evaluate('DC_APP.getStore().list().some(s=>s.name==="Anterior v0.10"&&s.data.identity.name==="Alex")'))
  p.click(card(a)+' .slot-load');p.keyboard.press('Escape');p.click('#pauseSaves');prior=p.evaluate('DC_APP.getStore().raw()')
  p.evaluate('()=>{window.realWrite=DC_APP.getStore().storage.setItem;DC_APP.getStore().storage.setItem=()=>{throw new Error("QuotaExceededError")}}');p.click('#librarySaveCurrent');ck('Quota warning replaces success message',p.locator('#libraryMessage').inner_text().find('No se pudo guardar')>=0);ck('Quota leaves saved bytes intact',p.evaluate('DC_APP.getStore().raw()')==prior)
  p.evaluate('()=>{DC_APP.getStore().storage.setItem=realWrite}');p.click('#closeLibrary');p.click('#editAppearance');original=p.evaluate('({name:DC_APP.sim.characterName,look:DC_APP.sim.appearance})');p.fill('#characterName','No persistir');p.evaluate('()=>{DC_APP.getStore().storage.setItem=()=>{throw new Error("QuotaExceededError")}}');p.click('#commitCreator');ck('Edit rolls back if persistence fails',p.evaluate('({name:DC_APP.sim.characterName,look:DC_APP.sim.appearance})')==original);p.evaluate('()=>{DC_APP.getStore().storage.setItem=realWrite}');p.click('#closeCreator')
  # Detect already-stale save revisions rather than writing live stale state over newer data.
  p.evaluate('const s=DC_APP.getStore().get(DC_APP.activeSlot.id);s.data.cash=8877;DC_APP.getStore().update(s.id,s.data,s.revision)');ck('Stale live revision refuses overwrite',p.evaluate('DC_APP.save(false)===false&&DC_APP.getStore().get(DC_APP.activeSlot.id).data.cash===8877'))
  p.click('#pauseSaves');ck('Conflict is explained in library', 'conflicto' in p.locator('#libraryMessage').inner_text());modal(p,card(a)+' .slot-load',True);ck('Reload after conflict restores newer state',p.evaluate('DC_APP.sim.cash===8877'));p.keyboard.press('Escape');p.click('#pauseSaves')
  ck('Names rendered as text not HTML',p.evaluate('()=>{const x=DC_APP.getStore().create("<img src=x>",DC_APP.sim.serialize(),{activate:false});DC_APP.paintLibrary();return !document.querySelector(".save-card img")&&Array.from(document.querySelectorAll(".save-card input")).some(n=>n.value==="<img src=x>")}'))
  store=p.evaluate('Array.from(testStore.entries())');c.close()
  # Recreated page with captured fixture. This is not a test of native browser localStorage.
  c,p=load(b,extra='for(const [k,v]of '+json.dumps(store)+')testStore.set(k,v);');ck('Catalogue rehydrates on a recreated page',p.evaluate('DC_APP.getStore().list().length===6'));p.click('#continue');ck('Continue restores stored identity and newer progress',p.evaluate('DC_APP.sim.characterName==="Noa Río"&&DC_APP.sim.cash===8877'));c.close()
  for w,h in [(390,844),(844,390)]:
   c,p=load(b,w,h,True);p.tap('#start');p.wait_for_timeout(200);ck(f'{w}: creator footer and return reachable',hit(p,'commitCreator')and hit(p,'closeCreator'))
   ck(f'{w}: preview fits viewport',p.evaluate('(()=>{let r=document.getElementById("world").getBoundingClientRect();return r.width>100&&r.height>70&&r.x>=0&&r.y>=0&&r.right<=innerWidth+.1&&r.bottom<=innerHeight+.1})()'))
   p.locator('[data-preset="3"]').tap();p.locator('#characterName').fill('Sol');p.locator('#newSaveName').fill('Sol '+str(w));p.locator('[data-key="coat"][data-value="5"]').tap();ck(f'{w}: scroll reaches palette swatch',p.evaluate('DC_APP.creator.look.coat===5'));p.locator('#creatorForm').evaluate('e=>e.scrollTop=0');frame(p,'04-creator-'+str(w))
   p.tap('#commitCreator');ck(f'{w}: tactile commit creates slot',p.evaluate('DC_APP.mode==="play"&&DC_APP.getStore().list().length===1'));p.tap('#dismissTutorial');p.tap('#pauseButton');p.tap('#pauseSaves');ck(f'{w}: library close reachable',hit(p,'closeLibrary'));p.locator('.slot-name-row button').tap();ck(f'{w}: card actions operable',p.evaluate('DC_APP.getStore().list()[0].revision>=2'));frame(p,'05-library-'+str(w));c.close()
  # Explicit storage unavailable path, not a pretend persistent in-memory fallback in production.
  c,p=load(b,extra='Object.defineProperty(localStorage,"setItem",{value:()=>{throw new Error("SecurityError")}});');p.click('#start');p.click('#commitCreator');ck('Storage denied offers explicit volatile session',p.evaluate('DC_APP.mode==="creator"&&!document.getElementById("playVolatile").hidden'));p.click('#playVolatile');ck('Volatile session is playable and marked unsaved',p.evaluate('DC_APP.mode==="play"&&DC_APP.detached&&DC_APP.activeSlot===null'));c.close()
  ck('No JavaScript or WebGL console errors',not errors);ck('No external requests during game',not requests);b.close()
finally:
 report={'passed':sum(x['pass']for x in checks),'failed':sum(not x['pass']for x in checks),'checks':checks,'errors':errors,'requests':requests,'pages':pages,'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'environment':'Chromium Xvfb SwiftShader. Real DOM inputs; keyframe WebGL, renderer parked between captures. Memory localStorage fixture. No native persistence or hardware FPS claim.'};(O/'library-regression.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print('RESULT',report['passed'],report['failed'],flush=True)
