'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,scene,inspect}=require('./helpers/sidearm_sight.cjs');
function begin(id){const s=scene(id);s.equipment.aimWeight=0;D.WeaponHandling.beginEquip(s);return s;}
test('sidearm draw bounds every 60 Hz step including the first rendered interval',()=>{
 for(const id of ['pistol','revolver']){
  const s=begin(id);let previous=D.Equipment.mount(s).origin,max=0,peak=-1;
  for(let i=0;i<120;i++){
   s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=D.Equipment.mount(s);
   const delta=Math.hypot(...m.origin.map((x,j)=>x-previous[j]));if(delta>max){max=delta;peak=i;}previous=m.origin;
  }
  assert.ok(max<.035,`${id}: ${(max*1000).toFixed(2)} mm at interval ${peak}; includes frame zero`);
  assert.ok(inspect(s).error<.003);
 }
});
test('draw completes promptly across moderate neck, crouch and elevation variants',()=>{
 for(const id of ['pistol','revolver'])for(const neck of [-1,0,1])for(const pitch of [-.3,0,.3]){
  const s=begin(id);s.appearance.neckLength=neck;s.player.crouch=1;s.equipment.pitch=pitch;
  let previous=D.Equipment.mount(s).origin,max=0;
  for(let i=0;i<60;i++){
   s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=D.Equipment.mount(s);
   max=Math.max(max,Math.hypot(...m.origin.map((x,j)=>x-previous[j])));previous=m.origin;
   for(const gap of Object.values(inspect(s).contacts))assert.ok(gap<.012);
  }
  assert.ok(max<.035,`${id}/${neck}/${pitch} draw ${max}`);
  assert.ok(inspect(s).error<.010);
  assert.ok(D.Equipment.mount(s).aim>.99,'draw must be ready within one second');
 }
});
test('visual draw does not delay a native trigger or change ammunition accounting',()=>{
 for(const id of ['pistol','revolver']){
  const s=begin(id),ammo=s.equipment.ammo[id].loaded;
  s.time+=1/60;s.equipmentStep(1/60,{aim:true,fire:true,firePressed:true});
  assert.equal(s.equipment.shots,1);assert.equal(s.equipment.ammo[id].loaded,ammo-1);
  assert.ok(s.equipment.aimWeight>0);assert.ok(D.Equipment.mount(s).aim<s.equipment.aimWeight);
  const snap=JSON.stringify(s.serialize());D.Equipment.mount(s);assert.equal(JSON.stringify(s.serialize()),snap);
 }
});
test('ready-state and unrelated equipment retain the unmodified aiming contract',()=>{
 for(const id of ['pistol','revolver','smg','sniper','gauss','emp','launcher','shotgun','binoculars']){
  const s=begin(id);s.equipment.aimWeight=.5;s.equipment.handling.ready=1;
  assert.equal(D.Equipment.mount(s).aim,.5);
  const state=JSON.stringify(s.equipment.handling);D.WeaponHandling.step(s,0);assert.equal(JSON.stringify(s.equipment.handling),state);
  if(!['pistol','revolver'].includes(id)){s.equipment.handling.ready=.2;assert.equal(D.Equipment.mount(s).aim,.5);}
 }
});
