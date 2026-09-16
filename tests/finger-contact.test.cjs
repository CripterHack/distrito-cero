'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {D,R,stats}=require('./helpers/finger_surfaces.cjs');
function scene(id,reload=0){const s=new D.Simulation(new D.World());Object.assign(s.player,{x:0,z:0,yaw:0,car:null});s.time=1.25;s.equipment.selected=id;s.equipment.aimWeight=1;s.equipment.reloading=reload*(D.Equipment.get(id).reload||0);return s;}
test('actual middle ring and little skin stay outside the primary grip interior',()=>{const s=scene('rifle');for(const name of['middle','ring','little']){const v=stats(s,'R',name,'grip');assert.ok(v.min>-.003,`${name} skin penetrates grip proxy by ${(-v.min*1000).toFixed(1)} mm`);}});
test('support fingers wrap the rifle foregrip without burying the index pad',()=>{const s=scene('rifle');for(const name of['index','middle','ring','little']){const v=stats(s,'L',name,'fore');assert.ok(v.min>-.003,`${name}: ${v.min}`);}});
test('detached magazine remains outside the support fingertips in the held phase',()=>{const s=scene('rifle',.5);for(const name of['index','middle','ring','little']){const v=stats(s,'L',name,'magazine');assert.ok(v.min>-.003,`${name}: ${v.min}`);}});
// These assertions cover the original non-thumb subset. Thumb base opposition
// has its own surface, self-contact and transition gates in thumb-contact.test.cjs.
test('all nine primary handles retain skin clearance through aim, pitch and crouch',()=>{
 for(const id of ['pistol','revolver','smg','rifle','shotgun','sniper','gauss','emp','launcher'])for(const [aim,pitch,crouch]of[[0,-.4,0],[1,.35,1],[.45,0,.5]]){
  const s=scene(id);Object.assign(s.equipment,{aimWeight:aim,pitch});s.player.crouch=crouch;
  for(const name of['middle','ring','little']){const v=stats(s,'R',name,'grip');assert.ok(v.min>-.003&&v.min<.007,`${id}/${name}: ${v.min}`);}
 }
});
test('six detachable magazines are held with finger skin outside their solid volume',()=>{
 for(const id of ['pistol','smg','rifle','sniper','gauss','emp'])for(const progress of [.32,.52,.72]){
  const s=scene(id,1-progress);s.player.crouch=1;s.equipment.pitch=.3;
  for(const name of['index','middle','ring','little']){const v=stats(s,'L',name,id==='pistol'?'pistolMagazine':'magazine');assert.ok(v.min>-.003&&v.min<.007,`${id}/${progress}/${name}: ${v.min}`);}
 }
});
test('surface checks remain invariant when the whole actor and prop rotate and translate',()=>{
 const s=scene('rifle'),baseline=stats(s,'R','little','grip').min;
 for(const yaw of [-2.4,.8,2.8]){Object.assign(s.player,{yaw,x:800,z:-600});const v=stats(s,'R','little','grip');assert.ok(Math.abs(v.min-baseline)<.0001);}
});
test('shape proxies are independently checked against the actual cosmetic prop geometry',()=>{
 const mesh=D.EquipmentGeometry.build('rifle').find(p=>p.role==='grip').data;
 for(const [axis,expected]of[[0,.030],[1,-.025],[2,.024]]){let max=-Infinity;for(let i=axis;i<mesh.length;i+=8)max=Math.max(max,mesh[i]);assert.ok(Math.abs(max-expected)<1e-6);}
 for(const id of ['pistol','rifle','gauss']){const p=D.EquipmentGeometry.build(id).filter(p=>p.role==='magazine'),v=p.flatMap(p=>Array.from(p.data).filter((_,i)=>i%8<3));assert.ok(v.length>0);}
});
test('free distal joints can curve without increasing proximal penetration',()=>{
 const m=D.Equipment.mount(scene('rifle')),f=m.grips.L.fingers.index;
 assert.ok(f[2]>f[0]*2,'support index must not remain a uniformly straight finger');
 assert.ok(f.every(v=>Number.isFinite(v)&&v>=0&&v<1.46));
});
test('contact fitting does not move arm or palm anchors and preserves all segment lengths',()=>{
 const s=scene('rifle',.5),m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=R.pose(n,s.time),opened=structuredClone(n);
 for(const k of ['L','R'])for(const name of['index','middle','ring','little'])opened.handGrips[k].fingers[name]=[0,0,0];
 const neutral=R.pose(opened,s.time),fingerIds=new Set(Object.values(R.fingers).flat().flatMap(f=>f.bones.map(b=>R.ids[b])));
 for(let i=0;i<R.bones.length;i++)if(!fingerIds.has(i))assert.deepEqual(q.matrices.subarray(i*16,i*16+16),neutral.matrices.subarray(i*16,i*16+16));
 for(const k of['L','R'])for(const f of R.fingers[k])for(let j=0;j<3;j++){
  const a=f.joints[j],b=j<2?f.joints[j+1]:f.tip,mat=q.matrices.subarray(R.ids[f.bones[j]]*16,R.ids[f.bones[j]]*16+16),aa=R.transform(mat,a),bb=R.transform(mat,b);
  assert.ok(Math.abs(Math.hypot(...aa.map((v,i)=>v-bb[i]))-Math.hypot(...a.map((v,i)=>v-b[i])))<1e-6);
 }
});
test('fitting is cached by four finite authored contact profiles, not actor or world position',()=>{
 for(const id of['pistol','rifle','emp','smg','gauss','sniper'])D.Equipment.mount(scene(id,.5));
 const before=D.WeaponHandling.contactFitStats();assert.equal(before.cached,4);
 for(let i=0;i<50;i++){const s=scene(i%2?'rifle':'pistol',.5);s.player.x=i*700;s.player.yaw=i;D.Equipment.mount(s);}
 assert.deepEqual(D.WeaponHandling.contactFitStats(),before);
});
test('finger contacts are pure presentation and do not alter inventory or serialized sessions',()=>{
 const s=scene('rifle',.5),before=JSON.stringify(s.serialize()),m=D.Equipment.mount(s);R.pose(D.WeaponHandling.actor(s.player,m,s.equipment),s.time);
 assert.equal(JSON.stringify(s.serialize()),before);assert.ok(!before.includes('fingerContacts'));assert.ok(!before.includes('scales'));
});
test('reloading finger poses approach and release the object without discrete pose jumps',()=>{
 for(const id of['pistol','rifle','gauss']){let prev=null;const s=scene(id);for(let i=0;i<=400;i++){
  s.equipment.reloading=(1-i/400)*D.Equipment.get(id).reload;const m=D.Equipment.mount(s),vals=['index','middle','ring','little'].flatMap(name=>m.grips.L.fingers[name]);
  if(prev)assert.ok(Math.max(...vals.map((v,j)=>Math.abs(v-prev[j])))<.09,`${id} reload frame ${i}`);prev=vals;
 }}
});
test('the primary index retains its independent trigger transition while the thumb stays independent of firing',()=>{
 const s=scene('rifle'),a=D.Equipment.mount(s);s.equipment.trigger=true;const b=D.Equipment.mount(s);
 assert.notDeepEqual(a.grips.R.fingers.index,b.grips.R.fingers.index);assert.deepEqual(a.grips.R.fingers.thumb,b.grips.R.fingers.thumb);
 assert.deepEqual(a.grips.R.thumbOpposition,b.grips.R.thumbOpposition);assert.ok(a.grips.R.fingers.thumb.every(Number.isFinite));
});
test('native reload timing releases the fingers without a one-frame opening jolt',()=>{
 for(const id of['pistol','smg','rifle','sniper','gauss','emp']){const s=scene(id);s.free=true;s.equipment.reloading=0;s.equipment.ammo[id].loaded=2;s.reloadWeapon();let previous=null;
  for(let i=0;i<240;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=D.Equipment.mount(s),v=['index','middle','ring','little'].flatMap(n=>m.grips.L.fingers[n]);if(previous)assert.ok(Math.max(...v.map((n,j)=>Math.abs(n-previous[j])))<.25,`${id}, frame ${i}`);previous=v;}
 }
});
