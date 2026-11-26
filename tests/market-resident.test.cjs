'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const ctx=vm.createContext({});
for(const name of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','character-motion']){
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../src',name+'.js'),'utf8'),ctx);
}
const D=ctx.DC;
function scene(seed=1337){
 const s=new D.Simulation(new D.FrontierWorld(seed));
 const cast=s.peds.filter(n=>n.visualModel==='mercado-higgsfield');
 assert.equal(cast.length,1);
 return {s,n:cast[0]};
}
function tick(s,count){for(let i=0;i<count;i++)s.pedestrians(1/60);}
test('one existing pedestrian lives on the Mercado pavement across streaming and legacy restoration',()=>{
 for(const seed of [1337,777]){
  const {s,n}=scene(seed),{personId}=n;
  assert.equal(s.peds.length,72);
  assert.ok(/^ped:\d+$/.test(personId));
  assert.equal(n.moveSpeed,0);
  assert.equal(n.x,155.5);assert.equal(n.z,130);
  assert.equal(n.groundY,.145);assert.ok(!s.world.blocked(n.x,n.z,.35));
  assert.ok(s.travel(2016,0));s.recyclePopulation();tick(s,240);
  assert.equal(n.z,130);assert.equal(n.x,155.5);
  const data=s.serialize();assert.ok(!JSON.stringify(data).includes('mercado-higgsfield'));
  const other=scene(seed===777?1337:777).s;
  assert.ok(other.restore(data));assert.equal(other.peds.find(p=>p.visualModel==='mercado-higgsfield').personId,personId);
  assert.ok(s.travel(168,96));assert.equal(s.peds.find(p=>p.visualModel==='mercado-higgsfield'),n);
 }
});
test('the resident waits, walks to the corner, turns in place, and walks back on the same sidewalk',()=>{
 const {s,n}=scene();s.player.x=166;s.player.z=131;
 const phase=n.phase;tick(s,120);assert.equal(n.phase,phase);assert.equal(n.moveSpeed,0);
 tick(s,60);assert.ok(Math.abs(n.moveSpeed-1.35)<1e-6);assert.ok(n.z>130.5&&n.z<131.2);
 let stopped=false;for(let i=0;i<1000;i++){tick(s,1);if(n.z>148.99&&n.moveSpeed<.0001){stopped=true;break;}}
 assert.ok(stopped);const corner=n.z;tick(s,100);assert.equal(n.z,corner);
 tick(s,100);assert.ok(n.z<corner-.4);assert.ok(Math.cos(n.yaw)<-.95);assert.equal(n.x,155.5);
});
test('the horn makes the waiting resident run and the calm walk resumes',()=>{
 const {s,n}=scene();const c=s.cars[0];
 Object.assign(c,{x:n.x+2,z:n.z-1,speed:0});
 Object.assign(s.player,{car:0,x:c.x,z:c.z});
 s.interact('horn');tick(s,4);
 assert.ok(n.panic>0);assert.ok(Math.abs(n.moveSpeed-3.78)<1e-6);
 assert.equal(n.visualModel,'mercado-higgsfield');
 s.player.car=null;tick(s,210);
 assert.equal(n.panic,0);assert.ok(Math.abs(n.moveSpeed-1.35)<1e-6);
});
