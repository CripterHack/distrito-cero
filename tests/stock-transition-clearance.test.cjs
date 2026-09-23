'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
for(const file of ['longarm_contact','stock_clearance'])vm.runInThisContext(fs.readFileSync('tools/qa/'+file+'.js','utf8'));
function sample(item,{aim=1,reload=0,crouch=0,pitch=0,neck=0}={}){
 const sim=scene(item);sim.player.crouch=crouch;sim.appearance.neckLength=neck;Object.assign(sim.equipment,{aimWeight:aim,pitch,reloading:reload?(1-reload)*D.Equipment.get(item).reload:0,
 handling:{item,ready:1,kick:0,rifleAim:aim,longarmAim:aim}});
 const mount=D.Equipment.mount(sim),actor=D.WeaponHandling.actor(sim.player,mount,sim.equipment),pose=R.pose(actor,sim.time);
 return {sim,mount,actor,pose,clearance:DC_STOCK_CLEARANCE.inspect(sim,{mount,actor,pose}),contacts:DC_LONGARM_QA.inspect(sim,{mount,actor,pose})};
}
for(const item of ['rifle','smg','shotgun','sniper']){
 test(item+' keeps the sampled face and jacket clear while lowering to guard',()=>{
  for(const crouch of [0,1])for(const aim of [0,.25,.5,.75,1]){
   const q=sample(item,{aim,crouch});
   for(const part of ['face','jacket'])assert.ok(q.clearance.minimum[part].distance>=-.002,JSON.stringify({item,aim,crouch,part,distance:q.clearance.minimum[part].distance}));
   assert.ok(Math.max(...Object.values(q.contacts.palmErrors))<.012,'preserve hand contact');
   assert.ok(Math.max(...Object.values(q.contacts.segmentErrors))<1e-6,'preserve arm lengths');
  }
 });
 test(item+' keeps the sampled face and jacket clear throughout reload phases',()=>{
  for(const crouch of [0,1])for(const reload of [.08,.16,.32,.5,.7,.84,.92,.98]){
   const q=sample(item,{reload,crouch});
   for(const part of ['face','jacket'])assert.ok(q.clearance.minimum[part].distance>=-.002,JSON.stringify({item,reload,crouch,part,distance:q.clearance.minimum[part].distance}));
   assert.ok(Math.max(...Object.values(q.contacts.palmErrors))<.012,'preserve hand contact');
   assert.ok(Math.max(...Object.values(q.contacts.segmentErrors))<1e-6,'preserve arm lengths');
  }
 });
}

// Regression for oblique recovery: a neutral-only pass can still sweep through
// the chin, or clip the lower buttplate against the chest when pointing down.
test('inclined guard and reload clear the existing neck/crouch variants',()=>{
 for(const item of ['rifle','smg','shotgun','sniper'])for(const neck of [-1,1])for(const crouch of [0,1])for(const pitch of [-.3,.3])for(const [aim,reload] of [[0,0],[.5,0],[1,0],[1,.16],[1,.5],[1,.92]]){
  const q=sample(item,{neck,crouch,pitch,aim,reload});
  for(const part of ['face','jacket'])assert.ok(q.clearance.minimum[part].distance>=-.002,JSON.stringify({item,neck,crouch,pitch,aim,reload,part,distance:q.clearance.minimum[part].distance}));
  assert.ok(Math.max(...Object.values(q.contacts.palmErrors))<.012);
  assert.ok(Math.max(...Object.values(q.contacts.segmentErrors))<1e-6);
 }
});

test('settled native equipment raise/reload/lower preserves clearance, continuity and ammunition',()=>{
 for(const item of ['rifle','smg','shotgun','sniper']){
  const sim=scene(item);D.WeaponHandling.beginEquip(sim);sim.equipment.aimWeight=0;sim.equipment.handling.ready=1;
  let previous;
  for(const phase of ['raise','reload','lower']){
   let totalAmmo;
   if(phase==='reload'){
    sim.equipment.ammo[item].loaded=0;
    totalAmmo=sim.equipment.ammo[item].reserve;
    assert.equal(sim.reloadWeapon(),true,'start the real reload state machine');
   }
   for(let frame=0;frame<240;frame++){
    sim.time+=1/60;sim.equipmentStep(1/60,{aim:phase!=='lower'});
    const mount=D.Equipment.mount(sim),actor=D.WeaponHandling.actor(sim.player,mount,sim.equipment),pose=R.pose(actor,sim.time);
    const points=['L','R'].map(k=>R.palmPoint(pose,actor,k));
    if(previous)for(let k=0;k<2;k++)assert.ok(Math.hypot(points[k].x-previous[k].x,points[k].y-previous[k].y,points[k].z-previous[k].z)<.030,JSON.stringify({item,phase,frame,hand:k}));
    previous=points;
    // Input/timers and palm continuity run at 60 Hz. Surface sampling is 10 Hz,
    // not a claim of continuous collision detection between sampled frames.
    if(frame%6===0){
     const v=DC_STOCK_CLEARANCE.inspect(sim,{mount,actor,pose});
     for(const part of ['face','jacket'])assert.ok(v.minimum[part].distance>=-.002,JSON.stringify({item,phase,frame,part,distance:v.minimum[part].distance}));
    }
   }
   if(phase==='reload'){
    assert.equal(sim.equipment.reloading,0);assert.equal(sim.equipment.reloadId,null);
    assert.equal(sim.equipment.ammo[item].loaded,D.Equipment.get(item).mag);
    assert.equal(sim.equipment.ammo[item].loaded+sim.equipment.ammo[item].reserve,totalAmmo);
   }
  }
 }
});

test('surface-relative mounting is read-only and commutes with world transforms',()=>{
 for(const item of ['rifle','smg','shotgun','sniper'])for(const reload of [0,.16,.5,.92]){
  const q=sample(item,{aim:reload?1:.5,reload}),sim=q.sim,initial=q.clearance;
  const before=JSON.stringify(sim.serialize()),handling=JSON.stringify(sim.equipment.handling);
  for(const yaw of [.7,-1.5]){
   Object.assign(sim.player,{x:19,z:-23,yaw});
   const state=JSON.stringify(sim.serialize()),mount=D.Equipment.mount(sim),actor=D.WeaponHandling.actor(sim.player,mount,sim.equipment),pose=R.pose(actor,sim.time);
   const v=DC_STOCK_CLEARANCE.inspect(sim,{mount,actor,pose});
   for(const part of ['face','jacket'])assert.ok(Math.abs(v.minimum[part].distance-initial.minimum[part].distance)<1e-6,part);
   assert.equal(JSON.stringify(sim.serialize()),state);assert.equal(JSON.stringify(sim.equipment.handling),handling);
  }
  Object.assign(sim.player,{x:0,z:0,yaw:0});assert.equal(JSON.stringify(sim.serialize()),before);
 }
});
