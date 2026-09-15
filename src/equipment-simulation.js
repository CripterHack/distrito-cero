/* Simulation-owned arsenal. All numbers tune fictional gameplay, not real weapons. */
'use strict';
(function(D){
 const Base=D.Simulation,E=D.Equipment,clamp=D.clamp;
 class EquipmentSimulation extends Base{
  constructor(world){super(world);this.equipment=E.initial();this.weaponEffects=[];this.weaponProjectiles=[];this.weaponMarks=[];this.weaponRng=D.rng(17821);this.weaponId=0;this.empActive=false;this.shotHeatUntil=0;}
  setLightLookup(){super.setLightLookup();const base=this.dynamics.lightActive;this.dynamics.lightActive=i=>{const p=this.dynamics.byId.get(this.world.lights[i]?.id||'lamp:'+i);return base(i)&&!(p?.empUntil>this.time);};}
  equipmentAvailable(){const p=this.player;return p.car===null&&!this.access&&!p.carry&&!(p.dodge>0)&&!(this.repairProgress>0)&&!(this.policeState?.surrender>0)&&p.health>0;}
  cancelEquipment(){if(!this.equipment)return;Object.assign(this.equipment,{charge:0,trigger:false,blockedTrigger:true,aiming:false,aimWeight:0});}
  equipWeapon(id){if(!E.get(id))return false;const e=this.equipment;if(e.selected===id)return true;this.cancelEquipment();Object.assign(e,{selected:id,reloading:0,reloadId:null,recoil:0,cooldown:e.cooldown});D.WeaponHandling.beginEquip(this);this.emit('sound','equip');return true;}
  cycleOptics(delta){this.equipment.zoom=clamp(this.equipment.zoom+Math.sign(delta),0,3);return E.zoom[this.equipment.zoom];}
  reloadWeapon(){const e=this.equipment,w=E.get(e.selected),ammo=e.ammo[w.id];if(!this.equipmentAvailable()||!w.mag||!ammo||e.reloading>0||ammo.loaded>=w.mag||ammo.reserve<=0)return false;e.charge=0;e.reloading=w.reload;e.reloadId=w.id;e.blockedTrigger=true;this.emit('sound','reload');return true;}
  addWeaponEffect(f){if(this.weaponEffects.length>=96)this.weaponEffects.shift();this.weaponEffects.push(f);}
  resupplyWeapon(){const depot=this.nearestSupply(),e=this.equipment;if(!depot||depot.distance>9||this.wanted||this.access||this.actualSpeed()>.6){this.emit('toast','Reabastece junto a una taquilla, taller o refugio, detenido y sin búsqueda.');return false;}const need=E.catalog.some(w=>w.mag&&(e.ammo[w.id].loaded<w.mag||e.ammo[w.id].reserve<w.reserve));if(!need){this.emit('toast','La munición ya está completa.');return false;}if(this.cash<120){this.emit('toast','Reabastecimiento: necesitas $120 del juego.');return false;}this.cash-=120;for(const w of E.catalog)if(w.mag)e.ammo[w.id]={loaded:w.mag,reserve:w.reserve};e.reloading=0;e.charge=0;this.emit('toast','Munición y celdas repuestas · $120');this.emit('save','');return true;}
  nearestSupply(){return[{x:10,z:1,name:'Taquilla del cruce'},...this.world.pois.filter(p=>['safe','garage'].includes(p.type))].map(p=>({...p,distance:D.distance(this.player,p)})).sort((a,b)=>a.distance-b.distance)[0]||null;}
  equipmentStep(dt,input={}){this.stepEquipmentCore(dt,input);D.WeaponHandling.step(this,dt);}
  stepEquipmentCore(dt,input={}){
   if(!Number.isFinite(dt)||dt<=0)return;dt=Math.min(dt,.25);const e=this.equipment,w=E.get(e.selected),ok=this.equipmentAvailable(),fire=!!input.fire;
   e.cooldown=Math.max(0,e.cooldown-dt);e.recoil=D.damp(e.recoil,0,14,dt);e.lastHitAge=(e.lastHitAge||0)+dt;
   if(input.aimRay&&Array.isArray(input.aimRay.origin)&&Array.isArray(input.aimRay.direction)&&input.aimRay.origin.length===3&&input.aimRay.direction.length===3&&[...input.aimRay.origin,...input.aimRay.direction].every(Number.isFinite)&&Math.hypot(input.aimRay.origin[0]-this.player.x,input.aimRay.origin[2]-this.player.z)<10&&Math.hypot(...input.aimRay.direction)>.1){e.ray={origin:input.aimRay.origin.slice(),direction:D.normalize(input.aimRay.direction)};e.pitch=clamp(Math.asin(clamp(e.ray.direction[1],-1,1)),-.75,.75);}
   e.aiming=ok&&!!input.aim;e.aimWeight=D.damp(e.aimWeight,(e.aiming||fire)?1:0,12,dt);
   if(e.reloading>0){e.reloading=Math.max(0,e.reloading-dt);if(e.reloading===0&&e.reloadId){const def=E.get(e.reloadId),ammo=e.ammo[def.id],n=Math.min(def.mag-ammo.loaded,ammo.reserve);ammo.loaded+=n;ammo.reserve-=n;e.reloadId=null;this.emit('sound','reloadDone');}}
   if(!ok){e.charge=0;e.blockedTrigger=fire;e.trigger=fire;return;}
   if(!fire||input.firePressed)e.blockedTrigger=false;
   const pressed=fire&&(input.firePressed||!e.trigger)&&!e.blockedTrigger,released=!fire&&e.trigger;
   if(w.kind==='gauss'){
    if(fire&&!e.blockedTrigger&&!e.reloading&&e.cooldown===0&&e.ammo.gauss.loaded>0)e.charge=Math.min(1,e.charge+dt/w.chargeTime);
    if(released){if(e.charge>=w.minCharge&&e.cooldown===0&&!e.reloading)this.fireWeapon(w,e.charge);e.charge=0;}
   }else if(!e.reloading&&e.cooldown===0&&(pressed||w.automatic&&fire&&!e.blockedTrigger)){
    if(w.kind==='optics'){if(e.aiming)this.markOptics();}
    else if(w.kind!=='none')this.fireWeapon(w,1);
   }
   e.trigger=fire;
  }
  aimTrace(range=600){const e=this.equipment,p=this.player,ray=e.ray||{origin:[p.x,1.34+(p.y||0),p.z],direction:[Math.sin(p.yaw),0,Math.cos(p.yaw)]};return{ray,hit:E.trace(this,ray.origin,ray.direction,range)[0]||null};}
  markOptics(){if(!this.equipmentAvailable()||E.get(this.equipment.selected).kind!=='optics')return false;const {hit}=this.aimTrace(600);if(!hit){this.emit('toast','Sin superficie visible que marcar dentro de 600 m.');return false;}this.pin={x:hit.point[0],z:hit.point[2]};this.routeClock=0;this.emit('toast','GPS · punto observado a '+Math.round(hit.distance)+' m');this.equipment.cooldown=.4;return true;}
  fireWeapon(w,charge=1){
   const e=this.equipment;if(w.mag&&e.ammo[w.id].loaded<=0){if(!this.reloadWeapon()){this.emit('sound','dry');e.cooldown=.35;}return false;}
   if((w.kind==='rocket'||w.kind==='grenade')&&this.weaponProjectiles.length>=24){e.cooldown=.2;return false;}
   if(w.mag)e.ammo[w.id].loaded--;e.shots=Math.min(1e9,e.shots+1);e.shotSerial++;e.cooldown=w.interval||.5;e.recoil=1;e.lastShot=this.time;
   if(w.kind==='emp'){this.pulseEMP();this.reportWeapon(w);this.emit('sound','emp');return true;}
   const {ray,hit}=this.aimTrace(w.range),m=E.mount(this),point=hit?.point||E.endpoint(ray.origin,ray.direction,w.range);let origin=m.muzzle;
   let direction=D.normalize(point.map((v,i)=>v-origin[i]));
   if(w.kind==='melee'){origin=[this.player.x,(this.player.y||0)+1.08,this.player.z];direction=D.normalize([ray.direction[0],0,ray.direction[2]]);}
   // The entire shoulder-to-muzzle path must be clear before a shot can emerge.
   const torso=[this.player.x,origin[1],this.player.z],barrelDirection=D.normalize(origin.map((v,i)=>v-torso[i])),barrelLength=Math.hypot(...origin.map((v,i)=>v-torso[i]));
   const obstruction=E.trace(this,torso,barrelDirection,barrelLength,{onlyBuildings:true})[0];
   if(obstruction){this.impactWeapon(obstruction,w.damage||15);this.addWeaponEffect({kind:'trace',from:torso,to:obstruction.point,life:.13,total:.13,color:[.9,.72,.42]});this.reportWeapon(w);this.emit('sound','shot');return true;}
   if(w.kind==='rocket'||w.kind==='grenade'){
    const grenade=w.kind==='grenade';this.weaponProjectiles.push({id:++this.weaponId,kind:w.kind,position:origin.slice(),velocity:direction.map((v,i)=>v*w.speed+(grenade&&i===1?5.5:0)),life:grenade?2.4:6,radius:w.radius,damage:w.damage,gravity:grenade?10:0,bounces:0});
   }else{
    const pellets=w.pellets||1;for(let k=0;k<pellets;k++){
     const spread=(w.spread||0)*(e.aiming?.55:1),right=D.normalize(D.cross(direction,[0,1,0])),up=D.cross(right,direction),u=(this.weaponRng()-.5)*2*spread,v=(this.weaponRng()-.5)*2*spread;
     const d=D.normalize(direction.map((x,i)=>x+right[i]*u+up[i]*v));
     const hits=E.trace(this,origin,d,w.range,{radius:w.kind==='melee'?.23:0});let end=E.endpoint(origin,d,w.range),remaining=w.kind==='gauss'?3:1,falloff=1;
     for(const h of hits){end=h.point;if(h.type==='wall'||h.type==='ground'){this.impactWeapon(h,3);break;}this.impactWeapon(h,(w.damage||20)*(w.kind==='gauss'?.35+.65*charge:1)*falloff);falloff*=.7;if(--remaining<=0)break;}
     if(w.kind!=='melee')this.addWeaponEffect({kind:w.kind==='gauss'?'gauss':'trace',from:origin.slice(),to:end,life:w.kind==='gauss'?.44:.13,total:w.kind==='gauss'?.44:.13,charge,color:w.kind==='gauss'?[.16,.75,1]:[.96,.72,.39]});
    }
   }
   this.reportWeapon(w);this.emit('sound',w.kind==='gauss'?'gauss':w.kind==='melee'?'swing':w.kind==='grenade'?'throw':w.kind==='rocket'?'launch':'shot');return true;
  }
  reportWeapon(w){if(this.time>=this.shotHeatUntil){this.addHeat(w.heat||5);this.shotHeatUntil=this.time+.8;}for(const n of this.peds)if(!n.hidden&&D.distance(n,this.player)<48)n.panic=Math.max(n.panic||0,5);}
  impactWeapon(hit,damage){
   const [x,y,z]=hit.point,e=this.equipment;let material='metal';
   if(hit.type==='car'){D.damageVehicle(hit.ref,damage*1.25,x,z);hit.ref.combatHitUntil=this.time+.4;material='metal';}
   if(hit.type==='prop'){const p=hit.ref,coef=p.type==='tree'?.52:.9;this.dynamics.impactProp(p,1.5+Math.sqrt(Math.max(.01,damage)/coef),Math.sin(this.player.yaw),Math.cos(this.player.yaw));material=p.material;}
   if(hit.type==='npc'){const n=hit.ref;n.combatHealth=Math.max(0,(n.combatHealth??100)-damage);n.stagger=1;n.panic=8;n.combatHitUntil=this.time+.45;if(n.combatHealth===0)n.combatStunUntil=this.time+12;material='smoke';}
   if(['car','prop','npc'].includes(hit.type)){e.hits=Math.min(1e9,e.hits+1);e.lastHitAge=0;e.lastHit=hit.type;}
   this.dynamics.burst(x,y,z,material,hit.type==='npc'?3:6);
   if(hit.type!=='npc'){if(this.weaponMarks.length>=32)this.weaponMarks.shift();this.weaponMarks.push({point:hit.point.slice(),life:3});}
  }
  pulseEMP(){const p=this.player,e=this.equipment,w=E.get('emp'),origin=[p.x,(p.y||0)+1.05,p.z];let count=0;
   for(const c of this.cars)if(D.distance(c,p)<w.radius&&this.world.visible(p.x,p.z,c.x,c.z)){c.empUntil=Math.max(c.empUntil||0,this.time+w.duration);c.horn=0;count++;}
   for(const o of this.dynamics.props)if(o.type==='lamp'&&!o.broken&&D.distance(o,p)<w.radius&&this.world.visible(p.x,p.z,o.x,o.z)){o.empUntil=Math.max(o.empUntil||0,this.time+w.duration);count++;}
   this.dynamics.lightRevision++;this.empActive=true;e.lastPulse=count;this.addWeaponEffect({kind:'emp',point:origin,radius:w.radius,life:1.3,total:1.3,color:[.12,.65,1]});this.emit('toast','EMP · '+count+' sistemas interrumpidos durante 8 s. La búsqueda continúa.');
  }
  explodeWeapon(point,radius,damage){
   const q={x:point[0],z:point[2]},visible=o=>this.world.visible(q.x,q.z,o.x,o.z);
   for(const [type,items]of[['car',this.cars],['prop',this.dynamics.props],['npc',this.peds]])for(const o of items){const d=Math.hypot(o.x-q.x,o.z-q.z,(type==='car'?.8:type==='prop'?(o.y||0)+.3:1)-point[1]);if(d>=radius||o.hidden||o.broken||!visible(o))continue;this.impactWeapon({type,ref:o,point:[o.x,type==='car'?.75:.4,o.z]},damage*(1-d/radius));}
   const dist=Math.hypot(this.player.x-q.x,this.player.z-q.z,(this.player.y||0)+.8-point[1]);if(dist<radius&&visible(this.player)){this.player.health=Math.max(0,this.player.health-damage*(1-dist/radius)*.7);this.trauma=.45;}
   this.addWeaponEffect({kind:'blast',point:point.slice(),radius,life:.7,total:.7,color:[1,.51,.18]});this.dynamics.burst(...point,'metal',15);this.dynamics.burst(...point,'smoke',10);this.emit('sound','explosion');
  }
  projectileStep(dt){
   for(const p of this.weaponProjectiles){
    const from=p.position.slice();p.life-=dt;
    if(!p.resting){p.velocity[1]-=p.gravity*dt;const delta=p.velocity.map(v=>v*dt),length=Math.hypot(...delta),h=length?E.trace(this,from,delta,length,{radius:.07})[0]:null;
     if(h){p.position=h.point.map((v,i)=>v-(delta[i]/Math.max(length,.001))*.026);
      if(p.kind==='grenade'){
       if(h.type==='ground'){p.position[1]=.09;p.velocity[1]=Math.abs(p.velocity[1])*.43;p.velocity[0]*=.64;p.velocity[2]*=.64;if(p.bounces>=4||Math.abs(p.velocity[1])<.45){p.resting=true;p.velocity=[0,0,0];}}
       else{p.velocity[0]*=-.36;p.velocity[2]*=-.36;p.velocity[1]=Math.max(0,p.velocity[1])*.55;if(p.bounces>=5){p.velocity[0]=p.velocity[2]=0;}}
       p.bounces++;
      }else p.life=0;
     }else p.position=from.map((v,i)=>v+delta[i]);
    }
    if(p.life<=0)this.explodeWeapon(p.position,p.radius,p.damage);
   }this.weaponProjectiles=this.weaponProjectiles.filter(p=>p.life>0);
  }
  coastDisabled(c,dt,input={}){c.speed=D.damp(c.speed,0,input.brake?9:1.9,dt);c.yaw+=clamp(input.steer||0,-1,1)*Math.min(Math.abs(c.speed),4)*dt*.25;const q=this.world.move(c.x,c.z,Math.sin(c.yaw)*c.speed*dt,Math.cos(c.yaw)*c.speed*dt,.95);c.x=q.x;c.z=q.z;if(q.hit)c.speed=0;D.ensureVehicle(c);c.steerAngle=D.damp(c.steerAngle,(input.steer||0)*.35,5,dt);}
  drive(c,dt,input={}){if(c.empUntil>this.time){this.coastDisabled(c,dt,input);return;}super.drive(c,dt,input);}
  traffic(c,dt){if(c.empUntil>this.time){this.coastDisabled(c,dt);return;}super.traffic(c,dt);}
  pedestrians(dt){
   const stunned=this.peds.filter(n=>n.combatStunUntil>this.time),snap=stunned.map(n=>({hidden:n.hidden,x:n.x,z:n.z,phase:n.phase,walk:n.walk}));
   stunned.forEach(n=>n.hidden=true);super.pedestrians(dt);
   stunned.forEach((n,i)=>{Object.assign(n,snap[i]);n.moveSpeed=0;});
   for(const n of this.peds)if(n.combatStunUntil&&n.combatStunUntil<=this.time){delete n.combatStunUntil;n.combatHealth=100;n.panic=6;}
  }
  walk(dt,input={}){const e=this.equipment,aim=e?.aiming,filtered=aim?{...input,sprint:false,throttle:(input.throttle||0)*.60,steer:(input.steer||0)*.60}:input;super.walk(dt,filtered);if(e&&this.equipmentAvailable()&&(aim||e.charge>0||e.recoil>.05)){const d=e.ray?.direction;if(d)this.player.yaw=D.turn(this.player.yaw,Math.atan2(d[0],d[2]),dt*12);}}
  interact(kind='car'){if(this.equipment&&['car','use','dodge','push'].includes(kind))this.cancelEquipment();super.interact(kind);}
  respawn(reason){super.respawn(reason);this.cancelEquipment();if(this.equipment){this.equipment.reloading=0;this.equipment.cooldown=.25;}}
  step(dt,input={}){if(!Number.isFinite(dt)||dt<=0)return;const h=Math.min(.25,dt)/Math.ceil(Math.min(.25,dt)*60),count=Math.ceil(Math.min(.25,dt)*60);for(let i=0;i<count;i++){this.equipmentStep(h,i===0?input:{...input,firePressed:false});super.step(h,input);this.projectileStep(h);for(const f of this.weaponEffects)f.life-=h;this.weaponEffects=this.weaponEffects.filter(f=>f.life>0);for(const m of this.weaponMarks)m.life-=h;this.weaponMarks=this.weaponMarks.filter(m=>m.life>0);if(this.empActive){const any=this.cars.some(c=>c.empUntil>this.time)||this.dynamics.props.some(o=>o.empUntil>this.time);if(!any){this.empActive=false;this.dynamics.lightRevision++;}}}}
  serialize(){const data=super.serialize();data.equipment=E.snapshot(this.equipment||E.initial());return data;}
  restore(data){if(!E.valid(data?.equipment))return false;if(!super.restore(data))return false;this.equipment=E.restore(data.equipment);D.WeaponHandling.beginEquip(this);this.weaponEffects=[];this.weaponProjectiles=[];this.weaponMarks=[];this.empActive=false;this.shotHeatUntil=0;this.weaponId=0;for(const c of this.cars)c.empUntil=0;for(const o of this.dynamics.props)o.empUntil=0;this.setLightLookup();return true;}
 }
 D.EquipmentSimulation=EquipmentSimulation;D.Simulation=EquipmentSimulation;
})(DC);
