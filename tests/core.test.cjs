const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const {test} = require('node:test');
const context = {console, Math, JSON, Float32Array, Uint16Array, Uint32Array, performance, globalThis:null};
context.globalThis=context;
vm.createContext(context);
for (const file of ['core.js','world.js','police.js','simulation.js','dynamics.js','interactions.js']) {
 const path=__dirname+'/../src/'+file;
 if (fs.existsSync(path)) vm.runInContext(fs.readFileSync(path,'utf8'), context);
}
const DC = context.DC || {};
test('core exports deterministic random and geometry',()=>{ assert.equal(typeof DC.rng,'function'); assert.equal(typeof DC.moveCircle,'function'); });
test('same seed yields same random sequence',()=>{let a=DC.rng(9),b=DC.rng(9); for(let i=0;i<20;i++) assert.equal(a(),b());});
test('collision stops player outside rectangle',()=>{let p=DC.moveCircle(0,0,20,0,1,[{x:10,z:0,w:4,d:10}]); assert.ok(p.x<=7.01);});
test('movement slides along walls',()=>{let p=DC.moveCircle(7,0,5,3,1,[{x:10,z:0,w:4,d:20}]); assert.ok(p.x<=7.01);assert.ok(p.z>2.5);});
test('city is deterministic and has usable spawn',()=>{let a=new DC.World(1337),b=new DC.World(1337);assert.equal(a.buildings.length,b.buildings.length);assert.ok(a.buildings.length>100);assert.equal(a.blocked(5,8,1),false);});
test('routes stay connected and reach destination',()=>{let w=new DC.World(1337);let path=w.route(1,1,330,-250);assert.ok(path.length>2);assert.ok(Math.hypot(path.at(-1).x-330,path.at(-1).z+250)<100);});
test('on-foot movement changes position',()=>{let s=new DC.Simulation(new DC.World(1337));s.player.x=-4;let z=s.player.z;for(let i=0;i<60;i++)s.step(1/60,{throttle:1,steer:0,sprint:false});assert.ok(s.player.z>z+2);});
test('player enters an adjacent car and exits safely',()=>{let s=new DC.Simulation(new DC.World(1337));assert.equal(s.player.car,null);s.interact();assert.ok(s.player.car!==null);s.interact();assert.equal(s.player.car,null);assert.ok(!s.world.blocked(s.player.x,s.player.z,.4));});
test('driving accelerates without non-finite positions',()=>{let s=new DC.Simulation(new DC.World(1337));s.interact();for(let i=0;i<120;i++)s.step(1/60,{throttle:1,steer:.12});assert.ok(Math.abs(s.cars[0].speed)>5);assert.ok(Number.isFinite(s.player.x));});
test('wanted level never exceeds five or becomes negative',()=>{let s=new DC.Simulation(new DC.World(1337));s.addHeat(99);assert.equal(s.wanted,5);s.heat=0;s.step(1/60,{});assert.equal(s.wanted,0);});
test('save roundtrip restores valid state',()=>{let s=new DC.Simulation(new DC.World(1337));s.cash=2400;s.story=2;let data=s.serialize();let t=new DC.Simulation(new DC.World(1337));assert.equal(t.restore(data),true);assert.equal(t.cash,2400);assert.equal(t.story,2);});
test('bad or future saves rejected',()=>{let s=new DC.Simulation(new DC.World(1337));assert.equal(s.restore({version:999}),false);assert.equal(s.restore({version:1,player:{x:NaN}}),false);});
test('mission cannot advance from arbitrary location',()=>{let s=new DC.Simulation(new DC.World(1337));s.player.x=-300;s.player.z=-300;let old=s.story;s.interact();assert.equal(s.story,old);});
test('right movement is right in a +Z-facing right-handed camera',()=>{let s=new DC.Simulation(new DC.World(1337));s.step(1/60,{steer:1,lookYaw:0});assert.ok(s.player.x<5);});
test('right steering turns right in chase-camera space',()=>{let s=new DC.Simulation(new DC.World(1337));s.interact();for(let i=0;i<60;i++)s.step(1/60,{throttle:1,steer:1});assert.ok(s.actor().yaw<0);});
test('story conversation starts only near the phone and advances on confirmation',()=>{let s=new DC.Simulation(new DC.World(1337));s.player.x=13;s.player.z=20;s.interact('use');assert.equal(s.story,0);assert.equal(s.awaitingStory,0);s.confirmStory();assert.equal(s.story,1);});
test('story advances when the assigned vehicle is entered',()=>{let s=new DC.Simulation(new DC.World(1337));s.story=1;s.interact();assert.equal(s.story,2);});
test('wanted player cannot use the story refuge',()=>{let s=new DC.Simulation(new DC.World(1337));s.story=3;s.player.x=-84;s.player.z=264;s.addHeat(35);s.interact('use');assert.equal(s.awaitingStory,undefined);assert.equal(s.story,3);});
test('upload requires staying on foot close to the terminal',()=>{let s=new DC.Simulation(new DC.World(1337));s.story=4;s.player.x=252;s.player.z=-72;s.interact('use');assert.equal(s.uploading,true);s.missions(6);assert.equal(s.upload,6);s.player.x=0;s.missions(1);assert.ok(s.upload<6);});
test('completed upload activates the final escape',()=>{let s=new DC.Simulation(new DC.World(1337));s.story=4;s.player.x=252;s.player.z=-72;s.interact('use');s.missions(12.1);assert.equal(s.story,5);assert.equal(s.uploading,false);assert.ok(s.wanted>=3);});
test('both campaign endings are reachable and reward differently',()=>{let rewards=[];for(let choice of [0,1]){let s=new DC.Simulation(new DC.World(1337));s.story=5;s.player.x=-252;s.player.z=-156;s.interact('use');assert.equal(s.awaitingStory,5);s.confirmStory(choice);assert.equal(s.story,6);assert.ok(s.ending);rewards.push(s.cash);}assert.ok(rewards[1]>rewards[0]);});
test('free roam disables story triggers',()=>{let s=new DC.Simulation(new DC.World(1337));s.free=true;s.player.x=13;s.player.z=20;s.interact('use');assert.equal(s.awaitingStory,undefined);assert.equal(s.storyTarget(),null);});
test('delivery success pays and clears active job',()=>{let s=new DC.Simulation(new DC.World(1337));s.free=true;s.player.x=0;s.player.z=-72;s.interact('use');assert.ok(s.job);let goal=s.job.points[0],before=s.cash;s.player.x=goal.x;s.player.z=goal.z;s.missions(.1);assert.equal(s.job,null);assert.equal(s.cash,before+650);assert.equal(s.stats.jobs,1);});
test('expired job gives no reward',()=>{let s=new DC.Simulation(new DC.World(1337));s.job={type:'delivery',points:[{x:336,z:336}],index:0,time:1,reward:650};let cash=s.cash;s.missions(1.1);assert.equal(s.job,null);assert.equal(s.cash,cash);});
test('race requires a vehicle',()=>{let s=new DC.Simulation(new DC.World(1337));s.free=true;s.player.x=-168;s.player.z=12;s.interact('use');assert.equal(s.job,null);});
test('police heat decays after losing sight',()=>{let s=new DC.Simulation(new DC.World(1337));s.cars=s.cars.filter(c=>!c.police);s.addHeat(20);for(let i=0;i<900;i++)s.police(1/60);assert.equal(s.wanted,0);assert.equal(s.stats.escapes,1);});
test('arrest respawns player and preserves story',()=>{let s=new DC.Simulation(new DC.World(1337));s.story=3;let c=s.cars.find(c=>c.police);c.x=s.player.x;c.z=s.player.z;c.speed=0;s.addHeat(40);for(let i=0;i<300;i++)s.police(1/60);assert.equal(s.wanted,0);assert.equal(s.story,3);assert.equal(s.cash,550);assert.equal(s.player.health,100);});
test('collectibles reward only once',()=>{let s=new DC.Simulation(new DC.World(1337));let c=s.world.crates[0];s.player.x=c.x;s.player.z=c.z;let old=s.cash;s.missions(.1);s.missions(.1);assert.equal(s.cash,old+150);assert.equal(s.collected.length,1);});
test('zero-delta simulation remains finite',()=>{let s=new DC.Simulation(new DC.World(1337));s.step(0,{});assert.ok(Number.isFinite(s.player.x));assert.ok(Number.isFinite(s.player.z));});
test('all mission destinations are outside buildings',()=>{let w=new DC.World(1337);for(let t of DC.stories)assert.equal(w.blocked(t.x,t.z,.4),false,t.name);});
test('restoring does not resume transient timed jobs',()=>{let s=new DC.Simulation(new DC.World(1337));s.job={type:'delivery',points:[{x:0,z:84}],index:0,time:50,reward:650};let t=new DC.Simulation(new DC.World(1337));assert.equal(t.restore(s.serialize()),true);assert.equal(t.job,null);});
test('a stolen police car cannot detect or arrest its own driver',()=>{let s=new DC.Simulation(new DC.World(1337));let c=s.cars.find(c=>c.police);c.x=s.player.x;c.z=s.player.z;c.speed=0;s.interact();assert.equal(s.actor().police,true);for(let car of s.cars)if(car!==c&&car.police){car.x=420;car.z=420;}for(let i=0;i<180;i++)s.police(1/60);assert.equal(s.bust,0);assert.equal(s.seen,false);});
test('save restores police vehicle appearance and stolen state',()=>{let s=new DC.Simulation(new DC.World(1337));let c=s.cars.find(c=>c.police);c.x=5;c.z=8;c.speed=0;s.interact();let t=new DC.Simulation(new DC.World(1337));assert.equal(t.restore(s.serialize()),true);assert.equal(t.actor().police,true);assert.equal(t.actor().stolen,true);});
test('map projection places camera-right world direction on the right',()=>{assert.equal(typeof DC.mapProject,'function');let p=DC.mapProject(-10,20,0,0,200,200,2);assert.equal(p[0],120);assert.equal(p[1],60);});
test('map click inverse preserves world positions',()=>{assert.equal(typeof DC.mapUnproject,'function');let p=DC.mapProject(-84,168,0,0,800,600,.6),q=DC.mapUnproject(p[0],p[1],0,0,800,600,.6);assert.ok(Math.abs(q.x+84)<1e-8);assert.ok(Math.abs(q.z-168)<1e-8);});

test('humanoid pose distinguishes idle walk run and airborne states',()=>{
 assert.equal(typeof DC.humanoidPose,'function');
 const idle=DC.humanoidPose({phase:0,speed:0,sprint:0,y:0,vy:0,turn:0,time:1});
 const walk=DC.humanoidPose({phase:Math.PI/2,speed:3.3,sprint:0,y:0,vy:0,turn:0,time:1});
 const run=DC.humanoidPose({phase:Math.PI/2,speed:6.2,sprint:1,y:0,vy:0,turn:0,time:1});
 const air=DC.humanoidPose({phase:0,speed:3, sprint:0,y:1,vy:2,turn:0,time:1});
 assert.ok(Math.abs(idle.hipBob)<.03);
 assert.ok(Math.abs(walk.left.hip)>Math.abs(idle.left.hip)+.15);
 assert.ok(Math.abs(run.left.hip)>Math.abs(walk.left.hip));
 assert.ok(air.airborne>.9);
 assert.ok(air.left.knee>.15 && air.right.knee>.15);
});

test('humanoid pose counter-rotates shoulders and reacts to turning',()=>{
 const pose=DC.humanoidPose({phase:Math.PI/2,speed:4,sprint:.35,y:0,vy:0,turn:.8,time:2});
 assert.ok(Math.sign(pose.shoulderYaw)===-Math.sign(pose.pelvisYaw));
 assert.ok(Math.abs(pose.spineRoll)>.01);
 assert.ok(Math.abs(pose.headYaw)>.01);
});

test('on-foot animation state tracks speed sprint jump and landing',()=>{
 let s=new DC.Simulation(new DC.World(1337));s.player.x=-4;
 for(let i=0;i<30;i++)s.step(1/60,{throttle:1,steer:0,sprint:true,lookYaw:0});
 assert.ok(s.player.moveSpeed>5);
 assert.ok(s.player.sprintBlend>.5);
 s.step(1/60,{brake:true,lookYaw:0});
 assert.equal(s.player.grounded,false);
 assert.ok(s.player.vy>0);
 for(let i=0;i<120;i++)s.step(1/60,{lookYaw:0});
 assert.equal(s.player.grounded,true);
 assert.ok(s.player.landing>=0);
});
