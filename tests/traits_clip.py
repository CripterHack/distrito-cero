"""Capture cervical motion from the production renderer at controlled animation time.
The output is a review film, not live performance, mocap or generated imagery.
"""
from pathlib import Path
import os,json,hashlib,time,io
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v016';F=O/'clip-frames';F.mkdir(exist_ok=True)
os.environ.setdefault('DISPLAY',':99');fps=20;per=60;errors=[];requests=[]
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',11)
FIX="""(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
source=R/'index.html';started=time.time();samples=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
 p=b.new_page(viewport={'width':1120,'height':800});p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:requests.append(r.url) if r.url.startswith(('http:','https:')) else None)
 p.set_content(source.read_text().replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady')
 p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.loop=()=>{}');p.click('#start');p.wait_for_timeout(100)
 p.add_style_tag(content='.preview-label,.preview-controls,.preview-hint,.preview-overline{visibility:hidden!important}')
 p.evaluate("""()=>{const a=DC_APP,c=a.creator;c.animate=false;c.preview.setIdentity('Alex',{...DC.Appearance.default(),skin:1,coat:1});a.renderer.quality='balanced';a.renderer.daylight=.5;a.fitCreator();}""")
 labels=['GIRO · cuello ajustado y flequillo lateral','FLEXIÓN · recogido y anclaje cervical']
 for phase in range(2):
  for i in range(per):
   t=i/fps
   out=p.evaluate('''({phase,t})=>{const a=DC_APP,c=a.creator,s=c.preview,r=a.renderer,n=s.player;s.time=t+1;s.appearance.hairStyle=phase===0?7:9;
    Object.assign(n,{x:0,z:0,y:0,yaw:0,vy:0,moveSpeed:0,sprintBlend:0,walk:0,crouch:0,seatBlend:0,seated:false,reach:0,handTargets:undefined,grip:0,lookYaw:phase===0?Math.sin(t*Math.PI/2)*.72:0,lookPitch:phase===1?Math.sin(t*Math.PI/2)*.22:0,lookRoll:0});
    r.camera.eye=phase===0?[.18,1.645,.74]:[.66,1.645,.40];r.camera.target=[0,1.51,0];
    const pose=DC.SkinRig.pose({...n,neckDrop:DC.CharacterFit.drop(0)},s.time);r.frame=0;drawActual(s);
    return {gl:r.gl.getError(),cervical:pose.cervical,eyes:r.camera.eye,frame:r.frame};}''',{'phase':phase,'t':t})
   if out['gl']:raise RuntimeError(out)
   frame=Image.open(io.BytesIO(p.locator('#creatorViewport').screenshot(timeout=30000))).convert('RGB')
   d=ImageDraw.Draw(frame);d.rectangle((0,0,frame.width,66),fill=(12,19,24));d.text((20,12),'DISTRITO CERO  v0.16',fill=(220,233,220),font=font);d.text((20,39),labels[phase],fill=(228,233,237),font=small)
   d.rectangle((0,frame.height-33,frame.width,frame.height),fill=(12,19,24));d.text((12,frame.height-23),'Motor real · tiempo controlado · no es una medición de FPS',fill=(188,205,211),font=small)
   if frame.width%2 or frame.height%2:frame=frame.crop((0,0,frame.width//2*2,frame.height//2*2))
   frame.save(F/f'{phase*per+i:04d}.jpg',quality=93)
   if i in [0,15,30,45,59]:samples.append({'phase':phase,'sample':i,**out})
  print('COMPLETE',labels[phase],flush=True)
 b.close()
report={'frames':per*2,'playbackFPS':fps,'seconds':per*2/fps,'wallSeconds':round(time.time()-started,2),'errors':errors,'requests':requests,'samples':samples,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'scope':'Actual WebGL frames, prepared studio cameras and explicitly sampled animation time. Not realtime performance or motion capture.'}
(O/'clip-report.json').write_text(json.dumps(report,indent=2));assert not errors and not requests;print('DONE',report['frames'],flush=True)
