'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
D.App=class {};D.Audio=class {};vm.runInThisContext(fs.readFileSync('src/equipment-ui.js','utf8'));
const pairs=[['rifle','pistol'],['pistol','rifle']],revolverPairs=[['rifle','revolver'],['revolver','rifle']],smgPairs=[['smg','revolver'],['revolver','smg']],pistolSmgPairs=[['pistol','smg'],['smg','pistol']],allPairs=[...pairs,...revolverPairs,...smgPairs,...pistolSmgPairs],phases=[null,0,.08,.28,.46,.65,.86,.97];
const reloadPhases=()=>phases;
const partRole=m=>m.displayItem==='revolver'?'body':'magazine';
const xyz=p=>[p.x,p.y,p.z],distance=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
function tick(s,n=1){for(let i=0;i<n;i++){s.time+=1/60;s.equipmentStep(1/60,{});}}
function setup(id,phase=null,cfg={}){const s=scene(id);s.player.crouch=cfg.crouch||0;s.equipment.pitch=cfg.pitch||0;s.appearance.neckLength=cfg.neck||0;
 D.WeaponHandling.beginEquip(s);for(let i=0;i<180;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:cfg.aim!==false});}
 if(phase!==null){s.equipment.ammo[id].loaded-=2;assert.equal(s.reloadWeapon(),true);tick(s,Math.floor(D.Equipment.get(id).reload*phase*60));}return s;}
function read(s,source=s.player){const mount=D.WeaponHandling.present(s,source),actor=D.WeaponHandling.actor(source,mount,s.equipment),pose=R.pose(actor,s.time);
 return{mount,actor,pose,palms:['L','R'].map(k=>xyz(R.palmPoint(pose,actor,k)))};}
function app(s,source=s.player,frozen=null){return{sim:s,renderer:{camera:{weaponPitch:s.equipment.pitch},frozenHandling:frozen,handlingActor(){return source;}},
 clearWeaponInput(){s.cancelEquipment();},closeArsenal(){this.renderer.frozenHandling=null;},toast(){},updateEquipmentHUD(){}};}
function select(a,id,close=false){D.EquipmentApp.prototype.selectEquipment.call(a,id,close);}
function sameStart(a,b){for(let k=0;k<2;k++)assert.ok(distance(a.palms[k],b.palms[k])<1e-5,`initial palm ${k}: ${distance(a.palms[k],b.palms[k])}m`);
 for(let i=0;i<a.pose.matrices.length;i++)assert.ok(Math.abs(a.pose.matrices[i]-b.pose.matrices[i])<1e-5,`${R.bones[Math.floor(i/16)][0]} presentation snapped`);
 assert.equal(b.mount.displayItem,a.mount.displayItem);}
function lengths(v){for(const side of ['L','R'])for(const [a,b]of [['upperArm','forearm'],['forearm','hand']]){const pa=R.bones[R.ids[a+side]][2],pb=R.bones[R.ids[b+side]][2];
 const x=R.transform(v.pose.matrices.subarray(R.ids[a+side]*16,R.ids[a+side]*16+16),pa),y=R.transform(v.pose.matrices.subarray(R.ids[b+side]*16,R.ids[b+side]*16+16),pb);
 assert.ok(Math.abs(distance(x,y)-distance(pa,pb))<1e-6,'arm length changed');}}
for(const [from,to]of allPairs)test(from+' -> '+to+' preserves torso, palms and visible parts across aim and reload exits',()=>{
 let maximum=0,partMaximum=0,cases=0;
 for(const cfg of [{},{aim:false},{crouch:1,pitch:.3,neck:1},{crouch:1,pitch:-.3,neck:-1}])for(const phase of reloadPhases(from,to)){const s=setup(from,phase,cfg),a=app(s),before=read(s),ammo=JSON.stringify(s.equipment.ammo),time=s.time,shots=s.equipment.shots;
  select(a,to);let previous=read(s);sameStart(before,previous);assert.equal(s.equipment.selected,to);assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.reloadId,null);assert.equal(s.equipment.trigger,false);assert.equal(s.equipment.aimWeight,0);assert.equal(s.time,time);
  const points=[[0,0,0],[.03,-.18,-.02],[-.025,-.14,.04]];
  for(const p of points)assert.ok(distance(before.mount.partPoint(partRole(before.mount),p),previous.mount.partPoint(partRole(previous.mount),p))<1e-5,'old magazine initial transform changed');
  let changes=0;
  for(let frame=1;frame<=72;frame++){tick(s);const data=JSON.stringify(s.serialize()),memory=JSON.stringify(s.equipment.handling),v=read(s);lengths(v);
   for(let k=0;k<2;k++){const d=distance(v.palms[k],previous.palms[k]);maximum=Math.max(d,maximum);assert.ok(d<.030,`${from} phase ${phase} ${JSON.stringify(cfg)} frame ${frame} palm ${k}: ${d}m`);}
   for(const k of ['L','R'])assert.ok(distance(xyz(R.palmPoint(v.pose,v.actor,k)),xyz(v.mount.palmContacts[k]))<.012,'unreachable presentation target');
   if(v.mount.displayItem===previous.mount.displayItem)for(const p of points){const d=distance(v.mount.partPoint(partRole(v.mount),p),previous.mount.partPoint(partRole(previous.mount),p));partMaximum=Math.max(d,partMaximum);assert.ok(d<.030,'visible piece transform discontinuity');}
   else {changes++;assert.equal(v.mount.displayItem,to);assert.ok(Math.hypot(...previous.mount.magazine.offset)<.001,'old magazine not seated before replacement');}
   assert.equal(JSON.stringify(s.serialize()),data);assert.equal(JSON.stringify(s.equipment.handling),memory);assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.equipment.shots,shots);previous=v;
  }
  assert.equal(changes,1);assert.equal(s.equipment.handling.handoff,undefined);assert.deepEqual(previous.mount.origin,D.Equipment.mount(s).origin);cases++;
 }
 console.log(JSON.stringify({from,to,cases,maximumPalmStep:maximum,maximumPartStep:partMaximum}));
});
test('cross-family frozen capture and rapid reversal retain the visible torso and part',()=>{
 for(const [from,to]of allPairs)for(const reverseAt of [9,36]){const s=setup(from,reloadPhases(from,to).includes(.46)?.46:null),before=read(s),frozen={mount:before.mount,equipment:{...s.equipment}},ammo=JSON.stringify(s.equipment.ammo);s.cancelEquipment();const a=app(s,s.player,frozen);select(a,to,true);sameStart(before,read(s));
  tick(s,reverseAt);const mid=read(s);select(a,from);sameStart(mid,read(s));tick(s,72);assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.equipment.handling.handoff,undefined);}
});
test('cross-family presentation remains transient and a real shot or reload always takes precedence',()=>{
 for(const [from,to]of allPairs)for(const action of ['restore','fire','reload']){const s=setup(from,reloadPhases(from,to).includes(.46)?.46:null),a=app(s);select(a,to);tick(s,4);assert.ok(s.equipment.handling.handoff);
  const plain={...s,equipment:{...s.equipment,handling:{...s.equipment.handling}}};delete plain.equipment.handling.handoff;
  assert.deepEqual(D.Equipment.mount(s).muzzle,D.Equipment.mount(plain).muzzle);
  if(action==='restore'){const data=s.serialize();assert.equal(JSON.stringify(data).includes('handoff'),false);const restored=scene('unarmed');assert.equal(restored.restore(data),true);assert.equal(restored.equipment.handling.handoff,undefined);}
  else {if(action==='fire'){const n=s.equipment.ammo[to].loaded;s.equipmentStep(1/60,{fire:true,firePressed:true});assert.equal(s.equipment.ammo[to].loaded,n-1);}else{s.equipment.ammo[to].loaded--;assert.equal(s.reloadWeapon(),true);}
   const v=read(s);assert.equal(v.mount.displayItem,to);assert.equal(v.mount.handoff,null);assert.deepEqual(v.mount.origin,D.Equipment.mount(s).origin);tick(s);assert.equal(s.equipment.handling.handoff,undefined);}
 }
});
test('cross-family selection reuses the moving actor and preserves foot support memory',()=>{
 for(const [from,to]of allPairs)for(const phase of reloadPhases(from,to).includes(.46)?[null,.46]:[null]){const s=setup(from,phase),tracker=new D.MotionTracker(4);Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vx:0,vz:0,vy:0});
  s.peds.forEach(n=>n.hidden=true);s.dynamics.props=[];s.cars.forEach((c,i)=>Object.assign(c,{x:5000+i*6,z:5000,driver:null,parked:true,speed:0}));
  let n;for(let i=0;i<30;i++){s.step(1/60,{aim:true,throttle:.6,steer:0});n=tracker.update('player',s.player,s.time);}
  const before=read(s,n),memory=JSON.stringify(n.motion);select(app(s,n),to);const first=read(s,n);sameStart(before,first);assert.equal(first.pose.rootY,before.pose.rootY);assert.equal(JSON.stringify(n.motion),memory);
  assert.equal(JSON.stringify(s.equipment.handling).includes('supportY'),false);
  const relative=v=>v.palms.map(p=>p.map((x,i)=>x-[v.actor.x,v.actor.y||0,v.actor.z][i]));let previous=relative(first);
  for(let i=0;i<72;i++){s.step(1/60,{aim:false,throttle:.6,steer:0});const v=read(s,tracker.update('player',s.player,s.time)),now=relative(v);for(let k=0;k<2;k++)assert.ok(distance(now[k],previous[k])<.030,'moving palm step');previous=now;}
 }
});
test('unavailable selections and other cross-family routes are not silently opted in',()=>{
 for(const [from,to]of [['shotgun','revolver'],['smg','binoculars'],['pistol','shotgun'],['pistol','sniper'],['pistol','gauss'],['rifle','binoculars']]){const s=setup(from);select(app(s),to);assert.equal(s.equipment.handling.handoff,undefined);}
 for(const [from,to]of allPairs){const s=setup(from);s.player.car='occupied';select(app(s),to);assert.equal(s.equipment.handling.handoff,undefined);}
 const s=setup('rifle'),handling=s.equipment.handling;assert.equal(s.equipWeapon('unknown-item'),false);assert.equal(s.equipment.handling,handling);
});
test('the displayed rifle or SMG clears sampled face and jacket during the cross-family arc',()=>{
 vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js','utf8'));
 let minimum=Infinity,samples=0;
 for(const [from,to]of allPairs)for(const cfg of [{},{aim:false},{crouch:1,pitch:.3,neck:1},{crouch:1,pitch:-.3,neck:-1}])for(const phase of reloadPhases(from,to).includes(.46)?[null,.46]:[null]){
  const s=setup(from,phase,cfg);select(app(s),to);
  for(let frame=0;frame<=54;frame++){if(frame)tick(s);if(frame%3)continue;const v=read(s);if(!['rifle','smg'].includes(v.mount.displayItem))continue;
   const shown={...s,equipment:{...s.equipment,selected:v.mount.displayItem}},result=DC_STOCK_CLEARANCE.inspect(shown,v);
   for(const part of ['face','jacket']){const d=result.minimum[part].distance;minimum=Math.min(d,minimum);assert.ok(d>=-.002,JSON.stringify({from,to,phase,cfg,frame,part,distance:d}));}samples++;
  }
 }
 console.log(JSON.stringify({sampledStockPoses:samples,minimumSampledDistance:minimum}));
});

test('rifle/revolver preserves the frozen reload pose at every sampled phase',()=>{
 for(const [from,to]of revolverPairs)for(const phase of phases.filter(x=>x!==null)){
  const s=setup(from,phase),before=read(s),ammo=JSON.stringify(s.equipment.ammo),time=s.time;
  const frozen={mount:before.mount,equipment:{...s.equipment}};s.cancelEquipment();
  select(app(s,s.player,frozen),to,true);sameStart(before,read(s));
  assert.ok(s.equipment.handling.handoff);assert.equal(s.time,time);
  assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.trigger,false);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
test('rifle/revolver retargets a returning piece without discarding its current pose',()=>{
 for(const [from,to]of revolverPairs)for(const reverseAt of [0,9,36]){
  const s=setup(from,.46),a=app(s);select(a,to);tick(s,reverseAt);const before=read(s),ammo=JSON.stringify(s.equipment.ammo);
  select(a,from);sameStart(before,read(s));assert.ok(s.equipment.handling.handoff);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
 // Preserve the original three-selection regression too: logical selection
 // passed through pistol, but the permitted rifle piece is still returning.
 const s=setup('rifle',.46),a=app(s);select(a,'pistol');tick(s,9);select(a,'revolver');
 const before=read(s);assert.equal(before.mount.displayItem,'rifle');assert.ok(before.mount.reload>0);
 select(a,'rifle');sameStart(before,read(s));assert.ok(s.equipment.handling.handoff);
 tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);
});
test('rifle/revolver still rejects a third displayed prop during free or reload presentation',()=>{
 for(const phase of [null,.46]){
  const s=setup('pistol',phase);select(app(s),'rifle');tick(s,9);
  assert.equal(read(s).mount.displayItem,'pistol');
  select(app(s),'revolver');assert.equal(s.equipment.handling.handoff,undefined);
 }
});


test('SMG/revolver preserves the frozen reload pose at every sampled phase',()=>{
 for(const [from,to]of smgPairs)for(const phase of phases.filter(x=>x!==null)){
  const s=setup(from,phase),before=read(s),ammo=JSON.stringify(s.equipment.ammo),time=s.time;
  const frozen={mount:before.mount,equipment:{...s.equipment}};s.cancelEquipment();
  select(app(s,s.player,frozen),to,true);sameStart(before,read(s));
  assert.ok(s.equipment.handling.handoff);assert.equal(s.time,time);
  assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.reloadId,null);assert.equal(s.equipment.trigger,false);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
test('SMG/revolver retargets returning pieces without discarding their visible pose',()=>{
 for(const [from,to]of smgPairs)for(const reverseAt of [0,9,36]){
  const s=setup(from,.46),a=app(s);select(a,to);tick(s,reverseAt);const before=read(s),ammo=JSON.stringify(s.equipment.ammo);
  select(a,from);sameStart(before,read(s));assert.ok(s.equipment.handling.handoff);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
 // Preserve both original three-selection cases: a logical intermediate item
 // does not discard the permitted piece that is still visibly returning.
 for(const [from,via,to]of [['smg','rifle','revolver'],['revolver','pistol','smg']]){
  const s=setup(from,.46),a=app(s);select(a,via);tick(s,9);select(a,from);
  const before=read(s),ammo=JSON.stringify(s.equipment.ammo);
  assert.equal(s.equipment.reloading,0);assert.ok(before.mount.reload>0);assert.equal(before.mount.displayItem,from);
  select(a,to);sameStart(before,read(s));assert.ok(s.equipment.handling.handoff);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
test('SMG/revolver rejects a third displayed prop without losing immediate selection',()=>{
 for(const [start,from,to]of [['rifle','smg','revolver'],['pistol','revolver','smg']])for(const phase of [null,.46]){
  const s=setup(start,phase),a=app(s);select(a,from);tick(s,9);assert.equal(read(s).mount.displayItem,start);
  const ammo=JSON.stringify(s.equipment.ammo);select(a,to);assert.equal(s.equipment.selected,to);
  assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});


test('pistol/SMG preserves every frozen reload phase after input cancellation',()=>{
 for(const [from,to]of pistolSmgPairs)for(const phase of phases.filter(x=>x!==null)){
  const s=setup(from,phase),before=read(s),ammo=JSON.stringify(s.equipment.ammo),time=s.time;
  const frozen={mount:before.mount,equipment:{...s.equipment}};s.cancelEquipment();
  select(app(s,s.player,frozen),to,true);sameStart(before,read(s));
  assert.ok(s.equipment.handling.handoff);assert.equal(s.time,time);
  assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.reloadId,null);assert.equal(s.equipment.trigger,false);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
test('pistol/SMG retargets the returning piece before and after replacement',()=>{
 for(const [from,to]of pistolSmgPairs)for(const reverseAt of [0,9,36]){
  const s=setup(from,.46),a=app(s);select(a,to);tick(s,reverseAt);const before=read(s),ammo=JSON.stringify(s.equipment.ammo);
  select(a,from);sameStart(before,read(s));assert.ok(s.equipment.handling.handoff);
  tick(s,72);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
test('pistol/SMG rejects a third displayed model while keeping immediate selection',()=>{
 for(const [from,to]of pistolSmgPairs)for(const phase of [null,.46]){
  const s=setup('rifle',phase),a=app(s);select(a,from);tick(s,9);assert.equal(read(s).mount.displayItem,'rifle');
  const ammo=JSON.stringify(s.equipment.ammo);select(a,to);assert.equal(s.equipment.selected,to);
  assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
 }
});
