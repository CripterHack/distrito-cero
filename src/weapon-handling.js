/* Coordinated fictional game-prop contacts, v0.19.
 * Surface anchors, wrist landmarks and visible pieces use the same rigid frame.
 * Pure mounting reads. Animation springs are transient and never enter saves.
 * These are artistic animation fixtures, not weapon engineering data. */
'use strict';
(function(D){
 const clamp=D.clamp,lerp=D.lerp;
 const sm=(a,b,x)=>{const t=clamp((x-a)/(b-a),0,1);return t*t*(3-2*t);};
 const mix=(a,b,t)=>a.map((v,i)=>lerp(v,b[i],t));
 const vec=p=>({x:p[0],y:p[1],z:p[2]});
 const add=(a,b)=>a.map((v,i)=>v+b[i]);
 const sub=(a,b)=>a.map((v,i)=>v-b[i]);
 // Palm-side contact reference relative to the existing neutral wrist joint.
 // Mirrored X is the palm thickness. Negative Y runs from wrist into palm.
 const palmLandmark=k=>[k==='L'?.013:-.013,-.049,0];
 const PRIMARY={p:[.031,-.107,-.030],palm:[-1,0,0],fingers:[0,-.10,.994987]};
 const SUPPORT={p:[-.003,-.047,.224],palm:[0,1,0],fingers:[.84,0,.542586]};
 const profiles={
  unarmed:{family:'none'},
  pistol:{family:'sidearm',support:{p:[-.040,-.113,-.037],palm:[1,0,0],fingers:[0,-.10,.994987]},reload:'magazine'},
  revolver:{family:'sidearm',support:{p:[-.040,-.116,-.036],palm:[1,0,0],fingers:[0,-.10,.994987]},reload:'cylinder'},
  smg:{family:'long',support:SUPPORT,reload:'magazine'},
  rifle:{family:'long',support:SUPPORT,reload:'magazine'},
  shotgun:{family:'long',support:{...SUPPORT,p:[-.003,-.080,.223]},reload:'port'},
  sniper:{family:'long',support:SUPPORT,reload:'magazine'},
  gauss:{family:'heavy',support:{...SUPPORT,p:[-.006,-.092,.240]},reload:'magazine'},
  emp:{family:'heavy',support:{...SUPPORT,p:[-.006,-.090,.230]},reload:'magazine'},
  launcher:{family:'heavy',support:{...SUPPORT,p:[-.006,-.062,.240]},reload:'port'},
  baton:{family:'melee',primary:{p:[.031,0,-.080],palm:[-1,0,0],fingers:[0,0,1]}},
  blade:{family:'melee',primary:{p:[.025,0,-.080],palm:[-1,0,0],fingers:[0,0,1]}},
  grenade:{family:'throw',primary:{p:[.056,.020,.015],palm:[-1,0,0],fingers:[0,-1,0]}},
  // Compact near-face optics need forward/downward elbows. The generic rear pole
  // nearly opposes the raised wrist direction when crouching and flips the IK plane.
  binoculars:{family:'optics',elbows:{L:[-.5,-.25,1],R:[.5,-.25,1]},primary:{p:[.113,-.020,.018],palm:[-1,0,0],fingers:[0,.20,.979796]},support:{p:[-.113,-.020,.018],palm:[1,0,0],fingers:[0,.20,.979796]}}
 };
 function freeze(o){Object.values(o).forEach(v=>{if(v&&typeof v==='object'&&!Object.isFrozen(v))freeze(v);});return Object.freeze(o);}
 freeze(profiles);
 const profile=id=>profiles[id]||profiles.unarmed;
 function frame(palm,fingers){
  const p=D.normalize(palm),dot=D.dot(p,fingers);
  let f=sub(fingers,p.map(v=>v*dot));
  if(Math.hypot(...f)<1e-6)f=D.cross(p,Math.abs(p[1])<.8?[0,1,0]:[0,0,1]);
  return{palm:p,fingers:D.normalize(f)};
 }
 function palmOffset(k,orientation){
  const side=k==='R'?1:-1,x=orientation.palm.map(v=>-side*v),y=orientation.fingers.map(v=>-v),z=D.cross(x,y),a=palmLandmark(k);
  return x.map((v,i)=>v*a[0]+y[i]*a[1]+z[i]*a[2]);
 }
 function spring(x,v,omega,dt){const b=v+omega*x,d=Math.exp(-omega*dt);return[(x+b*dt)*d,(v-omega*b*dt)*d];}
 function beginEquip(sim){const e=sim.equipment;return e.handling={item:e.selected,serial:e.shotSerial||0,kick:0,velocity:0,ready:0,triggerWeight:0,lagYaw:0,lagPitch:0,velYaw:0,velPitch:0,lastYaw:sim.player.yaw||0,lastPitch:e.pitch||0};}
 function step(sim,dt){
  if(!Number.isFinite(dt)||dt<=0)return;
  const e=sim.equipment;if(!e)return;dt=Math.min(dt,.25);
  const fam=profile(e.selected).family,omega=fam==='heavy'?19:fam==='sidearm'?25:22;
  let h=e.handling;
  if(!h||h.item!==e.selected)h=beginEquip(sim);
  if(h.serial!==(e.shotSerial||0)){h.serial=e.shotSerial||0;h.velocity=Math.min(65,h.velocity+(fam==='heavy'?40:fam==='sidearm'?37:31));}
  [h.kick,h.velocity]=spring(h.kick,h.velocity,omega,dt);
  h.ready=D.damp(h.ready,1,11,dt);
  const trigger=!e.reloading&&(e.trigger||e.recoil>.72)?1:0;h.triggerWeight=D.damp(h.triggerWeight||0,trigger,trigger?40:22,dt);
  const yaw=sim.player.yaw||0,pitch=e.pitch||0,dy=D.wrap(yaw-(h.lastYaw??yaw)),dp=pitch-(h.lastPitch??pitch);
  if(Math.abs(dy)>1.2||Math.abs(dp)>1){h.lagYaw=h.lagPitch=h.velYaw=h.velPitch=0;}
  else{
   h.lagYaw=clamp((h.lagYaw||0)-dy*.10,-.045,.045);h.lagPitch=clamp((h.lagPitch||0)-dp*.09,-.035,.035);
   [h.lagYaw,h.velYaw]=spring(h.lagYaw,h.velYaw||0,17,dt);[h.lagPitch,h.velPitch]=spring(h.lagPitch,h.velPitch||0,18,dt);
  }
  h.lastYaw=yaw;h.lastPitch=pitch;
 }
 function actor(n,m,e){return{...n,neckDrop:m.neckDrop??n.neckDrop??0,handTargets:m.hands,handGrips:m.grips,
  weaponPose:{aim:m.aim,reload:m.reload,family:m.family,kick:m.kick,brace:m.braceWeight||0},reach:.72,
  bodyLean:m.aim*.020-m.kick*.022,lookYaw:-(m.braceWeight||0)*.235,lookPitch:-(e.pitch||0)*.50+m.aim*.025};}
 function mount(sim,actorOverride=null){
  const p=actorOverride||sim.player,e=sim.equipment,w=D.Equipment.get(e.selected)||D.Equipment.get('unarmed'),spec=profile(w.id),family=spec.family;
  const aim=clamp(e.aimWeight||0,0,1),time=sim.time||0,speed=clamp(p.motion?.speed??p.moveSpeed??0,0,6),phase=p.motion?.phase??p.walk??0;
  const state=e.handling?.item&&e.handling.item!==w.id?null:e.handling;
  const kick=clamp(state?.kick??(e.recoil||0)*.45,0,1.3),ready=clamp(state?.ready??1,0,1);
  const t=e.reloading>0&&w.reload?clamp(1-e.reloading/w.reload,0,1):0;
  const reload=sm(0,.16,t)*(1-sm(.82,1,t)),contact=sm(.045,.24,t)*(1-sm(.84,1,t));
  const heavy=family==='heavy',optic=family==='optics',sidearm=family==='sidearm',melee=family==='melee',thrown=family==='throw',long=family==='long'||heavy;
  const braceWeight=long?aim*(1-reload*.82)*ready:0;
  const gait=clamp(speed/4,0,1)*(1-aim*.90)*(1-reload),sway=Math.sin(phase)*.007*gait;
  const inertia={yaw:(state?.lagYaw||0)*(1-aim*.7),pitch:(state?.lagPitch||0)*(1-aim*.7)};
  const eye=1.670-(D.CharacterFit?.drop(sim.appearance?.neckLength)||.045);
  const pos=[optic?0:sidearm?.045:melee||thrown?.22:.12,
   (p.y||0)+(optic?lerp(1.27,eye-.012,aim):melee||thrown?1.06:lerp(1.285,sidearm?1.505:1.37,aim))-(p.crouch||0)*.22,
   optic?lerp(.22,.135,aim):sidearm?lerp(.24,.515,aim):melee||thrown?.22:lerp(.145,.235,aim)];
  pos[0]+=sway;pos[1]+=Math.sin(time*1.47)*.0014+Math.cos(phase*2)*.003*gait-(1-ready)*.06-reload*(sidearm?.11:.035);
  pos[2]-=kick*(heavy?.023:.012)+reload*(sidearm?.11:.075)+(1-ready)*.05;
  const yaw=(p.yaw||0)+sway*.3+inertia.yaw;
  const pitch=(optic?(e.pitch||0)*aim:melee?-.30+kick*.9:thrown?-.26+kick*1.2:lerp(-.34,e.pitch||0,aim))+kick*(heavy?.050:.035)-reload*.25-(1-ready)*.18+inertia.pitch;
  const roll=reload*(sidearm?-.22:-.14)+Math.sin(phase+.35)*.014*gait;
  const cy=Math.cos(yaw),sy=Math.sin(yaw),cx=Math.cos(-pitch),sx=Math.sin(-pitch),cz=Math.cos(roll),sz=Math.sin(roll);
  function direction(q){const x=q[0],y=q[1]*cx-q[2]*sx,z=q[1]*sx+q[2]*cx,xx=x*cz-y*sz,yy=x*sz+y*cz;return[xx*cy+z*sy,yy,-xx*sy+z*cy];}
  const c=Math.cos(p.yaw||0),s=Math.sin(p.yaw||0);
  let origin=[(p.x||0)+pos[0]*c+pos[2]*s,pos[1],(p.z||0)-pos[0]*s+pos[2]*c];
  // Derive the brace from the same procedural torso before its arm IK is solved.
  const neckDrop=D.CharacterFit?.drop(sim.appearance?.neckLength)||.045;
  const poseInfo={aim,reload,kick,family,braceWeight,neckDrop},posed=D.SkinRig&&D.NaturalMotion?D.SkinRig.pose(actor(p,poseInfo,e),time):null;
  const shoulders={};
  for(const k of['L','R']){
   const bind=D.SkinRig?.bones[D.SkinRig.ids['upperArm'+k]]?.[2]||[k==='L'?-.2115:.2115,1.435,0];
   const q=posed?D.SkinRig.transform(posed.matrices.subarray(D.SkinRig.ids['upperArm'+k]*16,D.SkinRig.ids['upperArm'+k]*16+16),bind):bind;
   shoulders[k]=[(p.x||0)+q[0]*c+q[2]*s,q[1]+(posed?.rootY??((p.y||0)-(p.crouch||0)*.22)),(p.z||0)-q[0]*s+q[2]*c];
  }
  const stock=[0,-.012,-.238],shoulderTarget=add(shoulders.R,[.010*c+.024*s,-.040,-.010*s+.024*c]);
  if(long){const planted=sub(shoulderTarget,direction(stock));origin=mix(origin,planted,braceWeight);origin=add(origin,direction([0,0,-kick*.007*braceWeight]));}
  const pull=sm(.27,.46,t)*(1-sm(.62,.80,t));
  const detached=spec.reload==='magazine'&&reload>0;
  const magazine={offset:detached?[-.025*pull,-.211*pull,.025*pull]:[0,0,0],rotation:[0,0,detached?-.23*pull:0],
   pivot:sidearm?[0,-.18,-.016]:[0,-.135,.12],surface:sidearm?[-.030,-.180,-.018]:[-.031,-.145,.12],attachedToHand:detached&&t>=.24&&t<=.84};
  function partLocal(role,q){if(role!=='magazine')return q.slice();const z=magazine.rotation[2],co=Math.cos(z),si=Math.sin(z),v=sub(q,magazine.pivot);return add(add([v[0]*co-v[1]*si,v[0]*si+v[1]*co,v[2]],magazine.pivot),magazine.offset);}
  const localRotate=(role,q)=>{if(role!=='magazine')return q.slice();const z=magazine.rotation[2],c=Math.cos(z),s=Math.sin(z);return[q[0]*c-q[1]*s,q[0]*s+q[1]*c,q[2]];};
  const contacts={R:spec.primary||PRIMARY};let support=spec.support;
  if(reload&&support){
   const z=spec.reload==='cylinder'?.078:spec.reload==='port'?.22:sidearm?-.018:.12;
   const surface=spec.reload==='magazine'?partLocal('magazine',magazine.surface):[-.051,-.105,z];
   if(spec.reload==='port')surface[1]-=.045*Math.sin(Math.PI*sm(.2,.82,t));
   const orientation=frame(localRotate('magazine',[1,0,0]),localRotate('magazine',[0,-.10,.994987]));
   support={p:mix(support.p,surface,contact),...frame(mix(support.palm,orientation.palm,contact),mix(support.fingers,orientation.fingers,contact))};
  }
  if(support)contacts.L=support;
  const localHands={},orientations={};
  for(const [k,v]of Object.entries(contacts))if(family!=='none'){const f=frame(v.palm,v.fingers);orientations[k]=f;localHands[k]=sub(v.p,palmOffset(k,f));}
  // Project a rigid mount into both reach spheres. No limb is scaled to reach a prop.
  // The constraint takes precedence over a rigid shoulder brace at extreme angles.
  let fitDistance=0;
  if(posed&&family!=='none')for(let pass=0;pass<5;pass++)for(const k of Object.keys(localHands)){
   const hand=add(origin,direction(localHands[k])),delta=sub(hand,shoulders[k]),len=Math.hypot(...delta),limit=.547;
   if(len>limit){const d=(len-limit);const correction=delta.map(v=>-v/len*d);origin=add(origin,correction);fitDistance+=d;}
  }
  const point=(x,y,z)=>add(origin,direction([x,y,z]));
  function socket(k){const local=localHands[k],o=orientations[k];return{...vec(point(...local)),orientation:frame(direction(o.palm),direction(o.fingers)),pole:spec.elbows?.[k]||(k==='L'?[-.72,-1,-.18]:[.60,-1,-.30])};}
  const hands={},palmContacts={},grips={};
  for(const k of Object.keys(localHands)){hands[k]=socket(k);palmContacts[k]={...vec(point(...contacts[k].p)),local:contacts[k].p.slice()};}
  const trigger=Number.isFinite(state?.triggerWeight)?clamp(state.triggerWeight,0,1):(!e.reloading&&(e.trigger||e.recoil>.72))?1:0;
  function grip(amount,style){
   const f={};for(const name of['index','middle','ring','little','thumb']){
    const v=clamp(amount*(name==='little'?1.05:name==='ring'?1.025:1),0,.94);
    f[name]=name==='thumb'?[v*.86,v*.34,v*.23]:[v*.97,v*1.36,v*.86];
   }
   if(style==='primary')f.index=mix([.10,.12,.08],[.43,.67,.30],trigger);
   return{amount,style,fingers:f,indexLift:style==='primary'?lerp(-.10,.035,trigger):0};
  }
  grips.R=grip(optic?.38:melee?.78:thrown?.63:.76,optic?'optics':melee?'melee':thrown?'throw':'primary');
  if(hands.L){const freeTravel=sm(.035,.13,t)*(1-sm(.20,.29,t))+sm(.84,.89,t)*(1-sm(.94,1,t));const holding=lerp(optic?.38:sidearm?.61:heavy?.53:.52,.70,contact);grips.L=grip(lerp(holding,.16,clamp(freeTravel,0,1)),reload?'reload':optic?'optics':sidearm?'wrap':'support');}
  function partPoint(role,q){return point(...partLocal(role,q));}
  function partTransform(role){
   if(role!=='magazine'||!magazine.rotation[2])return{origin:partPoint(role,[0,0,0]),rx:-pitch,yaw,roll};
   const x=direction(localRotate(role,[1,0,0])),y=direction(localRotate(role,[0,1,0])),z=direction(localRotate(role,[0,0,1]));
   return{origin:partPoint(role,[0,0,0]),roll:Math.asin(clamp(x[1],-1,1)),rx:Math.atan2(-z[1],y[1]),yaw:Math.atan2(-x[2],x[0])};
  }
  const brace=long?{weight:braceWeight,target:shoulderTarget,stock:point(...stock),error:Math.hypot(...sub(point(...stock),shoulderTarget))}:null;
  const reloadStage=!reload?'':t<.24?'Buscar agarre':t<.57?'Extraer':t<.82?'Insertar':t<.90?'Asentar':'Recuperar apoyo';
  return{point,direction,partPoint,partTransform,yaw,pitch,roll,origin,hands,palmContacts,grips,magazine,reloadContact:contact,reload,reloadStage,aim,kick,ready,family,inertia,brace,braceWeight,fitDistance,neckDrop,
   phase:reload?'Recargar':optic?(aim>.5?'Observar':'Transportar'):kick>.12?(melee?'Golpear':thrown?'Lanzar':'Recuperar'):aim>.5?'Apuntar':'Guardia baja',
   muzzle:point(0,.012,w.length||.3),supportLocal:support?.p.slice()||null};
 }
 D.WeaponHandling=Object.freeze({profile,step,beginEquip,mount,actor,palmLandmark});
})(DC);
