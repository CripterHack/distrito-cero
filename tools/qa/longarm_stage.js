/* Prepared diagnostic scene using production renderer/pose and isolated state. */
(function(global){
 'use strict';const D=global.DC,Q=global.DC_LONGARM_QA;let state;
 function init(){
  const a=global.DC_APP,r=a.renderer;DC_MANUAL_FRAMES.start(a);
  const sim=new D.Simulation(new D.World(1337));sim.free=true;sim.wanted=sim.heat=0;
  sim.peds.forEach(n=>n.hidden=true);sim.dynamics.props=[];
  sim.cars.forEach((car,i)=>Object.assign(car,{x:5000+i*6,z:5000,driver:null,parked:true,speed:0}));
  state={a,r,sim,live:JSON.stringify(a.sim.serialize()),store:JSON.stringify([...qaLongarmStore]),draws:0,last:null};
  r.world=sim.world;r.rain=r.bloom=0;r.previewStudio=false;r.equipmentView=false;r.frozenHandling=null;
  r.canvas.removeAttribute('style');r.previewSize=null;r.resize();
  const original=r.drawEquipment;
  r.drawEquipment=function(s,m,e){const result=original.call(this,s,m,e);state.draws++;
   state.last={mount:m,actor:{...s.player},pose:{matrices:this.heroPalette.slice(),rootY:this.motionDebug.rootY,scale:1}};
   return result;};
  const gl=r.gl,ext=gl.getExtension('WEBGL_debug_renderer_info');
  return{quality:r.quality,viewport:[innerWidth,innerHeight],drawingBuffer:[gl.drawingBufferWidth,gl.drawingBufferHeight],
   renderer:gl.getParameter(ext?ext.UNMASKED_RENDERER_WEBGL:gl.RENDERER),version:gl.getParameter(gl.VERSION),seed:1337};
 }
 function prepare(config){
  const {sim:s,r}=state;
  Object.assign(s.player,{x:4,z:36,y:0,yaw:0,vy:0,vx:0,vz:0,car:null,moveSpeed:0,walk:0,crouch:config.crouch||0});
  s.setIdentity('Contacto largo',{...D.Appearance.default(),neckLength:config.neck||0});
  s.equipment=D.Equipment.initial();s.equipWeapon(config.item);s.equipment.handling.ready=1;
  s.equipment.aimWeight=config.aim??1;s.equipment.pitch=config.pitch||0;s.time=1.25;
  // Prepared settled aim includes the presentation filter, not just simulation intent.
  if(config.item==='rifle')s.equipment.handling.rifleAim=config.aim??1;
  r.motionTracker.clear();r.motionScene=s;r.frozenHandling=null;r.previewStudio=false;r.equipmentView=false;
  r.daylight=.67;r.lightTime=-1;r.fovOverride=.62;
  r.camera.target=[4.015,1.40-s.player.crouch*.22,36.25];
  r.camera.eye=config.front?[3.9,1.55-s.player.crouch*.22,37.85]:[5.6,1.54-s.player.crouch*.22,36.9];
  r.camera.initialized=true;
 }
 function observe(){
  const {a,r,sim:s}=state,count=state.draws;
  DC_MANUAL_FRAMES.draw(a,s);
  if(state.draws!==count+1)throw new Error('Missing or repeated production equipment draw');
  const before=JSON.stringify(s.serialize()),measurement=Q.inspect(s,state.last);
  const stockClearance=s.equipment.selected==='rifle'?DC_STOCK_CLEARANCE.inspect(s,state.last):null;
  if(before!==JSON.stringify(s.serialize()))throw new Error('Auditor mutated game state');
  return{measurement,screening:Q.screen(measurement),counterfactual:Q.translateToEye(measurement),
   stockClearance,stockScreen:stockClearance?DC_STOCK_CLEARANCE.screen(stockClearance):null,
   frame:r.frame,draws:state.draws,seed:1337,time:s.time,appearance:structuredClone(s.appearance),
   actor:{x:s.player.x,y:s.player.y,z:s.player.z,yaw:s.player.yaw,crouch:s.player.crouch},
   pitch:s.equipment.pitch,aim:s.equipment.aimWeight,camera:structuredClone(r.camera),fov:r.fovOverride,
   actors:r.castStats.actors,triangles:r.castStats.triangles};
 }
 function sample(config){prepare(config);return observe();}
 function stepCycle(start){
  const {sim:s}=state,points=[];
  for(let i=start;i<start+10;i++){
   s.time+=1/60;s.equipmentStep(1/60,{aim:i<40});
   const measurement=Q.inspect(s);points.push({frame:i+1,eyeError:measurement.eyeError,stockError:measurement.stockError});
  }
  return{points,rendered:observe()};
 }
 function matrix(){
  const rows=[];
  for(const item of Q.items)for(const neck of [-1,0,1])for(const crouch of [0,1])for(const pitch of [-.3,0,.3]){
   const s=DC_SIDEARM_SIGHT_QA.scene(item);s.appearance.neckLength=neck;s.player.crouch=crouch;s.equipment.pitch=pitch;
   const measurement=Q.inspect(s);rows.push({item,neck,crouch,pitch,measurement,screening:Q.screen(measurement)});
  }
  return rows;
 }
 function pristine(){return state.live===JSON.stringify(state.a.sim.serialize())&&state.store===JSON.stringify([...qaLongarmStore]);}
 global.DC_LONGARM_STAGE=Object.freeze({init,sample,stepCycle,matrix,pristine});
})(globalThis);
