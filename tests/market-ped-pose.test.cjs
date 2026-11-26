const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const {decodeGlb, accessor} = require('../tools/export_human_tangents.cjs');
const {buildPose} = require('../tools/prepare_market_ped_pose.cjs');

const root = path.resolve(__dirname, '..');
const {document:doc, binary} = decodeGlb(fs.readFileSync(path.join(root,'assets/higgsfield-20261125/character-walk.glb')));
const skin = doc.skins[0];
const jointCount = skin.joints.length;
const source = id => accessor(doc,binary,id);
const parents = new Map(doc.nodes.flatMap((n,i)=>(n.children||[]).map(child=>[child,i])));
const identity = [0,0,0,1];

function rig() {
  const ctx = vm.createContext({DC:{MarketPedData:{pose:buildPose(doc,binary)}},atob});
  vm.runInContext(fs.readFileSync(path.join(root,'src/market-ped-pose.js'),'utf8'),ctx);
  return ctx.DC.MarketPedPose;
}
function matrixProduct(a,b) {
  return Array.from({length:16},(_,i)=>{
    const row=i%4, col=i-row;
    return a[row]*b[col]+a[row+4]*b[col+1]+a[row+8]*b[col+2]+a[row+12]*b[col+3];
  });
}
function rotate(q,v) {
  const u=q.slice(0,3), cross=(a,b)=>a.map((_,i)=>a[(i+1)%3]*b[(i+2)%3]-a[(i+2)%3]*b[(i+1)%3]);
  const uv=cross(u,v), uuv=cross(u,uv);
  return v.map((x,i)=>x+2*(q[3]*uv[i]+uuv[i]));
}
function spherical(a,b,t) {
  let dot=a.reduce((s,n,i)=>s+n*b[i],0);
  if (dot<0) { b=b.map(n=>-n); dot=-dot; }
  const angle=Math.acos(Math.min(1,dot));
  const result=angle<1e-6?a.map((x,i)=>x*(1-t)+b[i]*t):
    a.map((x,i)=>(x*Math.sin((1-t)*angle)+b[i]*Math.sin(t*angle))/Math.sin(angle));
  const length=Math.hypot(...result);
  return result.map(x=>x/length);
}
function sourceLocals(name,phase) {
  const a=doc.animations.find(a=>a.name===name);
  const locals=doc.nodes.map(n=>({rotation:identity,translation:n.translation||[0,0,0]}));
  for (const channel of a.channels) {
    const {input,output}=a.samplers[channel.sampler], times=source(input), values=source(output);
    const progress=name==='Giro'?Math.min(1,Math.max(0,phase)):phase-Math.floor(phase);
    const time=progress*times.value(times.a.count-1);
    let j=0;
    while(j<times.a.count-2 && times.value(j+1)<time) j++;
    const t=(time-times.value(j))/(times.value(j+1)-times.value(j));
    const frame=n=>Array.from({length:values.width},(_,k)=>values.value(n,k));
    const lo=frame(j),hi=frame(j+1), kind=channel.target.path;
    locals[channel.target.node][kind]=kind==='rotation'?spherical(lo,hi,t):lo.map((v,k)=>v+(hi[k]-v)*t);
  }
  return locals;
}
function sourceMatrices(walkPhase,idlePhase,blend,runBlend=0,oneShot=false) {
  const walk=sourceLocals(oneShot?'Giro':'Marcha',walkPhase),idle=sourceLocals('Reposo',idlePhase);
  const run=runBlend?sourceLocals('Carrera',walkPhase):walk;
  const cache=new Map();
  function world(node) {
    if(cache.has(node))return cache.get(node);
    const w=walk[node], r=run[node], i=idle[node];
    const q=spherical(i.rotation,spherical(w.rotation,r.rotation,runBlend),blend);
    const columns=[[1,0,0],[0,1,0],[0,0,1]].flatMap(axis=>[...rotate(q,axis),0]);
    const locomotion=w.translation.map((v,k)=>v+runBlend*(r.translation[k]-v));
    const local=[...columns,...i.translation.map((v,k)=>v+blend*(locomotion[k]-v)),1];
    const m=parents.has(node)?matrixProduct(world(parents.get(node)),local):local;
    cache.set(node,m);
    return m;
  }
  const bind=doc.accessors[skin.inverseBindMatrices], view=doc.bufferViews[bind.bufferView];
  return skin.joints.flatMap((node,i)=>{
    const byteOffset=(view.byteOffset||0)+(bind.byteOffset||0)+i*(view.byteStride||64);
    return matrixProduct(world(node),Array.from({length:16},(_,k)=>binary.readFloatLE(byteOffset+4*k)));
  });
}
test('native GLB skin matrices reproduce all source joints in rest, walk and local pose blends',()=>{
  const implementation=rig(), out=new Float32Array(jointCount*16);
  for(const [name,clip] of Object.entries(implementation.clips)){
    const animation=doc.animations.find(a=>a.name===name), t=source(animation.samplers[0].input);
    assert.equal(clip.duration,t.value(t.a.count-1));
  }
  const mixes=[[0,0],[.37,0],[1,0]];
  if(implementation.clips.Carrera)mixes.push([1,1],[1,.54],[.68,.54]);
  for(const [blend,run] of mixes)for(const phase of [0,.0475,.125,.375,.61,.875,.999,-.125,1.125]){
    const idle=phase*.81+.064;
    implementation.writePalette(out,phase,idle,blend,run);
    const expected=sourceMatrices(phase,idle,blend,run);
    let error=0;
    for(let k=0;k<out.length;k++) error=Math.max(error,Math.abs(out[k]-expected[k]));
    assert.ok(error<.000025,`phase ${phase}, blend ${blend}, max matrix error ${error}`);
  }
});
test('cyclic playback closes on every joint and is independent of actor sampling order',()=>{
  const implementation=rig(), buffer=new Float32Array(jointCount*16);
  const sample=(w,i,b)=>{ implementation.writePalette(buffer,w,i,b); return Array.from(buffer); };
  const start=sample(0,0,.68);
  assert.deepEqual(sample(1,1,.68),start);
  const pose=sample(.25,.5,1);
  assert.ok(start.some((v,i)=>Math.abs(v-pose[i])>.05),'independent clips have different transforms');
  sample(.77,.18,.1);
  assert.deepEqual(sample(-.75,4.5,1),pose);
});

test('the turn samples the source GLB once, including its last key and the entry blend',()=>{
  const implementation=rig(), out=new Float32Array(jointCount*16);
  assert.ok(implementation.clips.Giro,'bake the authored turn into both street LODs');
  for(const [progress,mix] of [[-.2,1],[0,1],[.037,.35],[.16,1],[.48,1],[.98,1],[1,1],[1.24,1]]){
    implementation.writePalette(out,.27,.58,0,0,progress,mix);
    const expected=sourceMatrices(progress,.58,mix,0,true);
    const error=out.reduce((max,v,k)=>Math.max(max,Math.abs(v-expected[k])),0);
    assert.ok(error<.000025,`turn ${progress}, blend ${mix}, error ${error}`);
  }
});

test('turn endpoints join rest in world space across the instance yaw handoff',()=>{
  const implementation=rig(), rest=new Float32Array(jointCount*16), pose=rest.slice();
  implementation.writePalette(rest,0,0,0);
  for(const progress of [0,1]){
    implementation.writePalette(pose,0,0,0,0,progress);
    for(let k=0;k<pose.length;k++){
      // Each column's X/Z rows are negated by the final world Y half-turn.
      const expected=progress && (k%4===0 || k%4===2)?-rest[k]:rest[k];
      assert.ok(Math.abs(pose[k]-expected)<.000025,`progress ${progress}, joint ${Math.floor(k/16)}, component ${k%16}`);
    }
  }
});
