'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
const TAU=2*Math.PI;
const ankle=(q,n,k)=>{const p=R.transform(q.matrices.subarray(R.ids['foot'+k]*16,R.ids['foot'+k]*16+16),R.bones[R.ids['foot'+k]][2]),c=Math.cos(n.yaw||0),s=Math.sin(n.yaw||0);return [(n.x||0)+p[0]*c+p[2]*s,q.rootY+p[1],(n.z||0)-p[0]*s+p[2]*c];};
const dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));

test('grounded root and leg reach stay continuous at both support boundaries',()=>{
 for(const speed of [1.4,1.98,3.3,6.2])for(const crouch of [0,1]){
  const n={moveSpeed:speed,sprintBlend:speed>5?1:0,crouch},g=D.NaturalMotion.gait(speed,n.sprintBlend,crouch);
  for(const edge of [g.duty,1]){
   const before=R.pose({...n,walk:(edge-1e-6)*TAU},1.25),after=R.pose({...n,walk:(edge+1e-6)*TAU},1.25);
   assert.ok(Math.abs(after.rootY-before.rootY)<.001,JSON.stringify({speed,crouch,edge,before:before.rootY,after:after.rootY}));
   for(const q of [before,after])for(const k of ['L','R'])assert.ok(q.feet[k].reachError<.002,`unreachable ${speed} ${edge} ${k}: ${q.feet[k].reachError}`);
  }
 }
});

test('releasing an offset planted foot does not teleport it to the nominal swing',()=>{
 const tracker=new D.MotionTracker(4),speed=1.4,duty=D.NaturalMotion.gait(speed).duty;
 const initial={x:4,z:36,yaw:0,moveSpeed:speed,walk:(duty-.04)*TAU};
 const first=tracker.update('p',initial,1),last=tracker.update('p',{...initial,z:36.12,walk:(duty-.001)*TAU},1.08);
 const next=tracker.update('p',{...initial,z:36.14,walk:(duty+.001)*TAU},1.096);
 assert.ok(last.motion.feet.L);assert.equal(next.motion.feet.L,null);
 const a=ankle(R.pose(last,1.08),last,'L'),b=ankle(R.pose(next,1.096),next,'L');
 assert.ok(dist(a,b)<.008,`release jump ${dist(a,b)}`);
 assert.ok(dist(ankle(R.pose(first,1),first,'L'),a)<.045,'stance should remain planted in X/Z');
});

function simulate(throttle,duration,hz){
 const s=scene('rifle'),tracker=new D.MotionTracker(4);Object.assign(s.player,{x:4,z:36,y:0,yaw:0,walk:0,moveSpeed:0,vx:0,vz:0,vy:0});
 s.peds.forEach(n=>n.hidden=true);s.dynamics.props=[];s.cars.forEach((car,i)=>Object.assign(car,{x:5000+i*6,z:5000,driver:null,parked:true,speed:0}));
 let previous,max=0,worst;
 for(let f=0;f<(duration+2)*hz;f++){
  const time=f/hz;if(f)for(let tick=0;tick<60/hz;tick++)s.step(1/60,{aim:true,throttle:time<duration?throttle:0,steer:0,fire:false});
  const n=tracker.update('player',s.player,s.time),m=D.Equipment.mount(s,n),a=D.WeaponHandling.actor(n,m,s.equipment),q=R.pose(a,s.time);
  if(previous!==undefined){const d=Math.abs(q.rootY-previous);if(d>max){max=d;worst={time,rootY:q.rootY,previous};}}
  previous=q.rootY;
 }
 return {max,worst};
}
test('native walking and stopping have no discontinuous support-driven root jumps',()=>{
 for(const throttle of [.35,.6,1])for(const duration of [.6,1,1.5,2]){
  const result=simulate(throttle,duration,60);
  assert.ok(result.max<.030,JSON.stringify({throttle,duration,...result}));
 }
});

test('swing residual decays monotonically and is retired at the next support',()=>{
 const tracker=new D.MotionTracker(4),speed=1.4,duty=D.NaturalMotion.gait(speed).duty;
 tracker.update('p',{x:0,z:0,yaw:0,moveSpeed:speed,walk:(duty-.01)*TAU},1);
 let previousWeight=1,last;
 for(let i=0;i<=40;i++){
  const phase=duty+.001+(1-duty-.002)*i/40,time=1.01+i/120;
  const n={x:0,z:.02+i*.01,yaw:0,moveSpeed:speed,walk:phase*TAU};
  const before=JSON.stringify(n),tracked=tracker.update('p',n,time),release=tracked.motion.swing.L;
  assert.ok(release);assert.ok(release.weight<=previousWeight&&release.weight>=0);
  const raw=R.groundTargets(tracked,time),q=R.pose(tracked,time);
  assert.ok(q.rootY<=raw.rootY+1e-9,'recovery must not violate reach ceiling');
  for(const k of ['L','R'])assert.ok(q.feet[k].reachError<.002,`${i}: ${k} ${q.feet[k].reachError}`);
  assert.equal(JSON.stringify(n),before);
  assert.deepEqual(tracker.update('p',n,time).motion,tracked.motion,'same timestamp must not advance the filter');
  previousWeight=release.weight;last=tracked;
 }
 assert.ok(previousWeight<.00001);
 const landed=tracker.update('p',{...last,walk:1.001*TAU},1.36);
 assert.equal(landed.motion.swing.L,null);assert.ok(landed.motion.feet.L);
});

test('teleport, airborne and seated poses do not carry obsolete release or recovery',()=>{
 for(const state of [{x:400,z:800},{seated:true,y:-.29},{y:.3,vy:1},{accessPhase:'pull'}]){
  const tracker=new D.MotionTracker(4),speed=1.4,duty=D.NaturalMotion.gait(speed).duty;
  tracker.update('p',{x:0,z:0,yaw:0,moveSpeed:speed,walk:(duty-.01)*TAU},1);
  tracker.update('p',{x:0,z:.03,yaw:0,moveSpeed:speed,walk:(duty+.01)*TAU},1.02);
  const n=tracker.update('p',{x:0,z:.04,yaw:0,moveSpeed:speed,walk:(duty+.03)*TAU,...state},1.04);
  assert.equal(n.motion.swing.L,null);assert.equal(n.motion.swing.R,null);
  assert.equal(n.motion.supportY,R.groundTargets(n,1.04).rootY);
 }
});

test('tracked support and swing correction commute with world translation and yaw',()=>{
 const a=new D.MotionTracker(4),b=new D.MotionTracker(4),yaw=1.1,c=Math.cos(yaw),sn=Math.sin(yaw),speed=1.4;
 let phase=0,z=0;
 for(let i=0;i<130;i++){
  phase+=D.NaturalMotion.frequency(speed)/60;z+=speed/60;
  const x=a.update('p',{x:0,z,yaw:0,walk:phase,moveSpeed:speed},i/60);
  const y=b.update('p',{x:7+z*sn,z:-12+z*c,yaw,walk:phase,moveSpeed:speed},i/60);
  const qa=R.pose(x,i/60),qb=R.pose(y,i/60);
  assert.ok(Math.abs(qa.rootY-qb.rootY)<2e-6);
  for(const k of ['L','R']){
   const p=ankle(qa,x,k),expected=[7+p[0]*c+p[2]*sn,p[1],-12-p[0]*sn+p[2]*c];
   assert.ok(dist(ankle(qb,y,k),expected)<2e-5,`${i} ${k}`);
  }
 }
});

test('ground support sampler stays pure and does not change skeletal lengths',()=>{
 const n={x:1,z:3,yaw:.6,moveSpeed:1.98,walk:6,health:82,motion:{speed:1.98,phase:6,supportY:-.12,swing:{L:{dx:-.1,dz:-.03,yaw:.6,weight:.3},R:null}}};
 const before=JSON.stringify(n),q=R.pose(n,2);
 R.groundTargets(n,2);assert.equal(JSON.stringify(n),before);
 for(const k of ['L','R'])for(const [u,v] of [['thigh','shin'],['shin','foot']]){
  const start=R.bones[R.ids[u+k]][2],end=R.bones[R.ids[v+k]][2];
  const x=R.transform(q.matrices.subarray(R.ids[u+k]*16,R.ids[u+k]*16+16),start),y=R.transform(q.matrices.subarray(R.ids[v+k]*16,R.ids[v+k]*16+16),end);
  assert.ok(Math.abs(dist(x,y)-dist(start,end))<1e-6,`${u}${k}`);
 }
});
