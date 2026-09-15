"""Reproducible animation-review video from actual renderer frames, NOT a FPS benchmark.
Simulation stepped at 1/60s, one actual GPU frame recorded per 1/24s; time resampled
for visual review. No frame interpolation or generative imagery.
"""
from pathlib import Path
import os,json,base64,io,subprocess
from PIL import Image,ImageDraw,ImageFont
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v08';F=O/'clip-frames';F.mkdir(exist_ok=True);os.environ.setdefault('DISPLAY',':99')
FIXTURE="""(()=>{let d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'balanced',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',12);small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',10)
errors=[];count=0;phases=set()
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':800,'height':550});p.on('pageerror',lambda e:errors.append(str(e)));p.set_content((R/'index.html').read_text().replace('<script>','<script>'+FIXTURE,1),timeout=60000);p.wait_for_function('!!window.DC_APP',timeout=60000);p.evaluate('DC_APP.loop=()=>{};');p.click('#start');p.click('#dismissTutorial');p.evaluate("DC_APP.setMode('photo');")
 for mode,frames in [('OCUPADO',132),('VACÍO',79)]:
  p.evaluate("""mode=>{const a=DC_APP,s=new DC.Simulation(a.world);a.sim=s;s.free=true;for(let i=0;i<s.cars.length;i++)Object.assign(s.cars[i],{x:300+i*6,z:0,parked:true,speed:0});s.peds.forEach(n=>n.hidden=true);const c=s.cars[1];Object.assign(c,{x:4,z:40,yaw:0,parked:mode!=='OCUPADO',owned:mode!=='OCUPADO',stolen:false,driver:mode==='OCUPADO'?DC.driverProfile(c):null,color:[.065,.17,.21]});Object.assign(s.player,{x:1.75,z:40.1,yaw:Math.PI/2,car:null});a.renderer.daylight=.7;a.renderer.rain=0;a.renderer.camera.eye=[-1.2,2.0,42.6];a.renderer.camera.target=[2.35,1.02,40];a.renderer.frame=0;}""",mode)
  elapsed=0
  for j in range(frames):
   if j==12:p.evaluate("DC_APP.sim.interact('car')")
   target=j/24
   steps=int(round(target*60))-int(round(elapsed*60));elapsed=target
   data=p.evaluate("""steps=>{const a=DC_APP;for(let k=0;k<steps;k++)a.sim.step(1/60,{});a.renderer.render(a.sim);return{png:a.renderer.canvas.toDataURL('image/png'),gl:a.renderer.gl.getError(),phase:a.sim.accessPlayerPose().accessPhase||'reposo'};}""",steps)
   if data['gl']:raise RuntimeError(data['gl'])
   phases.add(data['phase']);im=Image.open(io.BytesIO(base64.b64decode(data['png'].split(',')[1]))).convert('RGB');draw=ImageDraw.Draw(im);draw.rectangle([0,0,im.width,30],fill=(11,21,23));draw.text((12,8),'DISTRITO CERO 0.8   /   '+mode+'   /   '+data['phase'].upper(),font=font,fill=(231,236,233));draw.rectangle([0,im.height-22,im.width,im.height],fill=(11,21,23));draw.text((12,im.height-16),'Frames del motor · tiempo de animación controlado · no es una medición de FPS',font=small,fill=(191,202,198));im.save(F/f'{count:04}.png');count+=1
   if count%24==0:print('frames',count,flush=True)
 b.close()
out=Path('/mnt/data/distrito-cero-v0.8-acceso.mp4');subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','24','-i',str(F/'%04d.png'),'-c:v','libx264','-preset','medium','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(out)],check=True)
(O/'clip-report.json').write_text(json.dumps({'frames':count,'fps_export':24,'phases':sorted(phases),'errors':errors,'video':str(out),'source':'Actual WebGL pixels. Stepped simulation at 60Hz, sampled 24 fps offline for animation review. No interpolation, no AI render, not hardware FPS.'},indent=2));print('complete',count,errors,flush=True)
