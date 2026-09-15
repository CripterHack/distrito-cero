'use strict';
(function(D){
 const CAR_COLORS=[[.11,.2,.23],[.38,.06,.045],[.045,.055,.063],[.62,.63,.56],[.1,.16,.29],[.29,.25,.19],[.09,.24,.17]];
 class Simulation{
  constructor(world){
   this.world=world;this.random=D.rng(418);this.time=0;this.cash=850;this.heat=0;this.wanted=0;this.unseen=0;this.seen=false;this.bust=0;this.story=0;this.free=false;this.ending=null;this.events=[];this.job=null;this.upload=0;this.uploading=false;this.collected=[];this.stats={distance:0,jobs:0,escapes:0};
   this.contactRecords=new Map();this.resetPolice();
   this.player={actualSpeed:0,x:5,z:8,y:0,vy:0,yaw:0,health:100,car:null,walk:0,moving:false,moveSpeed:0,sprintBlend:0,turnRate:0,grounded:true,landing:0};this.cars=[];this.peds=[];this.cooldowns={crime:0,crash:0,horn:0};
   this.cars.push(this.makeCar(5,11,0,false,true,0));
   for(let i=0;i<32;i++){
    let row=Math.floor(this.random()*9)-4,col=Math.floor(this.random()*9)-4,vertical=i%2===0,dir=i%3===0?-1:1;
    let x=vertical?col*84+dir*4:col*84+25,z=vertical?row*84+27:row*84-dir*4;
    this.cars.push(this.makeCar(x,z,vertical?(dir===1?0:Math.PI):(dir===1?Math.PI/2:-Math.PI/2),false,i%5===0,i+1));
   }
   for(let i=0;i<6;i++)this.cars.push(this.makeCar((i-3)*84+4,(i%2?2:-2)*84,0,true,false,i+40));
   for(let i=0;i<72;i++){
    let ix=Math.floor(this.random()*9)-4,iz=Math.floor(this.random()*9)-4;
    this.peds.push({x:ix*84+(i%2?13.7:-13.7),z:iz*84+12+this.random()*58,yaw:i%3?0:Math.PI,speed:.8+this.random()*.6,phase:this.random()*10,panic:0,homeZ:iz*84,skin:[[.36,.2,.13],[.63,.42,.29],[.8,.61,.46],[.21,.12,.09]][i%4],coat:CAR_COLORS[(i+3)%7]});
   }
   this.route=[];this.routeClock=0;this.pin=null;this.lastTarget=null;
  }
  makeCar(x,z,yaw,police,parked,id){
   let c={id,x,z,yaw,speed:parked?0:6+this.random()*3,health:100,color:police?[.075,.09,.115]:CAR_COLORS[id%CAR_COLORS.length],police,parked,owned:id===0,stolen:false,route:[],navTime:0,brake:0,wheel:0,horn:0,hit:0};
   this.newTrafficRoute(c);return c;
  }
  newTrafficRoute(c){
   let n=this.world.node(c.x,c.z),dest;
   // First waypoint lies ahead, never behind the moving car.
   let dx=Math.round(Math.sin(c.yaw)),dz=Math.round(Math.cos(c.yaw));
   let next={x:D.clamp(n.x+dx*84,-420,420),z:D.clamp(n.z+dz*84,-420,420)};
   dest={x:(Math.floor(this.random()*11)-5)*84,z:(Math.floor(this.random()*11)-5)*84};
   c.route=[next,...this.world.route(next.x,next.z,dest.x,dest.z).slice(1)];
  }
  emit(kind,text,extra={}){this.events.push({kind,text,...extra});}
  resetPolice(){
   this.seen=false;this.unseen=0;this.bust=0;
   this.policeState={lastSeen:null,lastSeenTime:-Infinity,searchHeat:0,surrender:0,graceUntil:0,contactHintUntil:0};
   if(this.contactRecords)this.contactRecords.clear();
   if(this.cars)for(const c of this.cars){c.recoverUntil=0;c.recoverCooldown=0;c.sight=false;c.aiMode='patrol';c.navTime=0;}
  }
  addHeat(n){
   this.heat=D.clamp(this.heat+n,0,100);this.wanted=Math.ceil(this.heat/20);this.unseen=0;
   // A reported incident supplies a location, not permanent omniscient tracking.
   this.policeState.lastSeen={x:this.player.x,z:this.player.z};this.policeState.lastSeenTime=this.time;
   this.policeState.searchHeat=this.heat;
  }
  actor(){return this.player.car!==null?this.cars[this.player.car]:this.player;}
  target(){
   if(this.pin)return{...this.pin,name:'DESTINO MARCADO',custom:true};
   if(this.job)return{...this.job.points[this.job.index],name:this.job.type==='race'?'CONTROL DE CARRERA':'ENTREGA PENDIENTE',job:true};
   if(!this.free&&this.story<D.stories.length){let m=D.stories[this.story];if(this.story===1){let c=this.cars[0];return{...m,x:c.x,z:c.z};}return m;}
   return null;
  }
  storyTarget(){if(this.free||this.story>=D.stories.length)return null;let t=D.stories[this.story];return this.story===1?{...t,x:this.cars[0].x,z:this.cars[0].z}:t;}
  nearestCar(max=4.8){let best=-1,dist=max;this.cars.forEach((c,i)=>{let d=D.distance(this.player,c);if(d<dist&&Math.abs(c.speed)<5){dist=d;best=i;}});return best;}
  getContext(){
   let p=this.player,t=this.storyTarget();
   if(t&&D.distance(p,t)<8&&this.story!==1){
    if(t.foot&&p.car!==null)return{key:'F',text:'Baja del vehículo para interactuar',action:'car'};
    if((this.story===3||this.story===5)&&this.wanted)return{key:'',text:'Pierde a la policía antes de acercarte'};
    return{key:'E',text:this.uploading?'Transmitiendo… permanece cerca':t.button,action:'story'};
   }
   const poi=this.world.pois.find(q=>D.distance(p,q)<7);
   if(poi&&!this.job){
    if(poi.type==='garage')return{key:'E',text:'Taller · reparar y cambiar pintura · $200',action:'garage'};
    if(poi.type==='job')return{key:'E',text:'Aceptar entrega · recompensa $650',action:'job'};
    if(poi.type==='race')return{key:'E',text:'Circuito nocturno · 90 segundos · $1,000',action:'race'};
    if(poi.type==='safe'&&!this.wanted)return{key:'E',text:'Refugio · descansar y guardar',action:'safe'};
   }
   if(p.car!==null)return{key:'F',text:Math.abs(this.actor().speed)<4?'Bajar del vehículo':'Detente para bajar',action:'car'};
   if(this.nearestCar()>=0)return{key:'F',text:'Entrar al vehículo',action:'car'};
   return null;
  }
  interact(kind='car'){
   let p=this.player;
   if(kind==='car'){
    if(p.car!==null){
     const c=this.actor();if(Math.abs(c.speed)>4){this.emit('toast','Detente antes de bajar del vehículo.');return;}
     const offsets=[[-2.2,0],[2.2,0],[0,-3],[0,3]];
     const candidate=offsets.map(([x,z])=>({x:c.x+x*Math.cos(c.yaw)+z*Math.sin(c.yaw),z:c.z-x*Math.sin(c.yaw)+z*Math.cos(c.yaw)})).find(v=>!this.world.blocked(v.x,v.z,.42)&&!this.cars.some(other=>other!==c&&D.vehicleContains(other,v.x,v.z,.48)));
     if(!candidate){this.emit('toast','No hay espacio para abrir la puerta.');return;}
     c.parked=true;c.speed=0;p.car=null;p.x=candidate.x;p.z=candidate.z;p.yaw=c.yaw;p.actualSpeed=0;this.emit('sound','door');return;
    }
    const i=this.nearestCar();if(i<0)return;
    const c=this.cars[i];p.car=i;p.x=c.x;p.z=c.z;p.yaw=c.yaw;c.parked=false;p.actualSpeed=0;this.emit('sound','door');
    if(!c.owned&&!c.stolen){c.stolen=true;this.addHeat(c.police?38:16);this.emit('toast',c.police?'Vehículo policial sustraído. Te están buscando.':'Vehículo sustraído. Un testigo llamó a la policía.');}
    if(this.story===1&&!this.free){this.story=2;this.pin=null;this.emit('chapter','CARGA SENSIBLE');this.emit('toast','LÍA · Taller del Mercado. Recoge el archivo y no hagas preguntas.');this.emit('save','');}
    return;
   }
   if(kind==='horn'){
    if(p.car!==null&&this.cooldowns.horn<=0){this.actor().horn=1;this.cooldowns.horn=1;this.emit('sound','horn');for(const n of this.peds)if(D.distance(n,p)<22)n.panic=3;}
    return;
   }
   let ctx=this.getContext();if(!ctx||!ctx.action||ctx.action==='car')return;
   if(ctx.action==='story'){this.storyInteract();return;}
   if(ctx.action==='garage'){
    if(this.wanted&&this.seen){this.emit('toast','El mecánico no abre mientras la policía te esté viendo.');return;}
    if(this.cash<200){this.emit('toast','Necesitas $200. Busca un encargo o un alijo.');return;}
    this.cash-=200;let c=p.car!==null?this.actor():this.cars[this.nearestCar(9)];if(c){c.health=100;c.color=CAR_COLORS[Math.floor(this.random()*CAR_COLORS.length)];}
    p.health=100;if(!this.seen){this.heat=0;this.wanted=0;this.resetPolice();}this.emit('toast','Reparación completa. Pintura nueva. Nadie ha visto nada.');this.emit('sound','reward');this.emit('save','');
   }
   if(ctx.action==='safe'){p.health=100;this.emit('toast','Estás a salvo. Salud recuperada y progreso guardado.');this.emit('save','');}
   if(ctx.action==='job'){
    let points=[{x:84,z:-168},{x:-168,z:252},{x:336,z:84},{x:-252,z:-252}];let q=points[Math.floor(this.random()*points.length)];
    this.job={type:'delivery',points:[q],index:0,time:150,reward:650};this.pin=null;this.emit('toast','ENCARGO · Entrega el paquete en menos de 150 segundos.');
   }
   if(ctx.action==='race'){
    if(p.car===null){this.emit('toast','Necesitas un vehículo para participar.');return;}
    this.job={type:'race',points:[{x:-168,z:168},{x:0,z:168},{x:0,z:0},{x:-168,z:0}],index:0,time:90,reward:1000};this.pin=null;this.emit('toast','CIRCUITO · Sigue los cuatro controles. El reloj está corriendo.');
   }
  }
  storyInteract(){
   if(this.awaitingStory!==undefined)return;
   if(this.story===0){this.awaitingStory=0;this.emit('dialog','Te dejé el coche frente a la esquina. Lleva un archivo del taller a mi refugio. Nada de mirar dentro. Vértice paga bien por el silencio, pero esta vez nos paga por conducir.',{speaker:'LÍA',title:'Un encargo sencillo',choices:['Acepto el encargo']});}
   if(this.story===2){this.awaitingStory=2;this.emit('dialog','No es una lista de entregas. Son desalojos, cuentas y nombres de la policía. Vértice nos está siguiendo. Llévalo a mi refugio del Mercado. Y no traigas a nadie detrás.',{speaker:'LÍA',title:'La carga tiene nombres',choices:['Guardar el archivo y salir']});}
   if(this.story===3&&this.wanted===0){this.awaitingStory=3;this.emit('dialog','Los perdimos. Hay una terminal en la zona de Vértice que puede sacar esto de la ciudad. Necesitas transmitir a pie. Una vez que empiece, toda su red de seguridad sabrá dónde estás.',{speaker:'LÍA',title:'No era solo dinero',choices:['Ir a la terminal']});}
   if(this.story===4&&!this.uploading){this.uploading=true;this.upload=0;this.addHeat(28);this.emit('toast','TRANSMISIÓN INICIADA · Permanece a menos de 12 metros durante 12 segundos.');}
   if(this.story===5&&this.wanted===0){this.awaitingStory=5;this.emit('dialog','El archivo está fuera. Todavía podemos liberar el acceso para que toda la ciudad vea quién la está vendiendo. O vender la clave y desaparecer. Yo ya tomé mi decisión. Ahora te toca a ti.',{speaker:'LÍA',title:'¿Qué vale una ciudad?',choices:['Publicar el archivo · $2,400','Vender la clave · $5,000']});}
  }
  confirmStory(choice=0){
   const s=this.awaitingStory;if(s===undefined)return;delete this.awaitingStory;
   if(s===0)this.story=1;
   if(s===2){this.story=3;this.cash+=450;this.addHeat(38);this.emit('toast','La policía ha recibido tu descripción. Rompe su línea de visión.');}
   if(s===3){this.story=4;this.cash+=700;}
   if(s===5){this.story=6;this.ending=choice===1?'vendido':'publicado';this.cash+=choice===1?5000:2400;this.emit('chapter',choice===1?'EL PRECIO DEL SILENCIO':'LA CIUDAD LO SABRÁ');this.emit('toast','HISTORIA COMPLETADA · La ciudad sigue abierta. Explora, encuentra alijos o acepta encargos.');}
   else this.emit('chapter',D.stories[this.story].name);
   this.pin=null;this.emit('sound','reward');this.emit('save','');
  }
  respawn(reason){
   let p=this.player;if(p.car!==null){let c=this.actor();c.speed=0;c.parked=true;}p.car=null;p.x=5;p.z=8;p.y=0;p.vy=0;p.health=100;p.yaw=0;p.actualSpeed=0;
   const fee=reason==='surrender'?D.POLICE.surrenderFee:D.POLICE.arrestFee;
   const paid=Math.min(this.cash,fee);this.cash-=paid;this.heat=0;this.wanted=0;this.resetPolice();this.uploading=false;this.upload=0;this.job=null;this.pin=null;
   this.emit('chapter',reason==='surrender'?'ENTREGA VOLUNTARIA':reason==='arrest'?'INTERCEPTADO':'FUERA DE COMBATE');
   this.emit('toast',`Has regresado al centro. ${reason==='surrender'?'Entrega sin resistencia':'Gastos'}: $${paid}. La historia conserva su progreso.`);this.emit('save','');
  }
  step(dt,input={}){
   if(!Number.isFinite(dt)||dt<=0)return;
   this.time+=dt;const p=this.player,previous={x:p.x,z:p.z};
   for(let k of Object.keys(this.cooldowns))this.cooldowns[k]=Math.max(0,this.cooldowns[k]-dt);
   if(p.car!==null)this.drive(this.actor(),dt,input);else this.walk(dt,input);
   if(p.car!==null){const c=this.actor();p.x=c.x;p.z=c.z;}
   // Speed before separation impulses: being pushed is not voluntary movement.
   p.actualSpeed=D.distance(p,previous)/dt;this.sensePolice();
   for(let i=0;i<this.cars.length;i++){let c=this.cars[i];c.hit=Math.max(0,c.hit-dt);c.horn=Math.max(0,c.horn-dt);if(p.car!==i)this.traffic(c,dt);c.wheel+=c.speed*dt/.37;}
   if(p.car!==null){let c=this.actor();p.x=c.x;p.z=c.z;p.yaw=c.yaw;p.y=0;}
   this.vehicleContacts(dt);this.pedestrians(dt);this.police(dt,input);this.missions(dt);
   this.stats.distance+=D.distance(p,previous);
   if(p.health<=0)this.respawn('health');
   const target=this.target();
   this.routeClock-=dt;
   if(target&&this.routeClock<=0){this.route=this.world.route(p.x,p.z,target.x,target.z);this.routeClock=1;}else if(!target)this.route=[];
   if(this.pin&&D.distance(p,this.pin)<8){this.pin=null;this.emit('toast','Llegaste al destino marcado.');}
  }
  walk(dt,input){
   let p=this.player,f=input.throttle||0,side=input.steer||0,m=Math.hypot(f,side),a=input.lookYaw??p.yaw,targetSpeed=(input.sprint?6.2:3.3)*Math.min(1,m);
   p.moving=m>.05;p.moveSpeed=D.damp(p.moveSpeed,targetSpeed,p.moving?12:9,dt);p.sprintBlend=D.damp(p.sprintBlend,input.sprint&&p.moving?1:0,8,dt);p.landing=Math.max(0,p.landing-dt*4.5);
   let oldYaw=p.yaw;
   if(m>0){f/=Math.max(1,m);side/=Math.max(1,m);let speed=input.sprint?6.2:3.3,dx=(Math.sin(a)*f-Math.cos(a)*side)*speed*dt,dz=(Math.cos(a)*f+Math.sin(a)*side)*speed*dt;
    let q=this.world.move(p.x,p.z,dx,dz,.38);p.x=q.x;p.z=q.z;p.yaw=D.turn(p.yaw,Math.atan2(dx,dz),dt*10);p.walk+=dt*(5.6+p.sprintBlend*2.8)*Math.min(1,m);}
   p.turnRate=D.damp(p.turnRate,dt>0?D.wrap(p.yaw-oldYaw)/dt:0,9,dt);
   let wasGrounded=p.grounded;
   if(input.brake&&p.y<=0&&p.vy===0){p.vy=5;p.grounded=false;}
   p.vy-=14*dt;p.y=Math.max(0,p.y+p.vy*dt);
   if(p.y===0){if(!wasGrounded&&p.vy<0)p.landing=1;p.vy=0;p.grounded=true;}else p.grounded=false;
  }
  drive(c,dt,input){
   const throttle=input.throttle||0,steer=input.steer||0;let acc=throttle>=0?13:10;
   if(throttle!==0){if(Math.sign(c.speed)!==Math.sign(throttle)&&Math.abs(c.speed)>1)acc=24;c.speed+=throttle*acc*dt;}
   c.speed*=Math.exp(-(input.brake?3.1:throttle===0?.38:.13)*dt);
   c.speed=D.clamp(c.speed,-11,c.health<15?15:42);
   const turn=(.22+1.35/(1+Math.abs(c.speed)*.11))*D.clamp(Math.abs(c.speed)/3,0,1);
   c.yaw-=steer*turn*Math.sign(c.speed||1)*dt*(input.brake?1.9:1);
   let dx=Math.sin(c.yaw)*c.speed*dt,dz=Math.cos(c.yaw)*c.speed*dt,q=this.world.move(c.x,c.z,dx,dz,1.12);
   c.x=q.x;c.z=q.z;c.brake=input.brake||throttle<0?1:0;
   if(q.hit&&Math.abs(c.speed)>2){let impact=Math.abs(c.speed);c.speed*=-.28;c.health=Math.max(5,c.health-impact*.42);this.player.health-=impact*.08;
    if(this.cooldowns.crash<=0){this.emit('sound','crash');this.cooldowns.crash=.6;c.hit=.4;}
   }
  }
  traffic(c,dt){
   if(dt<=0)return;
   if(c.parked){c.speed=D.damp(c.speed,0,6,dt);return;}
   const p=this.player,dist=D.distance(c,p),pursuit=c.police&&!c.stolen&&this.wanted>0;
   if(c.police&&c.id>42&&this.wanted<3&&dist>85){c.speed=0;return;}
   if(dist>260&&!pursuit){c.speed=0;return;}
   if(pursuit&&c.recoverUntil>this.time){
    // A real short reversing manoeuvre after impact, not teleportation or ghosting.
    c.aiMode='recover';c.speed=D.damp(c.speed,c.recoverDir*4.5,7,dt);c.brake=1;
    let q=this.world.move(c.x,c.z,Math.sin(c.yaw)*c.speed*dt,Math.cos(c.yaw)*c.speed*dt,1.1);c.x=q.x;c.z=q.z;
    if(q.hit){c.speed*=.5;c.yaw+=dt*(c.id%2?1:-1);}
    c.navTime=0;return;
   }
   const known=this.policeState.lastSeen;
   const sees=pursuit&&dist<D.POLICE.sightRange&&this.world.visible(c.x,c.z,p.x,p.z);
   let direct=sees&&dist<50,target=null;
   c.aiMode=pursuit?(this.seen?'pursuit':'search'):'patrol';c.navTime-=dt;
   if(pursuit&&c.navTime<=0&&known){
    // Only observed or reported positions enter the navigation system.
    let destination=known;
    if(!this.seen&&D.distance(c,known)<22){
     const origin=this.world.node(known.x,known.z),dirs=[[0,1],[1,0],[0,-1],[-1,0]],d=dirs[(c.id+Math.floor(this.unseen/5))%4];
     destination={x:D.clamp(origin.x+d[0]*84,-(this.world.coordinateLimit||420),(this.world.coordinateLimit||420)),z:D.clamp(origin.z+d[1]*84,-(this.world.coordinateLimit||420),(this.world.coordinateLimit||420))};
    }
    c.route=this.world.route(c.x,c.z,destination.x,destination.z);
    if(c.route.length>1&&D.distance(c,c.route[0])<20)c.route.shift();
    // Add the precise last-known point to the road route when approaching it.
    if(destination===known)c.route.push({x:known.x,z:known.z});
    c.navTime=1.2;
   }
   if(!c.route.length)this.newTrafficRoute(c);
   target=direct?p:c.route[0];if(!target)return;
   let tdx=target.x-c.x,tdz=target.z-c.z;
   if(!direct){if(Math.abs(tdz)>Math.abs(tdx))tdx+=Math.sign(tdz)*4;else tdz-=Math.sign(tdx)*4;}
   let a=Math.atan2(tdx,tdz),angle=Math.abs(D.wrap(a-c.yaw));
   let desired=pursuit?Math.min(27,12+this.wanted*3):9+(c.id%4)*1.3;
   desired*=angle>1.2?.26:angle>.6?.48:1;
   if(direct){
    const actor=this.actor(),gap=p.car===null?2.9:5.9;
    const targetForward=p.car===null?(p.actualSpeed||0)*Math.cos(D.wrap(p.yaw-c.yaw)):actor.speed*Math.cos(D.wrap(actor.yaw-c.yaw));
    // Maintain a bumper gap. Stopping a suspect never means driving at their centre.
    desired=Math.min(desired,Math.max(0,(dist-gap)*1.7+Math.max(0,targetForward)));
   }
   for(const other of this.cars){if(other===c)continue;let dx=other.x-c.x,dz=other.z-c.z,forward=dx*Math.sin(c.yaw)+dz*Math.cos(c.yaw),lateral=Math.abs(dx*Math.cos(c.yaw)-dz*Math.sin(c.yaw));
    if(forward>0&&forward<9&&lateral<1.9)desired=Math.min(desired,Math.max(0,(forward-4.9)*2));}
   c.brake=desired<c.speed-1?1:0;c.speed=D.damp(c.speed,desired,desired<c.speed?6:2.5,dt);
   c.yaw=D.turn(c.yaw,a,dt*(pursuit?1.7:1.25));
   let q=this.world.move(c.x,c.z,Math.sin(c.yaw)*c.speed*dt,Math.cos(c.yaw)*c.speed*dt,1.1);
   c.x=q.x;c.z=q.z;
   if(q.hit){c.speed*=.6;c.yaw=D.turn(c.yaw,a,dt*3);c.navTime=0;}
   if(!direct&&Math.hypot(tdx,tdz)<8){c.route.shift();if(!c.route.length)this.newTrafficRoute(c);}
  }
  vehicleContacts(dt){
   if(dt<=0)return;
   const p=this.player,playerCar=p.car!==null?this.actor():null;
   const nearby=this.cars.filter(c=>D.distance(c,p)<150);
   for(let i=0;i<nearby.length;i++)for(let j=i+1;j<nearby.length;j++){
    const a=nearby[i],b=nearby[j],hit=D.vehicleOverlap(a,b);if(!hit)continue;
    const key=a.id<b.id?`${a.id}:${b.id}`:`${b.id}:${a.id}`;
    let record=this.contactRecords.get(key);const fresh=!record||this.time-record.touch>.15;
    if(!record){record={touch:this.time,impact:-Infinity};this.contactRecords.set(key,record);}record.touch=this.time;
    const af=hit.x*Math.sin(a.yaw)+hit.z*Math.cos(a.yaw),bf=hit.x*Math.sin(b.yaw)+hit.z*Math.cos(b.yaw);
    const approachA=-a.speed*af,approachB=b.speed*bf;
    // Resolve overlap independently of speed. Tangential/sliding velocity is preserved.
    const push=(hit.depth+.004)*.5;
    const qa=this.world.move(a.x,a.z,hit.x*push,hit.z*push,1.1),qc=this.world.move(b.x,b.z,-hit.x*push,-hit.z*push,1.1);
    const moved=(qa.x-a.x)*hit.x+(qa.z-a.z)*hit.z+(b.x-qc.x)*hit.x+(b.z-qc.z)*hit.z;
    a.x=qa.x;a.z=qa.z;b.x=qc.x;b.z=qc.z;
    if(moved<hit.depth){
     const rest=hit.depth-moved+.004;
     // Give remaining clearance to the body that isn't trapped against a building.
     if(!qc.hit){const q=this.world.move(b.x,b.z,-hit.x*rest,-hit.z*rest,1.1);b.x=q.x;b.z=q.z;}
     else if(!qa.hit){const q=this.world.move(a.x,a.z,hit.x*rest,hit.z*rest,1.1);a.x=q.x;a.z=q.z;}
    }
    if(hit.closing>.05){const impulse=hit.closing*.53;a.speed+=impulse*af;b.speed-=impulse*bf;}
    const involved=a===playerCar||b===playerCar,other=a===playerCar?b:a;
    if(involved&&other.police&&!other.stolen&&this.wanted&&fresh&&this.time>=(other.recoverCooldown||0)&&!this.policeState.surrender){
     const forward=(playerCar.x-other.x)*Math.sin(other.yaw)+(playerCar.z-other.z)*Math.cos(other.yaw);
     other.recoverDir=forward>=0?-1:1;other.recoverUntil=this.time+D.POLICE.recoverySeconds;other.recoverCooldown=this.time+D.POLICE.recoveryCooldown;
     this.policeState.graceUntil=this.time+D.POLICE.impactGrace;this.policeState.contactHintUntil=this.time+3.5;
    }
    if(involved&&hit.closing>5&&this.time-record.impact>1){
     record.impact=this.time;playerCar.health=Math.max(5,playerCar.health-hit.closing*.22);p.health-=hit.closing*.025;
     playerCar.hit=.35;if(this.cooldowns.crash<=0){this.emit('sound','crash');this.cooldowns.crash=.5;}
     const playerApproach=a===playerCar?approachA:approachB,otherApproach=a===playerCar?approachB:approachA;
     if(playerApproach>5&&playerApproach>otherApproach*.7&&this.cooldowns.crime<=0){this.addHeat(other.police?18:7);this.cooldowns.crime=3;}
    }
   }
   for(const [key,value] of this.contactRecords)if(this.time-value.touch>3)this.contactRecords.delete(key);
   if(playerCar){p.x=playerCar.x;p.z=playerCar.z;}
  }
  pedestrians(dt){
   const p=this.player,car=p.car!==null?this.actor():null;
   for(let n of this.peds){if(n.hidden||D.distance(n,p)>145)continue;n.panic=Math.max(0,n.panic-dt);
    if(car&&Math.abs(car.speed)>5&&D.distance(n,car)<9)n.panic=3;
    let speed=n.speed*(n.panic?2.8:1);
    let direction=n.yaw;
    if(n.panic&&car)direction=Math.atan2(n.x-car.x,n.z-car.z);
    let q=this.world.move(n.x,n.z,Math.sin(direction)*speed*dt,Math.cos(direction)*speed*dt,.35);const travelled=D.distance(n,q);n.x=q.x;n.z=q.z;n.moveSpeed=travelled/Math.max(dt,.001);n.phase+=travelled*(D.NaturalMotion?D.NaturalMotion.distanceRate(n.moveSpeed,n.panic?.5:0):3);
    if(q.hit||n.z<n.homeZ+10||n.z>n.homeZ+74)n.yaw=D.wrap(n.yaw+Math.PI);
    if(car&&D.distance(n,car)<1.8&&Math.abs(car.speed)>4&&this.cooldowns.crime<=0){this.addHeat(18);this.cooldowns.crime=3;n.panic=8;this.emit('toast','Un peatón ha dado la alarma. La policía busca tu vehículo.');}
   }
  }
  sensePolice(){
   const p=this.player;let saw=false;
   for(const c of this.cars){c.sight=!!(this.wanted&&c.police&&!c.stolen&&c!==this.actor()&&D.distance(p,c)<D.POLICE.sightRange&&this.world.visible(c.x,c.z,p.x,p.z));if(c.sight)saw=true;}
   this.seen=saw;
   if(saw){this.policeState.lastSeen={x:p.x,z:p.z};this.policeState.lastSeenTime=this.time;}
   return saw;
  }
  actualSpeed(){return this.player.car!==null?Math.max(Math.abs(this.actor().speed),this.player.actualSpeed||0):(this.player.actualSpeed||0);}
  canSurrender(){
   if(!this.wanted||this.actualSpeed()>.7)return false;
   return this.cars.some(c=>c.police&&!c.stolen&&c!==this.actor()&&D.distance(c,this.player)<D.POLICE.surrenderRange&&this.world.visible(c.x,c.z,this.player.x,this.player.z));
  }
  police(dt,input={}){
   if(dt<=0)return;
   const C=D.POLICE,p=this.player,state=this.policeState,saw=this.sensePolice();
   if(this.wanted){
    const previousUnseen=this.unseen;
    if(saw){this.unseen=0;state.searchHeat=this.heat;}else{if(this.unseen===0)state.searchHeat=this.heat;this.unseen+=dt;}
    const decayTime=saw?0:Math.max(0,this.unseen-C.searchDelay)-Math.max(0,previousUnseen-C.searchDelay);
    if(decayTime>0)this.heat=Math.max(0,this.heat-decayTime*C.heatDecay);
    const movingInput=Math.abs(input.throttle||0)>.1||Math.abs(input.steer||0)>.1||input.brake||input.sprint;
    if(input.surrender&&!movingInput&&this.canSurrender()){
     state.surrender+=dt;this.bust=Math.max(0,this.bust-dt*C.arrestDecay);
     if(state.surrender>=C.surrenderSeconds){this.respawn('surrender');return;}
    }else{
     state.surrender=0;
     const inCar=p.car!==null,range=inCar?C.carArrestRange:C.footArrestRange;
     const near=this.cars.some(c=>c.sight&&D.distance(c,p)<range);
     const stopped=this.actualSpeed()<(inCar?C.carArrestSpeed:C.footArrestSpeed);
     if(near&&stopped&&this.time>=state.graceUntil)this.bust+=dt/(inCar?C.carArrestSeconds:C.footArrestSeconds);
     else this.bust=Math.max(0,this.bust-dt*C.arrestDecay);
     if(this.bust>=1){this.respawn('arrest');return;}
    }
   }else{this.bust=0;state.surrender=0;}
   const before=this.wanted;this.wanted=Math.ceil(this.heat/20);
   if(before>0&&this.wanted===0){this.stats.escapes++;this.resetPolice();this.emit('toast','BÚSQUEDA CANCELADA · Has desaparecido del radar.');this.emit('sound','reward');}
  }
  getPoliceStatus(){
   const s=this.policeState,C=D.POLICE,phase=!this.wanted?'patrol':s.surrender>0?'surrender':this.bust>.03?'arrest':this.seen?'pursuit':'search';
   const labels={patrol:'SIN BÚSQUEDA',pursuit:'PERSECUCIÓN ACTIVA',search:'BUSCAN TU ÚLTIMA POSICIÓN',arrest:'RIESGO DE DETENCIÓN',surrender:'ENTREGA VOLUNTARIA'};
   let hint=phase==='search'?'Ocúltate tras edificios. No conocen tu posición actual.':this.player.car!==null?'Usa reversa y dirección. Un contacto no equivale a un arresto.':'Corre para ganar distancia y busca cobertura.';
   if(phase==='arrest')hint='Muévete o rompe la línea de visión para reducir la captura.';
   if(this.time<s.contactHintUntil&&phase==='pursuit')hint='La patrulla está recolocándose. Aprovecha el espacio para maniobrar.';
   if(phase==='surrender')hint='Mantén pulsado. Suelta o muévete para cancelar.';
   return{phase,label:labels[phase],hint,capture:D.clamp(this.bust,0,1),surrenderAvailable:this.canSurrender(),surrenderProgress:D.clamp(s.surrender/C.surrenderSeconds,0,1),searchProgress:phase==='search'?D.clamp(1-this.heat/Math.max(1,s.searchHeat),0,1):0,searchSeconds:Math.ceil(Math.max(0,C.searchDelay-this.unseen)+this.heat/C.heatDecay)};
  }
  missions(dt){
   const p=this.player;
   if(this.uploading){const t=D.stories[4];if(D.distance(p,t)<12&&p.car===null){this.upload+=dt;if(this.upload>=12){this.story=5;this.uploading=false;this.cash+=900;this.addHeat(55);this.pin=null;this.emit('chapter','ÚLTIMA SALIDA');this.emit('toast','Archivo transmitido. Pierde a la policía y busca a Lía en el muelle.');this.emit('save','');}}
    else{this.upload=Math.max(0,this.upload-dt*.5);}}
   if(this.job){this.job.time-=dt;const goal=this.job.points[this.job.index];
    if(D.distance(p,goal)<11&&(this.job.type!=='race'||p.car!==null)){this.job.index++;this.emit('sound','reward');if(this.job.index>=this.job.points.length){this.cash+=this.job.reward;this.stats.jobs++;this.emit('toast',`TRABAJO COMPLETADO · +$${this.job.reward.toLocaleString('es-MX')}`);this.job=null;this.emit('save','');}else this.emit('toast',`CONTROL ${this.job.index}/${this.job.points.length} · Continúa.`);}
    if(this.job&&this.job.time<=0){this.job=null;this.emit('toast','El encargo ha caducado. Puedes aceptar otro.');}}
   for(let c of this.world.crates)if(!this.collected.includes(c.id)&&D.distance(p,c)<2.6&&p.car===null){this.collected.push(c.id);this.cash+=150;this.emit('toast',`ALIJO ENCONTRADO · +$150 · ${this.collected.length}/16`);this.emit('sound','reward');this.emit('save','');}
  }
  serialize(){
   let c=this.player.car!==null?this.actor():null;
   return{version:1,seed:this.world.seed,cash:this.cash,story:this.story,free:this.free,ending:this.ending,heat:this.heat,time:this.time,player:{x:this.player.x,z:this.player.z,yaw:this.player.yaw,health:this.player.health},vehicle:c?{x:c.x,z:c.z,yaw:c.yaw,health:c.health,color:c.color,police:c.police,stolen:c.stolen}:null,collected:[...this.collected],stats:{...this.stats}};
  }
  restore(data){
   if(!data||data.version!==1||!data.player||!Number.isFinite(data.player.x)||!Number.isFinite(data.player.z)||!Number.isFinite(data.cash)||!Number.isInteger(data.story)||data.story<0||data.story>6)return false;
   const p=data.player;if(Math.abs(p.x)>(this.world.coordinateLimit||426)||Math.abs(p.z)>(this.world.coordinateLimit||426))return false;
   this.cash=D.clamp(data.cash,0,1e8);this.story=data.story;this.free=!!data.free;this.ending=['publicado','vendido'].includes(data.ending)?data.ending:null;this.time=Number.isFinite(data.time)?Math.max(0,data.time):0;this.heat=D.clamp(Number(data.heat)||0,0,100);this.wanted=Math.ceil(this.heat/20);
   this.player.x=p.x;this.player.z=p.z;this.player.yaw=Number.isFinite(p.yaw)?p.yaw:0;this.player.health=D.clamp(Number(p.health)||100,1,100);this.player.car=null;
   if(this.world.blocked(p.x,p.z,.4)){this.player.x=5;this.player.z=8;}
   const v=data.vehicle;if(v&&[v.x,v.z,v.yaw].every(Number.isFinite)&&Math.abs(v.x)<=(this.world.coordinateLimit||425)&&Math.abs(v.z)<=(this.world.coordinateLimit||425)&&!this.world.blocked(v.x,v.z,1.12)){
    const c=this.cars[0];c.police=!!v.police;c.stolen=!!v.stolen;c.x=v.x;c.z=v.z;c.yaw=v.yaw;c.health=D.clamp(Number(v.health)||100,5,100);if(Array.isArray(v.color)&&v.color.length===3&&v.color.every(Number.isFinite))c.color=v.color.map(x=>D.clamp(x,0,1));c.speed=0;this.player.car=0;this.player.x=c.x;this.player.z=c.z;
   }
   this.collected=Array.isArray(data.collected)?[...new Set(data.collected.filter(x=>Number.isInteger(x)&&x>=0&&x<16))]:[];
   if(data.stats)for(let k of ['distance','jobs','escapes'])if(Number.isFinite(data.stats[k]))this.stats[k]=D.clamp(data.stats[k],0,1e9);
   this.job=null;this.upload=0;this.uploading=false;this.pin=null;this.player.actualSpeed=0;this.resetPolice();if(this.wanted){this.policeState.lastSeen={x:this.player.x,z:this.player.z};this.policeState.searchHeat=this.heat;}return true;
  }
 }
 D.Simulation=Simulation;
})(DC);
