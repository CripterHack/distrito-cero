/* Visual upgrade layer. Does not own physics, inputs, mission or save state. */
'use strict';
(function(D){
 const Base=D.Renderer;
 function decode(part){
  const raw=atob(part.data),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);
  if(bytes.length!==part.vertices*24)throw new Error('Corrupt hero asset size');
  const view=new DataView(bytes.buffer),out=new Float32Array(part.vertices*16);
  for(let i=0;i<part.vertices;i++){
   const b=i*24,o=i*16;for(let j=0;j<3;j++)out[o+j]=view.getInt16(b+j*2,true)/10000;
   let length=0;for(let j=0;j<3;j++){const v=view.getInt16(b+6+j*2,true)/32767;out[o+3+j]=v;length+=v*v;}
   length=Math.sqrt(length);for(let j=0;j<3;j++)out[o+3+j]/=length;
   for(let j=0;j<2;j++)out[o+6+j]=view.getUint16(b+12+j*2,true)/65535;
   for(let j=0;j<4;j++){out[o+8+j]=view.getUint8(b+16+j);out[o+12+j]=view.getUint8(b+20+j)/255;}
  }
  D.SkinRig.validate(out);return out;
 }
 class RealismRenderer extends Base{
  constructor(...args){
   super(...args);this.heroParts=[];this.heroPalette=D.SkinRig.rest();this.visuals=D.VisualGeometry.build();
   const map={coupe:'asset_BODY_shell',glassFront:'asset_GLASS_windshield',glassRear:'asset_GLASS_rear',glassLeft:'asset_GLASS_side_L',glassRight:'asset_GLASS_side_R'};
   for(const[name,data]of Object.entries(this.visuals)){
    const key=map[name]||name;if(this.meshes[key])this.deleteMesh(this.meshes[key]);
    const m=this.createMesh(data);m.chunks=[];m.dynamicBuffer=this.gl.createBuffer();this.meshes[key]=m;this.static[key]=[];this.dynamic[key]=[];
   }
   for(const part of D.HeroAsset.parts){
    const data=decode(part),key='hero_'+part.name,m=this.createSkinMesh(data);
    this.meshes[key]=m;this.static[key]=[];this.dynamic[key]=[];this.heroParts.push({...part,data:undefined,key});
   }
   this.humanTextures={};this.humanTextureStatus={loaded:0,failed:0,bytes:0};this.humanReady=this.loadHumanTextures();
   this.visualStats={heroTriangles:this.heroParts.reduce((s,p)=>s+p.vertices/3,0),heroParts:this.heroParts.length,bones:D.SkinRig.bones.length,nativeRecipe:true};
  }
  loadHumanTextures(){
   const g=this.gl;
   return Promise.all(['albedo','normal','roughness'].map((key,i)=>new Promise(resolve=>{
    const source=D.HumanMaterials[key],texture=g.createTexture();this.humanTextures[key]=texture;
    const fallback=key==='normal'?[128,128,255,255]:key==='roughness'?[170,170,170,255]:[184,139,114,255];
    const active=g.getParameter(g.ACTIVE_TEXTURE);g.activeTexture(g.TEXTURE4+i);g.bindTexture(g.TEXTURE_2D,texture);
    g.texImage2D(g.TEXTURE_2D,0,g.RGBA,1,1,0,g.RGBA,g.UNSIGNED_BYTE,new Uint8Array(fallback));
    g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.LINEAR);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MAG_FILTER,g.LINEAR);
    g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_S,g.REPEAT);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_WRAP_T,g.CLAMP_TO_EDGE);g.activeTexture(active);
    const image=new Image();image.onload=()=>{
     const previous=g.getParameter(g.ACTIVE_TEXTURE),flip=g.getParameter(g.UNPACK_FLIP_Y_WEBGL);g.activeTexture(g.TEXTURE4+i);g.bindTexture(g.TEXTURE_2D,texture);g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,true);
     g.texImage2D(g.TEXTURE_2D,0,g.RGBA,g.RGBA,g.UNSIGNED_BYTE,image);g.generateMipmap(g.TEXTURE_2D);g.texParameteri(g.TEXTURE_2D,g.TEXTURE_MIN_FILTER,g.LINEAR_MIPMAP_LINEAR);
     g.pixelStorei(g.UNPACK_FLIP_Y_WEBGL,flip);g.activeTexture(previous);this.humanTextureStatus.loaded++;this.humanTextureStatus.bytes+=image.width*image.height*4*4/3;resolve(true);
    };
    image.onerror=()=>{this.humanTextureStatus.failed++;console.warn('Embedded human map could not be decoded:',key);resolve(false);};image.src=source.uri;
   })));
  }
  sceneUniforms(...args){
   super.sceneUniforms(...args);const g=this.gl,p=this.sceneProgram;
   for(const [key,name,unit]of [['albedo','uSkinAlbedo',4],['normal','uSkinNormal',5],['roughness','uSkinRoughness',6]]){
    g.activeTexture(g.TEXTURE0+unit);g.bindTexture(g.TEXTURE_2D,this.humanTextures[key]);g.uniform1i(this.uniform(p,name),unit);
   }
  }
  deleteMesh(m){const g=this.gl;g.deleteVertexArray(m.vao);g.deleteBuffer(m.vbo);if(m.dynamicBuffer)g.deleteBuffer(m.dynamicBuffer);for(const c of m.chunks||[])g.deleteBuffer(c.buffer);}
  createSkinMesh(data){
   const g=this.gl,vao=g.createVertexArray(),vbo=g.createBuffer();g.bindVertexArray(vao);g.bindBuffer(g.ARRAY_BUFFER,vbo);g.bufferData(g.ARRAY_BUFFER,data,g.STATIC_DRAW);
   for(const [loc,size,offset] of [[0,3,0],[1,3,12],[2,2,24],[7,4,32],[8,4,48]]){g.enableVertexAttribArray(loc);g.vertexAttribPointer(loc,size,g.FLOAT,false,64,offset);g.vertexAttribDivisor(loc,0);}
   return{vao,vbo,count:data.length/16,skinned:true,palette:this.heroPalette,chunks:[],dynamicBuffer:g.createBuffer(),dynamicCount:0};
  }
  renderPerson(n,isPlayer=false){
   if(!isPlayer||!this.heroParts?.length||this.heroFallback)return super.renderPerson(n,isPlayer);
   const q=D.SkinRig.pose(n,this.currentTime||0);this.heroPalette.set(q.matrices);
   this.add(this.dynamic,'smoke',n.x,-.010,n.z,.75,.53,1,[.004,.006,.008],37,.50*Math.exp(-Math.max(0,n.y||0)*2),n.yaw,0,0,-Math.PI/2);
   for(const part of this.heroParts)this.add(this.dynamic,part.key,n.x,q.rootY,n.z,q.scale,q.scale,q.scale,part.color,part.material,0,n.yaw,0,0);
  }
  renderTreeDetail(p,put){
   const low=D.distance(p,this.currentSim.player)>(this.quality==='eco'?40:78);
   put(low?'treeWoodLow':'treeWood',0,0,0,1,1,1,[.16,.115,.072],35);
   // Canopy remains below original contact envelope. Wind does not alter gameplay collision.
   put(low?'treeLeavesLow':'treeLeaves',0,0,0,.91,.93,.91,[.070,.155,.071],36);
  }
 }
 D.Realism={decode};D.Renderer=RealismRenderer;
})(DC);
