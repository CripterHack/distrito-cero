'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const test = require('node:test');
const vm = require('node:vm');

const stride = 49 * 16;
class StreetCast {
  renderPerson(n, isPlayer) { this.forwarded.push({n,isPlayer}); }
  chooseLOD(n, isPlayer, distance) { this.distance = distance; return distance < 16 ? 0 : 1; }
  add(list, ...record) { list.push(record); }
}

function scene() {
  const palettes = [];
  const ctx = vm.createContext({DC: {}, console});
  vm.runInContext(fs.readFileSync('src/core.js','utf8'),ctx);
  const D = ctx.DC;
  Object.assign(D,{Renderer:StreetCast,SkinRig:{paletteStride:stride},MarketPedAsset:{
    clips:{Marcha:{duration:.7654},Reposo:{duration:4},Carrera:{duration:.52},Giro:{duration:1.4}},
    writePalette(out,...phase) { out.fill(3);palettes.push(phase); }
  }});
  vm.runInContext(fs.readFileSync('src/market-ped-renderer.js','utf8'),ctx);
  const r=Object.create(D.Renderer.prototype);
  Object.assign(r,{dynamic:[],forwarded:[],castStats:{actors:0,lod:[0,0,0],triangles:0},
    castCursor:1,posePixels:new Float32Array(stride*4),currentSim:{},camera:{eye:[100,2,100]},
    quality:'balanced',currentTime:1,marketPedLoaded:true,marketPedMotion:new WeakMap(),
    meshes:{marketPed0:{count:15},marketPed1:{count:6}}});
  return {r,palettes};
}
const person=(extra={})=>({personId:'m:1',visualModel:'mercado-higgsfield',x:101,z:99,yaw:1.2,
  groundY:.145,phase:Math.PI/2,moveSpeed:0,speed:1.35,...extra});

test('a marked civilian uses its own authored mesh and skin palette row on the pavement',()=>{
  const {r,palettes}=scene(), n=Object.freeze(person());
  r.renderPerson(n);
  assert.equal(r.forwarded.length,0);
  assert.equal(r.dynamic.length,2);
  const [body,shadow]=r.dynamic;
  assert.equal(body[0],'marketPed0');
  assert.deepEqual(body.slice(1,7),[n.x,.145,n.z,1,1,1]);
  assert.equal(body[8],52);
  assert.equal(body[10],n.yaw);
  assert.equal(body[12],201);
  assert.equal(shadow[0],'smoke');
  assert.ok(Math.abs(shadow[2]-.148)<1e-9);
  assert.deepEqual(palettes[0],[.25,.25,0,0]);
  assert.ok(r.posePixels.subarray(0,stride).every(v=>v===0),'player row must remain untouched');
  assert.ok(r.posePixels.subarray(stride,2*stride).every(v=>v===3));
  assert.equal(r.castStats.actors,1);
  assert.equal(r.castStats.triangles,5);
  assert.equal(r.castCursor,2);
});

test('both LODs share one actor phase, pause freezes transitions and panic runs in the same clothing',()=>{
  const {r,palettes}=scene(), n=person();
  r.renderPerson(n);
  r.camera.eye=[104,1.5,130];
  n.phase+=Math.PI;n.moveSpeed=1.35;r.currentTime+=.08;r.renderPerson(n);
  assert.equal(r.dynamic[2][0],'marketPed1');
  assert.equal(palettes[1][0],.75);
  assert.ok(palettes[1][2]>0 && palettes[1][2]<1);
  r.castCursor=1;r.renderPerson(n);
  assert.deepEqual(palettes[1],palettes[2]);
  n.panic=2;n.moveSpeed=3.78;r.currentTime+=.7;r.castCursor=1;r.renderPerson(n);
  assert.ok(palettes.at(-1)[3]>.98);
  assert.equal(r.forwarded.length,0);
});

test('players, other civilians, seated actors and studio previews retain their own path',()=>{
  for(const options of [{player:true},{previewStudio:true},{marketPedLoaded:false},{heroFallback:true},
    {actor:{visualModel:undefined}},{actor:{seated:true}},{castCursor:128}]){
    const {r}=scene(),{actor,player,...flags}=options;Object.assign(r,flags);
    const n=person(actor);r.renderPerson(n,!!player);
    assert.equal(r.forwarded.length,1);assert.equal(r.forwarded[0].n,n);
    assert.equal(r.forwarded[0].isPlayer,!!player);assert.deepEqual(r.dynamic,[]);
  }
});

test('the same marked mesh reacts to a hit and a stationary stun, without mutating combat state',()=>{
  const {r,palettes}=scene();
  const n=Object.freeze(person({moveSpeed:1.35,combatStunUntil:4,combatHitUntil:2}));
  r.renderPerson(n);
  const [body]=r.dynamic;
  assert.equal(body[0],'marketPed0');assert.notEqual(body[11],0);
  assert.equal(palettes[0][2],0);
  assert.equal(n.moveSpeed,1.35);
});

test('the one-shot turn stays in its starting frame across LOD, panic and repeated draws',()=>{
  const {r,palettes}=scene(), n=person({moveSpeed:1.35});
  const startYaw=n.yaw;
  r.renderPerson(n);
  n.sidewalkRoute={turn:{startYaw,progress:0}};n.moveSpeed=0;
  r.renderPerson(n);
  assert.deepEqual(palettes[1].slice(0,4),palettes[0]);
  assert.equal(palettes[1][4],0);
  assert.equal(palettes[1][5],0,'first frame must retain the incoming walk');
  for(const progress of [.07,.5,1]) {
    r.currentTime+=.09;r.castCursor=1;
    n.yaw=startYaw+progress*Math.PI;n.sidewalkRoute.turn.progress=progress;
    if(progress>=.5){r.camera.eye=[104,1.5,130];n.panic=2;}
    r.renderPerson(n);
    const [body,shadow]=r.dynamic.slice(-2);
    assert.equal(body[0],progress>=.5?'marketPed1':'marketPed0');
    assert.equal(body[10],startYaw,'instance yaw must not repeat the root rotation');
    assert.equal(shadow[10],n.yaw);
    assert.equal(palettes.at(-1)[4],progress);
    if(progress===.07)assert.ok(palettes.at(-1)[5]>0 && palettes.at(-1)[5]<1);
    else assert.equal(palettes.at(-1)[5],1);
    r.castCursor=1;r.renderPerson(n);
    assert.deepEqual(palettes.at(-1),palettes.at(-2));
  }
  n.sidewalkRoute.turn=null;r.currentTime+=.01;r.castCursor=1;r.renderPerson(n);
  assert.equal(r.dynamic.at(-2)[10],startYaw+Math.PI);
  assert.equal(palettes.at(-1)[1],0,'resume the authored exit breathing phase');
  assert.equal(palettes.at(-1).length,4);
  r.currentTime+=.4;r.castCursor=1;r.renderPerson(n);
  assert.ok(Math.abs(palettes.at(-1)[1]-.1)<1e-12);
});
