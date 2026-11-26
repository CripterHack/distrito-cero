'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const assert=require('node:assert/strict'),{test}=require('node:test');
const root=path.resolve(__dirname,'..');
for(const name of ['core','character-fit','character-motion','skin-rig','dual-quaternion','hero-asset','hair-geometry','crowd-geometry','graphics-resources','renderer'])
 vm.runInThisContext(fs.readFileSync(path.join(root,'src',name+'.js'),'utf8'));
const NativeRenderer=DC.Renderer;
vm.runInThisContext(fs.readFileSync(path.join(root,'src/realism-renderer.js'),'utf8'));
const NativeSkin=DC.Renderer;
DC.Simulation=class{};
for(const name of ['appearance','human-materials'])vm.runInThisContext(fs.readFileSync(path.join(root,'src',name+'.js'),'utf8'));
const castSource=fs.readFileSync(path.join(root,'src/cast-renderer.js'),'utf8');
const hash=data=>crypto.createHash('sha256').update(Buffer.from(data.buffer,data.byteOffset,data.byteLength)).digest('hex');
function fixture(){
 const calls=[],creations=[],deleted=[],uploads=new Map(),draws=[],textureUploads=[];let serial=0,boundBuffer,boundVAO;
 const methods={isContextLost:()=>false,bindBuffer(_,buffer){boundBuffer=buffer;},bindVertexArray(vao){boundVAO=vao;},
  bufferData(_,data){if(ArrayBuffer.isView(data))uploads.set(boundBuffer,Float32Array.from(data));},
  texSubImage2D(...args){textureUploads.push({width:args[4],height:args[5],data:Float32Array.from(args[8])});},
  getParameter:()=>null,drawArraysInstanced(mode,first,count,instances){draws.push({vao:boundVAO,count,instances});}};
 for(const kind of ['Buffer','Texture','Framebuffer','Renderbuffer','VertexArray','Program','Shader']){
  methods['create'+kind]=()=>({kind,id:++serial});methods['delete'+kind]=handle=>{if(handle)deleted.push(handle);};
 }
 const gl=new Proxy(methods,{get:(target,key)=>key in target?target[key]:typeof key==='string'&&key===key.toUpperCase()?key:()=>{}});
 class Base{
  constructor(){
   this.gl=gl;this.resources=new DC.GLResources(gl);this.disposed=false;this.uniforms=new Map();
   this.heroPalette=DC.SkinRig.rest();this.heroParts=[];this.meshes={};this.static={};this.dynamic={};this.assetParts=[];this.visualStats={};
   this.quality='balanced';this.world={crates:[]};this.renderOrigin=[1000,2000];
   for(const part of DC.HeroAsset.parts){const key='hero_'+part.name;this.meshes[key]=this.createSkinMesh(DC.Realism.decode(part));this.static[key]=[];this.dynamic[key]=[];this.heroParts.push({...part,data:undefined,key});}
   for(const key of ['body','smoke']){this.meshes[key]=this.createSkinMesh(new Float32Array());this.static[key]=[];this.dynamic[key]=[];}
  }
  createSkinMesh(data){const mesh=NativeSkin.prototype.createSkinMesh.call(this,data);mesh.data=data;creations.push(mesh);return mesh;}
  createMesh(data){return NativeRenderer.prototype.createMesh.call(this,data);}
  deleteMesh(mesh){return NativeSkin.prototype.deleteMesh.call(this,mesh);}
  renderReactive(){}
 }
 Object.setPrototypeOf(Base.prototype,NativeRenderer.prototype);
 const D={...DC,Renderer:Base,CrowdGeometry:{reduce(data,cell,options){calls.push({data,cell,options});return DC.CrowdGeometry.reduce(data,cell,options);}}};
 vm.runInNewContext(castSource,{DC:D,Float32Array,Uint16Array,atob});
 const renderer=new D.CastRenderer();
 return {renderer,calls,creations,deleted,uploads,draws,textureUploads};
}
function part(renderer,lod,name){return renderer.lodParts[lod].find(p=>p.name===name);}
function snapshot(renderer,lod,excludeJacket=false){
 const h=crypto.createHash('sha256');
 for(const p of renderer.lodParts[lod])if(!excludeJacket||p.name!=='jacket'){
  const data=renderer.meshes[p.key].data;h.update(p.name+':'+p.vertices+':');h.update(Buffer.from(data.buffer,data.byteOffset,data.byteLength));
 }
 return h.digest('hex');
}
const sourceBefore='df11a1ce85b35ea16c288d4380661af0f69fa318a321c86cbae039382daaec4b';
const built=fixture();
// Regression cases
// Frozen on the pre-policy v0.20.24 constructor, including face seam welding.
const baseline={lod0:'3c2883002e8cf02cd3768be0000dd687496cef0845f2fd5acaefaee0607db3db',
 otherLod1:'78ecb683cd05bc4d2b0355ee57682ac8b03fae49d9fec4f19abfc1c4bc25926e',
 otherLod2:'31a43771ad8e45c9dd2b2bc818c88eec8f9fbbfd922e26591164d373222f271c',
 legacyJacket:'3d7125a498abde6def16c410be2e4b768cc20a0faa866de94a7c278972c9525f'};
test('preserves the authored lateral occluders and their posterior transition in every reduced jacket', () => {
 const renderer = built.renderer;
 const full = renderer.meshes[part(renderer, 0, 'jacket').key].data;
 // The two camera rays through skin anchor 9216 hit different surfaces.
 // These are the original torso and collar triangles in the canonical asset.
 const triangleKey = (data, offset) => Buffer.from(
  data.buffer, data.byteOffset + offset * Float32Array.BYTES_PER_ELEMENT,
  48 * Float32Array.BYTES_PER_ELEMENT
 ).toString('hex');
 for (const lod of [1, 2]) {
  const mesh = renderer.meshes[part(renderer, lod, 'jacket').key].data;
  const keys = new Set();
  for (let offset = 0; offset < mesh.length; offset += 48) keys.add(triangleKey(mesh, offset));
  // 8621 is the posterior transition at skin anchor 9352 during a right turn.
  for (const id of [9815, 15887, 8621]) {
   assert.ok(keys.has(triangleKey(full, id * 48)), 'Missing source occluder ' + id + ' at LOD' + lod);
  }
 }
});
test('restores the authored neckline boundary without introducing new open edges at the join', () => {
 function openEdges(data) {
  const counts = new Map();
  for (let i = 0; i < data.length; i += 48) {
   const points = [0,16,32].map(offset => data.subarray(i+offset,i+offset+3).join(':'));
   for (let k = 0; k < 3; k++) {
    const key = [points[k],points[(k+1)%3]].sort().join('/');
    counts.set(key,(counts.get(key)||0)+1);
   }
  }
  return new Set([...counts].filter(([,count]) => count===1).map(([key]) => key));
 }
 const source = built.renderer.meshes[part(built.renderer,0,'jacket').key].data;
 const authored = openEdges(source);
 const previous = openEdges(DC.CrowdGeometry.reduce(source,.027));
 const candidate = openEdges(built.renderer.meshes.crowd1_jacket.data);
 assert.equal(authored.size,128);
 assert.ok([...authored].every(edge => candidate.has(edge)));
 assert.ok([...candidate].every(edge => authored.has(edge) || previous.has(edge)));
 assert.equal([...candidate].filter(edge => !authored.has(edge)).length,16);
});
test('far jacket reuses the intermediate entry, mesh and detailed 3965-triangle buffer',()=>{
 const r=built.renderer,a=part(r,1,'jacket'),b=part(r,2,'jacket');
 assert.equal(b,a);assert.equal(b.key,'crowd1_jacket');assert.equal(b.vertices/3,3965);
 assert.equal(hash(r.meshes[b.key].data),'1b5cdc0cdd8ac52f9c32f469df539cc9c1287ea3734c8e5932e832cbb2837069');
 assert.equal(r.visualStats.lodTriangles[2],9119);
});
test('the constructor reduces jacket once and allocates no LOD2 jacket resource or queue',()=>{
 const r=built.renderer,source=DC.Realism.decode(DC.HeroAsset.parts.find(p=>p.name==='jacket')),sourceHash=hash(source);
 const calls=built.calls.filter(c=>c.data.length===source.length&&hash(c.data)===sourceHash);
 assert.equal(calls.length,1);assert.equal(calls[0].cell,.027);
 assert.equal(built.creations.filter(m=>m===r.meshes.crowd1_jacket).length,1);
 for(const store of [r.meshes,r.static,r.dynamic])assert.equal(Object.hasOwn(store,'crowd2_jacket'),false);
 const keys=Object.keys(r.meshes).filter(k=>r.meshes[k]===r.meshes.crowd1_jacket);assert.deepEqual(keys,['crowd1_jacket']);
});
test('every LOD0 part and every other LOD1 part retains its pre-policy bytes',()=>{
 const source = built.renderer.meshes[part(built.renderer,0,'jacket').key].data;
 assert.equal(hash(DC.CrowdGeometry.reduce(source,.027)),baseline.legacyJacket);
 assert.equal(snapshot(built.renderer,0),baseline.lod0);assert.equal(snapshot(built.renderer,1,true),baseline.otherLod1);
 assert.deepEqual(Array.from(built.renderer.visualStats.lodTriangles.slice(0,2)),[77481,16802]);
});
test('other LOD2 parts including welded face and canonical source remain unchanged',()=>{
 assert.equal(snapshot(built.renderer,2,true),baseline.otherLod2);
 assert.equal(hash(Buffer.from(fs.readFileSync(path.join(root,'src/hero-asset.js')))),sourceBefore);
 const face=built.calls.filter(c=>c.options.weldUVSeams);assert.equal(face.length,2);
 assert.equal(face[0].options.clusterUV,face[1].options.clusterUV);
});
test('native renderPerson, upload and draw share one jacket batch with two independent actor slots',()=>{
 const {renderer:r,uploads,draws,textureUploads}=built;
 // Exclude the player and scenery, while using the real NPC traversal,
 // renderPerson, motion/rig, add, dynamic upload and instanced draw methods.
 r.renderPlayer=()=>{};
 const player={x:1000,z:2000,y:0,yaw:0,car:null};
 const near={id:'near',x:1020,z:2000,y:0,yaw:.2,variant:3,speed:0};
 const far={id:'far',x:1060,z:2000,y:0,yaw:-.4,variant:14,speed:0,crouch:.4};
 const sim={time:1.25,player,peds:[near,far],cars:[],collected:[],target:()=>null,actor:()=>null};
 r.updateDynamic(sim);
 const key='crowd1_jacket',mesh=r.meshes[key],queue=r.dynamic[key],packed=uploads.get(mesh.dynamicBuffer);
 assert.equal(mesh.dynamicCount,2);assert.equal(queue.length,32);assert.equal(packed.length,32);
 assert.deepEqual([queue[15],queue[31]],[201,202]);assert.deepEqual([packed[15],packed[31]],[201,202]);
 assert.deepEqual([packed[0],packed[2],packed[16],packed[18]],[20,0,60,0]);
 assert.equal(r.castCursor,3);assert.deepEqual(Array.from(r.castStats.lod),[0,1,1]);assert.equal(r.castStats.actors,2);
 assert.equal(r.castStats.triangles,16802+9119);assert.equal(r.castStats.paletteRows,3);
 const distinctKeys=new Set([...r.lodParts[1],...r.lodParts[2]].map(p=>p.key));
 assert.equal(r.castStats.drawBatches,distinctKeys.size);
 assert.equal(textureUploads.length,3);assert.ok(textureUploads.every(t=>t.height===3&&t.data.every(Number.isFinite)));
 const stride=DC.SkinRig.paletteStride;
 assert.notDeepEqual(r.posePixels.slice(stride,2*stride),r.posePixels.slice(2*stride,3*stride));
 assert.notDeepEqual(r.appearancePixels.slice(8,16),r.appearancePixels.slice(16,24));
 r.drawMeshes();
 assert.deepEqual(draws.filter(d=>d.vao===mesh.vao),[{vao:mesh.vao,count:3965*3,instances:2}]);
 // A second frame clears the shared queue, without a stale far actor/slot.
 sim.time+=.016;sim.peds=[near];r.updateDynamic(sim);
 assert.equal(mesh.dynamicCount,1);assert.equal(r.dynamic[key].length,16);assert.equal(r.dynamic[key][15],201);
 assert.equal(r.castStats.triangles,16802);assert.deepEqual(Array.from(r.castStats.lod),[0,1,0]);
});
test('per-part reuse leaves balanced and eco actor LOD hysteresis unchanged',()=>{
 for(const [quality,distances]of [['balanced',[20,50,40,36,10,18,20]],['eco',[20,30,23,22,7,10,11]]]){
  const state={quality,lodHistory:new Map()},actor={id:'test'};
  const results=distances.map(d=>built.renderer.chooseLOD.call(state,actor,false,d));
  assert.deepEqual(results,[1,2,2,1,0,0,1]);
  assert.equal(built.renderer.chooseLOD.call(state,{id:'player'},true,100),0);
  assert.equal(state.lodHistory.has('player'),false);
 }
});
test('shared jacket owns one resource set across idempotent disposal and reconstruction',()=>{
 const {renderer:r,deleted}=built,oldMesh=r.meshes.crowd1_jacket,live=r.resources.stats().total,before=deleted.length;
 r.dispose();assert.equal(deleted.length-before,live);assert.equal(new Set(deleted).size,deleted.length);
 assert.equal(deleted.filter(h=>h===oldMesh.vao).length,1);assert.equal(deleted.filter(h=>h===oldMesh.vbo).length,1);
 assert.equal(deleted.filter(h=>h===oldMesh.dynamicBuffer).length,1);
 const after=deleted.length;r.dispose();assert.equal(deleted.length,after);assert.equal(Object.keys(r.meshes).length,0);
 const rebuilt=fixture(),next=rebuilt.renderer,mesh=next.meshes.crowd1_jacket;
 assert.notEqual(mesh.vao,oldMesh.vao);assert.equal(part(next,1,'jacket'),part(next,2,'jacket'));
 assert.equal(next.dynamic.crowd1_jacket.length,0);assert.equal(next.lodHistory.size,0);assert.equal(next.castCursor,1);
 next.dispose();assert.equal(new Set(rebuilt.deleted).size,rebuilt.deleted.length);
});
