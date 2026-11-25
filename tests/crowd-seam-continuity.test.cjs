'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{test}=require('node:test');
const root=path.resolve(__dirname,'..');
for(const name of ['core','character-fit','character-motion','skin-rig','dual-quaternion','hero-asset','crowd-geometry'])
 vm.runInThisContext(fs.readFileSync(path.join(root,'src',name+'.js'),'utf8'));
DC.Renderer=class{};DC.Simulation=class{};
for(const name of ['realism-renderer','appearance'])vm.runInThisContext(fs.readFileSync(path.join(root,'src',name+'.js'),'utf8'));
const hash=data=>crypto.createHash('sha256').update(Buffer.from(data.buffer,data.byteOffset,data.byteLength)).digest('hex');
const geometry=data=>data.filter((_,i)=>i%16!==6&&i%16!==7);
const face=DC.HeroAsset.parts.find(p=>p.name==='face'),source=DC.Realism.decode(face),metadata=Buffer.from(face.lodClusterUV,'base64');
const clusterUV=Uint16Array.from({length:face.vertices},(_,i)=>metadata.readUInt16LE(i*2));
const options={preserveUV:true,clusterUV};
const neck=p=>Math.abs(p[0])<.035&&p[1]>1.455&&p[1]<1.635&&p[2]<-.02;
function posteriorBoundaryCount(data,transform=p=>p){
 const points=new Map(),edges=new Map(),cache=new Map();
 for(let i=0;i<data.length;i+=48){const ids=[],regional=[];
  for(let k=0;k<3;k++){
   const o=i+k*16,p=Array.from(data.slice(o,o+3)),tuple=[...data.slice(o,o+6),...data.slice(o+8,o+16)].join(':');
   let moved=cache.get(tuple);if(!moved){moved=transform(p,data.slice(o+8,o+12),data.slice(o+12,o+16));assert.ok(moved.every(Number.isFinite));cache.set(tuple,moved);}
   const key=moved.join(':');if(!points.has(key))points.set(key,points.size);ids.push(points.get(key));regional.push(neck(p));
  }
  for(let k=0;k<3;k++){
   const a=ids[k],b=ids[(k+1)%3],key=a<b?a+':'+b:b+':'+a;
   const edge=edges.get(key)||{count:0,neck:regional[k]&&regional[(k+1)%3]};edge.count++;edges.set(key,edge);
  }
 }
 return [...edges.values()].filter(e=>e.count===1&&e.neck).length;
}
function fixture(){
 const p=[[0,0,0],[1,0,0],[0,1,0],[0,0,0],[-1,0,0],[0,-1,0],[.02,0,0],[1,1,0],[-1,1,0]];
 const uv=[[.01,.01],[.3,.01],[.01,.3],[.9,.9],[.6,.9],[.9,.6],[.02,.01],[.3,.3],[.01,.3]];
 return {data:new Float32Array(p.flatMap((point,i)=>[...point,0,0,1,...uv[i],4,3,0,0,1,0,0,0])),
  clusterUV:new Uint16Array([0,0,0,32,32,32,0,0,0])};
}
test('welding closes a UV-only seam without blending separate atlas islands or mutating inputs',()=>{
 const {data,clusterUV}=fixture(),before=Float32Array.from(data),legacy=DC.CrowdGeometry.reduce(data,.1,{preserveUV:true,clusterUV});
 assert.notEqual(legacy[0],legacy[3*16]);
 const out=DC.CrowdGeometry.reduce(data,.1,{preserveUV:true,clusterUV,weldUVSeams:true});
 assert.deepEqual(geometry(out.slice(0,16)),geometry(out.slice(3*16,4*16)));
 assert.deepEqual(out.slice(6,8),data.slice(6,8));assert.deepEqual(out.slice(3*16+6,3*16+8),data.slice(3*16+6,3*16+8));
 assert.deepEqual(data,before);assert.ok(DC.SkinRig.validate(out));
});
test('different normals, positions, joint order, zero-weight IDs or weights do not authorize welding',()=>{
 for(const kind of ['normal','position','joint-order','zero-weight-id','weights']){
  const {data,clusterUV}=fixture(),o=3*16;
  if(kind==='normal')data.set([0,1,0],o+3);
  if(kind==='position')data[o]=.00001;
  if(kind==='joint-order')data.set([4,0,3,0],o+8);
  if(kind==='zero-weight-id')data[o+10]=5;
  if(kind==='weights')data.set([.75,.25,0,0],o+12);
  const args={preserveUV:true,clusterUV},legacy=DC.CrowdGeometry.reduce(data,.1,args),out=DC.CrowdGeometry.reduce(data,.1,{...args,weldUVSeams:true});
  assert.equal(hash(geometry(out)),hash(geometry(legacy)),kind);assert.notEqual(out[0],out[o],kind);
 }
});
test('seam welding is explicit and requires UV preservation',()=>{
 const {data}=fixture();
 assert.throws(()=>DC.CrowdGeometry.reduce(data,.1,{weldUVSeams:true}),/seam|UV/i);
 assert.throws(()=>DC.CrowdGeometry.reduce(data,.1,{preserveUV:true,weldUVSeams:'true'}),/seam|UV/i);
 assert.deepEqual(DC.CrowdGeometry.reduce(data,.1,{weldUVSeams:false}),DC.CrowdGeometry.reduce(data,.1));
});
test('actual posterior neck boundary improves from 22 to zero with finite normalized output and zero collapsed UVs',()=>{
 const before=hash(source),legacy=DC.CrowdGeometry.reduce(source,.025*.65,options);
 assert.equal(posteriorBoundaryCount(source),0);assert.equal(posteriorBoundaryCount(legacy),22,'fixed RED cohort');
 for(const [cell,triangles]of [[.009*.65,6229],[.025*.65,3645]]){
  const out=DC.CrowdGeometry.reduce(source,cell,{...options,weldUVSeams:true});
  assert.equal(out.length/48,triangles);assert.equal(posteriorBoundaryCount(out),0);assert.ok(DC.SkinRig.validate(out));
  assert.ok(out.every(Number.isFinite));
  for(let i=0;i<out.length;i+=48){const det=(out[i+22]-out[i+6])*(out[i+39]-out[i+7])-(out[i+38]-out[i+6])*(out[i+23]-out[i+7]);assert.notEqual(det,0);}
 }
 assert.equal(hash(source),before);
});
test('welded neck remains closed under native CPU DQ cervical poses and all benchmark profiles',()=>{
 const out=DC.CrowdGeometry.reduce(source,.025*.65,{...options,weldUVSeams:true});
 const profiles=JSON.parse(fs.readFileSync(path.join(root,'tests/benchmarks/characters.json'),'utf8')).profiles;
 for(const [name,look]of Object.entries(profiles))for(const pose of [{},{lookYaw:-.7},{lookYaw:.7},{lookPitch:-.35,lookRoll:.15},{lookPitch:.35,lookRoll:-.15}]){
  const drop=DC.CharacterFit.drop(look.neckLength||0),palette=DC.DualQuaternion.pack(DC.SkinRig.pose({...pose,neckDrop:drop},1).matrices);
  const count=posteriorBoundaryCount(out,(p,j,w)=>DC.DualQuaternion.transform(palette,
   DC.CharacterFit.point(DC.Appearance.shapePoint(p,40,look.build,look.face,look.neck||0),drop),j,w));
  assert.equal(count,0,name+' '+JSON.stringify(pose));
 }
});
