"""Optional capability check: unmocked file:// storage across Chromium restarts.
Failures to navigate are recorded as unavailable coverage, not as successful persistence.
Uses an isolated temporary browser profile, never the user's browser data.
"""
from pathlib import Path
import tempfile,os,json,time,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v012';os.environ.setdefault('DISPLAY',':99')
report={'available':False,'passed':0,'checks':[],'sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest()}
with tempfile.TemporaryDirectory(prefix='dc012-native-') as profile:
 try:
  with sync_playwright() as pw:
   args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']
   c=pw.chromium.launch_persistent_context(profile,executable_path='/usr/bin/chromium',headless=False,args=args,viewport={'width':640,'height':480});p=c.pages[0]
   p.add_init_script("try{localStorage.setItem('distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false}));}catch(e){}")
   p.goto((R/'index.html').as_uri(),timeout=30000);p.wait_for_function('!!window.DC_APP',timeout=60000)
   p.evaluate('window.haltRender=DC_APP.renderer.render;DC_APP.renderer.render=()=>{}');p.click('#start');p.fill('#characterName','Río');p.fill('#newSaveName','Primera prueba nativa');p.click('#commitCreator');p.wait_for_function('DC_APP.mode==="play"');p.click('#dismissTutorial');p.keyboard.press('Escape')
   p.evaluate('DC_APP.sim.cash=1937;DC_APP.save(false);const s=DC_APP.sim.serialize();s.identity.name="Luz";s.cash=2481;DC_APP.getStore().create("Segunda prueba nativa",s,{activate:false});')
   before=p.evaluate('DC_APP.getStore().list().map(s=>[s.id,s.name,s.data.identity.name,s.data.cash])');c.close()
   c=pw.chromium.launch_persistent_context(profile,executable_path='/usr/bin/chromium',headless=False,args=args,viewport={'width':640,'height':480});p=c.pages[0];p.goto((R/'index.html').as_uri(),timeout=30000);p.wait_for_function('!!window.DC_APP',timeout=60000)
   after=p.evaluate('DC_APP.getStore().list().map(s=>[s.id,s.name,s.data.identity.name,s.data.cash])');p.click('#continue');state=p.evaluate('({name:DC_APP.sim.characterName,cash:DC_APP.sim.cash})')
   report.update(available=True,checks=[{'name':'Two named slots survive browser process restart on identical file URL','pass':before==after and len(after)==2},{'name':'Continue restores saved character and money from native localStorage','pass':state=={'name':'Río','cash':1937}}]);report['passed']=sum(x['pass']for x in report['checks']);c.close()
 except Exception as e:report['limitation']=str(e)[:2000]
(O/'native-storage.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps(report,ensure_ascii=False),flush=True)
