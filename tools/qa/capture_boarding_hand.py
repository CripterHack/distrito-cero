"""Render the driver opening a stationary sedan and measure the rendered palm and handle."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
from character_benchmark import FIX
from qa_support import launch_options

SETUP = """() => {
  DC_APP.stopFrame?.();
  qaStopFrames();
  window.requestAnimationFrame = () => 0;
  const sim = new DC.Simulation(new DC.World(1337));
  sim.free = true;
  sim.time = 1.25;
  sim.peds.forEach(p => p.hidden=true);
  sim.cars.forEach((v,i) => Object.assign(v,{x:300+6*i,z:0,speed:0,parked:true}));
  const car = sim.cars[1];
  Object.assign(car,{x:4,z:40,yaw:0,speed:0,parked:true,owned:true,stolen:false,driver:null});
  Object.assign(sim.player,{x:1.75,z:40.1,yaw:Math.PI/2,car:null});
  sim.startAccess();
  if (sim.access?.kind !== 'enter' || sim.access.c !== car) throw Error('Failed to start empty driver access');
  const r = DC_APP.renderer;
  r.world = sim.world;
  r.previewStudio = false;
  r.rain = r.bloom = 0;
  r.quality = 'balanced';
  r.fovOverride = .46;
  Object.assign(r.camera, {eye:[-.6,2.3,43.7], target:[2.46,1.04,39.9], initialized:true});
  r.resetSectors();
  r.syncSectors(1000);
  const style = document.createElement('style');
  style.textContent = 'body>*:not(#world){visibility:hidden!important}#world{position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}';
  document.head.append(style);
  r.resize();
  window.boardingFixture = {r,sim,car,storage:JSON.stringify([...qaCharacterStorage]),live:JSON.stringify(DC_APP.sim.serialize())};
  const gl=r.gl, extension=gl.getExtension('WEBGL_debug_renderer_info');
  return {eye:r.camera.eye, target:r.camera.target, fov:r.fovOverride,
          nativeBuffer:[gl.drawingBufferWidth,gl.drawingBufferHeight],
          renderer:gl.getParameter(extension?.UNMASKED_RENDERER_WEBGL || gl.RENDERER)};
}"""

FRAME = """fraction => {
  const {r,sim,car,storage,live} = boardingFixture;
  // Advance the production access controller; the mesh and skin still get their state from render(sim).
  for (let ticks=0; car.doorOpen < fraction; ++ticks) {
    if (!sim.access || ticks>6000) throw Error('Door did not reach capture phase');
    sim.step(1/600,{});
  }
  if (car.doorOpen-fraction>.02 || sim.player.car !== null) throw Error('Missed opening or premature seat transfer');
  r.frame=0;
  r.lightTime=-1;
  r.render(sim);
  r.gl.finish();
  // Instance records carry the actual world transform of the near body. Slot zero is the player.
  const skin = r.lodParts[0].find(p => p.name==='skin');
  const stride=16, stream=r.dynamic[skin.key], playerTransforms=[];
  for (let i=0; i<stream.length; i+=stride) {
    if (stream[i+15]===200) playerTransforms.push(stream.slice(i,i+7));
  }
  if (playerTransforms.length!==1) throw Error('Expected one rendered player in the skin batch');
  const [x,rootY,z,yaw,scale] = playerTransforms[0];
  const palm = DC.SkinRig.palmPoint({matrices:r.heroPalette,rootY,scale},{x,z,yaw},'R');
  const handles=[], panel=r.dynamic.box;
  for (let i=0; i<panel.length; i+=stride) {
    const [px,py,pz,yaw,w,h,d] = panel.slice(i,i+7);
    if (w===.03 && h===.036 && d===.21 && px<car.x && Math.abs(pz-car.z)<2)
      handles.push({center:[px,py,pz],yaw,roll:panel[i+13],halfWidth:w/2});
  }
  if (handles.length!==1) throw Error('Expected one driver-side handle in the draw stream');
  const {center:handle,yaw:panelYaw,roll,halfWidth}=handles[0], palmWorld=[palm.x,palm.y,palm.z];
  // Outer face center of the drawn handle. Pitch leaves the local X axis invariant.
  const normal=[-Math.cos(panelYaw)*Math.cos(roll),-Math.sin(roll),Math.sin(panelYaw)*Math.cos(roll)];
  const outside=handle.map((v,i)=>v+halfWidth*normal[i]);
  const pixel = world => {
    const [nx,ny,nz,w]=r.project(...world);
    if (w<=0 || Math.abs(nx)>=1 || Math.abs(ny)>=1 || Math.abs(nz)>=1) throw Error('Contact outside camera');
    return [(1+nx)*innerWidth/2,(1-ny)*innerHeight/2];
  };
  if (r.gl.isContextLost() || r.gl.getError() || storage!==JSON.stringify([...qaCharacterStorage]) ||
      live!==JSON.stringify(DC_APP.sim.serialize())) throw Error('Draw or isolation failed');
  return {open:car.doorOpen, elapsed:sim.access.elapsed, phase:sim.accessPlayerPose().accessPhase,
          palmWorld, handleWorld:handle, palmPixel:pixel(palmWorld), handlePixel:pixel(handle),
          palmToHandleCenterM:Math.hypot(...palmWorld.map((v,i)=>v-handle[i])),
          outerFaceWorld:outside, palmToOuterFaceCenterM:Math.hypot(...palmWorld.map((v,i)=>v-outside[i]))};
}"""


MOTION_FRAME = """first => {
  const {r,sim,car,live,storage} = boardingFixture;
  if (!first) for (let i=0;i<3;i++) sim.step(1/60,{});
  r.render(sim);
  r.gl.finish();
  if (r.gl.isContextLost() || r.gl.getError() || live!==JSON.stringify(DC_APP.sim.serialize()) ||
      storage!==JSON.stringify([...qaCharacterStorage])) throw Error('Motion capture failed');
  return {time:sim.time,phase:sim.access ? sim.accessPlayerPose().accessPhase : 'complete',open:car.doorOpen,
          seated:sim.player.car!==null};
}"""


def record_motion(page, out):
    frames = []
    # Each displayed interval represents three actual 60 Hz gameplay updates.
    with subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-n','-f','image2pipe','-framerate','20',
                           '-vcodec','png','-i','pipe:0','-c:v','libx264','-pix_fmt','yuv420p','-crf','16',
                           '-movflags','+faststart',str(out / 'motion.mp4')], stdin=subprocess.PIPE) as encoder:
        for i in range(100):
            state = page.evaluate(MOTION_FRAME, i==0)
            encoder.stdin.write(page.screenshot())
            frames.append(state)
            if state['seated'] and state['phase']=='complete':
                break
        encoder.stdin.close()
        if encoder.wait():
            raise RuntimeError('Motion encoder failed')
    if frames[-1]['phase']!='complete':
        raise RuntimeError('Driver did not finish entering the sedan')
    return {'fps':20, 'videoSha256':sha256((out / 'motion.mp4').read_bytes()).hexdigest(), 'motionFrames':frames}


def capture_samples(page, out):
    frames = {}
    for percent in (25, 50, 75):
        info = page.evaluate(FRAME, percent / 100)
        png = page.screenshot()
        name = f'open-{percent}.png'
        (out / name).write_bytes(png)
        frames[name] = {**info, 'imageSha256': sha256(png).hexdigest()}
    return {'frames':frames}


def capture(browser, html, out, motion):
    page = browser.new_page(viewport={'width': 960, 'height': 600}, device_scale_factor=1)
    page.set_default_timeout(120000)
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
        result = record_motion(page, out) if motion else capture_samples(page, out)
        if errors:
            raise RuntimeError(str(errors))
        return {'htmlSha256': sha256(raw).hexdigest(), 'scene': scene, **result}
    finally:
        page.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--motion', action='store_true', help='Encode the complete boarding action as a 20 fps MP4 (requires ffmpeg).')
    parser.add_argument('--require-contact', action='store_true', help='Check the corrected palm stays within 6 mm of the outer face at all three openings.')
    args = parser.parse_args()
    if args.require_contact and args.motion:
        parser.error('Contact measurement uses the three individual frames; run --motion separately.')
    out = args.output.resolve()
    if (ROOT / 'artifacts') not in out.parents:
        parser.error('Use a fresh directory under artifacts/')
    out.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as playwright, playwright.chromium.launch(**launch_options()) as browser:
        report = capture(browser, args.html, out, args.motion)
        report.update(browser=browser.version, producerSha256=sha256(Path(__file__).read_bytes()).hexdigest())
        (out / 'report.json').write_text(json.dumps(report, indent=2)+'\n')
        if args.require_contact and any(f['palmToOuterFaceCenterM'] >= .006 for f in report['frames'].values()):
            raise RuntimeError('Rendered right palm missed the outer face of the driver handle')


if __name__ == '__main__':
    main()
