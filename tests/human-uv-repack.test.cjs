'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const {encodeGlb,decodeGlb,accessor}=require('../tools/export_human_tangents.cjs');
const target=path.resolve(__dirname,'../tools/repack_human_uv.cjs');
const M=fs.existsSync(target)?require(target):{};
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const PNG=Buffer.from('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aFOkAAAAASUVORK5CYII=','base64');
function fixture(){
 const doc={asset:{version:'2.0'},buffers:[{byteLength:0}],bufferViews:[],accessors:[],
  materials:[{name:'source',pbrMetallicRoughness:{baseColorTexture:{index:0},metallicRoughnessTexture:{index:2},metallicFactor:0,roughnessFactor:1},normalTexture:{index:1,scale:.3},occlusionTexture:{index:2,strength:.7}}],
  textures:[{source:0},{source:1},{source:2}],images:[{uri:'source-a.png'},{uri:'source-n.png'},{uri:'source-o.png'}],
  nodes:[{name:'rig',mesh:0,skin:0}],skins:[{joints:[0]}],animations:[{name:'preserved',channels:[],samplers:[]}],scenes:[{nodes:[0]}],scene:0};
 const chunks=[];
 function add(values,type,width,component=5126,normalized){
  const size=component===5126?4:1,pad=(4-doc.buffers[0].byteLength%4)%4;
  if(pad){chunks.push(Buffer.alloc(pad));doc.buffers[0].byteLength+=pad;}
  const data=Buffer.alloc(values.length*size);values.forEach((v,i)=>component===5126?data.writeFloatLE(v,i*4):data.writeUInt8(v,i));
  const bufferView=doc.bufferViews.length;doc.bufferViews.push({buffer:0,byteOffset:doc.buffers[0].byteLength,byteLength:data.length});
  chunks.push(data);doc.buffers[0].byteLength+=data.length;
  const index=doc.accessors.length;doc.accessors.push({bufferView,componentType:component,type,count:values.length/width,...(normalized===undefined?{}:{normalized})});return index;
 }
 const attributes={POSITION:add([0,0,0,1,0,0,1,1,0,0,1,0],'VEC3',3),NORMAL:add(Array(4).fill([0,0,1]).flat(),'VEC3',3),
  TEXCOORD_0:add([0,0,1,0,1,1,0,1],'VEC2',2),TANGENT:add(Array(4).fill([1,0,0,1]).flat(),'VEC4',4),
  JOINTS_0:add(Array(4).fill([0,0,0,0]).flat(),'VEC4',4,5121),WEIGHTS_0:add(Array(4).fill([255,0,0,0]).flat(),'VEC4',4,5121,true)};
 const indices=add([0,1,2,0,2,3],'SCALAR',1,5121);
 doc.meshes=[{name:'face',primitives:[{attributes,indices,material:0,mode:4}]},{name:'other',primitives:[{attributes:{...attributes},indices,material:0,mode:4}]}];
 const binary=Buffer.concat(chunks),recipe={schema:1,mesh:0,primitive:0,normalScale:1,cornerUvs:[[.05,.05],[.45,.05],[.45,.45],[.55,.55],[.95,.55],[.95,.95]],images:{baseColor:'color.png',normal:'normal.png',orm:'orm.png'}};
 return {doc,binary,recipe,images:{baseColor:PNG,normal:PNG,orm:PNG}};
}
function call(f){assert.equal(typeof M.repackUv,'function','Missing UV rebake repacker');return M.repackUv(f.doc,f.binary,f.recipe,f.images);}
test('UV repack preserves rig, animations, other primitives and original bytes without mutation',()=>{
 const f=fixture(),doc=structuredClone(f.doc),bytes=Buffer.from(f.binary),recipe=structuredClone(f.recipe),out=call(f);
 assert.deepEqual(f.doc,doc);assert.deepEqual(f.binary,bytes);assert.deepEqual(f.recipe,recipe);assert.deepEqual(out.binary.subarray(0,bytes.length),bytes);
 for(const key of ['nodes','skins','animations','scenes','scene'])assert.deepEqual(out.document[key],doc[key]);
 assert.deepEqual(out.document.meshes[1],doc.meshes[1]);assert.deepEqual(out.document.materials.slice(0,doc.materials.length),doc.materials);
 assert.equal(out.report.triangles,2);assert.equal(out.report.outputVertices,6);
});
test('split UV corners retain position, normal, joints and weights exactly; stale tangents are removed',()=>{
 const f=fixture(),out=call(f),old=f.doc.meshes[0].primitives[0],fresh=out.document.meshes[0].primitives[0],order=accessor(f.doc,f.binary,old.indices);
 assert.equal(fresh.attributes.TANGENT,undefined);
 for(const name of ['POSITION','NORMAL','JOINTS_0','WEIGHTS_0']){
  const a=accessor(f.doc,f.binary,old.attributes[name]),b=accessor(out.document,out.binary,fresh.attributes[name]);
  for(let i=0;i<6;i++)assert.deepEqual(b.row(i),a.row(order.value(i)),name+':'+i);
 }
 const uv=accessor(out.document,out.binary,fresh.attributes.TEXCOORD_0);
 for(let i=0;i<6;i++)for(let k=0;k<2;k++)assert.equal(uv.value(i,k),Math.fround(f.recipe.cornerUvs[i][k]));
});
test('new texture/material records point to embedded PNGs and normalized baked normal strength',()=>{
 const f=fixture(),out=call(f),doc=out.document,p=doc.meshes[0].primitives[0],m=doc.materials[p.material];
 assert.equal(m.normalTexture.scale,1);assert.equal(m.occlusionTexture.strength,.7);assert.equal(m.pbrMetallicRoughness.metallicFactor,0);
 for(const texture of [m.pbrMetallicRoughness.baseColorTexture,m.normalTexture,m.pbrMetallicRoughness.metallicRoughnessTexture]){
  const image=doc.images[doc.textures[texture.index].source],v=doc.bufferViews[image.bufferView];
  assert.equal(image.uri,undefined);assert.equal(image.mimeType,'image/png');assert.deepEqual(out.binary.subarray(v.byteOffset,v.byteOffset+v.byteLength),PNG);
 }
 assert.equal(m.occlusionTexture.index,m.pbrMetallicRoughness.metallicRoughnessTexture.index);
});
test('malformed, nonfinite, collapsed and float32-collapsing recipes fail before mutation',()=>{
 for(const change of [r=>r.cornerUvs.pop(),r=>r.cornerUvs[0][0]=NaN,r=>r.cornerUvs[0]=r.cornerUvs[1],r=>r.cornerUvs.splice(0,3,[.5,.5],[.5+1e-9,.5],[.5,.5+1e-9]),r=>r.normalScale=.3,r=>delete r.normalScale,r=>r.mesh=2]){
  const f=fixture();change(f.recipe);const before=structuredClone(f.doc),bytes=Buffer.from(f.binary);assert.throws(()=>call(f),/recipe|UV|normalScale|target/i);assert.deepEqual(f.doc,before);assert.deepEqual(f.binary,bytes);
 }
});
test('unsupported geometry, textures and image payloads cannot create a derivative',()=>{
 for(const kind of ['morph','mode','sparse','range','index','extension','other-uv','emissive','nan','png']){
  const f=fixture(),p=f.doc.meshes[0].primitives[0];
  if(kind==='morph')p.targets=[{}];if(kind==='mode')p.mode=1;if(kind==='sparse')f.doc.accessors[0].sparse={};if(kind==='range')f.doc.bufferViews[0].byteLength=1;
  if(kind==='index')f.binary[f.doc.bufferViews[f.doc.accessors[p.indices].bufferView].byteOffset]=255;
  if(kind==='extension')f.doc.materials[0].extensions={};if(kind==='other-uv')f.doc.materials[0].normalTexture.texCoord=1;
  if(kind==='emissive')f.doc.materials[0].emissiveTexture={index:0};if(kind==='nan')f.binary.writeFloatLE(NaN,0);if(kind==='png')f.images.normal=Buffer.from('invalid');
  assert.throws(()=>call(f),/Unsupported|Invalid|Nonfinite|PNG|index|range/i,kind);
 }
});
test('CLI links exact recipe and image provenance, resets validation and refuses overwrite or wrong source',()=>{
 assert.equal(typeof M.repackUv,'function');const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'dc-uv-repack-'));
 try{
  const f=fixture(),input=path.join(tmp,'input'),bake=path.join(tmp,'bake'),output=path.join(tmp,'output');fs.mkdirSync(input);fs.mkdirSync(bake);
  const bytes=encodeGlb(f.doc,f.binary),manifest={assetId:'human',file:'source.glb',sha256:hash(bytes),officialValidation:'passed',validationCounts:{errors:0},portableTangents:{primitives:[{degenerateUvTriangles:99}]},tangentToolchain:{version:'old'},sources:{baseline:'unchanged'}};
  fs.writeFileSync(path.join(input,manifest.file),bytes);fs.writeFileSync(path.join(input,'source-manifest.json'),JSON.stringify(manifest));
  f.recipe.sourceSha256=manifest.sha256;for(const [key,name]of Object.entries(f.recipe.images))fs.writeFileSync(path.join(bake,name),f.images[key]);
  const recipePath=path.join(bake,'recipe.json');fs.writeFileSync(recipePath,JSON.stringify(f.recipe));
  const run=(out)=>spawnSync(process.execPath,[target,input,recipePath,out],{encoding:'utf8'});
  let r=run(output);assert.ifError(r.error);assert.equal(r.status,0,r.stderr);
  const accepted=JSON.parse(fs.readFileSync(path.join(output,'source-manifest.json')));assert.equal(accepted.officialValidation,'not-run');assert.equal(accepted.validationCounts,undefined);assert.equal(accepted.artisticAcceptance,'pending');assert.equal(accepted.portableTangents,undefined);assert.equal(accepted.tangentToolchain,undefined);
  assert.equal(accepted.derivedFrom.sha256,manifest.sha256);assert.equal(accepted.uvRebake.recipeSha256,hash(fs.readFileSync(recipePath)));assert.equal(accepted.uvRebake.imageSha256.normal,hash(PNG));
  const result=fs.readFileSync(path.join(output,accepted.file));assert.equal(accepted.sha256,hash(result));decodeGlb(result);
  assert.equal(run(output).status,1);f.recipe.sourceSha256='0'.repeat(64);fs.writeFileSync(recipePath,JSON.stringify(f.recipe));r=run(path.join(tmp,'wrong'));assert.equal(r.status,1);assert.equal(fs.existsSync(path.join(tmp,'wrong')),false);
  assert.deepEqual(fs.readFileSync(path.join(input,manifest.file)),bytes);
 }finally{fs.rmSync(tmp,{recursive:true,force:true});}
});
