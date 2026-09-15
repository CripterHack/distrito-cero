'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const ctx={console,Math,JSON,Float32Array};vm.createContext(ctx);
for(const f of ['core.js','world.js','police.js','simulation.js','dynamics.js','interactions.js']){
 const p=__dirname+'/../src/'+f;if(fs.existsSync(p))vm.runInContext(fs.readFileSync(p,'utf8'),ctx);
}
const D=ctx.DC;
// Controlled fixture: real city geometry and production cars, no renderer or mocks.
function scene(){
 const s=new D.Simulation(new D.World(1337));s.free=true;s.peds=[];
 const cop=s.cars.find(c=>c.police);s.cars=[s.cars[0],cop];
 Object.assign(s.cars[0],{x:4,z:0,yaw:0,speed:0,parked:false});
 Object.assign(cop,{x:4,z:4,yaw:Math.PI,speed:0,parked:false});
 Object.assign(s.player,{x:4,z:0,yaw:0,car:0});return s;
}
function ticks(s,seconds,input={},hz=60){for(let i=0;i<Math.round(seconds*hz);i++)s.step(1/hz,input);}

test('parallel vehicles moving together do not lose speed from a side scrape',()=>{
 const s=scene(),a=s.actor(),b=s.cars[1];Object.assign(a,{speed:12});Object.assign(b,{x:5.98,z:0,yaw:0,speed:12});
 s.vehicleContacts(1/60);assert.ok(Math.abs(a.speed-12)<.01,`speed was ${a.speed}`);
});
test('side-by-side vehicles 2.5 m apart do not collide with an oversized circular body',()=>{
 const s=scene(),a=s.actor(),b=s.cars[1];Object.assign(a,{speed:10});Object.assign(b,{x:6.5,z:0,yaw:0,speed:10});
 s.vehicleContacts(1/60);assert.equal(a.x,4);assert.equal(a.speed,10);
});
test('perfectly overlapping cars are separated instead of skipped',()=>{
 const s=scene();Object.assign(s.cars[1],{x:4,z:0,yaw:0});s.vehicleContacts(1/60);
 assert.ok(D.distance(s.cars[0],s.cars[1])>1.5);
});
test('zero-delta contact solving does not change position or speed',()=>{
 const s=scene();s.cars[1].z=2.8;s.actor().speed=12;const before=JSON.stringify(s.cars.map(c=>[c.x,c.z,c.speed]));
 s.vehicleContacts(0);assert.equal(JSON.stringify(s.cars.map(c=>[c.x,c.z,c.speed])),before);
});
test('a rear-end hit initiated by police does not blame the stationary player',()=>{
 const s=scene();Object.assign(s.cars[1],{z:-2.9,yaw:0,speed:24});s.addHeat(20);s.vehicleContacts(1/60);
 assert.equal(s.heat,20,'Police-caused contact must not add wanted stars');
});
test('a deliberate high-speed ram by the player still has consequences',()=>{
 const s=scene();s.actor().speed=20;s.cars[1].z=3.0;s.vehicleContacts(1/60);
 assert.ok(s.heat>0);assert.ok(s.actor().health<100);
});
test('repeated tangential contact does not produce frame-dependent velocity drain',()=>{
 for(const hz of [30,60,120]){
  const s=scene();s.actor().speed=15;s.cars[1].speed=15;s.cars[1].yaw=0;
  for(let i=0;i<hz;i++){s.actor().x=4;s.cars[1].x=5.98;s.cars[1].z=s.actor().z;s.vehicleContacts(1/hz);}
  assert.ok(s.actor().speed>14.9,`${hz}Hz: ${s.actor().speed}`);
 }
});
test('reverse and steering let the player pull away after front police contact',()=>{
 const s=scene();s.cars[1].z=3;s.addHeat(20);ticks(s,2.4,{throttle:-1,steer:.45});
 assert.equal(s.player.car,0,'No unavoidable arrest');assert.ok(s.actor().speed<-4,`reverse speed ${s.actor().speed}`);assert.ok(s.bust<.3);
});
test('a rear police contact does not prevent forward acceleration',()=>{
 const s=scene();Object.assign(s.cars[1],{z:-3,yaw:0,speed:9});s.addHeat(20);ticks(s,2.5,{throttle:1});
 assert.equal(s.player.car,0);assert.ok(s.actor().speed>10);assert.ok(s.bust<.2);
});
test('running on foot is not mistaken for being motionless by arrest logic',()=>{
 const s=scene();Object.assign(s.player,{car:null,actualSpeed:6.2,moveSpeed:6.2});s.cars[1].z=2;s.addHeat(40);s.bust=.3;
 s.police(.5);assert.ok(s.bust<.3,`capture increased to ${s.bust}`);
});
test('walking against a wall uses actual displacement rather than intended speed',()=>{
 const s=scene();s.player.car=null;s.world.buildings=[{x:4,z:3,w:10,d:2}];ticks(s,2,{throttle:1,lookYaw:0});
 assert.ok(s.player.actualSpeed<.1);assert.ok(s.player.moveSpeed<.1);assert.equal(s.player.moving,true);
});
test('police cannot arrest through an opaque wall',()=>{
 const s=scene();s.player.car=null;s.player.x=2;s.cars[1].x=6;s.cars[1].z=0;s.world.buildings=[{x:4,z:0,w:1,d:15}];s.addHeat(40);
 for(let i=0;i<360;i++)s.police(1/60);
 assert.equal(s.cash,850);assert.equal(s.bust,0);assert.equal(s.seen,false);
});
test('remaining stationary and visible can still lead to arrest',()=>{
 const s=scene();s.addHeat(40);s.story=3;
 for(let i=0;i<450;i++)s.police(1/60);
 assert.equal(s.wanted,0);assert.equal(s.cash,550);assert.equal(s.story,3);
});
test('capture progress recedes when movement resumes',()=>{
 const s=scene();s.addHeat(20);s.bust=.8;s.actor().speed=12;s.player.actualSpeed=12;
 s.police(1);assert.ok(s.bust<.2);
});
test('pursuit records a last-known location instead of tracking through walls',()=>{
 const s=scene();s.addHeat(20);s.police(.1);
 assert.ok(s.policeState?.lastSeen);const previous={...s.policeState.lastSeen};
 s.world.buildings=[{x:25,z:0,w:4,d:100}];s.player.x=40;s.cars[0].x=40;s.police(.1);
 assert.equal(s.seen,false);assert.equal(s.policeState.lastSeen.x,previous.x);assert.equal(s.policeState.lastSeen.z,previous.z);
});
test('stationary pursuit brakes short of the player rather than driving into the centre',()=>{
 const s=scene();s.cars[1].z=-18;s.cars[1].yaw=0;s.addHeat(20);
 for(let i=0;i<240;i++){s.time+=1/60;s.sensePolice?.();s.traffic(s.cars[1],1/60);}
 assert.ok(D.distance(s.actor(),s.cars[1])>4.5);assert.ok(Math.abs(s.cars[1].speed)<2);
});
test('escape progress and status are available to the HUD',()=>{
 const s=scene();s.addHeat(20);assert.equal(typeof s.getPoliceStatus,'function');
 s.police(.1);assert.equal(s.getPoliceStatus().phase,'pursuit');
 s.cars[1].x=420;s.cars[1].z=420;s.police(7);
 assert.equal(s.getPoliceStatus().phase,'search');assert.ok(s.getPoliceStatus().searchProgress>0);
});
test('surrender requires a nearby visible officer and a stopped actor',()=>{
 const s=scene();s.addHeat(20);s.police(.1);assert.equal(typeof s.canSurrender,'function');assert.equal(s.canSurrender(),true);
 s.actor().speed=10;assert.equal(s.canSurrender(),false);s.actor().speed=0;s.cars[1].x=400;assert.equal(s.canSurrender(),false);
});
test('holding surrender resolves the encounter with a reduced cost and keeps story progress',()=>{
 const s=scene();s.addHeat(40);s.story=3;for(let i=0;i<121;i++)s.police(1/60,{surrender:true});
 assert.equal(s.wanted,0);assert.equal(s.cash,700);assert.equal(s.story,3);assert.equal(s.player.car,null);
});
test('releasing surrender cancels the countdown without deducting cash',()=>{
 const s=scene();s.addHeat(20);s.police(.6,{surrender:true});s.police(.1,{surrender:false});
 assert.equal(s.policeState?.surrender,0);assert.equal(s.cash,850);assert.ok(s.wanted>0);
});
test('movement input cancels surrender even while the player is blocked',()=>{
 const s=scene();s.addHeat(20);s.police(.6,{surrender:true});s.police(.1,{surrender:true,throttle:1});
 assert.equal(s.policeState?.surrender,0);assert.equal(s.cash,850);
});
test('respawn clears detection, recovery and surrender transient state',()=>{
 const s=scene();s.addHeat(20);s.police(.6,{surrender:true});s.respawn('arrest');
 assert.equal(s.seen,false);assert.equal(s.getPoliceStatus?.().phase,'patrol');assert.equal(s.policeState?.surrender,0);
});
test('old v1 save format remains compatible with v0.3 and resets capture',()=>{
 const s=scene();s.story=3;s.cash=1925;s.addHeat(40);const data=s.serialize();const restored=scene();assert.equal(restored.restore(data),true);
 assert.equal(restored.story,3);assert.equal(restored.cash,1925);assert.equal(restored.player.car,0);assert.equal(restored.bust,0);assert.equal(restored.policeState?.surrender,0);
});
test('exiting a car does not place the player inside an adjacent patrol',()=>{
 const s=scene();const c=s.cars[1];Object.assign(c,{x:1.8,z:0,yaw:0,speed:0});s.interact('car');
 assert.equal(s.player.car,null);assert.ok(D.distance(s.player,c)>1.4,'Exit must choose an unobstructed door');
});

test('search routing is identical for different unseen player locations',()=>{
 const routes=[];
 for(const x of [168,336]){
  const s=scene();s.addHeat(40);s.police(.1);s.world.buildings=[{x:30,z:0,w:4,d:840}];
  s.player.x=x;s.actor().x=x;s.police(.1);s.cars[1].navTime=-1;s.traffic(s.cars[1],1/60);
  routes.push(JSON.stringify(s.cars[1].route));
 }
 assert.equal(routes[0],routes[1]);
});
test('two patrols on opposing bumpers leave a controllable escape window',()=>{
 const s=scene();s.cars[1].z=3.4;
 const rear=s.makeCar(4,-3.4,0,true,false,41);rear.speed=0;s.cars.push(rear);s.addHeat(60);
 ticks(s,3,{throttle:-1,steer:.65});
 assert.equal(s.player.car,0);assert.ok(Math.abs(s.actor().speed)>4);assert.ok(s.bust<.35);
});
test('car-car physics also separates two police vehicles instead of stacking them',()=>{
 const s=scene();const second=s.makeCar(4,4,0,true,false,41);s.cars.push(second);s.actor().z=-40;s.player.z=-40;
 s.cars[1].yaw=0;s.vehicleContacts(1/60);
 assert.ok(D.distance(s.cars[1],second)>1.5);
});
test('reversing from initial police contact remains possible at different simulation steps',()=>{
 for(const hz of [30,60,120]){
  const s=scene();s.cars[1].z=3;s.addHeat(20);ticks(s,2.4,{throttle:-1,steer:.45},hz);
  assert.equal(s.player.car,0);assert.ok(s.actor().speed<-4,`${hz}Hz: ${s.actor().speed}`);
 }
});
test('surrender cannot produce negative cash',()=>{
 const s=scene();s.cash=40;s.addHeat(20);s.police(2,{surrender:true});assert.equal(s.cash,0);assert.equal(s.wanted,0);
});
test('surrender cannot happen through walls',()=>{
 const s=scene();s.addHeat(40);s.cars[1].x=8;s.cars[1].z=0;s.world.buildings=[{x:6,z:0,w:1,d:20}];
 assert.equal(s.canSurrender(),false);s.police(2,{surrender:true});assert.equal(s.cash,850);assert.ok(s.wanted>0);
});
test('rotated vehicle footprint detects a real head-on bumper overlap',()=>{
 const a={id:1,x:0,z:0,yaw:Math.PI/4,speed:10},b={id:2,x:2.8,z:2.8,yaw:Math.PI/4,speed:0};
 const hit=D.vehicleOverlap(a,b);assert.ok(hit);assert.ok(hit.closing>9);
});
test('separating car velocities are not treated as a second impact',()=>{
 const s=scene();Object.assign(s.actor(),{z:0,speed:-10});Object.assign(s.cars[1],{z:4,yaw:0,speed:10});
 s.vehicleContacts(1/60);assert.equal(s.actor().speed,-10);assert.equal(s.actor().health,100);assert.equal(s.heat,0);
});
