'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
for(const file of ['longarm_contact','stock_clearance'])vm.runInThisContext(fs.readFileSync('tools/qa/'+file+'.js','utf8'));
for(const item of ['rifle','smg','shotgun','sniper'])test(item+' initial equip clears sampled surfaces without discontinuity or stretched arms',()=>{
 for(const aim of [false,true]){
  const sim=scene(item);D.WeaponHandling.beginEquip(sim);sim.equipment.aimWeight=0;
  let previous;
  for(let frame=0;frame<=90;frame++){
   if(frame){sim.time+=1/60;sim.equipmentStep(1/60,{aim});}
   assert.ok(Math.abs(sim.equipment.handling.ready+Math.expm1(-11*frame/60))<1e-12,'presentation must not change native readiness');
   const before=JSON.stringify(sim.serialize());
   const mount=D.Equipment.mount(sim),actor=D.WeaponHandling.actor(sim.player,mount,sim.equipment),pose=R.pose(actor,sim.time);
   const clearance=DC_STOCK_CLEARANCE.inspect(sim,{mount,actor,pose}),contacts=DC_LONGARM_QA.inspect(sim,{mount,actor,pose});
   for(const part of ['face','jacket'])assert.ok(clearance.minimum[part].distance>=-.002,JSON.stringify({item,aim,frame,ready:mount.ready,part,distance:clearance.minimum[part].distance}));
   assert.ok(Math.max(...Object.values(contacts.palmErrors))<.012);
   assert.ok(Math.max(...Object.values(contacts.segmentErrors))<1e-6);
   const points=['L','R'].map(k=>R.palmPoint(pose,actor,k));
   if(previous)for(let k=0;k<2;k++)assert.ok(Math.hypot(points[k].x-previous[k].x,points[k].y-previous[k].y,points[k].z-previous[k].z)<.030,JSON.stringify({item,aim,frame,hand:k}));
   previous=points;
   assert.equal(JSON.stringify(sim.serialize()),before);
  }
 }
});

// Selected native-time snapshots across the established neck/crouch/pitch axes.
// The four cases above still inspect every step at 60 Hz; this is not CCD.
test('initial preparation retains clearance for established neck, crouch and pitch variants',()=>{
 const frames=new Set([0,1,5,10,20,40,90]);
 for(const item of ['rifle','smg','shotgun','sniper'])for(const neck of [-1,1])for(const crouch of [0,1])for(const pitch of [-.3,.3])for(const aim of [false,true]){
  const sim=scene(item);sim.appearance.neckLength=neck;sim.player.crouch=crouch;sim.equipment.pitch=pitch;D.WeaponHandling.beginEquip(sim);sim.equipment.aimWeight=0;
  for(let frame=0;frame<=90;frame++){
   if(frame){sim.time+=1/60;sim.equipmentStep(1/60,{aim});}if(!frames.has(frame))continue;
   const mount=D.Equipment.mount(sim),actor=D.WeaponHandling.actor(sim.player,mount,sim.equipment),pose=R.pose(actor,sim.time);
   const v=DC_STOCK_CLEARANCE.inspect(sim,{mount,actor,pose}),c=DC_LONGARM_QA.inspect(sim,{mount,actor,pose});
   for(const part of ['face','jacket'])assert.ok(v.minimum[part].distance>=-.002,JSON.stringify({item,neck,crouch,pitch,aim,frame,part,distance:v.minimum[part].distance}));
   assert.ok(Math.max(...Object.values(c.palmErrors))<.012);
   assert.ok(Math.max(...Object.values(c.segmentErrors))<1e-6);
  }
 }
});
