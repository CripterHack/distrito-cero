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

test('village, farm, suburb, future, retro and park parcels keep their own architecture; all four street corners occur',()=>{
  const w=new D.World(1337);
  const controls = [[0,24,'village'],[12,12,'farmland'],[5,5,'suburb'],[24,0,'future'],[-24,0,'retro']];
  for (const [ix,iz,type] of controls) {
    const cell = w.cell(ix,iz);
    assert.equal(cell.type,type);
    assert.ok(cell.buildings.length);
    assert.equal(bake(w,cell).rows('smoke').length,0);
  }
  const park = w.cell(-2,0);
  assert.ok(park.park);assert.equal(bake(w,park).rows('smoke').length,0);
  const orientations=new Set();
  for(let i=-4;i<4;i++)for(let j=-4;j<4;j++){
    const c=w.cell(i,j), p=bake(w,c).rows('smoke').filter(v=>v[7]===6);
    assert.ok(p.length===0||p.length===2);
    if(p.length===2)orientations.add(p.map(v=>Math.round(Math.sin(v[3]))+','+Math.round(Math.cos(v[3]))).sort().join('/'));
  }
  assert.equal(orientations.size,4);
});

test('the front display strip addresses only the shelves, rear wall and stock in each corner orientation',()=>{
  const world=new D.World(1337),orientations=new Set();
  for(let ix=-4;ix<4;ix++)for(let iz=-4;iz<4;iz++){
    const cell=world.cell(ix,iz),{r,rows}=bake(world,cell);
    const glass=rows('smoke').filter(v=>v[7]===6);
    if(glass.length!==2)continue;
    const key=glass.map(v=>Math.round(Math.sin(v[3]))+','+Math.round(Math.cos(v[3]))).join('/');
    if(orientations.has(key))continue;
    orientations.add(key);
    r.camera={eye:[glass[0][0],1.7,glass[0][2]]};r.quality='balanced';
    r.renderCornerShopDetails();
    const near=Array.from({length:r.dynamic.box.length/16},(_,i)=>r.dynamic.box.slice(i*16,i*16+16));
    const strip=near.find(v=>v[11]>.5 && v[7]===0);
    assert.ok(strip);
    const fixed=rows('box').filter(v=>v[7]===53),stock=near.filter(v=>v[7]===53);
    assert.equal(fixed.length,5,'four shelves and the rear wall receive display light');
    assert.equal(stock.length,18,'all eighteen stock items and trays receive display light');
    assert.equal(strip[4],D.ShopDisplay.stripLength);
    for(const v of [...fixed,...stock]){
      assert.ok(Math.abs(v[0]+v[14]-strip[0])<.0001);
      assert.ok(Math.abs(v[2]+v[15]-strip[2])<.0001);
      assert.ok(Math.abs(v[11]-strip[1])<.0001);
    }
  }
  assert.equal(orientations.size,4);
});
