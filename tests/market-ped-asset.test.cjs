'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
function load(){
 const ctx=vm.createContext({DC:{},atob,Float32Array,Uint8Array,DataView});
 for(const name of ['data','pose','asset'])vm.runInContext(fs.readFileSync(path.join(root,'src','market-ped-'+name+'.js'),'utf8'),ctx);
 return ctx.DC;
}
test('market pedestrian comes from the reviewed skinned GLB, with two budgeted LODs',()=>{
 const {MarketPedAsset:asset,MarketPedData:data}=load();
 assert.equal(data.sourceSha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,data.source))).digest('hex'));
 assert.equal(asset.levels.length,2);
 assert.match(asset.atlas,/^data:image\/webp;base64,UklGR/);
 assert.ok(asset.levels[0].triangles<=12000 && asset.levels[0].triangles>4000);
 assert.ok(asset.levels[1].triangles<asset.levels[0].triangles*.62);
 for(const [i,level] of asset.levels.entries()){
  const vertices=asset.decodeLevel(i);
  assert.equal(vertices.length,level.triangles*3*16);
  let floor=Infinity,top=-Infinity,arms=0;
  const influenced=new Set();
  for(let k=0;k<vertices.length;k+=16){
   const v=vertices.subarray(k,k+16);
   assert.ok(v.every(Number.isFinite));
   assert.ok(Math.abs(Math.hypot(...v.subarray(3,6))-1)<.0001);
   assert.ok(v[6]>=0&&v[6]<=1&&v[7]>=0&&v[7]<=1);
   assert.ok(Math.abs(v[12]+v[13]+v[14]+v[15]-1)<1e-6);
   for(let j=0;j<4;j++){assert.ok(Number.isInteger(v[8+j])&&v[8+j]>=0&&v[8+j]<49);if(v[12+j]>0)influenced.add(v[8+j]);}
   floor=Math.min(floor,v[1]);top=Math.max(top,v[1]);arms=Math.max(arms,Math.abs(v[0]));
  }
  assert.ok(floor>=-.001&&floor<=.003&&top>1.84&&top<1.86&&arms>.89);
  assert.equal(influenced.size,49);
 }
});

test('street meshes keep the repaired finger walls, both knee edges and source skin weights',()=>{
 const {accessor,decodeGlb}=require('../tools/export_human_tangents.cjs');
 const {MarketPedAsset:asset,MarketPedData:data}=load();
 const {document:doc,binary}=decodeGlb(fs.readFileSync(path.join(root,data.source)));
 const coords=new Map(), influences=new Map(), baseline=new Map(), opposed=new Set(), kneeEdges=[];
 const xyz=p=>p.join(','), edge=(a,b)=>a<b?a+':'+b:b+':'+a;
 const triangle=(a,b,c)=>[a,b,c].sort((a,b)=>a-b).join(':');
 function normalDot(p,n){
  const u=p[1].map((q,k)=>q-p[0][k]),v=p[2].map((q,k)=>q-p[0][k]);
  const cross=[u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0]];
  assert.ok(Math.hypot(...cross)>1e-10,'a tiny source facet collapsed');
  return cross.reduce((out,c,k)=>out+c*(n[0][k]+n[1][k]+n[2][k]),0);
 }
 const skin=(ids,weights)=>ids.map((x,k)=>x+'/'+weights[k]).join(',');
 const incidence=(counts,tri)=>tri.forEach((v,i)=>{
  const key=edge(v,tri[(i+1)%3]);counts.set(key,(counts.get(key)||0)+1);
 });
 let wallFaces=0;
 const wallTriangles=[];
 for(const [pi,p] of doc.meshes[0].primitives.entries()){
  const attr=Object.fromEntries(Object.entries(p.attributes).map(([key,i])=>[key,accessor(doc,binary,i)]));
  const indices=accessor(doc,binary,p.indices);
  const row=(a,i)=>Array.from({length:a.width},(_,k)=>a.value(i,k));
  const ids=[];
  for(let i=0;i<attr.POSITION.a.count;i++){
   const key=xyz(row(attr.POSITION,i));if(!coords.has(key))coords.set(key,coords.size);
   ids.push(coords.get(key));
   const weights=skin(row(attr.JOINTS_0,i),row(attr.WEIGHTS_0,i));
   if(!influences.has(key))influences.set(key,new Set());
   influences.get(key).add(weights);
  }
  if(pi===0)for(const [a,b] of [[6155,6194],[12708,12730]])kneeEdges.push(edge(ids[a],ids[b]));
  for(let i=0;i<indices.a.count;i+=3){
   const order=[0,1,2].map(k=>indices.value(i+k)),tri=order.map(k=>ids[k]);
   incidence(baseline,tri);
   if(pi===1){wallFaces++;wallTriangles.push(triangle(...tri));}
   if(normalDot(order.map(k=>row(attr.POSITION,k)),order.map(k=>row(attr.NORMAL,k)))<0)opposed.add(triangle(...tri));
  }
 }
 for(const [lod,level] of asset.levels.entries()){
  const v=asset.decodeLevel(lod),edges=new Map();
  for(let j=0;j<level.triangles;j++){
   const start=j*48,tri=[],p=[],n=[],uv=[];
   for(let h=0;h<3;h++){
    const i=start+h*16,pos=Array.from(v.subarray(i,i+3)),key=xyz(pos);
    p.push(pos);n.push(Array.from(v.subarray(i+3,i+6)));uv.push(v.subarray(i+6,i+8));
    tri.push(coords.get(key));
    const weights=skin(Array.from(v.subarray(i+8,i+12)),Array.from(v.subarray(i+12,i+16),w=>Math.round(w*255)));
    assert.ok(influences.get(key)?.has(weights),'source bone/weight tuple');
   }
   incidence(edges,tri);
   if(normalDot(p,n)<0)assert.ok(opposed.has(triangle(...tri)),'new flipped surface');
   if(j>=level.triangles-wallFaces)assert.equal(triangle(...tri),wallTriangles[j-level.triangles+wallFaces]);
   else{
    const a=uv[0],b=uv[1],c=uv[2],det=(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
    assert.ok(det>0,'new folded textured chart at triangle '+j+' (LOD '+lod+')');
   }
  }
  for(const key of kneeEdges)assert.ok(edges.has(key),'authored crease edge');
  const irregular=map=>[...map].filter(([,count])=>count!==2).sort();
  assert.deepEqual(irregular(edges),irregular(baseline),'no new openings or non-manifold edges');
 }
});
