'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),cp=require('node:child_process');
const glb=require('../tools/export_human_tangents.cjs');
const file=path.resolve('tools/qa/audit_uv.cjs');
const audit=(...args)=>{assert.ok(fs.existsSync(file),'Missing UV audit');return require(file).auditUv(...args);};
function fixture({uv=[0,0,1,0,0,1],positions=[0,0,0,1,0,0,0,1,0],indexed=true}={}){
 const doc={asset:{version:'2.0'},buffers:[{byteLength:0}],bufferViews:[],accessors:[],textures:[{},{},{}],materials:[{name:'test',normalTexture:{index:0}}],meshes:[]};
 const chunks=[];
 function add(values,type,width,componentType=5126){const data=Buffer.alloc(values.length*(componentType===5126?4:2));values.forEach((v,i)=>componentType===5126?data.writeFloatLE(v,i*4):data.writeUInt16LE(v,i*2));const bufferView=doc.bufferViews.length;doc.bufferViews.push({buffer:0,byteOffset:doc.buffers[0].byteLength,byteLength:data.length});chunks.push(data);doc.buffers[0].byteLength+=data.length;const id=doc.accessors.length;doc.accessors.push({bufferView,type,componentType,count:values.length/width});return id;}
 const attributes={POSITION:add(positions,'VEC3',3),TEXCOORD_0:add(uv,'VEC2',2)};
 const primitive={attributes,material:0};if(indexed)primitive.indices=add([0,1,2],'SCALAR',1,5123);
 doc.meshes=[{name:'surface',primitives:[primitive]}];return {doc,bin:Buffer.concat(chunks)};
}
test('a valid or mirrored UV chart passes without altering inputs',()=>{
 for(const uv of [[0,0,1,0,0,1],[1,0,0,0,1,1]]){const {doc,bin}=fixture({uv}),before=structuredClone(doc),bytes=Buffer.from(bin),r=audit(doc,bin);assert.equal(r.status,'passed');assert.equal(r.degenerateUvTriangles,0);assert.equal(r.charts[0].triangleCount,1);assert.deepEqual(doc,before);assert.deepEqual(bin,bytes);}
});
test('collapsed UVs identify exact triangle, spatial bounds and boundary coordinates',()=>{
 const {doc,bin}=fixture({uv:[.2,1,.5,1,.8,1]}),r=audit(doc,bin),c=r.charts[0];
 assert.equal(r.status,'blocked');assert.equal(r.degenerateUvTriangles,1);assert.deepEqual(c.triangleIndices,[0]);assert.deepEqual(c.positionBounds,{min:[0,0,0],max:[1,1,0]});assert.equal(c.uvBounds.min[1],1);assert.equal(c.uvBounds.max[1],1);assert.equal(c.constantVTriangles,1);assert.equal(c.geometricallyDegenerateTriangles,0);assert.equal(c.materialName,'test');assert.deepEqual(c.textureRoles,['normalTexture']);
});
test('spatially degenerate and collinear UV triangles remain blocked and counted separately',()=>{
 const {doc,bin}=fixture({positions:[0,0,0,1,0,0,2,0,0],uv:[0,0,.5,.5,1,1],indexed:false}),c=audit(doc,bin).charts[0];
 assert.deepEqual(c.triangleIndices,[0]);assert.equal(c.geometricallyDegenerateTriangles,1);assert.equal(c.constantUTriangles,0);assert.equal(c.constantVTriangles,0);
});
test('mixed triangles retain original IDs and geometry-only debt is distinct from UV debt',()=>{
 const {doc,bin}=fixture({positions:[0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,2,0,0],uv:[0,0,1,0,0,0,0,0,1,0,0,1],indexed:false});
 const c=audit(doc,bin).charts[0];assert.deepEqual(c.triangleIndices,[0]);assert.deepEqual(c.geometricallyDegenerateTriangleIndices,[1]);
});
test('normalized integer UVs and interleaved offset/stride accessors are decoded',()=>{
 const {doc,bin}=fixture(),uv=doc.accessors[1],view=doc.bufferViews[uv.bufferView],offset=view.byteOffset;
 uv.componentType=5123;uv.normalized=true;uv.byteOffset=2;view.byteStride=8;
 for(let i=0;i<3;i++){bin.writeUInt16LE(i===1?65535:0,offset+2+i*8);bin.writeUInt16LE(i===2?65535:0,offset+4+i*8);}
 assert.equal(audit(doc,bin).status,'passed');
});
test('integer collinearity is not hidden by floating point normalization',()=>{
 const {doc,bin}=fixture(),uv=doc.accessors[1],view=doc.bufferViews[uv.bufferView];uv.componentType=5123;uv.normalized=true;
 [1,1006,2,1007,3,1008].forEach((n,i)=>bin.writeUInt16LE(n,view.byteOffset+i*2));
 const r=audit(doc,bin);assert.equal(r.status,'blocked');assert.deepEqual(r.charts[0].triangleIndices,[0]);
});
test('each consumed UV set is audited once with all of its material roles',()=>{
 const {doc,bin}=fixture({uv:[0,0,0,0,0,0]});doc.materials[0].pbrMetallicRoughness={baseColorTexture:{index:1}};
 const p=doc.meshes[0].primitives[0];p.attributes.TEXCOORD_1=p.attributes.TEXCOORD_0;doc.materials[0].occlusionTexture={index:2,texCoord:1};
 const r=audit(doc,bin);assert.equal(r.charts.length,2);assert.equal(r.degenerateUvTriangles,1);assert.equal(r.degenerateUvTriangleCharts,2);assert.equal(r.charts[0].textureRoles.length,2);assert.equal(r.charts[1].texCoord,1);
});
test('untextured meshes are counted as skipped, never as checked UV charts',()=>{
 const {doc,bin}=fixture();doc.materials=[{}];const r=audit(doc,bin);assert.equal(r.status,'not-applicable');assert.equal(r.charts.length,0);assert.equal(r.skippedUntexturedPrimitives,1);
});
test('nonfinite, transformed, missing, sparse and malformed inputs fail closed without mutation',()=>{
 for(const kind of ['nan','transform','missing','sparse','count','index','mode','material','extension','texture']){const {doc,bin}=fixture(),p=doc.meshes[0].primitives[0];
  if(kind==='nan')bin.writeFloatLE(NaN,doc.bufferViews[1].byteOffset);
  if(kind==='transform')doc.materials[0].normalTexture.extensions={KHR_texture_transform:{scale:[0,1]}};
  if(kind==='missing')delete p.attributes.TEXCOORD_0;
  if(kind==='sparse')doc.accessors[1].sparse={};
  if(kind==='count')doc.accessors[1].count=2;
  if(kind==='index')bin.writeUInt16LE(9,doc.bufferViews[2].byteOffset);
  if(kind==='mode')p.mode=5;
  if(kind==='material')p.material=99;
  if(kind==='extension')doc.materials[0].extensions={KHR_materials_clearcoat:{clearcoatTexture:{index:1}}};
  if(kind==='texture')doc.materials[0].normalTexture.index=999;
  const before=structuredClone(doc),bytes=Buffer.from(bin);assert.throws(()=>audit(doc,bin),/unsupported|invalid|missing|finite|count/i,kind);assert.deepEqual(doc,before);assert.deepEqual(bin,bytes);
 }
});
test('CLI blocks collapsed charts with a source hash and no generated or modified asset',()=>{
 const root=fs.mkdtempSync(path.join(os.tmpdir(),'dc-uv-audit-'));
 try{for(const bad of [false,true]){const {doc,bin}=fixture(bad?{uv:[0,0,0,0,0,0]}:{}),raw=glb.encodeGlb(doc,bin),input=path.join(root,(bad?'bad':'good')+'.glb');fs.writeFileSync(input,raw);const p=cp.spawnSync(process.execPath,[file,input],{encoding:'utf8'});assert.equal(p.status,bad?1:0,p.stderr);const r=JSON.parse(p.stdout);assert.match(r.sourceSha256,/^[a-f0-9]{64}$/);assert.equal(r.status,bad?'blocked':'passed');assert.deepEqual(fs.readFileSync(input),raw);}}
 finally{fs.rmSync(root,{recursive:true,force:true});}
});
