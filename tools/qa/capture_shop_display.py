"""Measure merchandise against its own backing through the display glass in WebGL2."""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

from capture_street_architecture import DRAW, FIX, SETUP, VIEWS, launch_options

CAMERAS = {
    'front': ([148.5, 1.8, 176.7], [146.5, 1.55, 185.8]),
    'corner': ([155.3, 1.8, 179.6], [147.5, 1.65, 186.4]),
    'shelter': ([161.5, 1.62, 127.], [154.5, 1.5, 130.]),
    'rural': VIEWS['rural']
}
WEIGHTS = np.array([.2126, .7152, .0722])
# Only the fifteen packages in the selected corner. Shelves, trays, glazing
# and framing still draw during the second exposure used to measure the backing.
MASK_STOCK = '''() => {
 const {r}=archScene, original=r.renderCornerShopDetails;
 r.renderCornerShopDetails=function(){
  const rows=this.dynamic.box, start=rows.length;
  original.call(this);
  if(!archScene.hideStock)return;
  let dest=start, hidden=0;
  for(let i=start;i<rows.length;i+=16){
   const x=rows[i], y=rows[i+1], z=rows[i+2];
   if(x>141 && x<151 && z>185 && z<190 && [1.29,1.33,1.95].includes(y)){hidden++;continue;}
   for(let j=0;j<16;j++)rows[dest++]=rows[i+j];
  }
  rows.length=dest;
  if(hidden!==15)throw Error('Expected all 15 stock packages at the observed corner');
 };
}'''


def capture(browser, source):
    page = browser.new_page(viewport={'width': 768, 'height': 480}, device_scale_factor=1)
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    html = source.read_bytes()
    page.set_content(html.decode().replace('<script>', '<script>' + FIX, 1), timeout=120000)
    page.wait_for_function('!!window.DC_APP', timeout=120000)
    page.evaluate('Promise.all([DC_APP.renderer.humanReady, DC_APP.renderer.mercadoReady, DC_APP.renderer.marketPedReady])')
    stats = {'htmlSha256': sha256(html).hexdigest(), 'environment': page.evaluate(SETUP), 'views': {}}
    page.evaluate(MASK_STOCK)
    frames = {}
    for view, camera in CAMERAS.items():
        display = view in ('front', 'corner')
        for sky, daylight in [('night', .04), ('day', .83)] if display else [('night', .04)]:
            page.evaluate('d => archScene.r.daylight=d', daylight)
            for hidden in (False, True) if display and sky == 'night' else (False,):
                page.evaluate('b => archScene.hideStock=b', hidden)
                data = page.evaluate(DRAW, camera)
                frame = Image.open(io.BytesIO(page.screenshot())).convert('RGB')
                frames[view, sky, hidden] = np.asarray(frame, dtype=np.int16)
                if not hidden:
                    stats['views'][view + '-' + sky] = data
    page.close()
    if errors:
        raise RuntimeError(errors)
    return stats, frames


def measure(before, after):
    result = {}
    for view in ('front', 'corner'):
        delta = [group[view,'night',False] - group[view,'night',True] for group in (before,after)]
        # Common visible silhouettes, excluding subpixel boundaries/noise.
        mask = (abs(delta[0]).max(axis=2) > 6) & (abs(delta[1]).max(axis=2) > 6)
        result[view] = {'pixels': int(mask.sum()), 'stockAgainstBacking': [
            round(float(np.median(abs(d[mask] @ WEIGHTS))), 2) for d in delta
        ]}
        if mask.sum() < 200:
            raise ValueError(f'{view}: too few common merchandise pixels')
    return result


def gallery(before, after, path):
    panel, gap, label = 550, 10, 30
    rows = [('front', None, 'Desde la acera'),
            ('front', (170, 174, 594, 294), 'Detalle frontal'),
            ('corner', (234, 167, 496, 298), 'Detalle de esquina')]
    heights = [round(panel*480/768) if crop is None else round(panel*(crop[3]-crop[1])/(crop[2]-crop[0]))
               for _, crop, _ in rows]
    image = Image.new('RGB', (2*panel + 3*gap, sum(heights) + 3*label + 4*gap), '#18201f')
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype('DejaVuSans.ttf', 18)
    y = gap
    for (view, crop, description), height in zip(rows, heights):
        for col, (title, frames) in enumerate([('Antes', before), ('Con luz de exposición', after)]):
            source = Image.fromarray(frames[view,'night',False].astype('uint8'))
            if crop is not None:
                source = source.crop(crop)
            x = gap + col*(panel+gap)
            draw.text((x, y+2), f'{description} · {title}', font=font, fill='#eef3e9')
            image.paste(source.resize((panel, height), Image.Resampling.LANCZOS), (x, y+label))
        y += height+label+gap
    image.save(path, quality=91)


def run(before, after, output):
    output.mkdir(parents=True, exist_ok=False)
    with sync_playwright() as pw, pw.chromium.launch(**launch_options()) as browser:
        a, old = capture(browser, before)
        b, new = capture(browser, after)
        version = browser.version
    assert a['environment'] == b['environment']
    for key in a['views']:
        assert a['views'][key] == b['views'][key], f'Camera, draw calls or geometry changed at {key}'
    measurements = measure(old, new)
    changed = {}
    for (view, sky, hidden), frame in old.items():
        if hidden:
            continue
        key = view+'-'+sky
        changed[key] = int(np.any(frame != new[view,sky,False], axis=2).sum())
    stats = dict(chromium=version, before=a, after=b, merchandise=measurements, changedPixels=changed)
    (output/'mediciones.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2)+'\n')
    gallery(old, new, output/'vitrinas.jpg')
    for key in ('front-day', 'corner-day', 'shelter-night', 'rural-night'):
        assert changed[key] == 0, f'Night display treatment escaped its scope at {key}'
    for view, data in measurements.items():
        low, high = data['stockAgainstBacking']
        assert high-low >= 3, f'{view}: insufficient stock contrast gain ({low} to {high})'
    print(json.dumps(measurements))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('before','after','output'):
        parser.add_argument('--'+option, required=True, type=Path)
    args=parser.parse_args()
    run(args.before, args.after, args.output)
