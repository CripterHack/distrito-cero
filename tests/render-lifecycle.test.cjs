'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const ctx={DC:{SkinRig:{bones:Array(49)},rng:()=>()=>0},Float32Array,Map,Set,console};vm.createContext(ctx);
vm.runInContext(fs.readFileSync('src/renderer.js','utf8'),ctx);
const Base=ctx.DC.Renderer;
vm.runInContext(fs.readFileSync('src/frontier-renderer.js','utf8'),ctx);
const Frontier=ctx.DC.Renderer;
function instance(Type,{disposed=false,lost=false,ledgerDisposed=false}={}){
 const r=Object.create(Type.prototype);Object.assign(r,{disposed,resources:{disposed:ledgerDisposed},gl:{isContextLost:()=>lost},frame:17,camera:{target:[700,1,700]},renderOrigin:[0,0],lightTime:5,world:{seed:42,activeChunks:[{key:'0:0',cells:[{roads:{},x:0,z:0}]}]},streamSeed:42,sectorGPU:new Map(),meshes:{},static:{},dynamic:{}});return r;
}
for(const [name,options] of [['disposed generation',{disposed:true}],['lost context before event',{lost:true}],['disposed ledger',{ledgerDisposed:true}]]){
 test('base render refuses '+name+' before dynamic state or GL access',()=>{
  const r=instance(Base,options);r.updateDynamic=()=>{throw Error('should not build dynamic geometry');};
  assert.equal(r.render({}),false);assert.equal(r.frame,17);
 });
 test('streaming render refuses '+name+' before rebuilding empty mesh lists',()=>{
  const r=instance(Frontier,options);const origin=r.renderOrigin;
  assert.equal(r.render({}),false);assert.equal(r.frame,17);assert.equal(r.sectorGPU.size,0);assert.equal(r.renderOrigin,origin);assert.equal(r.lightTime,5);
 });
}
test('late direct sector sync on retired renderer is a no-op, even after context returns',()=>{
 const r=instance(Frontier,{disposed:true,lost:false});assert.equal(r.syncSectors(2),false);assert.equal(r.sectorGPU.size,0);
});
test('guard does not swallow invalid mesh errors in a live streaming renderer',()=>{
 const r=instance(Frontier);assert.throws(()=>r.render({}),/push/);
});
test('guard does not swallow an unrelated live draw exception',()=>{
 const r=instance(Base);r.updateDynamic=()=>{throw Error('live draw defect');};assert.throws(()=>r.render({}),/live draw defect/);
});
