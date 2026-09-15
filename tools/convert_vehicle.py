#!/usr/bin/env python3
"""Compile the inspected, baked glTF mesh subset to native WebGL vertex buffers.

Input is the quantized POSITION/NORMAL/index export of Higgsfield revision 2.
This deliberately is not a general glTF loader. Skins, material textures and
non-identity node transforms require an explicit new converter, never silent loss.
Only Python's standard library is required. The game never fetches this input.
"""
from pathlib import Path
import array,base64,json,math,sys
ROOT=Path(__file__).resolve().parents[1]
src=json.loads((ROOT/'assets/higgsfield-body.json').read_text())
parts=[]
for part in src['parts']:
    if part.get('transform'):
        raise ValueError('Expected transforms baked to model space: '+part['name'])
    pos,normals,indices=part['position'],part['normal'],part['indices']
    if len(pos)%3 or len(normals)!=len(pos) or len(indices)%3:
        raise ValueError('Invalid geometry attributes')
    out=array.array('f')
    for i in indices:
        if not isinstance(i,int) or not 0<=i<len(pos)//3: raise ValueError('Bad index')
        p=[pos[i*3+k]*src['unit'] for k in range(3)]
        n=[normals[i*3+k]*src['unit'] for k in range(3)]
        length=math.sqrt(sum(v*v for v in n))
        if length<.5: raise ValueError('Invalid normal')
        out.extend(p+[v/length for v in n]+[p[0],p[2]])
    if sys.byteorder!='little': out.byteswap()
    parts.append({'name':part['name'],'vertices':len(indices),'data':base64.b64encode(out.tobytes()).decode()})
asset={'sourceProject':src['sourceProject'],'revision':src['revision'],'generator':src['generator'],
       'coordinates':'metres, Y up, +Z forward','parts':parts}
(ROOT/'src/vehicle-asset.js').write_text('/* Original Higgsfield/Blender geometry, baked offline. No runtime requests. */\nDC.VehicleAsset='+json.dumps(asset,separators=(',',':'))+';\n')
print('Vehicle geometry:',sum(p['vertices']//3 for p in parts),'triangles in',len(parts),'native buffers')
