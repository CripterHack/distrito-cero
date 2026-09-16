'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const {D,R,stats}=require('./helpers/finger_surfaces.cjs');
function scene(id='rifle',progress=0){const s=new D.Simulation(new D.World());Object.assign(s.player,{x:0,z:0,yaw:0,car:null});s.time=1.25;Object.assign(s.equipment,{selected:id,aimWeight:1,reloading:progress?(1-progress)*D.Equipment.get(id).reload:0});return s;}
test('thumb skin does not cut through the dominant grip while the other digits hold it',()=>{const v=stats(scene(),'R','thumb','grip');assert.ok(v.min>-.003&&v.min<.009,`dominant thumb signed proxy distance ${v.min}`);});
test('support thumb opposes the fingers outside the forward support',()=>{const v=stats(scene(),'L','thumb','fore');assert.ok(v.min>-.003&&v.min<.009,`support thumb signed proxy distance ${v.min}`);});
test('thumb keeps contact outside the moving piece during its held phase',()=>{for(const id of ['rifle','pistol']){const v=stats(scene(id,.5),'L','thumb',id==='pistol'?'pistolMagazine':'magazine');assert.ok(v.min>-.003&&v.min<.009,`${id} thumb signed proxy distance ${v.min}`);}});
function pt(q,f,j,t){const m=q.matrices.subarray(R.ids[f.bones[j]]*16,R.ids[f.bones[j]]*16+16),a=f.joints[j],b=j<2?f.joints[j+1]:f.tip;return R.transform(m,a.map((v,i)=>v+(b[i]-v)*t));}
test('distal thumb segments do not substitute prop penetration with crossing other digits',()=>{
 for(const [id,k,p]of[['rifle','R',0],['rifle','L',.5],['pistol','L',.5]]){
  const s=scene(id,p),m=D.Equipment.mount(s),q=R.pose(D.WeaponHandling.actor(s.player,m,s.equipment),s.time),f=R.fingers[k].find(f=>f.name==='thumb');let min=1;
  for(const other of R.fingers[k].filter(f=>f.name!=='thumb'))for(let a=1;a<3;a++)for(let b=0;b<3;b++)for(const t of[0,.5,1])for(const u of[0,.5,1]){const x=pt(q,f,a,t),y=pt(q,other,b,u);min=Math.min(min,Math.hypot(...x.map((v,i)=>v-y[i]))-f.radius*.8-other.radius*.9);}
  assert.ok(min>-.003,`${id}/${k} thumb-other capsule overlap ${min}`);
 }
});
test('complete native reload keeps the thumb tip trajectory continuous',()=>{
 const s=scene();s.free=true;s.equipment.ammo.rifle.loaded=4;s.reloadWeapon();let prev=null,worst=0,at;
 for(let i=0;i<220;i++){s.time+=1/60;s.equipmentStep(1/60,{aim:true});const m=D.Equipment.mount(s),q=R.pose(D.WeaponHandling.actor(s.player,m,s.equipment),s.time),f=R.fingers.L.find(f=>f.name==='thumb'),p=pt(q,f,2,1);p[1]+=q.rootY;if(prev){const d=Math.hypot(...p.map((v,j)=>v-prev[j]));if(d>worst){worst=d;at={i,stage:m.reloadStage,remaining:s.equipment.reloading};}}prev=p;}
 assert.ok(worst<.035,JSON.stringify({worst,at}));
});
test('thumb coverage survives all primary families, crouch, pitch and world transforms',()=>{
 for(const id of ['pistol','revolver','smg','rifle','shotgun','sniper','gauss','emp','launcher'])for(const [a,p,c]of[[0,-.4,0],[1,.35,1]]){
 const s=scene(id);Object.assign(s.player,{yaw:.8,x:700,z:-600,crouch:c});Object.assign(s.equipment,{aimWeight:a,pitch:p});const v=stats(s,'R','thumb','grip');assert.ok(v.min>-.003&&v.min<.009,`${id}: ${v.min}`);
 }
});
test('moving detachable pieces retain thumb surface contact in the held phase',()=>{
 for(const id of ['pistol','smg','rifle','sniper','gauss','emp'])for(const progress of[.32,.52,.72]){const s=scene(id,progress);s.player.crouch=1;s.equipment.pitch=.3;const v=stats(s,'L','thumb',id==='pistol'?'pistolMagazine':'magazine');assert.ok(v.min>-.003&&v.min<.009,`${id}/${progress}: ${v.min}`);}
});
test('opposition is local to the thumb and preserves every segment length and non-thumb matrix',()=>{
 const s=scene('rifle',.5),m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=R.pose(n,s.time),baseline=structuredClone(n);
 for(const k of['L','R'])delete baseline.handGrips[k].thumbOpposition;
 const old=R.pose(baseline,s.time),thumbIds=new Set(['L','R'].flatMap(k=>R.fingers[k].find(f=>f.name==='thumb').bones.map(b=>R.ids[b])));
 for(let i=0;i<R.bones.length;i++)if(!thumbIds.has(i))assert.deepEqual(q.matrices.subarray(i*16,i*16+16),old.matrices.subarray(i*16,i*16+16));
 for(const k of ['L','R']){const f=R.fingers[k].find(f=>f.name==='thumb');for(let j=0;j<3;j++){const a=pt(q,f,j,0),b=pt(q,f,j,1),c=f.joints[j],d=j<2?f.joints[j+1]:f.tip;assert.ok(Math.abs(Math.hypot(...a.map((v,i)=>v-b[i]))-Math.hypot(...c.map((v,i)=>v-d[i])))<1e-6);}}
});
test('missing and invalid opposition retain the existing non-contact thumb behavior',()=>{
 const n={grip:.6},base=R.pose(n,1.25),badValues=[null,[NaN,0,0],[0,Infinity,0],[0,0],{},'invalid'];
 for(const value of badValues){const g=R.gripProfile(n,'R'),q=R.pose({...n,handGrips:{R:{...g,thumbOpposition:value}}},1.25);assert.deepEqual(q.matrices,base.matrices);}
});
test('optical and melee poses are not changed by the new authored contact references',()=>{
 for(const id of ['binoculars','baton','blade','grenade']){const m=D.Equipment.mount(scene(id));for(const g of Object.values(m.grips))assert.equal(g.thumbOpposition,undefined);}
});
test('thumb presentation is deterministic and cannot mutate persistent state or its caller',()=>{
 const s=scene('rifle',.5),before=JSON.stringify(s.serialize()),m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),input=JSON.stringify(n),a=R.pose(n,s.time),b=R.pose(n,s.time);
 assert.deepEqual(a.matrices,b.matrices);assert.equal(JSON.stringify(s.serialize()),before);assert.equal(JSON.stringify(n),input);assert.ok(!before.includes('thumbOpposition'));
});
