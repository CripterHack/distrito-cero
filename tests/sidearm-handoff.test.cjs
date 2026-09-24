'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
D.App=class {};D.Audio=class {};
vm.runInThisContext(fs.readFileSync('src/equipment-ui.js','utf8'));
const xyz=p=>[p.x,p.y,p.z],distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function step(s,n=1){for(let i=0;i<n;i++){s.time+=1/60;s.equipmentStep(1/60,{});}}
function setup(id,{aim=1,crouch=0,pitch=0,neck=0}={}){
 const s=scene(id);s.player.crouch=crouch;s.equipment.pitch=pitch;s.appearance.neckLength=neck;
 D.WeaponHandling.beginEquip(s);for(let i=0;i<180;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:!!aim});}return s;
}
function read(s,source=s.player){
 const mount=D.WeaponHandling.present(s,source),actor=D.WeaponHandling.actor(source,mount,s.equipment),pose=R.pose(actor,s.time);
 return{mount,actor,pose,palms:['L','R'].map(k=>xyz(R.palmPoint(pose,actor,k)))};
}
function appFor(s,actor=s.player,frozen=null){return {sim:s,renderer:{camera:{weaponPitch:s.equipment.pitch},frozenHandling:frozen,handlingActor(){return actor;}},
 clearWeaponInput(){s.cancelEquipment();this.cleared=true;},closeArsenal(){this.renderer.frozenHandling=null;},toast(){},updateEquipmentHUD(){}};}
function select(app,id,close=false){D.EquipmentApp.prototype.selectEquipment.call(app,id,close);}
function lengths(v){
 for(const side of ['L','R'])for(const [a,b]of [['upperArm','forearm'],['forearm','hand']]){
  const pa=R.bones[R.ids[a+side]][2],pb=R.bones[R.ids[b+side]][2];
  const x=R.transform(v.pose.matrices.subarray(R.ids[a+side]*16,R.ids[a+side]*16+16),pa);
  const y=R.transform(v.pose.matrices.subarray(R.ids[b+side]*16,R.ids[b+side]*16+16),pb);
  assert.ok(Math.abs(distance(x,y)-distance(pa,pb))<1e-6,'skeletal segment cannot stretch');
 }
}
for(const [from,to]of [['pistol','revolver'],['revolver','pistol']])test(from+' -> '+to+' keeps the visible palms through real UI cancellation and converges',()=>{
 for(const cfg of [{},{aim:0},{crouch:1,pitch:.3,neck:1},{crouch:1,pitch:-.3,neck:-1}]){
  const s=setup(from,cfg),app=appFor(s),before=read(s),ammo=JSON.stringify(s.equipment.ammo),time=s.time;
  select(app,to);const first=read(s);
  assert.equal(app.cleared,true);assert.equal(s.equipment.selected,to);assert.equal(s.equipment.trigger,false);assert.equal(s.equipment.aimWeight,0);assert.equal(s.time,time);
  for(let k=0;k<2;k++)assert.ok(distance(first.palms[k],before.palms[k])<1e-5,`${from}->${to} ${JSON.stringify(cfg)} initial palm ${k}: ${distance(first.palms[k],before.palms[k])}m`);
  let last=first,maximum=0;
  for(let i=1;i<=60;i++){
   step(s);const v=read(s);lengths(v);
   for(let k=0;k<2;k++){const jump=distance(v.palms[k],last.palms[k]);maximum=Math.max(maximum,jump);assert.ok(jump<.030,`${from}->${to} step ${i}, palm ${k}: ${jump}m`);}
   for(const k of ['L','R'])assert.ok(distance(xyz(R.palmPoint(v.pose,v.actor,k)),xyz(v.mount.palmContacts[k]))<.012);
   const data=JSON.stringify(s.serialize()),h=JSON.stringify(s.equipment.handling);read(s);assert.equal(JSON.stringify(s.serialize()),data);assert.equal(JSON.stringify(s.equipment.handling),h);
   last=v;
  }
  assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.equipment.handling.handoff,undefined);
  assert.deepEqual(last.mount.origin,D.Equipment.mount(s).origin);assert.equal(last.mount.displayItem,to);
  console.log(JSON.stringify({from,to,config:cfg,maximumPalmStep:maximum}));
 }
});
test('sidearm menu selection starts at the frozen displayed pose, not the cancelled logical blend',()=>{
 const s=setup('pistol'),before=read(s),frozen={mount:before.mount,equipment:{...s.equipment}};
 s.cancelEquipment();const app=appFor(s,s.player,frozen);select(app,'revolver',true);const first=read(s);
 for(let k=0;k<2;k++)assert.ok(distance(first.palms[k],before.palms[k])<1e-5,'frozen palm was lost');
 assert.equal(s.equipment.trigger,false);assert.equal(s.equipment.aimWeight,0);
 assert.equal(JSON.stringify(s.equipment.handling).includes('point'),false,'snapshot cannot retain mount closures');
});
test('a rapid sidearm reselection preserves current presentation and restore discards it',()=>{
 const s=setup('pistol'),app=appFor(s);select(app,'revolver');step(s,9);const before=read(s);select(app,'pistol');const first=read(s);
 for(let k=0;k<2;k++)assert.ok(distance(first.palms[k],before.palms[k])<1e-5,'reselection reset the live transition');
 assert.ok(s.equipment.handling.handoff);const copy=scene('pistol');assert.equal(copy.restore(s.serialize()),true);assert.equal(copy.equipment.handling.handoff,undefined);
 const raw=D.Equipment.mount(s),plain={...s,equipment:{...s.equipment,handling:{...s.equipment.handling}}};delete plain.equipment.handling.handoff;
 assert.deepEqual(raw.muzzle,D.Equipment.mount(plain).muzzle,'logical shot origin cannot follow the cosmetic arc');
});
test('sidearm handoff cannot delay a shot or reload and never creates ammunition',()=>{
 for(const action of ['fire','reload']){const s=setup('pistol'),app=appFor(s);select(app,'revolver');step(s,2);assert.ok(s.equipment.handling.handoff);
  const loaded=s.equipment.ammo.revolver.loaded;if(action==='fire'){s.equipmentStep(1/60,{fire:true,firePressed:true});assert.equal(s.equipment.ammo.revolver.loaded,loaded-1);}else{s.equipment.ammo.revolver.loaded--;assert.equal(s.reloadWeapon(),true);}
  const v=read(s);assert.equal(v.mount.displayItem,'revolver');assert.equal(v.mount.handoff,null);assert.deepEqual(v.mount.origin,D.Equipment.mount(s).origin);
 }
});
test('sidearm extension leaves reload exits, other families and unavailable paths explicit',()=>{
 for(const target of ['rifle','binoculars','gauss','unarmed']){const s=setup('pistol');s.equipWeapon(target);assert.equal(s.equipment.handling.handoff,undefined);}
 const s=setup('pistol');s.equipment.ammo.pistol.loaded--;s.reloadWeapon();s.equipWeapon('revolver');assert.equal(s.equipment.handling.handoff,undefined,'magazine/cylinder exchange is a separate contract');
 const hidden=setup('pistol');hidden.player.car='occupied';hidden.equipWeapon('revolver');assert.equal(hidden.equipment.handling.handoff,undefined);
});
test('sidearm selection preserves the tracked actor and its support memory while moving',()=>{
 for(const [from,to] of [['pistol','revolver'],['revolver','pistol']]){
  const s=setup(from),tracker=new D.MotionTracker(4);Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vx:0,vz:0,vy:0});
  s.peds.forEach(n=>n.hidden=true);s.dynamics.props=[];s.cars.forEach((c,i)=>Object.assign(c,{x:5000+i*6,z:5000,driver:null,parked:true,speed:0}));
  let n;for(let i=0;i<30;i++){s.step(1/60,{aim:true,throttle:.6,steer:0});n=tracker.update('player',s.player,s.time);}
  const before=read(s,n),memory=JSON.stringify(n.motion);select(appFor(s,n),to);const first=read(s,n);
  for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],first.palms[k])<1e-5);
  assert.equal(first.pose.rootY,before.pose.rootY);assert.equal(JSON.stringify(n.motion),memory);
  assert.equal(JSON.stringify(s.equipment.handling).includes('supportY'),false);
  const relative=v=>v.palms.map(p=>p.map((x,i)=>x-[v.actor.x,v.actor.y||0,v.actor.z][i]));let last=relative(first);
  for(let i=0;i<60;i++){s.step(1/60,{aim:false,throttle:.6,steer:0});const v=read(s,tracker.update('player',s.player,s.time)),now=relative(v);for(let k=0;k<2;k++)assert.ok(distance(now[k],last[k])<.030,'relative moving palm step');last=now;}
 }
});
