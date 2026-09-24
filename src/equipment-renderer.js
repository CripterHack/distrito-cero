/* Arsenal presentation only: mesh sharing, IK landmarks, camera optics and bounded FX. */
'use strict';
(function(D){
 const Base=D.Renderer,E=D.Equipment;
 class EquipmentRenderer extends Base{
  constructor(...args){super(...args);this.equipmentMeshes=new Map();this.equipmentView=false;this.equipmentStats={};
   for(const w of E.catalog){const parts=D.EquipmentGeometry.build(w.id).map(p=>{const key='equip_'+w.id+'_'+p.name,m=this.createMesh(p.data);m.chunks=[];m.dynamicBuffer=this.gl.createBuffer();this.meshes[key]=m;this.static[key]=[];this.dynamic[key]=[];return{...p,data:undefined,key,count:p.data.length/24};});this.equipmentMeshes.set(w.id,parts);}
  }
  // Share the existing visual tracker between drawing, menu freeze and selection.
  // Sampling is idempotent at a simulation instant and never writes game state.
  handlingActor(sim,n=sim.player){
   if(this.previewStudio||!this.motionTracker)return n;
   if(this.motionScene!==sim){this.motionTracker.clear();this.motionScene=sim;}
   return this.motionTracker.update('player',n,sim.time,false);
  }
  freezeHandling(sim){
   if(sim.equipmentAvailable?.()&&sim.equipment.selected!=='unarmed'){
    const tracked=this.handlingActor(sim);const m=D.WeaponHandling.present(sim,tracked);this.frozenHandling={mount:m,equipment:{...sim.equipment},actor:D.WeaponHandling.actor(tracked,m,sim.equipment)};
   }else this.frozenHandling=null;
  }
  renderPerson(n,isPlayer=false){
   if(!this.previewStudio&&isPlayer&&(this.frozenHandling||this.currentSim.equipmentAvailable?.()&&this.currentSim.equipment.selected!=='unarmed')){
    const frozen=this.frozenHandling,e=frozen?.equipment||this.currentSim.equipment,w=E.get(e.selected),tracked=frozen?.actor||this.handlingActor(this.currentSim,n),m=frozen?.mount||D.WeaponHandling.present(this.currentSim,tracked);
    if(!(w.kind==='optics'&&this.equipmentView&&e.aiming)){
     super.renderPerson(frozen?.actor||D.WeaponHandling.actor(tracked,m,e),true);
     this.drawEquipment(this.currentSim,m,e);
    }
    return;
   }
   if(!isPlayer&&n.combatStunUntil>this.currentTime){super.renderPerson({...n,crouch:1,stagger:.8,bodyLean:.7,moveSpeed:0,y:-.20,lookPitch:.28},false);return;}
   if(!isPlayer&&n.combatHitUntil>this.currentTime){super.renderPerson({...n,stagger:.8,bodyLean:-.10},false);return;}
   super.renderPerson(n,isPlayer);
  }
  drawEquipment(sim,m=D.WeaponHandling.present(sim),e=sim.equipment){
   const w=E.get(m.displayItem||e.selected),parts=this.equipmentMeshes.get(w.id)||[];
   for(const p of parts){
    const emission=p.material===0?(w.kind==='gauss'?.2+e.charge*3.5:w.kind==='emp'?1.1:.1):0;
    const transform=m.partTransform(p.role);
    this.add(this.dynamic,p.key,...transform.origin,1,1,1,p.color,p.material,emission,transform.yaw,0,0,transform.rx,transform.roll);
   }
   this.equipmentStats={selected:w.id,logicalSelected:e.selected,handoff:m.handoff,parts:parts.length,triangles:parts.reduce((v,p)=>v+p.count,0),hands:m.hands,phase:m.phase,reloadStage:m.reloadStage,magazine:m.magazine,palms:m.palmContacts,brace:m.brace,fitDistance:m.fitDistance,inertia:m.inertia,grips:m.grips,contacts:this.motionDebug?.contacts||null};
   if(e.recoil>.55&&['hitscan','rocket','gauss'].includes(w.kind)){const size=w.kind==='gauss'?.09:.055;this.add(this.dynamic,'sphere',...m.muzzle,size,size,size,w.kind==='gauss'?[.25,.75,1]:[1,.63,.23],0,2.0);}
  }
  segment(a,b,width,color,emission=0){const v=b.map((n,i)=>n-a[i]),len=Math.hypot(...v);if(len<.001)return;this.add(this.dynamic,'body',...(a.map((v,i)=>(v+b[i])*.5)),width,width,len,color,0,emission,Math.atan2(v[0],v[2]),0,0,-Math.asin(D.clamp(v[1]/len,-1,1)),0);}
  renderReactive(sim){super.renderReactive(sim);if(this.previewStudio||!sim.equipment)return;
   for(const f of sim.weaponEffects){const alpha=D.clamp(f.life/f.total,0,1),t=1-alpha;if(f.kind==='trace'||f.kind==='gauss')this.segment(f.from,f.to,(f.kind==='gauss'?.021:.006)*(alpha*.5+.5),f.color,f.kind==='gauss'?2:1.2);
    else if(f.point){const r=f.radius*(f.kind==='emp'?Math.sin(t*Math.PI*.5):(.08+t*.9)),count=f.kind==='emp'?56:32;
     for(let j=0;j<count;j++){const a=j*Math.PI*2/count,b=(j+1)*Math.PI*2/count;this.segment([f.point[0]+Math.cos(a)*r,.20+Math.sin(t*Math.PI)*.30,f.point[2]+Math.sin(a)*r],[f.point[0]+Math.cos(b)*r,.20+Math.sin(t*Math.PI)*.30,f.point[2]+Math.sin(b)*r],f.kind==='emp'?.022:.050,f.color,1.2*alpha);}
     if(f.kind==='blast'&&t<.24)this.add(this.dynamic,'sphere',...f.point,.30+t*4,.35+t*4,.30+t*4,f.color,0,2*alpha);
    }
   }
   for(const p of sim.weaponProjectiles){const yaw=Math.atan2(p.velocity[0],p.velocity[2]),pitch=-Math.asin(D.clamp(p.velocity[1]/Math.max(.001,Math.hypot(...p.velocity)),-1,1));this.add(this.dynamic,'body',...p.position,.07,.07,p.kind==='rocket'?.33:.12,p.kind==='rocket'?[.29,.35,.34]:[.18,.23,.14],3,0,yaw,0,0,pitch);if(p.kind==='rocket')this.segment(p.position,p.position.map((v,i)=>v-p.velocity[i]*.025),.035,[1,.50,.19],1.5);}
   for(const c of sim.cars)if(c.empUntil>sim.time&&D.distance(c,sim.player)<75){const q=D.carPoint(c,0,.8),life=c.empUntil-sim.time;for(let k=0;k<3;k++){const off=(k-1)*.27,phase=sim.time*2+k;this.segment([q.x+off,.88,q.z-.4],[q.x+off+.08*Math.sin(phase),1.0,q.z+.35],.012,[.2,.68,1],.7);}this.add(this.dynamic,'sphere',c.x,1.90,c.z,.08,.08,.08,[.1,.6,1],0,.65);}
   // Physical resupply locker at the starting crossing, outside the campaign telephone.
   this.add(this.dynamic,'body',10,.59,1,.65,1.18,.48,[.042,.097,.108],3);this.add(this.dynamic,'box',10,.89,.748,.48,.04,.014,[.5,.86,.77],0,.8);this.add(this.dynamic,'box',10,.56,.74,.34,.018,.018,[.23,.35,.35],3);
  }
  updateCamera(sim,dt,options={}){
   const e=sim.equipment,w=e&&E.get(e.selected),active=!!(w&&w.kind!=='none'&&sim.equipmentAvailable()&&!options.menu&&!options.photo&&!this.previewStudio);
   this.equipmentView=active;
   if(!active){this.fovOverride=null;super.updateCamera(sim,dt,options);return;}
   const c=this.camera,p=sim.player,optic=w.kind==='optics'&&e.aiming,scope=w.id==='sniper'&&e.aiming,yaw=c.yaw,pitch=D.clamp(c.weaponPitch||0,-.70,.70),dir=[Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)];
   const distance=optic?.0:e.aiming?1.8:2.6,side=optic?0:-.58,base=1.65-D.CharacterFit.drop(sim.appearance?.neckLength)-(p.crouch||0)*.22+(p.y||0),dx=-Math.sin(yaw)*distance+Math.cos(yaw)*side,dz=-Math.cos(yaw)*distance-Math.sin(yaw)*side;
   const q=this.world.move(p.x,p.z,dx,dz,.12);let eye=[q.x,base+.055,q.z];if(optic)eye=[p.x+dir[0]*.13,base,p.z+dir[2]*.13];
   c.eye=eye;c.target=eye.map((v,i)=>v+dir[i]*4);c.initialized=true;
   this.fovOverride=optic?2*Math.atan(Math.tan(Math.PI*.36/2)/E.zoom[e.zoom]):scope?2*Math.atan(Math.tan(Math.PI*.36/2)/4):e.aiming?.79:Math.PI*.36;
   if(!this.reducedMotion&&e.recoil>.02)c.target[1]+=e.recoil*(w.kind==='gauss'?1.4:.7);
  }
 }
 D.EquipmentRenderer=EquipmentRenderer;D.Renderer=EquipmentRenderer;
})(DC);
