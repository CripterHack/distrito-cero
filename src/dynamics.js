/* Ciudad reactiva. State, contacts and effects live in the simulation, not GPU buffers. */
'use strict';
(function(D){
 const TYPES=D.PROP_TYPES=Object.freeze({
  lamp:{label:'Poste de luz',radius:.22,height:7.4,mass:95,health:68,hinged:true,material:'metal',color:[.13,.18,.19]},
  tree:{label:'Árbol',radius:.33,height:5.6,mass:310,health:135,hinged:true,material:'wood',color:[.18,.13,.08]},
  crate:{label:'Caja de madera',radius:.38,height:.64,mass:8,health:27,carry:true,material:'wood',color:[.32,.24,.14]},
  bin:{label:'Bote de reciclaje',radius:.43,height:1.02,mass:21,health:65,material:'metal',color:[.075,.24,.23]},
  cone:{label:'Cono de tránsito',radius:.25,height:.60,mass:2,health:18,carry:true,material:'plastic',color:[.78,.29,.045]},
  bench:{label:'Banca',radius:.86,height:.72,mass:58,health:70,material:'wood',color:[.27,.20,.12]}
 });
 D.ensureVehicle=function(c){
  if(!c.damage)c.damage={front:0,rear:0,left:0,right:0};
  if(!c.suspension)c.suspension={pitch:0,roll:0,kick:0};
  if(!Number.isFinite(c.steerAngle))c.steerAngle=0;return c;
 };
 D.damageVehicle=function(c,amount,x,z){
  D.ensureVehicle(c);if(!Number.isFinite(amount)||amount<=0)return null;
  const dx=x-c.x,dz=z-c.z,u=dx*Math.cos(c.yaw)-dz*Math.sin(c.yaw),v=dx*Math.sin(c.yaw)+dz*Math.cos(c.yaw);
  const side=Math.abs(v)/2.23>Math.abs(u)?(v>=0?'front':'rear'):(u>=0?'right':'left');
  c.damage[side]=D.clamp(c.damage[side]+amount/55,0,1);c.health=D.clamp(c.health-amount*.50,5,100);
  c.suspension.kick=D.clamp(c.suspension.kick+amount*.004,0,.18);c.hit=Math.max(c.hit||0,.3);
  return side;
 };
 D.repairVehicle=function(c){D.ensureVehicle(c);c.health=100;for(const k of Object.keys(c.damage))c.damage[k]=0;c.hit=0;c.suspension.kick=0;};
 class SpatialHash{
  constructor(size=12){this.size=size;this.cells=new Map();}
  key(x,z){return Math.floor(x/this.size)+':'+Math.floor(z/this.size);}
  rebuild(items){this.cells.clear();for(const item of items){const key=this.key(item.x,item.z);let cell=this.cells.get(key);if(!cell)this.cells.set(key,cell=[]);cell.push(item);}}
  query(x,z,r){const out=[],n=this.size;for(let i=Math.floor((x-r)/n);i<=Math.floor((x+r)/n);i++)for(let j=Math.floor((z-r)/n);j<=Math.floor((z+r)/n);j++){const cell=this.cells.get(i+':'+j);if(cell)for(const p of cell)if(Math.hypot(x-p.x,z-p.z)<=r+p.radius)out.push(p);}return out;}
 }
 class ReactiveWorld{
  constructor(sim){
   this.sim=sim;this.world=sim.world;this.props=[];this.byId=new Map();this.hash=new SpatialHash();this.particles=[];this.marks=[];this.random=D.rng(937);this.contactTimes=new Map();this.lightRevision=0;this.impacts=0;
   this.world.lights.forEach((l,i)=>this.add('lamp',l.x,l.z,'lamp:'+i,{lightIndex:i,warm:l.warm}));
   for(let j=-4;j<5;j++){
    this.add('tree',13.5,j*84+52,'tree:street:'+j);this.add('tree',-13.5,j*84+28,'tree:west:'+j,{scale:1.15});
    this.add('bin',14.2,j*84+32,'bin:'+j);this.add('bench',-13.9,j*84+46,'bench:'+j);
   }
   for(const [i,b] of this.world.blocks.entries())if(b.park){const r=D.rng(i+63);for(let k=0;k<18;k++){const x=b.x+(r()-.5)*48,z=b.z+(r()-.5)*48;if(Math.abs(x-b.x)>4&&Math.abs(z-b.z)>4)this.add('tree',x,z,`tree:park:${i}:${k}`,{scale:1+r()*.45});}}
   // Discoverable verbs beside the initial crossing. Keep the car and story telephone unobstructed.
   this.add('crate',10.9,7,'intro:crate:0');this.add('crate',11,5.8,'intro:crate:1');this.add('cone',9.9,4,'intro:cone');this.add('bin',-11,16,'intro:bin');
   for(let j=-3;j<=3;j++)for(let i=-3;i<=3;i++)if((i+j)%2===0){this.add('crate',i*84+12.4,j*84+37,`crate:${i}:${j}`);this.add('cone',i*84-11,j*84+15,`cone:${i}:${j}`);}
   this.hash.rebuild(this.props);
  }
  add(type,x,z,id,extra={}){
   const def=TYPES[type],p={...def,id,type,x,z,homeX:x,homeZ:z,y:0,vx:0,vz:0,vy:0,yaw:0,spin:0,angle:0,angularVelocity:0,fallYaw:0,health:def.health,maxHealth:def.health,broken:false,held:false,changed:false,scale:1,...extra};
   this.props.push(p);this.byId.set(id,p);return p;
  }
  lightActive(index){return !this.byId.get('lamp:'+index)?.broken;}
  burst(x,y,z,material,count=10){
   const r=this.random,col=material==='metal'?[.94,.63,.22]:material==='glass'?[.41,.70,.76]:material==='smoke'?[.11,.13,.135]:[.34,.24,.13];
   for(let i=0;i<count;i++){if(this.particles.length>=180)this.particles.shift();const smoke=material==='smoke';this.particles.push({x,y,z,vx:(r()-.5)*(smoke?.35:5),vz:(r()-.5)*(smoke?.35:5),vy:smoke?.7+r()*.4:1+r()*4,life:smoke?1.6:1+r()*1.2,total:smoke?1.6:2.2,size:smoke?.24+r()*.1:.018+r()*.045,color:col,material,angle:r()*6});}
  }
  mark(x,z,yaw){if(this.marks.length>=120)this.marks.shift();this.marks.push({x,z,yaw,life:22});}
  impactProp(p,speed,nx,nz){
   if(p.broken||p.held||!Number.isFinite(speed)||speed<=1.5)return false;
   const damage=(speed-1.5)**2*(p.type==='tree'?.52:.9);p.health=Math.max(0,p.health-damage);p.changed=true;
   if(p.health<=0){
    p.broken=true;p.fallYaw=Math.atan2(nx,nz);p.angularVelocity=p.hinged?.25:0;p.angle=0;this.impacts++;
    this.burst(p.x,Math.min(p.height*.3,1.8),p.z,p.material,p.type==='lamp'?18:12);
    if(p.type==='lamp')this.lightRevision++;
    if(!p.hinged){p.vx+=nx*speed*.35;p.vz+=nz*speed*.35;p.vy=Math.min(4,speed*.12);p.spin=(this.random()-.5)*5;}
    if(D.distance(p,this.sim.player)<35){this.sim.emit('sound','crash');this.sim.impactLabel=`${p.label.toUpperCase()} · ${p.hinged?'DERRIBADO':'ROTO'}`;this.sim.impactUntil=this.sim.time+2.2;}
    return true;
   }
   return false;
  }
  carContacts(c,dt){
   D.ensureVehicle(c);const speed=Math.abs(c.speed),co=Math.cos(c.yaw),si=Math.sin(c.yaw);
   for(const p of this.hash.query(c.x,c.z,4.1)){
    if(p.held||p.broken||p.y>1.7||!D.vehicleContains(c,p.x,p.z,p.radius))continue;
    let dx=p.x-c.x,dz=p.z-c.z,u=dx*co-dz*si,v=dx*si+dz*co;
    const penX=1+p.radius-Math.abs(u),penZ=2.23+p.radius-Math.abs(v);
    let nx,nz,pen;if(penX<penZ){const s=Math.sign(u)||1;nx=co*s;nz=-si*s;pen=penX;}else{const s=Math.sign(v)||1;nx=si*s;nz=co*s;pen=penZ;}
    if(pen<=0)continue;
    const closing=Math.max(0,c.speed*(si*nx+co*nz)-p.vx*nx-p.vz*nz),key=c.id+':'+p.id,last=this.contactTimes.get(key)??-Infinity;
    if(closing>2&&this.sim.time-last>.65){
     this.contactTimes.set(key,this.sim.time);this.impactProp(p,closing,nx,nz);
     const strength=closing*(p.hinged?.9:.28);D.damageVehicle(c,strength,p.x,p.z);
     this.sim.trauma=Math.min(.65,(this.sim.trauma||0)+strength*.012);
     if(c===this.sim.actor()&&this.sim.player.car!==null&&closing>8&&this.sim.cooldowns.crime<=0){this.sim.addHeat(p.type==='tree'?3:2);this.sim.cooldowns.crime=4;}
    }
    if(p.broken){c.speed*=p.hinged?.77:.94;continue;}
    if(!p.hinged){
     const q=this.world.move(p.x,p.z,nx*(pen+.015),nz*(pen+.015),p.radius);p.x=q.x;p.z=q.z;p.changed=true;
     p.vx+=nx*Math.min(12,Math.max(closing*.8,.2));p.vz+=nz*Math.min(12,Math.max(closing*.8,.2));p.spin+=(nx+nz)*closing*.15;
     if(closing>2)c.speed*=1-Math.min(.12,p.mass/1500);
     if(!q.hit)continue;
    }
    // Separate position first, remove only velocity into the obstacle. No contact drag.
    const q=this.world.move(c.x,c.z,-nx*(pen+.015),-nz*(pen+.015),1.05);c.x=q.x;c.z=q.z;
    const dot=si*nx+co*nz;if(closing>0)c.speed-=closing*dot*1.1;
   }
   for(const [k,t]of this.contactTimes)if(this.sim.time-t>3)this.contactTimes.delete(k);
   if(speed>12&&c.brake&&this.sim.time-(c.lastMark||0)>.08){c.lastMark=this.sim.time;for(const side of [-1,1])this.mark(c.x+side*.82*co-si*1.3,c.z-side*.82*si-co*1.3,c.yaw);}
  }
  footContacts(p){
   for(const o of this.hash.query(p.x,p.z,1.5)){
    if(o.held||o.broken||p.y>o.height-.1||o.y>1.5)continue;
    let dx=p.x-o.x,dz=p.z-o.z,d=Math.hypot(dx,dz),min=.32+o.radius;if(d>=min)continue;
    if(d<.001){dx=-Math.sin(p.yaw);dz=-Math.cos(p.yaw);d=1;}
    const nx=dx/d,nz=dz/d;
    if(!o.hinged&&o.mass<60){o.vx-=nx*(p.moveSpeed||0)*.7;o.vz-=nz*(p.moveSpeed||0)*.7;const q=this.world.move(o.x,o.z,-nx*(min-d)*.8,-nz*(min-d)*.8,o.radius);o.x=q.x;o.z=q.z;o.changed=true;}
    const q=this.world.move(p.x,p.z,nx*(min-d+.005),nz*(min-d+.005),.32);p.x=q.x;p.z=q.z;
    if(o.hinged&&p.moveSpeed>3&&this.sim.time>(p.impactCooldown||0)){p.stagger=.35;p.impactCooldown=this.sim.time+.7;}
   }
  }
  update(dt){
   const s=this.sim,p=s.player;
   for(const o of this.props){
    if(o.held){o.x=p.x+Math.sin(p.yaw)*.54;o.z=p.z+Math.cos(p.yaw)*.54;o.y=p.y+1.02-(p.crouch||0)*.22;o.yaw=p.yaw;continue;}
    // The crown or lamp arm meets the ground before the trunk is completely horizontal.
    if(o.hinged){const rest=o.type==='lamp'?1.34:1.10;if(o.broken&&o.angle<rest){o.angularVelocity+=dt*(.9+3.6*Math.sin(o.angle));o.angle=Math.min(rest,o.angle+o.angularVelocity*dt);if(o.angle===rest){o.angularVelocity=0;this.burst(o.x+Math.sin(o.fallYaw)*o.height*.6,.4,o.z+Math.cos(o.fallYaw)*o.height*.6,o.material,8);}}continue;}
    if(Math.hypot(o.vx,o.vz)>.01||o.y>.001||Math.abs(o.vy)>.01){
     const q=this.world.move(o.x,o.z,o.vx*dt,o.vz*dt,o.radius*.8);if(q.hit){o.vx*=-.35;o.vz*=-.35;}o.x=q.x;o.z=q.z;
     o.vy-=9.81*dt;o.y+=o.vy*dt;if(o.y<0){o.y=0;o.vy=Math.abs(o.vy)>1?-o.vy*.23:0;}
     const drag=o.y<.01?4.5:.22;o.vx*=Math.exp(-drag*dt);o.vz*=Math.exp(-drag*dt);o.yaw+=o.spin*dt;o.spin*=Math.exp(-drag*dt);o.changed=true;
     // Flying props can hit vehicles, but a settled object does not repeatedly damage them.
     if(Math.hypot(o.vx,o.vz)>3&&o.y<1.5&&s.time>(o.hitUntil||0))for(const c of s.cars){if(D.distance(o,c)<3&&D.vehicleContains(c,o.x,o.z,o.radius)){const v=Math.hypot(o.vx,o.vz);D.damageVehicle(c,v*.35,o.x,o.z);o.vx*=-.32;o.vz*=-.32;o.hitUntil=s.time+.7;this.burst(o.x,o.y+.3,o.z,o.material,4);break;}}
    }
   }
   for(let i=this.particles.length-1;i>=0;i--){const f=this.particles[i];f.life-=dt;if(f.life<=0){this.particles.splice(i,1);continue;}f.x+=f.vx*dt;f.z+=f.vz*dt;f.y+=f.vy*dt;if(f.material==='smoke'){f.size+=dt*.19;}else{f.vy-=9*dt;if(f.y<.03){f.y=.03;f.vy=Math.abs(f.vy)*.22;f.vx*=.9;f.vz*=.9;}}f.angle+=dt*2;}
   for(let i=this.marks.length-1;i>=0;i--){this.marks[i].life-=dt;if(this.marks[i].life<=0)this.marks.splice(i,1);}
   this.hash.rebuild(this.props);
  }
  serialize(){return{props:this.props.filter(p=>p.changed).map(p=>({id:p.id,x:p.x,z:p.z,yaw:p.yaw,health:p.health,broken:p.broken,angle:p.angle,fallYaw:p.fallYaw}))};}
  validate(data){
   if(data===undefined)return true;
   if(!data||!Array.isArray(data.props)||data.props.length>this.props.length)return false;
   const ids=new Set();for(const p of data.props){if(!p||!this.byId.has(p.id)||ids.has(p.id)||![p.x,p.z,p.health].every(Number.isFinite)||Math.abs(p.x)>450||Math.abs(p.z)>450||p.health<0||p.health>this.byId.get(p.id).maxHealth)return false;ids.add(p.id);for(const k of ['yaw','angle','fallYaw'])if(p[k]!==undefined&&!Number.isFinite(p[k]))return false;}
   return true;
  }
  restore(data){
   for(const p of this.props){Object.assign(p,{x:p.homeX,z:p.homeZ,y:0,vx:0,vz:0,vy:0,health:p.maxHealth,broken:false,angle:0,angularVelocity:0,held:false,changed:false});}
   if(data)for(const q of data.props){const p=this.byId.get(q.id);Object.assign(p,{x:q.x,z:q.z,yaw:D.wrap(q.yaw||0),health:q.health,broken:!!q.broken,angle:D.clamp(q.angle||0,0,p.type==='lamp'?1.34:1.10),fallYaw:D.wrap(q.fallYaw||0),changed:true});}
   this.particles=[];this.marks=[];this.contactTimes.clear();this.lightRevision++;this.hash.rebuild(this.props);
  }
 }
 D.SpatialHash=SpatialHash;D.ReactiveWorld=ReactiveWorld;
})(DC);
