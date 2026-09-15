'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-motion','skin-rig'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const R=DC.SkinRig;
const maxDiff=(a,b)=>Math.max(...a.map((v,i)=>Math.abs(v-b[i])));
test('cervical look request changes head without rotating the torso',()=>{
 const a=R.pose({lookYaw:-.70},1),b=R.pose({lookYaw:.70},1);
 assert.ok(maxDiff(a.matrices.slice(64,80),b.matrices.slice(64,80))>.6);
 assert.deepEqual(a.matrices.slice(0,48),b.matrices.slice(0,48));
});
test('head orientation has explicit bounded neck/head diagnostics',()=>{
 const q=R.pose({lookYaw:9,lookPitch:-9,lookRoll:9},1);assert.ok(q.cervical);
 assert.ok(Math.abs(q.cervical.yaw)<=.850001);assert.ok(Math.abs(q.cervical.pitch)<=.400001);assert.ok(Math.abs(q.cervical.roll)<=.220001);
});
test('cervical request never changes feet or wrist targets',()=>{
 const n={x:0,z:0,yaw:0,moveSpeed:1.4,walk:2};const a=R.pose(n,2),b=R.pose({...n,lookYaw:.7,lookPitch:.15},2);
 for(const k of ['footL','footR','handL','handR'])assert.deepEqual(a.matrices.slice(R.ids[k]*16,R.ids[k]*16+16),b.matrices.slice(R.ids[k]*16,R.ids[k]*16+16));
});
test('cervical motion is deterministic, finite and does not alter actor input',()=>{
 for(const n of [{lookYaw:NaN,lookPitch:Infinity},{lookRoll:-Infinity},{moveSpeed:6.2,lookYaw:.4,crouch:1},{seated:true,lookYaw:-.8}]){
  const before=structuredClone(n),q=R.pose(n,1);assert.deepEqual(n,before);assert.equal(q.matrices.length,49*16);assert.ok([...q.matrices].every(Number.isFinite));assert.deepEqual(q,R.pose(n,1));
 }
});
test('small look steps do not jump at neutral or range limits',()=>{
 for(let yaw=-1;yaw<=1;yaw+=.04){const a=R.pose({lookYaw:yaw},1),b=R.pose({lookYaw:yaw+.0001},1);assert.ok(maxDiff(a.matrices,b.matrices)<.0003);}
});
test('neck thickness must not inflate chin, lips or jaw tip',()=>{
 for(const p of [[.024,1.557,.11],[0,1.580,.115],[.05,1.62,.092]]){
  const a=DC.Appearance.shapePoint(p,40,0,0,-1),b=DC.Appearance.shapePoint(p,40,0,0,1);
  assert.ok(maxDiff(a,b)<.0001,JSON.stringify({p,a,b}));
 }
});
test('neckline follows neck thickness and remains unchanged elsewhere',()=>{
 const p=[.063,1.48,-.010];const a=DC.Appearance.shapePoint(p,31,0,0,-1),b=DC.Appearance.shapePoint(p,31,0,0,1);assert.ok(b[0]-a[0]>.011);
 const hand=[.2637,.840,.015];assert.deepEqual(DC.Appearance.shapePoint(hand,30,0,0,1),hand);
 const collarEdge=[.14,1.43,.035];assert.deepEqual(DC.Appearance.shapePoint(collarEdge,31,0,0,1),collarEdge);
});
