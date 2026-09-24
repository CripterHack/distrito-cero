'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
const fs=require('node:fs'),vm=require('node:vm');
vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js','utf8'));
const items=['rifle','smg','shotgun','sniper'];
const phases=[0,.08,.28,.46,.65,.86,.97];
const xyz=p=>[p.x,p.y,p.z];
const distance=(a,b)=>Math.hypot(...a.map((x,i)=>x-b[i]));
function tick(s,n=1,aim=false){for(let i=0;i<n;i++){s.time+=1/60;s.equipmentStep(1/60,{aim});}}
function read(s){const mount=D.WeaponHandling.present(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment),pose=R.pose(actor,s.time);return {mount,actor,pose,palms:['L','R'].map(k=>xyz(R.palmPoint(pose,actor,k)))};}
function reloading(item,phase){const s=scene(item);D.WeaponHandling.beginEquip(s);tick(s,180,true);s.equipment.ammo[item].loaded-=2;assert.equal(s.reloadWeapon(),true);tick(s,Math.floor(D.Equipment.get(item).reload*phase*60));return s;}
for(let index=0;index<items.length;index++)test(items[index]+' cancels reload logically while preserving the shown pose and piece',()=>{
 const from=items[index];
 for(const to of items.filter(item=>item!==from))for(const phase of phases){
  const s=reloading(from,phase),before=read(s),ammo=JSON.stringify(s.equipment.ammo),shots=s.equipment.shots;
  s.cancelEquipment();assert.equal(s.equipWeapon(to),true);
  assert.equal(s.equipment.selected,to);assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.reloadId,null);
  const first=read(s);
  for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],first.palms[k])<1e-5,`${from} phase ${phase}: palm ${k} jumped ${distance(before.palms[k],first.palms[k])}m`);
  for(const q of [[0,0,0],[0,-.135,.12],[.03,-.2,.16]])assert.ok(distance(before.mount.partPoint('magazine',q),first.mount.partPoint('magazine',q))<1e-5,'visible magazine must not teleport on cancellation');
  let previous=first;
  for(let frame=1;frame<=48;frame++){
   tick(s);const data=JSON.stringify(s.serialize()),v=read(s);
   assert.equal(JSON.stringify(s.serialize()),data,'presentation is read-only');
   for(let k=0;k<2;k++)assert.ok(distance(previous.palms[k],v.palms[k])<.030,`${from} phase ${phase} frame ${frame}: palm ${k} step ${distance(previous.palms[k],v.palms[k])}`);
   const shown={...s,equipment:{...s.equipment,selected:v.mount.displayItem}};
   const clearance=DC_STOCK_CLEARANCE.inspect(shown,v);
   for(const part of ['jacket','face'])assert.ok(clearance.minimum[part].distance>=-.002,`${from} phase ${phase} frame ${frame}: ${part} ${clearance.minimum[part].distance}`);
   if(frame===18)assert.deepEqual(v.mount.magazine.offset,[0,0,0],'old detached piece is seated before model replacement');
   previous=v;
  }
  assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.equipment.shots,shots);
  assert.equal(s.equipment.trigger,false);assert.deepEqual(read(s).mount.origin,D.Equipment.mount(s).origin);
 }
});

test('reload handoff keeps a single captured piece across rapid reselection and clears on restore or an action',()=>{
 for(const action of ['switch','fire','reload','restore']){
  const s=reloading('rifle',.46),ammo=JSON.stringify(s.equipment.ammo);s.equipWeapon('smg');tick(s,5);const before=read(s);
  if(action==='switch'){
   s.equipWeapon('sniper');const first=read(s);
   for(let k=0;k<2;k++)assert.ok(distance(before.palms[k],first.palms[k])<1e-5);
   assert.ok(distance(before.mount.partPoint('magazine',[0,0,0]),first.mount.partPoint('magazine',[0,0,0]))<1e-5);
   tick(s,48);assert.equal(s.equipment.handling.handoff,undefined);assert.equal(JSON.stringify(s.equipment.ammo),ammo);
  }else if(action==='restore'){
   const data=s.serialize();assert.equal(JSON.stringify(data).includes('handoff'),false);
   const other=scene('unarmed');assert.equal(other.restore(data),true);assert.equal(other.equipment.handling.handoff,undefined);
  }else {
   if(action==='fire'){const n=s.equipment.ammo.smg.loaded;s.equipmentStep(1/60,{fire:true,firePressed:true});assert.equal(s.equipment.ammo.smg.loaded,n-1);}
   else {s.equipment.ammo.smg.loaded--;assert.equal(s.reloadWeapon(),true);}
   assert.equal(read(s).mount.displayItem,'smg');assert.deepEqual(read(s).mount.origin,D.Equipment.mount(s).origin);
   tick(s);assert.equal(s.equipment.handling.handoff,undefined);
  }
 }
});
