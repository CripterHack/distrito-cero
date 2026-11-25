'use strict';
// Offline authoring derivative. UVs/images change; rig and per-corner geometry do not.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {decodeGlb,encodeGlb,accessor}=require('./export_human_tangents.cjs');
const ROOT=path.resolve(__dirname,'..'),integer=n=>Number.isSafeInteger(n)&&n>=0;
const hash=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const KEYS=['baseColor','normal','orm'],PNG=Buffer.from([137,80,78,71,13,10,26,10]);
function repackUv(input,bytes,recipe,images){
 if(!Buffer.isBuffer(bytes)||input.buffers?.length!==1||input.buffers[0].uri||
    !integer(input.buffers[0].byteLength)||input.buffers[0].byteLength>bytes.length)throw new Error('Unsupported embedded buffer');
 if(recipe?.schema!==1||!integer(recipe.mesh)||!integer(recipe.primitive)||recipe.normalScale!==1)throw new Error('Invalid recipe target or normalScale; baked normalScale must be 1');
 const primitive=input.meshes?.[recipe.mesh]?.primitives?.[recipe.primitive];
 if(!primitive)throw new Error('Invalid recipe target');
 if((primitive.mode??4)!==4||primitive.targets||primitive.extensions)throw new Error('Unsupported primitive, morph or compression');
 if(!integer(primitive.material)||!input.materials?.[primitive.material])throw new Error('Invalid material index');
 const material=input.materials[primitive.material],pbr=material.pbrMetallicRoughness;
 if(material.extensions||pbr?.extensions||material.emissiveTexture)throw new Error('Unsupported material extension or emissive texture');
 const textures=[pbr?.baseColorTexture,material.normalTexture,pbr?.metallicRoughnessTexture];
 if(textures.some(t=>!t))throw new Error('Unsupported source material; all three baked maps are required');
 if(material.occlusionTexture)textures.push(material.occlusionTexture);
 for(const texture of textures){
  if(!integer(texture.index)||!input.textures?.[texture.index]||(texture.texCoord??0)!==0||texture.extensions||input.textures[texture.index].extensions)throw new Error('Unsupported texture coordinates or invalid texture index');
 }
 for(const key of KEYS){
  const image=images?.[key];
  if(!Buffer.isBuffer(image)||image.length<24||!image.subarray(0,8).equals(PNG)||image.toString('ascii',12,16)!=='IHDR'||!image.readUInt32BE(16)||!image.readUInt32BE(20))throw new Error('Invalid PNG for '+key);
 }
 const attributes=Object.fromEntries(Object.entries(primitive.attributes??{}).map(([name,index])=>[name,accessor(input,bytes,index)]));
 const pos=attributes.POSITION,norm=attributes.NORMAL,uv=attributes.TEXCOORD_0;
 if(!pos||!norm||!uv||pos.width!==3||norm.width!==3||uv.width!==2||
    [pos,norm,uv].some(a=>a.a.componentType!==5126||a.a.normalized))throw new Error('Unsupported position, normal or UV layout');
 const count=pos.a.count;
 for(const attr of Object.values(attributes)){
  if(attr.a.count!==count||attr.a.extensions)throw new Error('Unsupported attribute extension or count');
  if(attr.a.componentType===5126)for(let i=0;i<count;i++)for(let k=0;k<attr.width;k++)if(!Number.isFinite(attr.value(i,k)))throw new Error('Nonfinite vertex input');
 }
 const indices=primitive.indices===undefined?null:accessor(input,bytes,primitive.indices);
 if(indices&&(indices.width!==1||![5121,5123,5125].includes(indices.a.componentType)||indices.a.normalized||indices.a.extensions))throw new Error('Invalid index layout');
 const corners=indices?.a.count??count;
 if(corners%3)throw new Error('Invalid triangle count');
 const order=Array.from({length:corners},(_,i)=>indices?indices.value(i):i);
 if(order.some(i=>!integer(i)||i>=count))throw new Error('Invalid triangle index');
 if(!Array.isArray(recipe.cornerUvs)||recipe.cornerUvs.length!==corners||recipe.cornerUvs.some(p=>!Array.isArray(p)||p.length!==2||p.some(v=>!Number.isFinite(v)||v<0||v>1)))throw new Error('Invalid recipe UV count, range or coordinates');
 const freshUvs=recipe.cornerUvs.map(p=>p.map(Math.fround));
 for(let i=0;i<corners;i+=3){
  const [a,b,c]=freshUvs.slice(i,i+3),det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]);
  if(!Number.isFinite(det)||det===0)throw new Error('Collapsed baked UV triangle after float32 conversion: '+i/3);
 }
 const doc=structuredClone(input),chunks=[Buffer.from(bytes)];let length=bytes.length;
 function appendView(data,target){
  const padding=(4-length%4)%4;if(padding){chunks.push(Buffer.alloc(padding));length+=padding;}
  const index=doc.bufferViews.length;doc.bufferViews.push({buffer:0,byteOffset:length,byteLength:data.length,...(target?{target}:{})});chunks.push(data);length+=data.length;return index;
 }
 function appendAccessor(data,descriptor,target){const bufferView=appendView(data,target),index=doc.accessors.length;doc.accessors.push({...descriptor,bufferView});return index;}
 const out=doc.meshes[recipe.mesh].primitives[recipe.primitive];
 out.attributes={};
 for(const [name,attr]of Object.entries(attributes)){
  if(name==='TEXCOORD_0'||name==='TANGENT')continue;
  const descriptor=structuredClone(attr.a);delete descriptor.bufferView;delete descriptor.byteOffset;descriptor.count=corners;
  if(descriptor.min||descriptor.max||name==='POSITION'){
   descriptor.min=Array.from({length:attr.width},(_,k)=>order.reduce((n,i)=>Math.min(n,attr.value(i,k)),Infinity));
   descriptor.max=Array.from({length:attr.width},(_,k)=>order.reduce((n,i)=>Math.max(n,attr.value(i,k)),-Infinity));
  }
  out.attributes[name]=appendAccessor(Buffer.concat(order.map(i=>attr.row(i))),descriptor,34962);
 }
 const uvBytes=Buffer.alloc(corners*8);freshUvs.forEach((p,i)=>p.forEach((v,k)=>uvBytes.writeFloatLE(v,i*8+k*4)));
 out.attributes.TEXCOORD_0=appendAccessor(uvBytes,{componentType:5126,type:'VEC2',count:corners},34962);
 const indexSize=corners<=65536?2:4,indexBytes=Buffer.alloc(corners*indexSize);
 for(let i=0;i<corners;i++)indexSize===2?indexBytes.writeUInt16LE(i,i*2):indexBytes.writeUInt32LE(i,i*4);
 out.indices=appendAccessor(indexBytes,{componentType:indexSize===2?5123:5125,type:'SCALAR',count:corners},34963);
 doc.images??=[];doc.textures??=[];doc.samplers??=[];
 const sampler=doc.samplers.length;doc.samplers.push({magFilter:9729,minFilter:9987,wrapS:33071,wrapT:33071});
 const newTextures={};
 for(const key of KEYS){
  const image=doc.images.length;doc.images.push({name:'Rebaked '+key,mimeType:'image/png',bufferView:appendView(images[key])});
  newTextures[key]=doc.textures.length;doc.textures.push({source:image,sampler});
 }
 const baked=structuredClone(material);baked.name=(baked.name??'Material')+' UV rebake';
 baked.pbrMetallicRoughness.baseColorTexture={index:newTextures.baseColor};
 baked.pbrMetallicRoughness.metallicRoughnessTexture={index:newTextures.orm};
 baked.normalTexture={index:newTextures.normal,scale:1};
 if(baked.occlusionTexture)baked.occlusionTexture={...baked.occlusionTexture,index:newTextures.orm};
 out.material=doc.materials.length;doc.materials.push(baked);doc.buffers[0].byteLength=length;
 return {document:doc,binary:Buffer.concat(chunks),report:{mesh:recipe.mesh,primitive:recipe.primitive,triangles:corners/3,inputVertices:count,outputVertices:corners,
  inputMaterial:primitive.material,outputMaterial:out.material,originalBinaryBytes:bytes.length,addedBinaryBytes:length-bytes.length,normalScale:1,
  policy:'Original binary retained; raw corner attributes preserved except UV/TANGENT; tangents require regeneration; artistic acceptance pending.'}};
}
function exportRepacked(inputDirectory,recipeFile,outputDirectory){
 const input=fs.realpathSync(inputDirectory),recipePath=fs.realpathSync(recipeFile),output=path.resolve(outputDirectory);
 if(fs.existsSync(output))throw new Error('Output directory already exists');
 const resolved=path.join(fs.realpathSync(path.dirname(output)),path.basename(output));
 if(resolved===ROOT||resolved.startsWith(ROOT+path.sep)&&!resolved.startsWith(path.join(ROOT,'artifacts')+path.sep))throw new Error('Refusing versioned output directory');
 const manifestPath=path.join(input,'source-manifest.json'),manifestBytes=fs.readFileSync(manifestPath),manifest=JSON.parse(manifestBytes);
 if(typeof manifest.file!=='string'||path.basename(manifest.file)!==manifest.file||!manifest.file.endsWith('.glb'))throw new Error('Invalid source GLB filename');
 const filePath=path.join(input,manifest.file),raw=fs.readFileSync(filePath),recipeBytes=fs.readFileSync(recipePath),recipe=JSON.parse(recipeBytes);
 if(hash(raw)!==manifest.sha256||recipe.sourceSha256!==manifest.sha256)throw new Error('Recipe or source GLB hash mismatch');
 const images={},imageFiles={},imageSha256={},recipeDirectory=path.dirname(recipePath);
 for(const key of KEYS){
  const name=recipe.images?.[key];if(typeof name!=='string'||path.isAbsolute(name))throw new Error('Invalid recipe image path');
  const file=fs.realpathSync(path.resolve(recipeDirectory,name));
  if(!file.startsWith(recipeDirectory+path.sep))throw new Error('Recipe image escapes bake directory');
  imageFiles[key]=file;images[key]=fs.readFileSync(file);imageSha256[key]=hash(images[key]);
 }
 const decoded=decodeGlb(raw),out=repackUv(decoded.document,decoded.binary,recipe,images),blob=encodeGlb(out.document,out.binary),file=manifest.file.replace(/\.glb$/,'-uv-rebaked.glb');
 const record={...manifest,assetId:(manifest.assetId??'human')+'-uv-rebaked',file,bytes:blob.length,sha256:hash(blob),officialValidation:'not-run',artisticAcceptance:'pending',
  derivedFrom:{sha256:manifest.sha256,sourceManifestSha256:hash(manifestBytes)},uvRebake:{...out.report,recipeSha256:hash(recipeBytes),imageSha256,toolchain:recipe.toolchain??null},
  limitations:[...(manifest.limitations??[]),'UV rebake is an authoring derivative, not a native runtime replacement.','Recomputed tangents, official validation and visual comparison are separate gates.'],
  sources:{...manifest.sources,'tools/repack_human_uv.cjs':hash(fs.readFileSync(__filename)),
   'tools/export_human_tangents.cjs':hash(fs.readFileSync(path.join(__dirname,'export_human_tangents.cjs')))}};
 delete record.validationCounts;delete record.validationReportSha256;delete record.validatorPackage;
 // The original tangent report describes the source charts, not this derivative.
 delete record.portableTangents;delete record.tangentToolchain;
 if(hash(fs.readFileSync(filePath))!==manifest.sha256||hash(fs.readFileSync(manifestPath))!==hash(manifestBytes)||hash(fs.readFileSync(recipePath))!==hash(recipeBytes)||KEYS.some(k=>hash(fs.readFileSync(imageFiles[k]))!==imageSha256[k]))throw new Error('Input changed during UV repack');
 fs.mkdirSync(resolved);fs.writeFileSync(path.join(resolved,file),blob,{flag:'wx'});fs.writeFileSync(path.join(resolved,'source-manifest.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});return record;
}
module.exports={repackUv,exportRepacked};
if(require.main===module){try{
 if(process.argv.length!==5)throw new Error('Usage: node tools/repack_human_uv.cjs INPUT_DIR RECIPE_JSON OUTPUT_DIR');
 const result=exportRepacked(...process.argv.slice(2));console.log(JSON.stringify({file:result.file,sha256:result.sha256,...result.uvRebake}));
}catch(error){console.error(error.message);process.exitCode=1;}}
