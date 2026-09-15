#!/usr/bin/env python3
"""Export the actual native geometry, not the remote Higgsfield GLB.

Build-only dependencies: Python/numpy/scipy and Node. Exported GLB files are
optional authoring assets and are NOT fetched by the offline game. Skin poses
are sampled from the native controller, not motion capture. Materials are the
portable PBR approximation of the game's procedural shaders.
"""
from pathlib import Path
import json,subprocess,struct,base64,math
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]
JS=r'''
const fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','character-motion','skin-rig','hero-asset','visual-geometry'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const defs=[['Idle',{},4],['Walk',{moveSpeed:3.3},Math.PI*2/(3.3*4.8)],['Run',{moveSpeed:6.2,sprintBlend:1},Math.PI*2/(6.2*2.7)],['Crouch',{crouch:1},3],['Carry',{carry:'crate',reach:.8},3]];
const clips=defs.map(([name,state,duration])=>{const frames=[];const count=Math.max(18,Math.ceil(duration*30));for(let i=0;i<=count;i++){
 const t=i/count,pose=DC.SkinRig.pose({...state,walk:name==='Walk'||name==='Run'?t*Math.PI*2:0},t*duration);
 frames.push({time:t*duration,palette:Array.from(pose.matrices),rootY:pose.rootY});}
 frames.at(-1).palette=frames[0].palette;frames.at(-1).rootY=frames[0].rootY;
 return{name,frames};});
console.log(JSON.stringify({hero:DC.HeroAsset,bones:DC.SkinRig.bones,geometry:DC.VisualGeometry.build(),clips}));
'''
D=json.loads(subprocess.check_output(['node','-e',JS],cwd=ROOT))
class GLB:
 def __init__(self,name):
  self.doc={'asset':{'version':'2.0','generator':'Distrito Cero native exporter v0.5','copyright':'Original Distrito Cero geometry'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'children':[]}],'meshes':[],'materials':[],'buffers':[{'byteLength':0}],'bufferViews':[],'accessors':[], 'extras':{'provenance':'Native reconstruction using original metric recipes also authored in Higgsfield. Not the remote GLB.','units':'metres, +Y up, +Z forward'}};self.binary=bytearray()
 def accessor(self,array,kind,ctype=5126,target=None,normalized=False):
  dtype={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[ctype];a=np.asarray(array,dtype=dtype)
  self.binary.extend(b'\0'*((-len(self.binary))%4));v={'buffer':0,'byteOffset':len(self.binary),'byteLength':a.nbytes}
  if target:v['target']=target
  vi=len(self.doc['bufferViews']);self.doc['bufferViews'].append(v);self.binary.extend(a.tobytes())
  ac={'bufferView':vi,'componentType':ctype,'count':len(a),'type':kind}
  if normalized:ac['normalized']=True
  if kind=='VEC3' and target==34962 or kind=='SCALAR' and ctype==5126:
   ac['min']=np.atleast_1d(a.min(axis=0)).astype(float).tolist();ac['max']=np.atleast_1d(a.max(axis=0)).astype(float).tolist()
  idx=len(self.doc['accessors']);self.doc['accessors'].append(ac);return idx
 def material(self,name,color,rough=.75,metal=0):
  i=len(self.doc['materials']);self.doc['materials'].append({'name':name,'pbrMetallicRoughness':{'baseColorFactor':[*color,1],'metallicFactor':metal,'roughnessFactor':rough}});return i
 def mesh(self,name,rows,indices,material,skin=False):
  a=np.asarray(rows,dtype=float);attrs={'POSITION':self.accessor(a[:,:3],'VEC3',target=34962),'NORMAL':self.accessor(a[:,3:6],'VEC3',target=34962),'TEXCOORD_0':self.accessor(a[:,6:8],'VEC2',target=34962)}
  if skin:
   attrs['JOINTS_0']=self.accessor(a[:,8:12],'VEC4',5121,34962)
   attrs['WEIGHTS_0']=self.accessor(a[:,12:16],'VEC4',5121,34962,True)
  ix=self.accessor(indices,'SCALAR',5123 if len(a)<65536 else 5125,34963)
  mi=len(self.doc['meshes']);self.doc['meshes'].append({'name':name,'primitives':[{'attributes':attrs,'indices':ix,'material':material,'mode':4}]});return mi
 def node(self,name,mesh=None,**kwargs):
  n={'name':name,**kwargs}
  if mesh is not None:n['mesh']=mesh
  i=len(self.doc['nodes']);self.doc['nodes'].append(n);self.doc['nodes'][0]['children'].append(i);return i
 def write(self,path):
  self.doc['buffers'][0]['byteLength']=len(self.binary);self.binary.extend(b'\0'*((-len(self.binary))%4))
  text=json.dumps(self.doc,separators=(',',':'),ensure_ascii=False).encode();text+=b' '*((-len(text))%4)
  data=struct.pack('<4sII',b'glTF',2,28+len(text)+len(self.binary))+struct.pack('<II',len(text),0x4e4f534a)+text+struct.pack('<II',len(self.binary),0x004e4942)+self.binary
  path.write_bytes(data);return {'file':path.name,'bytes':len(data),'meshes':len(self.doc['meshes']),'nodes':len(self.doc['nodes']),'animations':len(self.doc.get('animations',[]))}

def hero():
 g=GLB('DC05 native protagonist');bones=D['bones'];ids={b[0]:i+1 for i,b in enumerate(bones)}
 for name,parent,bind in bones:
  pb=np.array(bones[ids[parent]-1][2]) if parent else np.zeros(3)
  g.doc['nodes'].append({'name':name,'translation':(np.array(bind)-pb).tolist(),'children':[]})
 for i,(_,parent,_) in enumerate(bones):g.doc['nodes'][ids[parent] if parent else 0]['children'].append(i+1)
 ibm=[]
 for _,_,p in bones:
  m=np.eye(4);m[:3,3]=-np.array(p);ibm.append(m.T.reshape(16))
 g.doc['skins']=[{'name':'DC original 17-joint rig','joints':list(range(1,18)),'skeleton':1,'inverseBindMatrices':g.accessor(ibm,'MAT4')}]
 for part in D['hero']['parts']:
  raw=base64.b64decode(part['data']);rows=[];indices=[];lookup={}
  for off in range(0,len(raw),24):
   block=raw[off:off+24]
   if block not in lookup:
    v=struct.unpack('<6h2H8B',block);norm=np.array(v[3:6],float);norm/=np.linalg.norm(norm)
    row=[x/10000 for x in v[:3]]+norm.tolist()+[x/65535 for x in v[6:8]]+list(v[8:16]);lookup[block]=len(rows);rows.append(row)
   indices.append(lookup[block])
  rough={30:.55,31:.86,32:.91,33:.84,34:.16,3:.32,4:.82}.get(part['material'],.75)
  mat=g.material(part['name'],part['color'],rough,.8 if part['material']==3 else 0)
  g.node('HERO_'+part['name'],g.mesh(part['name'],rows,indices,mat,True),skin=0)
 g.doc['animations']=[]
 for clip in D['clips']:
  frames=clip['frames'];ta=g.accessor([f['time'] for f in frames],'SCALAR');animation={'name':clip['name']+' procedural','samplers':[],'channels':[]}
  quats=[[] for _ in bones]
  for f in frames:
   world=[]
   for i,(_,parent,bind) in enumerate(bones):
    m=np.array(f['palette'][i*16:(i+1)*16]).reshape(4,4).T
    b=np.eye(4);b[:3,3]=bind;world.append(m@b)
    local=np.linalg.inv(world[ids[parent]-1])@world[i] if parent else world[i]
    q=Rotation.from_matrix(local[:3,:3]).as_quat()
    if quats[i] and np.dot(q,quats[i][-1])<0:q=-q
    quats[i].append(q.tolist())
  for i,qs in enumerate(quats):
   oa=g.accessor(qs,'VEC4');j=len(animation['samplers']);animation['samplers'].append({'input':ta,'output':oa,'interpolation':'LINEAR'});animation['channels'].append({'sampler':j,'target':{'node':i+1,'path':'rotation'}})
  oa=g.accessor([[0,f['rootY'],0] for f in frames],'VEC3');j=len(animation['samplers']);animation['samplers'].append({'input':ta,'output':oa,'interpolation':'LINEAR'});animation['channels'].append({'sampler':j,'target':{'node':0,'path':'translation'}})
  g.doc['animations'].append(animation)
 return g.write(ROOT/'assets/dc05-hero-native.glb')

def car():
 g=GLB('DC05 native coupe geometry kit');color=g.material('Petrol enamel',[.055,.20,.24],.26,.58);glass=g.material('Smoked glass',[.028,.069,.095],.10,.28);rubber=g.material('Rubber',[.018,.023,.028],.84);alloy=g.material('Brushed alloy',[.35,.4,.44],.32,.8)
 g.doc['extras']['scope']='Body, glazing, curved roof and shared wheel geometry. Small runtime trim parts remain procedural in the game.'
 mi={}
 for name in ['coupe','roof','glassFront','glassRear','glassLeft','glassRight','tire','rim']:
  a=np.array(D['geometry'][name]).reshape(-1,8).astype(np.float32);unique,inv=np.unique(a,return_inverse=True,axis=0);mat=glass if name.startswith('glass') else rubber if name=='tire' else alloy if name=='rim' else color;mi[name]=g.mesh(name,unique,inv,mat)
  if name not in ('tire','rim'):g.node(name,mi[name])
 for side in [-1,1]:
  for z in [-1.39,1.36]:
   label=('left' if side<0 else 'right')+('_front' if z>0 else '_rear')
   g.node('wheel_'+label,mi['tire'],translation=[side*.92,.365,z],scale=[.27,.73,.73])
   g.node('rim_'+label,mi['rim'],translation=[side*1.052,.365,z],scale=[.025,.528,.528])
 return g.write(ROOT/'assets/dc05-coupe-native.glb')
if __name__=='__main__':
 report=[hero(),car()];(ROOT/'assets/native-exports.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
