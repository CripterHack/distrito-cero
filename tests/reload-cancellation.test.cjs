'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
for(const name of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-fit','weapon-handling','equipment','equipment-simulation','save-store','character-motion','skin-rig']){
 vm.runInThisContext(fs.readFileSync('src/'+name+'.js','utf8'));
}
// Exercise the same selector adapter as contact-transitions.test.cjs. This is
// not a replacement for real-browser pause, keyboard or persistence tests.
DC.Audio=class{};DC.App=class{};
vm.runInThisContext(fs.readFileSync('src/equipment-ui.js','utf8'));
const D=DC,E=D.Equipment,FRAME=1/60;
const PHASES=[0,.14,.30,.52,.72,.90,.999];
const RELOADABLE=E.catalog.filter(w=>w.mag&&w.reload);

function advance(sim,seconds,input={}){
 let left=seconds,first=true;
 while(left>1e-10){
  const dt=Math.min(FRAME,left);sim.time+=dt;
  sim.equipmentStep(dt,first?input:{...input,firePressed:false});
  first=false;left-=dt;
 }
}
function atPhase(w,fraction){
 const sim=new D.Simulation(new D.World());
 Object.assign(sim.player,{x:4,z:36,yaw:0,car:null,moveSpeed:0});sim.time=2;
 sim.equipment.selected=w.id;D.WeaponHandling.beginEquip(sim);
 const ammo=sim.equipment.ammo[w.id];
 ammo.loaded=Math.max(0,w.mag-2);
 // Cover both a full refill and a reserve too small to fill larger magazines.
 ammo.reserve=fraction<.5?w.reserve:1;
 const initial=E.snapshot(sim.equipment),events=[],emit=sim.emit.bind(sim);
 sim.emit=(...args)=>{events.push(args);return emit(...args);};
 assert.equal(sim.reloadWeapon(),true,w.id+' must enter a real reload');
 advance(sim,w.reload*fraction,{aim:true});
 assert.ok(sim.equipment.reloading>0,w.id+' checkpoint must precede completion');
 assert.deepEqual(E.snapshot(sim.equipment),initial,'no early ammo transfer');
 return{sim,initial,events};
}
const completed=events=>events.filter(([type,value])=>type==='sound'&&value==='reloadDone').length;
function noHeldAction(sim,w){
 const shots=sim.equipment.shots;
 advance(sim,w.reload+.12,{aim:true,fire:true});
 assert.equal(sim.equipment.shots,shots,'phantom fire from held input: '+w.id);
 assert.equal(sim.equipment.charge,0,'discarded charge revived: '+w.id);
 assert.equal(sim.equipment.blockedTrigger,true,'held input must remain blocked');
}
function noReloadProp(sim){
 const m=E.mount(sim);
 assert.equal(m.reload,0);
 assert.equal(m.magazine.attachedToHand,false);
 assert.ok(m.magazine.offset.every(v=>v===0),'detached reload piece survived cancellation');
 assert.ok(m.magazine.rotation.every(v=>v===0));
}
function freshAction(sim,w){
 const shots=sim.equipment.shots,loaded=sim.equipment.ammo[w.id].loaded;
 advance(sim,FRAME,{fire:false});
 advance(sim,FRAME,{aim:true,fire:true,firePressed:true});
 if(w.kind==='gauss'){
  advance(sim,w.chargeTime*.5,{aim:true,fire:true});
  advance(sim,FRAME,{aim:true,fire:false});
 }
 assert.equal(sim.equipment.shots,shots+1,'a fresh input must still work: '+w.id);
 assert.equal(sim.equipment.ammo[w.id].loaded,loaded-1);
}

test('reload matrix includes every current reloadable item, including grenade and technology',()=>{
 assert.deepEqual(RELOADABLE.map(w=>w.id).sort(),['emp','gauss','grenade','launcher','pistol','revolver','rifle','shotgun','smg','sniper']);
 assert.equal(PHASES.length,7);
});

for(const w of RELOADABLE){
 test(w.id+': input cancellation at every checkpoint completes exactly once and requires rearming',()=>{
  for(const fraction of PHASES){
   const {sim,initial,events}=atPhase(w,fraction),remaining=sim.equipment.reloading;
   sim.cancelEquipment();sim.cancelEquipment();
   assert.deepEqual(E.snapshot(sim.equipment),initial);
   assert.equal(sim.equipment.reloading,remaining,'input cancellation must not discard the reload');
   assert.equal(sim.equipment.reloadId,w.id);
   assert.equal(sim.equipment.trigger,false);assert.equal(sim.equipment.charge,0);
   noHeldAction(sim,w);
   const expected=structuredClone(initial),ammo=expected.ammo[w.id],total=ammo.loaded+ammo.reserve;
   ammo.loaded=Math.min(total,w.mag);ammo.reserve=total-ammo.loaded;
   assert.deepEqual(E.snapshot(sim.equipment),expected,'ammo transfers only once');
   assert.equal(completed(events),1);assert.equal(sim.equipment.reloading,0);assert.equal(sim.equipment.reloadId,null);
   noReloadProp(sim);noHeldAction(sim,w);
   assert.deepEqual(E.snapshot(sim.equipment),expected,'completed reload cannot transfer twice');
   assert.equal(completed(events),1);
   freshAction(sim,w);
  }
 });
 test(w.id+': switching at every checkpoint discards the reload without deferred transfers',()=>{
  for(const fraction of PHASES)for(const target of ['unarmed','binoculars',w.id==='gauss'?'pistol':'gauss']){
   const {sim,initial,events}=atPhase(w,fraction);
   assert.equal(sim.equipWeapon(target),true);
   assert.equal(sim.equipment.reloading,0);assert.equal(sim.equipment.reloadId,null);
   assert.equal(sim.equipment.trigger,false);assert.equal(sim.equipment.charge,0);
   assert.equal(E.mount(sim).ready,0);noReloadProp(sim);
   noHeldAction(sim,w);
   assert.deepEqual(E.snapshot(sim.equipment).ammo,initial.ammo);
   assert.equal(completed(events),0);
   assert.equal(sim.equipWeapon(w.id),true);noReloadProp(sim);
   noHeldAction(sim,w);
   assert.deepEqual(E.snapshot(sim.equipment),initial,'returning to the original item must not resume the discarded reload');
   assert.equal(completed(events),0);
  }
 });
 test(w.id+': save restoration at every checkpoint preserves ammo without replaying transient actions',()=>{
  for(const fraction of PHASES){
   const {sim,initial,events}=atPhase(w,fraction),saved=JSON.parse(JSON.stringify(sim.serialize()));
   assert.deepEqual(saved.equipment,initial);
   assert.equal(sim.restore(saved),true);
   assert.deepEqual(E.snapshot(sim.equipment),initial);
   assert.equal(sim.equipment.reloading,0);assert.equal(sim.equipment.reloadId,null);
   assert.equal(sim.equipment.trigger,false);assert.equal(sim.equipment.charge,0);
   assert.equal(E.mount(sim).ready,0);noReloadProp(sim);
   // The UI owns input cancellation on resume. Restore itself owns data only.
   sim.cancelEquipment();noHeldAction(sim,w);
   assert.deepEqual(E.snapshot(sim.equipment),initial);assert.equal(completed(events),0);
  }
 });
 test(w.id+': selector return during every checkpoint never restores a trigger or charged action',()=>{
  for(const fraction of PHASES)for(const returnMode of ['play','pause']){
   const {sim,initial}=atPhase(w,fraction),remaining=sim.equipment.reloading;
   const app={sim,arsenalReturn:returnMode,renderer:{frozenHandling:{equipment:{selected:w.id,aimWeight:.82,trigger:true,charge:.99}}},
    setMode(mode){this.mode=mode;this.renderer.frozenHandling=null;this.sim.cancelEquipment();}};
   D.EquipmentApp.prototype.closeArsenal.call(app);
   assert.equal(app.mode,returnMode);assert.equal(sim.equipment.aimWeight,returnMode==='play'?.82:0);
   assert.equal(sim.equipment.trigger,false);assert.equal(sim.equipment.charge,0);assert.equal(sim.equipment.blockedTrigger,true);
   assert.equal(sim.equipment.reloading,remaining);assert.deepEqual(E.snapshot(sim.equipment),initial);
   // Advance only the simulation after the adapter boundary. No claim that
   // this mock setMode measures a browser's paused clock or physical inputs.
   noHeldAction(sim,w);
  }
 });
}

test('held-input oracle rejects an intentionally unsafe cancellation after a real reload',()=>{
 const w=E.get('rifle'),{sim}=atPhase(w,.52);
 sim.cancelEquipment();sim.equipment.blockedTrigger=false;
 assert.throws(()=>noHeldAction(sim,w),/phantom fire from held input/);
});
