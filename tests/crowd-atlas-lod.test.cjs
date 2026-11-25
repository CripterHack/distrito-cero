'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const zlib=require('node:zlib');
const assert=require('node:assert/strict'),{test}=require('node:test');
const root=path.resolve(__dirname,'..');
for(const name of ['core','character-motion','skin-rig','crowd-geometry','hero-asset'])vm.runInThisContext(fs.readFileSync(path.join(root,'src',name+'.js'),'utf8'));
DC.Renderer=class {};
vm.runInThisContext(fs.readFileSync(path.join(root,'src/realism-renderer.js'),'utf8'));
const castSource=fs.readFileSync(path.join(root,'src/cast-renderer.js'),'utf8');
const hash=data=>crypto.createHash('sha256').update(Buffer.from(data.buffer,data.byteOffset,data.byteLength)).digest('hex');
const bins=data=>Uint16Array.from({length:data.length/16},(_,i)=>Math.floor(data[i*16+6]*32)+33*Math.floor(data[i*16+7]*32));
const geometry=data=>Float32Array.from(data.filter((_,i)=>i%16!==6&&i%16!==7));
function fixture(){
 const rows=[];
 for(const [uv,points]of [[[.1,.2],[[.001,0,0],[1,0,0],[0,1,0]]],[[.11,.21],[[.002,0,0],[-1,0,0],[0,1.001,0]]]])
  for(const p of points)rows.push(...p,0,0,1,...uv,4,3,0,0,.75,.25,0,0);
 const original=new Float32Array(rows),atlas=Float32Array.from(original);
 const uv=[[.01,.01],[.02,.01],[.01,.02],[.8,.8],[.9,.8],[.8,.9]];
 for(let i=0;i<uv.length;i++)atlas.set(uv[i],i*16+6);
 return {original,atlas,clusterUV:bins(original)};
}
function encodeBins(values){const b=Buffer.alloc(values.length*2);values.forEach((v,i)=>b.writeUInt16LE(v,i*2));return b.toString('base64');}
function castFixture(source,clusterUV){
 let decodes=0;const calls=[],part={name:'face',key:'hero_face',vertices:source.length/16,lodClusterUV:encodeBins(clusterUV)};
 const noop=()=>{},g=new Proxy({createTexture:()=>({}),createBuffer:()=>({})},{get:(target,key)=>target[key]??noop});
 class Base{
  constructor(){this.gl=g;this.heroParts=[{...part}];this.meshes={hero_face:{data:source},body:{}};this.static={};this.dynamic={};this.assetParts=[];this.visualStats={};}
  createSkinMesh(data){return {data};}createMesh(){return {};}deleteMesh(){}
 }
 const D={...DC,Renderer:Base,HeroAsset:{parts:[part]},Realism:{decode:()=>source},MotionTracker:class{},
  CrowdGeometry:{reduce(data,cell,options){calls.push(options);return DC.CrowdGeometry.reduce(data,cell,options);}}};
 vm.runInNewContext(castSource,{DC:D,Float32Array,Uint16Array,atob(value){decodes++;return Buffer.from(value,'base64').toString('binary');}});
 return {renderer:new D.CastRenderer(),calls,decodes};
}

test('atlas UVs retain legacy cluster geometry and each retained corner UV',()=>{
 const {original,atlas,clusterUV}=fixture(),before=Float32Array.from(atlas);
 const baseline=DC.CrowdGeometry.reduce(original,.1,{preserveUV:true});
 const result=DC.CrowdGeometry.reduce(atlas,.1,{preserveUV:true,clusterUV});
 assert.deepEqual(geometry(result),geometry(baseline));
 for(let i=0;i<result.length;i+=16)assert.deepEqual(result.slice(i+6,i+8),atlas.slice(i+6,i+8));
 assert.deepEqual(atlas,before);assert.deepEqual(clusterUV,bins(original));
});
test('merged vertices share averaged UVs within one connected atlas island only',()=>{
 const points=[[.001,0,0],[1,0,0],[0,1,0],[1,1,0],[.002,0,0],[-1,0,0],[0,-1,0]];
 const uv=[[.1,.1],[.8,.1],[.1,.8],[.8,.8],[.11,.1],[.95,.8],[.8,.95]];
 const rows=[];
 for(const [triangle,ids]of [[0,[0,1,2]],[1,[1,3,2]],[2,[2,3,4]],[3,[0,5,6]]])
  for(const id of ids)rows.push(...points[id],0,0,1,...(triangle===3&&id===0?[.9,.9]:uv[id]),4,0,0,0,1,0,0,0);
 const atlas=new Float32Array(rows),clusterUV=new Uint16Array(atlas.length/16),original=Float32Array.from(atlas);
 for(let i=0;i<original.length;i+=16)original.set([.01,.01],i+6);
 const expected=DC.CrowdGeometry.reduce(original,.1,{preserveUV:true});
 const actual=DC.CrowdGeometry.reduce(atlas,.1,{preserveUV:true,clusterUV});
 assert.equal(hash(geometry(actual)),hash(geometry(expected)));
 assert.deepEqual(actual.slice(6,8),actual.slice(8*16+6,8*16+8),'the same merged vertex in one island must have one UV');
 assert.equal(actual[6],Math.fround((atlas[6]+atlas[8*16+6])/2));
 assert.deepEqual(actual.slice(9*16+6,9*16+8),atlas.slice(9*16+6,9*16+8),'disconnected island keeps its own UV');
});
test('atlas islands touching at one vertex are not joined across an absent shared edge',()=>{
 const rows=[];
 for(const [p,uv]of [[[.001,0,0],[.1,.1]],[[1,0,0],[.4,.1]],[[0,1,0],[.1,.4]],
                      [[.002,0,0],[.2,.1]],[[0,1,0],[.1,.4]],[[-1,0,0],[0,.4]]])
  rows.push(...p,0,0,1,...uv,4,0,0,0,1,0,0,0);
 const atlas=new Float32Array(rows),out=DC.CrowdGeometry.reduce(atlas,.1,{preserveUV:true,clusterUV:new Uint16Array(6)});
 assert.notEqual(out[6],out[3*16+6]);
 assert.equal(out[6],atlas[6]);assert.equal(out[3*16+6],atlas[3*16+6]);
});
test('legacy output remains byte-identical without cluster metadata',()=>{
 const {original}=fixture();
 for(const preserveUV of [false,true])assert.equal(hash(DC.CrowdGeometry.reduce(original,.1,{preserveUV})),
  '7409ffa8bb8cb93ab0349d8c25e3f7c2f6475024af51009ba073a2c1202fef2a');
});
test('duplicate and collapsed triangles keep legacy filtering and the first retained atlas corners',()=>{
 const f=fixture(),tiny=[];
 for(const p of [[2,2,0],[2.001,2,0],[2,2.001,0]])tiny.push(...p,0,0,1,.1,.2,4,3,0,0,.75,.25,0,0);
 const original=new Float32Array([...f.original,...f.original.slice(0,48),...tiny]);
 const atlas=new Float32Array([...f.atlas,...f.atlas.slice(0,48),...tiny]);
 for(let i=f.atlas.length;i<atlas.length;i+=16){atlas[i+6]=.5+(i%48)*.001;atlas[i+7]=.6;}
 const baseline=DC.CrowdGeometry.reduce(original,.1,{preserveUV:true});
 const actual=DC.CrowdGeometry.reduce(atlas,.1,{preserveUV:true,clusterUV:bins(original)});
 assert.equal(actual.length,96);assert.equal(hash(geometry(actual)),hash(geometry(baseline)));
 for(let i=0;i<actual.length;i+=16)assert.deepEqual(actual.slice(i+6,i+8),f.atlas.slice(i+6,i+8));
});
test('atlas clustering rejects wrong type, length, range or absent UV preservation',()=>{
 const {atlas,clusterUV}=fixture(),before=Float32Array.from(atlas);
 for(const invalid of [null,new Float32Array(clusterUV),clusterUV.slice(1),new Uint16Array(clusterUV.length).fill(1089)])
  assert.throws(()=>DC.CrowdGeometry.reduce(atlas,.1,{preserveUV:true,clusterUV:invalid}),/cluster/i);
 assert.throws(()=>DC.CrowdGeometry.reduce(atlas,.1,{clusterUV}),/cluster/i);
 assert.deepEqual(atlas,before);
});
test('cast renderer decodes little-endian cluster metadata once and shares it across LODs',()=>{
 const {atlas,clusterUV}=fixture(),{calls,decodes}=castFixture(atlas,clusterUV);
 assert.equal(decodes,1);assert.equal(calls.length,2);
 assert.deepEqual(calls[0].clusterUV,clusterUV);assert.equal(calls[0].clusterUV,calls[1].clusterUV);
});
test('real face remapping preserves positions, normals, joint IDs and weights at all three LODs',()=>{
 const face=DC.HeroAsset.parts.find(p=>p.name==='face'),original=DC.Realism.decode(face),atlas=Float32Array.from(original),clusterUV=bins(original);
 // Change chart placement on the actual mesh without touching any geometry.
 for(let i=0;i<atlas.length;i+=16){atlas[i+6]=.07+atlas[i+6]*.43;atlas[i+7]=.11+atlas[i+7]*.37;}
 const {renderer}=castFixture(atlas,clusterUV);
 for(let lod=0;lod<3;lod++){
  const expected=lod?DC.CrowdGeometry.reduce(original,(lod===1?.009:.025)*.65,{preserveUV:true}):original;
  const actual=renderer.meshes[lod?'crowd'+lod+'_face':'hero_face'].data;
  assert.equal(hash(geometry(actual)),hash(geometry(expected)),'LOD '+lod);
 }
});
test('authored face atlas matches original source geometry at LOD0, LOD1 and LOD2',()=>{
 const atlasRoot=process.env.DC_FACE_ATLAS_ROOT?path.resolve(process.env.DC_FACE_ATLAS_ROOT):root;
 const context={DC:{}};
 vm.runInNewContext(fs.readFileSync(path.join(atlasRoot,'src/hero-asset.js'),'utf8'),context);
 const face=context.DC.HeroAsset.parts.find(p=>p.name==='face');
 const seed=JSON.parse(fs.readFileSync(path.join(atlasRoot,'assets/native-face-uv-source.json'),'utf8'));
 const oldUV=zlib.inflateSync(Buffer.from(seed.uvZlibBase64,'base64')),raw=Buffer.from(face.data,'base64');
 assert.equal(oldUV.length,face.vertices*4);assert.equal(seed.corners,face.vertices);
 for(let i=0;i<face.vertices;i++)oldUV.copy(raw,i*24+12,i*4,i*4+4);
 assert.equal(hash(raw),seed.faceSha256,'restored face matches the original source fingerprint');
 const original=DC.Realism.decode({...face,data:raw.toString('base64')}),atlas=DC.Realism.decode(face);
 const metadata=Buffer.from(face.lodClusterUV,'base64');assert.equal(metadata.length,face.vertices*2);
 const clusterUV=Uint16Array.from({length:face.vertices},(_,i)=>metadata.readUInt16LE(i*2));
 assert.deepEqual(clusterUV,bins(original),'authoring bins describe the original decoded UVs');
 assert.notEqual(face.data,raw.toString('base64'),'the authored atlas actually remaps UVs');
 const {renderer}=castFixture(atlas,clusterUV);
 // Frozen before atlas integration: ordered position/normal/joint/weight bytes.
 const baselineHashes=['f692f0f7e6b12c415c7e0f217c857984153ba7b62d5a42cc96a9cbecd2fd6f60',
  '411e01b0fe55a6a2841d50edf5d56e7f65b4c76d850906ea66c6730acee84420',
  '8cdf605aa448a78a61d15e8c3a1b5a80e13555bd5020ee1ed8ea1ed0d8cbab21'];
 for(let lod=0;lod<3;lod++){
  const expected=lod?DC.CrowdGeometry.reduce(original,(lod===1?.009:.025)*.65,{preserveUV:true}):original;
  const actual=renderer.meshes[lod?'crowd'+lod+'_face':'hero_face'].data;
  assert.equal(hash(geometry(expected)),baselineHashes[lod],'original geometry fingerprint LOD '+lod);
  assert.equal(actual.length,expected.length,'retained corners LOD '+lod);
  assert.equal(hash(geometry(actual)),hash(geometry(expected)),'exact geometry LOD '+lod);
  let collapsed=0;
  for(let i=0;i<actual.length;i+=48){
   const det=(actual[i+22]-actual[i+6])*(actual[i+39]-actual[i+7])-(actual[i+38]-actual[i+6])*(actual[i+23]-actual[i+7]);
   if(det===0)collapsed++;
  }
  assert.equal(collapsed,0,'atlas UV triangles remain noncollapsed at LOD '+lod);
 }
});
