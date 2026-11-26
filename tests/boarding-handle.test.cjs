'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const ctx=vm.createContext({DC:{Renderer:class{}}});
for(const file of ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','character-fit','character-motion','skin-rig','reactive-renderer']){
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../src',file+'.js'),'utf8'),ctx);
}
const D=ctx.DC;
function scene(occupied,yaw,startSide=-1){
 const s=new D.Simulation(new D.FrontierWorld(1337)),c=s.cars[0];s.free=true;s.cars=[c];s.peds=[];
 Object.assign(c,{x:4,z:40,yaw,speed:0,parked:!occupied,driver:occupied?D.driverProfile(c):null});
 Object.assign(s.player,D.carPoint(c,startSide*2.25,.1),{car:null,y:0});s.interact('car');
 assert.equal(s.access?.kind,occupied?'extract':'enter');return {s,c};
}
function drawnHandle(s,c){
 let handle;
 const rig={assetParts:[{name:'BODY_shell',key:'body-shell'}],currentSim:s,currentTime:s.time,dynamic:{},meshes:{},
  add(_list,key,x,y,z,w,h,d,_col,_mat,_em,yaw,_a,_b,pitch,roll){
   if(!handle&&key==='box'&&w===.03&&h===.036&&d===.21)handle={x,y,z,yaw,pitch,roll};
  }};
 D.Renderer.prototype.renderCar.call(rig,c);
 // The first detailed side panel is on the driver's left. Its outside face
 // is 15 mm from the drawn handle's center on the rotated local -X axis.
 const {yaw,roll}=handle;
 return {x:handle.x-.015*Math.cos(yaw)*Math.cos(roll),y:handle.y-.015*Math.sin(roll),z:handle.z+.015*Math.sin(yaw)*Math.cos(roll)};
}
const gap=(p,t)=>Math.hypot(p.x-t.x,p.y-t.y,p.z-t.z);
for(const occupied of [false,true])test((occupied?'occupied':'empty')+' sedan keeps the moving outer handle under the posed palm',()=>{
 for(const yaw of [0,.74,-.65]){
  const {s,c}=scene(occupied,yaw);let checks=0,previous;
  const tracker=new D.MotionTracker();
  for(let i=0;i<360&&s.access;i++){
   s.step(1/60,{});if(!s.access)break;
   // Include a tipped and damaged car, using the full geometry orientation.
   c.suspension.pitch=.055*Math.sin(i*.07);c.suspension.roll=-.035;c.damage.left=.47;
   const n=s.accessPlayerPose(),actor=tracker.update('player',n,s.time,false);
   const q=D.SkinRig.pose({...actor,neckDrop:.043},s.time),p=D.SkinRig.palmPoint(q,actor,'R');
   if(n.accessPhase!=='open')continue;
   if(previous)assert.ok(gap(p,previous)<.18,'palm jumped at '+c.doorOpen);
   previous=p;
   if(c.doorOpen<.01||c.doorOpen>.99)continue;
   const dist=gap(p,drawnHandle(s,c));checks++;
   assert.ok(dist<.006,`palm missed handle by ${dist.toFixed(3)} m at ${c.doorOpen.toFixed(3)}`);
  }
  assert.ok(checks>=12,'insufficient opening coverage');
 }
});
test('grounded actor rounds the end of the open panel and withdraws the hand continuously',()=>{
 const {s,c}=scene(false,-.4),tracker=new D.MotionTracker();
 let previous=null,checked=0,locks=0,swings=0;
 for(let i=0;i<420&&s.access;i++){
  s.step(1/60,{});if(!s.access)break;
  const n=s.accessPlayerPose(),a=tracker.update('player',n,s.time,false),q=D.SkinRig.pose(a,s.time);
  const palm=D.SkinRig.palmPoint(q,a,'R');
  if(previous)assert.ok(gap(palm,previous)<.19,'palm jumped at '+i);
  if(n.accessPhase==='enter')break;
  previous=palm;
  if(n.accessPhase!=='open')continue;
  locks+=Number(!!a.motion.feet.L||!!a.motion.feet.R);
  swings+=Number(q.feet.L?.y>.12||q.feet.R?.y>.12);
  if(c.doorOpen<.999)continue;
  const frame=D.vehicleBodyFrame(c,s.time),door=frame.door(-1,c.doorOpen);
  const dx=n.x-door.panel[0],dz=n.z-door.panel[2];
  const localX=dx*Math.cos(door.yaw)-dz*Math.sin(door.yaw),localZ=dx*Math.sin(door.yaw)+dz*Math.cos(door.yaw);
  assert.ok(Math.hypot(localX,Math.max(0,Math.abs(localZ)-.85))>.31,'body cuts across panel');
  checked++;
 }
 assert.ok(checked>40&&locks>20&&swings>10,'incomplete stepping sequence');
});
test('cancel halfway through the door swing leaves the player where their feet were visible',()=>{
 for(const occupied of [false,true]){
  const {s,c}=scene(occupied,0),driver=c.driver;
  while(s.access&&c.doorOpen<.5)s.step(1/60,{});
  assert.ok(s.access);const pose=s.accessPlayerPose();
  s.interact('car');assert.equal(s.access,null);assert.equal(c.doorOpen,0);
  assert.equal(c.driver,driver);assert.equal(s.player.car,null);
  assert.ok(D.distance(pose,s.player)<.04&&s.clearance(s.player,c,true));
 }
});

test('approaching the passenger side still uses the physical driver latch',()=>{
 const {s,c}=scene(false,.4,1);
 assert.ok(s.access.path.length>2,'must approach around the car');
 while(s.access&&c.doorOpen<.5)s.step(1/60,{});
 assert.equal(s.access?.kind,'enter');assert.equal(c.doorSide,-1);
 const n=s.accessPlayerPose(),rig=D.SkinRig.pose(n,s.time);
 assert.ok(gap(D.SkinRig.palmPoint(rig,n,'R'),drawnHandle(s,c))<.006);
});
test('an obstacle entering the swing path cancels before the actor walks through it',()=>{
 const {s,c}=scene(true,0),driver=c.driver;
 while(s.access&&c.doorOpen<.30)s.step(1/60,{});
 const start=s.accessPlayerPose();
 s.step(1/60,{});
 const next=s.accessPlayerPose(),distance=D.distance(next,start);
 const cone=s.dynamics.add('cone',next.x+.64*(next.x-start.x)/distance,
  next.z+.64*(next.z-start.z)/distance,'boarding-test-cone');
 s.dynamics.hash.rebuild(s.dynamics.props);
 for(let i=0;i<30&&s.access;i++)s.step(1/60,{});
 assert.equal(s.access,null);assert.equal(c.driver,driver);assert.equal(c.doorOpen,0);
 assert.equal(s.player.car,null);assert.ok(s.clearance(s.player,c,true));
 assert.ok(D.distance(s.player,cone)>=cone.radius+.32);
});
test('the supporting leg stays within reach when several swing frames are skipped',()=>{
 for(const framesBetweenDraws of [8,10,15]){
  const {s,c}=scene(false,0),tracker=new D.MotionTracker();let samples=0;
  for(let i=0;s.access;i++){
   s.step(1/60,{});if(!s.access||i%framesBetweenDraws)continue;
   const n=s.accessPlayerPose(),a=tracker.update('player',n,s.time,false),q=D.SkinRig.pose(a,s.time);
   if(n.accessPhase==='enter')break;
   if(n.accessPhase!=='open')continue;
   assert.ok(q.rootY>-.26,'planted foot dragged the pelvis down to '+q.rootY+' m');
   if(c.doorOpen>.02&&c.doorOpen<.98)assert.ok(gap(D.SkinRig.palmPoint(q,a,'R'),drawnHandle(s,c))<.006);
   samples++;
  }
  assert.ok(samples>=7);
 }
});
