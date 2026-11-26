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
   this.mercadoReady=this.loadMercadoAtlas();
  }
  loadMercadoAtlas(){
   const g=this.gl, image=new Image();
   return new Promise(resolve=>{
    image.onload=()=>{
     if(!this.canRender()){resolve(false);return;}
     const previous=g.getParameter(g.ACTIVE_TEXTURE),flip=g.getParameter(g.UNPACK_FLIP_Y_WEBGL);
     g.activeTexture(g.TEXTURE10);g.bindTexture(g.TEXTURE_2D,this.mercadoTexture);
     g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,true);
     g.texImage2D(g.TEXTURE_2D,0,g.RGBA,g.RGBA,g.UNSIGNED_BYTE,image);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.CLAMP_TO_EDGE);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAX_LEVEL,3);
     g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.LINEAR_MIPMAP_LINEAR);
     g.generateMipmap(g.TEXTURE_2D);
     g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,flip);g.activeTexture(previous);
     this.mercadoLoaded=true;resolve(true);
    };
    image.onerror=()=>resolve(false);
    image.src=D.MercadoModels.atlas;
   });
  }
  sceneUniforms(...args){
   super.sceneUniforms(...args);
   const p=args[4]||this.sceneProgram,g=this.gl;
   g.activeTexture(g.TEXTURE10);
   g.bindTexture(g.TEXTURE_2D,this.mercadoLoaded?this.mercadoTexture:this.white);
   g.uniform1i(this.uniform(p,'uMercadoAtlas'),10);
   g.uniform1i(this.uniform(p,'uMercadoLoaded'),this.mercadoLoaded?1:0);
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
   for(const site of this.world.shelters)draw('marquesina',site,51,330,40);
  }
 }
 D.Renderer=MercadoRenderer;
})(DC);
