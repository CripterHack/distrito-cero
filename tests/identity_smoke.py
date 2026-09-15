from pathlib import Path
import json,os
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v011';os.environ['DISPLAY']=':99'
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 page=b.new_page(viewport={'width':1280,'height':840});errs=[];page.on('pageerror',lambda e:errs.append(str(e)))
 html=(R/'index.html').read_text()
 page.set_default_timeout(30000)
 page.route('https://distrito.test/**',lambda route:route.fulfill(status=200,content_type='text/html',body=html))
 try:
  page.goto('https://distrito.test/',timeout=60000);origin='virtual HTTPS origin via Playwright route, native localStorage'
 except Exception as e:
  print('origin navigation failed:',str(e)[:300],flush=True)
  page.set_content(html.replace('<script>','<script>Object.defineProperty(window,"localStorage",{value:{getItem:k=>window._m?.get(k)||(k==="distrito-cero:settings:v1"?JSON.stringify({quality:"eco",sound:false,rain:false,bloom:false}):null),setItem:(k,v)=>(window._m??=new Map()).set(k,v)}});',1),timeout=90000);origin='set_content memory fixture'
 page.wait_for_function('window.DC_APP || !document.getElementById("error").hidden',timeout=90000)
 print('boot',page.evaluate('({ok:!!window.DC_APP,error:document.getElementById("errorText").textContent})'),origin,errs,flush=True)
 page.evaluate('DC_APP.renderer.humanReady')
 page.evaluate('window.__render=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{}')
 page.click('#start');page.wait_for_function('DC_APP.mode==="creator"')
 page.wait_for_timeout(300);page.evaluate('__render(DC_APP.creator.preview)');page.screenshot(path=str(O/'creator-first.png'),timeout=60000)
 print('creator',page.evaluate('({mode:DC_APP.mode,gl:DC_APP.renderer.gl.getError(),frame:DC_APP.renderer.frame,look:DC_APP.renderer.appearancePixels.slice(0,4),rect:document.getElementById("world").getBoundingClientRect().toJSON()})'),errs,flush=True)
 print('fill name',flush=True)
 page.fill('#characterName','Noa');print('fill save name',flush=True);page.fill('#newSaveName','Ruta de Noa');print('preset',flush=True);page.locator('[data-preset="2"]').click();print('commit',flush=True);page.click('#commitCreator');print('committed',page.evaluate('({mode:DC_APP.mode,msg:document.getElementById("creatorMessage").textContent})'),flush=True);page.wait_for_function('DC_APP.mode==="play"',timeout=30000)
 page.click('#dismissTutorial');page.keyboard.press('Escape');page.click('#pauseSaves');page.evaluate('__render(DC_APP.sim)');page.screenshot(path=str(O/'library-first.png'),timeout=60000)
 print('library',page.evaluate('({mode:DC_APP.mode,slots:DC_APP.getStore().list().map(s=>({name:s.name,actor:s.data.identity.name})),gl:DC_APP.renderer.gl.getError()})'),errs,flush=True)
 (O/'smoke.json').write_text(json.dumps({'origin':origin,'errors':errs},indent=2));b.close()
