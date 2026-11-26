const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const assert = require('node:assert/strict');
const test = require('node:test');
const context = { console };
vm.createContext(context);
for (const file of ['core','world','frontier-world','skin-rig','renderer','reactive-renderer','frontier-renderer']) {
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../src', file + '.js'), 'utf8'), context);
}
const D = context.DC;

function bake(world, cell) {
  const r = Object.create(D.FrontierRenderer.prototype);
  const meshes = {box:{},body:{},gable:{},smoke:{}};
  r.meshes = meshes;
  r.dynamic = {box:[]};
  let buffer;
  r.gl = {
    createBuffer: () => ({}), bindBuffer: (_,b) => {buffer=b;},
    bufferData: (_,data) => {buffer.data=Array.from(data);}
  };
  const chunk = {cells:[cell],key:'test',x:Math.floor(cell.ix/4)*336,z:Math.floor(cell.iz/4)*336};
  r.world = {home:world.home,activeChunks:[chunk]};
  const batch = r.buildSector(chunk);
  r.sectorGPU = new Map([[chunk.key,batch]]);
  const rows = name => {
    const packed = batch[name]?.buffer.data || [], result = [];
    for (let i=0; i<packed.length; i+=16) {
      const row = packed.slice(i,i+16);row[0]+=chunk.x;row[2]+=chunk.z;result.push(row);
    }
    return result;
  };
  return {r,rows,batch};
}

function shoppingCorner(world, ix, iz) {
  const c = world.cell(ix,iz), baked = bake(world,c);
  const panes = baked.rows('smoke').filter(row => row[7]===6);
  assert.equal(panes.length,2,'two street-facing glazing panels must enclose a real display recess');
  const front = panes.find(row => Math.abs(Math.sin(row[3]))<.01);
  const side = panes.find(row => Math.abs(Math.sin(row[3]))>.99);
  const b = c.buildings.find(b => Math.abs(Math.abs(b.z-front[2])-b.d/2)<.15 && Math.abs(Math.abs(b.x-side[0])-b.w/2)<.15);
  assert.ok(b);
  const sx = Math.sign(b.x-c.x), sz = Math.sign(b.z-c.z);
  assert.equal(Math.sign(Math.sin(side[3])),sx);assert.equal(Math.sign(Math.cos(front[3])),sz);
  return {...baked,c,b,sx,sz,front,side};
}

test('urban shop has glazing, a recessed display, street-facing signage and room under the awning',()=>{
  const w = new D.World(1337), a=shoppingCorner(w,0,0);
  const {b,sx,sz,front,side} = a;
  const x=front[0], z=front[2]-sz*.5;
  const solids = a.rows('box');
  assert.ok(!solids.some(v => Math.abs(x-v[0])<v[4]/2 && Math.abs(1.94-v[1])<v[5]/2 && Math.abs(z-v[2])<v[6]/2),'rear wall cannot fill the display bay');
  assert.ok(w.blocked(x,z,.30),'closed glazed frontage retains its authored collision');
  const fascia=solids.find(v=>[12,13,20].includes(v[7])&&Math.abs(v[2]-front[2])<.7);
  assert.ok(fascia);assert.equal(Math.sign(Math.cos(fascia[3])),sz);
  assert.ok(fascia[4] / fascia[5] <= 3, 'sign lettering stays close to the natural aspect of an atlas tile');
  const canopy=solids.filter(v=>Math.abs(v[0]-front[0])<1 && v[4]>=front[4] && (v[2]-front[2])*sz>.25);
  assert.ok(canopy.some(v=>v[6]>=1 && v[1]-v[5]/2>=2.55));
  assert.ok((side[0]-b.x)*sx>=b.w/2-.02);
  const repeat = new D.World(1337);
  assert.deepEqual(a.rows('box'),bake(repeat,repeat.cell(0,0)).rows('box'));
});

test('detail is bounded in the existing box batch and leaves the street at distance or eviction',()=>{
  const a=shoppingCorner(new D.World(1337),0,0),r=a.r, p=[a.side[0],2,a.front[2]];
  const draw=(eye,quality)=>{r.camera={eye};r.quality=quality;r.dynamic.box.length=0;r.renderCornerShopDetails();return r.dynamic.box.length/16;};
  const n=draw(p,'balanced');assert.ok(n>8 && n<=28);
  assert.equal(draw([p[0]+140,p[1],p[2]],'balanced'),0);
  assert.equal(draw([p[0],p[1]+140,p[2]],'balanced'),0);
  assert.equal(draw([p[0]+40,p[1],p[2]],'eco'),0);
  assert.equal(draw([p[0]+40,p[1],p[2]],'balanced'),n);
  r.sectorGPU.clear();assert.equal(draw(p,'balanced'),0);
});

test('farm, retro and park parcels keep their own buildings; all four street corners occur',()=>{
  const w=new D.World(1337);
  for (const cell of [w.cell(0,24),w.cell(-24,0),w.cell(-2,0)]) assert.equal(bake(w,cell).rows('smoke').length,0);
  const orientations=new Set();
  for(let i=-4;i<4;i++)for(let j=-4;j<4;j++){
    const c=w.cell(i,j), p=bake(w,c).rows('smoke').filter(v=>v[7]===6);
    assert.ok(p.length===0||p.length===2);
    if(p.length===2)orientations.add(p.map(v=>Math.round(Math.sin(v[3]))+','+Math.round(Math.cos(v[3]))).sort().join('/'));
  }
  assert.equal(orientations.size,4);
});
