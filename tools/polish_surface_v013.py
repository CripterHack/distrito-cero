#!/usr/bin/env python3
"""Deterministic, build-only smoothing of sampled garment surfaces.
The bound controls preserve the neck opening, zipper, cuffs, foot and hand data.
No runtime package, network resource or extra polygons are introduced.
"""
import json,base64
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
d=json.loads((R/'assets/hero-v012-baseline.js').read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
report={}
def ramp(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
for part in d['parts']:
 if part['name']=='skin':
  data=np.frombuffer(base64.b64decode(part['data']),DT).copy();v,inv=np.unique(data['p'],axis=0,return_inverse=True);f=inv.reshape(-1,3);v=v.astype(float)
  fn=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]);normal=np.zeros_like(v)
  for i in range(3):np.add.at(normal,f[:,i],fn)
  normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-15)
  before=data['n'].copy();data['n']=np.round(normal[inv]*32767).astype('<i2')
  report['hands']={'position_changes':0,'weight_changes':0,'normal_corner_changes':int(np.count_nonzero(np.any(before!=data['n'],axis=1))),'method':'angle-continuous area-weighted normals on shared quantized positions'}
  part['data']=base64.b64encode(data.tobytes()).decode();continue
 if part['name'] not in ['jacket','pants']:continue
 data=np.frombuffer(base64.b64decode(part['data']),DT).copy()
 unique,inv=np.unique(data['p'],axis=0,return_inverse=True);v=unique.astype(float)/10000;base=v.copy();f=inv.reshape(-1,3)
 edges=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges=np.unique(np.vstack([edges,edges[:,::-1]]),axis=0)
 graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))).tocsr();degree=np.asarray(graph.sum(1));degree=np.maximum(degree,1)
 x,y,z=v.T
 if part['name']=='jacket':
  mask=ramp(.075,.14,np.abs(x))*ramp(1.27,1.37,y)*(1-ramp(1.45,1.493,y))
  mask=np.maximum(mask,.5*ramp(.19,.225,np.abs(x))*np.exp(-((y-1.135)/.075)**2))
 else:mask=.4*np.exp(-((y-.495)/.060)**2)*(1-ramp(.72,.82,y))
 for _ in range(5):
  for coefficient in [.44,-.45]:v+=coefficient*mask[:,None]*(graph.dot(v)/degree-v)
 delta=v-base;length=np.linalg.norm(delta,axis=1);v=base+delta*np.minimum(1,.0045/np.maximum(length,1e-10))[:,None]
 vp=np.round(v*10000).astype('<i2')
 # Keep triangle orientation; undo an affected vertex if rounding flips a tiny face.
 for _ in range(3):
  p=vp.astype(float);old=base[f];new=p[f];cross0=np.cross(old[:,1]-old[:,0],old[:,2]-old[:,0]);cross1=np.cross(new[:,1]-new[:,0],new[:,2]-new[:,0]);bad=np.sum(cross0*cross1,axis=1)<0
  if not np.any(bad):break
  ids=np.unique(f[bad]);vp[ids]=unique[ids]
 p=vp.astype(float)/10000;n=np.zeros_like(p);fn=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
 for j in range(3):np.add.at(n,f[:,j],fn)
 norm=np.linalg.norm(n,axis=1);norm=np.maximum(norm,1e-15);n/=norm[:,None]
 data['p']=vp[inv]
 # Blending normals across transition band keeps untouched garment lighting unchanged.
 oldN=data['n'].astype(float)/32767;mix=mask[inv,None];newN=oldN*(1-mix)+n[inv]*mix
 newN/=np.maximum(np.linalg.norm(newN,axis=1)[:,None],1e-15);data['n']=np.clip(np.round(newN*32767),-32767,32767).astype('<i2')
 part['data']=base64.b64encode(data.tobytes()).decode()
 dist=np.linalg.norm(p-base,axis=1);report[part['name']]={'unique_vertices':len(v),'changed_vertices':int(np.count_nonzero(dist>.0001)),'max_delta_metres':float(dist.max())}
d['provenance']+=' Original v0.13 constrained surface polish on shoulders and garment flexion zones and welded skin shading normals, stable topology and bind contract.'
(R/'src/hero-asset.js').write_text('/* v0.13 polished original garment surfaces; HM08 head and existing hand topology retained. */\nDC.HeroAsset='+json.dumps(d,separators=(',',':'))+';\n')
(R/'assets/surface-polish-v013.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
