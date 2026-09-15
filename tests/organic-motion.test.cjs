'use strict';
const test=require('node:test'),a=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
for(const n of ['core','character-motion','skin-rig'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));
const R=DC.SkinRig,pt=(q,id,p)=>{const m=q.matrices.subarray(R.ids[id]*16,R.ids[id]*16+16);return [0,1,2].map(i=>m[i]*p[0]+m[4+i]*p[1]+m[8+i]*p[2]+m[12+i]+(i===1?q.rootY:0));};
test('grounded sole has a contact, not an unreachable ankle during the stride',()=>{
 const q=R.pose({moveSpeed:3.3,sprintBlend:0,walk:0},1);
 const ys=[-.075,.05,.205].map(z=>pt(q,'footL',[-.108,.015,z])[1]);
 a.ok(Math.min(...ys)<.026,JSON.stringify(ys));
});
test('organic motion exposes phase diagnostics and heel/toe articulation',()=>{a.ok(DC.NaturalMotion);const q=R.pose({moveSpeed:1.4,walk:.1},1);a.ok(q.feet?.L);a.notEqual(q.feet.L.pitch,0);});
test('all gait phases retain ground clearance and attainable support',()=>{
 a.ok(DC.NaturalMotion);
 for(const speed of [0,.4,1.4,3.3,6.2])for(const crouch of [0,1])for(let j=0;j<40;j++){
  const q=R.pose({moveSpeed:speed,sprintBlend:speed>5?1:0,walk:j*Math.PI/20,crouch,turnRate:1.2},1);
  for(const k of ['L','R']){const ys=[-.075,.05,.205].flatMap(z=>[-.048,.048].map(x=>pt(q,'foot'+k,[(k==='L'?-.108:.108)+x,.015,z])[1]));a.ok(Math.min(...ys)>.006,`${speed} ${crouch} ${j} ${k}: ${Math.min(...ys)}`);if(q.feet[k].contact)a.ok(Math.min(...ys)<.033,'supported sole must touch');}
  a.ok(Array.from(q.matrices).every(Number.isFinite));
 }
});
test('seated target pose remains seated and does not acquire ground foot locks',()=>{const q=R.pose({y:-.29,seated:true,moveSpeed:0},1);a.ok(q.feet?.L===null);a.ok(pt(q,'shinR',R.bones[R.ids.shinR][2])[2]>.25);});
test('running elbows bend and arms oppose leading legs',()=>{const q=R.pose({moveSpeed:6.2,sprintBlend:1,walk:0},1);a.ok(q.pose.left.elbow>.75);a.ok(q.pose.left.shoulder>0);});
test('acceleration and braking produce distinct bounded posture',()=>{a.ok(DC.NaturalMotion);const x={moveSpeed:3,walk:1,motion:{acceleration:5,turn:0}},q=R.pose(x,1),r=R.pose({...x,motion:{acceleration:-5,turn:0}},1);a.ok(q.pose.spinePitch>r.pose.spinePitch+.03);a.ok(Math.abs(q.pose.spinePitch)<.45);});
test('contextual fingers differ between wheel and box, without moving wrist',()=>{a.ok(R.gripProfile);const g=R.gripProfile({seated:true},'R'),b=R.gripProfile({carry:1},'R');a.notDeepEqual(g.fingers,b.fingers);a.ok(g.fingers.index[0]!==g.fingers.little[0]);});
test('rest breathing differs between actors and has no root-coordinate mutation',()=>{const n={x:1,z:2,yaw:.2,variant:0,moveSpeed:0};const saved=JSON.stringify(n),q=R.pose(n,3),r=R.pose({...n,variant:5},3);a.notDeepEqual([...q.matrices],[...r.matrices]);a.equal(JSON.stringify(n),saved);});
test('visible tracking holds support points and is idempotent at same timestamp',()=>{a.ok(DC.MotionTracker);const t=new DC.MotionTracker();let n={x:0,z:0,yaw:0,walk:.1,moveSpeed:1.4};const x=t.update('p',n,1),y=t.update('p',{...n,z:.014,walk:.18},1.01);a.equal(y.motion.feet.L.z,x.motion.feet.L.z);const y2=t.update('p',{...n,z:.014,walk:.18},1.01);a.deepEqual(y.motion,y2.motion);});
test('tracking resets on teleport and has bounded memory',()=>{a.ok(DC.MotionTracker);const t=new DC.MotionTracker(32);t.update('p',{x:0,z:0,yaw:0,walk:.1,moveSpeed:1},1);const q=t.update('p',{x:4000,z:4000,yaw:0,walk:.1,moveSpeed:1},2);a.ok(q.motion.feet.L.x>3990);for(let i=0;i<500;i++)t.update('id'+i,{x:0,z:0},3);a.ok(t.size<=32);});
test('motion tracking never creates a lock while seated or airborne',()=>{a.ok(DC.MotionTracker);const t=new DC.MotionTracker();for(const n of [{seated:true,y:-.29},{y:.2,vy:-1},{accessPhase:'pull'}]){const r=t.update('p',{x:0,z:0,moveSpeed:0,...n},1);a.equal(r.motion.feet.L,null);}});
test('visual tracking leaves actor inputs and serialization fields untouched',()=>{a.ok(DC.MotionTracker);const t=new DC.MotionTracker(),n={x:0,z:0,walk:.2,moveSpeed:3.3,health:100};const before=JSON.stringify(n);t.update('p',n,2);a.equal(JSON.stringify(n),before);});
test('cadence is finite, zero at rest, and shared between run and walk previews',()=>{a.ok(DC.NaturalMotion);a.equal(DC.NaturalMotion.frequency(0),0);for(const v of [.1,1.4,3.3,6.2])a.ok(DC.NaturalMotion.frequency(v)>0&&DC.NaturalMotion.frequency(v)<16);});
test('sequential straight gait holds the contacting ankle while root travels',()=>{
 const t=new DC.MotionTracker();let z=0,phase=0;let tested=0,maxError=0;
 for(let i=0;i<240;i++){const speed=1.4;z+=speed/60;phase+=DC.NaturalMotion.frequency(speed)/60;const n=t.update('p',{x:0,z,yaw:0,walk:phase,moveSpeed:speed},i/60),q=R.pose(n,i/60);for(const k of ['L','R']){if(!n.motion.feet[k]||!q.feet[k])continue;const ankle=pt(q,'foot'+k,R.bones[R.ids['foot'+k]][2]),lock=n.motion.feet[k],error=Math.hypot(ankle[0]-lock.x,ankle[2]+z-lock.z);maxError=Math.max(maxError,error);tested++;}}
 a.ok(tested>120);a.ok(maxError<.012,`slip ${maxError}`);
});
test('sitting transition remains continuous rather than changing IK branches abruptly',()=>{let prev;for(let i=0;i<=100;i++){const t=i/100,q=R.pose({seatBlend:t,seated:t===1,y:-.29*t,moveSpeed:0,grip:.6},2),p=pt(q,'footR',R.bones[R.ids.footR][2]);if(prev)a.ok(Math.hypot(...p.map((x,j)=>x-prev[j]))<.045);prev=p;}});
test('turns and a stop release obsolete support and leave finite bounds',()=>{const t=new DC.MotionTracker();let x=0,z=0,phase=0;for(let i=0;i<360;i++){const speed=i<200?3.3:0,yaw=i/100;x+=Math.sin(yaw)*speed/60;z+=Math.cos(yaw)*speed/60;phase+=DC.NaturalMotion.frequency(speed)/60;const n=t.update('p',{x,z,yaw,walk:phase,moveSpeed:speed},i/60),q=R.pose(n,i/60);a.ok(Array.from(q.matrices).every(Number.isFinite));a.ok(q.rootY>-.45&&q.rootY<.12);}});
test('heel strike and push-off remain continuous at both cycle boundaries',()=>{
 for(const speed of [1.4,6.2]){const n={moveSpeed:speed,sprintBlend:speed>5?1:0},g=DC.NaturalMotion.gait(speed,n.sprintBlend);for(const phase of [g.duty,1]){const f=DC.NaturalMotion.foot({...n,walk:(phase-1e-6)*Math.PI*2},'L'),h=DC.NaturalMotion.foot({...n,walk:(phase+1e-6)*Math.PI*2},'L');a.ok(Math.abs(f.pitch-h.pitch)<.0001,`pitch discontinuity at ${phase}`);a.ok(Math.hypot(f.y-h.y,f.z-h.z)<.0001);}}
});
