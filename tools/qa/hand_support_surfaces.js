/* QA only: real quantized skin versus opposing-digit capsule envelopes.
 * Shares the source mesh decoder, not the runtime contact-fitting implementation.
 * Selected vertices have >=75% digital influence. Mixed palm webs are not covered.
 * Distances are in metres and are proxy estimates, not whole-mesh autocolllision.
 */
(function(global){
 'use strict';
 const {D,R,samples}=global.DC_FINGER_QA;
 const sub=(a,b)=>a.map((v,i)=>v-b[i]);
 function segmentDistance(p,a,b){
  const d=sub(b,a),length2=D.dot(d,d);
  const t=length2>1e-14?D.clamp(D.dot(sub(p,a),d)/length2,0,1):0;
  return Math.hypot(...sub(p,a.map((v,i)=>v+t*d[i])));
 }
 function scene(id='pistol'){
  const s=new D.Simulation(new D.World());
  Object.assign(s.player,{x:0,z:0,yaw:0,car:null});
  s.time=1.25;s.equipment.selected=id;s.equipment.aimWeight=1;
  return s;
 }
 function report(s,rendered=null){
  const m=rendered?.mount||D.Equipment.mount(s);
  const q=rendered?.pose||R.pose(D.WeaponHandling.actor(s.player,m,s.equipment),s.time);
  const dq=D.DualQuaternion.pack(q.matrices),caps={};
  for(const k of ['L','R']){
   caps[k]=[];
   for(const f of R.fingers[k])for(let j=0;j<3;j++){
    const mat=q.matrices.subarray(R.ids[f.bones[j]]*16,R.ids[f.bones[j]]*16+16);
    caps[k].push({name:f.name,j,
     a:R.transform(mat,f.joints[j]),
     b:R.transform(mat,j<2?f.joints[j+1]:f.tip),
     radius:f.radius*[.94,.85,.70][j]});
   }
  }
  const values={};
  for(const k of ['L','R'])for(const name of ['index','middle','ring','little','thumb']){
   let min=Infinity,inside=0,worst=null;
   const points=samples[k+name];
   if(!points.length)throw Error('Empty digital sample: '+k+name);
   for(const v of points){
    const p=D.DualQuaternion.transform(dq,v.p,v.j,v.w);
    for(const c of caps[k==='L'?'R':'L']){
     const distance=segmentDistance(p,c.a,c.b)-c.radius;
     if(!Number.isFinite(distance))throw Error('Nonfinite hand clearance');
     if(distance<min){min=distance;worst={other:c.name,j:c.j,p};}
     if(distance<-.001)inside++;
    }
   }
   values[k+name]={min,inside,worst,samples:points.length};
  }
  return {values};
 }
 global.DC_HAND_SUPPORT_QA=Object.freeze({scene,report,segmentDistance});
})(globalThis);
