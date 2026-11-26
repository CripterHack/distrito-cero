/* Draw the authored market resident in the existing crowd passes and palette texture. */
'use strict';
(function(D){
 const model='mercado-higgsfield',material=52,atlasUnit=11;
 const wrap=value=>value-Math.floor(value);
 class MarketPedRenderer extends D.Renderer{
  constructor(...args){
   super(...args);
   this.marketPedMotion=new WeakMap();
   for(const [lod] of D.MarketPedAsset.levels.entries()){
    const key='marketPed'+lod,mesh=this.createSkinMesh(D.MarketPedAsset.decodeLevel(lod));
    mesh.crowd=true;mesh.linearCrowd=true;
    this.meshes[key]=mesh;this.static[key]=[];this.dynamic[key]=[];
   }
   this.marketPedTexture=this.gl.createTexture();
   this.marketPedReady=D.loadStreetAtlas(this,this.marketPedTexture,D.MarketPedAsset.atlas,atlasUnit,2)
    .then(ready=>(this.marketPedLoaded=ready));
  }
  sceneUniforms(...args){
   super.sceneUniforms(...args);
   const g=this.gl,program=args[4]||this.sceneProgram;
   if(program===this.basicSceneProgram)return;
   g.activeTexture(g.TEXTURE0+atlasUnit);
   g.bindTexture(g.TEXTURE_2D,this.marketPedLoaded?this.marketPedTexture:this.white);
   g.uniform1i(this.uniform(program,'uMarketPedAtlas'),atlasUnit);
  }
  updateDynamic(sim){
   super.updateDynamic(sim);
   this.castStats.marketPed=this.meshes.marketPed0.dynamicCount+this.meshes.marketPed1.dynamicCount;
  }
  renderPerson(n,isPlayer=false){
   if(isPlayer||n.visualModel!==model||n.seated||this.previewStudio||this.heroFallback||
      !this.marketPedLoaded||this.castCursor>=128)return super.renderPerson(n,isPlayer);

   const eye=this.camera.eye,y=(n.groundY||0)+(n.y||0);
   const distance=Math.hypot(n.x-eye[0],y+.9-eye[1],n.z-eye[2]);
   const lod=Math.min(1,this.chooseLOD(n,false,distance)),key='marketPed'+lod;
   const t=this.currentTime,stunned=n.combatStunUntil>t,speed=stunned?0:(n.moveSpeed??n.speed??0);
   const walking=D.clamp(speed/.65,0,1),running=D.clamp((speed-1.50)/(3.78-1.50),0,1);
   const tilt=stunned?.36:n.combatHitUntil>t?-.17*Math.sin(Math.PI*D.clamp((n.combatHitUntil-t)/.45,0,1)):0;
   const last=this.marketPedMotion.get(n),dt=last?t-last.time:Infinity;
   // Fade between clips in game time; a paused or repeated draw keeps the pose fixed.
   const blend=dt<0?1:1-Math.exp(-12*dt);
   const step=n.sidewalkRoute?.brake,brake=step&&D.MarketPedAsset.clips[step.clip]?step:null;
   const finishedBrake=last?.braking && !brake;
   const walk=finishedBrake && !speed?0:D.lerp(last?.walk??walking,walking,blend),run=D.lerp(last?.run??running,running,blend);
   const reaction=D.lerp(last?.reaction??tilt,tilt,blend);
   const turn=D.MarketPedAsset.clips.Giro && n.sidewalkRoute?.turn;
   // The turn ends on Reposo's first key in the new facing direction.
   const idleStart=last&&dt>=0?((last.turning&&!turn||finishedBrake)?t:last.idleStart):0;
   this.marketPedMotion.set(n,{time:t,walk,run,reaction,idleStart,turning:!!turn,braking:!!brake});
   const slot=this.castCursor++,stride=D.SkinRig.paletteStride;
   const palette=this.posePixels.subarray(slot*stride,(slot+1)*stride);
   const walkPhase=wrap((n.phase||0)/(2*Math.PI)),idlePhase=wrap((t-idleStart)/D.MarketPedAsset.clips.Reposo.duration);
   if(brake){
    D.MarketPedAsset.writePalette(palette,walkPhase,idlePhase,walk,run,brake.progress,1,brake.clip);
   }else if(turn){
    // Preserve the incoming pose briefly when panic reverses a moving actor.
    const entry=D.clamp(turn.progress/.13,0,1);
    D.MarketPedAsset.writePalette(palette,walkPhase,idlePhase,walk,run,turn.progress,entry*entry*(3-2*entry));
   }else D.MarketPedAsset.writePalette(palette,walkPhase,idlePhase,walk,run);
   this.add(this.dynamic,key,brake?brake.startX:n.x,y,brake?brake.startZ:n.z,1,1,1,[1,1,1],material,0,turn?turn.startYaw:n.yaw,reaction,200+slot);
   this.add(this.dynamic,'smoke',n.x,(n.groundY||0)+.003,n.z,.68,.46,1,[.004,.006,.008],37,
            .48*Math.exp(-Math.max(0,n.y||0)*2),n.yaw,0,0,-Math.PI/2);
   this.castStats.actors++;this.castStats.lod[lod]++;this.castStats.triangles+=this.meshes[key].count/3;
  }
 }
 D.Renderer=MarketPedRenderer;
})(DC);
