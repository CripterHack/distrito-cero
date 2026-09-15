#!/usr/bin/env python3
"""v0.15 cervical mass integration. Reproducible, offline authoring only.
The dimensions are art-directed for this avatar, not an anthropometric standard.
Keeps topology, UVs, bone IDs, facial landmarks and unrelated model surfaces.
"""
import base64,json
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def smooth(a,b,x):
 t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)
def normals(data,blend):
 unique,inv=np.unique(data['p'],axis=0,return_inverse=True);v=unique.astype(float)/1e4;f=inv.reshape(-1,3)
 n=np.zeros_like(v);fn=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
 for j in range(3):np.add.at(n,f[:,j],fn)
 n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-15)
 new=data['n']/32767*(1-blend[:,None])+n[inv]*blend[:,None]
 new/=np.maximum(np.linalg.norm(new,axis=1)[:,None],1e-15)
 data['n']=np.round(new*32767).astype('<i2')
Y=np.array([1.447,1.473,1.498,1.521,1.543,1.560,1.577,1.595,1.620])
OLD_X=[.070,.055,.048,.046,.0465,.0475,.052,.057,.065]
OLD_Z=[.064,.051,.045,.044,.046,.048,.052,.057,.065]
NEW_X=[.089,.075,.066,.064,.0635,.063,.0635,.067,.065]
NEW_Z=[.073,.065,.060,.059,.060,.061,.063,.064,.065]
NEW_BACK=[.079,.067,.061,.056,.051,.048,.050,.057,.065]
CENTRE=[-.016,-.018,-.018,-.018,-.019,-.020,-.020,-.018,-.014]
def curve(values,y):return PchipInterpolator(Y,values)(np.clip(y,Y[0],Y[-1]))
def main():
 d=json.loads((R/'assets/hero-v014-baseline.js').read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
 report={'base':'v0.14','topology':'unchanged','units':'metres','profile_y':Y.tolist(),'profile_radius_x':NEW_X,'profile_radius_z':NEW_Z,'profile_back_radius':NEW_BACK,'parts':{}}
 for part in d['parts']:
  if part['name'] not in ('face','jacket','metal'):continue
  data=np.frombuffer(base64.b64decode(part['data']),DT).copy();old=data.copy();v=data['p'].astype(float)/1e4;x,y,z=v.T.copy()
  if part['name']=='face':
   center=curve(CENTRE,y)
   guard=smooth(.035,.092,z)*smooth(1.530,1.549,y)
   strength=(1-smooth(1.572,1.621,y))*(1-guard)
   sx=curve(NEW_X,y)/curve(OLD_X,y);sz=(curve(NEW_BACK,y)*(1-smooth(-.018,.022,z-center))+curve(NEW_Z,y)*smooth(-.018,.022,z-center))/curve(OLD_Z,y)
   v[:,0]=x*(1+(sx-1)*strength);v[:,2]=center+(z-center)*(1+(sz-1)*strength)
   # Broad subtle relief, not separate tendons or repeated grooves.
   phi=np.arctan2(v[:,0],v[:,2]-center)
   band=smooth(1.463,1.490,y)*(1-smooth(1.560,1.601,y))
   path=.48+1.1*smooth(1.475,1.597,y)
   relief=.0008*np.exp(-((np.abs(phi)-path)/.42)**2)*band*(1-guard)
   v[:,0]+=np.sin(phi)*relief;v[:,2]+=np.cos(phi)*relief
   # Spread the under-jaw transition over an oblique surface instead of a
   # short height threshold. Preserve full head influence on the chin tip.
   head=np.maximum(smooth(1.542,1.622,y),smooth(.016,.103,v[:,2])*smooth(1.485,1.550,y))
   head=np.where((z>.098)&(y>1.550),1,head)
   chest=(1-head)*(1-smooth(1.455,1.520,y))
   neck=np.maximum(0,1-head-chest)
   for i in np.where(y<1.625)[0]:
    w=np.array([chest[i],neck[i],head[i]]);j=np.array([2,3,4]);order=np.argsort(-w,kind='stable')
    qw=np.round(w[order]*255).astype(int);qw[0]+=255-int(qw.sum())
    data['j'][i]=[*j[order],0];data['w'][i]=[*qw,0]
   normal_mask=1-smooth(1.612,1.627,y)
  else:
   # Drape the same opening over the wider neck with broad falloff into shoulders.
   radius=np.hypot(x,(z+.016)*1.04)
   vertical=smooth(1.414,1.470,y)*(1-smooth(1.495,1.505,y))
   local=1-smooth(.085,.168,radius)
   m=vertical*local
   v[:,0]=x*(1+.255*m);v[:,2]=-.016+(z+.016)*(1+.265*m)
   # Raised inner trapezius, lower outer shoulder: keep the collar height, no turtleneck.
   slope=np.exp(-((np.abs(x)-.125)/.054)**2)*smooth(1.417,1.455,y)*(1-smooth(1.480,1.499,y))
   v[:,1]+=.004*slope
   normal_mask=smooth(1.392,1.423,y)*(1-smooth(1.501,1.520,y))
  data['p']=np.round(v*1e4).astype('<i2');normals(data,normal_mask)
  delta=np.linalg.norm((data['p'].astype(float)-old['p'])/1e4,axis=1)
  part['data']=base64.b64encode(data.tobytes()).decode()
  report['parts'][part['name']]={'changed_corners':int((delta>0).sum()),'max_displacement_m':float(delta.max()),'weights_preserved':bool(np.array_equal(data['w'],old['w'])),'uv_preserved':bool(np.array_equal(data['uv'],old['uv']))}
 d['provenance']+=' v0.15 integrated cervical mass, broader posterior support and fitted garment opening. Facial features, original licenses and skeletal dimensions preserved.'
 (R/'src/hero-asset.js').write_text('/* v0.15 integrated neck. See assets/ATTRIBUTION-v015.md. */\nDC.HeroAsset='+json.dumps(d,separators=(',',':'))+';\n')
 (R/'assets/cervical-integration-v015.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
if __name__=='__main__':main()
