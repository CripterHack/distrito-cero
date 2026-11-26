"""Compare a native vehicle door at fixed opening fractions in the production renderer."""
import argparse
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sys

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
from character_benchmark import FIX
from qa_support import launch_options

CASES = [('closed', 0, False), ('quarter', .25, False), ('half', .5, False),
         ('open', 1, False), ('tilted-damaged', 1, True)]
SETUP = """() => {
  DC_APP.stopFrame?.(); qaStopFrames(); window.requestAnimationFrame = () => 0;
  const r=DC_APP.renderer, sim=new DC.Simulation(new DC.World(1337));
  const car=sim.cars[0];
  sim.free=true; sim.time=1.25; sim.wanted=0;
  Object.assign(sim.player,{x:16,z:0,car:null}); sim.peds.forEach(n=>n.hidden=true);
  sim.cars=[car]; Object.assign(car,{x:0,z:0,yaw:0,speed:0,steerAngle:0,parked:true,driver:null,boarding:true,doorSide:-1});
  r.world=sim.world; r.previewStudio=true; r.daylight=.65; r.rain=0; r.bloom=0;
  r.quality='balanced'; r.resize(); r.fovOverride=.54;
  Object.assign(r.camera,{eye:[-5.4,2.2,3.1],target:[-.65,.86,-.1],initialized:true});
  const style=document.createElement('style');
  style.textContent='body>*:not(#world){visibility:hidden!important}#world{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}';
  document.head.append(style);
  window.doorScene={r,sim,car,live:JSON.stringify(DC_APP.sim.serialize()),storage:JSON.stringify([...qaCharacterStorage])};
  const g=r.gl, ext=g.getExtension('WEBGL_debug_renderer_info');
  return {renderer:ext?g.getParameter(ext.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER),
          size:[g.drawingBufferWidth,g.drawingBufferHeight],eye:r.camera.eye,target:r.camera.target,fov:r.fovOverride};
}"""
FRAME = """({fraction,tilt,hide}) => {
  const {r,sim,car,storage,live}=doorScene;
  Object.assign(car,{doorOpen:fraction,damage:{left:tilt?.65:0,right:0,front:0,rear:0},suspension:{pitch:tilt?.11:0,roll:tilt?-.08:0,kick:0}});
  // The intact drawing path produces the reference. A second draw omits just
  // the left handle to measure actual handle visibility in the same viewport.
  const add=r.add; let handle, panels=0;
  if(hide) r.add=function(list,mesh,x,y,z,sx,sy,sz,...rest) {
    if(mesh==='box' && x<0 && sx===.03 && sy===.036 && sz===.21) return;
    return add.call(this,list,mesh,x,y,z,sx,sy,sz,...rest);
  };
  try {r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);r.gl.finish();}
  finally {if(hide) delete r.add;}
  for(const [mesh,stream] of Object.entries(r.dynamic)){
    for(let i=0;i<stream.length;i+=16){
      const [x,y,z,,w,h,d]=stream.slice(i,i+7);
      if(mesh==='body' && w===.035 && h===.30 && d===1.7) panels++;
      if(mesh==='box' && x<0 && w===.03 && h===.036 && d===.21){
        const [nx,ny]=r.project(x,y,z);
        handle={world:[x,y,z],pixel:[(nx+1)*innerWidth/2,(1-ny)*innerHeight/2]};
      }
    }
  }
  if (!!handle===hide || panels!==2 || r.gl.getError() || r.gl.isContextLost() ||
      JSON.stringify([...qaCharacterStorage])!==storage || JSON.stringify(DC_APP.sim.serialize())!==live)
    throw Error('Native door draw or isolation check failed');
  return handle || null;
}"""


def rgb(data):
    return Image.open(BytesIO(data)).convert('RGB')


def compare(a,b):
    delta=ImageChops.difference(rgb(a),rgb(b))
    return {'pixels':sum(any(pixel) for pixel in delta.get_flattened_data()),'bounds':delta.getbbox()}


def run(browser, html, out):
    page=browser.new_page(viewport={'width':960,'height':600},device_scale_factor=1)
    errors=[]
    page.on('pageerror',lambda exc: errors.append(str(exc)))
    page.on('console',lambda msg: errors.append(msg.text) if msg.type=='error' else None)
    page.on('request',lambda req: errors.append(req.url) if req.url.startswith(('http:', 'https:')) else None)
    try:
        raw=html.read_bytes()
        page.set_content(raw.decode().replace('<script>','<script>'+FIX,1),timeout=120000)
        page.wait_for_function('!!window.DC_APP',timeout=120000)
        page.evaluate('DC_APP.renderer.humanReady')
        scene=page.evaluate(SETUP)
        frames={}
        for key, fraction, tilt in CASES:
            options={'fraction':fraction,'tilt':tilt}
            handle=page.evaluate(FRAME,{**options,'hide':False})
            shown=page.screenshot()
            page.evaluate(FRAME,{**options,'hide':True})
            hidden=page.screenshot()
            (out/(key+'.png')).write_bytes(shown)
            frames[key]={'open':fraction,'tiltedDamaged':tilt,'sha256':sha256(shown).hexdigest(),
                         'handle':handle,'visibleHandleDifference':compare(shown,hidden)}
        if errors:
            raise RuntimeError(str(errors))
        return {'htmlSha256':sha256(raw).hexdigest(),'scene':scene,'frames':frames}
    finally:
        page.close()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('before','after','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args()
    out=a.output.resolve()
    if not (ROOT/'artifacts') in out.parents:
        p.error('Use a fresh directory inside artifacts/')
    out.mkdir(parents=True,exist_ok=False)
    report={'producerSha256':sha256(Path(__file__).read_bytes()).hexdigest(),'seed':1337,
            'time':1.25,'viewport':[960,600],'limitations':'Prepared stationary car, isolated storage and software WebGL.'}
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        report['browser']=browser.version
        for label,html in [('before',a.before),('after',a.after)]:
            (out/label).mkdir()
            report[label]=run(browser,html,out/label)
    if report['before']['scene']!=report['after']['scene']:
        raise RuntimeError('Capture environment differs')
    deltas={}
    for key,_,_ in CASES:
        deltas[key]=compare(*[(out/l/(key+'.png')).read_bytes() for l in ('before','after')])
    report['comparison']=deltas
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if deltas['closed']['pixels'] or not deltas['open']['pixels'] or not report['after']['frames']['open']['visibleHandleDifference']['pixels']:
        raise RuntimeError('Closed control, open difference or visible open handle failed')


if __name__=='__main__':
    main()
