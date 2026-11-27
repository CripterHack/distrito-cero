// QA for a real seeded route. Mesh coordinates, weights and palette rows are those of the street renderer.
options => {
 const far=typeof options==='object'?options.far:options, braking=!!options.braking;
 const {r,sim,ped,live,storage}=marketQA,gl=r.gl,route=ped.sidewalkRoute;
 const key=far?'marketPed1':'marketPed0',other=far?'marketPed0':'marketPed1';
 const dt=1/60,mesh=r.meshes[key],stride=DC.SkinRig.paletteStride;
 const previous=gl.getParameter(gl.ARRAY_BUFFER_BINDING),vbo=new Float32Array(mesh.count*16);
 gl.bindBuffer(gl.ARRAY_BUFFER,mesh.vbo);gl.getBufferSubData(gl.ARRAY_BUFFER,0,vbo);
 gl.bindBuffer(gl.ARRAY_BUFFER,previous);
 if(gl.getError())throw Error('Cannot read the production street vertex buffer');
 const feet={};
 for(const side of ['L','R']){
   // Each fixed sample is a unique point with weights. Triangulation and UV seams do not bias its mean.
   const points=new Map();
   for(let i=0;i<vbo.length;i+=16){
     const v=vbo.subarray(i,i+16);
     if((side==='L'?v[0]>0:v[0]<0)&&v[1]<.15)
       points.set([v[0],v[1],v[2],...v.subarray(8,16)].join(','),v);
   }
   const shoe=[...points.values()],bottom=Math.min(...shoe.map(v=>v[1]));
   const sole=shoe.filter(v=>v[1]<bottom+.015);
   if(sole.length<3||!Number.isFinite(bottom))throw Error('Missing tread patch '+side);
   feet[side]={shoe,sole:new Set(sole),bottom};
   if(braking){
     // Follow two fixed material points. The neutral shoe faces +Z, including at the north end.
     const zMin=Math.min(...sole.map(v=>v[2])),zMax=Math.max(...sole.map(v=>v[2]));
     const length=zMax-zMin;
     if(length<.12)throw Error('Tread has no longitudinal extent');
     const lowest=patch=>patch.reduce((a,b)=>a[1]<b[1]?a:b);
     feet[side].markers={
       heel:lowest(sole.filter(v=>v[2]<=zMin+.20*length)),
       toe:lowest(sole.filter(v=>v[2]>=zMax-.20*length))
     };
   }
 }
 function position(v,palette,inst){
   const xyz=[0,0,0];
   for(let k=0;k<4;k++){
     const j=v[8+k]*16,w=v[12+k];
     if(w===0)continue;
     for(let a=0;a<3;a++)
       xyz[a]+=w*(palette[j+a]*v[0]+palette[j+4+a]*v[1]+palette[j+8+a]*v[2]+palette[j+12+a]);
   }
   const [x,y,z]=xyz.map((value,i)=>value*inst[4+i]),c=Math.cos(inst[3]),s=Math.sin(inst[3]);
   return [inst[0]+c*x+s*z,inst[1]+y-(ped.groundY||0),inst[2]-s*x+c*z];
 }
 function sample(){
   const inst=r.dynamic[key];
   if(inst.length!==16||r.dynamic[other].length||inst[12]||inst[13]||inst[14]||ped.panic)
     throw Error('Expected one upright, calm Mercado instance in '+key);
   const slot=inst[15]-200;
   if(!Number.isInteger(slot)||slot<1||slot>=r.castCursor)throw Error('Invalid skin palette row');
   const palette=r.posePixels.subarray(slot*stride,(slot+1)*stride),feetWorld={};
   for(const [side,{shoe,sole}] of Object.entries(feet)){
     const center=[0,0,0];let clearance=Infinity;
     for(const v of shoe){
       const p=position(v,palette,inst);
       clearance=Math.min(clearance,p[1]);
       if(sole.has(v))for(let a=0;a<3;a++)center[a]+=p[a]/sole.size;
     }
     feetWorld[side]={center,clearance};
     if(braking)for(const [name,v] of Object.entries(feet[side].markers))
       feetWorld[side][name]=position(v,palette,inst);
   }
   return {...(braking?{brake:route.brake?.progress??null,...(route.brake?{clip:route.brake.clip}:{}),phase:ped.phase,towardEnd:route.towardEnd}:{}),time:sim.time,root:[ped.x,ped.z],yaw:inst[3],heading:ped.yaw,turn:route.turn?.progress??null,wait:route.wait,speed:ped.moveSpeed,feet:feetWorld};
 }
 function arrive(approach){
   const towardEnd=route.towardEnd,dest=towardEnd?route.endZ:route.startZ;
   const eye=far?[route.x+5.6,1.65,dest+23.7]:[route.x+2.05,1.30,dest+1.92];
   const target=[route.x,1.02,dest];
   if(sim.world.blocked(eye[0],eye[2],.18)||!sim.world.visible(eye[0],eye[2],route.x,dest))
     throw Error('Endpoint camera is obstructed');
   const floorProbes=[];
   for(const dx of [-.40,0,.40])for(const dz of [-.40,0,.40]){
     const floor=r.playerSurface(route.x+dx,dest+dz).shadow-.003;
     if(Math.abs(floor-ped.groundY)>.0001)throw Error('Footprint crosses a different street surface: '+floor);
     floorProbes.push(floor);
   }
   Object.assign(r.camera,{eye,target,initialized:true});r.fovOverride=.78;
   // Advance the full simulation. Warm the production renderer's time-based blend on approach.
   for(let i=0;i<1500;i++){
     sim.step(dt,{});
     if(approach && Math.abs(sim.time-approach.begin)<dt*.25){
       if(route.towardEnd!==towardEnd)throw Error('Approach starts after the endpoint');
       return {dest,eye,target,batch:key,fov:r.fovOverride,quality:r.quality,floorProbes,arrival:approach.arrival,towardEnd};
     }
     if(route.towardEnd!==towardEnd){
       if(Math.abs(ped.z-dest)>.002||Math.abs(route.wait-2.4)>.001||sim.peds.length!==72||ped.panic)
         throw Error('Unexpected endpoint, population, or stop');
       return {dest,eye,target,batch:key,fov:r.fovOverride,quality:r.quality,floorProbes,arrival:sim.time,towardEnd};
     }
     if(approach?Math.abs(ped.z-dest)<3:Math.abs(ped.z-dest)<1 && i%3===0)r.updateDynamic(sim);
   }
   throw Error('No natural arrival in 25 simulated seconds');
 }
 function frame({ticks,draw}){
   const rows=[];
   for(let i=0;i<=ticks;i++){
     if(ticks && i===0)continue;
     if(ticks)sim.step(dt,{});
     if(draw&&i===ticks){
       r.frame=0;r.lightTime=-1;r.lightVP=null;r.render(sim);gl.finish();
     }else r.updateDynamic(sim);
     rows.push(sample());
   }
   if(gl.getError()||gl.isContextLost()||r.streamStats.pending)throw Error('Incomplete WebGL2 frame');
   return {rows,png:draw?r.canvas.toDataURL('image/png').split(',')[1]:null};
 }
 function finish(){
   if(live!==JSON.stringify(DC_APP.sim.serialize())||storage!==JSON.stringify([...qaCharacterStorage]))
     throw Error('QA changed the live session or storage');
 }
 window.marketTurnQA={arrive,frame,finish};
 return Object.fromEntries(Object.entries(feet).map(([side,f])=>[side,{shoePoints:f.shoe.length,solePoints:f.sole.size,bindBottom:f.bottom,...(braking?{heel:Array.from(f.markers.heel.slice(0,3)),toe:Array.from(f.markers.toe.slice(0,3))}:{})}]));
}
