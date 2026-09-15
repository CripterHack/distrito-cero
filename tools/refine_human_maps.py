#!/usr/bin/env python3
"""Repair atlas disocclusion texels introduced by cylindrical reprojection.
Only the bake's defective left orbital region is mirrored from the clean right.
The raw transfer remains immutable. This is not a new scan or generated photo.
"""
from pathlib import Path
from PIL import Image, ImageFilter
import numpy as np,struct,base64,json,hashlib
R=Path(__file__).resolve().parents[1];source=R/'assets/anatomy-source'
b=(source/'compact.bin').read_bytes();o=16
for n,l in zip(['head.xz','skin.webp','normal.webp','roughness.webp'],struct.unpack_from('<4I',b)):
 (source/n).write_bytes(b[o:o+l]);o+=l
p=source/'skin.webp';im=Image.open(p).convert('RGB');a=np.asarray(im,dtype=float);yy,xx=np.indices(a.shape[:2]);mask=np.clip(1-(((xx-284)/30)**2+((yy-244)/41)**2),0,1)
mask=np.asarray(Image.fromarray((mask*255).astype('uint8')).filter(ImageFilter.GaussianBlur(3)))/255
mask=np.clip(mask*2.7,0,1);a=a*(1-mask[:,:,None])+a[:,::-1,:]*mask[:,:,None]
# Remove isolated reprojection spikes, not normal freckles or wrinkles.
med=np.asarray(Image.fromarray(a.astype('uint8')).filter(ImageFilter.MedianFilter(9)),float)
bad=(a.mean(2)<med.mean(2)-18)&(xx>130)&(xx<382)&(yy>110)&(yy<380)
a[bad]=med[bad]
Image.fromarray(a.astype('uint8')).save(source/'skin-repaired.webp',quality=92,method=6)
(source/'map-repair.json').write_text(json.dumps({'source_sha256':hashlib.sha256(b).hexdigest(),'repair':'Orbital disocclusion mirror with feathered border; isolated outlier removal','immutable_source':'compact.bin'},indent=2))
