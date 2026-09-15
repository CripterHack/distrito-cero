#!/usr/bin/env python3
"""Reproducible modest garment refinement. Preserves topology, weights, hands and source CC0 attribution."""
from pathlib import Path
import json,base64,struct
import numpy as np
R=Path(__file__).resolve().parents[1]
s=(R/'assets/hero-v010-baseline.js').read_text();asset=json.loads(s[s.index('{'):s.rfind('}')+1])
dtype=np.dtype([('pos','<i2',3),('normal','<i2',3),('uv','<u2',2),('joints','u1',4),('weights','u1',4)])
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def warp(p,mat):
 q=p.copy();x,y,z=p.T
 if mat in [31,32,3]:
  shoulder=smooth(.14,.22,abs(x))*np.exp(-((y-1.425)/.042)**2)
  q[:,0]-=np.sign(x)*shoulder*.007
  # Broader abdominal contour and less tubular transition into the upper chest.
  if mat==31:
   torso=(1-smooth(.15,.205,abs(x)))
   q[:,0]+=x*.052*np.exp(-((y-1.08)/.16)**2)*torso
   q[:,2]+=z*.05*np.exp(-((y-1.30)/.12)**2)*torso
   # Lower the overly high cylindrical collar without moving the neck skin.
   q[:,1]-=.015*smooth(1.463,1.521,y)
 return q
counts={}
for part in asset['parts']:
 if part['material'] not in [31,32,3]:continue
 a=np.frombuffer(base64.b64decode(part['data']),dtype=dtype).copy();p=a['pos'].astype(float)/10000;n=a['normal'].astype(float)/32767
 q=warp(p,part['material']);eps=.0001
 J=np.stack([(warp(p+np.eye(3)[i]*eps,part['material'])-warp(p-np.eye(3)[i]*eps,part['material']))/(2*eps) for i in range(3)],axis=-1)
 n=np.linalg.solve(np.transpose(J,(0,2,1)),n[...,None])[...,0];n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-8)
 a['pos']=np.round(q*10000);a['normal']=np.clip(np.round(n*32767),-32767,32767)
 part['data']=base64.b64encode(a.tobytes()).decode();counts[part['name']]=len(a)
asset['revision']='0.11';asset['refinement']='Softer shoulder cap, abdominal ease, chest depth and lower collar. Topology and 49-bone weights preserved.'
(R/'src/hero-asset.js').write_text("/* Shared weighted garment refinement; source in assets/hero-v010-baseline.js. */\nDC.HeroAsset="+json.dumps(asset,separators=(',',':'))+';\n')
print(counts)
