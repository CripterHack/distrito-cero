'use strict';
const test=require('node:test'), assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const ctx=vm.createContext({});
for(const file of ['core','world','frontier-world','simulation','occupancy','skin-rig','renderer','frontier-renderer','cast-renderer'])
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
 sim.access=null;p.car=0;sim.actor=()=>({x:p.x,z:p.z,yaw:0});D.VehicleCabin={hands:()=>({})};
 r.renderPlayer(sim);assert.ok(seen.at(-1)[0].seated);close(dynamic.shoe[49],-.29+.015);
});
