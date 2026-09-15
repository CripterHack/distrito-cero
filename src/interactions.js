/* A contained extension of v0.3. Police pursuit/arrest rules remain in the base simulation. */
'use strict';
(function(D){
 const Base=D.Simulation;
 class ReactiveSimulation extends Base{
  constructor(world){super(world);this.dynamics=new D.ReactiveWorld(this);this.trauma=0;this.repairProgress=0;this.impactUntil=0;this.impactLabel='';this.lastInput={};
   Object.assign(this.player,{vx:0,vz:0,crouch:0,carry:null,reach:0,stagger:0,dodge:0,dodgeCooldown:0,transition:null});for(const c of this.cars)D.ensureVehicle(c);
  }
  step(dt,input={}){
   if(!Number.isFinite(dt)||dt<=0)return;
   // Bound catch-up work. Normal play still advances exactly 1/60 s per tick.
   const count=Math.ceil(Math.min(dt,.25)/(1/60)),h=Math.min(dt,.25)/count;
   for(let k=0;k<count;k++){
    super.step(h,input);const p=this.player;this.trauma=Math.max(0,this.trauma-h*1.4);p.reach=Math.max(0,p.reach-h*1.8);p.stagger=Math.max(0,p.stagger-h*1.7);p.dodgeCooldown=Math.max(0,p.dodgeCooldown-h);p.dodge=Math.max(0,p.dodge-h);
    if(p.transition){p.transition.elapsed+=h;if(p.transition.elapsed>=p.transition.duration)p.transition=null;}
    this.repairStep(h,input);this.dynamics.update(h);
    if(p.car!==null){const c=this.actor();p.x=c.x;p.z=c.z;}
    this.lastInput={...input};
   }
  }
  drive(c,dt,input){
   D.ensureVehicle(c);const oldSpeed=c.speed,oldYaw=c.yaw,oldHealth=c.health;
   super.drive(c,dt,input);
   if(c.health<oldHealth){const impact=oldHealth-c.health;c.health=oldHealth;D.damageVehicle(c,impact*1.5,c.x+Math.sin(c.yaw)*Math.sign(oldSpeed)*2,c.z+Math.cos(c.yaw)*Math.sign(oldSpeed)*2);this.dynamics.burst(c.x+Math.sin(c.yaw)*2,.7,c.z+Math.cos(c.yaw)*2,'metal',12);this.trauma=Math.min(.7,Math.abs(oldSpeed)*.02);}
   c.steerAngle=D.damp(c.steerAngle,-(input.steer||0)*.42,9,dt);
   const accel=(c.speed-oldSpeed)/dt,turn=D.wrap(c.yaw-oldYaw)/dt;
   c.suspension.pitch=D.damp(c.suspension.pitch,D.clamp(-accel*.002,-.09,.09),9,dt);
   c.suspension.roll=D.damp(c.suspension.roll,D.clamp(-turn*c.speed*.003,-.10,.10),8,dt);c.suspension.kick=D.damp(c.suspension.kick,0,7,dt);
   // Damage affects performance moderately, while keeping an escape manoeuvre possible.
   c.speed=D.clamp(c.speed,-11,42*(1-c.damage.front*.23));
   this.dynamics.carContacts(c,dt);this.vehicleSmoke(c);
  }
  traffic(c,dt){
   D.ensureVehicle(c);const oldYaw=c.yaw;
   // Unoccupied cars can roll after being pushed. This does not recruit a traffic driver.
   if(c.parked&&c.pushedUntil>this.time){const q=this.world.move(c.x,c.z,Math.sin(c.yaw)*c.speed*dt,Math.cos(c.yaw)*c.speed*dt,1.08);c.x=q.x;c.z=q.z;c.speed*=Math.exp(-1.25*dt);if(q.hit)c.speed=0;}
   else super.traffic(c,dt);
   c.steerAngle=D.damp(c.steerAngle,D.clamp(D.wrap(c.yaw-oldYaw)/Math.max(dt,.001)*.2,-.4,.4),8,dt);
   if(this.dynamics&&D.distance(c,this.player)<120)this.dynamics.carContacts(c,dt);
   this.vehicleSmoke(c);
  }
  vehicleSmoke(c){if(!this.dynamics)return;D.ensureVehicle(c);if((c.health<55||c.damage.front>.62)&&D.distance(c,this.player)<60&&this.time-(c.lastSmoke||0)>.16){c.lastSmoke=this.time;this.dynamics.burst(c.x+Math.sin(c.yaw)*1.2,1.1,c.z+Math.cos(c.yaw)*1.2,'smoke',1);}}
  walk(dt,input){
   const p=this.player,f=input.throttle||0,side=input.steer||0,m=Math.min(1,Math.hypot(f,side)),a=input.lookYaw??p.yaw;
   p.crouch=D.damp(p.crouch,input.crouch?1:0,11,dt);p.moving=m>.05;
   const speed=(input.sprint?6.2:3.3)*(1-p.crouch*.55)*(p.carry?.80:1)*(1-p.stagger*.45);
   const mag=Math.max(1,Math.hypot(f,side)),tx=(Math.sin(a)*f-Math.cos(a)*side)/mag*speed,tz=(Math.cos(a)*f+Math.sin(a)*side)/mag*speed;
   const vx=Number.isFinite(p.vx)?p.vx:0,vz=Number.isFinite(p.vz)?p.vz:0;
   p.vx=D.damp(vx,tx,p.moving?12:10,dt);p.vz=D.damp(vz,tz,p.moving?12:10,dt);
   let dx=p.vx*dt,dz=p.vz*dt;
   if(p.dodge>0){dx+=Math.sin(p.dodgeYaw)*7*dt;dz+=Math.cos(p.dodgeYaw)*7*dt;}
   const old={x:p.x,z:p.z},oldYaw=p.yaw,q=this.world.move(p.x,p.z,dx,dz,.34);p.x=q.x;p.z=q.z;
   if(m>.05)p.yaw=D.turn(p.yaw,Math.atan2(tx,tz),dt*9);
   if(q.hit&&Math.hypot(p.vx,p.vz)>3&&this.time>(p.impactCooldown||0)){p.stagger=.55;p.impactCooldown=this.time+.8;this.trauma=.14;}
   p.moveSpeed=D.distance(p,old)/dt;
   p.sprintBlend=D.damp(p.sprintBlend,input.sprint&&m>.05?1:0,8,dt);p.turnRate=D.damp(p.turnRate,D.wrap(p.yaw-oldYaw)/dt,9,dt);p.landing=Math.max(0,p.landing-dt*4.5);
   const wasGrounded=p.grounded;
   if(input.brake&&!p.jumpHeld&&p.y===0&&p.vy===0){p.vy=5;p.grounded=false;}
   p.jumpHeld=!!input.brake;p.vy-=14*dt;p.y=Math.max(0,p.y+p.vy*dt);
   if(p.y===0){if(!wasGrounded&&p.vy<0){p.landing=1;this.trauma=Math.max(this.trauma,.055);}p.vy=0;p.grounded=true;}else p.grounded=false;
   this.dynamics.footContacts(p);this.playerVehicleContact(dt);p.moveSpeed=D.distance(p,old)/dt;p.walk+=D.distance(p,old)*(D.NaturalMotion?D.NaturalMotion.distanceRate(p.moveSpeed,p.sprintBlend,p.crouch):D.lerp(4.8,2.7,p.sprintBlend));
  }
  playerVehicleContact(dt){
   const p=this.player;if(p.transition)return;
   for(const c of this.cars){if(D.distance(c,p)>3.2||!D.vehicleContains(c,p.x,p.z,.32)||p.y>1.3)continue;
    // A grounded player isn't a ghost. On slow contact step out along the nearest side.
    const co=Math.cos(c.yaw),si=Math.sin(c.yaw),dx=p.x-c.x,dz=p.z-c.z,u=dx*co-dz*si,v=dx*si+dz*co;
    const px=1.33-Math.abs(u),pz=2.56-Math.abs(v);if(px<0||pz<0)continue;let nx,nz,pen;
    if(px<pz){nx=co*(Math.sign(u)||1);nz=-si*(Math.sign(u)||1);pen=px;}else{nx=si*(Math.sign(v)||1);nz=co*(Math.sign(v)||1);pen=pz;}
    const q=this.world.move(p.x,p.z,nx*(pen+.01),nz*(pen+.01),.32);p.x=q.x;p.z=q.z;
    if(Math.abs(c.speed)>3&&this.time>(p.carHitUntil||0)){const v=Math.abs(c.speed);p.carHitUntil=this.time+1.3;p.stagger=1;p.vx+=nx*3;p.vz+=nz*3;p.health=Math.max(1,p.health-v*.45);this.trauma=.5;this.emit('sound','crash');}
   }
  }
  vehicleContacts(dt){
   // Keep v0.3's tested separation/recovery solver, and capture the pre-solve impact for visuals.
   const p=this.player,car=p.car!==null?this.actor():null;let hits=[];
   if(car)for(const other of this.cars){if(other===car)continue;const hit=D.vehicleOverlap(car,other);if(hit&&hit.closing>5){const key='visual:'+Math.min(car.id,other.id)+':'+Math.max(car.id,other.id),last=this.dynamics.contactTimes.get(key)??-Infinity;if(this.time-last>1){hits.push({other,hit});this.dynamics.contactTimes.set(key,this.time);}}}
   super.vehicleContacts(dt);
   for(const {other,hit}of hits){D.damageVehicle(car,hit.closing*.42,other.x,other.z);D.damageVehicle(other,hit.closing*.35,car.x,car.z);this.dynamics.burst((car.x+other.x)/2,.75,(car.z+other.z)/2,'metal',12);this.trauma=Math.min(.7,hit.closing*.014);}
  }
  nearestProp(range=1.9,includeBroken=false){const p=this.player;return this.dynamics.hash.query(p.x,p.z,range).filter(o=>!o.held&&(includeBroken||!o.broken)&&D.distance(o,p)<range&&this.world.visible(p.x,p.z,o.x,o.z)).sort((a,b)=>D.distance(a,p)-D.distance(b,p))[0]||null;}
  getContext(){
   const base=super.getContext(),p=this.player;
   if(p.car!==null)return base;
   if(base&&base.action!=='car')return base;
   if(p.carry)return{key:'E',text:'Soltar objeto · G para lanzar',action:'drop'};
   const o=this.nearestProp(1.8,true);
   if(o){if(o.broken)return{key:'E',text:'Restaurar '+o.label.toLowerCase()+' · $60',action:'restoreProp'};if(o.carry)return{key:'E',text:'Recoger '+o.label.toLowerCase()+' · G para empujar',action:'pick'};if(!o.hinged)return{key:'G',text:'Empujar '+o.label.toLowerCase(),action:'push'};}
   return base;
  }
  interact(kind='car'){
   const p=this.player;
   if(kind==='dodge'){
    if(p.car!==null){super.interact('horn');return;}if(p.dodgeCooldown>0||p.y>0)return;
    p.dodge=.40;p.dodgeCooldown=1.3;const i=this.lastInput,a=i.lookYaw??p.yaw;
    p.dodgeYaw=Math.hypot(i.throttle||0,i.steer||0)>.05?Math.atan2(Math.sin(a)*(i.throttle||0)-Math.cos(a)*(i.steer||0),Math.cos(a)*(i.throttle||0)+Math.sin(a)*(i.steer||0)):p.yaw;return;
   }
   if(kind==='push'){
    if(p.car!==null)return;
    if(p.carry){const o=this.dynamics.byId.get(p.carry);o.held=false;o.y=Math.max(.5,p.y+.95);o.vx=Math.sin(p.yaw)*9;o.vz=Math.cos(p.yaw)*9;o.vy=3.0;o.changed=true;p.carry=null;p.reach=1;this.emit('sound','door');return;}
    const o=this.nearestProp(2);if(o&&!o.hinged){const a=Math.atan2(o.x-p.x,o.z-p.z);o.vx+=Math.sin(a)*5.2;o.vz+=Math.cos(a)*5.2;o.vy=.25;o.changed=true;p.reach=.8;return;}
    const i=this.nearestCar();if(i!==null&&i!==undefined&&i>=0){const c=this.cars[i];if(c&&Math.abs(c.speed)<2.5){const dot=(c.x-p.x)*Math.sin(c.yaw)+(c.z-p.z)*Math.cos(c.yaw);c.speed+=Math.sign(dot||1)*2;c.pushedUntil=this.time+2;c.parked=true;p.reach=1;this.emit('toast','Empujas el vehículo. Puedes moverlo sin encenderlo.');return;}}
    return;
   }
   if(kind==='use'){
    const ctx=this.getContext();
    if(ctx?.action==='drop'){this.dropHeld();p.reach=.7;return;}
    if(ctx?.action==='pick'){const o=this.nearestProp(1.8);if(o?.carry&&!o.broken){p.carry=o.id;o.held=true;o.changed=true;o.vx=o.vz=o.vy=0;p.reach=1;this.emit('toast','OBJETO EN MANOS · E soltar · G lanzar');}return;}
    if(ctx?.action==='push'){this.interact('push');return;}
    if(ctx?.action==='restoreProp'){const o=this.nearestProp(1.8,true);if(!o?.broken)return;if(this.wanted){this.emit('toast','Pierde la búsqueda antes de restaurar el entorno.');return;}if(this.cash<60){this.emit('toast','Restauración: necesitas $60.');return;}
     // Never resurrect a solid prop through an actor.
     if(this.cars.some(c=>D.vehicleContains(c,o.homeX,o.homeZ,o.radius))||D.distance({x:o.homeX,z:o.homeZ},p)<o.radius+.4){this.emit('toast','Despeja la base del objeto antes de restaurarlo.');return;}
     this.cash-=60;Object.assign(o,{x:o.homeX,z:o.homeZ,y:0,yaw:0,health:o.maxHealth,broken:false,angle:0,angularVelocity:0,vx:0,vz:0,vy:0,changed:true});this.dynamics.lightRevision++;p.reach=1;this.emit('toast','Entorno restaurado.');return;
    }
   }
   const beforeCar=p.car,old={x:p.x,z:p.z,yaw:p.yaw},garageCar=beforeCar!==null?this.actor():this.cars[this.nearestCar(9)],oldHealth=garageCar?.health||0;
   if(kind==='car'&&p.carry)this.dropHeld();
   super.interact(kind);
   if(p.car!==beforeCar){const c=this.cars[p.car!==null?p.car:beforeCar],enter=p.car!==null;D.ensureVehicle(c);p.vx=p.vz=0;
    p.transition={enter,carIndex:enter?p.car:beforeCar,from:old,to:{x:p.x,z:p.z,yaw:p.yaw},elapsed:0,duration:.78};c.doorUntil=this.time+.85;c.doorSide=((old.x-c.x)*Math.cos(c.yaw)-(old.z-c.z)*Math.sin(c.yaw))<0?-1:1;
   }
   if(kind==='use'&&garageCar&&oldHealth<100&&garageCar.health===100)D.repairVehicle(garageCar);
  }
  dropHeld(){const p=this.player;if(!p.carry)return;const o=this.dynamics.byId.get(p.carry);if(o){o.held=false;o.vx=o.vz=0;o.vy=0;o.y=Math.max(.1,p.y+.8);o.changed=true;}p.carry=null;}
  repairStep(dt,input){
   if(!input.repair||this.player.car!==null||this.player.moveSpeed>.3||this.seen){this.repairProgress=0;return;}
   const i=this.nearestCar(),c=Number.isInteger(i)&&i>=0?this.cars[i]:null;
   if(!c||D.distance(c,this.player)>3.8||Math.abs(c.speed)>.25||c.health>=99.9||this.cash<90||!this.world.visible(c.x,c.z,this.player.x,this.player.z)){this.repairProgress=0;return;}
   if(this.repairCar!==i){this.repairProgress=0;this.repairCar=i;}
   this.player.reach=.45;this.repairProgress+=dt/3;
   if(this.repairProgress>=1){D.repairVehicle(c);this.cash-=90;this.repairProgress=0;this.emit('toast','REPARACIÓN COMPLETA · $90 · Carrocería y luces restauradas.');this.emit('sound','reward');this.emit('save','');}
  }
  respawn(reason){this.dropHeld();super.respawn(reason);Object.assign(this.player,{vx:0,vz:0,transition:null,dodge:0,stagger:0,crouch:0,carry:null});this.repairProgress=0;}
  serialize(){const data=super.serialize();data.dynamics=this.dynamics.serialize();
   data.dynamics.vehicles=this.cars.filter(c=>(this.player.car===null||c!==this.actor())&&(c.health<100||Object.values(c.damage||{}).some(v=>v>0)||c.pushedUntil)).map(c=>({id:c.id,x:c.x,z:c.z,yaw:c.yaw,health:c.health,parked:c.parked,damage:{...D.ensureVehicle(c).damage}}));if(data.vehicle){D.ensureVehicle(this.actor());data.vehicle.damage={...this.actor().damage};}return data;}
  restore(data){
   if(!this.dynamics.validate(data?.dynamics))return false;
   const fleet=data?.dynamics?.vehicles;
   if(fleet!==undefined){if(!Array.isArray(fleet)||fleet.length>this.cars.length)return false;const seen=new Set();for(const v of fleet){if(!v||seen.has(v.id)||!this.cars.some(c=>c.id===v.id)||![v.x,v.z,v.yaw,v.health].every(Number.isFinite)||Math.abs(v.x)>(this.world.coordinateLimit||425)||Math.abs(v.z)>(this.world.coordinateLimit||425)||v.health<5||v.health>100||!v.damage||!['front','rear','left','right'].every(k=>Number.isFinite(v.damage[k])&&v.damage[k]>=0&&v.damage[k]<=1))return false;seen.add(v.id);}}
   const dmg=data?.vehicle?.damage;if(dmg&&(!['front','rear','left','right'].every(k=>Number.isFinite(dmg[k])&&dmg[k]>=0&&dmg[k]<=1)))return false;
   if(!super.restore(data))return false;this.dynamics.restore(data.dynamics);Object.assign(this.player,{vx:0,vz:0,carry:null,transition:null,crouch:0,dodge:0,stagger:0});this.repairProgress=0;
   for(const v of fleet||[]){const c=this.cars.find(c=>c.id===v.id);if(this.player.car!==null&&c===this.actor())continue;Object.assign(c,{x:v.x,z:v.z,yaw:D.wrap(v.yaw),speed:0,health:v.health,parked:!!v.parked,damage:{...v.damage}});}
   if(this.player.car!==null){D.ensureVehicle(this.actor());this.actor().damage=dmg?{...dmg}:{front:0,rear:0,left:0,right:0};}return true;
  }
 }
 D.Simulation=ReactiveSimulation;
})(DC);
