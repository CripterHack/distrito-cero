'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-motion','skin-rig','dual-quaternion'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const A=DC.Appearance;
test('cervical volume responds to constitution independently of neck preference',()=>{
 const p=[.062,1.52,-.01];const thin=A.shapePoint(p,40,-1,0,0),broad=A.shapePoint(p,40,1,0,0);
 assert.ok(broad[0]-thin[0]>.005,'Neck must follow build instead of leaving a thin stalk below larger torso');
 assert.ok(broad[0]-thin[0]<.013,'Constitution coupling is restrained');
});
test('neck preference is bounded across constitution range',()=>{
 for(const build of [-1,0,1])for(const neck of [-1,0,1]){
  const p=[.063,1.52,-.01],q=A.shapePoint(p,40,build,0,neck);
  assert.ok(q[0]>=.053&&q[0]<=.074,JSON.stringify({build,neck,q}));
 }
});
test('neck preferences preserve chin, upper face, fingers, shoes and eye geometry',()=>{
 for(const [p,mat]of [[[.024,1.557,.11],40],[[.031,1.671,.09],40],[[.2637,.84,.015],30],[[.108,.03,.08],4]]){
  const a=A.shapePoint(p,mat,-1,0,-1),b=A.shapePoint(p,mat,1,0,1);assert.deepEqual(a,b);
 }
});
test('clothing opening responds at the wider neck circumference',()=>{
 const p=[.086,1.48,-.01],a=A.shapePoint(p,31,0,0,-1),b=A.shapePoint(p,31,0,0,1);
 assert.ok(b[0]-a[0]>.010,'Widened collar must follow cervical preference');
});
test('volume settings do not modify bone dimensions, physics or profile schema',()=>{
 const n={lookYaw:.6,lookPitch:.15,moveSpeed:1.2,walk:2};const a=DC.SkinRig.pose(n,1);
 assert.equal(DC.SkinRig.bones.length,49);assert.equal(A.default().version,1);
 const old={...A.default()};delete old.neck;assert.equal(A.copy(old).neck,0);
 assert.deepEqual(DC.SkinRig.pose(n,1),a);assert.deepEqual(n,{lookYaw:.6,lookPitch:.15,moveSpeed:1.2,walk:2});
});
