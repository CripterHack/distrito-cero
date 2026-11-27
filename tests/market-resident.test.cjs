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
 let stopped=false;for(let i=0;i<1000;i++){tick(s,1);if(n.z===149&&n.sidewalkRoute.wait>0){stopped=true;break;}}
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

test('both ends play one grounded half-turn inside the existing wait, independent of frame rate',()=>{
 for(const hz of [30,60,120]){
  const {s,n}=scene();s.player.x=158;s.player.z=137;
  const route=n.sidewalkRoute,dt=1/hz;
  for(const [corner,direction] of [[149,-1],[130,1]]){
   let approach=0;
   while(route.towardEnd===(direction===-1) && approach++<hz*20)s.pedestrians(dt);
   assert.ok(Math.abs(n.z-corner)<1e-6);
   const initialYaw=n.yaw;
   let samples=0,previous=0,rotation=0,lastYaw=n.yaw,waiting=0;
   for(;waiting<hz*3;waiting++){
    s.pedestrians(dt);
    rotation+=D.wrap(n.yaw-lastYaw);lastYaw=n.yaw;
    if(route.turn){
     assert.equal(n.z,corner);assert.ok(n.moveSpeed<1e-8);
     assert.ok(route.turn.progress>=previous && route.turn.progress<=1);
     assert.ok(Math.abs(D.wrap(route.turn.startYaw-initialYaw))<1e-6);
     previous=route.turn.progress;samples++;
    }
    if(Math.abs(n.z-corner)>1e-7)break;
   }
   assert.ok(Math.abs(samples/hz-1.4)<2/hz,'one full turn during the wait');
   assert.ok(Math.abs(waiting/hz-2.4)<2/hz);
   assert.ok(Math.abs(rotation-Math.PI)<1e-5);
   assert.equal(Math.sign(n.z-corner),direction);assert.equal(n.x,route.x);
  }
 }
});

test('a horn during the turn preserves the planted actor and accelerates its departure',()=>{
 const {s,n}=scene(),route=n.sidewalkRoute;
 s.player.x=158;s.player.z=144;
 for(let i=0;i<1200 && !(route.turn?.progress>.25);i++)s.pedestrians(1/60);
 assert.ok(route.turn);
 const c=s.cars[0],phase=route.turn.progress,corner=n.z;
 Object.assign(c,{x:n.x+2,z:n.z-1,speed:0});Object.assign(s.player,{car:0,x:c.x,z:c.z});
 s.interact('horn');
 s.pedestrians(1/60);
 assert.ok(route.turn.progress>phase);
 assert.equal(n.z,corner);
 let count=0;
 while(n.z===corner && count++<65)s.pedestrians(1/60);
 assert.ok(n.z<corner && count<60);
 s.pedestrians(1/60);assert.ok(Math.abs(n.moveSpeed-3.78)<1e-5);
 assert.equal(n.visualModel,'mercado-higgsfield');
});

test('a horn ahead reverses the walking resident once and streaming preserves the turn',()=>{
 const {s,n}=scene(),route=n.sidewalkRoute;
 Object.assign(s.player,{x:158,z:137});tick(s,420);
 const z=n.z,initialYaw=n.yaw,c=s.cars[0];
 assert.ok(z>133 && z<145);
 Object.assign(c,{x:n.x+2,z:z+1,speed:0});Object.assign(s.player,{car:0,x:c.x,z:c.z});
 s.interact('horn');tick(s,12);
 assert.equal(route.turn.startYaw,initialYaw);assert.equal(n.z,z);
 const progress=route.turn.progress;
 Object.assign(s.player,{car:null,x:1000,z:1000});tick(s,90);
 assert.equal(route.turn.progress,progress);
 Object.assign(s.player,{x:158,z:137});tick(s,60);
 assert.equal(route.turn,null);assert.ok(n.z<z);assert.ok(Math.cos(n.yaw)<-.999);
 assert.ok(Math.abs(n.moveSpeed-3.78)<1e-6);
});

test('each approach joins a fitted stopping step and reaches the endpoint at clip completion',()=>{
 const reach=.1653272101033296,duration=4*reach/1.35,feet=new Set();
 for(const hz of [30,60,120]){
  const {s,n}=scene(),r=n.sidewalkRoute,dt=1/hz;
  Object.assign(s.player,{x:158,z:137});
  for(const end of [149,130]){
   const toward=r.towardEnd,dir=toward?1:-1;
   let active=0,last=0,priorD,priorPhase,entry;
   for(let i=0;i<20*hz && r.towardEnd===toward;i++){
    priorD=Math.abs(end-n.z);priorPhase=n.phase/(Math.PI*2);
    s.pedestrians(dt);
    if(!r.brake)continue;
    if(!active){
     entry=r.brake.clip==='FrenadaL'?.15:.65;
     const joined=priorPhase+(priorD-reach)*D.NaturalMotion.distanceRate(n.speed)/(Math.PI*2);
     assert.ok(Math.abs(joined-entry-Math.round(joined-entry))<1e-5,'last walking stride reaches the first authored key');
    }
    active++;const {clip,progress,startX,startZ}=r.brake;
    assert.ok(['FrenadaL','FrenadaR'].includes(clip));feet.add(clip);
    assert.ok(progress>=last && progress<=1);last=progress;
    assert.equal(startX,n.x);assert.ok(Math.abs(startZ-(end-dir*reach))<1e-9);
    assert.ok(Math.abs(n.z-(end-dir*reach*(1-progress)**4))<1e-8);
   }
   assert.ok(Math.abs(active*dt-duration)<2*dt,'one stopping clip at either rate');
   assert.equal(n.z,end);assert.equal(r.wait,2.4);assert.ok(!r.brake);
   tick(s,2);
  }
 }
 assert.deepEqual([...feet].sort(),['FrenadaL','FrenadaR']);
});

test('the horn accelerates a braking resident through the same planted step and turn',()=>{
 const {s,n}=scene(),r=n.sidewalkRoute;Object.assign(s.player,{x:158,z:144});
 for(let i=0;i<1200 && !(r.brake?.progress>.18);i++)s.pedestrians(1/60);
 assert.ok(r.brake);const {progress,clip,startZ}=r.brake;
 const c=s.cars[0];Object.assign(c,{x:n.x+2,z:n.z+1,speed:0});Object.assign(s.player,{car:0,x:c.x,z:c.z});
 s.interact('horn');s.pedestrians(1/60);
 assert.equal(r.brake.clip,clip);assert.equal(r.brake.startZ,startZ);
 assert.ok(r.brake.progress>progress+1/60/.49);assert.ok(n.z<=149);
 let ticks=0;while(r.brake&&ticks++<24)s.pedestrians(1/60);
 assert.ok(ticks<24);assert.equal(n.z,149);assert.equal(r.wait,0);assert.equal(r.towardEnd,false);
 s.pedestrians(1/60);assert.ok(r.turn);
});

test('a fading panic prepares a walk stop while there is room for the fitted stride',()=>{
 for(const [hz,hornZ,expectBrake] of [[30,135,true],[60,136.7,true],[120,135,true],[60,137.5,false]]){
  const {s,n}=scene(),r=n.sidewalkRoute,dt=1/hz,c=s.cars[0];
  Object.assign(s.player,{x:158,z:139});
  while(n.z<hornZ)s.pedestrians(dt);
  Object.assign(c,{x:n.x+2,z:n.z-1,speed:0});Object.assign(s.player,{car:0,x:c.x,z:c.z});
  s.interact('horn');s.player.car=null;
  let stopped=false,decayed=false;
  for(let i=0;i<12*hz && r.towardEnd;i++){
   const z=n.z,phase=n.phase;
   s.pedestrians(dt);const moved=n.z-z;
   if(!n.panic)decayed=true;
   if(r.brake)stopped=true;
   if(moved>1e-5 && !r.brake && r.towardEnd && n.moveSpeed>1){
    const rate=D.NaturalMotion.distanceRate(n.moveSpeed,n.panic?.5:0);
    assert.ok(Math.abs((n.phase-phase)/moved/rate-1)<.040001,'cadence stays continuous and within four percent');
   }
  }
  assert.equal(n.z,149);assert.ok(decayed);
  assert.equal(stopped,expectBrake,'a panic that ends inside the braking distance must not rewind to its first key');
 }
});
