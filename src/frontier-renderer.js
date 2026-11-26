/* Streaming presentation only. Bounded GL buffers with chunk-local coordinates. */
'use strict';
(function(D){
 const Base=D.Renderer;
 function extraGeometry(){
  const out=[];const tri=(a,b,c)=>{const n=D.normalize(D.cross(b.map((v,i)=>v-a[i]),c.map((v,i)=>v-a[i])));for(const p of[a,b,c])out.push(...p,...n,(p[0]+.5),(p[2]+.5));};
  const a=[-.5,0,-.5],b=[.5,0,-.5],c=[0,.6,-.5],d=[-.5,0,.5],e=[.5,0,.5],f=[0,.6,.5];tri(a,c,b);tri(d,e,f);tri(a,d,f);tri(a,f,c);tri(b,c,f);tri(b,f,e);return out;
 }
 // Detail records follow the lifetime of their uploaded sector. The frame loop
 // appends the near records to the existing dynamic box batch.
 const shopDetailBySector=new WeakMap();
 const shopPaint=[[.12,.30,.24],[.43,.22,.14],[.24,.31,.35]];
 const shopSigns=[3,10,2];
 function cornerShop(cell){
  if(cell.type!=='urban'||cell.park||cell.seed<.35||!cell.buildings.length)return null;
  // Lowest seed picks one tenant per block independently of sector load order.
  const b=cell.buildings.reduce((best,building)=>building.seed<best.seed?building:best);
  const sx=Math.sign(b.x-cell.x),sz=Math.sign(b.z-cell.z);
  if(!cell.roads[sx>0?'e':'w']||!cell.roads[sz>0?'s':'n'])return null;
  return {b,sx,sz,x:b.x+sx*b.w/2,z:b.z+sz*b.d/2};
 }
 function buildCornerShop(shop,add,nearBox,wall){
  const {b,x,z,sx,sz}=shop;
  const width=9.6,side=5.2,depth=1.12,floor=.26,ceiling=3.75;
  const trim=[.22,.20,.16],stone=[.48,.45,.37],wood=[.38,.25,.15];
  const variant=b.sign%shopPaint.length,paint=shopPaint[variant];
  // u and v are metres inward from the intersection-facing corner.
  const box=(u,y,v,du,h,dv,col,mat=0,em=0)=>add('box',x-sx*u,y,z-sz*v,du,h,dv,col,mat,em);
  const close=(u,y,v,du,h,dv,col,mat=0,em=0)=>nearBox(x-sx*u,y,z-sz*v,du,h,dv,col,mat,em);
  const podium=(u0,u1,v0,v1,col)=>box((u0+u1)/2,(ceiling+floor)/2,(v0+v1)/2,u1-u0,ceiling-floor,v1-v0,col);

  add('box',b.x,(b.h+.15+ceiling)/2,b.z,b.w,b.h+.15-ceiling,b.d,wall,1,0,0,b.seed,b.style);
  box(b.w/2,.20,b.d/2,b.w+.28,.12,b.d+.28,stone);
  podium(0,b.w,side,b.d,wall);
  podium(width,b.w,0,side,wall);
  podium(depth,width,depth,side,[.39,.32,.23]);

  // Two sealed glazing planes on the original collision envelope. The
  // transparent quad is also used for particles with a different material.
  const frontYaw=sz>0?0:Math.PI;
  add('smoke',x-sx*width/2,1.75,z,width,2.98,1,[.16,.26,.25],6,0,frontYaw);
  add('smoke',x,1.75,z-sz*side/2,side,2.98,1,[.16,.26,.25],6,0,sx*Math.PI/2);

  const doorJamb=width-1.52;
  box(doorJamb/2,.49,0,doorJamb,.46,.21,stone);
  box(0,.49,side/2,.21,.46,side,stone);
  for(const u of [0,doorJamb/2,doorJamb,width])box(u,1.74,0,.11,2.96,.14,trim,3);
  for(const v of [side/2,side])box(0,1.74,v,.14,2.96,.11,trim,3);
  box(width/2,2.57,0,width,.09,.14,trim,3);
  box(0,2.57,side/2,.14,.09,side,trim,3);
  // Cantilever over the pavement. The two runs meet edge-to-edge at the corner.
  box((width-1.08)/2,2.99,-.51,width+1.08,.16,1.14,paint,3);
  box(-.51,2.99,(side+.06)/2,1.14,.16,side-.06,paint,3);
  box(width/2,3.47,.39,width,.56,.94,paint);
  box(.40,3.47,(side+.86)/2,.96,.56,side-.86,paint);
  add('box',x-sx*width*.48,3.73,z+sz*.12,3.55,1.22,.12,[1,1,1],10+shopSigns[variant],0,frontYaw);
  // Timber shelf and return wall are visible through the glass from the street.
  for(const y of [1.02,1.73]){
   box(4.35,y,.69,6.1,.065,.53,wood);
   box(.70,y,3.0,.51,.065,2.9,wood);
  }
  box(doorJamb+.76,1.39,.94,1.30,2.23,.10,[.19,.23,.22]);
  box(doorJamb+.76,.29,0,1.40,.06,.32,stone);

  // Small features are prepared once, then streamed only near the eye.
  close(doorJamb+.28,1.30,-.11,.042,.39,.049,[.68,.68,.58],3);
  for(const y of [1.16,1.45])close(doorJamb+.28,y,-.07,.043,.037,.09,trim,3);
  close(3.93,2.91,.43,5.4,.035,.10,[.95,.79,.48],0,.7);
  const stock=[[.42,.23,.15],[.67,.51,.26],[.20,.35,.29]];
  for(let bay=0;bay<3;bay++){
   const u=2.1+bay*1.91;
   close(u,1.17,.66,1.48,.25,.40,wood);
   for(let i=0;i<3;i++)close(u+(i-1)*.37,1.33,.65,.30,.27,.31,stock[(bay+i+variant)%3]);
   close(u+.10,1.95,.74,.62,.36,.23,stock[(bay+variant)%3]);
  }
  for(let i=0;i<3;i++)close(.76,1.29,1.96+i*1.0,.29,.46,.65,stock[(variant+i)%3]);
 }
 class FrontierRenderer extends Base{
  buildCity(){} // Replaces one finite city batch with independently disposable sectors.
  constructor(...a){super(...a);this.sectorGPU=new Map();this.streamSeed=this.world.seed;this.renderOrigin=[0,0];this.daylight=.62;this.streamStats={loaded:0,pending:0,instances:0,buffers:0};
   for(const [name,data]of[['gable',extraGeometry()]]){const m=this.createMesh(data);m.chunks=[];m.dynamicBuffer=this.gl.createBuffer();this.meshes[name]=m;this.static[name]=[];this.dynamic[name]=[];}
   this.syncSectors(25);
  }
  releaseSector(key){const entry=this.sectorGPU.get(key);if(!entry)return;for(const b of Object.values(entry))this.gl.deleteBuffer(b.buffer);this.sectorGPU.delete(key);}
  resetSectors(){for(const key of [...this.sectorGPU.keys()])this.releaseSector(key);for(const m of Object.values(this.meshes))m.chunks=[];this.streamSeed=this.world.seed;this.lightTime=-1;}
  syncSectors(budget=2){
   if(!this.canRender())return false;
   if(this.previewStudio){for(const m of Object.values(this.meshes))m.chunks=[];return;}
   if(this.streamSeed!==this.world.seed)this.resetSectors();const active=this.world.activeChunks||[];const desired=new Set(active.map(c=>c.key));
   for(const key of this.sectorGPU.keys())if(!desired.has(key))this.releaseSector(key);
   for(const chunk of active){if(this.sectorGPU.has(chunk.key))continue;if(budget--<=0)break;this.sectorGPU.set(chunk.key,this.buildSector(chunk));}
   for(const m of Object.values(this.meshes))m.chunks=[];
   let instances=0,buffers=0;for(const sector of this.sectorGPU.values())for(const[name,batch]of Object.entries(sector)){this.meshes[name].chunks.push(batch);instances+=batch.count;buffers++;}
   this.streamStats={loaded:this.sectorGPU.size,pending:active.length-this.sectorGPU.size,instances,buffers};
  }
  buildSector(chunk){
   const shops=[];
   const lists={};for(const name of Object.keys(this.meshes))lists[name]=[];
   const add=(...a)=>this.add(lists,...a),box=(x,y,z,sx,sy,sz,c,mat=0,em=0,yaw=0,seed=0,detail=0,pitch=0,roll=0)=>add('box',x,y,z,sx,sy,sz,c,mat,em,yaw,seed,detail,pitch,roll);
   const grass=[.13,.21,.105],curb=[.29,.31,.29],asphalt=[.048,.055,.058],stripe=[.62,.59,.39];
   for(const c of chunk.cells){
    const x0=c.ix*84,z0=c.iz*84,r=D.rng(Math.floor(c.seed*4294967295)),type=c.type,country=['village','farmland','woodland'].includes(type),field=type==='farmland',forest=type==='woodland';
    const ground=c.home?[.09,.11,.10]:field?[[.25,.22,.12],[.14,.22,.095],[.27,.27,.12],[.11,.19,.09]][c.crop]:forest?[.095,.145,.078]:grass;
    // Ground below the whole cell, then an inset land parcel. No grass plane under asphalt.
    box(c.x,-.52,c.z,84,.4,84,ground,4);
    const landW=84-(c.roads.w+c.roads.e)/2,landD=84-(c.roads.n+c.roads.s)/2;
    box(c.x+(c.roads.w-c.roads.e)/4,-.24,c.z+(c.roads.n-c.roads.s)/4,landW,.4,landD,ground,4);
    if((!country||c.park)&&type!=='suburb'){box(c.x,.045,c.z,62,.20,62,c.park?grass:curb,c.park?4:0);}
    for(const [side,width]of Object.entries(c.roads))if(width){
     const vertical=side==='w'||side==='e',edgeX=side==='w'?x0:side==='e'?x0+84:c.x,edgeZ=side==='n'?z0:side==='s'?z0+84:c.z;
     const rx=edgeX+(side==='w'?width/4:side==='e'?-width/4:0),rz=edgeZ+(side==='n'?width/4:side==='s'?-width/4:0);
     box(rx,-.037,rz,vertical?width/2:84,.020,vertical?84:width/2,asphalt,2);
     if(side==='w'||side==='n'){
      for(let k=0;k<6;k++){const q=k*14+7;box(vertical?edgeX:x0+q,-.022,vertical?z0+q:edgeZ,vertical?.12:6,.011,vertical?6:.12,stripe,3);}
      if(width>=20)for(const sign of[-1,1])box(vertical?edgeX+sign*8.9:c.x,-.022,vertical?c.z:edgeZ+sign*8.9,vertical?.12:62,.011,vertical?62:.12,[.67,.69,.65],3);
     }
     if(!country)box(edgeX+(side==='w'?width/2+1:side==='e'?-width/2-1:0),.05,edgeZ+(side==='n'?width/2+1:side==='s'?-width/2-1:0),vertical?2:62,.20,vertical?62:2,curb,0);
    }
    if(c.park){box(c.x,.16,c.z,3,.03,61,[.37,.33,.23],4);box(c.x,.16,c.z,61,.03,3,[.37,.33,.23],4);}
    if(field&&!c.buildings.length){
     const rows=c.crop===0?14:18;for(let i=0;i<rows;i++){const z=z0+15+i*(53/(rows-1));box(c.x,.01,z,54,.025,1.5,[.18,.125,.06],4);if(c.crop)box(c.x,.22+(c.crop===2?.15:0),z,53,.34,1.1,c.crop===2?[.35,.37,.12]:[.09,.235,.06],4);}
     box(c.x,-.05,z0+11,62,.05,.8,[.065,.21,.25],7); // Irrigation channel, inside parcel.
     for(const zz of [z0+11,z0+73]){for(let i=0;i<5;i++)box(x0+12+i*15,.54,zz,.10,1.1,.10,[.30,.22,.135]);box(c.x,.76,zz,61,.065,.065,[.38,.31,.20]);}
    }
    const shop=cornerShop(c);
    for(const b of c.buildings){
     if(b.landmark==='taller')continue;
     const kind=b.kind||'urban',retro=kind==='retro',rural=['village','suburb','barn','greenhouse'].includes(kind),future=kind==='future';
     const colors=retro?[[.47,.32,.23],[.32,.40,.35],[.54,.48,.33],[.36,.40,.46]]:rural?[[.49,.44,.33],[.44,.37,.29],[.43,.49,.46],[.48,.50,.44]]:[[.22,.255,.28],[.25,.28,.30],[.27,.295,.29],[.18,.225,.265]];
     const color=colors[Math.floor(b.tone*4)];
     if(kind==='greenhouse'){
      box(b.x,1.5,b.z,b.w,3,b.d,[.19,.31,.30],6);add('gable',b.x,3,b.z,b.w,3,b.d,[.31,.43,.39],6);
      for(let i=-2;i<=2;i++){box(b.x+i*5,1.55,b.z,.12,3.1,b.d+.1,[.56,.58,.53],3);box(b.x,1.3,b.z+i*4,b.w-.4,.20,1,[.10,.26,.085],4);}
     }else{
      if(b===shop?.b){
       const detail={box:[]};
       buildCornerShop(shop,add,(...args)=>this.add(detail,'box',...args),color);
       shops.push({x:shop.x,z:shop.z,boxes:detail.box});
      }else{
       add(future?'body':'box',b.x,b.h/2+.15,b.z,b.w,b.h,b.d,color,rural?0:1,0,0,b.seed,future?1:b.style);
       box(b.x,.45,b.z,b.w+.28,.8,b.d+.28,[.27,.28,.26]);
      }
      if(rural||retro){
       add('gable',b.x,b.h+.12,b.z,b.w+1.0,rural?4:2.4,b.d+1,[.30,.19,.13],0);
       box(b.x-b.w*.25,b.h+1.6,b.z-2,1.05,3.0,1.05,[.28,.26,.22]);
       for(const sign of[-1,1]){
        const face=b.z+sign*(b.d/2+.03);
        for(const off of[-.29,.29]){box(b.x+off*b.w,2.05,face,2.5,2,.08,[.10,.19,.19],6);box(b.x+off*b.w,3.13,face,2.9,.12,.22,[.71,.68,.55]);box(b.x+off*b.w,2.0,face,.09,2,.13,[.65,.61,.49]);}
        box(b.x,.96,face,1.1,1.9,.10,[.23,.19,.13],0);
        if(retro){box(b.x,3.75,face+sign*.8,b.w*.84,.16,2,[.25,.32,.30]);box(b.x,4.25,face+sign*1.7,b.w*.85,.065,.07,[.13,.16,.17],3);for(let k=-3;k<=3;k++)box(b.x+k*2.4,4.0,face+sign*1.7,.07,.70,.07,[.13,.16,.17],3);}
       }
       if(kind==='barn'){box(b.x,1.45,b.z+b.d/2+.09,5.2,2.9,.13,[.31,.16,.085]);for(const sign of[-1,1])box(b.x+sign*1.2,1.45,b.z+b.d/2+.17,.11,3.3,.11,[.69,.63,.48],0,0,0,0,0,0,sign*.6);}
       if(kind==='suburb'){box(b.x,2,b.z+b.d/2+4,b.w*.85,.16,7,[.28,.31,.27]);for(const sign of[-1,1])box(b.x+sign*b.w*.4,1,b.z+b.d/2+6,.15,2,.15,[.45,.45,.39]);}
      }else{
       box(b.x,b.h+.24,b.z,b.w+.24,.24,b.d+.24,[.19,.22,.235]);box(b.x+2,b.h+1.1,b.z-2,b.w*.3,1.6,b.d*.3,[.16,.19,.20],3);
       for(let y=5;y<b.h;y+=future?9:12)box(b.x,y,b.z,b.w+.12,.15,b.d+.12,future?[.26,.44,.46]:[.17,.20,.23],future?3:0);
       if(future){
        for(const sign of[-1,1])box(b.x+sign*(b.w*.5+.04),b.h*.53,b.z+b.d/2+.08,.09,b.h*.87,.13,[.08,.74,.81],0,1.8);
        for(let k=0;k<3;k++)box(b.x-6+k*5,b.h+1.0,b.z+2,3.7,.15,6,[.025,.12,.21],3,0,0,0,0,-.22);
        box(b.x,b.h*.68,b.z,b.w+1.1,.26,b.d+1.1,[.15,.63,.60],3,1.1);
       }
       if(b!==shop?.b){const edge=b.z+b.d/2+.09;box(b.x,2,edge,b.w*.75,2.5,.12,[.08,.17,.20],6);box(b.x,3.5,edge+.3,b.w*.83,.2,1.4,[.23,.26,.27],3);}
      }
     }
     if(b!==shop?.b&&!rural&&b.seed%4<1.2)box(b.x,retro?3.05:4.7,b.z+b.d/2+.3,Math.min(11,b.w*.8),retro?1.6:2.4,.15,[1,1,1],10+(retro?4:future?0:b.sign));
     if(rural){ // Each home connects to its nearest road, rather than opening onto a crop row.
      box(b.x,-.012,(z0+10+b.z-b.d/2)/2,2,.028,Math.max(.1,b.z-b.d/2-z0-10),[.34,.30,.22],4);
     }
    }
    // City services remain in their original locations, with physical signs.
    for(const p of (c.home?this.world.home.pois.filter(p=>Math.floor(p.x/84)===c.ix&&Math.floor(p.z/84)===c.iz):c.pois)){
     box(p.x,1.1,p.z,.3,2.2,.3,[.23,.27,.24],3);box(p.x,2.4,p.z,3.4,.9,.16,[.67,.86,.76],p.type==='garage'?15:p.type==='job'?23:22);
    }
    if(c.ix===0&&c.iz===0){box(13,.95,20,.65,1.8,.5,[.22,.32,.31],3);box(13,1.35,19.73,.48,.50,.035,[.1,.75,.64],0,1.1);}
    if(field&&c.seed>.94){const px=c.x,pz=c.z;box(px,10,pz,.4,20,.4,[.60,.62,.59],3);add('body',px,20,pz,1.8,.8,.9,[.69,.70,.65],3);for(let k=0;k<3;k++){const a=k*Math.PI*2/3;box(px+Math.sin(a)*3.7,20+Math.cos(a)*3.7,pz+.6,.35,7.5,.17,[.76,.77,.71],3,0,0,0,0,0,-a);}}
   }
   const entries={};for(const[name,data]of Object.entries(lists)){if(!data.length)continue;const packed=new Float32Array(data.length);for(let i=0;i<data.length;i++)packed[i]=data[i]-(i%16===0?chunk.x:i%16===2?chunk.z:0);const buffer=this.gl.createBuffer();this.gl.bindBuffer(this.gl.ARRAY_BUFFER,buffer);this.gl.bufferData(this.gl.ARRAY_BUFFER,packed,this.gl.STATIC_DRAW);entries[name]={buffer,count:data.length/16,basicMaterials:this.basicMaterialBatch(packed),baseX:chunk.x,baseZ:chunk.z,min:[chunk.x-12,-3,chunk.z-12],max:[chunk.x+348,170,chunk.z+348]};}
   if(shops.length)shopDetailBySector.set(entries,shops);
   return entries;
  }
  renderCornerShopDetails(){
   const [x,y,z]=this.camera.eye,radius=this.quality==='eco'?30:52,r2=radius*radius;
   if((y-1.5)**2>r2)return;
   for(const chunk of this.world.activeChunks){
    if(x<chunk.x-radius||x>chunk.x+336+radius||z<chunk.z-radius||z>chunk.z+336+radius)continue;
    const shops=shopDetailBySector.get(this.sectorGPU.get(chunk.key));
    if(shops)for(const shop of shops){
     if((x-shop.x)**2+(y-1.5)**2+(z-shop.z)**2<=r2)this.dynamic.box.push(...shop.boxes);
    }
   }
  }
  renderReactive(sim){
   super.renderReactive(sim);
   this.renderCornerShopDetails();
   // Distant vegetation is cheap geometry, while the interactive near tree retains its detail.
   for(const p of sim.dynamics.props){if(p.type!=='tree'||p.broken)continue;const dist=D.distance(p,sim.player),near=this.quality==='eco'?105:155;if(dist<=near||dist>600)continue;const s=p.scale||1;
    this.add(this.dynamic,'box',p.x,1.7*s,p.z,.25*s,3.4*s,.25*s,[.18,.13,.08],35);
    this.add(this.dynamic,'body',p.x,4.1*s,p.z,3.1*s,3.4*s,2.8*s,[.10,.19,.085],36);
   }
  }
  render(sim){
   if(!this.canRender())return false;
   const next=[Math.floor(this.camera.target[0]/336)*336,Math.floor(this.camera.target[2]/336)*336];if(next[0]!==this.renderOrigin[0]||next[1]!==this.renderOrigin[1]){this.lightTime=-1;this.lightVP=null;}this.renderOrigin=next;this.syncSectors(2);super.render(sim);
  }
 }
 D.FrontierRenderer=FrontierRenderer;D.Renderer=FrontierRenderer;
})(DC);
