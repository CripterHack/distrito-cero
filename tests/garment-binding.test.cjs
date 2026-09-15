/* SPEC-003 / #6: test real garment vertices, not just palmar IK pivots. */
'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-fit','weapon-handling','equipment','equipment-simulation','character-motion','skin-rig','dual-quaternion','hero-asset'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const D=DC,part=D.HeroAsset.parts.find(p=>p.name==='jacket'),buffer=Buffer.from(part.data,'base64'),unique=new Map();
for(let i=0;i<part.vertices;i++){
 const off=i*24,p=[0,2,4].map(k=>buffer.readInt16LE(off+k)/1e4),key=p.join(',');
 if(!unique.has(key))unique.set(key,{p,j:[16,17,18,19].map(k=>buffer[off+k]),w:[20,21,22,23].map(k=>buffer[off+k]/255)});
}
const sleeves=[...unique.values()].filter(v=>v.p[1]<1.24&&Math.abs(v.p[0])>.195),trunk=[...unique.values()].filter(v=>v.p[1]<1.24&&Math.abs(v.p[0])<.18);
function influence(v,match){return v.j.reduce((n,j,i)=>n+(match(D.SkinRig.bones[j][0])?v.w[i]:0),0);}
function segmentDistance(p,a,b){const ab=b.map((v,i)=>v-a[i]),t=Math.max(0,Math.min(1,D.dot(p.map((v,i)=>v-a[i]),ab)/D.dot(ab,ab)));return Math.hypot(...p.map((v,i)=>v-a[i]-t*ab[i]));}
test('disconnected lower sleeves do not inherit chest, spine or pelvis motion',()=>{
 assert.ok(sleeves.length>1500,'real lower sleeve sample');
 const max=Math.max(...sleeves.map(v=>influence(v,n=>['pelvis','spine','chest','neck','head'].includes(n))));
 assert.ok(max<=1/255,`detached sleeve torso influence ${max}`);
});
test('lower trunk does not follow arm, wrist or clavicle contacts',()=>{
 assert.ok(trunk.length>2000);
 const max=Math.max(...trunk.map(v=>influence(v,n=>/Arm|forearm|hand|clavicle/.test(n))));
 assert.ok(max<=1/255,`trunk arm influence ${max}`);
});
test('posed inner sleeve remains around its arm in aim, crouch and reload',()=>{
 const s=new D.Simulation(new D.World(1337));Object.assign(s.player,{x:4,z:36,yaw:0,car:null,moveSpeed:0});s.time=1.25;
 const sample=sleeves.filter((v,i)=>i%7===0);let worst=0;
 for(const id of ['pistol','rifle','gauss','emp','binoculars'])for(const crouch of[0,1])for(const progress of[0,.52]){
  s.equipment.selected=id;s.equipment.aimWeight=1;s.player.crouch=crouch;s.equipment.reloading=progress?(1-progress)*(D.Equipment.get(id).reload||0):0;
  const m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=D.SkinRig.pose(n,s.time),dq=D.DualQuaternion.pack(q.matrices);
  for(const v of sample){
   const k=v.p[0]<0?'L':'R',ps=['upperArm','forearm','hand'].map(name=>{const j=D.SkinRig.ids[name+k];return D.SkinRig.transform(q.matrices.subarray(j*16,j*16+16),D.SkinRig.bones[j][2]);});
   const p=D.DualQuaternion.transform(dq,v.p,v.j,v.w),distance=Math.min(segmentDistance(p,ps[0],ps[1]),segmentDistance(p,ps[1],ps[2]));worst=Math.max(worst,distance);
   assert.ok(distance<.090,`${id} crouch=${crouch} reload=${progress} vertex=${v.p} sleeve-to-arm=${distance}`);
  }
 }
 console.log('lowerSleeveMaxDistanceM',worst);
});
