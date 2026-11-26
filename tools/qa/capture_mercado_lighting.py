"""Compare the shelter lamp from the road before and after, in the production renderer."""
import argparse
import base64
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from capture_mercado import FIX, RENDER, SETUP, launch_options

# Both cameras stand on the 20 m road along X=168. Keep the regular gameplay FOV.
CAMERAS = {
    'taller': ([174, 1.62, 98], 3.0),
    'marquesina': ([161.5, 1.62, 127], 1.28),
}
CONFIGURE = """async () => {
 const {r,world,sim}=mercadoQA,gl=r.gl,draw=r.drawMeshes;
 if(!(await r.marketPedReady))throw Error('Resident atlas unavailable');
 const resident=sim.peds.find(n=>n.visualModel==='mercado-higgsfield');
 if(!resident)throw Error('Resident missing from generated world');
 resident.hidden=false;
 // Only omit the target's near mesh from the main color pass for the visibility control.
 // Its shadow and every other object remain identical in each paired exposure.
 r.drawMeshes=function(...args){
  const mesh=r.meshes[mercadoQA.omit];
  if(!mesh || gl.getParameter(gl.FRAMEBUFFER_BINDING)!==r.scene.fb)return draw.apply(r,args);
  const count=mesh.dynamicCount;mesh.dynamicCount=0;
  try{return draw.apply(r,args);}finally{mesh.dynamicCount=count;}
 };
 const ext=gl.getExtension('WEBGL_debug_renderer_info');
 return {renderer:ext?gl.getParameter(ext.UNMASKED_RENDERER_WEBGL):gl.getParameter(gl.RENDERER),
  sites:{taller:[world.workshop.x,world.workshop.z],marquesina:[world.shelters[1].x,world.shelters[1].z]},
  roadWidth:world.roadWidth(2,1,'v'),resident:[resident.x,resident.z]};
}"""
LIGHT = """value => {
 const slider=document.getElementById('daylight');
 slider.value=String(value);slider.dispatchEvent(new Event('input',{bubbles:true}));
 return [DC_APP.settings.daylight,DC_APP.renderer.daylight];
}"""


def frame(page, site, eye, height, omitted=None):
    page.evaluate('mesh=>{mercadoQA.omit=mesh;}', omitted)
    capture = page.evaluate(RENDER, {'site': site, 'eye': [eye[0]-site[0], eye[1], eye[2]-site[1]],
                                     'target': [0, height, 0], 'fov': math.pi*.36})
    png = base64.b64decode(capture['pixels'])
    return Image.open(io.BytesIO(png)).convert('RGB'), capture['lod']


def capture(browser, html):
    raw = html.read_bytes()
    errors = []
    scenes = {}
    page = browser.new_page(viewport={'width': 800, 'height': 480}, device_scale_factor=1)
    try:
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.on('request', lambda r: errors.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
        page.set_content(raw.decode().replace('<script>', '<script>'+FIX, 1), timeout=120000)
        page.wait_for_function('!!window.DC_APP', timeout=120000)
        page.evaluate(SETUP)
        config = page.evaluate(CONFIGURE)
        for name, (eye, height) in CAMERAS.items():
            site = config['sites'][name]
            assert abs(eye[0]-168) < config['roadWidth']/2
            for setting, value in [('day', 100), ('night', 0)]:
                assert page.evaluate(LIGHT, value) == [value/100]*2
                visible, lod = frame(page, site, eye, height)
                assert lod[name+'0'] == 1
                controls = {}
                for mesh in ([name+'0', 'marketPed0'] if name == 'marquesina' else [name+'0']):
                    control, _ = frame(page, site, eye, height, mesh)
                    controls[mesh] = np.asarray(control, dtype=np.int16)
                scenes[name, setting] = (visible, controls)
                if name == 'marquesina':
                    pose = page.evaluate("""() => {
                     const r=mercadoQA.r,slot=r.dynamic.marketPed0[15]-200,step=DC.SkinRig.paletteStride;
                     if(r.meshes.marketPed0.dynamicCount!==1||slot<1)throw Error('Missing resident');
                     return Array.from(r.posePixels.subarray(slot*step,(slot+1)*step));
                    }""")
                    digest = hashlib.sha256(np.array(pose, dtype='<f4').tobytes()).hexdigest()
                    assert config.setdefault('poseSha256', digest) == digest
        if errors:
            raise RuntimeError(errors)
        return scenes, config, hashlib.sha256(raw).hexdigest()
    finally:
        page.close()


def readings(scenes, site, mesh, upper_body=False):
    images = {}
    differences = {}
    for version, frames in scenes.items():
        for sky in ('day', 'night'):
            visible, controls = frames[site, sky]
            key = version, sky
            images[key] = np.asarray(visible, dtype=np.int16)
            differences[key] = images[key]-controls[mesh]
    mask = np.logical_and.reduce([abs(d).max(axis=2) > 4 for d in differences.values()])
    if upper_body:
        # Jacket band, expressed as a fraction of the visible resident's height.
        ys = np.flatnonzero(mask.any(axis=1))
        height = ys[-1]-ys[0]+1
        mask[:ys[0]+round(.20*height)] = False
        mask[ys[0]+round(.55*height):] = False
    if mask.sum() < 125:
        raise ValueError(f'{mesh}: too few shared visible pixels')
    weights = [.2126, .7152, .0722]
    result = {'sharedPixels': int(mask.sum())}
    for version in scenes:
        result[version] = {}
        for sky in ('day', 'night'):
            key = version, sky
            result[version][sky] = {
                'medianLuma': round(float(np.median(images[key][mask] @ weights)), 2),
                'medianBackgroundDifference': round(float(np.median(abs(differences[key][mask] @ weights))), 2)}
    return result


def scene_difference(before, after):
    delta = abs(np.asarray(before, dtype=np.int16)-np.asarray(after, dtype=np.int16)).max(axis=2)
    return {'p99MaxChannelDelta': round(float(np.percentile(delta, 99)), 2),
            'changedPixelsOver4': int(np.count_nonzero(delta > 4))}


def sheet(scenes, output):
    w, h = scenes['after']['marquesina', 'night'][0].size
    panel_width, panel_height = 600, round(h*600/w)
    label_height, gutter = 34, 8
    canvas = Image.new('RGB', (2*panel_width+3*gutter, 3*(panel_height+label_height)+4*gutter), '#172029')
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=18)
    center = (w/2, h/2)
    # Same 2x crop and display scale for both night details. No exposure changes.
    crop = (round(center[0]-w/4), round(center[1]-h/4), round(center[0]+w/4), round(center[1]+h/4))
    panels = [
        ('before', 'marquesina', 'night', 'Noche · Antes', False),
        ('after', 'marquesina', 'night', 'Noche · Con luminaria', False),
        ('before', 'marquesina', 'night', 'Detalle 2x · Antes', True),
        ('after', 'marquesina', 'night', 'Detalle 2x · Con luminaria', True),
        ('after', 'marquesina', 'day', 'Control · Parada a plena luz', False),
        ('after', 'taller', 'night', 'Control · Taller de noche', False),
    ]
    for i, (version, site, sky, label, zoom) in enumerate(panels):
        x = gutter+(i%2)*(panel_width+gutter)
        y = gutter+(i//2)*(panel_height+label_height+gutter)
        draw.text((x+2, y+4), label, font=font, fill='#f2f4f3')
        im = scenes[version][site, sky][0]
        im = im.crop(crop) if zoom else im
        canvas.paste(im.resize((panel_width, panel_height), Image.Resampling.LANCZOS), (x, y+label_height))
    canvas.save(output, quality=92, method=6)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('before', 'after', 'output'):
        parser.add_argument('--'+flag, required=True, type=Path)
    args = parser.parse_args()
    scenes, hashes = {}, {}
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        configs = []
        for name, path in [('before', args.before), ('after', args.after)]:
            scenes[name], config, hashes[name] = capture(browser, path)
            configs.append(config)
        assert configs[0] == configs[1], 'renderer, world, camera or resident pose changed'
        version = browser.version
    materials = {name: readings(scenes, site, mesh, jacket) for name, site, mesh, jacket in [
        ('workshop', 'taller', 'taller0', False), ('shelter', 'marquesina', 'marquesina0', False),
        ('resident', 'marquesina', 'marketPed0', False), ('jacketBand', 'marquesina', 'marketPed0', True)]}
    deltas = {site+'_'+sky: scene_difference(scenes['before'][site, sky][0], scenes['after'][site, sky][0])
              for site in CAMERAS for sky in ('day', 'night')}
    report = {'htmlSha256': hashes, 'chromium': version, **configs[0], 'timeS': 1.25, 'sliderPercent': [100, 0],
              'frameSize': list(scenes['after']['marquesina', 'night'][0].size), 'quality': 'balanced',
              'cameras': CAMERAS, 'materials': materials, 'frameDifferences': deltas}
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'mediciones.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    sheet(scenes, args.output/'calzada.webp')
    before, after = [materials['jacketBand'][v]['night']['medianBackgroundDifference'] for v in scenes]
    assert after-before >= 4 and after >= 1.15*before, f'Night jacket contrast {before} -> {after}'
    for control in ('taller_day', 'taller_night', 'marquesina_day'):
        assert deltas[control]['p99MaxChannelDelta'] <= 1, f'Light escaped the night shelter in {control}'
    print(f'PASS · Night jacket contrast {before} -> {after}, daylight and workshop controls passed.')


if __name__ == '__main__':
    main()
