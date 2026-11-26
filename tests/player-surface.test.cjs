'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const ctx=vm.createContext({});
for(const file of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','character-motion','skin-rig','renderer','frontier-renderer','cast-renderer'])
 vm.runInContext(fs.readFileSync('src/'+file+'.js','utf8'),ctx);
const D=ctx.DC;
const close=(a,b,eps=1e-6)=>assert.ok(Math.abs(a-b)<eps,a+' / '+b);

function renderer(){
 const r=Object.create(D.CastRenderer.prototype);
 r.world=new D.World(1337);
 return r;
}

test('surveyed player contact uses streamed street, curb, overlapping parcel and park tops',()=>{
 const r=renderer();
 const park=r.world.home.blocks.find(c=>c.park);
 for(const [x,z,top] of [[156.85630222456163,141.59919430609622,.15],[155.5,138.595,.145],
                           [162.8,141.6,-.027],[park.x,park.z,.175],[-168,0,-.027]]){
  const frame=r.playerSurface(x,z);close(frame.shadow,top+.003);close(frame.lift+.015,top);
 }
 // Approach the same 17.7 cm roadside step from both directions.
 let previous=r.playerSurface(157.5,141.6).lift;
 for(let x=157.51;x<=158.5;x+=.01){
  const value=r.playerSurface(x,141.6).lift;
  assert.ok(value<=previous+1e-7 && previous-value<.009,'unbounded curb step at '+x);
  previous=value;
 }
});

test('one presentation translation moves avatar, held prop and shadow, independently of jump, yaw, seats and studio',()=>{
 const r=renderer(),p={x:156.8563,z:141.5992,y:.44,vy:-1.3,yaw:1.12,car:null};
 const dynamic={shoe:[],prop:[],smoke:[]},sim={player:p},seen=[];
 r.renderPerson=(actor,isPlayer)=>{
  seen.push([actor,isPlayer]);
  for(const [name,y,material] of [['shoe',actor.y+.015,0],['prop',actor.y+1.28,3],['smoke',-.010,37]])
   r.add(dynamic,name,actor.x,y,actor.z,1,1,1,[1,1,1],material,0,actor.yaw);
 };
 r.renderPlayer(sim);
 assert.equal(seen[0][0],p);assert.equal(seen[0][1],true);
 close(dynamic.shoe[1],.15+p.y);close(dynamic.prop[1]-dynamic.shoe[1],1.28-.015);
 close(dynamic.smoke[1],.153);close(dynamic.shoe[3],p.yaw);close(p.y,.44);
 assert.equal(r.playerSurfaceFrame,null);
 r.add(dynamic,'prop',0,1.5,0,1,1,1,[1,1,1]);close(dynamic.prop[17],1.5);
 r.previewStudio=true;r.renderPlayer(sim);close(dynamic.shoe[17],p.y+.015);r.previewStudio=false;
 sim.access={};const accessPose={...p,y:-.29,seated:true};sim.accessPlayerPose=()=>accessPose;
 r.renderPlayer(sim);assert.equal(seen.at(-1)[0],accessPose);close(dynamic.shoe[33],-.29+.015);
 sim.access=null;p.car=0;sim.actor=()=>({x:p.x,z:p.z,yaw:0});
 r.renderPlayer(sim);assert.ok(seen.at(-1)[0].seated);close(dynamic.shoe[49],-.29+.015);
});


test('boarding and exiting at a real curb preserve both street endpoints, the door grip and the seat',()=>{
 const r=renderer(),sim=new D.Simulation(r.world),c=sim.cars[1],p=sim.player;
 sim.free=true;
 sim.cars.forEach((other,i)=>Object.assign(other,{x:300+6*i,z:0,speed:0,parked:true}));
 Object.assign(c,{x:158.7,z:141.45,yaw:0,speed:0,driver:null,owned:true});
 Object.assign(p,{x:156.40,z:141.60,yaw:Math.PI/2,car:null});
 let pose;
 function sample(){
  let lift=0;
  r.renderPerson=n=>{pose=n;lift=r.playerSurfaceFrame?.lift||0;};
  r.renderPlayer(sim);return lift;
 }
 const start=sample();close(start,.135);
 sim.interact('car');assert.equal(sim.access?.kind,'enter');close(sample(),start);
 let last=start,grips=0,seats=0,steps=0;
 while(sim.access&&steps++<600){
  const current=sample();
  assert.ok(Math.abs(last-current)<.024,'boarding discontinuity '+(current-last));
  if(pose.handTargets?.R?.weight===1){
   close(current,0);
   const body=D.vehicleBodyFrame(c,sim.time),door=body.door(-1,c.doorOpen);
   const outside=body.direction(-1,0,0,door.yaw),target=door.handle.map((v,i)=>v+.015*outside[i]);
   const hand=D.SkinRig.palmPoint(D.SkinRig.pose(pose,sim.time),pose,'R');
   assert.ok(Math.hypot(hand.x-target[0],hand.y+current-target[1],hand.z-target[2])<.005,'palm left the rotating handle');
   grips++;
  }
  if(pose.seatBlend===1){close(current,0);close(pose.y,-.29);seats++;}
  last=current;sim.step(1/60,{});
 }
 assert.ok(grips&&seats);assert.equal(p.car,1);close(sample(),0);
 const seat=D.carPoint(c,-.38,-.20);close(pose.x,seat.x);close(pose.z,seat.z);close(pose.y,-.29);
 sim.interact('car');assert.equal(sim.access?.kind,'exit');last=sample();close(last,0);
 steps=0;
 while(sim.access&&steps++<600){
  const current=sample();
  assert.ok(Math.abs(last-current)<.024,'exit discontinuity '+(current-last));
  if(pose.seatBlend===1){close(current,0);close(pose.y,-.29);}
  last=current;sim.step(1/60,{});
 }
 assert.equal(p.car,null);close(sample(),last);close(last,.135);
 sim.interact('car');assert.equal(sim.access?.kind,'enter');
 while(sim.access.elapsed<sim.access.approach+.55){sample();sim.step(1/60,{});}
 last=sample();close(last,0);sim.interact('car');assert.equal(sim.access,null);close(sample(),last);
 for(let i=0;i<18;i++){sim.step(1/60,{});const next=sample();assert.ok(Math.abs(next-last)<.017);last=next;}
 close(last,r.playerSurface(p.x,p.z).lift);
});
