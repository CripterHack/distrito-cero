'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,stats}=require('./helpers/finger_surfaces.cjs');
const {scene,report}=require('./helpers/hand_support.cjs');
test('support middle and ring skin do not cross the dominant fingers on sidearms',()=>{
 for(const id of ['pistol','revolver']){const a=report(scene(id));for(const f of ['Lindex','Lmiddle','Lring','Lthumb','Rmiddle','Rring'])assert.ok(a.values[f].min>-.002,`${id}/${f} enters other hand by ${(-a.values[f].min*1000).toFixed(2)}mm`);}
});
test('support grip does not exchange hand overlap for penetration of the cosmetic handle',()=>{
 for(const id of ['pistol','revolver'])for(const f of ['index','middle','ring','little','thumb']){const v=stats(scene(id),'L',f,'grip');assert.ok(v.min>-.003,`${id}/${f}: ${v.min}`);}
});
test('the support closes on the other hand instead of floating far from it',()=>{
 for(const id of ['pistol','revolver']){const a=report(scene(id));for(const f of ['Lindex','Lmiddle','Lring'])assert.ok(a.values[f].min<.006,`${id}/${f} contact gap ${a.values[f].min}`);}
});
test('hand separation holds when aiming, moving, crouching and pulling the trigger',()=>{
 for(const id of ['pistol','revolver'])for(const [aim,pitch,crouch,trigger]of[[0,-.4,0,false],[1,.3,1,false],[1,-.3,1,true],[.5,.15,.5,true]]){
  const s=scene(id);Object.assign(s.equipment,{aimWeight:aim,pitch,trigger});Object.assign(s.player,{crouch,moveSpeed:1.7,walk:2.1});const a=report(s);
  for(const [f,v]of Object.entries(a.values))assert.ok(v.min>-.002,`${id}/${f}/${trigger}: ${v.min}`);
 }
});
test('support poses do not alter dominant hands, wrist anchors, segment lengths or game data',()=>{
 const s=scene('pistol'),saved=JSON.stringify(s.serialize()),m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=R.pose(n,s.time),old=structuredClone(n);
 for(const f of ['index','middle','ring','little'])old.handGrips.L.fingers[f]=[.6,.8,.5];delete old.handGrips.L.thumbOpposition;
 const other=R.pose(old,s.time),leftIds=new Set(R.fingers.L.flatMap(f=>f.bones.map(b=>R.ids[b])));
 for(let i=0;i<R.bones.length;i++)if(!leftIds.has(i))assert.deepEqual(q.matrices.subarray(i*16,i*16+16),other.matrices.subarray(i*16,i*16+16));
 for(const f of R.fingers.L)for(let j=0;j<3;j++){const a=f.joints[j],b=j<2?f.joints[j+1]:f.tip,mat=q.matrices.subarray(R.ids[f.bones[j]]*16,R.ids[f.bones[j]]*16+16),aa=R.transform(mat,a),bb=R.transform(mat,b);assert.ok(Math.abs(Math.hypot(...aa.map((v,i)=>v-bb[i]))-Math.hypot(...a.map((v,i)=>v-b[i])))<1e-6);}
 assert.equal(JSON.stringify(s.serialize()),saved);
});
test('short-prop recargas retain settled support and bounded finger transitions',()=>{
 for(const id of ['pistol','revolver']){const s=scene(id);s.equipWeapon(id);D.WeaponHandling.beginEquip(s);s.equipment.handling.ready=1;for(let i=0;i<90;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}
  const before=D.Equipment.mount(s).grips.L;s.equipment.ammo[id].loaded=0;s.reloadWeapon();let prev=null,max=0;
  for(let i=0;i<300;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=D.Equipment.mount(s),v=Object.values(m.grips.L.fingers).flat().concat(m.grips.L.thumbOpposition||[0,0,0]);if(prev)max=Math.max(max,...v.map((n,j)=>Math.abs(n-prev[j])));prev=v;}
  assert.ok(max<.25,`${id}: ${max}`);assert.equal(s.equipment.reloading,0);assert.deepEqual(D.Equipment.mount(s).grips.L,before);
 }
});
test('opposing-envelope helper handles segment endpoints and zero-length fixtures',()=>{
 const {segmentDistance}=require('./helpers/hand_support.cjs');
 assert.equal(segmentDistance([0,0,0],[1,0,0],[1,0,0]),1);
 assert.equal(segmentDistance([1,1,0],[0,0,0],[2,0,0]),1);
 assert.equal(segmentDistance([3,0,0],[0,0,0],[2,0,0]),1);
});
test('world translation and rotation do not change local hand clearance',()=>{
 const s=scene('pistol'),base=report(s).values;
 for(const yaw of [-2.3,.6,2.7]){Object.assign(s.player,{yaw,x:7200,z:-6400});const got=report(s).values;for(const k of Object.keys(base))assert.ok(Math.abs(got[k].min-base[k].min)<.0001,`${yaw}/${k}`);}
});
test('changing equipment clears the support presentation without persisting a pose',()=>{
 const s=scene('pistol'),before=JSON.stringify(s.serialize());D.Equipment.mount(s);assert.equal(JSON.stringify(s.serialize()),before);
 for(const id of ['rifle','gauss','emp','binoculars','grenade','baton','blade']){s.equipWeapon(id);const m=D.Equipment.mount(s);assert.notEqual(m.fingerContacts.L?.profile,'sidearm-wrap-L');}
 s.equipWeapon('pistol');for(let i=0;i<60;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}
 const saved=JSON.stringify(s.serialize());assert.ok(!saved.includes('sidearm-wrap-L'));
 assert.equal(D.Equipment.mount(s).fingerContacts.L.profile,'sidearm-wrap-L');
});
