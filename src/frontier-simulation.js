'use strict';
(function(D){
 const Base=D.Simulation, LIMIT=D.Frontier.LIMIT;
 const DELTA_FIELDS=['id','x','z','yaw','health','broken','angle','fallYaw'];
 const delta=o=>Object.fromEntries(DELTA_FIELDS.map(k=>[k,o[k]]));
 class FrontierSimulation extends Base{
  constructor(world){
   if(world.home){world.buildings=world.home.buildings;world.blocks=world.home.blocks;world.lights=world.home.lights;world.pois=world.home.pois;world.activeKey='';}
   super(world);this.homeProps=[...this.dynamics.props];this.streamProps=new Map();this.changes=new Map();this.sectorVisits=new Set();this.recycleClock=0;this.setLightLookup();this.syncRegion();
  }
  setLightLookup(){this.dynamics.lightActive=index=>!this.dynamics.byId.get(this.world.lights[index]?.id||'lamp:'+index)?.broken;}
  archive(){for(const o of this.streamProps.values())if(o.changed){if(this.changes.size>=4096&&!this.changes.has(o.id)){if(!this.deltaWarning){this.emit('toast','Límite de 4096 cambios persistentes. Los nuevos daños lejanos no se archivarán.');this.deltaWarning=true;}continue;}this.changes.set(o.id,delta(o));}}
  syncRegion(){
   if(!this.world.focus(this.player.x,this.player.z,2)&&this.streamProps.size)return;
   this.archive();const wanted=new Map();for(const chunk of this.world.activeChunks)for(const p of chunk.props)wanted.set(p.id,p);
   for(const [id,o]of this.streamProps)if(!wanted.has(id)&&!o.held)this.streamProps.delete(id);
   for(const [id,desc]of wanted)if(!this.streamProps.has(id)){
    const t=D.PROP_TYPES[desc.type];const p={...t,...desc,homeX:desc.x,homeZ:desc.z,y:0,yaw:0,health:t.health,maxHealth:t.health,vx:0,vz:0,vy:0,spin:0,angle:0,fallYaw:0,angularVelocity:0,broken:false,held:false,changed:false,scale:desc.scale||1};
    const saved=this.changes.get(id);if(saved)Object.assign(p,saved,{changed:true});this.streamProps.set(id,p);
   }
   this.dynamics.props=[...this.homeProps,...this.streamProps.values()];this.dynamics.byId=new Map(this.dynamics.props.map(p=>[p.id,p]));this.dynamics.hash.rebuild(this.dynamics.props);this.dynamics.lightRevision++;
   const r=this.world.region(this.player.x,this.player.z),key=r.center.mx+':'+r.center.mz;if(!this.sectorVisits.has(key)){if(this.sectorVisits.size<2048)this.sectorVisits.add(key);if(this.time>1)this.emit('toast','HORIZONTE · '+r.name+' · '+r.subtitle);}
  }
  newTrafficRoute(c){
   if(!this.world.chunkSize)return super.newTrafficRoute(c);
   const n=this.world.node(c.x+Math.sin(c.yaw)*34,c.z+Math.cos(c.yaw)*34),r=this.random||D.rng(c.id+18);
   const dest=this.world.node(n.x+(Math.floor(r()*13)-6)*84,n.z+(Math.floor(r()*13)-6)*84);
   c.route=this.world.route(n.x,n.z,dest.x,dest.z);if(!c.route.length)c.route=[n];
  }
  traffic(c,dt){if(c.boarding){c.speed=D.damp(c.speed,0,12,dt);return;}super.traffic(c,dt);}
  recyclePopulation(){
   const p=this.player,large=!this.world.isHome(p.x,p.z);
   for(const c of this.cars){
    if(c===this.actor()||c.owned||c.boarding||c.health<95||D.distance(c,p)<850||(this.wanted&&c.police))continue;
    const a=this.random()*Math.PI*2,d=350+this.random()*220,sp=this.world.node(p.x+Math.sin(a)*d,p.z+Math.cos(a)*d);
    c.x=sp.x+4;c.z=sp.z+24;c.yaw=0;c.speed=0;c.route=[];c.navTime=0;this.newTrafficRoute(c);
   }
   for(let i=0;i<this.peds.length;i++){const n=this.peds[i];if(D.distance(n,p)<420)continue;const a=this.random()*Math.PI*2,d=180+this.random()*110,sp=this.world.node(p.x+Math.sin(a)*d,p.z+Math.cos(a)*d);n.x=sp.x+12;n.z=sp.z+20;n.homeZ=sp.z;n.panic=0;const t=this.world.region(n.x,n.z).type;n.hidden=large&&['farmland','woodland'].includes(t)&&i%9!==0;}
  }
  step(dt,input={}){
   if(!Number.isFinite(dt)||dt<=0)return;this.syncRegion();super.step(dt,input);
   this.recycleClock-=Math.min(dt,.25);if(this.recycleClock<=0){this.recycleClock=2;this.recyclePopulation();}
  }
  interact(kind='car'){
   const ctx=kind==='use'?this.getContext():null;
   if(ctx?.action==='job'&&!this.world.isHome(this.player.x,this.player.z)){
    const p=this.player,sp=this.world.node(p.x+336*(this.random()>.5?1:-1),p.z+336),dest={x:sp.x+4,z:sp.z+8};
    this.job={type:'delivery',points:[dest],index:0,time:170,reward:650};this.pin=null;this.emit('toast','CORREO REGIONAL · Entrega a la cooperativa. 170 segundos · $650.');return;
   }
   super.interact(kind);
  }
  travel(x,z){
   if(!D.Frontier.valid(x,z)||Math.max(Math.abs(x),Math.abs(z))>LIMIT-2048||this.wanted||this.job||this.uploading||this.player.transition){this.emit('toast','Viaje no disponible durante búsqueda, encargo, transmisión o acceso al vehículo.');return false;}
   if(this.player.car!==null&&Math.abs(this.actor().speed)>1){this.emit('toast','Detén el vehículo antes del viaje.');return false;}
   this.dropHeld();this.archive();const n=this.world.node(x,z);let dest=null;
   for(const o of [[4,8],[-4,8],[4,-8],[-4,-8],[0,0]]){const q={x:n.x+o[0],z:n.z+o[1]};if(!this.world.blocked(q.x,q.z,1.3)){dest=q;break;}}
   if(!dest)return false;
   // Transport the current actor, without granting money, repair, or erasing pursuit.
   if(this.player.car!==null)Object.assign(this.actor(),dest,{speed:0,yaw:0});
   Object.assign(this.player,dest,{y:0,vy:0,vx:0,vz:0,yaw:0,walk:0,moveSpeed:0,actualSpeed:0,transition:null});this.pin=null;this.route=[];this.world.activeKey='';this.syncRegion();this.recyclePopulation();
   for(const c of this.cars)if(c!==this.actor()&&D.distance(c,this.player)<6){c.x+=20;this.newTrafficRoute(c);}
   this.emit('toast','REGIÓN · '+this.world.region(dest.x,dest.z).name);this.emit('save','');return true;
  }
  serialize(){
   this.archive();const props=this.dynamics.props;this.dynamics.props=this.homeProps;let out;try{out=super.serialize();}finally{this.dynamics.props=props;}
   out.horizon={version:1,seed:this.world.seed,changes:[...this.changes.values()],visits:[...this.sectorVisits]};return out;
  }
  restore(data){
   if(!data||data.version!==1)return false;
   const h=data?.horizon;if(h!==undefined){
    if(!h||h.version!==1||!Number.isInteger(h.seed)||h.seed<-2147483648||h.seed>2147483647||!Array.isArray(h.changes)||h.changes.length>4096||!Array.isArray(h.visits)||h.visits.length>2048)return false;
    const seen=new Set();for(const q of h.changes){if(!q||typeof q.id!=='string'||!/^w(?:l)?:-?\d+:-?\d+(?::\d+)?$/.test(q.id)||seen.has(q.id)||!D.Frontier.valid(q.x,q.z)||!Number.isFinite(q.health)||q.health<0||q.health>135||!['yaw','angle','fallYaw'].every(k=>Number.isFinite(q[k])))return false;seen.add(q.id);}
    if(h.visits.some(v=>typeof v!=='string'||! /^-?\d+:-?\d+$/.test(v)))return false;
   }
   if(!data?.player||!D.Frontier.valid(data.player.x,data.player.z)||Math.max(Math.abs(data.player.x),Math.abs(data.player.z))>LIMIT-2048||!Number.isFinite(data.cash)||!Number.isInteger(data.story)||data.story<0||data.story>6)return false;
   if(h&&h.seed!==this.world.seed){const candidate=new D.FrontierWorld(h.seed),probe=new Base(candidate);if(!probe.restore(data))return false;Object.assign(this.world,candidate);this.dynamics=new D.ReactiveWorld(this);this.homeProps=[...this.dynamics.props];}
   const active=this.dynamics.props,activeIndex=this.dynamics.byId;this.dynamics.props=this.homeProps;this.dynamics.byId=new Map(this.homeProps.map(p=>[p.id,p]));
   if(!super.restore(data)){this.dynamics.props=active;this.dynamics.byId=activeIndex;return false;}
   this.changes=new Map((h?.changes||[]).map(q=>[q.id,{...q}]));this.sectorVisits=new Set(h?.visits||[]);this.streamProps.clear();this.world.activeKey='';this.setLightLookup();this.syncRegion();return true;
  }
 }
 D.FrontierSimulation=FrontierSimulation;D.Simulation=FrontierSimulation;
})(DC);
