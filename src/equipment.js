/* Arsenal v0.17. Fictional gameplay data and geometry queries, no DOM or renderer state. */
'use strict';
(function(D){
 const catalog=[
  {id:'unarmed',name:'Manos libres',group:'Esenciales',kind:'none',desc:'Explora e interactúa sin equipo en las manos.',range:0,key:'`'},
  {id:'baton',name:'Bastón',group:'Cuerpo a cuerpo',kind:'melee',desc:'Golpe de corto alcance, sin munición.',range:2.1,damage:26,interval:.66,heat:6},
  {id:'blade',name:'Hoja táctica',group:'Cuerpo a cuerpo',kind:'melee',desc:'Ataque cercano. Requiere una línea de contacto libre.',range:1.8,damage:38,interval:.58,heat:9},
  {id:'pistol',name:'Pistola Vector',group:'Armas cortas',kind:'hitscan',desc:'Disparo semiautomático equilibrado.',mag:12,reserve:96,range:110,damage:20,interval:.24,reload:1.25,spread:.008,heat:7,key:'1',length:.29},
  {id:'revolver',name:'Revólver Nexo',group:'Armas cortas',kind:'hitscan',desc:'Seis disparos potentes, con mayor retroceso.',mag:6,reserve:48,range:135,damage:36,interval:.48,reload:1.8,spread:.007,heat:8,key:'2',length:.36},
  {id:'smg',name:'Subfusil Kestrel',group:'Armas largas',kind:'hitscan',desc:'Fuego automático rápido. Menor precisión a distancia.',mag:30,reserve:180,range:100,damage:13,interval:.075,reload:1.7,spread:.026,automatic:true,heat:5,key:'3',length:.48},
  {id:'shotgun',name:'Escopeta Umbral',group:'Armas largas',kind:'hitscan',desc:'Ocho perdigones con dispersión de corto alcance.',mag:8,reserve:56,range:62,damage:8,pellets:8,interval:.85,reload:2.2,spread:.07,heat:12,key:'4',length:.72},
  {id:'rifle',name:'Fusil Horizonte',group:'Armas largas',kind:'hitscan',desc:'Fuego automático controlado y alcance medio.',mag:30,reserve:150,range:210,damage:24,interval:.115,reload:1.9,spread:.011,automatic:true,heat:8,key:'5',length:.68},
  {id:'sniper',name:'Precisión Faro',group:'Armas largas',kind:'hitscan',desc:'Óptica 4×, alta precisión y cadencia baja.',mag:5,reserve:30,range:520,damage:80,interval:1.15,reload:2.5,spread:.0008,zoom:4,heat:16,key:'6',length:.84},
  {id:'launcher',name:'Lanzador Atlas',group:'Explosivos',kind:'rocket',desc:'Proyectil visible. Explosión de área y daño propio cercano.',mag:1,reserve:6,range:280,damage:95,radius:7,interval:1.2,reload:2.8,speed:48,heat:24,key:'7',length:.72},
  {id:'grenade',name:'Granada',group:'Explosivos',kind:'grenade',desc:'Lanzamiento con arco, rebote y detonación tras 2.4 s.',mag:1,reserve:8,range:45,damage:80,radius:6,interval:.7,reload:.75,speed:17,heat:18,key:'8',length:.10},
  {id:'gauss',name:'Cañón Gauss',group:'Tecnología',kind:'gauss',desc:'Mantén para cargar y suelta. Atraviesa hasta tres objetivos, no edificios.',mag:3,reserve:21,range:420,damage:120,interval:1.05,reload:2.4,chargeTime:1.5,minCharge:.23,heat:23,key:'9',length:.85},
  {id:'emp',name:'Emisor EMP',group:'Tecnología',kind:'emp',desc:'Pulso de 26 m. Interrumpe motores y luces durante 8 s, sin dañar personas.',mag:1,reserve:8,range:26,radius:26,duration:8,interval:1,reload:3.2,heat:12,key:'0',length:.44},
  {id:'binoculars',name:'Binoculares',group:'Observación',kind:'optics',desc:'Óptica 2× / 4× / 8× / 12×. Mide y marca únicamente lo que ves.',range:600,key:'B',length:.17}
 ].map(v=>Object.freeze(v));
 const byId=new Map(catalog.map(x=>[x.id,x])),zoom=[2,4,8,12],clamp=D.clamp;
 function initial(){return{version:1,selected:'unarmed',zoom:0,ammo:Object.fromEntries(catalog.filter(w=>w.mag).map(w=>[w.id,{loaded:w.mag,reserve:w.reserve}])),shots:0,hits:0,charge:0,cooldown:0,reloading:0,reloadId:null,trigger:false,blockedTrigger:false,aiming:false,aimWeight:0,recoil:0,pitch:0,shotSerial:0};}
 function snapshot(s){return{version:1,selected:s.selected,zoom:s.zoom,shots:s.shots,hits:s.hits,ammo:Object.fromEntries(catalog.filter(w=>w.mag).map(w=>[w.id,{...s.ammo[w.id]}]))};}
 function valid(s){if(s===undefined)return true;if(!s||s.version!==1||!byId.has(s.selected)||!Number.isInteger(s.zoom)||s.zoom<0||s.zoom>3||!s.ammo||typeof s.ammo!=='object'||![s.shots,s.hits].every(v=>Number.isSafeInteger(v)&&v>=0&&v<=1e9))return false;
  if(Object.keys(s.ammo).length!==catalog.filter(w=>w.mag).length)return false;
  return catalog.filter(w=>w.mag).every(w=>{const q=s.ammo[w.id];return q&&Number.isInteger(q.loaded)&&q.loaded>=0&&q.loaded<=w.mag&&Number.isInteger(q.reserve)&&q.reserve>=0&&q.reserve<=w.reserve*5;});
 }
 function restore(s){if(!valid(s))throw new Error('Equipamiento inválido.');const out=initial();if(s)Object.assign(out,snapshot(s));return out;}
 function rayBox(origin,dir,box,range){let lo=0,hi=range;for(let i=0;i<3;i++){if(Math.abs(dir[i])<1e-10){if(origin[i]<box.min[i]||origin[i]>box.max[i])return null;}else{let a=(box.min[i]-origin[i])/dir[i],b=(box.max[i]-origin[i])/dir[i];if(a>b)[a,b]=[b,a];lo=Math.max(lo,a);hi=Math.min(hi,b);if(lo>hi)return null;}}return lo<=range&&hi>=0?lo:null;}
 const endpoint=(o,d,t)=>o.map((v,i)=>v+d[i]*t);
 function trace(sim,o,d,range=300,{ignore=null,radius=0,onlyBuildings=false}={}){
  if(![...o,...d,range].every(Number.isFinite)||Math.hypot(...d)<1e-6)return[];
  range=clamp(range,0,650);d=D.normalize(d);const hits=[],put=(type,ref,distance)=>{if(distance!==null)hits.push({type,ref,distance,point:endpoint(o,d,distance)});};
  const end=endpoint(o,d,range),mid=[(o[0]+end[0])/2,(o[2]+end[2])/2];
  for(const b of sim.world.nearby(mid[0],mid[1],range*.5+4))put('wall',b,rayBox(o,d,{min:[b.x-b.w/2-radius,-.25,b.z-b.d/2-radius],max:[b.x+b.w/2+radius,b.h||10,b.z+b.d/2+radius]},range));
  if(d[1]<-1e-7){const t=(.01-o[1])/d[1];if(t>=0&&t<=range)put('ground',null,t);}
  if(!onlyBuildings){
   for(const c of sim.cars){if(c===ignore)continue;const dx=o[0]-c.x,dz=o[2]-c.z,co=Math.cos(c.yaw),si=Math.sin(c.yaw),local=[dx*co-dz*si,o[1],dx*si+dz*co],ld=[d[0]*co-d[2]*si,d[1],d[0]*si+d[2]*co];put('car',c,rayBox(local,ld,{min:[-1.04-radius,.08-radius,-2.24-radius],max:[1.04+radius,1.52+radius,2.24+radius]},range));}
   for(const p of sim.dynamics.props){if(p===ignore||p.broken||p.held)continue;const r=(p.radius||.2)*(p.scale||1)+radius,y=p.y||0;put('prop',p,rayBox(o,d,{min:[p.x-r,y,p.z-r],max:[p.x+r,y+(p.height||.6)*(p.scale||1),p.z+r]},range));}
   for(const n of sim.peds){if(n===ignore||n.hidden||n.combatStunUntil>sim.time)continue;const r=.24+radius,base=n.y||0;put('npc',n,rayBox(o,d,{min:[n.x-r,base+.06,n.z-r],max:[n.x+r,base+1.70-(n.crouch||0)*.35,n.z+r]},range));}
  }
  hits.sort((a,b)=>a.distance-b.distance);return hits;
 }
 function mount(sim,actorOverride=null){return D.WeaponHandling.mount(sim,actorOverride);}

 D.Equipment=Object.freeze({catalog:Object.freeze(catalog),zoom:Object.freeze(zoom),get:id=>byId.get(id)||null,initial,snapshot,valid,restore,rayBox,trace,endpoint,mount});
})(DC);
