'use strict';
// Requires the pinned development dependency, installed explicitly in human-export CI.
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto');
const M=require('../tools/export_human_tangents.cjs');
const dependency=process.env.DC_MIKKTSPACE_MODULE;
assert.ok(dependency,'Set DC_MIKKTSPACE_MODULE to pinned mikktspace 1.1.1');
const gen=M.loadGenerator(dependency).generateTangents;
const directory=process.env.DC_TANGENT_INPUT;
assert.ok(directory,'Set DC_TANGENT_INPUT to a current-human export directory');
const manifest=JSON.parse(fs.readFileSync(path.join(directory,'source-manifest.json'))),raw=fs.readFileSync(path.join(directory,manifest.file)),before=M.decodeGlb(raw);
const after=M.addTangents(before.document,before.binary,gen);
function rows(doc,bin,id){
 const a=doc.accessors[id],v=doc.bufferViews[a.bufferView],w={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type],s={5121:1,5123:2,5125:4,5126:4}[a.componentType];
 return Array.from({length:a.count},(_,i)=>{const off=(v.byteOffset||0)+(a.byteOffset||0)+i*(v.byteStride||w*s);return Buffer.from(bin.subarray(off,off+w*s));});
}
function indices(doc,bin,primitive){const a=doc.accessors[primitive.indices];return rows(doc,bin,primitive.indices).map(b=>a.componentType===5125?b.readUInt32LE():a.componentType===5123?b.readUInt16LE():b[0]);}
test('MikkTSpace preserves every real corner attribute and every earlier binary byte',()=>{
 assert.deepEqual(after.binary.subarray(0,before.binary.length),before.binary);
 for(let m=0;m<before.document.meshes.length;m++){
  const a=before.document.meshes[m].primitives[0],b=after.document.meshes[m].primitives[0];
  if(!before.document.materials[a.material]?.normalTexture){assert.deepEqual(b,a);continue;}
  const oldOrder=indices(before.document,before.binary,a),newOrder=indices(after.document,after.binary,b);
  assert.equal(newOrder.length,oldOrder.length);
  for(const attribute of Object.keys(a.attributes)){
   const old=rows(before.document,before.binary,a.attributes[attribute]),now=rows(after.document,after.binary,b.attributes[attribute]);
   for(let i=0;i<oldOrder.length;i++)assert.deepEqual(now[newOrder[i]],old[oldOrder[i]],`${m} ${attribute} corner ${i}`);
  }
 }
 for(const key of ['skins','nodes','animations','images','textures','materials','scenes'])assert.deepEqual(after.document[key],before.document[key],key);
});
test('real output provides normalized orthogonal tangents and uniform triangle handedness',()=>{
 for(const record of after.report.primitives){const p=after.document.meshes[record.mesh].primitives[record.primitive];
  const ns=rows(after.document,after.binary,p.attributes.NORMAL),ts=rows(after.document,after.binary,p.attributes.TANGENT),order=indices(after.document,after.binary,p);
  for(let i=0;i<ts.length;i++){const t=[0,4,8,12].map(k=>ts[i].readFloatLE(k)),n=[0,4,8].map(k=>ns[i].readFloatLE(k));assert.ok(t.every(Number.isFinite));assert.ok(Math.abs(Math.hypot(...t.slice(0,3))-1)<1e-5);assert.ok(Math.abs(t.slice(0,3).reduce((sum,v,k)=>sum+v*n[k],0))<1e-5);assert.equal(Math.abs(t[3]),1);}
  for(let i=0;i<order.length;i+=3){assert.equal(ts[order[i]].readFloatLE(12),ts[order[i+1]].readFloatLE(12));assert.equal(ts[order[i]].readFloatLE(12),ts[order[i+2]].readFloatLE(12));}
  assert.equal(record.degenerateUvTriangles,984);assert.equal(record.fallbackTangentCorners,2952);
 }
});
test('valid-chart frames are the pinned Mikk result with only documented W conversion',()=>{
 const primitive=before.document.meshes[3].primitives[0],order=indices(before.document,before.binary,primitive);
 const expand=(id,width)=>{const values=rows(before.document,before.binary,id);return Float32Array.from(order.flatMap(i=>Array.from({length:width},(_,k)=>values[i].readFloatLE(k*4))));};
 const p=expand(primitive.attributes.POSITION,3),n=expand(primitive.attributes.NORMAL,3),uv=expand(primitive.attributes.TEXCOORD_0,2),expected=gen(p,n,uv);
 const out=after.document.meshes[3].primitives[0],outOrder=indices(after.document,after.binary,out),ts=rows(after.document,after.binary,out.attributes.TANGENT);
 let compared=0;
 for(let i=0;i<order.length;i+=3){const q=i*2,det=(uv[q+2]-uv[q])*(uv[q+5]-uv[q+1])-(uv[q+4]-uv[q])*(uv[q+3]-uv[q+1]);if(det===0)continue;
  for(let j=i;j<i+3;j++)for(let k=0;k<4;k++)assert.equal(ts[outOrder[j]].readFloatLE(k*4),expected[j*4+k]*(k===3?-1:1));compared+=3;
 }
 assert.equal(compared,26064);
});
test('separate derivative is reproducible, hash-linked and not pre-approved',()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'dc-tangent-test-'));
 const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
 try{
  const a=M.exportWithTangents(directory,path.join(root,'a'),dependency),b=M.exportWithTangents(directory,path.join(root,'b'),dependency);
  assert.deepEqual(a,b);assert.equal(a.derivedFrom.sha256,hash(raw));assert.equal(a.officialValidation,'not-run');assert.equal(a.artisticAcceptance,'pending');
  assert.equal(hash(fs.readFileSync(path.join(root,'a',a.file))),a.sha256);assert.ok(a.sources['tools/export_human_tangents.cjs']);
  assert.throws(()=>M.exportWithTangents(directory,path.join(root,'a'),dependency),/already exists/);
  assert.throws(()=>M.exportWithTangents(directory,path.resolve('src/never-tangents'),dependency),/versioned/);
  assert.deepEqual(fs.readFileSync(path.join(directory,manifest.file)),raw);
 }finally{fs.rmSync(root,{recursive:true,force:true});}
});
test('wrong hashes, package versions and source paths cannot produce a derivative',()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'dc-tangent-reject-'));
 try{
  const input=path.join(root,'in'),dest=path.join(root,'out');fs.mkdirSync(input);fs.writeFileSync(path.join(input,manifest.file),raw);
  for(const change of [{sha256:'wrong'},{file:'../outside.glb'}]){
   fs.writeFileSync(path.join(input,'source-manifest.json'),JSON.stringify({...manifest,...change}));
   assert.throws(()=>M.exportWithTangents(input,dest,dependency),/hash|filename/);assert.equal(fs.existsSync(dest),false);
  }
  const fake=path.join(root,'fake');fs.mkdirSync(fake);fs.writeFileSync(path.join(fake,'package.json'),JSON.stringify({name:'mikktspace',version:'0.0.0'}));
  assert.throws(()=>M.loadGenerator(fake),/version/);
 }finally{fs.rmSync(root,{recursive:true,force:true});}
});
