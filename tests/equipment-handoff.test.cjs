'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
const items=['rifle','smg','shotgun','sniper'];
const xyz=p=>[p.x,p.y,p.z];
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function advance(s,n=1,aim=false){for(let i=0;i<n;i++){s.time+=1/60;s.equipmentStep(1/60,{aim});}}
function read(s){const mount=(D.WeaponHandling.present||D.WeaponHandling.mount)(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment),pose=R.pose(actor,s.time);return {mount,actor,pose,palms:['L','R'].map(k=>xyz(R.palmPoint(pose,actor,k)))};}
function settled(item){const s=scene(item);D.WeaponHandling.beginEquip(s);advance(s,180,true);return s;}
for(const from of items)test(from+' visual handoff starts at the preceding palms and converges without changing the logical selection',()=>{
 for(const to of items.filter(i=>i!==from)){
  const s=settled(from),before=read(s),ammo=JSON.stringify(s.equipment.ammo);
  // Same path used by the UI: cancel inputs first, then select the item.
  s.cancelEquipment();assert.equal(s.equipWeapon(to),true);
  assert.equal(s.equipment.selected,to);assert.equal(s.equipment.handling.ready,0);
  const first=read(s);
  for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],first.palms[k])<1e-5,`${from}->${to} hand ${k} jumps ${distance(before.palms[k],first.palms[k])}m at equip`);
  let previous=first;
  for(let frame=1;frame<=60;frame++){
   advance(s);const state=JSON.stringify(s.serialize()),a=read(s),b=read(s);
   assert.deepEqual(a.palms,b.palms,'render reads are deterministic');assert.equal(JSON.stringify(s.serialize()),state,'read does not mutate game state');
   for(let k=0;k<2;k++)assert.ok(distance(previous.palms[k],a.palms[k])<.030,`${from}->${to} frame ${frame} hand ${k}`);
   for(const k of ['L','R'])assert.ok(distance(xyz(R.palmPoint(a.pose,a.actor,k)),xyz(a.mount.palmContacts[k]))<.012,'IK follows presentation contact without stretching');
   previous=a;
  }
  assert.equal(JSON.stringify(s.equipment.ammo),ammo);
  assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.trigger,false);
  assert.equal(s.equipment.handling.handoff,undefined,'finite presentation state is retired');
  assert.deepEqual(read(s).mount.origin,D.Equipment.mount(s).origin,'endpoint exactly matches the existing mount');
 }
});
test('a second rapid docked selection retargets from the current presentation, not the first item',()=>{
 const s=settled('rifle');s.equipWeapon('sniper');advance(s,7);const before=read(s);s.cancelEquipment();s.equipWeapon('shotgun');const after=read(s);
 for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],after.palms[k])<1e-5,`interrupted hand ${k} teleported`);
 advance(s,60);assert.equal(s.equipment.handling.handoff,undefined);
});
test('presentation handoff leaves gameplay mount, serialization, and restore independent',()=>{
 const s=settled('rifle');s.equipWeapon('smg');advance(s,3);
 const data=s.serialize(),raw=D.Equipment.mount(s),h=s.equipment.handling;
 const plain={...s,equipment:{...s.equipment,handling:{...h}}};delete plain.equipment.handling.handoff;
 const independent=D.Equipment.mount(plain);
 for(const key of ['origin','muzzle','aim','ready','coordination'])assert.deepEqual(raw[key],independent[key]);
 assert.equal(JSON.stringify(data).includes('handoff'),false);
 const restored=scene('pistol');assert.equal(restored.restore(data),true);assert.equal(restored.equipment.handling.handoff,undefined);
 assert.equal(s.equipWeapon('not-an-item'),false);assert.equal(s.equipment.handling,h,'invalid selection is a no-op');
});
test('firing or reloading interrupts the cosmetic handoff without delaying the actual action',()=>{
 for(const action of ['fire','reload']){
  const s=settled('rifle');s.equipWeapon('sniper');advance(s,2);
  const loaded=s.equipment.ammo.sniper.loaded;
  if(action==='fire'){s.equipmentStep(1/60,{fire:true,firePressed:true});assert.equal(s.equipment.ammo.sniper.loaded,loaded-1);}
  else {s.equipment.ammo.sniper.loaded--;assert.equal(s.reloadWeapon(),true);}
  assert.equal(read(s).mount.displayItem,'sniper');assert.deepEqual(read(s).mount.origin,D.Equipment.mount(s).origin,'active action renders the real gameplay mount');
  advance(s);assert.equal(s.equipment.handling.handoff,undefined);
 }
});
test('unavailable, reloading and non-docked equipment retain the original immediate path',()=>{
 const s=settled('rifle');s.equipment.ammo.rifle.loaded--;s.reloadWeapon();s.equipWeapon('smg');assert.equal(s.equipment.handling.handoff,undefined);assert.equal(s.equipment.reloading,0);
 for(const id of ['pistol','gauss','binoculars','unarmed']){s.equipWeapon(id);assert.equal(s.equipment.handling.handoff,undefined);}
 const hidden=settled('rifle');hidden.player.car='occupied';hidden.equipWeapon('sniper');assert.equal(hidden.equipment.handling.handoff,undefined);
});
test('the displayed prop clears sampled face and jacket throughout every docked family handoff',()=>{
 const fs=require('node:fs'),vm=require('node:vm');vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js','utf8'));
 for(const from of items)for(const to of items.filter(i=>i!==from)){
  const s=settled(from);s.equipWeapon(to);
  for(let frame=0;frame<=24;frame++){
   if(frame)advance(s);if(frame%3)continue;
   const v=read(s),shown={...s,equipment:{...s.equipment,selected:v.mount.displayItem}};
   const result=DC_STOCK_CLEARANCE.inspect(shown,v);
   for(const p of ['face','jacket'])assert.ok(result.minimum[p].distance>=-.002,`${from}->${to} ${frame} ${p}: ${result.minimum[p].distance}`);
  }
 }
});
test('handoff snapshot is actor-local, isolated, finite and advances only with simulation time',()=>{
 const a=settled('rifle'),b=settled('rifle');a.equipWeapon('sniper');b.equipWeapon('sniper');
 const saved=JSON.stringify(a.equipment.handling),before=read(a);
 for(let i=0;i<5;i++)read(a);
 assert.equal(JSON.stringify(a.equipment.handling),saved,'render calls cannot run a second clock');
 a.equipmentStep(0,{});assert.equal(JSON.stringify(a.equipment.handling),saved);
 advance(b,10);assert.equal(JSON.stringify(a.equipment.handling),saved,'another actor cannot advance this snapshot');
 a.player.x=12;a.player.z=-8;a.player.y=1;a.player.yaw=1.2;
 const rotated=read(a);for(let k=0;k<2;k++){
  const p=before.palms[k],expected=[12+p[0]*Math.cos(1.2)+p[2]*Math.sin(1.2),1+p[1],-8-p[0]*Math.sin(1.2)+p[2]*Math.cos(1.2)];
  assert.ok(distance(rotated.palms[k],expected)<1e-5,'snapshot travels and rotates with actor');
 }
});
test('sampled handoff clearance remains within the existing tolerance across crouch, neck and pitch variants',()=>{
 const fs=require('node:fs'),vm=require('node:vm');vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js','utf8'));
 for(const [from,to]of [['rifle','smg'],['smg','rifle'],['shotgun','sniper'],['sniper','shotgun']])for(const neck of [-1,1])for(const crouch of [0,1])for(const pitch of [-.3,.3]){
  const s=scene(from);s.appearance.neckLength=neck;s.player.crouch=crouch;s.equipment.pitch=pitch;D.WeaponHandling.beginEquip(s);advance(s,180,true);s.equipWeapon(to);
  for(let frame=0;frame<=24;frame++){
   if(frame)advance(s);if(frame%6)continue;
   const v=read(s),shown={...s,equipment:{...s.equipment,selected:v.mount.displayItem}},result=DC_STOCK_CLEARANCE.inspect(shown,v);
   for(const p of ['face','jacket'])assert.ok(result.minimum[p].distance>=-.002,JSON.stringify({from,to,neck,crouch,pitch,frame,part:p,distance:result.minimum[p].distance}));
  }
 }
});
test('the support hand deliberately releases during transfer instead of pulling the stock back into the body',()=>{
 const s=settled('shotgun');s.equipWeapon('sniper');advance(s,12);const v=read(s);
 assert.equal(v.mount.handoff.freeHand,'L');
 assert.equal(v.mount.fingerContacts.L.weight,0,'free hand must not claim an attached finger contact');
 const grip=D.WeaponHandling.profile('sniper').support.p;
 assert.ok(distance(xyz(v.mount.palmContacts.L),v.mount.point(...grip))>.025,'support hand is reaching, not falsely reported as an attached grip');
 const primary=D.WeaponHandling.profile('sniper').primary?.p||[.031,-.107,-.030];
 assert.ok(distance(xyz(v.mount.palmContacts.R),v.mount.point(...primary))<1e-6);
});
