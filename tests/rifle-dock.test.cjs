'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
vm.runInThisContext(fs.readFileSync('tools/qa/longarm_contact.js','utf8'));
vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js','utf8'));
const Q=DC_LONGARM_QA,dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function evidence(s){const mount=D.Equipment.mount(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment);return{mount,actor,pose:R.pose(actor,s.time)};}
function jacketTarget(s,r){
 const part=D.HeroAsset.parts.find(p=>p.name==='jacket'),data=Buffer.from(part.data,'base64'),dq=D.DualQuaternion.pack(r.pose.matrices),a=s.appearance,vertices=[];
 for(let i=26694;i<26697;i++){const b=i*24,p=[0,2,4].map(k=>data.readInt16LE(b+k)/1e4),j=[16,17,18,19].map(k=>data[b+k]),w=[20,21,22,23].map(k=>data[b+k]/255);
  vertices.push(D.DualQuaternion.transform(dq,D.CharacterFit.point(D.Appearance.shapePoint(p,part.material,a.build,a.face,a.neck||0),r.mount.neckDrop),j,w));}
 const p=[0,1,2].map(k=>vertices.reduce((sum,v)=>sum+v[k],0)/3),c=Math.cos(s.player.yaw),sn=Math.sin(s.player.yaw);
 return [s.player.x+p[0]*c+p[2]*sn,r.pose.rootY+p[1],s.player.z-p[0]*sn+p[2]*c];
}
test('rifle brace is measured against rendered jacket, not a shifted upper-arm pivot',()=>{
 const s=scene('rifle'),r=evidence(s),v=Q.inspect(s,r);assert.ok(dist(v.shoulderTarget,jacketTarget(s,r))<2e-6);
 assert.equal(v.shoulderReference,'rendered jacket triangle 8898');assert.ok(Number.isFinite(v.legacyStockError));
});
test('changing only the supplied chest palette moves the rifle surface reference',()=>{
 const s=scene('rifle'),r=evidence(s),a=Q.inspect(s,r);r.pose.matrices=r.pose.matrices.slice();r.pose.matrices[R.ids.chest*16+12]+=.02;
 const b=Q.inspect(s,r);assert.ok(Math.abs(b.shoulderTarget[0]-a.shoulderTarget[0]-.02)<2e-6);assert.ok(dist(b.eye,a.eye)<1e-9);
});
test('new stock geometry leaves the torso, grip, magazine, muzzle and data unscaled',()=>{
 const s=scene('rifle'),r=evidence(s),v=Q.inspect(s,r);assert.ok(v.eyeError<.01);assert.ok(v.stockError<.03);
 assert.ok(Math.max(...Object.values(v.segmentErrors))<1e-6);assert.deepEqual(r.mount.palmContacts.R.local,[.031,-.107,-.030]);
 assert.deepEqual(r.mount.palmContacts.L.local,[-.003,-.047,.224]);assert.equal(r.pose.scale,1);
});
test('rifle raise, lower and reload retain bounded native palm trajectories',()=>{
 const s=scene('rifle');D.WeaponHandling.beginEquip(s);s.equipment.aimWeight=0;let prev;
 const maximum={raise:0,reload:0,lower:0};
 for(const phase of ['raise','reload','lower']){
  if(phase==='reload')s.equipment.reloading=D.Equipment.get('rifle').reload;
  for(let i=0;i<180;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:phase!=='lower'});const r=evidence(s);
   const pts=['L','R'].map(k=>R.palmPoint(r.pose,r.actor,k));
   if(prev)for(let k=0;k<2;k++)maximum[phase]=Math.max(maximum[phase],Math.hypot(pts[k].x-prev[k].x,pts[k].y-prev[k].y,pts[k].z-prev[k].z));prev=pts;
  }
 }
 assert.ok(maximum.raise<.030,JSON.stringify(maximum));assert.ok(maximum.reload<.030,JSON.stringify(maximum));assert.ok(maximum.lower<.030,JSON.stringify(maximum));
});
test('rifle central aim range preserves clearance across crouch and neck-length presets',()=>{
 for(const neck of [-1,0,1])for(const crouch of [0,1])for(const pitch of [-.3,0,.3]){
  const s=scene('rifle');s.appearance.neckLength=neck;s.player.crouch=crouch;s.equipment.pitch=pitch;
  const r=evidence(s),v=Q.inspect(s,r),surface=DC_STOCK_CLEARANCE.inspect(s,r),label=JSON.stringify({neck,crouch,pitch});
  assert.ok(v.eyeError<.010,label+' eye '+v.eyeError);assert.ok(v.stockError<.030,label+' stock '+v.stockError);
  for(const part of ['face','jacket'])assert.ok(surface.minimum[part].distance>=-.002,label+' '+part+' '+surface.minimum[part].distance);
 }
});
