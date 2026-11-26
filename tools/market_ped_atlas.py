"""Resample the three original PBR images and the interdigital vertex material into one native atlas.

Invoked by prepare_market_ped.cjs. Each 512 px tile contains the primary map plus a small
two-dimensional skin swatch derived from the original linear RGB vertex colors.
"""
import base64
import io
import json
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageOps

TILE, GUTTER, MAIN_HEIGHT, WALL_TOP = 512, 4, 476, 488
SIDE = TILE - 2 * GUTTER


def extend(tile, patch, top, first, last):
    padded = np.pad(np.asarray(patch), ((top-first, last-top-patch.height),
                                        (GUTTER,GUTTER), (0,0)), mode='edge')
    tile.paste(Image.fromarray(padded), (0, first))


def linear_to_srgb(x):
    return np.where(x<=.0031308, 12.92*x, 1.055*np.power(np.maximum(x,0),1/2.4)-.055)


def prepare(request):
    colors = np.array(request['colors'])
    low, high = colors.min(axis=0), colors.max(axis=0)
    wall_height = TILE - GUTTER - WALL_TOP
    red, green = np.meshgrid(np.linspace(low[0],high[0],SIDE),
                             np.linspace(low[1],high[1],wall_height))
    # The second source material stores baked skin colors per vertex. Red and green
    # parameterize an interpolable swatch; fit its remaining color component in linear RGB.
    factors, *_ = np.linalg.lstsq(np.column_stack((colors[:,:2],np.ones(len(colors)))), colors[:,2],rcond=None)
    blue = red*factors[0]+green*factors[1]+factors[2]
    rgb = np.stack((red,green,blue), axis=-1)
    swatch = Image.fromarray(np.rint(np.clip(linear_to_srgb(rgb),0,1)*255).astype('uint8'))
    raw = Path(request['source']).read_bytes()
    atlas = Image.new('RGB',(TILE,TILE*3))
    for i,(offset,length) in enumerate(request['maps']):
        source = Image.open(io.BytesIO(raw[offset:offset+length])).convert('RGB')
        main = source.resize((SIDE,MAIN_HEIGHT),Image.Resampling.LANCZOS)
        if i == 2:
            # Native vertices use 1 - glTF V. Reflect the bitangent component once,
            # matching the derivative-based tangent frame reconstructed in the shader.
            r,g,b = main.split()
            main = Image.merge('RGB',(r,ImageOps.invert(g),b))
        tile = Image.new('RGB',(TILE,TILE))
        extend(tile,main,GUTTER,0,WALL_TOP-GUTTER)
        if i == 0:
            patch = swatch
        elif i == 1:
            patch = Image.new('RGB',(SIDE,wall_height),(255,round(request['roughness']*255),0))
        else:
            patch = Image.new('RGB',(SIDE,wall_height),(128,128,255))
        extend(tile,patch,WALL_TOP,WALL_TOP-GUTTER,TILE)
        # GPU UNPACK_FLIP_Y_WEBGL uploads bottom file row as texture row zero.
        atlas.paste(tile,(0,(2-i)*TILE))
    encoded = io.BytesIO()
    atlas.save(encoded,'WEBP',method=6,quality=94)
    return {
        'atlas':'data:image/webp;base64,'+base64.b64encode(encoded.getvalue()).decode('ascii'),
        'mainHeight':MAIN_HEIGHT,'wallTop':WALL_TOP,'tile':TILE,'gutter':GUTTER,
        'colorMin':low[:2].tolist(),'colorMax':high[:2].tolist(),
    }


if __name__ == '__main__':
    json.dump(prepare(json.load(sys.stdin)),sys.stdout)
