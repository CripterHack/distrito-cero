'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs');
const file=require('node:path').resolve('tools/export_human_tangents.cjs');
const M=fs.existsSync(file)?require(file):{};
function call(...args){assert.equal(typeof M.addTangents,'function','Missing portable tangent stage');return M.addTangents(...args);}
function fixture(){
 const doc={asset:{version:'2.0'},buffers:[{byteLength:0}],bufferViews:[],accessors:[],
  materials:[{normalTexture:{index:0}}],meshes:[],nodes:[{name:'same'}],skins:[{joints:[0]}],
  animations:[{name:'same'}],images:[{name:'same'}]};
 const chunks=[];
 function add(values,type,width,component=5126){
  const data=Buffer.alloc(values.length*(component===5126?4:1));
  values.forEach((v,i)=>component===5126?data.writeFloatLE(v,i*4):data.writeUInt8(v,i));
  const view=doc.bufferViews.length;doc.bufferViews.push({buffer:0,byteOffset:doc.buffers[0].byteLength,byteLength:data.length});chunks.push(data);doc.buffers[0].byteLength+=data.length;
  const ix=doc.accessors.length;doc.accessors.push({bufferView:view,componentType:component,count:values.length/width,type,...(component===5121&&width===4?{normalized:true}:{})});return ix;
 }
 const attrs={POSITION:add([0,0,0,1,0,0,0,1,0],'VEC3',3),NORMAL:add([0,0,1,0,0,1,0,0,1],'VEC3',3),
  TEXCOORD_0:add([0,0,1,0,0,1],'VEC2',2),WEIGHTS_0:add([255,0,0,0,255,0,0,0,255,0,0,0],'VEC4',4,5121)};
 const indices=add([0,1,2,0,2,1],'SCALAR',1,5121);
 doc.meshes=[{primitives:[{attributes:attrs,indices,material:0,mode:4}]}];
 return {doc,bin:Buffer.concat(chunks)};
}
function generated(p){const out=new Float32Array(p.length/3*4);for(let i=0;i<out.length;i+=4){out[i]=1;out[i+3]=1;}return out;}
function rows(doc,bin,index){const a=doc.accessors[index],v=doc.bufferViews[a.bufferView],width={SCALAR:1,VEC2:2,VEC3:3,VEC4:4}[a.type],size={5121:1,5123:2,5125:4,5126:4}[a.componentType];
 return Array.from({length:a.count},(_,i)=>Array.from({length:width},(_,j)=>{const o=(v.byteOffset||0)+(a.byteOffset||0)+i*(v.byteStride||width*size)+j*size;return a.componentType===5126?bin.readFloatLE(o):a.componentType===5125?bin.readUInt32LE(o):a.componentType===5123?bin.readUInt16LE(o):bin[o];}));}
test('tangent stage preserves input and all prior binary bytes',()=>{
 const {doc,bin}=fixture(),before=structuredClone(doc),bytes=Buffer.from(bin);const out=call(doc,bin,generated);
 assert.deepEqual(doc,before);assert.deepEqual(bin,bytes);assert.deepEqual(out.binary.subarray(0,bin.length),bin);
 for(const k of ['materials','nodes','skins','images','animations'])assert.deepEqual(out.document[k],doc[k]);
 const p=out.document.meshes[0].primitives[0];assert.ok(p.attributes.TANGENT!==undefined);
 assert.ok(rows(out.document,out.binary,p.attributes.TANGENT).every(t=>t[0]===1&&t[3]===-1));
});
test('mirrored tangent bases split vertices without changing any triangle attribute',()=>{
 const {doc,bin}=fixture();const out=call(doc,bin,p=>{const t=generated(p);for(let i=12;i<t.length;i+=4)t[i+3]=-1;return t;});
 const a=doc.meshes[0].primitives[0],b=out.document.meshes[0].primitives[0];
 assert.equal(out.document.accessors[b.attributes.POSITION].count,6);
 const old=rows(doc,bin,a.indices).flat(),fresh=rows(out.document,out.binary,b.indices).flat();
 for(const name of Object.keys(a.attributes)){const prev=rows(doc,bin,a.attributes[name]),now=rows(out.document,out.binary,b.attributes[name]);
  assert.deepEqual(fresh.map(i=>now[i]),old.map(i=>prev[i]),name);}
});
test('consistent shared corners remain indexed instead of duplicating every triangle',()=>{
 const {doc,bin}=fixture(),out=call(doc,bin,generated),p=out.document.meshes[0].primitives[0];assert.equal(out.document.accessors[p.attributes.POSITION].count,3);
});
test('meshes without normal maps are preserved verbatim',()=>{
 const {doc,bin}=fixture();doc.materials=[{}];const out=call(doc,bin,()=>assert.fail('unneeded generation'));
 assert.deepEqual(out.document,doc);assert.deepEqual(out.binary,bin);
});
test('nonfinite, unnormalized, nonorthogonal and wrong-handed generator output is refused',()=>{
 for(const kind of ['nan','length','norm','dot','w']){const {doc,bin}=fixture(),before=structuredClone(doc);
  assert.throws(()=>call(doc,bin,p=>{const t=generated(p);if(kind==='length')return t.slice(4);if(kind==='nan')t[0]=NaN;if(kind==='norm')t[0]=2;if(kind==='dot'){t[0]=0;t[2]=1;}if(kind==='w')t[3]=0;return t;}),/tangent/i);
  assert.deepEqual(doc,before);
 }
});
test('unsupported and corrupt primitives fail without mutating input',()=>{
 for(const kind of ['sparse','range','index','count','mode','morph','uv-transform','nan']){
  const {doc,bin}=fixture(),p=doc.meshes[0].primitives[0];
  if(kind==='sparse')doc.accessors[0].sparse={};if(kind==='range')doc.bufferViews[0].byteLength=3;
  if(kind==='index')bin[doc.bufferViews[doc.accessors[p.indices].bufferView].byteOffset]=255;
  if(kind==='count')doc.accessors[1].count=2;if(kind==='mode')p.mode=1;if(kind==='morph')p.targets=[{}];
  if(kind==='uv-transform')doc.materials[0].normalTexture.extensions={KHR_texture_transform:{offset:[.2,.2]}};
  if(kind==='nan')bin.writeFloatLE(NaN,0);const before=structuredClone(doc),bytes=Buffer.from(bin);
  assert.throws(()=>call(doc,bin,generated),/unsupported|invalid|range|finite|count|index/i,kind);
  assert.deepEqual(doc,before);assert.deepEqual(bin,bytes);
 }
});
module.exports={fixture,generated,rows};
test('collapsed UVs use a declared orthogonal fallback without relaxing valid-UV checks',()=>{
 const {doc,bin}=fixture();const n=doc.bufferViews[doc.accessors[1].bufferView].byteOffset,uv=doc.bufferViews[doc.accessors[2].bufferView].byteOffset;
 for(let i=0;i<3;i++){bin.writeFloatLE(1,n+i*12);bin.writeFloatLE(0,n+i*12+8);bin.writeFloatLE(0,uv+i*8);bin.writeFloatLE(0,uv+i*8+4);}
 const out=call(doc,bin,generated),p=out.document.meshes[0].primitives[0];
 assert.equal(out.report.primitives[0].degenerateUvTriangles,2);
 assert.equal(out.report.primitives[0].fallbackTangentCorners,6);
 assert.match(out.report.degenerateUvPolicy,/orthogonal/);
 for(const t of rows(out.document,out.binary,p.attributes.TANGENT)){assert.ok(Math.abs(t[0])<1e-6);assert.ok(Math.abs(Math.hypot(...t.slice(0,3))-1)<1e-6);assert.equal(t[3],1);}
});
test('normal vectors must be unit length even on a collapsed UV chart',()=>{
 const {doc,bin}=fixture();bin.writeFloatLE(2,doc.bufferViews[doc.accessors[1].bufferView].byteOffset+8);
 assert.throws(()=>call(doc,bin,generated),/normal/i);
});
test('a nondegenerate triangle cannot contain mixed tangent handedness',()=>{
 const {doc,bin}=fixture();assert.throws(()=>call(doc,bin,p=>{const t=generated(p);t[3]=-1;return t;}),/handedness/i);
});
