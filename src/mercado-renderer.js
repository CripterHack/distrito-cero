/* The two home-district assets share an embedded PBR atlas and immutable geometry. */
'use strict';
(function(D){
 function bytes(base64){return Uint8Array.from(atob(base64),c=>c.charCodeAt(0));}
 function unpack(level){
  const vertices=new DataView(bytes(level.points).buffer),indices=new DataView(bytes(level.indices).buffer);
  const count=indices.byteLength/2, out=new Float32Array(count*8);
  for(let i=0;i<count;i++){
   const j=indices.getUint16(i*2,true)*14, o=i*8;
   for(let k=0;k<3;k++){
    out[o+k]=vertices.getInt16(j+k*2,true)/1000;
    out[o+k+3]=vertices.getInt8(j+k+6)/127;
   }
   out[o+6]=vertices.getUint16(j+10,true)/65535;
   out[o+7]=vertices.getUint16(j+12,true)/65535;
  }
  return out;
 }
 // Shared atlas upload for embedded street assets. Each promise belongs to one GL generation.
 D.loadStreetAtlas=function(renderer,texture,source,unit,maxLevel){
  const g=renderer.gl,image=new Image();
  return new Promise(resolve=>{
   image.onload=()=>{
    if(!renderer.canRender()){resolve(false);return;}
    const previous=g.getParameter(g.ACTIVE_TEXTURE),flip=g.getParameter(g.UNPACK_FLIP_Y_WEBGL);
    g.activeTexture(g.TEXTURE0+unit);
    const previousTexture=g.getParameter(g.TEXTURE_BINDING_2D);
    try{
     g.bindTexture(g.TEXTURE_2D,texture);
     g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,true);
     g.texImage2D(g.TEXTURE_2D,0,g.RGBA,g.RGBA,g.UNSIGNED_BYTE,image);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAX_LEVEL,maxLevel);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.LINEAR_MIPMAP_LINEAR);
     g.generateMipmap(g.TEXTURE_2D);
     resolve(renderer.canRender());
    }catch{resolve(false);}
    finally{g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,flip);g.bindTexture(g.TEXTURE_2D,previousTexture);g.activeTexture(previous);}
   };
   image.onerror=()=>resolve(false);
   image.src=source;
  });
 };
 class MercadoRenderer extends D.Renderer{
  constructor(...args){
   super(...args);
   for(const key of ['taller','marquesina']){
    for(const [lod,level] of D.MercadoModels[key].levels.entries()){
     const name=key+lod,mesh=this.createMesh(unpack(level));
     mesh.chunks=[];mesh.dynamicBuffer=this.gl.createBuffer();
     this.meshes[name]=mesh;this.static[name]=[];this.dynamic[name]=[];
    }
   }
   this.mercadoTexture=this.gl.createTexture();
   this.mercadoReady=D.loadStreetAtlas(this,this.mercadoTexture,D.MercadoModels.atlas,10,3)
    .then(ready=>(this.mercadoLoaded=ready));
  }
  sceneUniforms(...args){
   super.sceneUniforms(...args);
   const p=args[4]||this.sceneProgram,g=this.gl;
   g.activeTexture(g.TEXTURE10);
   g.bindTexture(g.TEXTURE_2D,this.mercadoLoaded?this.mercadoTexture:this.white);
   g.uniform1i(this.uniform(p,'uMercadoAtlas'),10);
   g.uniform1i(this.uniform(p,'uMercadoLoaded'),this.mercadoLoaded?1:0);
  }
  diffuserPower(){
   const t=D.clamp((.64-this.daylight)/.54,0,1);
   return t*t*(3-2*t);
  }
  sceneLights(sim){
   const lights=super.sceneLights(sim),downlight=this.diffuserPower();
   if(!this.previewStudio && downlight>0){
    for(const stop of this.world.shelters)lights.push({...stop.diffuser,downlight});
   }
   return lights;
  }
  renderReactive(sim){
   super.renderReactive(sim);
   if(this.previewStudio||!this.world.workshop)return;
   const eye=this.camera.eye;
   const draw=(key,site,material,reach,near)=>{
    const d=Math.hypot(site.x-eye[0],site.z-eye[2]);
    if(d>reach)return;
    const lod=d<near*(this.quality==='eco'?.66:1)?0:1;
    this.add(this.dynamic,key+lod,site.x,.145,site.z,1,1,1,[.45,.43,.38],material,0,site.yaw);
   };
   draw('taller',this.world.workshop,50,950,72);
   for(const site of this.world.shelters){
    draw('marquesina',site,51,330,40);
    const l=site.diffuser;
    if(Math.hypot(l.x-eye[0],l.z-eye[2])<90){
     this.add(this.dynamic,'box',l.x,l.y+.023,l.z,.78,.046,.15,[.59,.55,.46],0,5*this.diffuserPower(),site.yaw);
    }
   }
  }
 }
 D.Renderer=MercadoRenderer;
})(DC);
