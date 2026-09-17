/* QA only: stable bind-space palm/thumb band, including low thumb weights.
   Selection deliberately does not use a skin-weight threshold: rebinding cannot
   make a failing vertex disappear from the test. No renderer/runtime dependency. */
(function(global){
'use strict';
const D=global.DC,R=D.SkinRig,F=global.DC_FINGER_QA;
const part=D.HeroAsset.parts.find(p=>p.name==='skin'),raw=Uint8Array.from(atob(part.data),c=>c.charCodeAt(0)),view=new DataView(raw.buffer),samples={};
for(const side of['L','R']){
 const wx=R.bones[R.ids['hand'+side]][2][0],out=[],seen=new Set();
 for(let i=0;i<part.vertices;i++){
  const b=i*24,p=[0,2,4].map(k=>view.getInt16(b+k,true)/10000);
  if(Math.abs(p[0]-wx)>.055||p[1]<.820||p[1]>.885||p[2]<0||p[2]>.048)continue;
  const key=p.join();if(seen.has(key))continue;seen.add(key);
  out.push({p,j:[16,17,18,19].map(k=>raw[b+k]),w:[20,21,22,23].map(k=>raw[b+k]/255)});
 }
 samples[side]=out;
}
function localPoint(s,m,q,dq,v,key){
 let p=D.DualQuaternion.transform(dq,v.p,v.j,v.w);const n=s.player,c=Math.cos(n.yaw||0),sn=Math.sin(n.yaw||0);
 p=[(n.x||0)+p[0]*c+p[2]*sn,p[1]+q.rootY,(n.z||0)-p[0]*sn+p[2]*c].map((v,i)=>v-m.origin[i]);
 p=[[1,0,0],[0,1,0],[0,0,1]].map(ax=>D.dot(p,m.direction(ax)));
 if(key==='magazine'||key==='pistolMagazine'){
  const o=m.magazine.offset,t=m.magazine.rotation[2],pi=m.magazine.pivot;
  p=p.map((v,i)=>v-o[i]-pi[i]);p=[p[0]*Math.cos(t)+p[1]*Math.sin(t),-p[0]*Math.sin(t)+p[1]*Math.cos(t),p[2]].map((v,i)=>v+pi[i]);
 }
 return p;
}
function stats(s,side,key,rendered=null){
 const m=rendered?.mount||D.Equipment.mount(s),q=rendered?.pose||R.pose(D.WeaponHandling.actor(s.player,m,s.equipment),s.time),dq=D.DualQuaternion.pack(q.matrices);
 let min=Infinity,worst,inside=0;
 for(const v of samples[side]){const p=localPoint(s,m,q,dq,v,key),d=F.shapeSDF(p,F.shapes[key]);if(d<0)inside++;if(d<min){min=d;worst={bind:v.p,local:p};}}
 return{samples:samples[side].length,min,inside,worst};
}
global.DC_THENAR_QA={samples,stats,localPoint};
})(globalThis);
