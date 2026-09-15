/* Development-only fixtures: never bundled by build.py. Uses the real D.Renderer.
   Canonical-surface and skeleton measurements are distinct, not clinical anatomy.
   Scene/clock preparation is explicit and does not constitute a gameplay test. */
'use strict';
(function(global){
 const D=global.DC, cache=new Map();let state=null;
 function raw(name){
  if(cache.has(name))return cache.get(name);
  const part=D.HeroAsset.parts.find(p=>p.name===name);
  if(!part)throw new Error('Missing canonical part: '+name);
  const bytes=Uint8Array.from(atob(part.data),c=>c.charCodeAt(0)),view=new DataView(bytes.buffer),points=[];
  for(let i=0;i<part.vertices;i++)points.push([0,2,4].map(k=>view.getInt16(i*24+k,true)/1e4));
  cache.set(name,points);return points;
 }
 function bounds(points){
  if(!points.length)throw new Error('Anatomical sample is empty.');
  const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  for(const p of points)for(let i=0;i<3;i++){if(!Number.isFinite(p[i]))throw new Error('Nonfinite mesh sample.');min[i]=Math.min(min[i],p[i]);max[i]=Math.max(max[i],p[i]);}
  return {min,max,widthM:max[0]-min[0],heightM:max[1]-min[1],depthM:max[2]-min[2],samples:points.length};
 }
 function profileMetrics(input){
  const look=D.Appearance.copy(input),drop=D.CharacterFit.drop(look.neckLength),fit=D.CharacterFit.fittedBones(D.SkinRig.bones,drop);
  const byName=Object.fromEntries(fit.map(([name,,position])=>[name,position]));
  const transform=(p,mat)=>D.CharacterFit.point(D.Appearance.shapePoint(p,mat,look.build,look.face,look.neck),drop);
  const face=raw('face'),neck=face.filter(p=>p[1]>=1.49&&p[1]<=1.51);
  return {units:'metres',axes:'Y-up, +Z forward',boneCount:fit.length,
   headToChestPivotM:Math.hypot(...byName.head.map((v,i)=>v-byName.chest[i])),
   shoulderJointSpanM:Math.hypot(...byName.upperArmR.map((v,i)=>v-byName.upperArmL[i])),neckDropM:drop,
   fittedBind:byName,surfaces:{face:bounds(face.map(p=>transform(p,40))),neckBand:bounds(neck.map(p=>transform(p,40)))},
   note:'Face includes canonical lower neck. Neck sample is the canonical 1.490–1.510 m band after appearance/fit, not a universal anatomical target.'};
 }
 function geometryBudget(lodParts,style){
  if(!Array.isArray(lodParts)||lodParts.length!==3||!Number.isInteger(style)||style<0||style>10)throw new Error('Invalid LOD budget input.');
  return lodParts.map((parts,lod)=>{
   const bodyTriangles=parts.reduce((n,p)=>n+p.vertices/3,0),hairTriangles=D.HairGeometry.build(style,lod).reduce((n,p)=>n+p.data.length/48,0);
   if(!Number.isFinite(bodyTriangles)||bodyTriangles<0)throw new Error('Invalid renderer vertex count.');
   return {lod,bodyTriangles,hairTriangles,totalTriangles:bodyTriangles+hairTriangles,note:'Geometry counts, not FPS, GPU time or VRAM.'};
  });
 }
 function init(){
  const a=global.DC_APP;if(!a)throw new Error('Game has not booted.');a.stopFrame?.();
  const sim=new D.Simulation(new D.World(1337));sim.free=true;
  state={a,sim,r:a.renderer,player:structuredClone(sim.player),live:JSON.stringify(a.sim.serialize()),store:JSON.stringify([...global.qaCharacterStorage.entries()])};
  sim.peds.forEach(n=>n.hidden=true);sim.dynamics.props=[];
  const css=document.createElement('style');css.textContent='body>*:not(#world){visibility:hidden!important}#world{visibility:visible!important;position:fixed!important;inset:0!important;width:100vw!important;height:100vh!important}';document.head.append(css);
  state.r.canvas.removeAttribute('style');state.r.previewSize=null;state.r.rain=0;state.r.bloom=0;state.r.resize();
  const g=state.r.gl,ext=g.getExtension('WEBGL_debug_renderer_info');
  return {version:g.getParameter(g.VERSION),renderer:ext?g.getParameter(ext.UNMASKED_RENDERER_WEBGL):g.getParameter(g.RENDERER),viewport:[innerWidth,innerHeight],drawingBuffer:[g.drawingBufferWidth,g.drawingBufferHeight],quality:state.r.quality};
 }
 function applyCase(c){
  if(!state)throw new Error('Initialize the benchmark first.');
  const {sim:s,r}=state,look={...D.Appearance.default(),...c.look},spec=c.sample;
  if(!D.Appearance.valid(look))throw new Error('Invalid benchmark appearance.');
  s.access=null;s.player=structuredClone(state.player);
  Object.assign(s.player,{x:4,z:36,yaw:0,y:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0,crouch:0,sprintBlend:0,seatBlend:0,seated:false,health:100},spec.actor);
  s.setIdentity('Referencia',look);s.equipment=D.Equipment.initial();s.time=c.time;s.wanted=0;s.heat=0;
  for(const [i,car] of s.cars.entries())Object.assign(car,{x:5000+i*6,z:5000,parked:true,speed:0,driver:null,boarding:false,doorOpen:0});
  if(spec.weapon){
   s.equipWeapon(spec.weapon);const e=s.equipment;e.aimWeight=spec.aim||0;e.aiming=e.aimWeight>.5;e.pitch=0;
   if(e.handling){e.handling.ready=1;e.handling.kick=0;}
   if(spec.reload){e.reloading=(1-spec.reload)*D.Equipment.get(spec.weapon).reload;e.reloadId=spec.weapon;}
  }
  if(c.pose==='seated'||c.pose==='entry'){
   const car=s.cars[0];Object.assign(car,{x:5.85,z:36,yaw:0,steerAngle:.15});
   if(c.pose==='seated'){s.player.car=0;s.player.x=car.x;s.player.z=car.z;}
   else{s.startAccess();if(!s.access)throw new Error('Entry fixture failed to start a real access transaction.');s.access.elapsed=s.access.approach+s.access.opening+s.access.entry*.4;car.doorOpen=1;}
  }
  r.world=s.world;r.previewStudio=spec.scene==='studio';r.equipmentView=false;r.equipmentStats={};r.frozenHandling=null;
  r.motionTracker.clear();r.motionScene=s;
  if(c.pose==='brake')r.motionTracker.update('player',{...s.player,moveSpeed:6.1},s.time-.1,true);
  if(r.previewStudio){s.player.x=0;s.player.z=0;}
  const actor=s.access?s.accessPlayerPose():s.player,center=[actor.x,c.pose==='crouch'?.74:.93,actor.z];
  const distance=c.pose==='seated'||c.pose==='entry'?4.2:3.3;
  r.camera.eye=[center[0]+Math.sin(c.yaw)*distance,center[1]+.10,center[2]+Math.cos(c.yaw)*distance];r.camera.target=center;r.camera.initialized=true;r.fovOverride=.62;
  s.world.lights=(c.light==='side'?[[-1.6,2.8,2,true],[1.5,2.3,-1.2,false]]:[[-3,4,3,true],[3,3,2,false],[1,3,-3,false]])
   .map(([x,y,z,warm])=>({x:x+actor.x,y,z:z+actor.z,warm}));
  s.dynamics.lightActive=()=>true;r.daylight=c.daylight;r.lightTime=-1;r.lightVP=null;r.frame=0;
  r.render(s);r.gl.finish();
  const g=r.gl,glError=g.getError(),finitePalette=Array.from(r.heroPalette).every(Number.isFinite),equipment=r.equipmentStats;
  if(g.isContextLost()||glError!==g.NO_ERROR||!finitePalette||r.castStats.actors<1)throw new Error('Invalid production-renderer sample: '+JSON.stringify({glError,finitePalette,actors:r.castStats.actors}));
  return {glError,finitePalette,actors:r.castStats.actors,triangles:r.castStats.triangles,
   characterLOD:r.castStats.lod,drawBatches:r.castStats.drawBatches,hairStyle:look.hairStyle,
   camera:{eye:[...r.camera.eye],target:[...r.camera.target],fov:r.fovOverride},
   selected:s.equipment.selected,accessPhase:s.access?.kind? s.accessPlayerPose().accessPhase:null,
   equipment:equipment.selected?{selected:equipment.selected,phase:equipment.phase,contacts:equipment.contacts,palms:equipment.palms,magazine:equipment.magazine}:null,
   resources:r.resources?.stats()||null,lodBudgets:geometryBudget(r.lodParts,look.hairStyle),appearance:look,anatomy:profileMetrics(look),scene:spec.scene,
   storageUntouched:JSON.stringify([...global.qaCharacterStorage.entries()])===state.store,
   liveSimulationUntouched:JSON.stringify(state.a.sim.serialize())===state.live};
 }
 global.DCCharacterBenchmark=Object.freeze({init,applyCase,profileMetrics,geometryBudget});
})(globalThis);
