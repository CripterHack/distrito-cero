/* v0.8 — Seat ownership, cancellable paired actions, persistent driver identity.
   All gameplay state belongs here. Rendering consumes poses, never transfers control. */
'use strict';
(function(D){
 const Base=D.Simulation, clamp=D.clamp, mix=D.lerp, ease=t=>{t=clamp(t,0,1);return t*t*(3-2*t);};
 const SKINS=[[.46,.28,.185],[.29,.16,.105],[.61,.42,.295],[.39,.23,.16],[.68,.49,.36]];
 const COATS=[[.16,.23,.21],[.24,.12,.075],[.18,.19,.26],[.20,.23,.27],[.29,.25,.17]];
 D.carPoint=(c,x,z)=>({x:c.x+x*Math.cos(c.yaw)+z*Math.sin(c.yaw),z:c.z-x*Math.sin(c.yaw)+z*Math.cos(c.yaw)});
 // Shared cabin landmarks: the wrist sits behind the rim, allowing the palm to wrap it.
 D.VehicleCabin=Object.freeze({wheel:Object.freeze({x:-.38,y:.995,z:.31,tilt:-.48,radius:.155}),hands(c){
  const angle=D.clamp((c.steerAngle||0)*1.25,-.58,.58),w=this.wheel,out={};
  for(const [k,side]of [['L',-1],['R',1]]){const x=side*.147*Math.cos(angle),yy=side*.147*Math.sin(angle),q=D.carPoint(c,w.x+x+side*.010,w.z+yy*Math.sin(w.tilt)-.080);out[k]={...q,y:w.y+yy*Math.cos(w.tilt)+.024};}return out;
 }});
 D.driverProfile=c=>({id:'driver:'+c.id,police:!!c.police,skin:SKINS[Math.abs(c.id)%SKINS.length].slice(),coat:(c.police?[.026,.048,.094]:COATS[Math.abs(c.id)%COATS.length]).slice(),variant:Math.abs(c.id)%9});
 const copyDriver=d=>d?{...d,skin:[...d.skin],coat:[...d.coat]}:null;
 function pointOnPath(path,t){
  const lengths=path.slice(1).map((p,i)=>D.distance(path[i],p));let remaining=clamp(t,0,1)*lengths.reduce((a,b)=>a+b,0);
  for(let i=0;i<lengths.length;i++){const length=lengths[i];if(remaining<=length||i===lengths.length-1){const f=length?clamp(remaining/length,0,1):1,a=path[i],b=path[i+1];return{x:mix(a.x,b.x,f),z:mix(a.z,b.z,f),yaw:Math.atan2(b.x-a.x,b.z-a.z)};}remaining-=length;}
  return{...path[path.length-1],yaw:0};
 }
 class OccupancySimulation extends Base{
  constructor(world){
   super(world);this.access=null;this.accessSerial=0;this.driverEvents=new Set();
   for(const c of this.cars){c.driver=c.owned||c.parked?null:D.driverProfile(c);c.boarding=false;c.doorOpen=0;}
   for(let i=0;i<this.peds.length;i++)Object.assign(this.peds[i],{personId:'ped:'+i,variant:i%9});
  }
  clearance(q,c,includeTarget=false){
   if(this.world.blocked(q.x,q.z,.38))return false;
   if(this.cars.some(o=>(includeTarget||o!==c)&&D.vehicleContains(o,q.x,q.z,.38)))return false;
   return !this.dynamics.hash.query(q.x,q.z,1.5).some(o=>!o.broken&&!o.held&&D.distance(q,o)<Math.min(o.radius||.2,.8)+.32);
  }
  pathToDoor(c){
   const p=this.player,from={x:p.x,z:p.z},end=D.carPoint(c,-1.85,.15),evict=D.carPoint(c,-2.8,-.50);
   if(!this.clearance(end,c)||c.driver&&(!this.clearance(evict,c)||!this.clearance(D.carPoint(c,-3.60,.25),c)||!this.clearance(D.carPoint(c,-2.9,.9),c)))return null;
   const candidates=[[from,end]];
   for(const front of [3.1,-3.1])candidates.push([from,D.carPoint(c,2.15,front),D.carPoint(c,-2.15,front),end],[from,D.carPoint(c,-2.15,front),end]);
   const valid=candidates.filter(path=>path.every((v,i)=>{
    if(!i)return true;const u=path[i-1],steps=Math.ceil(D.distance(u,v)/.19);
    for(let j=1;j<=steps;j++){const q={x:mix(u.x,v.x,j/steps),z:mix(u.z,v.z,j/steps)};if(!this.clearance(q,c,true))return false;}return true;
   }));
   valid.sort((a,b)=>a.slice(1).reduce((s,p,i)=>s+D.distance(p,a[i]),0)-b.slice(1).reduce((s,p,i)=>s+D.distance(p,b[i]),0));
   return valid[0]||null;
  }
  startAccess(){
   const p=this.player,exiting=p.car!==null,index=exiting?p.car:this.nearestCar();if(index<0)return;
   const c=this.cars[index];
   if(Math.abs(c.speed)>2.5||p.y>.02){this.emit('toast','El coche debe estar casi detenido y tus pies sobre el suelo.');return;}
   const door=D.carPoint(c,-1.85,.15);const path=exiting?null:this.pathToDoor(c);
   if(!this.clearance(door,c)||(!exiting&&!path)){this.emit('toast','No hay espacio libre junto a la puerta del conductor.');return;}
   if(p.carry)this.dropHeld();
   const approach=exiting?0:Math.max(.16,path.slice(1).reduce((s,v,i)=>s+D.distance(v,path[i]),0)/2.9);
   const kind=exiting?'exit':c.driver?'extract':'enter';
   const opening=.38,pulling=kind==='extract'?1.40:0,returning=kind==='extract'?.9:0,entry=1.05,closing=.34;
   this.access={serial:++this.accessSerial,kind,index,c,elapsed:0,duration:approach+opening+pulling+returning+entry+closing,approach,opening,pulling,returning,entry,closing,door,path,driver:copyDriver(c.driver),released:false,reported:false,wasParked:c.parked,from:{x:p.x,z:p.z,yaw:p.yaw},lastSafe:{x:p.x,z:p.z},anchor:{x:c.x,z:c.z,yaw:c.yaw}};
   c.boarding=true;c.doorOpen=0;c.doorSide=-1;c.speed=0;p.vx=p.vz=0;p.transition=null;p.moveSpeed=0;this.repairProgress=0;
   this.emit('sound','door');
  }
  interact(kind='car'){
   if(kind==='car'){if(this.access)this.cancelAccess();else this.startAccess();return;}
   if(this.access)return;super.interact(kind);
  }
  cancelAccess(silent=false){
   const a=this.access;if(!a)return;const p=this.player,c=a.c;
   c.boarding=false;c.doorOpen=0;c.parked=a.released?true:a.wasParked;
   if(a.kind!=='exit'){
    p.car=null;const candidates=[a.lastSafe,a.door,a.from,D.carPoint(c,-3.0,.1),D.carPoint(c,-2.2,-3.1)];
    const safe=candidates.find(q=>this.clearance(q,c,true));if(safe){p.x=safe.x;p.z=safe.z;}
   }else{p.car=a.index;p.x=c.x;p.z=c.z;}
   p.y=0;p.vy=0;p.vx=p.vz=0;p.transition=null;p.moveSpeed=0;p.actualSpeed=0;this.access=null;
   if(!silent)this.emit('toast','Interacción cancelada.');
  }
  walk(dt,input){if(this.access){this.player.vx=this.player.vz=0;return;}super.walk(dt,input);}
  drive(c,dt,input){if(this.access&&this.access.c===c){c.speed=0;return;}super.drive(c,dt,input);}
  traffic(c,dt){if(c.boarding){c.speed=0;return;}if(c.driver===null&&!c.pushedUntil)c.parked=true;super.traffic(c,dt);}
  repairStep(dt,input){if(this.access){this.repairProgress=0;return;}super.repairStep(dt,input);}
  recyclePopulation(){
   // Never recycle a car whose ownership/occupancy changed. Base traffic remains bounded.
   const protectedCars=this.cars.filter(c=>c.stolen||c.driver===null),flags=protectedCars.map(c=>c.boarding);
   protectedCars.forEach(c=>c.boarding=true);super.recyclePopulation();protectedCars.forEach((c,i)=>c.boarding=flags[i]);
  }
  releaseDriver(a){
   if(a.released)return;a.released=true;const c=a.c,id=a.driver.id;c.driver=null;c.parked=true;c.stolen=true;
   if(this.peds.some(n=>n.personId===id))return;
   const q=D.carPoint(c,-2.8,-.50);
   this.peds.push({...copyDriver(a.driver),personId:id,...q,y:0,yaw:c.yaw-Math.PI*.56,phase:0,walk:0,moveSpeed:0,speed:1.4,panic:6,homeZ:Math.floor(q.z/84)*84,reactUntil:this.time+1.1,evicted:true});
   const old=this.peds.filter(n=>n.evicted);if(old.length>24){const remove=old.sort((x,y)=>D.distance(y,this.player)-D.distance(x,this.player))[0];this.peds=this.peds.filter(n=>n!==remove);}
   this.emit('sound','door');
  }
  completeAccess(a){
   const p=this.player,c=a.c;
   if(a.kind==='exit'){p.car=null;p.x=a.door.x;p.z=a.door.z;p.yaw=c.yaw-Math.PI*.55;c.parked=true;}
   else{
    p.car=a.index;p.x=c.x;p.z=c.z;p.yaw=c.yaw;c.parked=false;c.driver=null;
    if(!c.owned&&!c.stolen)this.addHeat(c.police?38:16);c.stolen=c.stolen||!c.owned;
    if(this.story===1&&!this.free&&c.id===0){this.story=2;this.pin=null;this.emit('chapter','CARGA SENSIBLE');this.emit('toast','LÍA · Recoge el archivo en el Taller del Mercado.');}
   }
   c.speed=0;c.boarding=false;c.doorOpen=0;p.transition=null;p.y=0;p.vy=0;p.vx=p.vz=0;p.moveSpeed=0;p.actualSpeed=0;this.access=null;
   this.emit('sound','door');this.emit('save','');
  }
  step(dt,input={}){
   if(!Number.isFinite(dt)||dt<=0)return;
   const count=Math.ceil(Math.min(dt,.25)*60),h=Math.min(dt,.25)/count;
   for(let i=0;i<count;i++){
    let a=this.access;
    if(a){
     if(Math.abs(input.throttle||0)>.15||Math.abs(input.steer||0)>.15||input.brake||input.surrender||D.distance(a.c,a.anchor)>.65||Math.abs(D.wrap(a.c.yaw-a.anchor.yaw))>.2)this.cancelAccess();
     else{
      a.elapsed+=h;const t=a.elapsed-a.approach,open=ease(t/a.opening),close=ease((a.elapsed-a.duration+a.closing)/a.closing);
      a.c.doorOpen=open*(1-close);a.c.speed=0;
      if(a.kind!=='exit'){
       if(a.elapsed<a.approach){const q=pointOnPath(a.path,a.elapsed/a.approach);this.player.walk+=D.distance(this.player,q)*(D.NaturalMotion?D.NaturalMotion.distanceRate(2.9):4.8);Object.assign(this.player,q,{moveSpeed:2.9});if(this.clearance(q,a.c,true))a.lastSafe={x:q.x,z:q.z};}
       else{this.player.x=a.door.x;this.player.z=a.door.z;this.player.moveSpeed=0;this.player.yaw=Math.atan2(a.c.x-a.door.x,a.c.z-a.door.z);a.lastSafe={...a.door};}
       if(a.kind==='extract'&&t>=a.opening+.25&&!a.reported){a.reported=true;this.addHeat(a.c.police?38:16);this.emit('toast',a.c.police?'Alerta policial: intento de sustracción de patrulla.':'El conductor está dando la alarma.');}
       if(a.kind==='extract'&&t>=a.opening+a.pulling)this.releaseDriver(a);
      }
     }
    }
    super.step(h,input);a=this.access;
    if(a&&D.distance(a.c,a.anchor)>.65){this.cancelAccess();continue;}
    if(a&&a.elapsed>=a.duration){if(a.kind==='exit'&&!this.clearance(a.door,a.c)){this.cancelAccess();this.emit('toast','La salida quedó obstruida.');}else this.completeAccess(a);}
   }
  }
  pedestrians(dt){
   const evicted=this.peds.filter(n=>n.evicted),oldHidden=evicted.map(n=>n.hidden);evicted.forEach(n=>n.hidden=true);super.pedestrians(dt);
   evicted.forEach((n,i)=>{
    n.hidden=oldHidden[i];if(D.distance(n,this.player)>145)return;
    if(this.time<n.reactUntil){n.moveSpeed=0;n.crouch=.4;n.stagger=.35;return;}n.crouch=0;n.stagger=0;
    n.panic=Math.max(0,n.panic-dt);const speed=n.panic>0?3.0:1.25;let yaw=n.yaw;
    if(n.panic>0&&D.distance(n,this.player)<25)yaw=Math.atan2(n.x-this.player.x,n.z-this.player.z);
    n.yaw=D.turn(n.yaw,yaw,dt*6);const q=this.world.move(n.x,n.z,Math.sin(n.yaw)*speed*dt,Math.cos(n.yaw)*speed*dt,.36);
    if(this.cars.some(c=>D.vehicleContains(c,q.x,q.z,.35))){n.yaw+=dt*2;n.moveSpeed=0;return;}
    const dist=D.distance(n,q);Object.assign(n,q);n.moveSpeed=dist/dt;n.walk=(n.walk||0)+dist*(D.NaturalMotion?D.NaturalMotion.distanceRate(n.moveSpeed,n.panic?.5:0):(n.panic?2.7:4.8));n.phase=n.walk;if(q.hit)n.yaw+=Math.PI*.6;
   });
  }
  accessPlayerPose(){
   const a=this.access,p=this.player;if(!a)return p;const c=a.c,seat=D.carPoint(c,-.38,-.20),yaw=c.yaw,base={...p,walk:p.walk||0,moveSpeed:0,y:0,vy:0,stagger:0,crouch:0,dodge:0,reach:0,bodyLean:0};
   if(a.elapsed<a.approach)return{...base,...pointOnPath(a.path,a.elapsed/a.approach),moveSpeed:2.9,accessPhase:'approach'};
   const t=a.elapsed-a.approach,pullEnd=a.opening+a.pulling,entryStart=pullEnd+a.returning;
   if(a.kind==='exit'){
    const f=ease((t-a.opening)/a.entry);return{...base,x:mix(seat.x,a.door.x,f),z:mix(seat.z,a.door.z,f),yaw:yaw-f*Math.PI*.55,y:mix(-.29,0,f),seatBlend:1-f,seated:f<.999,crouch:Math.sin(f*Math.PI)*.12,reach:.4,accessPhase:f<1?'exit':'close'};
   }
   if(t<pullEnd){
    const pulling=a.kind==='extract'&&t>a.opening,drag=ease((t-a.opening-.25)/1.15),q=D.carPoint(c,mix(-1.85,-1.30,ease(t/a.opening))-drag*2.25,mix(.15,0,ease(t/a.opening))-drag*.24);
    const driver=this.driverPose(c),handTarget=pulling&&driver?{x:driver.x-Math.cos(c.yaw)*.20,y:(driver.y||0)+1.30,z:driver.z+Math.sin(c.yaw)*.20}: {...D.carPoint(c,-.99,.54),y:1.0};
    return{...base,...q,yaw:D.turn(base.yaw,yaw+Math.PI*.5,ease(t/a.opening)),bodyLean:pulling?.16:0,reach:pulling?.8:.65,crouch:pulling?.09:0,handTargets:{R:handTarget,L:pulling?{...handTarget,y:handTarget.y-.09,z:handTarget.z-.16}:null},accessPhase:pulling?'pull':'open'};
   }
   if(a.returning&&t<entryStart){const f=ease((t-pullEnd)/a.returning),u=1-f,q=D.carPoint(c,u*u*-3.55+2*u*f*-2.9+f*f*-1.85,u*u*-.24+2*u*f*1.20+f*f*.15);return{...base,...q,yaw:yaw+Math.PI*.5,walk:f*8,moveSpeed:2.6,accessPhase:'reposition'};}
   const f=ease((t-entryStart)/a.entry),start=a.kind==='extract'?a.door:D.carPoint(c,-1.30,0);return{...base,x:mix(start.x,seat.x,f),z:mix(start.z,seat.z,f),yaw:yaw+Math.PI*.5*(1-f),y:mix(0,-.29,f),seatBlend:f,seated:f>.001,crouch:Math.sin(f*Math.PI)*.12,reach:.4,accessPhase:f<1?'enter':'close'};
  }
  driverPose(c){
   if(!c.driver)return null;const q=D.carPoint(c,-.38,-.20);let n={...c.driver,...q,y:-.29,yaw:c.yaw,seated:true,seatBlend:1,moveSpeed:0,walk:0,reach:1,steering:c.steerAngle||0,handTargets:D.VehicleCabin.hands(c)};
   const a=this.access;if(a&&a.c===c&&a.kind==='extract'){
    const f=ease((a.elapsed-a.approach-a.opening-.25)/1.15),out=D.carPoint(c,-2.8,-.50);
    n={...n,x:mix(q.x,out.x,f),z:mix(q.z,out.z,f),y:mix(-.29,0,f),yaw:c.yaw-f*Math.PI*.56,seatBlend:1-f,seated:f<.999,crouch:Math.sin(f*Math.PI)*.12,bodyLean:f*.10,reach:1-f*.65,handTargets:null,accessPhase:f>0?'pulled':'seated'};
   }return n;
  }
  getContext(){
   if(this.access){const a=this.access,phase=this.accessPlayerPose().accessPhase;const labels={approach:'Acercándose',open:'Abriendo la puerta',pull:'Extrayendo al conductor',enter:'Entrando',reposition:'Volviendo al asiento',close:'Cerrando la puerta',exit:'Saliendo'};return{key:'F',text:(labels[phase]||'Interacción')+' · '+Math.round(clamp(a.elapsed/a.duration,0,1)*100)+'% · cancelar',action:'car'};}
   const q=super.getContext();if(q?.action==='car'&&this.player.car===null){const c=this.cars[this.nearestCar()];if(c?.driver)return{key:'F',text:c.police?'Patrulla ocupada · sacar al conductor':'Vehículo ocupado · sacar al conductor',action:'car'};}return q;
  }
  travel(x,z){if(this.access){this.emit('toast','Termina o cancela la interacción antes de viajar.');return false;}return super.travel(x,z);}
  respawn(reason){this.cancelAccess(true);super.respawn(reason);}
  serialize(){
   const data=super.serialize();
   data.occupancy={version:1,playerCarId:this.player.car===null?null:this.actor().id,cars:this.cars.map(c=>({id:c.id,x:c.x,z:c.z,yaw:c.yaw,health:c.health,damage:{...D.ensureVehicle(c).damage},color:[...c.color],police:!!c.police,parked:!!(c.parked||c.driver===null&&c!==this.actor()),stolen:!!c.stolen,owned:!!c.owned,driver:copyDriver(c.driver)})),evicted:this.peds.filter(n=>n.evicted).map(n=>({personId:n.personId,x:n.x,z:n.z,yaw:n.yaw,police:!!n.police,skin:[...n.skin],coat:[...n.coat],variant:n.variant||0}))};
   if(this.access&&this.player.car===null)Object.assign(data.player,this.access.lastSafe);
   return data;
  }
  validOccupancy(o){
   if(o===undefined)return true;const color=v=>Array.isArray(v)&&v.length===3&&v.every(n=>Number.isFinite(n)&&n>=0&&n<=1),pos=v=>[v.x,v.z,v.yaw].every(Number.isFinite)&&D.Frontier.valid(v.x,v.z);
   if(!o||o.version!==1||!Array.isArray(o.cars)||o.cars.length!==this.cars.length||!Array.isArray(o.evicted)||o.evicted.length>24)return false;
   const ids=new Set();for(const c of o.cars){if(!c||ids.has(c.id)||!this.cars.some(v=>v.id===c.id)||!pos(c)||!color(c.color)||!Number.isFinite(c.health)||c.health<5||c.health>100)return false;if(c.damage!==undefined&&(!c.damage||!['front','rear','left','right'].every(k=>Number.isFinite(c.damage[k])&&c.damage[k]>=0&&c.damage[k]<=1)))return false;ids.add(c.id);if(c.driver!==null&&(!c.driver||c.driver.id!=='driver:'+c.id||!color(c.driver.skin)||!color(c.driver.coat)))return false;}
   if(o.playerCarId!==null&&!ids.has(o.playerCarId))return false;
   const people=new Set();for(const n of o.evicted){if(!n||typeof n.personId!=='string'||!/^driver:\d+$/.test(n.personId)||people.has(n.personId)||!pos(n)||!color(n.skin)||!color(n.coat))return false;const c=o.cars.find(c=>'driver:'+c.id===n.personId);if(!c||c.driver!==null)return false;people.add(n.personId);}return true;
  }
  restore(data){
   if(!this.validOccupancy(data?.occupancy))return false;
   if(!super.restore(data))return false;this.access=null;const o=data.occupancy;
   for(const c of this.cars){c.boarding=false;c.doorOpen=0;c.driver=c.owned||c.parked||c.stolen?null:D.driverProfile(c);}
   if(o){
    for(const v of o.cars){const c=this.cars.find(c=>c.id===v.id);Object.assign(c,v,{color:[...v.color],damage:v.damage?{...v.damage}:{front:0,rear:0,left:0,right:0},driver:copyDriver(v.driver),speed:0,boarding:false,doorOpen:0});}
    this.player.car=o.playerCarId===null?null:this.cars.findIndex(c=>c.id===o.playerCarId);
    if(this.player.car!==null){const c=this.actor();c.driver=null;c.parked=false;this.player.x=c.x;this.player.z=c.z;}
    this.peds=this.peds.filter(n=>!n.evicted);for(const n of o.evicted)this.peds.push({...n,skin:[...n.skin],coat:[...n.coat],evicted:true,phase:0,walk:0,panic:0,moveSpeed:0,speed:1.3,homeZ:Math.floor(n.z/84)*84,reactUntil:0});
   }
   if(this.player.car!==null)this.actor().driver=null;return true;
  }
 }
 D.OccupancySimulation=OccupancySimulation;D.Simulation=OccupancySimulation;
})(DC);
