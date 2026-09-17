'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,samples,stats}=require('./helpers/thenar_surfaces.cjs');
function scene(id,progress=0){const s=new D.Simulation(new D.World(1337));Object.assign(s.player,{x:0,z:0,yaw:0,car:null});s.time=1.25;Object.assign(s.equipment,{selected:id,aimWeight:1,reloading:progress?(1-progress)*D.Equipment.get(id).reload:0});return s;}
test('mixed palm/thumb surface stays outside the foregrip instead of following the palm into it',()=>{
 const v=stats(scene('rifle'),'L','fore');assert.ok(v.min>-.001,`thenar band enters foregrip by ${(-v.min*1000).toFixed(3)} mm, ${v.inside}/${v.samples} samples`);
});
test('the same mixed skin remains outside a detached held piece',()=>{
 const v=stats(scene('rifle',.5),'L','magazine');assert.ok(v.min>-.001,`thenar band enters held piece by ${(-v.min*1000).toFixed(3)} mm`);
});
test('the audit keeps a fixed surface cohort when weights change',()=>{
 assert.equal(samples.L.length,806);assert.equal(samples.R.length,803);
 for(const side of ['L','R']){assert.equal(new Set(samples[side].map(v=>v.p.join())).size,samples[side].length);assert.ok(samples[side].some(v=>v.w.some((w,i)=>R.bones[v.j[i]][0]==='hand'+side&&w>.9)));}
});
test('all three foregrips retain the corrected band while aiming, crouching and moving',()=>{
 for(const id of ['smg','rifle','sniper'])for(const [aim,pitch,crouch]of[[0,-.4,0],[1,.35,1],[.45,0,.5]]){
  const s=scene(id);Object.assign(s.equipment,{aimWeight:aim,pitch});Object.assign(s.player,{crouch,walk:2.1,moveSpeed:1.7});const v=stats(s,'L','fore');assert.ok(v.min>-.001,`${id}: ${v.min}`);
 }
});
test('all six held pieces preserve corrected palm/thumb clearance during extraction and insertion',()=>{
 for(const id of ['pistol','smg','rifle','sniper','gauss','emp'])for(const progress of [.32,.52,.72]){
  const s=scene(id,progress);s.player.crouch=1;s.equipment.pitch=.3;const v=stats(s,'L',id==='pistol'?'pistolMagazine':'magazine');assert.ok(v.min>-.001,`${id}/${progress}: ${v.min}`);
 }
});
test('right palms and sidearm support do not trade the correction for a new penetration',()=>{
 for(const id of ['pistol','revolver','rifle','gauss','emp'])assert.ok(stats(scene(id),'R','grip').min>-.001);
 for(const id of ['pistol','revolver']){const a=stats(scene(id),'L','grip');assert.ok(a.min>0&&a.min<.006);}
});
test('fixed-cohort measurements are invariant to actor translation and yaw',()=>{
 const s=scene('rifle'),v=stats(s,'L','fore');for(const yaw of [-2.4,.8,2.8]){Object.assign(s.player,{x:6400,z:-7300,yaw});const a=stats(s,'L','fore');assert.equal(a.samples,v.samples);assert.ok(Math.abs(a.min-v.min)<.0001);}
});
test('the source correction stays bounded after every sampled skeletal pose',()=>{
 const fs=require('node:fs'),zlib=require('node:zlib'),seed=JSON.parse(fs.readFileSync('assets/thenar-contour-source.json','utf8')),records=zlib.inflateSync(Buffer.from(seed.recordsZlibBase64,'base64')),raw=Buffer.from(D.HeroAsset.parts.find(p=>p.name==='skin').data,'base64');
 const seen=new Set(),corners=[];for(let b=0;b<records.length;b+=28){const i=records.readUInt32LE(b),key=records.subarray(b+4,b+10).toString('hex');if(seen.has(key))continue;seen.add(key);corners.push({p:[4,6,8].map(k=>records.readInt16LE(b+k)/1e4),new:[0,2,4].map(k=>raw.readInt16LE(i*24+k)/1e4),j:[16,17,18,19].map(k=>raw[i*24+k]),w:[20,21,22,23].map(k=>raw[i*24+k]/255)});}
 const poses=[{}, {grip:0},{grip:1},{seated:true},{crouch:1}];
 for(const [id,p]of [['rifle',0],['rifle',.5],['pistol',0],['pistol',.5],['binoculars',0]]){const s=scene(id,p);poses.push(D.WeaponHandling.actor(s.player,D.Equipment.mount(s),s.equipment));}
 for(const n of poses){const q=R.pose(n,1.25),dq=D.DualQuaternion.pack(q.matrices);for(const c of corners){const before=D.DualQuaternion.transform(dq,c.p,c.j,c.w),after=D.DualQuaternion.transform(dq,c.new,c.j,c.w);assert.ok(Math.hypot(...before.map((v,i)=>v-after[i]))<=.00401);}}
});
test('contour metadata and surface inspection never enter persistent session state',()=>{
 const s=scene('rifle',.5),before=JSON.stringify(s.serialize());stats(s,'L','magazine');assert.equal(JSON.stringify(s.serialize()),before);assert.ok(!before.includes('thenarContour'));
});
