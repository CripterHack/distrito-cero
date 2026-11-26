"""Compare the two road-facing elevations of a streamed shop on the native renderer."""
import argparse
import hashlib
import io
import json
import sys
from pathlib import Path

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
from character_benchmark import FIX
from qa_support import launch_options

# Fixed world-space views, in metres. The first three follow the same pavement
# around a corner of the seed-1337 home block; the rural view is a control.
VIEWS = {
    'approach': ([76.4, 2.1, 5.0], [64.5, 2.0, 15.3]),
    'entrance': ([67.5, 1.76, 6.5], [63.2, 1.88, 15.4]),
    'corner': ([73.4, 1.79, 10.4], [66.3, 1.88, 17.7]),
    'return': ([77.6, 1.78, 20.2], [67.8, 1.88, 18.3]),
    'rural': ([5.5, 1.85, 2020.], [26.0, 2.0, 2041.])
}
SETUP = """() => {
    const app=DC_APP;
    app.stopFrame();qaStopFrames();window.requestAnimationFrame=()=>0;
    const sim=new DC.Simulation(new DC.World(1337));
    sim.free=true;sim.time=1.25;
    sim.peds.forEach(p=>p.hidden=true);sim.cars.forEach((v,i)=>Object.assign(v,{x:6000+i*6,z:6000,driver:null}));
    const r=app.renderer;r.previewStudio=false;r.world=sim.world;r.resetSectors();
    r.daylight=.83;r.rain=r.bloom=0;r.quality='balanced';r.resize();
    const css=document.createElement('style');
    css.textContent='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}';
    document.head.append(css);
    const gl=r.gl,ext=gl.getExtension('WEBGL_debug_renderer_info');
    window.archScene={sim,r};
    return {webGL:gl.getParameter(gl.VERSION),renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER)};
}"""
DRAW = """([eye,target]) => {
    const {r,sim}=archScene,gl=r.gl;
    if(sim.world.blocked(eye[0],eye[2],.20))throw Error('Camera is inside a building');
    Object.assign(sim.player,{x:eye[0]-3,y:0,z:eye[2]-4,car:null});
    sim.syncRegion();r.syncSectors(100);
    Object.assign(r.camera,{eye,target,initialized:true});r.frame=0;r.lightTime=-1;
    const original=gl.drawArraysInstanced;let calls=0,triangles=0;
    gl.drawArraysInstanced=function(mode,first,vertices,instances){calls++;triangles+=vertices*instances/3;return original.call(this,mode,first,vertices,instances);};
    try{r.render(sim);gl.finish();}finally{gl.drawArraysInstanced=original;}
    if(gl.getError()!==gl.NO_ERROR || gl.isContextLost() || r.streamStats.pending)throw Error('Incomplete native frame');
    return {eye:r.camera.eye,target:r.camera.target,calls,triangles,stream:r.streamStats,world:sim.world.seed};
}"""

def capture_walk(page, path):
    # Walk from the front door to the side window via the outer pavement.
    frames = []
    last = None
    for start, end in [('entrance', 'corner'), ('corner', 'return')]:
        for step in range(7):
            if start == last and step == 0:
                continue
            t = step / 6
            view = [[a + (b - a) * t for a, b in zip(left, right)]
                    for left, right in zip(VIEWS[start], VIEWS[end])]
            page.evaluate(DRAW, view)
            with Image.open(io.BytesIO(page.screenshot(timeout=120000))) as img:
                frames.append(img.convert('RGB').resize((640, 360), Image.Resampling.LANCZOS))
        last = end
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=155,
                   quality=76, method=4, loop=0)


def capture(browser, html, directory, walk):
    page = browser.new_page(viewport={'width': 1024, 'height': 576}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    try:
        source = html.read_bytes()
        page.set_content(source.decode().replace('<script>', '<script>' + FIX, 1), timeout=120000)
        page.wait_for_function('!!window.DC_APP', timeout=120000)
        page.evaluate('DC_APP.renderer.humanReady')
        result = {
            'sha256': hashlib.sha256(source).hexdigest(),
            'environment': page.evaluate(SETUP),
            'views': {}
        }
        for name, view in VIEWS.items():
            result['views'][name] = page.evaluate(DRAW, view)
            page.screenshot(path=str(directory / (name + '.png')), timeout=120000)
            print('Captured', directory.name, name, flush=True)
        if walk:
            capture_walk(page, directory / 'walk.webp')
        if errors:
            raise RuntimeError(errors)
        return result
    finally:
        page.close()


def comparison_sheet(output):
    sheet = Image.new('RGB', (1538, 866), '#202020')
    for col, label in enumerate(('before', 'after')):
        for row, name in enumerate(('entrance', 'corner')):
            with Image.open(output / label / (name + '.png')) as source:
                frame = source.resize((768, 432), Image.Resampling.LANCZOS)
                sheet.paste(frame, (col * 770, row * 434))
    sheet.save(output / 'comparacion.jpg', quality=87)


def run(before, after, output, walk):
    output.mkdir(parents=True, exist_ok=False)
    report = {}
    with sync_playwright() as p, p.chromium.launch(**launch_options()) as browser:
        for label, html in [('before', before), ('after', after)]:
            (output / label).mkdir()
            report[label] = capture(browser, html, output / label, walk and label == 'after')
    if report['before']['environment'] != report['after']['environment']:
        raise RuntimeError('Renderers differ')
    report['changedPixels'] = {}
    for name in VIEWS:
        views = [Image.open(output / label / (name + '.png')).convert('RGB') for label in ('before', 'after')]
        diff = ImageChops.difference(*views)
        red, green, blue = diff.split()
        maximum = ImageChops.lighter(ImageChops.lighter(red, green), blue)
        count = diff.width * diff.height - maximum.histogram()[0]
        if (name == 'rural') != (count == 0):
            raise RuntimeError(f'Unexpected pixel comparison for {name}: {count}')
        report['changedPixels'][name] = count
    comparison_sheet(output)
    (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('before', 'after', 'output'):
        parser.add_argument('--' + flag, type=Path, required=True)
    parser.add_argument('--walk', action='store_true', help='Capture a 13-frame pavement walkthrough on the candidate')
    options = parser.parse_args()
    run(options.before, options.after, options.output, options.walk)
