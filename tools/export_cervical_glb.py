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
from PIL import Image
import io
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[1]
JS=r'''
const fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','character-motion','skin-rig','hero-asset','visual-geometry'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const defs=[['Idle',{},4],['Walk',{moveSpeed:1.4},Math.PI*2/DC.NaturalMotion.frequency(1.4)],['Run',{moveSpeed:6.2,sprintBlend:1},Math.PI*2/DC.NaturalMotion.frequency(6.2,1)],['Crouch',{crouch:1},3],['Carry',{carry:'crate',reach:.8},3],['HandRelaxed',{grip:0},2],['HandGrip',{grip:1},2],['Seated',{seated:true,y:-.29,handTargets:{L:{x:-.157,y:1.019,z:.43},R:{x:.157,y:1.019,z:.43}}},3],['Reach',{reach:1,handTargets:{R:{x:.34,y:1.26,z:.36}}},3],['NeckTurn',{},6],['NeckNod',{},4]];
const clips=defs.map(([name,state,duration])=>{const frames=[];const count=Math.max(18,Math.ceil(duration*30));for(let i=0;i<=count;i++){
 const t=i/count,pose=DC.SkinRig.pose({...state,...(name==='NeckTurn'?{lookYaw:Math.sin(t*Math.PI*2)*.72}:name==='NeckNod'?{lookPitch:Math.sin(t*Math.PI*2)*.22}:{}),walk:name==='Walk'||name==='Run'?t*Math.PI*2:0},t*duration);
 frames.push({time:t*duration,palette:Array.from(pose.matrices),rootY:pose.rootY});}
 frames.at(-1).palette=frames[0].palette;frames.at(-1).rootY=frames[0].rootY;
 return{name,frames};});
console.log(JSON.stringify({hero:DC.HeroAsset,bones:DC.SkinRig.bones,geometry:DC.VisualGeometry.build(),clips}));
'''
D=json.loads(subprocess.check_output(['node','-e',JS],cwd=ROOT))
class GLB:
 def __init__(self,name):
  self.doc={'asset':{'version':'2.0','generator':'Distrito Cero anatomy exporter v0.14','copyright':'MakeHuman HM08 and adult target CC0; Aksel Skin by Mindfront CC0; original Distrito Cero garments, eyes, groom and animation'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':name,'children':[]}],'meshes':[],'materials':[],'buffers':[{'byteLength':0}],'bufferViews':[],'accessors':[], 'extras':{'provenance':'Actual native runtime geometry. Head derived from MakeHuman HM08 CC0. Skin derived from Aksel Skin by Mindfront CC0. Procedural shader details and paired vehicle animations are not portable clips.','units':'metres, +Y up, +Z forward'}};self.binary=bytearray()
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
 g=GLB('DC013 movement and surface');bones=D['bones'];ids={b[0]:i+1 for i,b in enumerate(bones)}
 for name,parent,bind in bones:
  pb=np.array(bones[ids[parent]-1][2]) if parent else np.zeros(3)
  g.doc['nodes'].append({'name':name,'translation':(np.array(bind)-pb).tolist(),'children':[]})
 for i,(_,parent,_) in enumerate(bones):g.doc['nodes'][ids[parent] if parent else 0]['children'].append(i+1)
 ibm=[]
 for _,_,p in bones:
  m=np.eye(4);m[:3,3]=-np.array(p);ibm.append(m.T.reshape(16))
 g.doc['skins']=[{'name':'DC 49-joint anatomical rig','joints':list(range(1,len(bones)+1)),'skeleton':1,'inverseBindMatrices':g.accessor(ibm,'MAT4')}]
 g.doc['images']=[];g.doc['textures']=[];g.doc['samplers']=[{'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':33071}]
 source=ROOT/'assets/anatomy-source'
 images=[Image.open(source/'skin-repaired.webp').convert('RGB'),Image.open(source/'normal.webp').convert('RGB'),Image.open(source/'roughness.webp').convert('L')]
 # glTF image UV origin is top-left. Flip V below and adjust normal tangent Y accordingly.
 normal=np.asarray(images[1]).copy();normal[:,:,1]=255-normal[:,:,1];images[1]=Image.fromarray(normal)
 orm=np.zeros((*np.asarray(images[2]).shape,3),dtype=np.uint8);orm[:,:,0]=255;orm[:,:,1]=np.asarray(images[2]);images[2]=Image.fromarray(orm)
 for i,im in enumerate(images):
  stream=io.BytesIO();im.save(stream,format='PNG',optimize=True);data=stream.getvalue();g.binary.extend(b'\0'*((-len(g.binary))%4))
  vi=len(g.doc['bufferViews']);g.doc['bufferViews'].append({'buffer':0,'byteOffset':len(g.binary),'byteLength':len(data)});g.binary.extend(data)
  g.doc['images'].append({'name':['CC0 Aksel rebaked albedo','CC0 Aksel rebaked normal','Derived roughness ORM'][i],'mimeType':'image/png','bufferView':vi});g.doc['textures'].append({'source':i,'sampler':0})
 for part in D['hero']['parts']:
  raw=base64.b64decode(part['data']);rows=[];indices=[];lookup={}
  for off in range(0,len(raw),24):
   block=raw[off:off+24]
   if block not in lookup:
    v=struct.unpack('<6h2H8B',block);norm=np.array(v[3:6],float);norm/=np.linalg.norm(norm)
    row=[x/10000 for x in v[:3]]+norm.tolist()+[x/65535 for x in v[6:8]]+list(v[8:16]);lookup[block]=len(rows);rows.append(row)
   indices.append(lookup[block])
  rough={30:.66,31:.83,32:.90,33:.67,34:.12,40:1,41:.19,42:.72,3:.32,4:.82,44:.56}.get(part['material'],.75)
  mat=g.material(part['name'],part['color'],rough,.8 if part['material']==3 else 0)
  if part['material']==40:
   for row in rows:row[7]=1-row[7]
   m=g.doc['materials'][mat];m['pbrMetallicRoughness'].update({'baseColorTexture':{'index':0},'metallicRoughnessTexture':{'index':2},'metallicFactor':0});m['normalTexture']={'index':1,'scale':.30}
  if part['material'] in (33,42):g.doc['materials'][mat]['doubleSided']=True
  g.node('HERO_'+part['name'],g.mesh(part['name'],rows,indices,mat,True),skin=0)
 g.doc['animations']=[]
 for clip in D['clips']:
  frames=clip['frames'];ta=g.accessor([f['time'] for f in frames],'SCALAR');animation={'name':clip['name']+' procedural','samplers':[],'channels':[]}
  quats=[[] for _ in bones];translations=[[] for _ in bones]
  for f in frames:
   world=[]
   for i,(_,parent,bind) in enumerate(bones):
    m=np.array(f['palette'][i*16:(i+1)*16]).reshape(4,4).T
    b=np.eye(4);b[:3,3]=bind;world.append(m@b)
   for i,(_,parent,bind) in enumerate(bones):
    local=np.linalg.inv(world[ids[parent]-1])@world[i] if parent else world[i]
    q=Rotation.from_matrix(local[:3,:3]).as_quat()
    if quats[i] and np.dot(q,quats[i][-1])<0:q=-q
    quats[i].append(q.tolist());translations[i].append(local[:3,3].tolist())
  for i,qs in enumerate(quats):
   oa=g.accessor(qs,'VEC4');j=len(animation['samplers']);animation['samplers'].append({'input':ta,'output':oa,'interpolation':'LINEAR'});animation['channels'].append({'sampler':j,'target':{'node':i+1,'path':'rotation'}})
  for i,ts in enumerate(translations):
   oa=g.accessor(ts,'VEC3');j=len(animation['samplers']);animation['samplers'].append({'input':ta,'output':oa,'interpolation':'LINEAR'});animation['channels'].append({'sampler':j,'target':{'node':i+1,'path':'translation'}})
  oa=g.accessor([[0,f['rootY'],0] for f in frames],'VEC3');j=len(animation['samplers']);animation['samplers'].append({'input':ta,'output':oa,'interpolation':'LINEAR'});animation['channels'].append({'sampler':j,'target':{'node':0,'path':'translation'}})
  g.doc['animations'].append(animation)
 g.doc['extras']['limitations']='The game uses native dual-quaternion skinning. Standard glTF viewers generally use linear blend skinning, so posed deformation is not identical. Native vertex blink, gaze, scalp stipple, crowd morphology, microdetail and neck blend are runtime-only. Material appearance is portable approximation; no motion capture or physical cloth.'
 return g.write(ROOT/'assets/dc014-human-cervical.glb')

if __name__=='__main__':
 report=hero();(ROOT/'assets/cervical-export.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
