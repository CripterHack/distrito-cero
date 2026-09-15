#!/usr/bin/env python3
"""Bake the native counterpart of the original Higgsfield character recipe.

This is an independent build-time reconstruction, NOT a byte-for-byte GLB import.
Garments are implicit unions, meshed here using marching cubes. Runtime requires
no Python or third-party libraries. The exported Higgsfield GLB is a separate asset.
"""
import base64, json, struct, hashlib
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes
ROOT=Path(__file__).resolve().parents[1]
PI=np.pi
BONES=[('pelvis',None,[0,.90,0]),('spine','pelvis',[0,1.10,0]),('chest','spine',[0,1.34,0]),('neck','chest',[0,1.50,0]),('head','neck',[0,1.63,0])]
for s,k in [(-1,'L'),(1,'R')]:BONES.extend([('upperArm'+k,'chest',[s*.255,1.43,0]),('forearm'+k,'upperArm'+k,[s*.29,1.12,0]),('hand'+k,'forearm'+k,[s*.305,.835,0]),('thigh'+k,'pelvis',[s*.115,.90,0]),('shin'+k,'thigh'+k,[s*.115,.48,0]),('foot'+k,'shin'+k,[s*.115,.08,0])])
IDS={n:i for i,(n,_,_) in enumerate(BONES)}
MATERIALS={
 'jacket':([.105,.165,.155],31), 'pants':([.048,.065,.081],32),
 'skin':([.46,.28,.185],30), 'hair':([.024,.021,.018],33),
 'rubber':([.022,.027,.032],4),'sole':([.35,.38,.36],0),
 'metal':([.40,.43,.42],3),'eye':([.55,.51,.43],34),'iris':([.044,.061,.035],34),
 'pupil':([.009,.009,.008],34),'lip':([.24,.099,.070],30)}
GROUPS={k:[] for k in MATERIALS}
METRICS={}
def blend(a,b,t):
 t=float(np.clip(t,0,1));t=t*t*(3-2*t);return {a:1-t,b:t}
def weights(cat,p):
 x,y,z=p;k='L' if x<0 else 'R'
 if cat=='head':return {'head':1}
 if cat=='neck':return blend('chest','head',(y-1.47)/.14)
 if cat.startswith('hand'):return {'hand'+cat[-1]:1}
 if cat.startswith('foot'):return {'foot'+cat[-1]:1}
 if cat=='jacket':
  # Soft transverse blend removes the abrupt sleeve/torso weight discontinuity.
  body=blend('pelvis','spine',(y-.95)/.21) if y<1.16 else blend('spine','chest',(y-1.16)/.23)
  if y>1.46:return body
  if y>1.35:arm=blend('upperArm'+k,'chest',(y-1.35)/.17)
  elif y>1.04:arm=blend('forearm'+k,'upperArm'+k,(y-1.04)/.16)
  else:arm=blend('hand'+k,'forearm'+k,(y-.81)/.10)
  t=float(np.clip((abs(x)-.185)/.066,0,1));t=t*t*(3-2*t)
  out={}
  for n,w in body.items():out[n]=out.get(n,0)+w*(1-t)
  for n,w in arm.items():out[n]=out.get(n,0)+w*t
  return out
 if cat=='pants':
  if y>.86:return blend('thigh'+k,'pelvis',(y-.86)/.13)
  if y>.39:return blend('shin'+k,'thigh'+k,(y-.39)/.18)
  return blend('foot'+k,'shin'+k,(y-.08)/.11)
 return {'pelvis':1}
def add_mesh(name,verts,faces,material,cat,normals=None):
 v=np.asarray(verts,float);f=np.asarray(faces,int)
 # Consistent outward winding for closed geometry; leaves are not part of this bake.
 volume=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
 if volume<0:f=f[:,[0,2,1]]
 if normals is None:
  normals=np.zeros_like(v);ns=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
  for j in range(3):np.add.at(normals,f[:,j],ns)
  normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
 rows=[]
 for point,n in zip(v,normals):
  entries=sorted(weights(cat,point).items(),key=lambda t:t[1],reverse=True)[:4];total=sum(w for _,w in entries)
  joints=[IDS[name] for name,_ in entries]+[0]*(4-len(entries));ws=[w/total for _,w in entries]+[0]*(4-len(entries))
  # Store cylindrical-ish coordinates for procedural weave/freckles, not image textures.
  uv=[np.arctan2(point[2],point[0])/PI*.5+.5,float(point[1]/1.9)]
  point=point.copy();n=n.copy()
  if cat=='head':
   point[0]*=.76;point[1]=1.63+(point[1]-1.63)*.82;point[2]*=.90;n/=np.array([.76,.82,.90])
  elif cat in ('jacket','neck','handL','handR'):
   point[0]*=.90;n[0]/=.90
  n/=max(np.linalg.norm(n),1e-8)
  rows.append([*point,*n,*uv,*joints,*ws])
 data=np.asarray(rows,dtype=np.float32)[f.reshape(-1)]
 valid=np.linalg.norm(np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]]),axis=1)>1e-10
 data=data.reshape(-1,3,16)[valid].reshape(-1,16)
 GROUPS[material].append(data);METRICS[name]={'vertices':len(v),'triangles':len(data)//3,'category':cat}
def loft(name,rings,material,cat,seg=32,subdiv=3):
 r=np.asarray(sorted(rings,key=lambda t:t[1]),float);ys=np.linspace(r[0,1],r[-1,1],(len(r)-1)*subdiv+1)
 # Piecewise monotone interpolation avoids over-inflated limbs at cuffs.
 from scipy.interpolate import PchipInterpolator
 columns=[PchipInterpolator(r[:,1],r[:,j])(ys) for j in [0,2,3,4]]
 p=[];f=[]
 for y,x,z,rx,rz in zip(ys,*columns):
  for i in range(seg):a=i*2*PI/seg;p.append([x+np.cos(a)*rx,y,z+np.sin(a)*rz])
 for j in range(len(ys)-1):
  for i in range(seg):a=j*seg+i;b=j*seg+(i+1)%seg;f.extend([[a,b,b+seg],[a,b+seg,a+seg]])
 for i in range(1,seg-1):f.append([0,i+1,i]);a=(len(ys)-1)*seg;f.append([a,a+i,a+i+1])
 add_mesh(name,p,f,material,cat)
def ellipsoid(name,center,radii,material,cat,seg=16,lat=10):
 p=[];f=[]
 for j in range(lat+1):
  a=j*PI/lat
  for i in range(seg):b=i*PI*2/seg;p.append([center[0]+radii[0]*np.sin(a)*np.cos(b),center[1]+radii[1]*np.cos(a),center[2]+radii[2]*np.sin(a)*np.sin(b)])
 for j in range(lat):
  for i in range(seg):a=j*seg+i;b=j*seg+(i+1)%seg;f.extend([[a,b,b+seg],[a,b+seg,a+seg]])
 # Exact smooth ellipsoid normals (including poles).
 norms=(np.asarray(p)-np.array(center))/np.square(radii);norms/=np.linalg.norm(norms,axis=1)[:,None]
 add_mesh(name,p,f,material,cat,norms)
def union_garment(name,lofts,material,step=.016):
 from scipy.interpolate import PchipInterpolator
 lo=np.array([-.41,.04,-.18]) if material=='pants' else np.array([-.41,.80,-.18]);hi=np.array([.41,1.04,.18]) if material=='pants' else np.array([.41,1.53,.18])
 axes=[np.arange(lo[i],hi[i]+step,step) for i in range(3)];x,y,z=np.meshgrid(*axes,indexing='ij');field=np.ones_like(x)*10
 for rings in lofts:
  r=np.asarray(sorted(rings,key=lambda t:t[1]));clipped=np.clip(y,r[0,1],r[-1,1]);x0,z0,rx,rz=[PchipInterpolator(r[:,1],r[:,j])(clipped) for j in [0,2,3,4]]
  # SDF approximation of an elliptical loft with end caps, clipped union.
  f=(np.sqrt(((x-x0)/rx)**2+((z-z0)/rz)**2)-1)*np.minimum(rx,rz)
  f=np.maximum(f,np.maximum(r[0,1]-y,y-r[-1,1]));field=np.minimum(field,f)
 field=gaussian_filter(field,.6)
 v,f,_,_=marching_cubes(field,0,spacing=(step,step,step),allow_degenerate=False);v+=lo
 # Rounded cloth contours and restrained physical-sized folds near elbows/knees/waist.
 for i,point in enumerate(v):
  xx,yy,zz=point
  if material=='jacket':fold=np.exp(-((yy-1.115)/.12)**2)+.5*np.exp(-((yy-1.0)/.07)**2)
  else:fold=np.exp(-((yy-.48)/.085)**2)+.4*np.exp(-((yy-.16)/.045)**2)
  angle=np.arctan2(zz,xx if material=='jacket' else xx-np.sign(xx)*.115)
  point[2]+=.0035*fold*np.sin(yy*120+xx*22)*np.sin(angle)
 add_mesh(name,v,f,material,material)
TORSO=[(0,.96,0,.175,.112),(0,1,0,.186,.12),(0,1.07,0,.178,.112),(0,1.16,-.003,.193,.121),(0,1.28,-.009,.219,.128),(0,1.39,-.005,.245,.115),(0,1.445,0,.208,.097),(0,1.48,0,.085,.075)]
SLEEVE=[(1.45,.22,.093,.092),(1.40,.254,.082,.09),(1.31,.269,.073,.081),(1.22,.28,.067,.075),(1.12,.29,.063,.070),(1.065,.294,.065,.072),(.97,.30,.058,.064),(.87,.305,.050,.055),(.835,.305,.046,.051)]
lofts=[TORSO]+[[(s*x,y,0,rx,rz) for y,x,rx,rz in SLEEVE] for s in [-1,1]]
union_garment('Jacket continuous native bake',lofts,'jacket')
PELVIS=[(0,.815,-.005,.14,.102),(0,.89,-.005,.177,.116),(0,.97,-.006,.175,.11),(0,1.015,-.006,.17,.105)]
LEG=[(.96,.09,0,.098,.109),(.86,.112,0,.105,.116),(.76,.116,-.003,.094,.105),(.63,.116,-.004,.081,.091),(.49,.115,.005,.068,.076),(.44,.115,.003,.072,.081),(.36,.115,-.008,.069,.081),(.23,.115,-.004,.057,.067),(.10,.115,0,.048,.057),(.075,.115,0,.049,.056)]
lofts=[PELVIS]+[[(s*x,y,z,rx,rz) for y,x,z,rx,rz in LEG] for s in [-1,1]]
union_garment('Trousers continuous native bake',lofts,'pants')
loft('Neck',[(0,1.43,0,.075,.065),(0,1.50,0,.060,.063),(0,1.57,.008,.063,.065),(0,1.60,.01,.067,.068)],'skin','neck',24,2)
profile=[(1.556,.054,.081,.047),(1.579,.076,.101,.062),(1.61,.096,.106,.079),(1.645,.112,.106,.102),(1.678,.124,.109,.114),(1.710,.126,.107,.119),(1.746,.121,.105,.117),(1.779,.108,.091,.105),(1.810,.078,.064,.079),(1.831,.014,.013,.014)]
from scipy.interpolate import PchipInterpolator
pr=np.array(profile);ys=np.linspace(pr[0,0],pr[-1,0],32);columns=[PchipInterpolator(pr[:,0],pr[:,j])(ys) for j in [1,2,3]]
p=[];f=[];seg=40
for y,rx,front,back in zip(ys,*columns):
 for k in range(seg):
  a=k*2*PI/seg;x=np.cos(a)*rx;sn=np.sin(a);z=sn*(front if sn>=0 else back)
  if sn>0:
   nose=.039*np.exp(-(x/.022)**2-((y-1.665)/.051)**2)+.008*np.exp(-(x/.025)**2-((y-1.646)/.012)**2)
   socket=-.013*sum(np.exp(-((x-s*.053)/.025)**2-((y-1.699)/.016)**2) for s in [-1,1])
   cheek=.007*sum(np.exp(-((x-s*.073)/.037)**2-((y-1.662)/.022)**2) for s in [-1,1]);z+=(nose+socket+cheek)*sn**4
  p.append([x,y,z])
for j in range(len(ys)-1):
 for i in range(seg):a=j*seg+i;b=j*seg+(i+1)%seg;f.extend([[a,b,b+seg],[a,b+seg,a+seg]])
for i in range(1,seg-1):f.extend([[0,i+1,i],[(len(ys)-1)*seg,(len(ys)-1)*seg+i,(len(ys)-1)*seg+i+1]])
add_mesh('Face original anatomical recipe',p,f,'skin','head')
for s in [-1,1]:
 ellipsoid('ear'+str(s),(s*.127,1.683,-.007),(.020,.037,.022),'skin','head')
 ellipsoid('earConcha'+str(s),(s*.143,1.682,.003),(.007,.021,.012),'lip','head',12,8)
 ellipsoid('eye'+str(s),(s*.050,1.697,.090),(.018,.0060,.014),'eye','head',20,10)
 ellipsoid('iris'+str(s),(s*.050,1.697,.103),(.0075,.0055,.002),'iris','head',16,10)
 ellipsoid('pupil'+str(s),(s*.050,1.697,.105),(.0029,.0031,.001),'pupil','head',12,8)
 ellipsoid('brow'+str(s),(s*.052,1.714,.101),(.026,.003,.004),'hair','head',16,8)
 ellipsoid('nostril'+str(s),(s*.016,1.644,.132),(.005,.0026,.0025),'lip','head',12,8)
ellipsoid('upperLip',(0,1.613,.107),(.031,.004,.004),'lip','head',20,8)
ellipsoid('lowerLip',(0,1.602,.107),(.028,.004,.004),'lip','head',20,8)
# Hair cap with small surface variation, without strand simulation.
p=[];f=[]
for j in range(12):
 t=j/11
 for i in range(40):
  a=i*PI/20;bound=1.733+.023*max(0,np.sin(a));y=bound+(1.839-bound)*t;r=np.sqrt(max(.0001,1-t*t));noise=1+.015*np.sin(a*12+t*9)
  p.append([np.cos(a)*.124*r*noise,y,np.sin(a)*.116*r*noise-.007])
for j in range(11):
 for i in range(40):a=j*40+i;b=j*40+(i+1)%40;f.extend([[a,b,b+40],[a,b+40,a+40]])
add_mesh('Hair',p,f,'hair','head')
for s in [-1,1]:
 k='L' if s<0 else 'R';cat='hand'+k;x=s*.305
 ellipsoid('palm'+k,(x,.793,.001),(.039,.052,.023),'skin',cat)
 for i in range(4):
  length=[.048,.060,.063,.053][i];ellipsoid('finger'+k+str(i),(x+(i-1.5)*.016,.750-length*.32,.006),(.008,length*.65,.009),'skin',cat,12,8)
 ellipsoid('thumb'+k,(x-s*.038,.785,.014),(.010,.037,.011),'skin',cat,12,8)
 ellipsoid('shoe'+k,(s*.115,.088,.068),(.073,.062,.155),'rubber','foot'+k,24,12)
 ellipsoid('sole'+k,(s*.115,.031,.071),(.075,.022,.160),'sole','foot'+k,24,10)
 for i in range(4):ellipsoid('lace'+k+str(i),(s*.115,.140-i*.005,.02+i*.024),(.038,.0025,.003),'sole','foot'+k,12,6)
loft('Collar',[(0,1.455,.004,.087,.078),(0,1.505,.003,.080,.071),(0,1.510,.003,.076,.068)],'jacket','neck',24,2)
for i in range(24):ellipsoid('zip'+str(i),(0,1.00+i*.017,.127),(.004,.004,.003),'metal','jacket',8,4)
for s in [-1,1]:ellipsoid('pocket'+str(s),(s*.112,1.12,.121),(.062,.003,.005),'hair','jacket',16,6)
# Quantized storage. Float32 decode happens once, expanded triangles avoid index extensions.
parts=[]
for name,chunks in GROUPS.items():
 if not chunks:continue
 data=np.concatenate(chunks);binary=bytearray()
 for row in data:
  pos=np.round(row[:3]*10000).astype(int);normal=np.clip(np.round(row[3:6]*32767),-32767,32767).astype(int);uv=np.clip(np.round(row[6:8]*65535),0,65535).astype(int)
  joints=row[8:12].astype(int);w=np.round(row[12:16]*255).astype(int);w[0]+=255-int(sum(w))
  binary.extend(struct.pack('<6h2H8B',*pos,*normal,*uv,*joints,*w))
 color,material=MATERIALS[name];parts.append({'name':name,'color':color,'material':material,'vertices':len(data),'data':base64.b64encode(binary).decode()})
meta={'version':1,'stride':24,'positionScale':10000,'bones':[n for n,_,_ in BONES],'parts':parts,'provenance':'Native reconstruction from the original DC Higgsfield metric recipe, not imported GLB topology.'}
(ROOT/'src/hero-asset.js').write_text('/* Original build-time baked geometry. */\nDC.HeroAsset='+json.dumps(meta,separators=(',',':'))+';\n')
report={'triangles':sum(x['vertices']//3 for x in parts),'parts':[{k:v for k,v in p.items() if k!='data'} for p in parts],'components':METRICS,'recipe_higgsfield_project':'bea56607-3eea-4526-abc9-b546a4717f10','integration':'Native reconstruction with same metric recipes, custom weights; source GLB separate.'}
(ROOT/'assets/hero-native-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'triangles':report['triangles'],'parts':len(parts),'source_bytes':(ROOT/'src/hero-asset.js').stat().st_size}))
