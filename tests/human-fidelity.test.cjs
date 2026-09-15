'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict'),{test}=require('node:test');
for(const name of ['core','character-motion','skin-rig','crowd-geometry','human-materials','hero-asset'])if(fs.existsSync(__dirname+'/../src/'+name+'.js'))vm.runInThisContext(fs.readFileSync(__dirname+'/../src/'+name+'.js','utf8'));
test('anatomical head replaces the parametric ring approximation',()=>{
 assert.ok(DC.HeroAsset.parts.some(p=>p.name==='face'));
 assert.match(DC.HeroAsset.provenance,/MakeHuman/);
 const f=DC.HeroAsset.parts.find(p=>p.name==='face');assert.ok(f.vertices>15000&&f.vertices<60000);
});
test('embedded skin maps have correct roles and bounded resolutions',()=>{
 assert.ok(DC.HumanMaterials);for(const k of ['albedo','normal','roughness']){
 const t=DC.HumanMaterials[k];assert.ok(t.width<=1024&&t.height<=1024);assert.match(t.uri,/^data:image\//);assert.ok(t.uri.length>100);
 }assert.equal(DC.HumanMaterials.albedo.colorSpace,'srgb');assert.equal(DC.HumanMaterials.normal.colorSpace,'linear');
});
test('skin tint is relative and preserves the reference appearance',()=>{
 assert.equal(typeof DC.HumanMaterials?.tint,'function');const c=DC.HumanMaterials.tint(DC.HumanMaterials.referenceSkin);assert.deepEqual(c,[1,1,1]);for(const s of [[.05,.03,.02],[1,1,1],[.44,.275,.185]])assert.ok(DC.HumanMaterials.tint(s).every(x=>Number.isFinite(x)&&x>0&&x<4));
});
test('LOD does not merge opposite UV seam corners',()=>{
 const a=[];for(const uv of [0.01,.99])for(const p of [[0,0,0],[1,0,0],[0,1,0]])a.push(...p,0,0,1,uv,.2,4,0,0,0,1,0,0,0);
 const out=DC.CrowdGeometry.reduce(new Float32Array(a),.01,{preserveUV:true});assert.equal(out.length,96);assert.ok(out[6]<.02);assert.ok(out[54]>.98);
});
