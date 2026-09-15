/* #6 / CONTACT-03/05/06: preserve the full arm trajectory, not only end-point IK. */
'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
for(const name of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-fit','weapon-handling','equipment','equipment-simulation','character-motion','skin-rig','dual-quaternion','hero-asset'])vm.runInThisContext(fs.readFileSync('src/'+name+'.js','utf8'));
const D=DC,dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function setup(id='binoculars',crouch=0){const s=new D.Simulation(new D.World(1337));s.time=1.25;Object.assign(s.player,{x:4,z:36,yaw:0,y:0,car:null,moveSpeed:0,crouch});s.equipWeapon(id);s.equipment.handling.ready=1;return s;}
function sample(s){const m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=D.SkinRig.pose(n,s.time);return {m,n,q,point(name){const j=D.SkinRig.ids[name];return D.SkinRig.transform(q.matrices.subarray(j*16,j*16+16),D.SkinRig.bones[j][2]);}};}
test('compact optical raise avoids elbow-plane inversion while crouching',()=>{
 const s=setup('binoculars',1);let previous=null,worst=0;
 for(let i=0;i<=180;i++){s.equipment.aimWeight=i/180;const q=sample(s);if(previous)for(const k of ['L','R']){const step=dist(q.point('forearm'+k),previous.point('forearm'+k));worst=Math.max(worst,step);assert.ok(step<.012,`aim=${i/180} ${k} elbow moved ${step}m for 1/180 raise`);}previous=q;}
 console.log('opticalRaiseMaxElbowStepM',worst);
});
test('native aiming cadence cannot flick the upper arm when raising or lowering optics',()=>{
 const s=setup('binoculars',1);let previous=sample(s),worst=0;
 for(let i=0;i<150;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:i<75});const q=sample(s);for(const k of ['L','R']){const step=dist(q.point('forearm'+k),previous.point('forearm'+k));worst=Math.max(worst,step);assert.ok(step<.045,`step=${i} ${k} elbow displacement ${step}m`);}previous=q;}
 console.log('nativeOpticalMaxElbowStepM',worst);
});
test('fully raised optical elbows stay below their wrists in the supported central viewing range',()=>{
 for(const crouch of [0,1])for(const pitch of [-.25,0,.25]){const s=setup('binoculars',crouch);s.equipment.aimWeight=1;s.equipment.pitch=pitch;const q=sample(s);for(const k of ['L','R'])assert.ok(q.point('forearm'+k)[1]<q.point('hand'+k)[1]+.02,`crouch=${crouch} pitch=${pitch} ${k} elbow above optical wrist`);}
});
test('optical postures preserve exact segment lengths, oriented palmar contact and deterministic reads',()=>{
 for(const crouch of [0,1])for(const yaw of [-2.2,0,.9])for(const pitch of [-.75,0,.75])for(const aim of [0,.5,.97,1]){
  const s=setup('binoculars',crouch);s.player.yaw=yaw;s.equipment.pitch=pitch;s.equipment.aimWeight=aim;const saved=JSON.stringify(s.serialize()),q=sample(s),second=sample(s);
  assert.deepEqual(q.q.matrices,second.q.matrices);assert.equal(JSON.stringify(s.serialize()),saved);
  for(const k of ['L','R']){
   for(const [a,b] of [['upperArm','forearm'],['forearm','hand']]){const expected=dist(D.SkinRig.bones[D.SkinRig.ids[a+k]][2],D.SkinRig.bones[D.SkinRig.ids[b+k]][2]);assert.ok(Math.abs(dist(q.point(a+k),q.point(b+k))-expected)<1e-5);}
   const palm=D.SkinRig.palmPoint(q.q,q.n,k),t=q.m.palmContacts[k];assert.ok(Math.hypot(palm.x-t.x,palm.y-t.y,palm.z-t.z)<.012);assert.ok(q.q.handContacts[k].orientationError<1e-5);
  }
 }
});
test('non-optical families retain their established elbow references and shared mount contract',()=>{
 for(const w of D.Equipment.catalog.filter(w=>!['none','optics'].includes(w.kind))){const s=setup(w.id);for(const aim of [0,1])for(const progress of [0,.3,.65,.9]){s.equipment.aimWeight=aim;s.equipment.reloading=progress*(w.reload||0);const {m}=sample(s);for(const k of ['L','R'])if(m.hands[k])assert.deepEqual(m.hands[k].pole,k==='L'?[-.72,-1,-.18]:[.60,-1,-.30]);}}
});
test('optical elbow reference stays away from collinearity across the entire supported pitch and crouch range',()=>{
 const s=setup();let min=1;
 for(const crouch of [0,.5,1])for(const pitch of [-.75,-.375,0,.375,.75])for(let i=0;i<=40;i++){
  s.player.crouch=crouch;s.equipment.pitch=pitch;s.equipment.aimWeight=i/40;const q=sample(s);
  for(const k of ['L','R']){const a=q.point('upperArm'+k),b=q.point('hand'+k),dir=D.normalize(b.map((v,j)=>v-a[j])),pole=D.normalize(q.m.hands[k].pole),sine=Math.sqrt(Math.max(0,1-D.dot(dir,pole)**2));min=Math.min(min,sine);assert.ok(sine>.70,`poorly conditioned elbow reference ${sine} crouch=${crouch} pitch=${pitch} aim=${i/40}`);}
 }
 console.log('minimumOpticalPoleSine',min);
});
test('optical presentation settles within half a second and leaves firearm timing, inventory and zoom unchanged',()=>{
 const optic=setup(),rifle=setup('rifle'),snapshot=D.Equipment.snapshot(optic.equipment);
 for(let i=0;i<30;i++){optic.equipmentStep(1/60,{aim:true});rifle.equipmentStep(1/60,{aim:true});}
 assert.ok(optic.equipment.aimWeight>.94&&optic.equipment.aimWeight<.97);assert.ok(Math.abs(rifle.equipment.aimWeight-(1-Math.exp(-6)))<1e-6);
 assert.deepEqual(D.Equipment.snapshot(optic.equipment),snapshot);
 for(let i=0;i<30;i++)optic.equipmentStep(1/60,{aim:false});assert.ok(optic.equipment.aimWeight<.05);
});
test('upper garment surface stays continuous through the native optical cycle',()=>{
 const part=D.HeroAsset.parts.find(p=>p.name==='jacket'),raw=Buffer.from(part.data,'base64'),vertices=[],seen=new Set();
 for(let i=0;i<part.vertices;i++){const o=i*24,p=[0,2,4].map(k=>raw.readInt16LE(o+k)/1e4),key=p.join(',');if(p[1]<1.24||p[1]>1.50||Math.abs(p[0])<.13||seen.has(key))continue;seen.add(key);if(seen.size%7===0)vertices.push({p,j:[16,17,18,19].map(k=>raw[o+k]),w:[20,21,22,23].map(k=>raw[o+k]/255)});}
 assert.ok(vertices.length>150,'sample upper shoulder and axilla skin, not only joints');let worst=0;
 for(const crouch of [0,1]){
  const s=setup('binoculars',crouch);let previous=null;
  for(let i=0;i<150;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:i<75});const {q}=sample(s),dq=D.DualQuaternion.pack(q.matrices),points=vertices.map(v=>D.DualQuaternion.transform(dq,v.p,v.j,v.w));
   if(previous)for(let j=0;j<points.length;j++){const step=dist(points[j],previous[j]);worst=Math.max(worst,step);assert.ok(step<.05,`crouch=${crouch} tick=${i} upper garment moved ${step}m`);}previous=points;
  }
 }
 console.log('nativeOpticalUpperGarmentMaxStepM',worst,'surfaceSamplesPerPose',vertices.length);
});
