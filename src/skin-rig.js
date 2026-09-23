/* Native skeletal palette and analytic contacts. Renderer applies dual-quaternion skinning. Metres, Y up, +Z forward. */
'use strict';
(function(D){
 // Preserve the first 17 indices for existing data and append explicit clavicles/digits.
 const bones=[['pelvis',null,[0,.94,0]],['spine','pelvis',[0,1.125,0]],['chest','spine',[0,1.345,0]],['neck','chest',[0,1.50,0]],['head','neck',[0,1.63,0]]];
 for(const [s,k] of [[-1,'L'],[1,'R']])bones.push(['upperArm'+k,'clavicle'+k,[s*.2115,1.435,0]],['forearm'+k,'upperArm'+k,[s*.2538,1.135,0]],['hand'+k,'forearm'+k,[s*.2637,.885,0]],['thigh'+k,'pelvis',[s*.108,.94,0]],['shin'+k,'thigh'+k,[s*.108,.495,0]],['foot'+k,'shin'+k,[s*.108,.085,0]]);
 for(const [s,k] of [[-1,'L'],[1,'R']])bones.push(['clavicle'+k,'chest',[s*.075,1.414,-.006]]);
 const fingers={L:[],R:[]};
 for(const [s,k] of [[-1,'L'],[1,'R']]){
  const wx=s*.2637;
  for(const [name,z,y,lengths,radius] of [['index',.023,.799,[.031,.022,.017],.0083],['middle',.003,.794,[.034,.024,.019],.0086],['ring',-.017,.799,[.031,.022,.018],.0081],['little',-.034,.813,[.023,.017,.015],.0068]]){
   const joints=[];let yy=y;
   for(let j=0;j<3;j++){joints.push([wx-s*.0015*j,yy,z]);yy-=lengths[j];}
   const tip=[wx-s*.004,yy,z+.001];const names=joints.map((_,j)=>name+j+k);
   joints.forEach((p,j)=>bones.push([names[j],j?names[j-1]:'hand'+k,p]));
   fingers[k].push({name,bones:names,joints,tip,radius});
  }
  const joints=[[wx-s*.008,.842,.028],[wx-s*.018,.819,.046],[wx-s*.022,.798,.055]],tip=[wx-s*.024,.782,.060],names=joints.map((_,j)=>'thumb'+j+k);
  joints.forEach((p,j)=>bones.push([names[j],j?names[j-1]:'hand'+k,p]));
  fingers[k].push({name:'thumb',bones:names,joints,tip,radius:.010});
 }
 const ids=Object.fromEntries(bones.map((b,i)=>[b[0],i]));
 function matrix(t,rx=0,ry=0,rz=0){
  const a=Math.cos(rx),b=Math.sin(rx),c=Math.cos(ry),d=Math.sin(ry),e=Math.cos(rz),f=Math.sin(rz);
  return new Float32Array([c*e,f,-d*e,0,-c*f*a+d*b,e*a,d*f*a+c*b,0,c*f*b+d*a,-e*b,-d*f*b+c*a,0,...t,1]);
 }
 function multiply(a,b){const o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)for(let k=0;k<4;k++)o[c*4+r]+=a[k*4+r]*b[c*4+k];return o;}
 function evaluate(rotations={},offsets={},neckDrop=0){
  const fitted=neckDrop&&D.CharacterFit?D.CharacterFit.fittedBones(bones,neckDrop):bones;
  const world=[],visiting=new Set(),out=new Float32Array(bones.length*16);
  function visit(i){
   if(world[i])return world[i];if(visiting.has(i))throw new Error('Cyclic skeleton');visiting.add(i);
   const [name,parent,bind]=fitted[i],p=parent===null?null:ids[parent],pb=p===null?[0,0,0]:fitted[p][2];
   const local=matrix(bind.map((v,j)=>v-pb[j]+(offsets[name]?.[j]||0)),...(rotations[name]||[0,0,0]));
   world[i]=p===null?local:multiply(visit(p),local);visiting.delete(i);
   out.set(multiply(world[i],matrix(bind.map(v=>-v))),i*16);return world[i];
  }
  bones.forEach((_,i)=>visit(i));return out;
 }
 // Re-evaluate descendants after a wrist is replaced by the analytic contact solver.
 function refreshFingers(q,rot,k,opposition=null){
  for(const finger of fingers[k])for(const name of finger.bones){
   const i=ids[name],[,parent,bind]=bones[i],pi=ids[parent],pb=bones[pi][2];
   const worldParent=multiply(q.matrices.subarray(pi*16,pi*16+16),matrix(pb));
   let local=matrix(bind.map((v,j)=>v-pb[j]),...(rot[name]||[0,0,0]));
   if(finger.name==='thumb'&&name===finger.bones[0]&&opposition){
    // Virtual metacarpal base: move the thumb root by rotation about the palm,
    // not by scaling segments or moving the wrist/contact target. Artist values.
    const side=k==='R'?1:-1,pivot=[pb[0]-.002*side,pb[1]-.018,pb[2]+.012];
    const a=opposition.map(v=>D.clamp(v,-1.2,1.2));
    local=multiply(multiply(matrix(pivot.map((v,j)=>v-pb[j])),matrix([0,0,0],a[0],side*a[1],side*a[2])),matrix(bind.map((v,j)=>v-pivot[j]),...(rot[name]||[0,0,0])));
   }
   const world=multiply(worldParent,local);
   q.matrices.set(multiply(world,matrix(bind.map(v=>-v))),i*16);
  }
 }
 function gripProfile(n,k){
  if(n.handGrips?.[k])return n.handGrips[k];
  const explicit=Number.isFinite(n.grip),seated=D.clamp(n.seatBlend??(n.seated?1:0),0,1),carry=!!n.carry,reach=n.reach||0;
  const amount=D.clamp(explicit?n.grip:seated>.1?.61:carry?.70:reach>.1?.43:.13+(n.sprintBlend||0)*.18,0,1);
  const style=explicit?'manual':seated>.1?'wheel':carry?'carry':reach>.1?'reach':'relaxed';
  const patterns={manual:[1,1,1,1,1],wheel:[.94,1.05,1.08,1.06,.79],carry:[.75,.90,.98,1.02,.78],reach:[.66,.80,.94,1,.65],relaxed:[.70,1,1.18,1.38,.75]};
  const f={};for(const [j,name]of ['index','middle','ring','little','thumb'].entries()){
   const v=D.clamp(amount*patterns[style][j],0,1);
   f[name]=name==='thumb'?[v*.95,v*.35,v*.20]:[.83*v,1.22*v,.85*v];
  }
  return{amount,style,fingers:f};
 }
 // Author-directed cervical coordination. Radians, no rig scaling or physics mutation.
 function cervicalAngles(n,time,rot,g,seated,p){
  const finite=(v,fallback)=>Number.isFinite(v)?v:fallback;
  const idle=1-g.weight,seed=(n.variant||0)*1.37;
  const torsoPitch=rot.spine[0]+rot.chest[0],torsoRoll=rot.spine[2]+rot.chest[2];
  const turn=finite(n.motion?.turn,n.turnRate||0);
  const yaw=D.clamp(finite(n.lookYaw,p.headYaw*.80+D.clamp(turn,-2,2)*.055*(1-seated)+idle*Math.sin(time*.27+seed)*.018),-.85,.85);
  const pitch=D.clamp(finite(n.lookPitch,0)-torsoPitch*.80+idle*Math.sin(time*.47+seed)*.009,-.34,.40);
  const roll=D.clamp(finite(n.lookRoll,0)-torsoRoll*.75,-.22,.22);
  return {yaw,pitch,roll,neck:[pitch*.35,yaw*.63,roll*.55],head:[pitch*.65,yaw*.37,roll*.45]};
 }
 function groundTargets(n={},time=0){
  const motion=n.motion||{},g=D.NaturalMotion.gait(motion.speed??n.moveSpeed??0,n.sprintBlend,n.crouch);
  const seated=D.clamp(n.seatBlend??(n.seated?1:0),0,1),air=(n.y||0)>.025||Math.abs(n.vy||0)>.05,seed=(n.variant||0)*1.37;
  const breath=Math.sin(time*1.47+seed)*.0017+Math.sin(time*.73+seed*.4)*.0006;
  const feet={L:D.NaturalMotion.foot(n,'L'),R:D.NaturalMotion.foot(n,'R')};
  let rootY=(n.y||0)-.025*g.weight-(n.crouch||0)*.22-(n.dodge||0)*.21-(n.landing||0)*.065;
  if(!air&&seated<.01){
   rootY+=breath*(1-g.weight*.75);
   const bodyRoot=rootY;
   if(!feet.L.contact&&!feet.R.contact)rootY+=.045*g.run*Math.sin(Math.PI*((feet.L.progress+feet.R.progress)%1));
   for(const k of ['L','R']){
    const f=feet[k],lock=motion.feet?.[k],swing=motion.swing?.[k];
    if(lock&&f.contact){const dx=lock.x-(n.x||0),dz=lock.z-(n.z||0),c=Math.cos(n.yaw||0),s=Math.sin(n.yaw||0);f.x=dx*c-dz*s;f.z=dx*s+dz*c;f.yaw=D.wrap(lock.yaw-(n.yaw||0));}
    else if(swing&&!f.contact){
     const c=Math.cos(n.yaw||0),s=Math.sin(n.yaw||0);
     f.x+=(swing.dx*c-swing.dz*s)*swing.weight;
     f.z+=(swing.dx*s+swing.dz*c)*swing.weight;
     f.yaw=D.wrap(swing.yaw-(n.yaw||0))*swing.weight;
    }
    const hip=bones[ids['thigh'+k]][2],horizontal=Math.hypot(f.x-hip[0],f.z);
    // Swing targets must be reachable too. Waiting for heel strike applies
    // the same constraint in one frame and makes the body drop abruptly.
    rootY=Math.min(rootY,f.y+Math.sqrt(Math.max(.08,.850*.850-horizontal*horizontal))-.94-.002);
    if(!f.contact){
     // Prepare the pelvis for the next heel target throughout swing, instead
     // of waiting until the falling foot makes the reach ceiling drop steeply.
     const phase=(motion.phase??n.walk??0)+(1-f.phase)*Math.PI*2+1e-8;
     const landing=D.NaturalMotion.foot({...n,motion:{...motion,phase}},k);
     const reach=Math.hypot(landing.x-hip[0],landing.z);
     const ceiling=landing.y+Math.sqrt(Math.max(.08,.850*.850-reach*reach))-.94-.002;
     rootY=Math.min(rootY,D.lerp(bodyRoot,ceiling,D.NaturalMotion.smooth(0,1,f.progress)));
    }
   }
  }
  rootY=D.lerp(rootY,n.y||0,seated);if(air)rootY=n.y||0;
  return {feet,rootY};
 }
 function pose(n={},time=0){
  const motion=n.motion||{},speed=motion.speed??n.moveSpeed??0,g=D.NaturalMotion.gait(speed,n.sprintBlend,n.crouch);
  const p=D.humanoidPose({phase:motion.phase??n.walk??0,speed,sprint:g.run,y:n.y||0,vy:n.vy||0,turn:(motion.turn??n.turnRate??0)*.13,time,landing:n.landing||0,crouch:n.crouch||0,carry:!!n.carry,reach:n.reach||0,stagger:n.stagger||0,dodge:n.dodge||0});
  const seated=D.clamp(n.seatBlend??(n.seated?1:0),0,1),air=(n.y||0)>.025||Math.abs(n.vy||0)>.05,seed=(n.variant||0)*1.37;
  const breath=Math.sin(time*1.47+seed)*.0017+Math.sin(time*.73+seed*.4)*.0006;
  const support=groundTargets(n,time),feet=support.feet;
  // The tracked recovery stays at or BELOW the reach ceiling, so smoothing
  // cannot make either leg unreachable or move the physical actor/camera.
  const rootY=!air&&seated<.01&&Number.isFinite(motion.supportY)?Math.min(support.rootY,motion.supportY):support.rootY;
  const accel=D.clamp(motion.acceleration||0,-7,7);
  p.spinePitch=D.lerp(p.spinePitch,.065+g.run*.12+(n.crouch||0)*.22+(n.stagger||0)*.25+(n.dodge||0)*.4,g.weight)+accel*.012*g.weight;
  p.spineRoll=-D.clamp((motion.turn??n.turnRate??0)*speed*.012,-.12,.12)*(1-seated);
  const idle=1-g.weight;
  p.shoulderYaw*=1.1;p.pelvisRoll=Math.sin((motion.phase??n.walk??0))*g.weight*.027;
  const rot={pelvis:[0,p.pelvisYaw*.5,p.pelvisRoll*.6],spine:[p.spinePitch*.48,p.shoulderYaw*.27,p.spineRoll*.55],chest:[p.spinePitch*.40,p.shoulderYaw*.48,p.spineRoll*.35],neck:[-p.spinePitch*.40+idle*Math.sin(time*.47+seed)*.012,p.headYaw*.25+idle*Math.sin(time*.27+seed)*.025,-p.spineRoll*.36],head:[-p.spinePitch*.35+idle*Math.sin(time*.33+seed)*.008,p.headYaw*.55,-p.spineRoll*.32]};
  for(const [side,name,k] of [[-1,'left','L'],[1,'right','R']]){
   const q=p[name];let leg=air?{hip:-q.hip-.3,knee:Math.max(.52,q.knee),ankle:0}:{hip:0,knee:0,ankle:0};
   if(!air){const f=feet[k],dy=.94+rootY-f.y,len=D.clamp(Math.hypot(dy,f.z),.09,.8548);const hip=Math.atan2(-f.z,dy)-Math.acos(D.clamp((.445*.445+len*len-.410*.410)/(2*.445*len),-1,1));const knee=Math.PI-Math.acos(D.clamp((.445*.445+.410*.410-len*len)/(2*.445*.410),-1,1));leg={hip,knee,ankle:f.pitch-(hip+knee)};}
   if(!air&&!seated){q.shoulder=Math.cos((motion.phase??n.walk??0)+(side>0?Math.PI:0))*(.22+.35*g.run)*g.weight;q.elbow=.16+g.run*1.03+g.weight*.07;}
   leg={hip:D.lerp(leg.hip,-1.40,seated),knee:D.lerp(leg.knee,1.49,seated),ankle:D.lerp(leg.ankle,-.09,seated)};
   rot['thigh'+k]=[leg.hip,0,0];rot['shin'+k]=[leg.knee,0,0];rot['foot'+k]=[leg.ankle,0,0];
   const reach=Math.max(seated,n.carry?.92:0,n.reach||0),armIdle=idle*(1-reach);
   rot['clavicle'+k]=[0,-side*reach*.035,-side*(.004+reach*.05)+breath*side*.6];
   rot['upperArm'+k]=[D.lerp(q.shoulder,-.83,reach)+armIdle*Math.sin(time*.9+seed+side*.4)*.010,-side*reach*.20,side*(.025+reach*.10+g.run*.025)];
   rot['forearm'+k]=[-D.lerp(q.elbow,.40,reach),0,0];rot['hand'+k]=[reach*.10+armIdle*.04,0,-side*(reach*.14+.04*idle)];
  }
  for(const [b,tgt] of [['spine',[.05,0,0]],['chest',[.025,0,0]],['pelvis',[0,0,0]]])rot[b]=rot[b].map((v,i)=>D.lerp(v,tgt[i],seated));
  rot.spine[0]+=(n.bodyLean||0)*.45;rot.chest[0]+=(n.bodyLean||0)*.4;
  if(n.weaponPose){const w=n.weaponPose;const brace=w.brace||0;rot.spine[1]+=.075*brace;rot.chest[1]+=.185*brace-.025*w.aim*(1-w.reload);rot['clavicleR'][2]-=.020*w.aim;rot['clavicleL'][1]+=.045*w.aim;rot.spine[0]+=.006*brace;rot.chest[0]-=.008*w.kick;}
  if(n.weaponPose?.rifle){
   const weight=D.clamp(n.weaponPose.rifle,0,1);
   rot.spine[2]-=.064*weight;rot.chest[2]-=.096*weight;
   rot.clavicleR[2]+=.12*weight;rot.clavicleL[1]+=.08*weight;
  }
  // A compact neck cannot absorb the same twist in a tiny tissue span. Let the
  // upper torso share deliberate large head turns; the final facing is retained.
  const assist=(n.neckDrop>0&&Number.isFinite(n.lookYaw))?D.clamp(n.lookYaw,-.85,.85)*.34*D.clamp(n.neckDrop/.045,0,1.15)*(1-seated*.45):0;
  rot.spine[1]+=assist*.30;rot.chest[1]+=assist*.70;
  const cervical=cervicalAngles(assist?{...n,lookYaw:n.lookYaw-assist}:n,time,rot,g,seated,p);cervical.torsoAssist=assist;rot.neck=cervical.neck;rot.head=cervical.head;
  const profiles={L:gripProfile(n,'L'),R:gripProfile(n,'R')};
  for(const [side,k]of [[-1,'L'],[1,'R']])for(const f of fingers[k])f.bones.forEach((name,j)=>{
   const value=profiles[k].fingers[f.name][j],grip=profiles[k].amount;
   rot[name]=f.name==='thumb'?[value,side*grip*.06,-side*grip*[.14,.23,.18][j]]:[f.name==='index'&&j===0?(profiles[k].indexLift||0):0,0,-side*value];
  });
  const neckDrop=D.clamp(n.neckDrop||0,0,.06);
  const matrices=evaluate(rot,{chest:[0,breath*(1-seated*.75),breath*.35]},neckDrop),q={neckDrop,matrices,rootY,scale:1,pose:p,cervical,grip:profiles.R.amount,gripStyle:profiles.R.style,feet:{L:null,R:null}};
  if(!air&&seated<.98){for(const k of ['L','R']){if(seated>.01)continue;applyLegTarget(q,k,feet[k]);q.feet[k]=feet[k];}}
  for(const k of ['L','R']){
   const v=profiles[k].thumbOpposition,opposition=Array.isArray(v)&&v.length===3&&v.every(Number.isFinite)?v:null;
   if(n.handTargets?.[k])applyArmTarget(q,n,k,n.handTargets[k]);
   if(n.handTargets?.[k]||opposition)refreshFingers(q,rot,k,opposition);
  }
  return q;
 }
 function applyLegTarget(q,k,f){
  const ai=ids['thigh'+k],bi=ids['shin'+k],fi=ids['foot'+k],a=bones[ai][2],b=bones[bi][2],c=bones[fi][2];
  const hip=transformed(q.matrices.subarray(ai*16,ai*16+16),a),goal=[f.x,f.y-q.rootY,f.z],v=goal.map((x,i)=>x-hip[i]),raw=Math.hypot(...v),dir=v.map(x=>x/Math.max(raw,.0001));
  const l1=.445,l2=.410,d=D.clamp(raw,.09,l1+l2-.0002),pole=[0,0,1],dot=D.dot(dir,pole),ortho=D.normalize(pole.map((x,i)=>x-dot*dir[i]));
  const along=(l1*l1+d*d-l2*l2)/(2*d),height=Math.sqrt(Math.max(0,l1*l1-along*along)),knee=hip.map((x,i)=>x+along*dir[i]+height*ortho[i]),ankle=hip.map((x,i)=>x+d*dir[i]);
  q.matrices.set(alignAt(a,knee.map((x,i)=>x-hip[i]),b.map((x,i)=>x-a[i]),hip),ai*16);
  q.matrices.set(alignAt(b,ankle.map((x,i)=>x-knee[i]),c.map((x,i)=>x-b[i]),knee),bi*16);
  q.matrices.set(multiply(matrix(ankle,f.pitch,f.yaw||0,0),matrix(c.map(x=>-x))),fi*16);
  f.reachError=Math.max(0,raw-d);f.ankle=[ankle[0],ankle[1]+q.rootY,ankle[2]];
 }
 // Analytic arm solve in model space. Targets originate in the action, never in the GPU.
 function transformed(m,p){return [m[0]*p[0]+m[4]*p[1]+m[8]*p[2]+m[12],m[1]*p[0]+m[5]*p[1]+m[9]*p[2]+m[13],m[2]*p[0]+m[6]*p[1]+m[10]*p[2]+m[14]];}
 function alignAt(bind,direction,original,position){
  const a=D.normalize(original),b=D.normalize(direction),axis=D.cross(a,b),c=D.clamp(a.reduce((s,v,i)=>s+v*b[i],0),-1,1),s=Math.hypot(...axis);
  let r=new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]);
  if(s>1e-6){const [x,y,z]=axis.map(v=>v/s),t=1-c;r.set([t*x*x+c,t*x*y+s*z,t*x*z-s*y,0,t*x*y-s*z,t*y*y+c,t*y*z+s*x,0,t*x*z+s*y,t*y*z-s*x,t*z*z+c,0,0,0,0,1]);}
  else if(c<0){r[0]=-1;r[5]=-1;}
  const o=transformed(r,bind);for(let i=0;i<3;i++)r[12+i]=position[i]-o[i];return r;
 }
 function applyArmTarget(q,n,k,target){
  if(![target.x,target.y,target.z].every(Number.isFinite))return;
  const si=Math.sin(n.yaw||0),co=Math.cos(n.yaw||0),dx=target.x-(n.x||0),dz=target.z-(n.z||0),goal=[(dx*co-dz*si)/q.scale,(target.y-q.rootY)/q.scale,(dx*si+dz*co)/q.scale];
  const ai=ids['upperArm'+k],ei=ids['forearm'+k],hi=ids['hand'+k],ab=bones[ai][2],eb=bones[ei][2],hb=bones[hi][2];
  const shoulder=transformed(q.matrices.subarray(ai*16,ai*16+16),ab),vec=goal.map((v,i)=>v-shoulder[i]),len=Math.hypot(...vec);if(len<1e-6)return;
  const l1=Math.hypot(...eb.map((v,i)=>v-ab[i])),l2=Math.hypot(...hb.map((v,i)=>v-eb[i])),d=D.clamp(len,.06,l1+l2-.002),dir=vec.map(v=>v/len),pole=target.pole&&target.pole.length===3&&target.pole.every(Number.isFinite)?target.pole:[k==='L'?-1:1,-.2,-.4];
  const dot=pole.reduce((s,v,i)=>s+v*dir[i],0);let perp=pole.map((v,i)=>v-dot*dir[i]);if(Math.hypot(...perp)<.0001)perp=D.cross(dir,[0,1,0]);perp=D.normalize(perp);
  const along=(l1*l1+d*d-l2*l2)/(2*d),height=Math.sqrt(Math.max(0,l1*l1-along*along)),elbow=shoulder.map((v,i)=>v+dir[i]*along+perp[i]*height),hand=shoulder.map((v,i)=>v+dir[i]*d);
  q.matrices.set(alignAt(ab,elbow.map((v,i)=>v-shoulder[i]),eb.map((v,i)=>v-ab[i]),shoulder),ai*16);
  const fore=alignAt(eb,hand.map((v,i)=>v-elbow[i]),hb.map((v,i)=>v-eb[i]),elbow);q.matrices.set(fore,ei*16);
  let wrist=new Float32Array(fore);
  const requested=target.orientation;
  if(requested&&[...(requested.palm||[]),...(requested.fingers||[])].length===6&&[...requested.palm,...requested.fingers].every(Number.isFinite)){
   const local=v=>[v[0]*co-v[2]*si,v[1],v[0]*si+v[2]*co];
   const side=k==='R'?1:-1,palm=D.normalize(local(requested.palm)),finger=D.normalize(local(requested.fingers));
   let x=palm.map(v=>-side*v),y=finger.map(v=>-v),z=D.cross(x,y);
   if(Math.hypot(...z)>.001){
    z=D.normalize(z);y=D.normalize(D.cross(z,x));x=D.normalize(x);
    // Spread a bounded axial twist through the forearm instead of putting all roll at the wrist.
    const axis=D.normalize(hand.map((v,i)=>v-elbow[i]));
    const project=v=>{const d=D.dot(v,axis);return v.map((x,i)=>x-d*axis[i]);};
    const initial=project([-side*fore[0],-side*fore[1],-side*fore[2]]),desired=project(palm);
    let twist=0;
    if(Math.hypot(...initial)>.001&&Math.hypot(...desired)>.001){
     const a=D.normalize(initial),b=D.normalize(desired);twist=D.clamp(Math.atan2(D.dot(axis,D.cross(a,b)),D.dot(a,b)),-1.7,1.7)*.72;
     const [ax,ay,az]=axis,c=Math.cos(twist),sn=Math.sin(twist),t=1-c;
     const r=new Float32Array([t*ax*ax+c,t*ax*ay+sn*az,t*ax*az-sn*ay,0,t*ax*ay-sn*az,t*ay*ay+c,t*ay*az+sn*ax,0,t*ax*az+sn*ay,t*ay*az-sn*ax,t*az*az+c,0,0,0,0,1]);
     const turned=multiply(r,fore),at=transformed(turned,eb);for(let i=0;i<3;i++)turned[12+i]+=elbow[i]-at[i];q.matrices.set(turned,ei*16);
    }
    wrist=new Float32Array([...x,0,...y,0,...z,0,0,0,0,1]);
    q.handContacts=q.handContacts||{};q.handContacts[k]={reachError:Math.max(0,len-d),twist,orientationError:Math.hypot(...y.map((v,i)=>v+finger[i]))};
   }
  }
  const origin=transformed(wrist,hb);for(let i=0;i<3;i++)wrist[12+i]+=hand[i]-origin[i];q.matrices.set(wrist,hi*16);
 }
 function handPoint(q,n,k){const p=transformed(q.matrices.subarray(ids['hand'+k]*16,ids['hand'+k]*16+16),bones[ids['hand'+k]][2]).map(v=>v*q.scale),c=Math.cos(n.yaw||0),s=Math.sin(n.yaw||0);return{x:(n.x||0)+p[0]*c+p[2]*s,y:q.rootY+p[1],z:(n.z||0)-p[0]*s+p[2]*c};}
 function palmPoint(q,n,k){
  const bind=bones[ids['hand'+k]][2],offset=D.WeaponHandling?.palmLandmark(k)||[k==='L'?.013:-.013,-.049,0];
  const local=bind.map((v,i)=>v+offset[i]),m=q.matrices.subarray(ids['hand'+k]*16,ids['hand'+k]*16+16),p=transformed(m,local).map(v=>v*q.scale),c=Math.cos(n.yaw||0),s=Math.sin(n.yaw||0);
  return{x:(n.x||0)+p[0]*c+p[2]*s,y:q.rootY+p[1],z:(n.z||0)-p[0]*s+p[2]*c};
 }
 function validate(data){
  if(!(data instanceof Float32Array)||data.length===0||data.length%16)throw new Error('Invalid weighted vertex layout');
  for(let i=0;i<data.length;i+=16){
   for(let k=0;k<16;k++)if(!Number.isFinite(data[i+k]))throw new Error('Nonfinite vertex');
   if(Math.abs(Math.hypot(data[i+3],data[i+4],data[i+5])-1)>.03)throw new Error('Nonunit normal');
   let sum=0;for(let j=0;j<4;j++){const joint=data[i+8+j],weight=data[i+12+j];if(joint<0||joint>=bones.length||joint!==Math.floor(joint))throw new Error('Invalid joint');if(weight<0||weight>1)throw new Error('Invalid weight');sum+=weight;}
   if(Math.abs(sum-1)>.001)throw new Error('Weights must sum to one');
  }return true;
 }
 function blink(time,seed=0){const period=3.7+seed*.8,t=((time+seed*7.31)%period+period)%period;if(t>.17)return 0;const f=1-Math.abs(t-.085)/.085;return f*f*(3-2*f);}
 D.SkinRig={bones,ids,fingers,paletteWidth:bones.length*4,paletteStride:bones.length*16,blink,gripProfile,cervicalAngles,rest:()=>evaluate(),evaluate,transform:transformed,groundTargets,pose,validate,matrix,multiply,handPoint,palmPoint};
})(DC);
