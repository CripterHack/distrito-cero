/* The atlas queries zoning without populating or allocating distant chunks. */
'use strict';
(function(D){
 const $=id=>document.getElementById(id), Base=D.App;
 const COLORS={urban:'#405c6d',future:'#3f8887',retro:'#947454',suburb:'#6c8073',village:'#94987b',farmland:'#66764a',woodland:'#304d3c'};
 class HorizonApp extends Base{
  constructor(){
   super();this.atlasRange=5600;this.atlasRegional=true;this.atlasCenter=null;this.nextCount=0;this.renderer.daylight=D.clamp(Number.isFinite(this.settings.daylight)?this.settings.daylight:.62,0,1);$('daylight').value=this.renderer.daylight*100;
   $('daylight').oninput=e=>{this.renderer.daylight=Number(e.target.value)/100;this.settings.daylight=this.renderer.daylight;this.renderer.lightTime=-1;this.saveSettings();};
   $('localView').onclick=()=>{this.atlasRegional=false;this.atlasRange=900;this.drawMap(true);};$('regionalView').onclick=()=>{this.atlasRegional=true;this.atlasRange=5600;this.drawMap(true);};
   $('zoomIn').onclick=()=>this.zoomAtlas(.64);$('zoomOut').onclick=()=>this.zoomAtlas(1.56);$('centerMap').onclick=()=>{this.atlasCenter=null;this.drawMap(true);};
   $('exploreHorizon').onclick=()=>{if(!this.started)this.start(!!this.readSave(),true);this.openMap();};
   $('travelPin').onclick=()=>{if(this.sim.pin)this.visit(this.sim.pin.x,this.sim.pin.z);};
   $('nextRegion').onclick=()=>{const r=this.world.region(this.sim.player.x,this.sim.player.z),k=++this.nextCount,dx=[1,0,-1,0][k%4],dz=[0,1,0,-1][k%4],c=this.world.center(r.center.mx+dx,r.center.mz+dz);this.visit(c.x,c.z);};
   $('applySeed').onclick=()=>{
    const seed=Number($('worldSeed').value);if(!Number.isInteger(seed)||seed<-2147483648||seed>2147483647){$('mapHint').textContent='Escribe un entero entre −2147483648 y 2147483647.';return;}
    if(!confirm('¿Crear otra partida con esta semilla? El guardado actual se reemplazará. Exporta la partida antes para conservarla.'))return;
    Object.assign(this.world,new D.FrontierWorld(seed));this.start(false,true);this.renderer.resetSectors();this.refreshStops();this.toast('NUEVA SEMILLA · '+seed);
   };
   this.refreshStops();this.renderDirty=true;
  }
  refreshStops(){
   $('atlasStops').replaceChildren();for(const d of this.world.destinations()){
    const row=document.createElement('div');row.className='atlas-stop';row.style.setProperty('--region-color',COLORS[d.type]);
    const b=document.createElement('button');b.className='stop-name';b.innerHTML='<span></span><strong></strong><small></small>';b.children[1].textContent=d.name;b.children[2].textContent=D.Frontier.NAMES[d.type][1];b.title='Marcar ruta a '+d.name;
    b.onclick=()=>{this.sim.pin={x:d.x,z:d.z};this.sim.routeClock=0;this.atlasCenter={x:d.x,z:d.z};this.drawMap(true);$('mapHint').textContent=d.name+' · Ruta marcada. Puedes conducir o visitar.';};
    const go=document.createElement('button');go.className='stop-go';go.textContent='IR ↗';go.title='Visitar '+d.name;go.setAttribute('aria-label','Visitar '+d.name);go.dataset.destination=d.id;go.onclick=()=>this.visit(d.x,d.z);row.append(b,go);$('atlasStops').append(row);
   }$('worldSeed').value=this.world.seed;
  }
  zoomAtlas(factor){this.atlasRange=D.clamp((this.atlasRange||5600)*factor,420,16000);this.atlasRegional=this.atlasRange>1500;this.drawMap(true);}
  visit(x,z){
   if(!this.started)return;if(this.sim.travel(x,z)){this.atlasCenter=null;this.renderer.camera.initialized=false;this.renderer.camera.yaw=this.sim.player.yaw;this.renderer.lightTime=-1;this.renderer.syncSectors(2);this.setMode('play');this.save(false);}
   else $('mapHint').textContent='Detente y termina la persecución o el encargo antes de viajar.';this.processEvents();
  }
  openMap(){this.atlasCenter=null;super.openMap();if(this.mode==='map'){this.refreshStops();this.drawMap(true);}}
  mapClick(e){
   const t=this.mapTransform;if(!t)return;const rect=$('citymap').getBoundingClientRect(),q=D.mapUnproject(e.clientX-rect.left,e.clientY-rect.top,t.cx,t.cz,t.w,t.h,t.scale);
   if(!D.Frontier.valid(q.x,q.z))return;const n=this.world.node(q.x,q.z);this.sim.pin={x:n.x+4,z:n.z+8};this.sim.route=this.world.route(this.sim.player.x,this.sim.player.z,n.x,n.z);this.sim.routeClock=0;
   $('mapHint').textContent=this.world.region(q.x,q.z).subtitle+' · GPS marcado. La ruta se actualiza por tramos.';this.drawMap(true);
  }
  drawMap(full=false){
   const canvas=$(full?'citymap':'minimap');if(!canvas)return;const ctx=canvas.getContext('2d'),rect=full?canvas.getBoundingClientRect():{width:160,height:160},w=rect.width,h=rect.height,dpr=Math.min(devicePixelRatio||1,2);if(!w||!h)return;
   if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}
   const p=this.sim.player,center=full&&this.atlasCenter||p,cx=center.x,cz=center.z,range=full?(this.atlasRange||5600):235,scale=Math.min(w,h)/range,point=(x,z)=>D.mapProject(x,z,cx,cz,w,h,scale);
   if(full){this.mapTransform={cx,cz,w,h,scale};$('localView').setAttribute('aria-pressed',String(range<=1500));$('regionalView').setAttribute('aria-pressed',String(range>1500));$('travelPin').disabled=!this.sim.pin;$('atlasTitle').textContent=range>1500?'El mundo continúa.':this.world.district(cx,cz);$('atlasPosition').textContent='SEMILLA '+this.world.seed;$('atlasStats').textContent=(this.sim.sectorVisits?.size||1)+' REGIONES VISITADAS · '+(this.renderer.streamStats?.loaded||0)+'/25 SECTORES EN MEMORIA';}
   if(full){const tag=[cx,cz,range,w,h,this.world.seed,this.world.generation,this.sim.pin?.x,this.sim.pin?.z,this.sim.story,this.sim.wanted,this.sim.job?.index].join('|');if(this.mapPaintTag===tag)return;this.mapPaintTag=tag;}
   ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle='#10211d';ctx.fillRect(0,0,w,h);ctx.save();ctx.beginPath();ctx.rect(0,0,w,h);ctx.clip();
   const left=cx-w/2/scale,right=cx+w/2/scale,top=cz-h/2/scale,bottom=cz+h/2/scale;
   if(full&&range>1500){
    // Fixed raster budget, independent of the kilometres visible in the atlas.
    const pixels=12;for(let y=0;y<h;y+=pixels)for(let x=0;x<w;x+=pixels){const pos=D.mapUnproject(x+pixels/2,y+pixels/2,cx,cz,w,h,scale),type=this.world.region(pos.x,pos.z).type;ctx.fillStyle=COLORS[type];ctx.fillRect(x,y,pixels+1,pixels+1);}
    ctx.fillStyle='#06171035';ctx.fillRect(0,0,w,h);ctx.lineWidth=.7;ctx.strokeStyle='#dfe9ca38';
    for(let x=Math.ceil(left/336)*336;x<right;x+=336){const a=point(x,top),b=point(x,bottom);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();}
    for(let z=Math.ceil(top/336)*336;z<bottom;z+=336){const a=point(left,z),b=point(right,z);ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.stroke();}
    for(const chunk of this.world.activeChunks){const a=point(chunk.x+336,chunk.z+336);ctx.strokeStyle='#e2ecc34d';ctx.strokeRect(a[0],a[1],336*scale,336*scale);}
    const mx0=Math.floor(left/2016)-1,mx1=Math.ceil(right/2016)+1,mz0=Math.floor(top/2016)-1,mz1=Math.ceil(bottom/2016)+1;
    ctx.textAlign='center';ctx.font='600 10px system-ui';for(let mx=mx0;mx<=mx1;mx++)for(let mz=mz0;mz<=mz1;mz++){const c=this.world.center(mx,mz),[x,y]=point(c.x,c.z);if(x<30||x>w-30||y<22||y>h-25)continue;const text=c.name.toUpperCase(),tw=ctx.measureText(text).width;ctx.fillStyle='#092020d9';ctx.fillRect(x-tw/2-6,y+7,tw+12,19);ctx.fillStyle='#edf5e0';ctx.fillText(text,x,y+20);ctx.beginPath();ctx.arc(x,y,3,0,Math.PI*2);ctx.fill();}
   }else{
    const a=Math.floor(left/84)-1,b=Math.floor(right/84)+1,c=Math.floor(top/84)-1,d=Math.floor(bottom/84)+1;
    for(let ix=a;ix<=b;ix++)for(let iz=c;iz<=d;iz++){
     const cell=this.world.cell(ix,iz),q=point(cell.ix*84+84,cell.iz*84+84);ctx.fillStyle=COLORS[cell.type];ctx.globalAlpha=.30;ctx.fillRect(q[0],q[1],84*scale,84*scale);ctx.globalAlpha=1;
     ctx.fillStyle='#879b8730';for(const obj of cell.buildings){const p=point(obj.x+obj.w/2,obj.z+obj.d/2);ctx.fillRect(p[0],p[1],obj.w*scale,obj.d*scale);}
     ctx.strokeStyle='#b2b99c66';for(const[edge,width]of[['v',cell.roads.w],['h',cell.roads.n]])if(width){ctx.lineWidth=Math.max(.65,width*.17*scale);const p1=point(ix*84,iz*84),p2=point((ix+(edge==='h'?1:0))*84,(iz+(edge==='v'?1:0))*84);ctx.beginPath();ctx.moveTo(...p1);ctx.lineTo(...p2);ctx.stroke();}
    }
   }
   const target=this.sim.target();if(target&&this.sim.route.length){ctx.beginPath();ctx.strokeStyle='#d7f394';ctx.lineWidth=full?2:1.8;ctx.setLineDash([5,3]);[p,...this.sim.route].forEach((q,i)=>{const xy=point(q.x,q.z);if(!i)ctx.moveTo(...xy);else ctx.lineTo(...xy);});ctx.stroke();ctx.setLineDash([]);}
   for(const poi of this.world.pois){const[x,y]=point(poi.x,poi.z);if(x<0||x>w||y<0||y>h)continue;ctx.fillStyle=poi.type==='garage'?'#87e1e0':poi.type==='safe'?'#eeeecc':'#d8e7aa';ctx.beginPath();ctx.arc(x,y,full?3:2,0,Math.PI*2);ctx.fill();if(full&&range<=1500){ctx.font='9px system-ui';ctx.textAlign='left';ctx.fillText(poi.name,x+5,y-4);}}
   if(this.sim.wanted){for(const car of this.sim.cars)if(car.police&&!car.stolen){const xy=point(car.x,car.z);ctx.fillStyle='#f5a094';ctx.beginPath();ctx.arc(...xy,3,0,Math.PI*2);ctx.fill();}const last=this.sim.policeState.lastSeen;if(last&&!this.sim.seen){const xy=point(last.x,last.z);ctx.strokeStyle='#f5c683';ctx.setLineDash([3,3]);ctx.beginPath();ctx.arc(...xy,Math.max(5,30*scale),0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);}}
   if(target){const[x,y]=point(target.x,target.z);ctx.save();ctx.translate(x,y);ctx.rotate(Math.PI/4);ctx.fillStyle='#d7f394';ctx.fillRect(-4,-4,8,8);ctx.restore();}
   const[x,y]=point(p.x,p.z);ctx.save();ctx.translate(x,y);ctx.rotate(-p.yaw);ctx.fillStyle='#f6ffe8';ctx.strokeStyle='#112b22';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(0,-8);ctx.lineTo(5,5);ctx.lineTo(0,3);ctx.lineTo(-5,5);ctx.closePath();ctx.stroke();ctx.fill();ctx.restore();ctx.restore();
   if(full){ctx.fillStyle='#09221ddd';ctx.fillRect(8,h-32,148,24);ctx.fillStyle='#dee8d6';ctx.font='10px monospace';ctx.textAlign='left';ctx.fillText('N ↑   '+(range/1000).toFixed(1)+' km · VISTA',16,h-16);}
  }
  updateUI(now){super.updateUI(now);if(!this.world.region)return;const p=this.sim.player,r=this.world.region(p.x,p.z);$('coordsLabel').textContent=r.subtitle+' · '+Math.floor(p.x/336)+', '+Math.floor(p.z/336);if(this.sim.free&&!this.sim.job){$('objectiveTitle').textContent='SIGUE EL HORIZONTE';$('objectiveText').textContent='Sal de Distrito Cero por cualquier carretera. M abre las regiones y sus rutas.';$('objectiveMeta').textContent='SEMILLA '+this.world.seed+' · '+(this.sim.stats.distance/1000).toFixed(1)+' KM RECORRIDOS';}}
 }
 D.HorizonApp=HorizonApp;D.App=HorizonApp;
})(DC);
