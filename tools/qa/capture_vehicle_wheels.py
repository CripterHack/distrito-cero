"""Compare the near wheel assembly and its distance transitions in native WebGL."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from playwright.sync_api import sync_playwright
from capture_vehicle_door import FIX, ROOT, SETUP, compare, launch_options

# The distant control intentionally keeps the camera close, to isolate its mesh.
CASES = [
    ('car', [-5.8, 2.18, 4.3], [0, .72, 0], .48, .0, .0, False, 2),
    ('front-rest', [-2.82, .97, 2.42], [-.94, .405, 1.36], .56, 0, 0, False, 2),
    ('front-left', [-2.82, .97, 2.42], [-.94, .405, 1.36], .56, -.42, .7, False, 2),
    ('front-right', [-2.82, .97, 2.42], [-.94, .405, 1.36], .56, .42, 1.35, False, 2),
    ('rear-tilted', [2.68, 1.04, -2.51], [.94, .405, -1.39], .56, .42, 1.35, True, 2),
    ('mid', [-5.8, 2.18, 4.3], [0, .72, 0], .48, -.42, 1.35, False, 28),
    ('far', [-5.8, 2.18, 4.3], [0, .72, 0], .48, -.42, 1.35, False, 68),
]

FRAME = """({eye,target,fov,steer,spin,tilt,distance,hide}) => {
 const {r,sim,car,live,storage}=doorScene;
 Object.assign(sim.player,{x:distance,z:0});
 Object.assign(car,{wheel:spin,steerAngle:steer,doorOpen:0,suspension:{pitch:tilt?.09:0,roll:tilt?-.065:0,kick:0}});
 Object.assign(r.camera,{eye,target,initialized:true});r.fovOverride=fov;
 const original=r.renderCar, add=r.add, pieces={};
 r.renderCar=function(candidate){
  this.add=function(list,key,x,y,z,w,h,d,...rest){
   const wheel=['wheel','rim','tire','wheelBrake','wheelAlloy','wheelCaliper'].includes(key)||
    (key==='body' && w===.030 && h===.27 && d===.041);
   if(wheel){
    pieces[key]=(pieces[key]||0)+1;
    if(hide)return;
   }
   return add.call(this,list,key,x,y,z,w,h,d,...rest);
  };
  try{return original.call(this,candidate);}finally{delete this.add;}
 };
 try{r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);r.gl.finish();}
 finally{delete r.renderCar;}
 if(r.gl.getError()||r.gl.isContextLost()||JSON.stringify(DC_APP.sim.serialize())!==live||
    JSON.stringify([...qaCharacterStorage])!==storage)throw Error('Renderer or isolated state failed');
 const triangleInstances=Object.entries(pieces).reduce((n,[key,count])=>n+count*r.meshes[key].count/3,0);
 return {pieces,triangleInstances};
}"""


DRIVING_FRAME = """({start,input}) => {
 const {r,sim,car,live,storage}=doorScene;
 if(start) {
  Object.assign(car,{x:0,z:0,yaw:0,wheel:0,speed:0,steerAngle:0,parked:false,boarding:false,
                     suspension:{pitch:0,roll:0,kick:0}});
  Object.assign(sim.player,{x:0,z:0,car:0});
 }
 for(let i=0;i<4;i++)sim.step(1/60,input);
 const at=(x,y,z)=>[car.x+x*Math.cos(car.yaw)+z*Math.sin(car.yaw),y,car.z-x*Math.sin(car.yaw)+z*Math.cos(car.yaw)];
 Object.assign(r.camera,{eye:at(-2.82,.97,2.42),target:at(-.94,.405,1.36),initialized:true});
 r.fovOverride=.56;r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);r.gl.finish();
 if(r.gl.getError()||r.gl.isContextLost()||JSON.stringify(DC_APP.sim.serialize())!==live||
    JSON.stringify([...qaCharacterStorage])!==storage)throw Error('Drive capture or isolation failed');
 return {x:car.x,z:car.z,speed:car.speed,spin:car.wheel,steer:car.steerAngle};
}"""

def capture(browser, html, destination):
    destination.mkdir()
    page = browser.new_page(viewport={'width': 800, 'height': 500}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda exc: errors.append(str(exc)))
    page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
    page.on('request', lambda req: errors.append(req.url) if req.url.startswith(('http:', 'https:')) else None)
    try:
        raw = html.read_bytes()
        page.set_content(raw.decode().replace('<script>', '<script>'+FIX, 1), timeout=120000)
        page.wait_for_function('!!window.DC_APP', timeout=120000)
        page.evaluate('DC_APP.renderer.humanReady')
        scene = page.evaluate(SETUP)
        frames = {}
        for name, eye, target, fov, steer, spin, tilt, distance in CASES:
            options = dict(eye=eye, target=target, fov=fov, steer=steer, spin=spin,
                           tilt=tilt, distance=distance)
            parts = page.evaluate(FRAME, {**options, 'hide':False})
            image = page.screenshot()
            (destination/(name+'.png')).write_bytes(image)
            frames[name] = dict(pose=options, **parts, sha256=sha256(image).hexdigest())
            if name in ('front-right', 'rear-tilted', 'car'):
                page.evaluate(FRAME, {**options, 'hide':True})
                visible = compare(image, page.screenshot())
                if not visible['pixels']:
                    raise ValueError('The wheel assembly must be visible in '+name)
                frames[name]['visibleAssembly'] = visible
        driving = []
        for sample in range(8):
            # Steer into, then out of, a turn while accelerating on a real sim tick.
            control = {'throttle': 1, 'steer': 1 if sample<4 else -1}
            pose = page.evaluate(DRIVING_FRAME, {'start': sample==0, 'input': control})
            image = page.screenshot()
            (destination/f'drive-{sample:02d}.png').write_bytes(image)
            driving.append(dict(input=control, **pose, sha256=sha256(image).hexdigest()))
        if not (driving[-1]['spin']>driving[0]['spin'] and driving[3]['steer']<0<driving[-1]['steer']):
            raise ValueError('The native driving sequence did not roll and steer both ways')
        if errors:
            raise RuntimeError(errors)
        return dict(html=sha256(raw).hexdigest(), scene=scene, frames=frames, driving=driving)
    finally:
        page.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ('before','after','output'):
        parser.add_argument('--'+arg,type=Path,required=True)
    args = parser.parse_args()
    out = args.output.resolve()
    if ROOT/'artifacts' not in out.parents:
        parser.error('Choose a fresh directory under artifacts/')
    out.mkdir(parents=True,exist_ok=False)
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        a = capture(browser,args.before,out/'before')
        b = capture(browser,args.after,out/'after')
        assert a['scene']==b['scene']
        for before,after in zip(a['driving'],b['driving'],strict=True):
            assert all(value==after[key] for key,value in before.items() if key!='sha256')
        deltas = {case[0]:compare(*[(out/v/(case[0]+'.png')).read_bytes() for v in ('before','after')])
                  for case in CASES}
        assert deltas['far']['pixels']==0 and all(deltas[k]['pixels'] for k in deltas if k!='far')
        assert b['frames']['front-rest']['pieces']['wheelCaliper']==4
        assert 'wheelCaliper' not in b['frames']['mid']['pieces']
        report = dict(browser=browser.version,before=a,after=b,comparison=deltas,
                      producerSha256=sha256(Path(__file__).read_bytes()).hexdigest())
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps(deltas, indent=2))


if __name__=='__main__':
    main()
