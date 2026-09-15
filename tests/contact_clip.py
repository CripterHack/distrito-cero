"""Actual WebGL inspection frames. Controlled animation clock, not a hardware benchmark."""
from pathlib import Path
import os,json,hashlib,subprocess
from playwright.sync_api import sync_playwright
R=Path(__file__).resolve().parents[1];Q=R/'qa/v019';O=Q/'contact-frames';O.mkdir(exist_ok=True)
HTML=(R/'index.html').read_text();errors=[];states=[]
FIX="""(()=>{const m=new Map([['distrito-cero:settings:v1',JSON.stringify({quality:'eco',rain:false,bloom:false,sound:false})]]);Object.defineProperty(window,'localStorage',{value:{getItem:k=>m.get(k)||null,setItem:(k,v)=>m.set(k,String(v)),removeItem:k=>m.delete(k)}});})();"""
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=False,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage']);p=b.new_page(viewport={'width':900,'height':620});p.on('pageerror',lambda e:errors.append(str(e)))
 p.set_content(HTML.replace('<script>','<script>'+FIX,1),timeout=90000);p.wait_for_function('!!window.DC_APP',timeout=90000);p.evaluate('DC_APP.renderer.humanReady');p.evaluate('window.requestAnimationFrame=()=>0');p.wait_for_timeout(100);p.click('#start');p.click('#commitCreator');p.click('#dismissTutorial')
 p.evaluate('''()=>{const a=DC_APP,s=a.sim;s.free=true;s.time=12;s.heat=s.wanted=0;s.peds.forEach(n=>n.hidden=true);s.cars.forEach((c,i)=>Object.assign(c,{x:-300,z:-250-i*5,parked:true,speed:0}));Object.assign(s.player,{x:4,z:36,yaw:0,y:0,car:null,walk:0,moveSpeed:0,health:100});s.equipWeapon('rifle');s.equipmentStep(.02,{});s.equipment.handling.ready=1;s.equipment.handling.kick=0;a.renderer.daylight=.63;a.renderer.rain=0;
 const style=document.createElement('style');style.textContent='#hud,#equipmentHUD,#weaponReticle,#touchControls,#toast,#chapter{display:none!important}';document.head.append(style);const label=document.createElement('div');label.id='inspection-label';label.style.cssText='position:fixed;z-index:900;left:24px;right:24px;bottom:20px;padding:14px 18px;background:rgba(8,18,22,.82);color:#edf5f4;font:15px system-ui;pointer-events:none';document.body.append(label);
 }''')
 for frame in range(120):
  state=p.evaluate('''frame=>{const a=DC_APP,s=a.sim;if(frame===40)s.reloadWeapon();for(let i=0;i<3;i++){const aim=frame>=14&&frame<104;const fire=frame===32&&i===0;s.step(1/60,{aim,fire,firePressed:fire,aimRay:{origin:[4,1.3,36],direction:[0,-.027,1]}});}a.renderer.equipmentView=false;a.renderer.camera.eye=[5.70,1.85,37.80];a.renderer.camera.target=[4.04,1.26,36.28];a.renderer.fovOverride=.57;a.renderer.render(s);const m=DC.Equipment.mount(s);document.getElementById('inspection-label').textContent='DISTRITO CERO v0.19 · '+m.phase+'  |  Motor WebGL real · tiempo de animación controlado';return{frame,phase:m.phase,magazine:m.magazine.offset,shots:s.equipment.shots,gl:a.renderer.gl.getError()};}''',frame)
  states.append(state);p.screenshot(path=str(O/f'{frame:04d}.png'),timeout=90000)
  if frame%20==0:print('frame',frame,state['phase'],flush=True)
 b.close()
assert not errors and all(s['gl']==0 for s in states)
assert any(s['magazine'][1]<-.15 for s in states) and max(s['shots'] for s in states)==1
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-framerate','20','-i',str(O/'%04d.png'),'-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-movflags','+faststart',str(Q/'contacto.mp4')],check=True)
(Q/'clip-report.json').write_text(json.dumps({'sha256':hashlib.sha256(HTML.encode()).hexdigest(),'frames':len(states),'playbackFPS':20,'duration':6,'errors':errors,'states':states,'note':'Prepared camera and initial state, production simulation and WebGL renderer. Controlled clock, not measured real-time performance.'},indent=2))
print('OK 120 frames, 6 s',flush=True)
