/* One shared skinned mesh per material/LOD, bone texture per actor. No per-NPC draw calls. */
'use strict';
(function(D){
 const Base=D.Renderer;
 function steeringRing(){const out=[],s=24,t=6,R=.155,r=.018;
  const v=(a,b)=>{const c=Math.cos(a),n=Math.sin(a),d=R+r*Math.cos(b);return[c*d,n*d,r*Math.sin(b),c*Math.cos(b),n*Math.cos(b),Math.sin(b),a/(2*Math.PI),b/(2*Math.PI)];};
  for(let i=0;i<s;i++)for(let j=0;j<t;j++){const a=i*Math.PI*2/s,b=j*Math.PI*2/t,A=v(a,b),B=v(a+Math.PI*2/s,b),C=v(a+Math.PI*2/s,b+Math.PI*2/t),E=v(a,b+Math.PI*2/t);out.push(...A,...B,...C,...A,...C,...E);}return out;
 }
 class CastRenderer extends Base{
  constructor(...args){
   super(...args);const g=this.gl;this.posePixels=new Float32Array(D.SkinRig.paletteStride*128);this.crowdTexture=g.createTexture();g.bindTexture(g.TEXTURE_2D,this.crowdTexture);g.texImage2D(g.TEXTURE_2D,0,g.RGBA32F,D.SkinRig.paletteWidth,128,0,g.RGBA,g.FLOAT,this.posePixels);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);
   this.dualPixels=new Float32Array(D.SkinRig.bones.length*8*128);this.dualTexture=g.createTexture();g.activeTexture(g.TEXTURE8);g.bindTexture(g.TEXTURE_2D,this.dualTexture);g.texImage2D(g.TEXTURE_2D,0,g.RGBA32F,D.SkinRig.bones.length*2,128,0,g.RGBA,g.FLOAT,this.dualPixels);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);
   this.appearancePixels=new Float32Array(128*8);this.appearanceTexture=g.createTexture();g.bindTexture(g.TEXTURE_2D,this.appearanceTexture);g.texImage2D(g.TEXTURE_2D,0,g.RGBA32F,2,128,0,g.RGBA,g.FLOAT,this.appearancePixels);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.NEAREST);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);
   this.hairParts=new Map();this.lodParts=[[],[],[]];this.lodHistory=new Map();this.motionTracker=new D.MotionTracker(144);this.motionScene=null;this.castCursor=1;this.castStats={};
   for(const part of this.heroParts){
    if(part.name==='scalp')continue;
    let src=D.Realism.decode(D.HeroAsset.parts.find(p=>p.name===part.name));
    if(part.name==='hair'){src=D.HairGeometry.brows(src);this.deleteMesh(this.meshes[part.key]);this.meshes[part.key]=this.createSkinMesh(src);part.vertices=src.length/16;}

    this.meshes[part.key].crowd=true;this.lodParts[0].push(part);
    for(let lod=1;lod<=2;lod++){
     const fine=['face','skin','eye','iris','pupil','lip','hair','scalp'].includes(part.name),cell=lod===1?(fine?.009:.027):(fine?.025:.060),data=D.CrowdGeometry.reduce(src,part.name==='face'?cell*.65:cell,{preserveUV:part.name==='face'});
     if(!data.length)continue;const key='crowd'+lod+'_'+part.name,m=this.createSkinMesh(data);m.crowd=true;this.meshes[key]=m;this.dynamic[key]=[];this.static[key]=[];this.lodParts[lod].push({...part,key,vertices:data.length/16});
    }
   }
   for(const part of this.assetParts)if(part.name.startsWith('GLASS'))this.meshes[part.key].transparent=true;
   // Window panel has a separate transparent draw, instead of an opaque black block.
   const box=this.createMesh(steeringRing());box.dynamicBuffer=g.createBuffer();box.chunks=[];this.meshes.steeringRing=box;this.static.steeringRing=[];this.dynamic.steeringRing=[];
   const original=this.meshes.body;this.meshes.glassPanel={...original,chunks:[],dynamicBuffer:g.createBuffer(),dynamicCount:0,transparent:true,sharedGeometry:true};this.static.glassPanel=[];this.dynamic.glassPanel=[];
   this.visualStats.hairstyles=11;this.visualStats.neckShortening=.045;this.visualStats.lodTriangles=this.lodParts.map(a=>a.reduce((s,p)=>s+p.vertices/3,0));this.visualStats.crowdPaletteBytes=this.posePixels.byteLength;this.visualStats.crowdCapacity=128;this.visualStats.sharedInstancing=true;this.visualStats.skinning='dual-quaternion';this.visualStats.dualPaletteBytes=this.dualPixels.byteLength;
  }
  getHairParts(style,lod){
   const id=style+':'+lod;if(this.hairParts.has(id))return this.hairParts.get(id);
   const parts=D.HairGeometry.build(style,lod).map(p=>{const key='groom_'+style+'_'+lod+'_'+p.name,m=this.createSkinMesh(p.data);m.crowd=true;this.meshes[key]=m;this.dynamic[key]=[];this.static[key]=[];return{key,name:p.name,material:p.material,vertices:p.data.length/16,color:[.03,.02,.01]};});
   this.hairParts.set(id,parts);return parts;
  }
  updateDynamic(sim){
   if(this.motionScene!==sim){this.motionTracker.clear();this.motionScene=sim;}
   this.castCursor=1;this.castStats={actors:0,drivers:0,evicted:0,lod:[0,0,0],triangles:0,paletteRows:0,drawBatches:0};
   super.updateDynamic(sim);
   const g=this.gl,rows=Math.max(1,this.castCursor);g.activeTexture(g.TEXTURE3);g.bindTexture(g.TEXTURE_2D,this.crowdTexture);g.texSubImage2D(g.TEXTURE_2D,0,0,0,D.SkinRig.paletteWidth,rows,g.RGBA,g.FLOAT,this.posePixels.subarray(0,rows*D.SkinRig.paletteStride));this.castStats.paletteRows=rows;
   g.activeTexture(g.TEXTURE8);g.bindTexture(g.TEXTURE_2D,this.dualTexture);g.texSubImage2D(g.TEXTURE_2D,0,0,0,D.SkinRig.bones.length*2,rows,g.RGBA,g.FLOAT,this.dualPixels.subarray(0,rows*D.SkinRig.bones.length*8));
   g.activeTexture(g.TEXTURE7);g.bindTexture(g.TEXTURE_2D,this.appearanceTexture);g.texSubImage2D(g.TEXTURE_2D,0,0,0,2,rows,g.RGBA,g.FLOAT,this.appearancePixels.subarray(0,rows*8));
   this.castStats.drawBatches=Object.values(this.meshes).filter(m=>m.crowd&&m.dynamicCount>0).length;this.castStats.hairGeometries=this.hairParts.size;
  }
  chooseLOD(n,isPlayer,distance){
   if(isPlayer)return 0;const id=n.personId||n.id||'unknown',last=this.lodHistory.get(id)??1,near=this.quality==='eco'?9:16,far=this.quality==='eco'?26:43;
   let lod=last;if(last===0&&distance>near*1.2)lod=1;else if(last===1&&distance<near*.8)lod=0;else if(last===1&&distance>far*1.15)lod=2;else if(last===2&&distance<far*.85)lod=1;
   this.lodHistory.set(id,lod);if(this.lodHistory.size>160)this.lodHistory.delete(this.lodHistory.keys().next().value);return lod;
  }
  renderReactive(sim){
   if(!this.previewStudio)return super.renderReactive(sim);
   this.add(this.dynamic,'box',0,-.07,0,40,.10,40,[.040,.048,.051],45);
   this.add(this.dynamic,'box',0,4,-6,40,8,.2,[.023,.033,.040],45);
   this.add(this.dynamic,'box',0,-.013,0,1.0,.01,1.0,[.055,.067,.065],45);
  }
  renderPerson(n,isPlayer=false){
   if(!this.lodParts||this.heroFallback)return super.renderPerson(n,isPlayer);
   if(!isPlayer&&this.castCursor>=128)return super.renderPerson(n,false);
   const distance=D.distance(n,this.currentSim.player),lod=this.chooseLOD(n,isPlayer,distance),slot=isPlayer?0:this.castCursor++,time=this.currentTime||0;
   const rawActor=isPlayer?n:{...n,walk:n.walk??n.phase??0,moveSpeed:n.seated?0:n.moveSpeed??(n.panic>0?3.0:n.speed||0),sprintBlend:n.panic>0?.5:0};
   const actor=this.motionTracker.update(isPlayer?'player':n.personId||n.id||('ped:'+this.currentSim.peds.indexOf(n)),rawActor,time,!!this.previewStudio);
   const look=D.Appearance.actorLook(n,isPlayer,this.currentSim),A=D.Appearance;
   this.appearancePixels.set([look.build,look.face,look.hairStyle,look.neck||0],slot*8);
   this.appearancePixels.set([look.neckLength||0,look.hairVolume||0,look.browMatch?1:0,0],slot*8+4);
   const neckDrop=D.CharacterFit.drop(look.neckLength);
   const pose=D.SkinRig.pose({...actor,neckDrop},time);if(isPlayer){this.motionDebug={neckDrop,rootY:pose.rootY,feet:pose.feet,gripStyle:pose.gripStyle,motion:actor.motion,contacts:pose.handContacts||null};}
   this.posePixels.set(pose.matrices,slot*D.SkinRig.paletteStride);D.DualQuaternion.pack(pose.matrices,this.dualPixels,slot*D.SkinRig.bones.length*8);if(isPlayer)this.heroPalette.set(pose.matrices);
   this.castStats.actors++;this.castStats.lod[lod]++;if(n.seated&&!isPlayer)this.castStats.drivers++;if(n.evicted)this.castStats.evicted++;
   const variation=n.variant||0,proportion=1;
   for(const part of [...this.lodParts[lod],...this.getHairParts(look.hairStyle,lod)]){
    let color=part.color;
    const skin=isPlayer?A.skin[look.skin].rgb:(n.skin||A.skin[look.skin].rgb);
    if(part.name==='face')color=D.HumanMaterials.tint(skin);
    if(part.name==='skin')color=skin;
    if(part.name==='nails')color=skin.map((v,i)=>v*.95+[.030,.026,.022][i]);
    if(part.name==='lip')color=skin.map((v,i)=>v*[.80,.53,.52][i]);
    if(part.material===31)color=isPlayer?A.coats[look.coat].rgb:n.coat||A.coats[look.coat].rgb;
    if(part.material===32)color=!isPlayer&&n.police?[.025,.038,.068]:A.pants[look.pants].rgb;
    if(part.material===33)color=A.hair[look.browMatch?look.hair:1].rgb;
    if(part.material===46||part.material===47)color=A.hair[look.hair].rgb;
    if(part.material===41)color=A.eyes[look.eyes].rgb;
    this.add(this.dynamic,part.key,n.x,pose.rootY,n.z,pose.scale*proportion,pose.scale*proportion,pose.scale*proportion,color,part.material,0,n.yaw,variation*.111,200+slot);
    this.castStats.triangles+=part.vertices/3;
   }
   if(!n.seated)this.add(this.dynamic,'smoke',n.x,-.010,n.z,.68,.46,1,[.004,.006,.008],37,.48*Math.exp(-Math.max(0,n.y||0)*2),n.yaw,0,0,-Math.PI/2);
   if(n.police&&lod<2){const q=D.carPoint(n,-.10,.128),y=pose.rootY+1.27;this.add(this.dynamic,'body',q.x,y,q.z,.043,.067,.008,[.63,.64,.44],3,0,n.yaw);}
  }
  renderPlayer(sim){
   if(sim.access){this.renderPerson(sim.accessPlayerPose(),true);return;}
   const p=sim.player;if(p.car===null){this.renderPerson(p,true);return;}
   const c=sim.actor(),q=D.carPoint(c,-.38,-.20),hands=D.VehicleCabin.hands(c);
   this.renderPerson({...p,...q,y:-.29,yaw:c.yaw,seated:true,seatBlend:1,moveSpeed:0,crouch:0,handTargets:hands},true);
  }
  renderCar(c){super.renderCar(c);if(c.driver&&D.distance(c,this.currentSim.player)<90){const n=this.currentSim.driverPose(c);if(n)this.renderPerson(n,false);}}
  updateCamera(sim,dt,options={}){
   super.updateCamera(sim,dt,options);if(options.menu||options.photo||options.look||this.reducedMotion)return;
   this.accessCameraWeight=D.damp(this.accessCameraWeight||0,sim.access?1:0,5,dt);if(sim.access)this.accessCameraCar=sim.access.c;
   if(this.accessCameraWeight<.01||!this.accessCameraCar)return;const c=this.camera,v=this.accessCameraCar,a=sim.access?sim.accessPlayerPose():sim.player,w=this.accessCameraWeight;
   const target=[(a.x+v.x)*.5,1.05,(a.z+v.z)*.5],distance=6.2,eye=[target[0]-Math.sin(c.yaw)*distance,2.8,target[2]-Math.cos(c.yaw)*distance];
   if(this.world.visible(target[0],target[2],eye[0],eye[2])&&!this.world.blocked(eye[0],eye[2],.3)){c.target=c.target.map((x,i)=>D.lerp(x,target[i],w*.12));c.eye=c.eye.map((x,i)=>D.lerp(x,eye[i],w*.12));}
  }
 }
 D.CastRenderer=CastRenderer;D.Renderer=CastRenderer;
})(DC);
