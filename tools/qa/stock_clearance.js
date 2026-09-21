/* QA-only rejection guard for fictional prop poses. No solver or game-state writes.
 * Samples canonical face/neck and upper-jacket vertices using the supplied palette.
 * Vertex sampling and two verified stock boxes are NOT general mesh collision.
 */
(function(global){
 'use strict';
 const D=global.DC,R=D.SkinRig,parts=['face','jacket'];
 const boxes=[{center:[0,-.050,-.15],half:[.024,.026,.075]},
              {center:[0,-.0745,-.2295],half:[.026,.0395,.009]}];
 const sub=(a,b)=>a.map((v,i)=>v-b[i]);
 const vector=p=>Array.isArray(p)&&p.length===3&&p.every(Number.isFinite);
 const key=p=>p.map(v=>v.toFixed(6)).join(',');
 const triKey=p=>p.map(key).sort().join('|');
 let verifiedGeometry,assetCache;
 function verifyGeometry(geometry){
  if(geometry===undefined&&verifiedGeometry===D.EquipmentGeometry)return structuredClone(boxes);
  const supplied=geometry!==undefined,triangles=new Set();
  for(const part of geometry??D.EquipmentGeometry.build('rifle')){
   if(!part.data||part.data.length%24)throw new Error('Invalid stock geometry triangle layout');
   for(let i=0;i<part.data.length;i+=24)triangles.add(triKey([0,8,16].map(k=>Array.from(part.data.subarray(i+k,i+k+3)))));
  }
  for(const box of boxes){
   const points=[[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]
    .map(p=>p.map((v,i)=>box.center[i]+v*box.half[i]));
   for(const f of [[0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[3,7,6,2],[0,1,5,4]])
    for(const t of [[f[0],f[1],f[2]],[f[0],f[2],f[3]]])
     if(!triangles.has(triKey(t.map(i=>points[i]))))throw new Error('Stock geometry changed or is missing a complete triangle');
  }
  if(!supplied)verifiedGeometry=D.EquipmentGeometry;
  return structuredClone(boxes);
 }
 function cohort(){
  if(assetCache?.asset===D.HeroAsset)return assetCache.samples;
  const samples=[];
  for(const name of parts){
   const part=D.HeroAsset.parts.find(p=>p.name===name);
   if(!part||!Number.isInteger(part.vertices)||part.vertices<1)throw new Error('Missing canonical surface '+name);
   const bytes=Uint8Array.from(atob(part.data),c=>c.charCodeAt(0));
   if(bytes.length!==part.vertices*24)throw new Error('Invalid canonical surface buffer');
   const view=new DataView(bytes.buffer),seen=new Set();
   for(let i=0;i<part.vertices;i++){
    const b=i*24,p=[0,2,4].map(k=>view.getInt16(b+k,true)/1e4);
    // Selection is in the canonical bind, never the corrected/posed position.
    if(name==='jacket'&&p[1]<1.30)continue;
    const j=[16,17,18,19].map(k=>bytes[b+k]),w=[20,21,22,23].map(k=>bytes[b+k]/255);
    if(j.some(v=>v>=R.bones.length)||Math.abs(w.reduce((a,b)=>a+b,0)-1)>1e-6)
     throw new Error('Invalid canonical skin influences');
    // Keep coincident seam vertices if their skinning differs.
    const id=[...p,...j,...w].join(',');if(seen.has(id))continue;seen.add(id);
    samples.push({part:name,index:i,material:part.material,bind:p,j,w});
   }
  }
  assetCache={asset:D.HeroAsset,samples};return samples;
 }
 function distance(point,box){
  const q=point.map((v,i)=>Math.abs(v-box.center[i])-box.half[i]);
  return Math.hypot(...q.map(v=>Math.max(0,v)))+Math.min(Math.max(...q),0);
 }
 function inspect(sim,evidence){
  if(sim.equipment?.selected!=='rifle')throw new Error('Stock rejection is scoped to rifle');
  const {mount,pose,actor}=evidence||{};
  if(!mount||!pose||!actor||pose.matrices?.length!==R.bones.length*16||
     !Array.from(pose.matrices).every(Number.isFinite)||!Number.isFinite(pose.rootY)||
     !Number.isFinite(pose.scale)||pose.scale<=0||!Number.isFinite(mount.neckDrop))
   throw new Error('Missing supplied palette evidence or nonfinite transform');
  if([actor.x??0,actor.z??0,actor.yaw??0].some(v=>!Number.isFinite(v)))throw new Error('Invalid actor transform');
  if(typeof mount.point!=='function'||typeof mount.direction!=='function')throw new Error('Missing rigid prop frame');
  const origin=mount.point(0,0,0),basis=[[1,0,0],[0,1,0],[0,0,1]].map(p=>mount.direction(p));
  if(!vector(origin)||!basis.every(vector)||basis.some(p=>Math.abs(Math.hypot(...p)-1)>1e-5)||
     Math.abs(D.dot(basis[0],basis[1]))>1e-5||Math.abs(D.dot(basis[0],basis[2]))>1e-5||
     Math.abs(D.dot(basis[1],basis[2]))>1e-5||D.dot(D.cross(basis[0],basis[1]),basis[2])<.99999)
   throw new Error('Invalid nonfinite or nonrigid prop frame');
  verifyGeometry();const skin=cohort(),dq=D.DualQuaternion.pack(pose.matrices);
  const a=sim.appearance||D.Appearance.default(),c=Math.cos(actor.yaw||0),s=Math.sin(actor.yaw||0);
  const minimum={},samples={face:0,jacket:0};
  for(const vertex of skin){
   const shaped=D.Appearance.shapePoint(vertex.bind,vertex.material,a.build,a.face,a.neck||0);
   const fitted=D.CharacterFit.point(shaped,mount.neckDrop),p=D.DualQuaternion.transform(dq,fitted,vertex.j,vertex.w);
   const world=[(actor.x||0)+(p[0]*c+p[2]*s)*pose.scale,pose.rootY+p[1]*pose.scale,
                (actor.z||0)+(-p[0]*s+p[2]*c)*pose.scale];
   const delta=sub(world,origin),local=basis.map(v=>D.dot(delta,v));
   const d=Math.min(...boxes.map(box=>distance(local,box)));
   if(!Number.isFinite(d))throw new Error('Nonfinite surface measurement');
   samples[vertex.part]++;
   if(!minimum[vertex.part]||d<minimum[vertex.part].distance)
    minimum[vertex.part]={distance:d,index:vertex.index,bind:vertex.bind.slice(),world,local};
  }
  return {schema:1,units:'metres',source:'supplied-palette',geometryVerified:true,samples,minimum,
   cohort:'All face/neck vertices and jacket bind y >= 1.30; distinct skin influences retained',
   artisticAcceptance:false,contactAcceptance:false};
 }
 function screen(v){
  const failures=[],valid=v?.geometryVerified===true&&parts.every(p=>Number.isInteger(v.samples?.[p])&&v.samples[p]>0&&Number.isFinite(v.minimum?.[p]?.distance));
  if(!valid)failures.push('invalid');
  for(const part of parts)if(v?.minimum?.[part]?.distance<-.002)failures.push(part+'-penetration');
  return {status:failures.length?'needs-review':'clearance-screened',failures,penetrationTolerance:.002,
   artisticAcceptance:false,contactAcceptance:false,
   note:'A clear vertex sample is not full collision, garment contact, or acceptance of the pose.'};
 }
 global.DC_STOCK_CLEARANCE=Object.freeze({verifyGeometry,inspect,screen});
})(globalThis);
