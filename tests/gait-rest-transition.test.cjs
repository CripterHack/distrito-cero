'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');

test('nearly stationary feet fade their stride amplitude instead of retaining a full step',()=>{
 for(const speed of [.02,.03,.04,.06,.08])for(let i=0;i<64;i++)for(const side of ['L','R']){
  const foot=D.NaturalMotion.foot({moveSpeed:speed,walk:i*Math.PI/32},side);
  assert.ok(Math.abs(foot.z)<.08,JSON.stringify({speed,phase:i,side,z:foot.z}));
 }
});

test('almost-rest gait phases cannot force the standing root below its reachable support',()=>{
 for(const speed of [.02,.03,.04,.06,.08])for(let i=0;i<64;i++){
  const pose=R.pose({moveSpeed:speed,walk:i*Math.PI/32},1.25);
  assert.ok(pose.rootY>-.12,JSON.stringify({speed,phase:i,rootY:pose.rootY}));
 }
});

test('native low-speed stop has no transient half-metre root drop',()=>{
 const s=scene('rifle'),tracker=new D.MotionTracker(4);
 Object.assign(s.player,{x:4,z:36,y:0,yaw:0,walk:0,moveSpeed:0,vx:0,vz:0,vy:0});
 s.peds.forEach(n=>n.hidden=true);s.dynamics.props=[];
 s.cars.forEach((car,i)=>Object.assign(car,{x:5000+i*6,z:5000,driver:null,parked:true,speed:0}));
 D.WeaponHandling.beginEquip(s);s.equipment.aimWeight=0;
 let previous=null;
 for(let frame=0;frame<120;frame++){
  if(frame)for(let tick=(frame-1)*4+1;tick<=frame*4;tick++){
   const t=tick/60;s.step(1/60,{aim:t<6.5,crouch:t>=4.5&&t<5.15,throttle:t>=5.35&&t<6.15?.35:0,steer:0,fire:false});
  }
  const tracked=tracker.update('player',s.player,s.time,false),mount=D.Equipment.mount(s,tracked);
  const actor=D.WeaponHandling.actor(tracked,mount,s.equipment),pose=R.pose(actor,s.time);
  if(frame>=93){
   assert.ok(pose.rootY>-.15,`frame ${frame}: rootY ${pose.rootY}`);
   if(previous!==null)assert.ok(Math.abs(pose.rootY-previous)<.05,`frame ${frame}: step ${pose.rootY-previous}`);
  }
  previous=pose.rootY;
 }
});

test('full-envelope walking and running keep their authored foot trajectories',()=>{
 for(const speed of [.65,1.4,3.3,6.2])for(const crouch of [0,1])for(let i=0;i<64;i++)for(const side of ['L','R']){
  const n={moveSpeed:speed,walk:i*Math.PI/32,crouch,sprintBlend:speed>5?1:0};
  const g=D.NaturalMotion.gait(speed,n.sprintBlend,crouch),f=D.NaturalMotion.foot(n,side);
  assert.equal(g.weight,1);
  const phase=((n.walk/(2*Math.PI)+(side==='R'?.5:0))%1+1)%1;
  const contact=phase<g.duty,t=contact?phase/g.duty:(phase-g.duty)/(1-g.duty);
  const expected=contact?g.span*(.5-t):g.span*(-.5+t*t*(3-2*t));
  assert.equal(f.z,expected);
 }
});

test('low-speed foot sampling is bounded, pure and independent of actor translation',()=>{
 for(const speed of [0,.01,.02,.03,.05,.1,.2,.4,.65])for(let i=0;i<32;i++){
  const n={x:400,z:-300,yaw:.8,moveSpeed:speed,walk:i*Math.PI/16,health:85};
  const before=JSON.stringify(n),a=D.NaturalMotion.foot(n,'L'),b=D.NaturalMotion.foot({...n,x:0,z:0},'L');
  assert.deepEqual(a,b);assert.equal(JSON.stringify(n),before);
  assert.ok([a.x,a.y,a.z,a.pitch].every(Number.isFinite));
  if(speed<=.02)assert.equal(Math.abs(a.z),0);
 }
});
