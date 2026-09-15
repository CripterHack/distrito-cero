"""Actual game renderer, fixed inspection camera. No generated or retouched imagery."""
from pathlib import Path
import os,sys,json,hashlib
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];O=R/'qa/v015';O.mkdir(parents=True,exist_ok=True);name=sys.argv[1] if len(sys.argv)>1 else 'full';os.environ.setdefault('DISPLAY',':99')
source=Path(os.environ.get('DC_REVIEW_HTML',str(R/'index.html')));tag=os.environ.get('DC_REVIEW_TAG','')
FIX="""(()=>{const d=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',sound:false,rain:false,bloom:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>d.get(k)||null,setItem:(k,v)=>d.set(k,String(v)),removeItem:k=>d.delete(k)}});})();"""
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':1120,'height':800},device_scale_factor=float(os.environ.get('DC_REVIEW_DPR','1')));errors=[];p.on('pageerror',lambda e:errors.append(str(e)));p.set_content(source.read_text().replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady');p.evaluate('window.drawActual=DC_APP.renderer.render.bind(DC_APP.renderer);DC_APP.renderer.render=()=>{};DC_APP.loop=()=>{}');p.click('#start');p.wait_for_timeout(150)
 p.evaluate('q=>window.REVIEW_QUALITY=q',os.environ.get('DC_REVIEW_QUALITY','balanced'))
 p.evaluate('''()=>{const a=DC_APP,c=a.creator,s=c.preview,r=a.renderer;c.animate=false;c.elapsed=1;s.time=1;Object.assign(s.player,{walk:0,moveSpeed:0,yaw:0,grip:0,crouch:0});s.setIdentity('Alex',{...DC.Appearance.default(),skin:1,coat:1,build:0});r.quality=window.REVIEW_QUALITY||'balanced';r.daylight=.50;a.fitCreator();r.camera.eye=[.36,1.28,2.95];r.camera.target=[0,.98,0];}''')
 if name=='neck':p.evaluate('DC_APP.renderer.camera.eye=[.36,1.59,.92];DC_APP.renderer.camera.target=[0,1.48,0]')
 if name=='close':p.evaluate('DC_APP.renderer.camera.eye=[.22,1.645,.69];DC_APP.renderer.camera.target=[0,1.535,0]')
 if name=='profile':p.evaluate('DC_APP.renderer.camera.eye=[.82,1.595,.12];DC_APP.renderer.camera.target=[0,1.51,0]')
 if name=='back':p.evaluate('DC_APP.renderer.camera.eye=[-.38,1.62,-.80];DC_APP.renderer.camera.target=[0,1.50,0]')
 if name=='front':p.evaluate('DC_APP.renderer.camera.eye=[0,1.60,1.03];DC_APP.renderer.camera.target=[0,1.49,0]')
 if name=='portrait':p.evaluate('DC_APP.renderer.camera.eye=[.16,1.72,.61];DC_APP.renderer.camera.target=[0,1.645,0]')
 if name in ['hand','grip']:
  p.evaluate('''closed=>{const c=DC_APP.creator,s=c.preview,p=s.player;p.grip=closed?1:0;const q=DC.SkinRig.pose(p,s.time),h=DC.SkinRig.handPoint(q,p,'R');DC_APP.renderer.camera.eye=[h.x+.27,h.y-.038,h.z+.25];DC_APP.renderer.camera.target=[h.x-.004,h.y-.084,h.z+.004];}''',name=='grip')
 if name in ['lookleft','lookright','noddown','nodup','thick','thin']:
  p.evaluate('n=>{const c=DC_APP.creator,p=c.preview.player;DC_APP.renderer.camera.eye=[.28,1.65,.76];DC_APP.renderer.camera.target=[0,1.535,0];p.lookYaw=n==="lookleft"?-.72:n==="lookright"?.72:0;p.lookPitch=n==="noddown"?.22:n==="nodup"?-.22:0;if(n==="thin"||n==="thick"){c.preview.setIdentity("Alex",{...DC.Appearance.default(),coat:1,neck:n==="thin"?-1:1});}}',name)
 if name in ['lean-min','broad-max','broad-neutral']:
  p.evaluate('n=>{const c=DC_APP.creator;DC_APP.renderer.camera.eye=[.36,1.59,.92];DC_APP.renderer.camera.target=[0,1.48,0];c.preview.setIdentity("Alex",{...DC.Appearance.default(),skin:1,coat:1,build:n==="lean-min"?-1:1,neck:n==="lean-min"?-1:n==="broad-max"?1:0});}',name)
 if name=='run':p.evaluate('Object.assign(DC_APP.creator.preview.player,{walk:4.35,moveSpeed:6.2,sprintBlend:1,grip:undefined});DC_APP.renderer.camera.eye=[1.7,1.30,2.65]')
 if name=='crouch':p.evaluate('DC_APP.creator.preview.player.crouch=1;DC_APP.renderer.camera.eye=[1.2,1.12,2.45];DC_APP.renderer.camera.target=[0,.73,0]')
 p.evaluate('DC_APP.renderer.frame=0;drawActual(DC_APP.creator.preview)');report=p.evaluate('({gl:DC_APP.renderer.gl.getError(),visual:DC_APP.renderer.visualStats,cast:DC_APP.renderer.castStats})');report.update(errors=errors,sha256=hashlib.sha256(source.read_bytes()).hexdigest(),quality=os.environ.get('DC_REVIEW_QUALITY','balanced'),deviceScale=float(os.environ.get('DC_REVIEW_DPR','1')),camera=p.evaluate('({eye:DC_APP.renderer.camera.eye,target:DC_APP.renderer.camera.target})'));print(json.dumps(report),flush=True)
 p.locator('#creatorViewport').screenshot(path=str(O/('review-'+tag+name+'.png')),timeout=45000)
 (O/('review-'+tag+name+'.json')).write_text(json.dumps(report,indent=2));b.close()
