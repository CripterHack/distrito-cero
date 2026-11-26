'use strict';
// Offline conversion of the two reviewed material primitives. meshoptimizer 0.23.0
// chooses surviving source vertices, so bone indices and normalized weights stay paired.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {decodeGlb,accessor}=require('./export_human_tangents.cjs');
const SOURCE='assets/higgsfield-20261125/character-walk.glb';
const ROOT=path.resolve(__dirname,'..');
const xyz=(attr,i)=>Array.from({length:attr.width},(_,k)=>attr.value(i,k));
function prepareAtlas(filename,doc,binary,parts,raw){
 const material=doc.materials[parts[0].material],pbr=material.pbrMetallicRoughness;
 const nodes=[pbr.baseColorTexture,pbr.metallicRoughnessTexture,material.normalTexture];
 const maps=nodes.map(ref=>{
  const view=doc.bufferViews[doc.images[doc.textures[ref.index].source].bufferView];
  return [28+raw.readUInt32LE(12)+(view.byteOffset||0),view.byteLength];
 });
 const wall=parts[1],color=accessor(doc,binary,wall.attributes.COLOR_0);
 const colors=Array.from({length:color.a.count},(_,i)=>xyz(color,i));
 const roughness=doc.materials[wall.material].pbrMetallicRoughness.roughnessFactor;
 return JSON.parse(execFileSync('python3',[path.join(__dirname,'market_ped_atlas.py')],
  {input:JSON.stringify({source:filename,maps,colors,roughness}),maxBuffer:5*1024*1024}));
}
function streams(doc,binary,p){
 const attr=Object.fromEntries(Object.entries(p.attributes).map(([key,i])=>[key,accessor(doc,binary,i)]));
 const idx=accessor(doc,binary,p.indices), n=attr.POSITION.a.count;
 const positions=new Float32Array(n*3),attributes=new Float32Array(n*15);
 const keyNodes=['thighL','shinL','footL','thighR','shinR','footR','forearmL','handL','forearmR','handR'];
 const boneAttribute=new Map(keyNodes.map((name,k)=>[doc.skins[0].joints.findIndex(id=>doc.nodes[id].name===name),k+5]));
 for(let i=0;i<n;i++){
  positions.set(xyz(attr.POSITION,i),i*3);attributes.set(xyz(attr.NORMAL,i),i*15);
  attributes.set(xyz(attr.TEXCOORD_0,i),i*15+3);
  for(let j=0;j<4;j++){
   const k=boneAttribute.get(attr.JOINTS_0.value(i,j));
   if(k!==undefined)attributes[i*15+k]+=attr.WEIGHTS_0.value(i,j)/255;
  }
 }
 return {attr,n,positions,attributes,order:Uint32Array.from({length:idx.a.count},(_,i)=>idx.value(i)),lock:new Uint8Array(n)};
}
function skinUvs(swatch,part,i){
 const {colorMin,colorMax,tile,gutter,mainHeight,wallTop}=swatch, span=tile-2*gutter-1;
 if(part.attr.COLOR_0){
  const [r,g]=xyz(part.attr.COLOR_0,i);
  const u=(r-colorMin[0])/(colorMax[0]-colorMin[0]);
  const v=(g-colorMin[1])/(colorMax[1]-colorMin[1]);
  return [u,(tile-gutter-wallTop-1)*(1-v)/span];
 }
 const [u,v]=xyz(part.attr.TEXCOORD_0,i);
 return [u,1-v*(mainHeight-1)/span];
}
function packVertex(part,i,atlas){
 const point=Buffer.alloc(34);
 for(let k=0;k<3;k++){
  point.writeFloatLE(part.attr.POSITION.value(i,k),k*4);
  point.writeInt16LE(Math.round(part.attr.NORMAL.value(i,k)*32767),12+k*2);
 }
 skinUvs(atlas,part,i).forEach((v,k)=>point.writeFloatLE(Math.max(0,Math.min(1,v)),18+k*4));
 part.attr.JOINTS_0.row(i).copy(point,26);
 part.attr.WEIGHTS_0.row(i).copy(point,30);
 return point;
}
// Edge incidence uses identical glTF positions. Packed vertices retain all UV,
// normal, material and skinning seams of each surviving source vertex.
function topology(part,order,baseline){
 const edges=new Map(),opposed=new Set(),bad=new Set(),{positions:p,attributes:a,geometricId:g}=part;
 for(let k=0;k<order.length;k+=3){
  const i=order[k],j=order[k+1],l=order[k+2],ip=3*i,jp=3*j,lp=3*l;
  const x=p[jp]-p[ip],y=p[jp+1]-p[ip+1],z=p[jp+2]-p[ip+2];
  const u=p[lp]-p[ip],v=p[lp+1]-p[ip+1],w=p[lp+2]-p[ip+2];
  const nx=y*w-z*v,ny=z*u-x*w,nz=x*v-y*u;
  const ii=15*i,jj=15*j,ll=15*l;
  const facing=nx*(a[ii]+a[jj]+a[ll])+ny*(a[ii+1]+a[jj+1]+a[ll+1])+nz*(a[ii+2]+a[jj+2]+a[ll+2]);
  if(facing<=0){
   const key=[i,j,l].sort((a,b)=>a-b).join(':');opposed.add(key);
   if(baseline&&!baseline.opposed.has(key)){bad.add(i);bad.add(j);bad.add(l);}
  }
  if(baseline&&!part.attr.COLOR_0){
   const det=(a[jj+3]-a[ii+3])*(a[ll+4]-a[ii+4])-(a[ll+3]-a[ii+3])*(a[jj+4]-a[ii+4]);
   if(det<=0){bad.add(i);bad.add(j);bad.add(l);}
  }
  for(let e=0;e<3;e++){
   const m=order[k+e],n=order[k+(e+1)%3];
   const key=Math.min(g[m],g[n])*part.n+Math.max(g[m],g[n]);
   if(edges.has(key))edges.get(key).count++;
   else edges.set(key,{count:1,m,n});
  }
 }
 if(baseline)for(const [key,{count,m,n}] of edges){
  if(count!==2 && baseline.edges.get(key)?.count!==count){bad.add(m);bad.add(n);}
 }
 return {edges,opposed,bad};
}
function simplify(opt,part,ratio){
 const lock=part.lock.slice(),target=Math.floor(part.order.length*ratio/3)*3;
 const weights=[.24,.24,.24,.8,.8,...Array(10).fill(.30)];
 const baseline=topology(part,part.order);
 let previousLocked=-1;
 for(let pass=0;pass<120;pass++){
  const [reduced]=opt.simplifyWithAttributes(part.order,part.positions,3,part.attributes,15,weights,lock,target,.05);
  const {bad}=topology(part,reduced,baseline);
  if(!bad.size)return reduced;
  // Restore the incident source triangles, not just the final edge endpoints.
  const weld=new Set([...bad].map(i=>part.geometricId[i]));
  const locked=lock.reduce((sum,x)=>sum+x,0),expand=locked===previousLocked;
  previousLocked=locked;
  for(let k=0;k<part.order.length;k+=3){
   const i=part.order[k],j=part.order[k+1],l=part.order[k+2];
   const flagged=[i,j,l].filter(k=>weld.has(part.geometricId[k])).length;
   if(flagged>=(expand?1:2)){
    lock[i]=lock[j]=lock[l]=1;
   }
  }
 }
 throw new Error('Could not preserve source winding, UV handedness and edge incidence');
}
async function prepare(filename,meshopt){
 const {MeshoptSimplifier:opt}=require(meshopt);await opt.ready;
 const raw=fs.readFileSync(filename),{document:doc,binary}=decodeGlb(raw);
 const primitives=doc.meshes[0].primitives;
 if(doc.meshes.length!==1||primitives.length!==2||doc.skins[0].joints.length!==49||
    !primitives.every(p=>p.attributes.JOINTS_0!==undefined&&p.attributes.WEIGHTS_0!==undefined))
  throw new Error('Expected the reviewed 49-joint character and both hand/body primitives');
 const swatch=prepareAtlas(filename,doc,binary,primitives,raw),parts=primitives.map(p=>streams(doc,binary,p));
 // Preserve the shared interdigital seam: separate materials cannot make independent
 // vertex removals at their common boundary without tearing the two web walls apart.
 const positionKeys=parts.map(part=>Array.from({length:part.n},(_,i)=>part.attr.POSITION.row(i).toString('hex')));
 const keySets=positionKeys.map(keys=>new Set(keys));
 for(const [pi,part] of parts.entries()){
  const geom=new Map();
  part.geometricId=positionKeys[pi].map(key=>{
   if(!geom.has(key))geom.set(key,geom.size);
   return geom.get(key);
  });
  for(let i=0;i<part.n;i++){
   part.lock[i]=+keySets[1-pi].has(positionKeys[pi][i]);
   // Test the actual Float32 atlas coordinates used for tangent reconstruction.
   part.attributes.set(skinUvs(swatch,part,i),i*15+3);
  }
 }
 // Endpoints of the reviewed posterior trouser fold in the source topology.
 for(const id of [6155,6194,12708,12730])parts[0].lock[id]=1;
 // Two nearby cloth layers at the outer left knee must retain their individual
 // facets. Longer diagonals of a simplified layer can cross its neighbour in motion.
 const body=parts[0];
 for(let i=0;i<body.n;i++){
  const [x,y,z]=body.positions.subarray(i*3,i*3+3);
  if(x>.19 && y>.49 && y<.61 && z>.01 && z<.065)body.lock[i]=1;
 }
 const vertices=[],lookup=new Map();
 const levels=[.30,.085].map(ratio=>{
  const ids=[];
  for(const part of parts){
   // The thin repaired interdigital walls carry 1,062 faces. Retain the source
   // connectivity in both levels: collapsing two opposite walls onto the same
   // diagonal makes a four-face edge across the two material primitives.
   const reduced=part.attr.COLOR_0?part.order:simplify(opt,part,ratio);
   const packedIds=new Map();
   for(const i of reduced){
    if(!packedIds.has(i)){
     const point=packVertex(part,i,swatch),key=point.toString('hex');
     if(!lookup.has(key)){lookup.set(key,vertices.length);vertices.push(point);}
     packedIds.set(i,lookup.get(key));
    }
    ids.push(packedIds.get(i));
   }
  }
  const packed=Buffer.alloc(ids.length*2);
  ids.forEach((id,k)=>packed.writeUInt16LE(id,k*2));
  return {triangles:ids.length/3,indices:packed.toString('base64')};
 });
 const {buildPose}=require('./prepare_market_ped_pose.cjs');
 const pose=buildPose(doc,binary);
 return {source:SOURCE,sourceSha256:crypto.createHash('sha256').update(raw).digest('hex'),
         vertices:Buffer.concat(vertices).toString('base64'),levels,pose,atlas:swatch.atlas};
}
if(require.main===module)(async()=>{
 const [meshoptDir,output,source=path.join(ROOT,SOURCE)]=process.argv.slice(2);
 if(!meshoptDir||!output)throw new Error('Usage: node tools/prepare_market_ped.cjs MESHOPTIMIZER_DIRECTORY OUTPUT_JS [SOURCE_GLB]');
 const meshopt=path.resolve(meshoptDir),pkg=require(path.join(meshopt,'package.json'));
 if(pkg.name!=='meshoptimizer'||pkg.version!=='0.23.0')throw new Error('Expected meshoptimizer 0.23.0');
 const data=await prepare(path.resolve(source),meshopt);
 fs.writeFileSync(output,'/* Generated by tools/prepare_market_ped.cjs */\nDC.MarketPedData='+JSON.stringify(data)+';\n');
 console.log(JSON.stringify({bytes:fs.statSync(output).size,source:data.sourceSha256,triangles:data.levels.map(l=>l.triangles)}));
})().catch(e=>{console.error(e);process.exitCode=1;});
