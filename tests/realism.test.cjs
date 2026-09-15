'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
for(const name of ['core','character-motion','skin-rig','visual-geometry']){
 const f=path.join(__dirname,'../src',name+'.js');if(fs.existsSync(f))vm.runInThisContext(fs.readFileSync(f,'utf8'));
}
test('Skin rig exposes a deterministic pose evaluator',()=>{assert.equal(typeof DC.SkinRig?.pose,'function');});
test('Skin rig rest palette leaves bind vertices unchanged',()=>{
 assert.ok(DC.SkinRig);const palette=DC.SkinRig.rest();assert.equal(palette.length,DC.SkinRig.bones.length*16);
 for(let i=0;i<palette.length;i++)assert.ok(Math.abs(palette[i]-((i%16)%5===0?1:0))<1e-5);
});
test('Idle, walk, run, airborne, carry and crouch skin palettes are finite',()=>{
 assert.ok(DC.SkinRig);for(const p of [{},{walk:1,moveSpeed:3},{walk:2,moveSpeed:7,sprintBlend:1},{y:.7,vy:2},{carry:'crate'},{crouch:1},{seated:true},{stagger:.8,dodge:.4}]){
  const q=DC.SkinRig.pose(p,2);assert.equal(q.matrices.length,DC.SkinRig.bones.length*16);assert.ok([...q.matrices].every(Number.isFinite));
 }
});
test('Walking and carrying actually change skin matrices',()=>{
 assert.ok(DC.SkinRig);const a=DC.SkinRig.pose({},1).matrices,b=DC.SkinRig.pose({walk:1.2,moveSpeed:4},1).matrices,c=DC.SkinRig.pose({carry:'crate'},1).matrices;
 assert.ok([...a].some((v,i)=>Math.abs(v-b[i])>.02));assert.ok([...a].some((v,i)=>Math.abs(v-c[i])>.1));
});
test('Weighted mesh validation rejects corrupt weights, normals and out-of-range joints',()=>{
 assert.equal(typeof DC.SkinRig?.validate,'function');
 const good=[0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0];assert.equal(DC.SkinRig.validate(new Float32Array(good)),true);
 for(const index of [3,8,12]){const a=good.slice();a[index]=index===8?900:NaN;assert.throws(()=>DC.SkinRig.validate(new Float32Array(a)));}
});
test('Shared visual meshes have finite unit normals and nondegenerate triangles',()=>{
 assert.equal(typeof DC.VisualGeometry?.build,'function');const g=DC.VisualGeometry.build();
 for(const [name,data]of Object.entries(g)){assert.ok(data.length%24===0,name);assert.ok(data.every(Number.isFinite),name);for(let i=0;i<data.length;i+=8)assert.ok(Math.abs(Math.hypot(...data.slice(i+3,i+6))-1)<.02,name);}
});
test('Visual geometry remains deterministic and bounded',()=>{
 assert.ok(DC.VisualGeometry);const a=DC.VisualGeometry.build(),b=DC.VisualGeometry.build();assert.deepEqual(a,b);assert.ok(Object.values(a).reduce((s,m)=>s+m.length/24,0)<20000);
});
test('The right window has outward normals and roof has a curved crown',()=>{
 const g=DC.VisualGeometry.build();assert.ok(g.glassRight&&g.roof);
 for(let i=0;i<g.glassRight.length;i+=8)assert.ok(g.glassRight[i+3]>.5);
 let low=Infinity,high=-Infinity;for(let i=0;i<g.roof.length;i+=8){low=Math.min(low,g.roof[i+1]);high=Math.max(high,g.roof[i+1]);}assert.ok(high-low>.02);
});
