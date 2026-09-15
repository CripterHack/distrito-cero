"""Real renderer frames at controlled animation time, NOT a realtime FPS recording.
A studio/treadmill comparison of gait and anatomical hand articulation. No synthetic
frames, motion interpolation, image-generation or external assets are used.
"""
from pathlib import Path
import os,json,hashlib,time,io
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v013';F=O/'clip-frames';F.mkdir(exist_ok=True)
os.environ.setdefault('DISPLAY',':99');fps=20;per=60;errors=[];requests=[];checks=[]
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(FONT,15);small=ImageFont.truetype(FONT,11)
FIX="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
source=R/'index.html';started=time.time()
with sync_playwright()as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1120,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url)if r.url.startswith(('http:','https:'))else None)
 p.set_content(source.read_text().replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
 p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.loop=()=>{}');p.click('#start');p.wait_for_timeout(100)
 p.add_style_tag(content='.preview-label,.preview-controls,.preview-hint,.preview-overline{visibility:hidden!important}')
 p.evaluate('''()=>{const a=DC_APP,c=a.creator;c.animate=false;c.preview.setIdentity('Alex',{...DC.Appearance.default(),skin:1,coat:1});a.renderer.quality='balanced';a.fitCreator();window.clipPhase=0;}''')
 labels=['MARCHA · talón, apoyo y despegue','CARRERA · brazos y pelvis coordinados','MANOS · apertura y flexión contextual']
 samples=[]
 for phase in range(3):
  p.evaluate('DC_APP.renderer.motionTracker.clear();window.clipPhase=0')
  for i in range(per):
   t=i/fps
   out=p.evaluate('''({phase,t,dt})=>{const a=DC_APP,c=a.creator,s=c.preview,r=a.renderer,n=s.player;s.time=t+1;
    const speed=phase===0?1.4:phase===1?6.2:0;window.clipPhase+=DC.NaturalMotion.frequency(speed,phase===1?1:0)*dt;
    Object.assign(n,{x:0,z:0,y:0,yaw:0,vy:0,moveSpeed:speed,sprintBlend:phase===1?1:0,walk:clipPhase,crouch:0,seatBlend:0,seated:false,reach:0,handTargets:undefined,grip:phase===2?.13+.65*(.5-.5*Math.cos(t*Math.PI*2/3)):undefined});
    r.camera.eye=[1.15,1.25,2.58];r.camera.target=[0,.89,0];
    if(phase===2){const q=DC.SkinRig.pose(n,s.time),h=DC.SkinRig.handPoint(q,n,'R');r.camera.eye=[h.x+.25,h.y-.035,h.z+.24];r.camera.target=[h.x-.004,h.y-.083,h.z+.004];}
    r.frame=0;drawActual(s);return{gl:r.gl.getError(),pose:r.motionDebug?.gripStyle,feet:r.motionDebug?.feet,frame:r.frame};}''',{'phase':phase,'t':t,'dt':1/fps})
   if out['gl']:raise RuntimeError(out)
   frame=Image.open(io.BytesIO(p.locator('#creatorViewport').screenshot(timeout=30000))).convert('RGB')
   dr=ImageDraw.Draw(frame);dr.rectangle((0,0,frame.width,66),fill=(12,19,24));dr.text((20,12),'DISTRITO CERO  v0.13',fill=(220,233,220),font=font);dr.text((20,39),labels[phase],fill=(228,233,237),font=small)
   dr.rectangle((0,frame.height-33,frame.width,frame.height),fill=(12,19,24));dr.text((20,frame.height-23),'Motor real · tiempo de animación controlado · no es una medición de FPS',fill=(188,205,211),font=small)
   if frame.width%2 or frame.height%2:frame=frame.crop((0,0,frame.width//2*2,frame.height//2*2))
   frame.save(F/f'{phase*per+i:04d}.jpg',quality=92)
   if i in [0,30,59]:samples.append({'phase':phase,'sample':i,'gl':out['gl'],'feet':out['feet']})
  print('completed',labels[phase],flush=True)
 b.close()
report={'frames':per*3,'playbackFPS':fps,'seconds':per*3/fps,'wallSeconds':round(time.time()-started,2),'errors':errors,'requests':requests,'samples':samples,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Frames rendered by the production WebGL renderer. Deterministic treadmill studio; not uninterrupted gameplay, not a real-world FPS benchmark.'}
(O/'clip-report.json').write_text(json.dumps(report,indent=2));assert not errors and not requests;print('DONE',report['frames'],flush=True)
