#!/usr/bin/env python3
"""v0.10: licensed MakeHuman HM08 anatomy, baked skin maps and original garments.
Build inputs and CC0 provenance are in assets/anatomy-source. No network at build
time or runtime. Extends the native skeleton to 49 bones with shared landmarks and context-aware grip.
"""
import base64, json, struct, hashlib, lzma, subprocess
import body_authoring as BODY
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from skimage.measure import marching_cubes
ROOT=Path(__file__).resolve().parents[1]
PI=np.pi
# One bind-pose contract: runtime and generator consume the same landmarks.
JSS="const fs=require('fs'),vm=require('vm');for(const n of ['core','character-motion','skin-rig'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));console.log(JSON.stringify({bones:DC.SkinRig.bones,ids:DC.SkinRig.ids,fingers:DC.SkinRig.fingers}));"
RIG=json.loads(subprocess.check_output(['node','-e',JSS],cwd=ROOT))
BONES=RIG['bones'];IDS=RIG['ids']
MATERIALS={
 'jacket':([.105,.165,.155],31), 'pants':([.048,.065,.081],32),
 'skin':([.48,.30,.205],30), 'face':([1,1,1],40), 'hair':([.047,.031,.020],33), 'scalp':([.037,.023,.015],42),
 'rubber':([.022,.027,.032],4),'sole':([.14,.155,.15],0),
 'metal':([.40,.43,.42],3),'eye':([.54,.50,.43],34),'iris':([.11,.066,.029],41),
 'nails':([.405,.290,.236],44),'pupil':([.009,.009,.008],34),'lip':([.32,.15,.105],30)}
GROUPS={k:[] for k in MATERIALS}
METRICS={}
def blend(a,b,t):
 t=float(np.clip(t,0,1));t=t*t*(3-2*t);return {a:1-t,b:t}
def weights(cat,p):
 x,y,z=p;k='L' if x<0 else 'R'
 if cat=='anatomical':return blend('neck','head',(y-1.51)/.085) if y<1.595 else {'head':1}
 if cat=='head':return {'head':1}
 if cat=='neck':return blend('chest','head',(y-1.47)/.14)
 if cat.startswith('hand'):return BODY.hand_weights(p,cat[-1],RIG)
 if cat.startswith('foot'):return {'foot'+cat[-1]:1}
 if cat in ('jacket','pants'):return BODY.garment_weights(cat,p,RIG)
 return {'pelvis':1}
def add_mesh(name,verts,faces,material,cat,normals=None,texture_uv=None):
 v=np.asarray(verts,float);f=np.asarray(faces,int)
 # Consistent outward winding for closed geometry; leaves are not part of this bake.
 volume=np.einsum('ij,ij->i',v[f[:,0]],np.cross(v[f[:,1]],v[f[:,2]])).sum()/6
 if volume<0:f=f[:,[0,2,1]]
 if normals is None:
  normals=np.zeros_like(v);ns=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
  for j in range(3):np.add.at(normals,f[:,j],ns)
  normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
 rows=[]
 for index,(point,n) in enumerate(zip(v,normals)):
  entries=sorted(weights(cat,point).items(),key=lambda t:t[1],reverse=True)[:4];total=sum(w for _,w in entries)
  joints=[IDS[name] for name,_ in entries]+[0]*(4-len(entries));ws=[w/total for _,w in entries]+[0]*(4-len(entries))
  # Store cylindrical-ish coordinates for procedural weave/freckles, not image textures.
  uv=list(texture_uv[index]) if texture_uv is not None else [np.arctan2(point[2],point[0])/PI*.5+.5,float(point[1]/1.9)]
  point=point.copy();n=n.copy()
  if cat=='head':
   point[0]*=.72;point[1]=1.60+(point[1]-1.63)*.98;point[2]*=.87;n/=np.array([.72,.98,.87])
  elif cat in ('jacket','neck'):
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
def union_garment(name,lofts,material,step=.014):
 from scipy.interpolate import PchipInterpolator
 lo=np.array([-.41,.04,-.18]) if material=='pants' else np.array([-.41,.80,-.18]);hi=np.array([.41,1.04,.18]) if material=='pants' else np.array([.41,1.53,.18])
 axes=[np.arange(lo[i],hi[i]+step,step) for i in range(3)];x,y,z=np.meshgrid(*axes,indexing='ij');field=np.ones_like(x)*10
 for rings in lofts:
  r=np.asarray(sorted(rings,key=lambda t:t[1]));clipped=np.clip(y,r[0,1],r[-1,1]);x0,z0,rx,rz=[PchipInterpolator(r[:,1],r[:,j])(clipped) for j in [0,2,3,4]]
  # Front/back depth differ around chest, scapula and seat. Authoring approximation.
  if material=='jacket':rz=rz*np.where(z>=z0,1.0+.045*np.exp(-((clipped-1.29)/.12)**2),1.0)
  else:rz=rz*np.where(z<z0,1+.075*np.exp(-((clipped-.885)/.085)**2),.96)
  # SDF approximation of an elliptical loft with end caps, clipped union.
  f=(np.sqrt(((x-x0)/rx)**2+((z-z0)/rz)**2)-1)*np.minimum(rx,rz)
  f=np.maximum(f,np.maximum(r[0,1]-y,y-r[-1,1]));field=np.minimum(field,f)
 field=gaussian_filter(field,.56)
 v,f,_,_=marching_cubes(field,0,spacing=(step,step,step),allow_degenerate=False);v+=lo
 # Rounded cloth contours and restrained physical-sized folds near elbows/knees/waist.
 for i,point in enumerate(v):
  xx,yy,zz=point
  if material=='jacket':fold=np.exp(-((yy-1.115)/.12)**2)+.5*np.exp(-((yy-1.0)/.07)**2)
  else:fold=np.exp(-((yy-.48)/.085)**2)+.4*np.exp(-((yy-.16)/.045)**2)
  angle=np.arctan2(zz,xx if material=='jacket' else xx-np.sign(xx)*.115)
  point[2]+=.0028*fold*(np.sin(yy*78+xx*26)+.45*np.sin(yy*131-xx*41))*np.sin(angle)
 add_mesh(name,v,f,material,material)
TORSO=BODY.TORSO;SLEEVE=BODY.SLEEVE;PELVIS=BODY.PELVIS;LEG=BODY.LEG
lofts=[TORSO]+[[(s*x,y,0,rx,rz) for y,x,rx,rz in SLEEVE] for s in [-1,1]]
union_garment('Tailored torso, scapula and sleeves',lofts,'jacket')
lofts=[PELVIS]+[[(s*x,y,z,rx,rz) for y,x,z,rx,rz in LEG] for s in [-1,1]]
union_garment('Anatomical hip, thigh and calf clothing',lofts,'pants')

# Anatomical head: mirror the symmetric source half and weld the midsagittal seam.
# The transport is delta-coded LZMA, decoded here only. Runtime receives standard baked vertices.
source=ROOT/'assets/anatomy-source'
raw=lzma.decompress((source/'head.xz').read_bytes());nv,nf=struct.unpack_from('<II',raw)
half=np.cumsum(np.frombuffer(raw,dtype='<i2',count=nv*3,offset=8).reshape(-1,3).astype(np.int32),axis=0)/10000
quads=np.cumsum(np.frombuffer(raw,dtype='<i2',offset=8+nv*6).astype(np.int32)).reshape(-1,4)
assert len(quads)==nf and np.isfinite(half).all() and quads.max()<nv
v=half.tolist();mirror={}
for i,p in enumerate(half):
 if abs(p[0])<.00005:mirror[i]=i
 else:mirror[i]=len(v);v.append([-p[0],p[1],p[2]])
qs=quads.tolist()+[[mirror[int(i)] for i in face[::-1]] for face in quads]
from collections import Counter
edgecount=Counter(tuple(sorted((a,b))) for q in qs for a,b in zip(q,q[1:]+q[:1]))
edge=[(a,b)for a,b in edgecount if edgecount[(a,b)]==1 and max(v[a][1],v[b][1])<1.56]
ring={i:i for e in edge for i in e};initial={i:np.array(v[i]) for i in ring}
for j in range(1,5):
 new={}
 for i,origin in initial.items():
  t=j/4;rad=np.hypot(origin[0],origin[2]+.01);target=np.array([origin[0]/rad*.047,1.475,(origin[2]+.01)/rad*.049-.01]);pt=origin*(1-t)+target*t
  new[i]=len(v);v.append(pt.tolist())
 for a,b in edge:
  q=[ring[a],ring[b],new[b],new[a]];qp=np.array([v[i] for i in q]);qn=np.cross(qp[1]-qp[0],qp[2]-qp[0]);out=qp.mean(0)-[0,qp[:,1].mean(),-.01]
  if np.dot(qn,out)<0:q=q[::-1]
  qs.append(q)
 ring=new
v=np.array(v);tri=np.array([t for q in qs for t in [[q[0],q[1],q[2]],[q[0],q[2],q[3]]]])
ns=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]])
# The winding from HM08 is preserved; correct its entire orientation, not individual lips/ears.
if np.einsum('ij,ij->i',ns,v[tri].mean(axis=1)-[0,1.665,0]).sum()<0:tri=tri[:,[0,2,1]];ns=-ns
normal=np.zeros_like(v)
for j in range(3):np.add.at(normal,tri[:,j],ns)
normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-8)
# Tiny asymmetry in external contours, not eye placement. It survives all LODs.
head_vertices=v.copy();head_normals=normal.copy();head_triangles=tri.copy()
uv=np.column_stack((np.arctan2(v[:,0],v[:,2])/(2*PI)+.5,(v[:,1]-1.52)/.28))
vv=v[tri].reshape(-1,3);nn=normal[tri].reshape(-1,3);uu=uv[tri].copy()
for i,t in enumerate(tri):
 if np.ptp(uu[i,:,0])>.5:uu[i,uu[i,:,0]>.8,0]=0
# Flatten only the UV seam, so geometric normals remain welded.
add_mesh('MakeHuman HM08 adult head',vv,np.arange(len(vv)).reshape(-1,3),'face','anatomical',nn,uu.reshape(-1,2))
# Neck joins the licensed head below its open lower boundary and the jacket collar.
EYE_X=.0307781;EYE_Y=1.6708135;EYE_Z=.08760675
for side in [-1,1]:
 x=side*EYE_X
 ellipsoid('Sclera'+str(side),(x,EYE_Y,EYE_Z),(.0126,.0122,.0126),'eye','anatomical',32,18)
 # Iris curved into the sclera, not a protruding button. Black limbal ring buried under iris.
 ellipsoid('Limbal ring'+str(side),(x,EYE_Y,EYE_Z+.0119),(.0058,.0058,.0006),'pupil','anatomical',32,12)
 ellipsoid('Iris'+str(side),(x,EYE_Y,EYE_Z+.01240),(.00525,.00525,.00065),'iris','anatomical',32,14)
 ellipsoid('Pupil'+str(side),(x,EYE_Y,EYE_Z+.01303),(.0022,.0022,.00025),'pupil','anatomical',24,12)
# Sparse, surface-conforming eyebrow strokes retain pores and skin between hairs.
from scipy.spatial import cKDTree
forehead=v[(v[:,2]>.052)&(v[:,1]>1.671)&(v[:,1]<1.72)]
brow_tree=cKDTree(forehead[:,:2])
for side in [-1,1]:
 for i in range(55):
  t=i/54;x=side*(.013+t*.043);y=EYE_Y+.014+np.sin(t*PI)*.0045-t*.004
  ds,ix=brow_tree.query([x,y],k=5);wt=1/np.maximum(ds,.0005)**2;z=float((forehead[ix,2]*wt).sum()/wt.sum())+.0007
  h=.0022+.0013*np.sin(t*PI);w=.00030*(1-.5*t);p=[[x-w,y,z],[x+w,y,z],[x+side*.0012,y+h,z-.0001]]
  add_mesh('Eyebrow stroke '+str(side)+' '+str(i),p,[[0,1,2]],'hair','anatomical')
# Scalp fitting from anatomical surface samples. No unrelated ellipsoid through the cranium.
from scipy.spatial import cKDTree
C=np.array([0,1.68,-.012]);hp=v[v[:,1]>1.66];dirs=hp-C;radius=np.linalg.norm(dirs,axis=1);dirs/=radius[:,None];tree=cKDTree(dirs)
def scalp(phi,theta,lift=0):
 d=np.array([np.sin(theta)*np.sin(phi),np.cos(theta),np.sin(theta)*np.cos(phi)])
 dd,ix=tree.query(d,k=8);wt=1/np.maximum(dd,.003)**3
 r=float((radius[ix]*wt).sum()/wt.sum())
 # Positive millimetric separation; conservative outer envelope prevents scalp poke-through.
 r=max(r,float(radius[ix[0]]))+.0023+lift
 return C+d*r
p=[];f=[];uvh=[];SEG=96;BANDS=25
for j in range(BANDS):
 for i in range(SEG):
  phi=2*PI*i/SEG;end=1.39-.57*max(0,np.cos(phi))+.38*max(0,-np.cos(phi))+.025*np.sin(phi*3)
  theta=.012+(end-.012)*j/(BANDS-1);lift=.005*np.sin(theta*1.25)*(.65+.35*np.sin(phi))
  p.append(scalp(phi,theta,lift));uvh.append([i/SEG,j/(BANDS-1)])
for j in range(BANDS-1):
 for i in range(SEG):a=j*SEG+i;b=j*SEG+(i+1)%SEG;f.extend([[a,b,b+SEG],[a,b+SEG,a+SEG]])
add_mesh('Scalp fitted to HM08',p,f,'scalp','anatomical',texture_uv=uvh)
# Fine swept ribbon clusters add a broken silhouette. Static groom, not simulated strands.
rng=np.random.default_rng(291)
for idx in range(260):
 phi=rng.uniform(0,2*PI);end=1.39-.57*max(0,np.cos(phi))+.38*max(0,-np.cos(phi));theta=rng.uniform(.18,max(.2,end-.20));length=rng.uniform(.18,.45);width=rng.uniform(.007,.014)
 p=[];f=[];tc=[]
 for j in range(7):
  t=j/6;th=min(end+.027,theta+length*t);ph=phi+.11*np.sin(PI*t);w=width*(1-t*.93)
  for k in [-1,1]:p.append(scalp(ph+k*w,th,.003+.005*np.sin(PI*t)));tc.append([(k+1)/2,t])
 for j in range(6):a=j*2;f.extend([[a,a+1,a+3],[a,a+3,a+2]])
 add_mesh('Groom '+str(idx),p,f,'hair','anatomical',texture_uv=tc)
BODY.hand_meshes(add_mesh,RIG)
BODY.shoe_meshes(add_mesh,loft,ellipsoid)
loft('Collar',[(0,1.455,-.010,.071,.061),(0,1.504,-.010,.074,.071),(0,1.521,-.010,.070,.068)],'jacket','neck',24,2)
# Conform closure and pocket trim to the actual meshed front, not to a linear profile.
from scipy.spatial import cKDTree
front=GROUPS['jacket'][0];front=front[(front[:,5]>.38)&(np.abs(front[:,0])<.180)]
front=np.unique(np.round(front[:,:3],7),axis=0);front_tree=cKDTree(front[:,:2])
def front_surface(x,y):
 distance,indices=front_tree.query([x*.9,y],k=6);w=1/np.maximum(distance,.0001)**2
 return float(np.dot(front[indices,2],w)/w.sum())
# Recessed front closure follows the actual garment profile instead of floating in air.
for side in [-1,1]:
 rings=[]
 for y in np.linspace(.98,1.478,26):
  z=front_surface(side*.005,y)+.0009
  rings.append((side*.005,y,z,.0020,.0012))
 loft('Zip tape'+str(side),rings,'pants','jacket',8,1)
for i in range(40):
 y=.985+i*.0123;z=front_surface(0,y)+.0020
 ellipsoid('zip'+str(i),((-1 if i%2 else 1)*.0016,y,z),(.0017,.0014,.001),'metal','jacket',8,4)
ellipsoid('Zipper pull',(0,1.461,front_surface(0,1.461)+.005),(.004,.008,.002),'metal','jacket',10,6)
for side in [-1,1]:
 k='L'if side<0 else'R'
 loft('Rib cuff '+k,[(side*.293,.879,0,.035,.037),(side*.293,.895,0,.036,.038),(side*.293,.918,0,.036,.039)],'pants','jacket',24,2)
 # Pocket piping sunk into the cloth on a slightly slanted line.
 for j in range(12):
  x=side*(.071+j*.0063);y=1.11-j*.0024;z=front_surface(x,y)+.0017
  ellipsoid('Pocket piping '+k+str(j),(x,y,z),(.004,.0014,.0018),'pants','jacket',8,4)
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
meta={'version':2,'stride':24,'positionScale':10000,'bones':[n for n,_,_ in BONES],'parts':parts,'provenance':'MakeHuman HM08 CC0 anatomical head with adult target, Mindfront Aksel CC0 skin maps. Original v0.10 continuous articulated hands, tailored garments, shoe lasts, eyes and groom. Authoring tools only, no external runtime libraries.'}
(ROOT/'src/hero-asset.js').write_text('/* Licensed HM08 head plus original native garments. See assets/anatomy-source. */\nDC.HeroAsset='+json.dumps(meta,separators=(',',':'))+';\n')
report={'triangles':sum(x['vertices']//3 for x in parts),'parts':[{k:v for k,v in p.items() if k!='data'} for p in parts],'components':METRICS,'historical_recipe_project':'bea56607-3eea-4526-abc9-b546a4717f10','integration':'v0.10 (head preserved from v0.9): actual CC0 HM08 head subset integrated in native rig. Skin bake prepared through Higgsfield sandbox, not an AI scan.'}
(ROOT/'assets/hero-native-report.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'triangles':report['triangles'],'parts':len(parts),'source_bytes':(ROOT/'src/hero-asset.js').stat().st_size}))
