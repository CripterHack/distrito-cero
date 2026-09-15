#!/usr/bin/env python3
"""Original v0.14 cervical contour correction on the continuous HM08-derived mesh.
Build-time only. Keeps triangle connectivity, positions of facial landmarks and 49-bone IDs.
The guide is an art-directed surface, not a biomechanical or clinical model.
"""
import json,base64
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def encode(p):return base64.b64encode(p.tobytes()).decode()
def welded_normals(data,blend=None):
 unique,inv=np.unique(data['p'],axis=0,return_inverse=True);v=unique.astype(float)/1e4;f=inv.reshape(-1,3)
 n=np.zeros_like(v);fn=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
 for j in range(3):np.add.at(n,f[:,j],fn)
 n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-15)
 new=n[inv]
 if blend is not None:
  new=data['n']/32767*(1-blend[:,None])+new*blend[:,None]
  new/=np.maximum(np.linalg.norm(new,axis=1)[:,None],1e-15)
 data['n']=np.round(new*32767).astype('<i2')
d=json.loads((R/'assets/hero-v013-baseline.js').read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
report={'base':'v0.13','topology':'unchanged','units':'metres','parts':{}}
for part in d['parts']:
 if part['name'] not in ['face','jacket']:continue
 data=np.frombuffer(base64.b64decode(part['data']),DT).copy();old=data.copy();v=data['p'].astype(float)/10000;x,y,z=v.T.copy()
 if part['name']=='face':
  ys=np.array([1.447,1.473,1.498,1.521,1.543,1.560,1.577,1.595,1.620])
  rx=PchipInterpolator(ys,[.070,.055,.048,.046,.0465,.0475,.052,.057,.065])(np.clip(y,ys[0],ys[-1]))
  rz=PchipInterpolator(ys,[.064,.051,.045,.044,.046,.048,.052,.057,.065])(np.clip(y,ys[0],ys[-1]))
  center=PchipInterpolator(ys,[-.016,-.018,-.018,-.018,-.019,-.020,-.020,-.018,-.014])(np.clip(y,ys[0],ys[-1]))
  phi=np.arctan2(x,z+.010)
  chin=smooth(.035,.092,z)*smooth(1.530,1.549,y)
  strength=(1-smooth(1.570,1.620,y))*(1-chin)
  band=smooth(1.467,1.495,y)*(1-smooth(1.578,1.604,y))
  direction=.40+1.10*smooth(1.472,1.594,y)
  scm=.00115*np.exp(-((np.abs(phi)-direction)/.31)**2)*band
  larynx=.00095*np.exp(-(phi/.35)**2-((y-1.531)/.017)**2)
  trapezius=.002*np.maximum(0,-np.cos(phi))**2*np.exp(-((y-1.479)/.042)**2)
  targetX=np.sin(phi)*(rx+scm)
  submental=.012*np.maximum(0,np.cos(phi))**4*np.exp(-((y-1.545)/.025)**2)
  targetZ=center+np.cos(phi)*(rz+scm+larynx+trapezius)+submental
  v[:,0]=x+(targetX-x)*strength;v[:,2]=z+(targetZ-z)*strength
  data['p']=np.round(v*1e4).astype('<i2')
  # Jaw belongs to the head regardless of the chin's height. The nape remains soft.
  head=np.maximum(smooth(1.532,1.619,y),chin)
  chest=(1-head)*(1-smooth(1.455,1.520,y))
  neck=np.maximum(0,1-head-chest)
  for i in np.where(y<1.625)[0]:
   weights=np.array([chest[i],neck[i],head[i]]);joints=np.array([2,3,4]);order=np.argsort(-weights,kind='stable')
   w=np.round(weights[order]*255).astype(int);w[0]+=255-int(w.sum())
   data['j'][i]=[*joints[order],0];data['w'][i]=[*w,0]
  welded_normals(data)
 else:
  # Let outer deltoid drape fall slightly instead of ending in a raised hard ledge.
  outer=smooth(.18,.265,np.abs(x))
  mask=smooth(1.375,1.435,y)*(1-smooth(1.464,1.487,y))
  v[:,1]-=.0075*outer*mask
  data['p']=np.round(v*1e4).astype('<i2')
  welded_normals(data,smooth(1.365,1.410,y)*smooth(.07,.14,np.abs(x)))
 delta=np.linalg.norm((data['p'].astype(float)-old['p'])/1e4,axis=1)
 part['data']=encode(data)
 report['parts'][part['name']]={'changed_corners':int((delta>0).sum()),'max_displacement_m':float(delta.max()),'normal_changes':int(np.any(data['n']!=old['n'],axis=1).sum()),'weight_changes':int(np.any(data['w']!=old['w'],axis=1).sum())}
d['provenance']+=' v0.14 original continuous cervical contour, nape and submandibular weights, preserved HM08 facial landmarks, slightly lowered garment deltoid edge.'
(R/'src/hero-asset.js').write_text('/* v0.14 cervical correction. Licensed ancestry unchanged, see assets/ATTRIBUTION-v014.md. */\nDC.HeroAsset='+json.dumps(d,separators=(',',':'))+';\n')
(R/'assets/cervical-v014.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
