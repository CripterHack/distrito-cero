/* Horizonte: deterministic zoning + finite working set over a procedural address space.
   Authoritative positions are JS doubles. Rendering uses camera-relative floats. */
'use strict';
(function(D){
 const Base=D.World, STEP=84, CHUNK=336, LIMIT=1e9;
 const mod=(x,n)=>((x%n)+n)%n;
 function hash(x,z,seed=0){let a=Math.imul(x|0,374761393)^Math.imul(z|0,668265263)^(seed|0);a=Math.imul(a^(a>>>13),1274126177);return((a^(a>>>16))>>>0)/4294967296;}
 const valid=(x,z)=>Number.isFinite(x)&&Number.isFinite(z)&&Math.abs(x)<=LIMIT&&Math.abs(z)<=LIMIT;
 const NAMES={urban:['CIUDAD NÁCAR','CENTRO METROPOLITANO'],future:['NUEVA AURORA','DISTRITO SOLAR'],retro:['SANTA COBALTO','BARRIO PATRIMONIAL'],village:['SAN LUCERO','PUEBLO DEL VALLE'],suburb:['PERIFERIA','TRANSICIÓN RESIDENCIAL'],farmland:['VEGA ABIERTA','PAISAJE AGRÍCOLA'],woodland:['MONTE CLARO','CORREDOR FORESTAL']};
 class FrontierWorld extends Base{
  constructor(seed=1337){
   super(seed|0);this.seed=seed|0;this.coordinateLimit=LIMIT;this.chunkSize=CHUNK;this.cells=new Map();this.chunks=new Map();this.generation=0;this.activeKey='';this.activeChunks=[];
   this.home={buildings:this.buildings,blocks:this.blocks,lights:this.lights.map((l,i)=>({...l,id:'lamp:'+i})),pois:this.pois,crates:this.crates};this.lights=this.home.lights;
   this.homeCells=new Map();for(const b of this.home.blocks){const ix=Math.floor(b.x/STEP),iz=Math.floor(b.z/STEP);this.homeCells.set(ix+':'+iz,{...b,ix,iz,home:true,type:'urban',buildings:this.home.buildings.filter(a=>Math.floor(a.x/STEP)===ix&&Math.floor(a.z/STEP)===iz)});}
  }
  isHome(x,z){return x>=-420&&x<420&&z>=-420&&z<420;}
  center(mx,mz){
   const r=D.rng((hash(mx,mz,this.seed)*4294967295)>>>0);let theme=['urban','future','retro','village'][Math.floor(r()*4)];
   let ix=mx*24+(Math.floor(r()*3)-1)*4,iz=mz*24+(Math.floor(r()*3)-1)*4;
   if(mx===0&&mz===0){ix=0;iz=0;theme='urban';}
   if(mx===1&&mz===0){ix=24;iz=0;theme='future';}
   if(mx===-1&&mz===0){ix=-24;iz=0;theme='retro';}
   if(mx===0&&mz===1){ix=0;iz=24;theme='village';}
   return{mx,mz,ix,iz,x:ix*STEP,z:iz*STEP,theme,name:(mx===0&&mz===0?'DISTRITO CERO':NAMES[theme][0])+(Math.abs(mx)+Math.abs(mz)>1?' '+Math.floor(hash(mx,mz,this.seed+6)*899+100):'')};
  }
  region(x,z){
   if(!valid(x,z))throw new RangeError('Coordenadas fuera del espacio procedural.');
   const ix=x/STEP,iz=z/STEP,mx=Math.round(ix/24),mz=Math.round(iz/24);let best=null,d=Infinity;
   for(let a=mx-1;a<=mx+1;a++)for(let b=mz-1;b<=mz+1;b++){const c=this.center(a,b),r=Math.hypot(c.ix-ix,c.iz-iz);if(r<d){d=r;best=c;}}
   let type=best.theme==='village'?(d<3.4?'village':null):(d<5.8?best.theme:d<8.8?'suburb':null);
   if(!type){const k=hash(Math.floor(ix/4),Math.floor(iz/4),this.seed+103);type=k>.73?'woodland':'farmland';}
   if(this.isHome(x,z))type='urban';
   return{type,name:this.isHome(x,z)?'DISTRITO CERO':type===best.theme?best.name:NAMES[type][0],subtitle:NAMES[type][1],center:best,distance:d*STEP};
  }
  roadWidth(ix,iz,axis){
   // One canonical edge function: adjacent chunks can never disagree about a crossing.
   if((axis==='v'?mod(ix,4):mod(iz,4))===0)return 20;
   const a=this.region((ix+(axis==='v'?-.5:.5))*STEP,(iz+(axis==='v'?.5:-.5))*STEP).type;
   const b=this.region((ix+.5)*STEP,(iz+.5)*STEP).type;
   if([a,b].some(t=>['urban','future','retro'].includes(t)))return 20;
   if([a,b].includes('suburb'))return 14;
   if([a,b].includes('village'))return 12;
   return 0;
  }
  cell(ix,iz){
   if(!Number.isInteger(ix)||!Number.isInteger(iz)||!valid(ix*STEP,iz*STEP))throw new RangeError('Parcela no válida.');
   const key=ix+':'+iz;if(this.cells.has(key)){const c=this.cells.get(key);this.cells.delete(key);this.cells.set(key,c);return c;}
   const x=(ix+.5)*STEP,z=(iz+.5)*STEP,r=D.rng((hash(ix,iz,this.seed)*4294967295)>>>0),reg=this.region(x,z),type=reg.type;
   const home=this.homeCells.get(key),roads={w:this.roadWidth(ix,iz,'v'),e:this.roadWidth(ix+1,iz,'v'),n:this.roadWidth(ix,iz,'h'),s:this.roadWidth(ix,iz+1,'h')};
   const c={ix,iz,x,z,type,roads,home:!!home,park:home?.park||false,seed:r(),buildings:[],props:[],lights:[],pois:[],crop:Math.floor(r()*4)};
   if(home)c.buildings=home.buildings.map(b=>({...b,kind:'urban'}));
   else{
    const b=(xx,zz,w,d,h,kind)=>c.buildings.push({x:xx,z:zz,w,d,h,kind,style:type==='future'?1:Math.floor(r()*4),tone:r(),seed:r()*500,sign:Math.floor(r()*12)});
    if(['urban','future','retro'].includes(type)){
     c.park=r()<.12;
     if(!c.park)for(let i=0;i<2;i++)for(let j=0;j<2;j++){
      const height=type==='future'?32+r()*67:type==='retro'?7+r()*13:15+r()*48;
      b(ix*STEP+26+i*31,iz*STEP+26+j*31,20+r()*6,20+r()*6,height,type);
     }
    }else if(type==='suburb'||type==='village'){
     c.park=r()<.10;
     if(!c.park){b(x-13,z-14,17+r()*6,16+r()*6,4+r()*4,type);if(r()<.75)b(x+15,z+15,16+r()*5,16+r()*5,4+r()*3,type);}
    }else if(type==='farmland'&&r()<.17)b(x,z,24+r()*4,22,4.5+r()*2,r()<.6?'barn':'greenhouse');
    const add=(t,px,pz,extra={})=>c.props.push({type:t,x:px,z:pz,id:`w:${ix}:${iz}:${c.props.length}`,...extra});
    const treeCount=type==='woodland'?7:c.park?5:type==='farmland'?1:1;
    for(let i=0;i<treeCount;i++){const tx=ix*STEP+15+r()*54,tz=iz*STEP+15+r()*54;if(!c.buildings.some(b=>D.circleBox(tx,tz,2.5,b)))add('tree',tx,tz,{scale:.82+r()*.60});}
    if(['urban','future','retro','suburb','village'].includes(type)){
     if(roads.w){const lamp={id:`wl:${ix}:${iz}`,x:ix*STEP+roads.w/2+1.6,z:z+12,y:7.6,warm:type!=='future'};c.lights.push(lamp);add('lamp',lamp.x,lamp.z,{id:lamp.id,warm:lamp.warm});}
     if(r()<.30)add('bench',ix*STEP+14,z+3);if(r()<.2)add('bin',ix*STEP+14,z-5);
    }
    if((type==='village'||type==='farmland')&&r()<.28)add('crate',ix*STEP+13,z-12);
    // Every regional centre has a safe road-side service point, never inside a building.
    const center=reg.center;if(ix===center.ix&&iz===center.iz){c.pois.push({type:'garage',name:'Taller de '+center.name,x:ix*STEP+12,z:iz*STEP+19,regional:true});c.pois.push({type:'job',name:'Cooperativa de mensajería',x:ix*STEP+12,z:iz*STEP+29,regional:true});}
   }
   this.cells.set(key,c);while(this.cells.size>768)this.cells.delete(this.cells.keys().next().value);return c;
  }
  chunk(cx,cz){
   if(!Number.isInteger(cx)||!Number.isInteger(cz)||!valid(cx*CHUNK,cz*CHUNK))throw new RangeError('Sector no válido.');
   const key=cx+':'+cz;if(this.chunks.has(key)){const c=this.chunks.get(key);this.chunks.delete(key);this.chunks.set(key,c);return c;}
   const cells=[];for(let ix=cx*4;ix<cx*4+4;ix++)for(let iz=cz*4;iz<cz*4+4;iz++)cells.push(this.cell(ix,iz));
   const c={key,cx,cz,x:cx*CHUNK,z:cz*CHUNK,cells,buildings:cells.flatMap(c=>c.buildings),props:cells.flatMap(c=>c.props),lights:cells.flatMap(c=>c.lights),pois:cells.flatMap(c=>c.pois)};
   this.chunks.set(key,c);while(this.chunks.size>64)this.chunks.delete(this.chunks.keys().next().value);return c;
  }
  focus(x,z,radius=2){
   const cx=Math.floor(x/CHUNK),cz=Math.floor(z/CHUNK),key=`${cx}:${cz}:${radius}`;if(this.activeKey===key)return false;
   this.activeKey=key;const chunks=[];for(let i=-radius;i<=radius;i++)for(let j=-radius;j<=radius;j++)chunks.push(this.chunk(cx+i,cz+j));
   chunks.sort((a,b)=>Math.hypot(a.cx-cx,a.cz-cz)-Math.hypot(b.cx-cx,b.cz-cz));this.activeChunks=chunks;
   this.buildings=chunks.flatMap(c=>c.buildings);this.blocks=chunks.flatMap(c=>c.cells);
   this.lights=[...this.home.lights.filter(l=>Math.abs(l.x-x)<1000&&Math.abs(l.z-z)<1000),...chunks.flatMap(c=>c.lights)];
   this.pois=[...this.home.pois,...chunks.flatMap(c=>c.pois)];this.generation++;return true;
  }
  nearby(x,z,r=10){
   if(!valid(x,z))return[];const out=[];r=Math.min(1200,Math.max(0,r));
   for(let ix=Math.floor((x-r)/STEP);ix<=Math.floor((x+r)/STEP);ix++)for(let iz=Math.floor((z-r)/STEP);iz<=Math.floor((z+r)/STEP);iz++)for(const b of this.cell(ix,iz).buildings)if(Math.abs(x-b.x)<b.w/2+r&&Math.abs(z-b.z)<b.d/2+r)out.push(b);return out;
  }
  blocked(x,z,r=.5){return!valid(x,z)||this.nearby(x,z,r).some(b=>D.circleBox(x,z,r,b));}
  move(x,z,dx,dz,r){if(!valid(x,z)||![dx,dz,r].every(Number.isFinite))return{x:0,z:0,hit:true};const q=D.moveCircle(x,z,dx,dz,r,this.nearby(x,z,Math.min(1200,Math.hypot(dx,dz)+r)));q.x=D.clamp(q.x,-LIMIT+2048,LIMIT-2048);q.z=D.clamp(q.z,-LIMIT+2048,LIMIT-2048);return q;}
  visible(ax,az,bx,bz){
   if(!valid(ax,az)||!valid(bx,bz))return false;const dist=Math.hypot(bx-ax,bz-az);if(dist>2500)return false;
   const n=Math.max(1,Math.ceil(dist/40)),visited=new Set();for(let i=0;i<=n;i++){const x=D.lerp(ax,bx,i/n),z=D.lerp(az,bz,i/n),ix=Math.floor(x/STEP),iz=Math.floor(z/STEP);const key=ix+':'+iz;if(visited.has(key))continue;visited.add(key);for(const b of this.cell(ix,iz).buildings)if(D.segmentBox(ax,az,bx,bz,b,.1))return false;}return true;
  }
  node(x,z){
   let ix=Math.round(x/STEP),iz=Math.round(z/STEP);const type=this.region(x,z).type;
   if(type==='farmland'||type==='woodland'){if(mod(ix,4)!==0&&mod(iz,4)!==0){if(Math.abs(x-Math.round(ix/4)*CHUNK)<Math.abs(z-Math.round(iz/4)*CHUNK))ix=Math.round(ix/4)*4;else iz=Math.round(iz/4)*4;}}
   return{x:ix*STEP,z:iz*STEP};
  }
  canRoad(ax,az,bx,bz){if(Math.abs(ax-bx)+Math.abs(az-bz)!==1)return false;return(ax===bx?this.roadWidth(ax,Math.min(az,bz),'v'):this.roadWidth(Math.min(ax,bx),az,'h'))>0;}
  route(ax,az,bx,bz){
   if(!valid(ax,az)||!valid(bx,bz))return[];let start=this.node(ax,az),end=this.node(bx,bz);
   // Route only a bounded useful prefix for intercontinental destinations.
   const far=Math.max(Math.abs(end.x-start.x),Math.abs(end.z-start.z));if(far>STEP*24)end=this.node(start.x+(end.x-start.x)*STEP*24/far,start.z+(end.z-start.z)*STEP*24/far);
   const sx=start.x/STEP,sz=start.z/STEP,ex=end.x/STEP,ez=end.z/STEP,k=(x,z)=>x+':'+z;
   const open=[{x:sx,z:sz,g:0,f:Math.abs(ex-sx)+Math.abs(ez-sz)}],cost=new Map([[k(sx,sz),0]]),parents=new Map();let found=null;
   for(let it=0;open.length&&it<3000;it++){
    let best=0;for(let j=1;j<open.length;j++)if(open[j].f<open[best].f)best=j;const n=open.splice(best,1)[0];if(n.x===ex&&n.z===ez){found=n;break;}
    for(const [dx,dz]of [[0,1],[1,0],[0,-1],[-1,0]]){let x=n.x+dx,z=n.z+dz;if(Math.abs(x-sx)>36||Math.abs(z-sz)>36||!this.canRoad(n.x,n.z,x,z))continue;const key=k(x,z),g=n.g+1;if(g>=(cost.get(key)??Infinity))continue;cost.set(key,g);parents.set(key,n);open.push({x,z,g,f:g+Math.abs(ex-x)+Math.abs(ez-z)});}
   }
   if(!found)return[start];const out=[];let node=found;while(node&&out.length<513){out.push({x:node.x*STEP,z:node.z*STEP});node=parents.get(k(node.x,node.z));}return out.reverse();
  }
  district(x,z){return this.isHome(x,z)?super.district(x,z):this.region(x,z).name;}
  destinations(){
   const presets=[['home','Distrito Cero',0,0,'urban'],['future','Nueva Aurora',2016,0,'future'],['retro','Santa Cobalto',-2016,0,'retro'],['village','San Lucero',0,2016,'village']];
   let farm={x:1008,z:1008};for(let i=8;i<17;i++)if(this.region(i*STEP,1008).type==='farmland'){farm={x:i*STEP,z:1008};break;}
   return[...presets.map(([id,name,x,z,type])=>({id,name,x,z,type})),{id:'farmland',name:'Vega Abierta',...farm,type:'farmland'}];
  }
 }
 D.Frontier={STEP,CHUNK,LIMIT,hash,mod,valid,NAMES};D.LegacyWorld=Base;D.FrontierWorld=FrontierWorld;D.World=FrontierWorld;
})(DC);
