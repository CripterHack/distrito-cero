const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const ctx = vm.createContext({});
for (const name of ['core','world','frontier-world']) {
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../src',name+'.js'),'utf8'),ctx);
}
const D = vm.runInContext('DC',ctx);
test('workshop replaces one campaign parcel and leaves its garage marker accessible', () => {
  for (const seed of [1337, 0, 517]) {
    const w = new D.World(seed), sites = w.home.buildings.filter(b => b.landmark === 'taller');
    assert.equal(sites.length,1);
    const b = sites[0], cell = w.cell(2,1);
    assert.equal(cell.buildings.filter(b=>b.landmark==='taller').length,1);
    assert.equal(w.home.buildings.length,392);
    assert.equal(b.h,6.5);
    assert.ok(w.blocked(b.x,b.z,.3));
    assert.ok(!w.blocked(168,96,.6));
    assert.ok(b.x-b.w/2>178 && b.z-b.d/2>94);
  }
});
test('shelters have a solid bench and open boarding pavement on the road side', () => {
  const w = new D.World(1337);
  assert.equal(w.shelters.length,2);
  for(const s of w.shelters) {
    assert.ok(w.blocked(s.x-.43,s.z,.22));
    assert.ok(!w.blocked(s.x+.68,s.z,.22));
    assert.ok(!w.blocked(s.x-.43,s.z+1.8,.22));
    assert.ok(w.move(s.x+1.1,s.z,-1.8,0,.22).hit);
  }
});
test('each native mesh has two indexed textured LODs on a shared metre-scale floor', () => {
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../src/mercado-models.js'),'utf8'),ctx);
  assert.ok(D.MercadoModels.atlas.startsWith('data:image/webp;base64,'));
  for(const [id,height] of [['taller',6.5],['marquesina',2.5]]) {
    const {levels,size} = D.MercadoModels[id];
    assert.ok(Math.abs(size[1]-height)<.001);
    assert.ok(levels[0].triangles>levels[1].triangles*2);
    for(const l of levels) {
      const points=Buffer.from(l.points,'base64'), indices=Buffer.from(l.indices,'base64');
      assert.equal(points.length%14,0);
      assert.equal(indices.length,l.triangles*6);
      const count=points.length/14;
      for(let i=0;i<indices.length;i+=2)assert.ok(indices.readUInt16LE(i)<count);
      const y=Array.from({length:count},(_,i)=>points.readInt16LE(i*14+2));
      assert.ok(Math.abs(Math.min(...y))<35 && Math.abs(Math.max(...y)-height*1000)<70);
    }
  }
});

test('the shelter diffuser and its dimmable downlight share one mounting point', () => {
  const testContext = vm.createContext({DC: {SkinRig: {bones: Array(49)}}});
  for (const name of ['core','world','frontier-world','renderer','mercado-renderer']) {
    vm.runInContext(fs.readFileSync(path.join(__dirname,'../src',name+'.js'),'utf8'),testContext);
    if(name==='renderer')testContext.DC.Renderer.prototype.renderReactive=()=>{};
  }
  const dc=testContext.DC, r=Object.create(dc.Renderer.prototype);
  r.world=new dc.World(1337);r.camera={eye:[161.5,1.62,127]};r.quality='balanced';r.dynamic=[];
  const baseStreetLight={x:167,y:7.6,z:108,warm:true};
  r.world.lights=[baseStreetLight,{x:162,y:7.6,z:90,warm:true}];
  const sim={dynamics:{lightActive:index=>index===0}};
  r.add=(list,...args)=>list.push(args);
  r.daylight=1;
  assert.deepEqual(Array.from(r.sceneLights(sim)),[baseStreetLight]);
  r.daylight=0;
  const lit=r.sceneLights(sim),stop=r.world.shelters[1],light=lit.find(l=>l.x>stop.x && l.downlight);
  assert.equal(lit.length,3);
  assert.equal(light.downlight,1);
  assert.ok(light.x < stop.x+.86 && Math.abs(light.z-stop.z)<1.45);
  assert.ok(light.y>2.48 && light.y<2.60);
  r.renderReactive(sim);
  const diffuser=r.dynamic.find(row=>row[0]==='box' && Math.abs(row[1]-light.x)<.001 && Math.abs(row[3]-light.z)<.001);
  assert.ok(diffuser && Math.abs(diffuser[2]-light.y)<.04 && diffuser[9]>0);
  r.daylight=.4;
  const partial=r.sceneLights(sim).find(l=>l.downlight);
  assert.ok(partial.downlight>0 && partial.downlight<light.downlight);
  r.previewStudio=true;
  assert.deepEqual(Array.from(r.sceneLights(sim)),[baseStreetLight]);
});
