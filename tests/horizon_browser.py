"""Current v0.7 integration with actual WebGL frames and DOM keyboard/touch.
Network navigation is blocked by lab policy. Inject HTML with isolated storage.
Representative scenes freeze render/camera between explicit WebGL captures;
a separate continuous test exercises the untouched render loop.
"""
from pathlib import Path
import os,json,time,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'qa/v07';OUT.mkdir(exist_ok=True)
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
checks=[];errors=[];requests=[]
def check(name,value):
 checks.append({'name':name,'pass':bool(value)});print(time.strftime('%H:%M:%S')+' '+('PASS ' if value else 'FAIL ')+name,flush=True);assert value,name

def load(browser,w,h,touch=False):
 ctx=browser.new_context(viewport={'width':w,'height':h},has_touch=touch,is_mobile=touch,device_scale_factor=1)
 page=ctx.new_page();page.set_default_timeout(30000);page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None);page.on('request',lambda r:requests.append(r.url))
 page.set_content((ROOT/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000)
 page.wait_for_function('!!window.DC_APP||!document.getElementById("error").hidden',timeout=60000)
 check('WebGL boot '+str((w,h)),page.evaluate('!!window.DC_APP'))
 page.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};window.cameraActual=DC_APP.renderer.updateCamera.bind(DC_APP.renderer);DC_APP.renderer.updateCamera=()=>{};')
 page.click('#start');page.click('#dismissTutorial');page.evaluate("document.getElementById('chapter').style.display='none';DC_APP.sim.free=true;DC_APP.sim.cars.forEach(c=>{c.speed=0;c.parked=true});")
 return ctx,page

def advance(p,seconds):
 p.evaluate('''sec=>{let a=DC_APP;for(let i=0;i<Math.ceil(sec*60);i++)a.sim.step(1/60,a.input());a.processEvents();a.updateUI(performance.now());}''',seconds)

def frame(p,name):
 p.evaluate('''()=>{const a=DC_APP;a.renderer.syncSectors(25);a.renderer.quality='eco';a.renderer.resize();a.renderer.frame=0;drawActual(a.sim);}''')
 check('Finite GL frame '+name,p.evaluate('DC_APP.renderer.gl.getError()===0'))
 if os.environ.get('CAPTURES','0')=='1': p.screenshot(path=str(OUT/name))

def reachable(p,sel):
 p.locator(sel).scroll_into_view_if_needed();b=p.locator(sel).bounding_box();check('Visible '+sel,bool(b));w,h=p.viewport_size.values();check('Inside viewport '+sel,b['x']>=0 and b['y']>=0 and b['x']+b['width']<=w+1 and b['y']+b['height']<=h+1)
 check('Receives pointer '+sel,p.evaluate('''q=>{const el=document.querySelector(q.sel),top=document.elementFromPoint(q.x,q.y);return top===el||el.contains(top)}''',dict(sel=sel,x=b['x']+b['width']/2,y=b['y']+b['height']/2)))

os.environ.setdefault('DISPLAY',':99')
try:
 with sync_playwright() as pw:
  b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
  ctx,p=load(b,900,640)
  check('24-bit depth prevents road/terrain precision conflict',p.evaluate('(()=>{const r=DC_APP.renderer,g=r.gl;g.bindRenderbuffer(g.RENDERBUFFER,r.scene.db);return g.getRenderbufferParameter(g.RENDERBUFFER,g.RENDERBUFFER_INTERNAL_FORMAT)===g.DEPTH_COMPONENT24;})()'))
  check('Initial bounded 25 sectors',p.evaluate('DC_APP.renderer.streamStats.loaded===25&&DC_APP.world.activeChunks.length===25'))
  check('Original 392 city buildings and 555 props preserved',p.evaluate('DC_APP.world.home.buildings.length===392&&DC_APP.sim.homeProps.length===555'))
  p.keyboard.press('m');check('M opens atlas',p.evaluate("DC_APP.mode==='map'"));reachable(p,'#regionalView');reachable(p,'[data-destination="future"]');p.screenshot(path=str(OUT/'01-atlas.png'))
  check('All five discovery destinations available',p.locator('[data-destination]').count()==5)
  p.click('#localView');check('Street-level map selected',p.evaluate('DC_APP.atlasRange===900'))
  p.click('#zoomOut');check('Map zoom changes actual scale',p.evaluate('DC_APP.atlasRange>900'))
  p.click('#regionalView');
  # Genuine atlas click sets a distant pin instead of clamping to the old city.
  rect=p.locator('#citymap').bounding_box();p.mouse.click(rect['x']+rect['width']*.2,rect['y']+rect['height']*.5)
  check('Atlas pin extends outside old 420m boundary',p.evaluate('Math.abs(DC_APP.sim.pin.x)>420'))
  check('Pin enables explicit visit',not p.locator('#travelPin').is_disabled());p.click('#clearPin');check('Clear pin remains functional',p.evaluate('DC_APP.sim.pin===null'))
  p.click('[data-destination="future"]');check('Travel uses real simulation API',p.evaluate('DC_APP.sim.player.x>1900&&DC_APP.mode==="play"'))
  check('Future region has correct zoning',p.evaluate('DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z).type==="future"'))
  snapshots=[]
  for dest in ['future','retro','village','farmland','home']:
   if p.evaluate('DC_APP.mode')!='map':p.keyboard.press('m')
   p.click('[data-destination="'+dest+'"]');check('Arrive '+dest,p.evaluate('DC_APP.mode==="play"'))
   p.evaluate('''()=>{const a=DC_APP,p=a.sim.player;a.setMode('photo');a.renderer.camera.eye=[p.x-6,12,p.z-30];a.renderer.camera.target=[p.x+10,9,p.z+36];a.renderer.daylight=.78;a.renderer.rain=0;}''')
   name='02-'+dest+'.png';frame(p,name);snapshots.append(p.evaluate('DC_APP.world.region(DC_APP.sim.player.x,DC_APP.sim.player.z).type'))
   check('GPU budget bounded '+dest,p.evaluate('DC_APP.renderer.streamStats.loaded<=25&&DC_APP.renderer.streamStats.buffers<=125'))
   check('Camera-relative origin follows '+dest,p.evaluate('Math.abs(DC_APP.renderer.camera.target[0]-DC_APP.renderer.renderOrigin[0])<336.01'))
   p.keyboard.press('p')
  check('Five distinct authoritative environment types',len(set(snapshots))==5)
  # Contact, destruction and migration on the expanded world.
  check('Remote destruction persists across streaming and save',p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.travel(2016,0);const lamp=s.dynamics.props.find(p=>p.id.startsWith('wl:'));window.testLamp=lamp.id;s.dynamics.impactProp(lamp,110,1,0);const data=s.serialize();s.travel(-2016,0);const fresh=new DC.Simulation(a.world);const ok=fresh.restore(data);a.sim=fresh;return ok&&fresh.dynamics.byId.get(testLamp)?.broken;}'''))
  p.evaluate("DC_APP.sim.wanted=2;DC_APP.sim.heat=60;DC_APP.setMode('play');");p.keyboard.press('m');x=p.evaluate('DC_APP.sim.player.x');p.click('[data-destination="home"]')
  check('Wanted player cannot teleport out of pursuit',p.evaluate('DC_APP.sim.player.x')==x and p.evaluate('DC_APP.mode==="map"'))
  p.evaluate('DC_APP.sim.wanted=0;DC_APP.sim.heat=0;');p.click('[data-destination="home"]')
  p.evaluate("const s=DC_APP.sim;s.player.car=null;Object.assign(s.player,{x:400,z:4,yaw:Math.PI/2,vx:0,vz:0});DC_APP.renderer.camera.yaw=Math.PI/2;")
  p.keyboard.down('w');p.keyboard.down('Shift');advance(p,4.5);p.keyboard.up('Shift');p.keyboard.up('w');check('Real keyboard crosses old city boundary',p.evaluate('DC_APP.sim.player.x>420'))
  check('Streaming keeps input and stride finite',p.evaluate('Number.isFinite(DC_APP.sim.player.x)&&DC_APP.sim.player.walk>0'))
  # Distant world precision, not a claim of an actually infinite number of unique places.
  check('Travel to 20 million metres succeeds',p.evaluate('DC_APP.sim.travel(20000004,-20000004)'))
  p.evaluate('''()=>{const a=DC_APP,p=a.sim.player;a.setMode('photo');a.renderer.camera.eye=[p.x+24,10,p.z-25];a.renderer.camera.target=[p.x,3,p.z+25];}''');frame(p,'03-distant-origin.png')
  check('Very distant projection remains finite',p.evaluate('''()=>{const a=DC_APP,p=a.sim.player,q=a.renderer.project(p.x,p.y,p.z);return q.every(Number.isFinite)&&Math.abs(a.renderer.renderOrigin[0])>1e7;}'''))
  p.keyboard.press('p');p.keyboard.press('m');p.click('summary');p.fill('#worldSeed','2026');p.once('dialog',lambda d:d.accept());p.click('#applySeed')
  check('Explicit new-seed action rebuilds authoritative world',p.evaluate('DC_APP.world.seed===2026&&DC_APP.sim.player.x===5'))
  check('Seed included in exportable save',p.evaluate('DC_APP.sim.serialize().horizon.seed===2026'))
  p.keyboard.press('Escape');p.locator('#daylight').fill('15');check('Daylight slider reaches renderer',p.evaluate('Math.abs(DC_APP.renderer.daylight-.15)<.001'));p.click('#resume')
  ctx.close()
  for w,h in [(390,844),(844,390)]:
   ctx,p=load(b,w,h,True);p.locator('#mapButton').tap();check('Touch opens atlas '+str(w),p.evaluate('DC_APP.mode==="map"'))
   for sel in ['#closeMap','#regionalView','[data-destination="farmland"]','#nextRegion'] :reachable(p,sel)
   p.locator('[data-destination="farmland"]').tap();check('Touch destination usable '+str(w),p.evaluate('DC_APP.mode==="play"&&Math.abs(DC_APP.sim.player.x)>500'))
   p.locator('#mapButton').tap();p.locator('#closeMap').scroll_into_view_if_needed();p.screenshot(path=str(OUT/('04-mobile-'+str(w)+'.png')));p.locator('#closeMap').tap();check('Touch exit restores play '+str(w),p.evaluate('DC_APP.mode==="play"'));ctx.close()
  check('No JavaScript / GL console errors',not errors);check('No network requests from game',not requests);b.close()
finally:
 report={'checks':checks,'passed':sum(c['pass']for c in checks),'failed':sum(not c['pass']for c in checks),'errors':errors,'requests':requests,'mode':'Injected HTML, isolated memory storage, real WebGL keyframes, native keyboard/touch, simulated viewports. Not native device benchmarks.'};(OUT/'horizon-browser.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:report[k]for k in ['passed','failed','errors']}),flush=True)
