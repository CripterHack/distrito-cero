'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
D.App=class {};D.Audio=class {};vm.runInThisContext(fs.readFileSync('src/equipment-ui.js','utf8'));
const phases=[0,.08,.28,.46,.65,.86,.97],xyz=p=>[p.x,p.y,p.z];
const distance=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function tick(s,n=1){for(let i=0;i<n;i++){s.time+=1/60;s.equipmentStep(1/60,{});}}
function setup(item,phase,cfg={}){const s=scene(item);s.player.crouch=cfg.crouch||0;s.equipment.pitch=cfg.pitch||0;s.appearance.neckLength=cfg.neck||0;D.WeaponHandling.beginEquip(s);for(let i=0;i<180;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});}
 s.equipment.ammo[item].loaded-=2;assert.equal(s.reloadWeapon(),true);tick(s,Math.floor(D.Equipment.get(item).reload*phase*60));return s;}
function read(s){const mount=D.WeaponHandling.present(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment),pose=R.pose(actor,s.time);
 return{mount,actor,pose,palms:['L','R'].map(k=>xyz(R.palmPoint(pose,actor,k)))};}
function app(s,frozen=null){return{sim:s,renderer:{camera:{weaponPitch:s.equipment.pitch},frozenHandling:frozen,handlingActor(){return s.player;}},
 clearWeaponInput(){s.cancelEquipment();},closeArsenal(){this.renderer.frozenHandling=null;},toast(){},updateEquipmentHUD(){}};}
function select(a,id,close=false){D.EquipmentApp.prototype.selectEquipment.call(a,id,close);}
function part(v,role){return [[0,0,0],[.03,-.18,-.02],[-.025,-.14,.04]].map(p=>v.mount.partPoint(role,p));}
function equalPose(a,b,role){for(let k=0;k<2;k++)assert.ok(distance(a.palms[k],b.palms[k])<1e-5,`initial palm ${k}: ${distance(a.palms[k],b.palms[k])}m`);
 for(let i=0;i<3;i++)assert.ok(distance(part(a,role)[i],part(b,role)[i])<1e-5,'piece initial transform changed');}
function lengths(v){for(const side of ['L','R'])for(const [a,b]of [['upperArm','forearm'],['forearm','hand']]){
 const pa=R.bones[R.ids[a+side]][2],pb=R.bones[R.ids[b+side]][2],x=R.transform(v.pose.matrices.subarray(R.ids[a+side]*16,R.ids[a+side]*16+16),pa),y=R.transform(v.pose.matrices.subarray(R.ids[b+side]*16,R.ids[b+side]*16+16),pb);
 assert.ok(Math.abs(distance(x,y)-distance(pa,pb))<1e-6,'arm length changed');}}
for(const [from,to]of [['pistol','revolver'],['revolver','pistol']])test(from+' reload exit preserves palms and the old visible piece at all seven phases',()=>{
 for(const cfg of [{},{crouch:1,pitch:.3,neck:1},{crouch:1,pitch:-.3,neck:-1}])for(const phase of phases){const s=setup(from,phase,cfg),a=app(s),before=read(s),ammo=JSON.stringify(s.equipment.ammo),time=s.time,shots=s.equipment.shots,role=from==='pistol'?'magazine':'body';
  assert.ok(s.equipment.reloading>0);select(a,to);let previous=read(s);equalPose(before,previous,role);
  assert.equal(s.equipment.selected,to);assert.equal(s.equipment.reloading,0);assert.equal(s.equipment.reloadId,null);assert.equal(s.equipment.trigger,false);assert.equal(s.time,time);
  let max=0,swapped=false;
  for(let frame=1;frame<=72;frame++){tick(s);const data=JSON.stringify(s.serialize()),handling=JSON.stringify(s.equipment.handling),v=read(s);lengths(v);
   for(let k=0;k<2;k++){const d=distance(v.palms[k],previous.palms[k]);max=Math.max(d,max);assert.ok(d<.030,`${from} phase ${phase} frame ${frame} palm ${k}: ${d}m`);}
   for(const k of ['L','R'])assert.ok(distance(xyz(R.palmPoint(v.pose,v.actor,k)),xyz(v.mount.palmContacts[k]))<.012,'presentation target unreachable');
   if(v.mount.displayItem===previous.mount.displayItem)for(let i=0;i<3;i++)assert.ok(distance(part(v,role)[i],part(previous,role)[i])<.030,'visible old piece moved discontinuously');
   if(v.mount.displayItem!==previous.mount.displayItem){assert.equal(v.mount.displayItem,to);assert.equal(swapped,false);swapped=true;
    if(from==='pistol')assert.ok(Math.hypot(...previous.mount.magazine.offset)<.001,'previous piece not seated before replacement');}
   assert.equal(JSON.stringify(s.serialize()),data);assert.equal(JSON.stringify(s.equipment.handling),handling);assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.equipment.shots,shots);previous=v;
  }
  assert.equal(swapped,true);assert.equal(s.equipment.handling.handoff,undefined);assert.deepEqual(previous.mount.origin,D.Equipment.mount(s).origin);
  console.log(JSON.stringify({from,to,phase,config:cfg,maximumPalmStep:max}));
 }
});
test('a frozen sidearm reload capture and rapid reselection retain the current piece without duplicate ammo',()=>{
 const s=setup('pistol',.46),before=read(s),frozen={mount:before.mount,equipment:{...s.equipment}},ammo=JSON.stringify(s.equipment.ammo);s.cancelEquipment();const a=app(s,frozen);
 select(a,'revolver',true);equalPose(before,read(s),'magazine');tick(s,7);const middle=read(s);select(a,'pistol');equalPose(middle,read(s),'magazine');
 assert.equal(JSON.stringify(s.equipment.handling).includes('partPoint'),false);tick(s,72);assert.equal(JSON.stringify(s.equipment.ammo),ammo);assert.equal(s.equipment.handling.handoff,undefined);
});
test('sidearm reload-exit memory stays transient and cannot delay firing or a new reload',()=>{
 for(const action of ['restore','fire','reload']){const s=setup('pistol',.46),a=app(s);select(a,'revolver');tick(s,4);assert.ok(s.equipment.handling.handoff);
  const raw=D.Equipment.mount(s),plain={...s,equipment:{...s.equipment,handling:{...s.equipment.handling}}};delete plain.equipment.handling.handoff;
  assert.deepEqual(raw.muzzle,D.Equipment.mount(plain).muzzle);
  if(action==='restore'){const saved=s.serialize();assert.equal(JSON.stringify(saved).includes('handoff'),false);const restored=scene('unarmed');assert.equal(restored.restore(saved),true);assert.equal(restored.equipment.handling.handoff,undefined);}
  else {if(action==='fire'){const n=s.equipment.ammo.revolver.loaded;s.equipmentStep(1/60,{fire:true,firePressed:true});assert.equal(s.equipment.ammo.revolver.loaded,n-1);}else{s.equipment.ammo.revolver.loaded--;assert.equal(s.reloadWeapon(),true);}
   assert.equal(read(s).mount.displayItem,'revolver');assert.equal(read(s).mount.handoff,null);tick(s);assert.equal(s.equipment.handling.handoff,undefined);}
 }
});
