'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','appearance','character-fit','weapon-handling','equipment','equipment-simulation','character-motion','skin-rig','dual-quaternion','hero-asset','hair-geometry'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
vm.runInThisContext(fs.readFileSync('tools/qa/character_stage.js','utf8'));
const B=DCCharacterBenchmark;
test('benchmark measures real canonical surfaces separately from rig pivots',()=>{
 const m=B.profileMetrics(DC.Appearance.default());
 assert.equal(m.boneCount,49);assert.ok(m.headToChestPivotM>.15&&m.headToChestPivotM<.4);
 assert.ok(m.surfaces.neckBand.samples>20);assert.ok(m.surfaces.face.samples>1000);
 assert.ok(m.surfaces.neckBand.widthM>.05&&m.surfaces.neckBand.widthM<.25);
});
test('reference measurements are deterministic, read-only and use the fitted bind',()=>{
 const look=DC.Appearance.default(),before=JSON.stringify(look),a=B.profileMetrics(look),b=B.profileMetrics(look);
 assert.deepEqual(a,b);assert.equal(JSON.stringify(look),before);
 assert.ok(B.profileMetrics({...look,neckLength:-1}).headToChestPivotM<B.profileMetrics({...look,neckLength:1}).headToChestPivotM);
});
test('constitution changes cervical surface but not the upper arm joint spacing',()=>{
 const a=B.profileMetrics({...DC.Appearance.default(),build:-1,neck:-1}),b=B.profileMetrics({...DC.Appearance.default(),build:1,neck:1});
 assert.ok(a.surfaces.neckBand.widthM<b.surfaces.neckBand.widthM);
 assert.equal(a.shoulderJointSpanM,b.shoulderJointSpanM);
});
test('profile validation rejects invalid data instead of returning misleading metrics',()=>{
 assert.throws(()=>B.profileMetrics({...DC.Appearance.default(),neckLength:NaN}));
});

test('geometry budgets derive separately from renderer parts and groom buffers',()=>{
 const lods=[[{vertices:300}],[{vertices:150}],[{vertices:60}]],q=B.geometryBudget(lods,0);
 assert.deepEqual(q.map(x=>x.bodyTriangles),[100,50,20]);
 for(let i=0;i<3;i++)assert.equal(q[i].hairTriangles,DC.HairGeometry.build(0,i).reduce((n,p)=>n+p.data.length/48,0));
 assert.ok(q[0].totalTriangles>q[1].totalTriangles&&q[1].totalTriangles>q[2].totalTriangles);
});
test('bald option contributes zero hair geometry without changing body parts',()=>{
 const q=B.geometryBudget([[{vertices:300}],[{vertices:150}],[{vertices:60}]],3);
 assert.ok(q.every(x=>x.hairTriangles===0&&x.totalTriangles===x.bodyTriangles));
});
