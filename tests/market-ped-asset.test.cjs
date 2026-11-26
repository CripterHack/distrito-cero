'use strict';
const {test}=require('node:test'), assert=require('node:assert/strict'), fs=require('node:fs'), path=require('node:path'), vm=require('node:vm'), crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
function load(){
 const ctx=vm.createContext({DC:{},atob,Float32Array,Uint8Array,DataView});
 for(const name of ['data','pose','asset'])vm.runInContext(fs.readFileSync(path.join(root,'src','market-ped-'+name+'.js'),'utf8'),ctx);
 return ctx.DC;
}
test('market pedestrian comes from the reviewed skinned GLB, with two budgeted LODs',()=>{
 const {MarketPedAsset:asset,MarketPedData:data}=load();
 assert.equal(data.sourceSha256,crypto.createHash('sha256').update(fs.readFileSync(path.join(root,data.source))).digest('hex'));
 assert.equal(asset.levels.length,2);
 assert.match(asset.atlas,/^data:image\/webp;base64,UklGR/);
 assert.ok(asset.levels[0].triangles<=12000 && asset.levels[0].triangles>4000);
 assert.ok(asset.levels[1].triangles<asset.levels[0].triangles*.62);
 for(const [i,level] of asset.levels.entries()){
  const vertices=asset.decodeLevel(i);
  assert.equal(vertices.length,level.triangles*3*16);
  let floor=Infinity,top=-Infinity,arms=0;
  const influenced=new Set();
  for(let k=0;k<vertices.length;k+=16){
   const v=vertices.subarray(k,k+16);
   assert.ok(v.every(Number.isFinite));
   assert.ok(Math.abs(Math.hypot(...v.subarray(3,6))-1)<.0001);
   assert.ok(v[6]>=0&&v[6]<=1&&v[7]>=0&&v[7]<=1);
   assert.ok(Math.abs(v[12]+v[13]+v[14]+v[15]-1)<1e-6);
   for(let j=0;j<4;j++){assert.ok(Number.isInteger(v[8+j])&&v[8+j]>=0&&v[8+j]<49);if(v[12+j]>0)influenced.add(v[8+j]);}
   floor=Math.min(floor,v[1]);top=Math.max(top,v[1]);arms=Math.max(arms,Math.abs(v[0]));
  }
  assert.ok(floor>=-.001&&floor<=.003&&top>1.84&&top<1.86&&arms>.89);
  assert.equal(influenced.size,49);
 }
});
