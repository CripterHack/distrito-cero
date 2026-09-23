'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
vm.runInThisContext(fs.readFileSync('tools/qa/longarm_contact.js','utf8'));
const Q=globalThis.DC_LONGARM_QA;
for(const item of ['smg','shotgun','sniper'])test(item+' settled sight meets the existing cooperative alignment criterion',()=>{
 const s=scene(item),before=JSON.stringify(s.serialize()),m=Q.inspect(s);
 assert.ok(m.eyeError<.010,item+' eye error '+m.eyeError);
 assert.ok(m.stockError<.030,item+' garment support '+m.stockError);
 assert.ok(m.behind>.05,item+' eye behind sight '+m.behind);
 assert.ok(Math.max(...Object.values(m.palmErrors))<.012);
 assert.ok(Math.max(...Object.values(m.segmentErrors))<1e-6);
 assert.equal(JSON.stringify(s.serialize()),before);
});
vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js','utf8'));
function evidence(s){const mount=D.Equipment.mount(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment);return{mount,actor,pose:R.pose(actor,s.time)};}
for(const item of ['smg','shotgun','sniper']){
 test(item+' central neck/crouch/pitch matrix preserves eyes, garment clearance and reach',()=>{
  for(const neck of [-1,0,1])for(const crouch of [0,1])for(const pitch of [-.3,0,.3]){
   const s=scene(item);s.appearance.neckLength=neck;s.player.crouch=crouch;s.equipment.pitch=pitch;
   const before=JSON.stringify(s.serialize()),r=evidence(s),m=Q.inspect(s,r),v=DC_STOCK_CLEARANCE.inspect(s,r);
   const label=JSON.stringify({item,neck,crouch,pitch});
   assert.ok(m.eyeError<.010,label+' eye '+m.eyeError);
   assert.ok(m.stockError<.030,label+' support '+m.stockError);
   assert.ok(m.behind>.05,label+' behind '+m.behind);
   assert.ok(Math.max(...Object.values(m.palmErrors))<.012,label+' palms');
   assert.ok(Math.max(...Object.values(m.segmentErrors))<1e-6,label+' lengths');
   for(const part of ['face','jacket'])assert.ok(v.minimum[part].distance>=-.002,label+' '+part+' '+v.minimum[part].distance);
   assert.equal(JSON.stringify(s.serialize()),before,label+' mutated state');
  }
 });
 test(item+' native raise/reload/lower stays below the existing 30 mm per-frame budget',()=>{
  const s=scene(item);D.WeaponHandling.beginEquip(s);s.equipment.aimWeight=0;let previous;
  const maximum={raise:0,reload:0,lower:0};
  for(const phase of ['raise','reload','lower']){
   if(phase==='reload')s.equipment.reloading=D.Equipment.get(item).reload;
   for(let i=0;i<240;i++){
    s.time+=1/60;s.equipmentStep(1/60,{aim:phase!=='lower'});const r=evidence(s);
    const points=['L','R'].map(k=>R.palmPoint(r.pose,r.actor,k));
    if(previous)for(let k=0;k<2;k++)maximum[phase]=Math.max(maximum[phase],Math.hypot(points[k].x-previous[k].x,points[k].y-previous[k].y,points[k].z-previous[k].z));
    previous=points;
   }
   for(const value of Object.values(maximum))assert.ok(value<.030,item+' '+JSON.stringify(maximum));
   if(phase==='raise')assert.ok(D.Equipment.mount(s).aim>.99,item+' never settled');
   if(phase==='lower')assert.ok(D.Equipment.mount(s).aim<.01,item+' never lowered');
  }
 });
 test(item+' clearance and contact transform with the actor without changing anatomy',()=>{
  const s=scene(item),initial=Q.inspect(s),clearance=DC_STOCK_CLEARANCE.inspect(s,evidence(s));
  for(const yaw of [.4,1.4,-2.4]){
   Object.assign(s.player,{yaw,x:23,z:-41});const r=evidence(s),m=Q.inspect(s,r),v=DC_STOCK_CLEARANCE.inspect(s,r);
   assert.ok(Math.abs(m.eyeError-initial.eyeError)<1e-6);
   assert.ok(Math.abs(m.stockError-initial.stockError)<1e-6);
   for(const part of ['face','jacket'])assert.ok(Math.abs(v.minimum[part].distance-clearance.minimum[part].distance)<1e-6);
   assert.ok(Math.max(...Object.values(m.segmentErrors))<1e-6);
  }
 });
 test(item+' validates its own complete stock triangles and rejects missing geometry',()=>{
  assert.equal(DC_STOCK_CLEARANCE.verifyGeometry(undefined,item).length,2);
  assert.throws(()=>DC_STOCK_CLEARANCE.verifyGeometry([],item),/missing|changed/);
  const s=scene(item),r=evidence(s);r.pose.matrices=r.pose.matrices.slice();r.pose.matrices[0]=NaN;
  assert.throws(()=>DC_STOCK_CLEARANCE.inspect(s,r),/nonfinite/);
 });
}

const untouchedGeometry={"unarmed": "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945", "baton": "3446b4e2636e32bee8a2ba3e601799baa8831fcd2e47055c4886c1b7cf13bc96", "blade": "20837107d90638e8fb65692b882e22b040acec713d794d76ac86c33e38d03d27", "pistol": "eb6dc4a9119842e5bd95a6a36b21f7cccd67cbcd927327af0b213f9a3f152982", "revolver": "1aab9cbfefa73bf91b1145ea9bac985bad4b6ef5fb5207ab20026bd7edcdc9ce", "rifle": "ad07a08d8460c257737c41f465f2d75337c5c70755e6f773e41220b549c482bb", "launcher": "afe7a3f0b86ca6949ed4230c9c21126de3ceb6158367a8b3e0bf8b829a28f2b0", "grenade": "24837e8b55a291ebf2c291f3034cd40014d51b1c98e8fdb992ffc4e04c4b794a", "gauss": "be80fcbaedf9ba5556785c474126e20137412c10762d9845fca8fb8eb8853f28", "emp": "e38e7faca22fdc5c0c5e913952e096367d5e4c0bbcf16093077a7d36c31ce2ee", "binoculars": "b16b427f829206c4ef37cf9765da93fe0380505de9f72e299092ff128369a458"};
test('rifle, tools, heavy props and short arms preserve their exact previous geometry',()=>{
 const crypto=require('node:crypto');
 for(const [item,expected] of Object.entries(untouchedGeometry))assert.equal(crypto.createHash('sha256').update(JSON.stringify(D.EquipmentGeometry.build(item))).digest('hex'),expected,item);
});
test('scope stock cannot validate against the open-sight stock geometry',()=>{
 assert.throws(()=>DC_STOCK_CLEARANCE.verifyGeometry(D.EquipmentGeometry.build('rifle'),'sniper'),/changed|missing/);
});
