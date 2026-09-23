'use strict';
// Authoring-only derivative. Does not alter native assets or load from the network.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const PIN='1.1.1',ROOT=path.resolve(__dirname,'..');
const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const WIDTH={SCALAR:1,VEC2:2,VEC3:3,VEC4:4};
const SIZE={5121:1,5123:2,5125:4,5126:4};
const integer=n=>Number.isSafeInteger(n)&&n>=0;
function decodeGlb(raw){
 if(!Buffer.isBuffer(raw)||raw.length<28||raw.readUInt32LE(0)!==0x46546c67||raw.readUInt32LE(4)!==2||raw.readUInt32LE(8)!==raw.length)throw new Error('Invalid GLB header');
 const n=raw.readUInt32LE(12),end=20+n;
 if(n%4||end+8>raw.length||raw.readUInt32LE(16)!==0x4e4f534a||raw.readUInt32LE(end+4)!==0x004e4942||end+8+raw.readUInt32LE(end)!==raw.length)throw new Error('Invalid GLB chunks');
 return {document:JSON.parse(raw.subarray(20,end).toString('utf8')),binary:Buffer.from(raw.subarray(end+8))};
}
function encodeGlb(doc,binary){
 const json=Buffer.from(JSON.stringify(doc)),padding=Buffer.alloc((4-json.length%4)%4,32);
 const binPadding=Buffer.alloc((4-binary.length%4)%4),j=Buffer.concat([json,padding]),b=Buffer.concat([binary,binPadding]);
 const head=Buffer.alloc(20);head.writeUInt32LE(0x46546c67);head.writeUInt32LE(2,4);head.writeUInt32LE(28+j.length+b.length,8);head.writeUInt32LE(j.length,12);head.writeUInt32LE(0x4e4f534a,16);
 const bh=Buffer.alloc(8);bh.writeUInt32LE(b.length);bh.writeUInt32LE(0x004e4942,4);
 return Buffer.concat([head,j,bh,b]);
}
function accessor(doc,binary,index){
 if(!integer(index)||!doc.accessors?.[index])throw new Error('Invalid accessor index');
 const a=doc.accessors[index],width=WIDTH[a.type],size=SIZE[a.componentType];
 if(!width||!size||a.sparse||!integer(a.count)||!a.count||!integer(a.bufferView))throw new Error('Unsupported accessor layout');
 const v=doc.bufferViews?.[a.bufferView],element=width*size;
 if(!v||v.buffer!==0||v.extensions)throw new Error('Unsupported buffer view');
 const start=v.byteOffset??0,relative=a.byteOffset??0,stride=v.byteStride??element,offset=start+relative;
 const end=offset+(a.count-1)*stride+element;
 if(![start,relative,stride,v.byteLength].every(integer)||stride<element||stride%size||relative%size||offset%size||
    relative+element>v.byteLength||end>binary.length||end>start+v.byteLength||end>doc.buffers[0].byteLength)throw new Error('Invalid accessor buffer range');
 const row=i=>binary.subarray(offset+i*stride,offset+i*stride+element);
 const value=(i,k=0)=>{const o=offset+i*stride+k*size;return a.componentType===5126?binary.readFloatLE(o):a.componentType===5125?binary.readUInt32LE(o):a.componentType===5123?binary.readUInt16LE(o):binary[o];};
 return {a,width,size,element,row,value};
}
function addTangents(input,bytes,generateTangents){
 if(typeof generateTangents!=='function')throw new Error('Missing tangent generator');
 if(!Buffer.isBuffer(bytes)||input.buffers?.length!==1||input.buffers[0].uri||!integer(input.buffers[0].byteLength)||input.buffers[0].byteLength>bytes.length)throw new Error('Unsupported embedded buffer');
 const doc=structuredClone(input),chunks=[Buffer.from(bytes)],records=[];let length=bytes.length;
 function append(data,descriptor,target){
  const pad=(4-length%4)%4;if(pad){chunks.push(Buffer.alloc(pad));length+=pad;}
  const vi=doc.bufferViews.length;doc.bufferViews.push({buffer:0,byteOffset:length,byteLength:data.length,target});chunks.push(data);length+=data.length;
  const ix=doc.accessors.length;doc.accessors.push({...descriptor,bufferView:vi});return ix;
 }
 for(let mi=0;mi<doc.meshes.length;mi++)for(let pi=0;pi<doc.meshes[mi].primitives.length;pi++){
  const p=doc.meshes[mi].primitives[pi],texture=doc.materials?.[p.material]?.normalTexture;
  if(!texture)continue;
  if((p.mode??4)!==4||p.targets||p.extensions||texture.extensions||p.attributes.TANGENT!==undefined)throw new Error('Unsupported tangent primitive, morph or UV transform');
  const attributes=Object.fromEntries(Object.entries(p.attributes).map(([name,ix])=>[name,accessor(input,bytes,ix)]));
  const position=attributes.POSITION,normal=attributes.NORMAL,uv=attributes['TEXCOORD_'+(texture.texCoord??0)];
  if(!position||!normal||!uv||position.width!==3||normal.width!==3||uv.width!==2||
     [position,normal,uv].some(v=>v.a.componentType!==5126||v.a.normalized))throw new Error('Unsupported position/normal/UV layout');
  const count=position.a.count;
  if(Object.values(attributes).some(v=>v.a.count!==count))throw new Error('Mismatched attribute count');
  const indices=p.indices===undefined?null:accessor(input,bytes,p.indices);
  if(indices&&(indices.width!==1||![5121,5123,5125].includes(indices.a.componentType)||indices.a.normalized))throw new Error('Invalid index layout');
  const corners=indices?.a.count??count;
  if(corners%3)throw new Error('Invalid triangle index count');
  const order=Array.from({length:corners},(_,i)=>indices?indices.value(i):i);
  if(order.some(i=>!integer(i)||i>=count))throw new Error('Invalid triangle index');
  const expand=v=>Float32Array.from(order.flatMap(i=>Array.from({length:v.width},(_,k)=>v.value(i,k))));
  const positions=expand(position),normals=expand(normal),uvs=expand(uv);
  if([positions,normals,uvs].some(a=>!a.every(Number.isFinite)))throw new Error('Nonfinite vertex input');
  for(let i=0;i<corners;i++)if(Math.abs(Math.hypot(...normals.subarray(i*3,i*3+3))-1)>1e-4)throw new Error('Invalid normal length');
  const result=generateTangents(positions,normals,uvs);
  if(!(result instanceof Float32Array)||result.length!==corners*4)throw new Error('Invalid tangent output length');
  if(!result.every(Number.isFinite))throw new Error('Nonfinite tangent output');
  const tangents=Float32Array.from(result),collapsed=new Set();
  for(let i=0;i<corners;i+=3){
   const q=i*2,det=(uvs[q+2]-uvs[q])*(uvs[q+5]-uvs[q+1])-(uvs[q+4]-uvs[q])*(uvs[q+3]-uvs[q+1]);
   if(det===0){
    collapsed.add(i/3);
    // There is no invertible UV basis here. Mikk returns its default X axis,
    // which need not be perpendicular to N. Declare, count and orthogonalize
    // these corners only; never substitute valid-UV Mikk results.
    for(let j=i;j<i+3;j++){
     const n=normals.subarray(j*3,j*3+3);let axis=0;
     for(let k=1;k<3;k++)if(Math.abs(n[k])<Math.abs(n[axis]))axis=k;
     const v=Array.from(n,(x,k)=>(k===axis?1:0)-x*n[axis]),len=Math.hypot(...v);
     for(let k=0;k<3;k++)tangents[j*4+k]=v[k]/len;
     tangents[j*4+3]=-1; // +1 after the glTF conversion below.
    }
   }else if(tangents[i*4+3]!==tangents[(i+1)*4+3]||tangents[i*4+3]!==tangents[(i+2)*4+3])throw new Error('Inconsistent tangent handedness');
  }
  for(let i=0;i<corners;i++){
   const t=tangents.subarray(i*4,i*4+4),n=normals.subarray(i*3,i*3+3);
   if(!t.every(Number.isFinite)||Math.abs(Math.hypot(...t.subarray(0,3))-1)>1e-4||
      Math.abs(t[0]*n[0]+t[1]*n[1]+t[2]*n[2])>1e-4||Math.abs(t[3])!==1)throw new Error('Invalid tangent frame');
   // mikktspace 1.1.1 documents this conversion for glTF image coordinates.
   t[3]*=-1;
  }
  const mapping=[],newIndices=[],sourceIds=[],unique=new Map(),tangentBytes=Buffer.alloc(tangents.length*4);
  tangents.forEach((v,i)=>tangentBytes.writeFloatLE(v,i*4));
  for(let i=0;i<corners;i++){
   const key=order[i]+':'+tangentBytes.subarray(i*16,i*16+16).toString('hex');
   if(!unique.has(key)){unique.set(key,sourceIds.length);sourceIds.push(order[i]);mapping.push(i);}
   newIndices.push(unique.get(key));
  }
  for(const [name,a] of Object.entries(attributes)){
   const data=Buffer.concat(sourceIds.map(a.row)),descriptor={componentType:a.a.componentType,type:a.a.type,count:sourceIds.length};
   if(a.a.normalized!==undefined)descriptor.normalized=a.a.normalized;
   if(a.a.min||a.a.max||name==='POSITION'){
    descriptor.min=Array.from({length:a.width},(_,k)=>sourceIds.reduce((min,i)=>Math.min(min,a.value(i,k)),Infinity));
    descriptor.max=Array.from({length:a.width},(_,k)=>sourceIds.reduce((max,i)=>Math.max(max,a.value(i,k)),-Infinity));
   }
   // Unknown metadata cannot silently change the meaning of a remapped accessor.
   if(a.a.extensions)throw new Error('Unsupported accessor extension');
   if(a.a.name)descriptor.name=a.a.name;if(a.a.extras)descriptor.extras=structuredClone(a.a.extras);
   p.attributes[name]=append(data,descriptor,34962);
  }
  p.attributes.TANGENT=append(Buffer.concat(mapping.map(i=>tangentBytes.subarray(i*16,i*16+16))),{componentType:5126,type:'VEC4',count:sourceIds.length},34962);
  const indexBytes=sourceIds.length<65536?2:4,data=Buffer.alloc(newIndices.length*indexBytes);
  newIndices.forEach((v,i)=>indexBytes===2?data.writeUInt16LE(v,i*2):data.writeUInt32LE(v,i*4));
  p.indices=append(data,{componentType:indexBytes===2?5123:5125,type:'SCALAR',count:corners},34963);
  records.push({mesh:mi,primitive:pi,inputVertices:count,referencedVertices:new Set(order).size,outputVertices:sourceIds.length,triangles:corners/3,degenerateUvTriangles:collapsed.size,fallbackTangentCorners:collapsed.size*3,splitVertices:sourceIds.length-new Set(order).size});
 }
 doc.buffers[0].byteLength=length;
 return {document:doc,binary:Buffer.concat(chunks),report:{algorithm:'MikkTSpace',packageVersion:PIN,degenerateUvPolicy:'Least-parallel-axis orthogonal frame, final W=+1; collapsed UVs remain unrepaired',gltfHandednessFlipped:true,originalBinaryBytes:bytes.length,addedBinaryBytes:length-bytes.length,primitives:records}};
}
function loadGenerator(directory){
 const root=path.resolve(directory),info=JSON.parse(fs.readFileSync(path.join(root,'package.json'),'utf8'));
 if(info.name!=='mikktspace'||info.version!==PIN||info.main!=='dist/main/mikktspace_main.js')throw new Error('Unexpected MikkTSpace package/version');
 const files=['package.json','LICENSE','dist/main/mikktspace_main.js','dist/main/mikktspace_main_bg.wasm'];
 const sources=Object.fromEntries(files.map(p=>[p,hash(fs.readFileSync(path.join(root,p)))]));
 return {generateTangents:require(root).generateTangents,provenance:{name:info.name,version:info.version,license:info.license,node:process.version,sources}};
}
function exportWithTangents(inputDirectory,outputDirectory,moduleDirectory){
 const input=fs.realpathSync(inputDirectory),output=path.resolve(outputDirectory);
 if(fs.existsSync(output))throw new Error('Output directory already exists');
 const parent=fs.realpathSync(path.dirname(output)),resolved=path.join(parent,path.basename(output));
 if(resolved===ROOT||resolved.startsWith(ROOT+path.sep)&&!resolved.startsWith(path.join(ROOT,'artifacts')+path.sep))throw new Error('Refusing versioned output directory');
 const manifestBytes=fs.readFileSync(path.join(input,'source-manifest.json')),manifest=JSON.parse(manifestBytes);
 if(typeof manifest.file!=='string'||path.basename(manifest.file)!==manifest.file||!manifest.file.endsWith('.glb'))throw new Error('Invalid source GLB filename');
 const raw=fs.readFileSync(path.join(input,manifest.file));if(hash(raw)!==manifest.sha256)throw new Error('Source GLB hash mismatch');
 const generator=loadGenerator(moduleDirectory),old=decodeGlb(raw),out=addTangents(old.document,old.binary,generator.generateTangents);
 if(!out.report.primitives.length)throw new Error('No normal-mapped primitive requires tangents');
 const blob=encodeGlb(out.document,out.binary),file=manifest.file.replace(/\.glb$/,'-tangents.glb');
 const record={...manifest,assetId:manifest.assetId+'-tangents',file,bytes:blob.length,sha256:hash(blob),officialValidation:'not-run',artisticAcceptance:'pending',
  derivedFrom:{sha256:manifest.sha256,sourceManifestSha256:hash(manifestBytes)},
  limitations:[...(manifest.limitations||[]),'UV-degenerate triangles use the counted orthogonal fallback, not an invertible Mikk UV basis.','Tangents are structurally validated separately; portable visual equivalence remains pending.'],
  portableTangents:out.report,tangentToolchain:generator.provenance,
  sources:{...manifest.sources,'tools/export_human_tangents.cjs':hash(fs.readFileSync(__filename))}};
 // A previously accepted input never supplies validation of its new derivative.
 delete record.validationCounts;delete record.validationReportSha256;delete record.validatorPackage;
 if(hash(fs.readFileSync(path.join(input,manifest.file)))!==manifest.sha256||hash(fs.readFileSync(path.join(input,'source-manifest.json')))!==hash(manifestBytes))throw new Error('Input changed during generation');
 fs.mkdirSync(resolved);fs.writeFileSync(path.join(resolved,file),blob,{flag:'wx'});
 fs.writeFileSync(path.join(resolved,'source-manifest.json'),JSON.stringify(record,null,2)+'\n',{flag:'wx'});
 return record;
}
module.exports={addTangents,decodeGlb,encodeGlb,accessor,loadGenerator,exportWithTangents};
if(require.main===module){try{if(process.argv.length!==5)throw new Error('Usage: node tools/export_human_tangents.cjs INPUT_DIR OUTPUT_DIR MIKKTSPACE_MODULE_DIR');const r=exportWithTangents(...process.argv.slice(2));console.log(JSON.stringify({file:r.file,sha256:r.sha256,...r.portableTangents}));}catch(error){console.error(error.message);process.exitCode=1;}}
