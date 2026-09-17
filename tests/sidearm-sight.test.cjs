'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,scene,inspect,eyeBind}=require('./helpers/sidearm_sight.cjs');
test('settled sidearm sight line passes through the posed eye reference',()=>{
 for(const id of ['pistol','revolver']){const v=inspect(scene(id));assert.ok(v.error<.003,`${id}: ${(v.error*1000).toFixed(2)} mm from sight line`);assert.ok(v.behind>.20&&v.behind<.6);}
});
test('aim follows the fitted eye across neck length, crouch and moderate elevation',()=>{
 for(const id of ['pistol','revolver'])for(const neck of [-1,0,1])for(const crouch of[0,1])for(const pitch of[-.30,0,.30]){
  const s=scene(id);s.appearance.neckLength=neck;s.player.crouch=crouch;s.equipment.pitch=pitch;const v=inspect(s);
  assert.ok(v.error<.010,`${id}/${neck}/${crouch}/${pitch}: ${v.error}`);for(const e of Object.values(v.contacts))assert.ok(e<.012);
 }
});
test('reference uses the actual eye mesh and existing visible sight surfaces',()=>{
 const s=scene(),m=D.Equipment.mount(s);assert.ok(m.sighting);
 const v=inspect(s);assert.ok(Math.hypot(...v.eye.map((x,i)=>x-m.sighting.eye[i]))<.0001);
 const parts=D.EquipmentGeometry.build('pistol'),positions=parts.flatMap(p=>Array.from({length:p.data.length/8},(_,i)=>Array.from(p.data.subarray(i*8,i*8+3))));
 // Each authored point lies in the top plane of its original visible box.
 for(const [y,z]of[[.0735,-.01],[.0795,.22]])assert.ok(positions.filter(p=>Math.abs(p[1]-y)<1e-6&&Math.abs(p[2]-z)<.013&&Math.abs(p[0])<.023).length>=4);
 assert.ok(Math.abs(eyeBind[0]-.0308)<.0001);
});
test('neutral carry and detached reload do not snap into the sight constraint',()=>{
 const s=scene();s.equipment.aimWeight=0;assert.equal(D.Equipment.mount(s).sighting.weight,0);
 s.equipment.aimWeight=1;s.equipment.reloading=D.Equipment.get('pistol').reload*.5;
 assert.equal(D.Equipment.mount(s).sighting.weight,0);
 s.equipment.reloading=0;D.WeaponHandling.beginEquip(s);assert.equal(D.Equipment.mount(s).sighting.weight,0);
});
test('unrelated equipment retains its previous placement and has no sight correction',()=>{
 for(const id of['rifle','smg','sniper','gauss','emp','launcher','shotgun','binoculars','blade','baton','grenade','unarmed'])assert.equal(D.Equipment.mount(scene(id)).sighting,null,id);
});
test('correction is rigid, finite and bounded while extreme elevation prioritizes arm reach',()=>{
 for(const id of['pistol','revolver'])for(const pitch of[-.7,-.5,0,.5,.7])for(const crouch of[0,1]){
  const s=scene(id);s.equipment.pitch=pitch;s.player.crouch=crouch;
  const m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=R.pose(n,s.time);
  assert.ok(m.sighting.applied<=.220001);assert.ok([...q.matrices].every(Number.isFinite));
  for(const [k,t]of Object.entries(m.hands)){const p=R.handPoint(q,n,k);assert.ok(Math.hypot(p.x-t.x,p.y-t.y,p.z-t.z)<.012);}
  const axes=[[1,0,0],[0,1,0],[0,0,1]].map(m.direction);
  for(const a of axes)assert.ok(Math.abs(Math.hypot(...a)-1)<1e-9);
  assert.ok(Math.abs(D.dot(axes[0],axes[1]))<1e-9);
 }
});
test('translations and yaw preserve both sight and palm measurements',()=>{
 const s=scene(),v=inspect(s),origin=s.player;
 for(const yaw of[-2.4,.8,2.9]){Object.assign(origin,{x:6800,z:-7300,yaw});const q=inspect(s);assert.ok(Math.abs(q.error-v.error)<1e-6);assert.ok(Math.abs(q.behind-v.behind)<1e-5);}
});
test('eye alignment never mutates serialized state or changes the skeletal head transform',()=>{
 const s=scene(),before=JSON.stringify(s.serialize()),m=D.Equipment.mount(s);
 const n=D.WeaponHandling.actor(s.player,m,s.equipment),a=R.pose(n,s.time),b=R.pose({...n,handTargets:null},s.time);
 assert.deepEqual(a.matrices.subarray(R.ids.head*16,R.ids.head*16+16),b.matrices.subarray(R.ids.head*16,R.ids.head*16+16));
 assert.equal(JSON.stringify(s.serialize()),before);assert.ok(!before.includes('sighting'));
});
test('native aim and reload transitions remain bounded and restore the sight line',()=>{
 for(const id of['pistol','revolver']){
  const s=scene(id);s.equipment.aimWeight=0;D.WeaponHandling.beginEquip(s);let last,max=0,maxReload=0,priorCorrection,maxCorrection=0;
  for(let i=0;i<300;i++){
   s.time+=1/60;if(i===100){s.equipment.ammo[id].loaded=0;s.reloadWeapon();}
   s.equipmentStep(1/60,{aim:i<260});const m=D.Equipment.mount(s);
   if(last){const d=Math.hypot(...m.origin.map((x,j)=>x-last[j]));max=Math.max(max,d);if(i>=100&&i<230)maxReload=Math.max(maxReload,d);}last=m.origin;
   if(priorCorrection)maxCorrection=Math.max(maxCorrection,Math.hypot(...m.sighting.correction.map((x,j)=>x-priorCorrection[j])));priorCorrection=m.sighting.correction;
  }
  // The unchanged base draw/aim transition already reaches 63.85 mm/step.
  // Bound the added correction separately instead of mistaking base cadence for a new jump.
  assert.ok(max<.075,`${id} total origin step ${max}`);
  assert.ok(maxCorrection<.015,`${id} new correction step ${maxCorrection}`);
  assert.ok(maxReload<.03,`${id} reload origin step ${maxReload}`);
  for(let i=0;i<100;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}
  assert.ok(inspect(s).error<.003);assert.equal(s.equipment.reloading,0);
 }
});
test('recoil pivots around the grip and recovers without consuming extra ammunition',()=>{
 const s=scene();s.equipment.handling={item:'pistol',ready:1,kick:.5,velocity:0};const m=D.Equipment.mount(s);assert.ok(m.sighting.weight>.99&&m.sighting.recoilAngle>0&&m.sighting.error>.001);
 const saved=JSON.stringify(D.Equipment.snapshot(s.equipment));for(let i=0;i<240;i++){s.time+=1/60;D.WeaponHandling.step(s,1/60);}
 assert.ok(D.Equipment.mount(s).sighting.weight>.99);assert.equal(JSON.stringify(D.Equipment.snapshot(s.equipment)),saved);
});
test('a rising recoil impulse does not pull the newly aligned prop down toward the old carry line',()=>{
 const s=scene();s.equipment.handling={item:'pistol',ready:1,kick:0,velocity:0,serial:0};
 const before=D.Equipment.mount(s);s.equipment.shotSerial=1;D.WeaponHandling.step(s,1/60);const after=D.Equipment.mount(s);
 assert.ok(after.muzzle[1]>before.muzzle[1]+.002,`muzzle vertical recoil ${after.muzzle[1]-before.muzzle[1]}`);
});
test('tracked locomotion uses the same articulated eye and preserves all limb lengths',()=>{
 const s=scene(),tracker=new D.MotionTracker(4);let max=0;
 for(let i=0;i<100;i++){
  s.time+=1/60;s.player.x+=.010;s.player.z+=.022;s.player.yaw=Math.sin(i*.03)*.15;s.player.moveSpeed=1.5;s.player.walk+=.12;
  const tracked=tracker.update('player',s.player,s.time),m=D.Equipment.mount(s,tracked),n=D.WeaponHandling.actor(tracked,m,s.equipment),q=R.pose(n,s.time);
  const v=inspect(s,{mount:m,pose:q});max=Math.max(max,v.error);for(const e of Object.values(v.contacts))assert.ok(e<.012);
  for(const k of['L','R'])for(const pair of[['upperArm','forearm'],['forearm','hand']]){
   const a=R.bones[R.ids[pair[0]+k]][2],b=R.bones[R.ids[pair[1]+k]][2],mat=q.matrices.subarray(R.ids[pair[0]+k]*16,R.ids[pair[0]+k]*16+16);
   const aa=R.transform(mat,a),bb=R.transform(mat,b);assert.ok(Math.abs(Math.hypot(...aa.map((v,j)=>v-bb[j]))-Math.hypot(...a.map((v,j)=>v-b[j])))<1e-6);
  }
 }
 assert.ok(max<.010,`tracked sight error ${max}`);
});
