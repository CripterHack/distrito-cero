/* Procedural animation is driven by travelled distance, not wall-clock speed. */
'use strict';
(function(D){
 const basePose=D.humanoidPose;
 D.humanoidPose=function(opts){
  const q=basePose(opts),c=opts.crouch||0,st=opts.stagger||0,reach=Math.max(opts.carry?.86:0,opts.reach||0);
  q.spinePitch+=c*.28+st*.37+(opts.dodge||0)*.65;q.headPitch-=c*.15+st*.10;q.spineRoll+=st*Math.sin((opts.time||0)*13)*.12;
  for(const side of ['left','right']){q[side].shoulder=D.lerp(q[side].shoulder,-.75,Math.min(1,reach));q[side].elbow=D.lerp(q[side].elbow,1.05,Math.min(1,reach));}
  return q;
 };
 D.solveFootPose=function(n,side,rootY,airPose){
  if(n.seated)return{hip:-1.35,knee:1.47,ankle:-.12};
  if((n.y||0)>.025||Math.abs(n.vy||0)>.05)return{...airPose,hip:-(airPose.hip||0)-.3,knee:Math.max(.5,airPose.knee||0),ankle:0};
  const run=n.sprintBlend||0,m=D.clamp((n.moveSpeed||0)/1.5,0,1),k=D.lerp(4.8,2.7,run),stride=Math.PI/(2*k)*m*(1-(n.crouch||0)*.28);
  const phase=((n.walk||0)+(side>0?Math.PI:0))%(Math.PI*2),stance=phase<Math.PI,t=stance?phase/Math.PI:(phase-Math.PI)/Math.PI;
  // During stance, derivative of foot z cancels forward root velocity on a straight line.
  const z=stance?stride*(1-2*t):stride*(-1+2*(t*t*(3-2*t)));
  const targetY=.09-rootY+(stance?0:Math.sin(t*Math.PI)*D.lerp(.14,.27,run)*m);
  const dy=.82-targetY,len=D.clamp(Math.hypot(dy,z),.14,.849),a=.43,b=.42;
  const hip=Math.atan2(-z,dy)-Math.acos(D.clamp((a*a+len*len-b*b)/(2*a*len),-1,1));
  const knee=Math.PI-Math.acos(D.clamp((a*a+b*b-len*len)/(2*a*b),-1,1));
  return{hip,knee,ankle:-(hip+knee)};
 };
})(DC);

/* v0.13: pure gait sampling and bounded visual contact memory. No gameplay writes. */
(function(D){
 const TAU=Math.PI*2,smooth=(a,b,x)=>{const t=D.clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
 const finite=(x,f=0)=>Number.isFinite(x)?x:f;
 function gait(speed=0,sprint=0,crouch=0){
  speed=D.clamp(finite(speed),0,10);crouch=D.clamp(finite(crouch),0,1);
  const run=Math.max(D.clamp(finite(sprint),0,1),smooth(1.85,4.8,speed))*(1-crouch*.8);
  const weight=smooth(.02,.65,speed),hz=(1.05+Math.min(1.1,speed*.19))*(1-crouch*.12)*weight;
  const duty=D.lerp(.62,.28,run),span=hz>1e-5?Math.min(.86,speed/hz*duty):0;
  return{speed,run,weight,hz,duty,span};
 }
 function foot(n,k){
  const m=n.motion||{},g=gait(m.speed??n.moveSpeed,n.sprintBlend,n.crouch),walk=finite(m.phase??n.walk),ph=((walk/TAU+(k==='R'?.5:0))%1+1)%1;
  const contact=ph<g.duty||g.weight<.025,t=contact?ph/g.duty:(ph-g.duty)/(1-g.duty),side=k==='L'?-1:1;
  let z=contact?g.span*(.5-t):g.span*(-.5+t*t*(3-2*t));
  const heel=-.10*(1-g.run*.5),toe=D.lerp(.28,.43,g.run);
  let pitch=contact?D.lerp(heel,0,smooth(0,.22,t))+toe*smooth(.62,1,t):D.lerp(toe,heel,smooth(0,1,t))-.22*Math.sin(Math.PI*t);
  pitch*=g.weight*(1-(n.crouch||0)*.6);
  const lift=contact?0:Math.pow(Math.max(0,Math.sin(Math.PI*t)),1.35)*D.lerp(.12,.24,g.run)*g.weight;
  // Rotate around heel on strike and forefoot on push-off; bottom is y=.015 in bind pose.
  const soleOffset=.015+.070*Math.cos(pitch)+Math.sin(pitch)*(pitch>=0?.205:-.075);
  return{x:side*(.108+.016*g.run+.018*(n.crouch||0)),y:soleOffset+lift,z,pitch,contact,phase:ph,progress:t,run:g.run,weight:g.weight,yaw:0};
 }
 function frequency(speed,sprint=0,crouch=0){return gait(speed,sprint,crouch).hz*TAU;}
 function distanceRate(speed,sprint=0,crouch=0){return speed>.01?frequency(speed,sprint,crouch)/speed:0;}
 class MotionTracker{
  constructor(limit=144){this.limit=Math.max(1,limit);this.entries=new Map();}
  get size(){return this.entries.size;}
  clear(){this.entries.clear();}
  update(id,n,time,inPlace=false){
   time=finite(time);const x=finite(n.x),z=finite(n.z),yaw=finite(n.yaw),old=this.entries.get(id),dt=old?time-old.time:0;
   if(old&&dt===0&&x===old.x&&z===old.z&&yaw===old.yaw&&n.walk===old.walk&&n.moveSpeed===old.rawSpeed&&!!n.seated===old.seated&&n.accessPhase===old.accessPhase)return{...n,motion:old.motion};
   const reset=!old||dt<0||dt>.3||Math.hypot(x-old.x,z-old.z)>1.4||Math.abs(D.wrap(yaw-old.yaw))>1.5;
   const measured=D.clamp(finite(n.moveSpeed),0,10),step=reset?0:D.clamp(dt,0,.1),speed=reset?measured:D.damp(old.motion.speed,measured,measured<.1?13:16,step);
   const acceleration=reset?0:D.damp(old.motion.acceleration,D.clamp((speed-old.motion.speed)/Math.max(step,.001),-9,9),7,step);
   const turn=reset?finite(n.turnRate):D.damp(old.motion.turn,D.clamp(D.wrap(yaw-old.yaw)/Math.max(step,.001),-4,4),9,step);
   const motion={speed,acceleration,turn,phase:finite(n.walk),feet:{L:null,R:null},reset,inPlace};
   const disabled=inPlace||n.seated||(n.seatBlend||0)>.025||(n.y||0)>.025||Math.abs(n.vy||0)>.05||!!n.accessPhase||(n.dodge||0)>.03;
   for(const k of ['L','R']){
    const f=foot({...n,motion},k),previous=!reset&&!disabled?old.motion.feet[k]:null;
    if(disabled||!f.contact)continue;
    // During a sharp reversal, release naturally instead of twisting the ankle indefinitely.
    let lock=previous;
    if(!lock||Math.hypot(lock.x-x,lock.z-z)>.57||Math.abs(D.wrap(lock.yaw-yaw))>.68){lock={x:x+f.x*Math.cos(yaw)+f.z*Math.sin(yaw),z:z-f.x*Math.sin(yaw)+f.z*Math.cos(yaw),yaw};}
    motion.feet[k]={...lock};
   }
   this.entries.delete(id);this.entries.set(id,{x,z,yaw,time,motion,walk:n.walk,rawSpeed:n.moveSpeed,seated:!!n.seated,accessPhase:n.accessPhase});
   while(this.entries.size>this.limit)this.entries.delete(this.entries.keys().next().value);
   return{...n,motion};
  }
 }
 D.NaturalMotion={gait,foot,frequency,distanceRate,smooth};D.MotionTracker=MotionTracker;
})(DC);
