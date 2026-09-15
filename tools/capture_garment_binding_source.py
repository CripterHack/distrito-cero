#!/usr/bin/env python3
"""Capture only authoring influences from the verified pre-fix garment, once."""
from pathlib import Path
import base64, hashlib, json, zlib
ROOT=Path(__file__).resolve().parents[1]
BASE='7dedf527bfe9e257c3067a4db063521e09a72d680ed2f8323fedd69a202ee5f4'
def capture(raw):
    if hashlib.sha256(raw).hexdigest()!=BASE: raise ValueError('Not the reviewed pre-fix asset; never derive seeds from a corrected asset')
    data=json.loads(raw.decode().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
    result={'schema':1,'sourceCommit':'072750bc65d9ceb10ca536bc7f0c7b3146a5b055','sourceAssetSha256':BASE,
        'note':'Original native garment binding data only. Geometry remains in src/hero-asset.js. Not a new third-party asset.','parts':{}}
    for part in data['parts']:
        if part['name'] not in ('jacket','pants'): continue
        b=base64.b64decode(part['data']);attributes=b''.join(b[i:i+16] for i in range(0,len(b),24));weights=b''.join(b[i+16:i+24] for i in range(0,len(b),24))
        result['parts'][part['name']]={'vertices':part['vertices'],'attributesSha256':hashlib.sha256(attributes).hexdigest(),'weightsZlibBase64':base64.b64encode(zlib.compress(weights,9)).decode()}
    return (json.dumps(result,indent=2)+'\n').encode()
if __name__=='__main__':
    path=ROOT/'assets/garment-binding-source.json'
    if path.exists(): raise SystemExit('Seed already exists. Do not overwrite authoring data.')
    path.write_bytes(capture((ROOT/'src/hero-asset.js').read_bytes()))
