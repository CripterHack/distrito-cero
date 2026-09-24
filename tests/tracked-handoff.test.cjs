'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
// Exercise the actual UI/renderer methods without allocating a WebGL context.
D.Renderer=class {};D.App=class {};D.Audio=class {};
vm.runInThisContext(fs.readFileSync('src/equipment-renderer.js','utf8'));
vm.runInThisContext(fs.readFileSync('src/equipment-ui.js','utf8'));
const items=['rifle','smg','shotgun','sniper'];
const xyz=p=>[p.x,p.y,p.z],distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function moving(item,throttle=.6,frames=30){
 const s=scene(item),tracker=new D.MotionTracker(4);
 Object.assign(s.player,{x:4,z:36,y:0,yaw:0,walk:0,moveSpeed:0,vx:0,vz:0,vy:0});
 s.peds.forEach(n=>n.hidden=true);s.dynamics.props=[];
 s.cars.forEach((c,i)=>Object.assign(c,{x:5000+i*6,z:5000,driver:null,parked:true,speed:0}));
 D.WeaponHandling.beginEquip(s);
 let n;for(let i=0;i<180+frames;i++){s.step(1/60,{aim:true,throttle:i<180?0:throttle,steer:0,fire:false});n=tracker.update('player',s.player,s.time);}
 return {s,tracker,n};
}
function read(s,n){const mount=D.WeaponHandling.present(s,n),actor=D.WeaponHandling.actor(n,mount,s.equipment),pose=R.pose(actor,s.time);return {mount,actor,pose,palms:['L','R'].map(k=>xyz(R.palmPoint(pose,actor,k)))};}
for(const from of items)test(from+' selection captures the same tracked actor that the renderer presents',()=>{
 for(const to of items.filter(x=>x!==from))for(const frames of [30,60]){
  const {s,tracker,n}=moving(from,.6,frames),before=read(s,n),ammo=JSON.stringify(s.equipment.ammo),motion=JSON.stringify(n.motion),time=s.time;
  s.cancelEquipment();assert.equal(s.equipWeapon(to,n),true);
  const after=read(s,n);
  for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],after.palms[k])<1e-5,`${from}->${to} frame ${frames} palm ${k}: ${distance(before.palms[k],after.palms[k])}m`);
  assert.equal(after.pose.rootY,before.pose.rootY,'selection preserves the tracked foot support');
  assert.equal(JSON.stringify(n.motion),motion,'selection cannot mutate tracker memory');
  assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.time,time);
  assert.equal(s.equipment.selected,to);assert.equal(s.equipment.handling.ready,0);assert.equal(s.equipment.trigger,false);
  const saved=JSON.stringify(s.serialize()),handling=JSON.stringify(s.equipment.handling),logical=D.Equipment.mount(s);
  for(let i=0;i<3;i++)read(s,n);
  assert.equal(JSON.stringify(s.serialize()),saved);assert.equal(JSON.stringify(s.equipment.handling),handling);
  const plain={...s,equipment:{...s.equipment,handling:{...s.equipment.handling}}};delete plain.equipment.handling.handoff;
  assert.deepEqual(logical.muzzle,D.Equipment.mount(plain).muzzle,'gameplay does not receive a tracked/interpolated firing origin');
  const relative=v=>v.palms.map(p=>p.map((x,i)=>x-[v.actor.x,v.actor.y||0,v.actor.z][i]));
  let last=relative(after);
  for(let i=0;i<50;i++){
   s.step(1/60,{aim:false,throttle:.6,steer:0,fire:false});const tracked=tracker.update('player',s.player,s.time),v=read(s,tracked),points=relative(v);
   for(let k=0;k<2;k++)assert.ok(distance(points[k],last[k])<.030,`${from}->${to} native step ${i} palm ${k}`);
   for(const k of ['L','R'])assert.ok(distance(xyz(R.palmPoint(v.pose,v.actor,k)),xyz(v.mount.palmContacts[k]))<.012,'tracked IK retains the contact');
   last=points;
  }
  assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
test('keyboard/menu selection transfers presentation context before clearing held inputs',()=>{
 const {s,n}=moving('rifle'),before=read(s,n);let reads=0;
 const app={sim:s,renderer:{camera:{weaponPitch:.1},handlingActor(sim){assert.equal(sim,s);assert.equal(sim.equipment.aiming,true,'read precedes cancellation');reads++;return n;}},
  clearWeaponInput(){s.cancelEquipment();},toast(){},updateEquipmentHUD(){},closeArsenal(){this.closed=true;}};
 D.EquipmentApp.prototype.selectEquipment.call(app,'smg',true);
 assert.equal(reads,1);assert.equal(app.closed,true);assert.equal(app.renderer.camera.weaponPitch,0);
 const after=read(s,n);for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],after.palms[k])<1e-5,'UI preserves tracked palms');
 D.EquipmentApp.prototype.selectEquipment.call(app,'invalid');assert.equal(reads,1,'invalid selection is a no-op');
});
test('renderer presentation sampling reuses one tracker, resets scenes and does not mutate simulation',()=>{
 const {s,tracker,n}=moving('rifle'),r={motionTracker:tracker,motionScene:s,previewStudio:false};
 const sample=()=>D.EquipmentRenderer.prototype.handlingActor.call(r,s),saved=JSON.stringify(s.serialize()),handling=JSON.stringify(s.equipment.handling);
 const a=sample(),b=sample();assert.equal(a.motion,n.motion);assert.equal(b.motion,a.motion,'same-time reads retain foot locks');
 assert.equal(JSON.stringify(s.serialize()),saved);assert.equal(JSON.stringify(s.equipment.handling),handling);
 const other=scene('rifle');const next=D.EquipmentRenderer.prototype.handlingActor.call(r,other);
 assert.equal(r.motionScene,other);assert.equal(next.motion.reset,true);assert.equal(tracker.size,1,'new scene discards old foot contacts');
 r.previewStudio=true;const size=tracker.size;assert.equal(D.EquipmentRenderer.prototype.handlingActor.call(r,s),s.player);assert.equal(tracker.size,size,'studio cannot rewrite live tracking');
 assert.equal(D.EquipmentRenderer.prototype.handlingActor.call({motionTracker:null},s),s.player,'headless fallback uses the logical actor');
});
test('tracked selection during reload preserves its piece and remains transient',()=>{
 const {s,n}=moving('rifle');s.equipment.ammo.rifle.loaded--;assert.equal(s.reloadWeapon(),true);s.equipment.reloading=D.Equipment.get('rifle').reload*.54;
 const before=read(s,n),ammo=JSON.stringify(s.equipment.ammo);s.cancelEquipment();s.equipWeapon('sniper',n);const after=read(s,n);
 for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],after.palms[k])<1e-5,'reload exit uses tracked pose');
 for(const q of [[0,0,0],[0,-.135,.12],[.03,-.2,.16]])assert.ok(distance(before.mount.partPoint('magazine',q),after.mount.partPoint('magazine',q))<1e-5,'visible piece does not teleport');
 assert.equal(s.equipment.reloading,0);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 assert.equal(JSON.stringify(s.equipment.handling).includes('supportY'),false,'do not retain the actor or foot tracker in handoff');
 const restored=scene('pistol');assert.equal(restored.restore(s.serialize()),true);assert.equal(restored.equipment.handling.handoff,undefined);
});
