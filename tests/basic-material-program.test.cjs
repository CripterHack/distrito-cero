'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const ctx={DC:{SkinRig:{bones:Array(49)}},Float32Array,Map,Set,WeakMap,console};vm.createContext(ctx);
for(const file of ['core.js','graphics-resources.js','renderer.js'])vm.runInContext(fs.readFileSync('src/'+file,'utf8'),ctx);
const Base=ctx.DC.Renderer;
vm.runInContext(fs.readFileSync('src/realism-renderer.js','utf8'),ctx);const Realism=ctx.DC.Renderer;
vm.runInContext(fs.readFileSync('src/frontier-renderer.js','utf8'),ctx);const Frontier=ctx.DC.Renderer;
function packed(...materials){return materials.flatMap(material=>[0,0,0,0,1,1,1,material,.2,.3,.4,0,0,0,0,0]);}
function boundary(){
 const calls=[],sources=[],deleted=[],state={program:null,buffer:null,vao:null,uniforms:new Map()};let serial=0;
 const gl={CURRENT_PROGRAM:1,ARRAY_BUFFER:2,STATIC_DRAW:3,FLOAT:4,TRIANGLES:5,BLEND:6,SRC_ALPHA:7,ONE_MINUS_SRC_ALPHA:8,TEXTURE_2D:9,TEXTURE0:20,TEXTURE3:23,TEXTURE4:24,TEXTURE7:27,TEXTURE8:28,VERTEX_SHADER:30,FRAGMENT_SHADER:31,COMPILE_STATUS:32,LINK_STATUS:33,
  getParameter:()=>state.program,useProgram:p=>{state.program=p;},isContextLost:()=>false,
  bindBuffer:(target,b)=>{state.buffer=b;},bindVertexArray:v=>{state.vao=v;},bufferData:(target,data)=>calls.push({upload:Array.from(data),buffer:state.buffer}),
  getUniformLocation:(program,name)=>({program,name}),
  shaderSource:(shader,source)=>sources.push({shader,source}),compileShader:()=>{},getShaderParameter:()=>true,getShaderInfoLog:()=>'',attachShader:()=>{},linkProgram:()=>{},getProgramParameter:()=>true,getProgramInfoLog:()=>'',
  drawArraysInstanced:(mode,first,vertices,count)=>{calls.push({program:state.program,buffer:state.buffer,vao:state.vao,vertices,count,skinned:state.uniforms.get(state.program)?.uSkinned});if(state.failure)throw state.failure;}
 };
 for(const key of ['activeTexture','bindTexture','enable','disable','blendFunc','depthMask','enableVertexAttribArray','vertexAttribPointer','vertexAttribDivisor'])gl[key]=()=>{};
 for(const key of ['uniform1i','uniform1f','uniform3fv','uniform4fv','uniformMatrix4fv'])gl[key]=(location,...args)=>{
  assert.equal(state.program,location.program,'uniform must address the current program');
  if(!state.uniforms.has(location.program))state.uniforms.set(location.program,{});
  state.uniforms.get(location.program)[location.name]=args.at(-1);
 };
 for(const kind of ['Buffer','Texture','Framebuffer','Renderbuffer','VertexArray','Program','Shader']){
  gl['create'+kind]=()=>({kind,id:++serial});gl['delete'+kind]=value=>deleted.push(value);
 }
 return{gl,calls,state,sources,deleted};
}
function renderer(Type=Base){
 const b=boundary(),r=Object.create(Type.prototype),scene={name:'scene'},basic={name:'basic'};
 Object.assign(r,{gl:b.gl,sceneProgram:scene,basicSceneProgram:basic,uniforms:new Map(),renderOrigin:[0,0],currentTime:2,meshes:{},visibleChunk:()=>true});b.state.program=scene;
 return{...b,r,scene,basic};
}
function mesh(name,batches=[],dynamicCount=0,extra={}){return{vao:name,count:36,chunks:batches,dynamicBuffer:name+'-dynamic',dynamicCount,...extra};}
function batch(buffer,count,basicMaterials){return{buffer,count,basicMaterials,min:[0,0,0],max:[1,1,1]};}

test('basic classification accepts only complete immutable material-ID batches in 0..25',()=>{
 const r=Object.create(Base.prototype);assert.equal(typeof r.basicMaterialBatch,'function','basic batch proof is missing');
 for(let material=0;material<=25;material++)assert.equal(r.basicMaterialBatch(packed(material)),true);
 const input=new Float32Array(packed(0,6,9,25)),before=Array.from(input);assert.equal(r.basicMaterialBatch(input),true);assert.deepEqual(Array.from(input),before);
 for(const material of [-1,26,30,49,50,NaN,Infinity,2.5,'2',null])assert.equal(r.basicMaterialBatch(packed(0,material)),false,String(material));
 for(const input of [null,undefined,[],[0],packed(0).slice(1),{length:16}])assert.equal(r.basicMaterialBatch(input),false);
});
test('legacy static uploads record proof without reordering or dropping instance bytes',()=>{
 const {r,calls}=renderer(),data=packed(1,25),before=data.slice(),batches=r.chunkInstances(data);
 assert.equal(batches.length,1);assert.equal(batches[0].basicMaterials,true);assert.equal(batches[0].count,2);
 assert.deepEqual(calls[0].upload,Array.from(new Float32Array(data)));assert.deepEqual(data,before);
 assert.equal(r.chunkInstances(packed(0,40))[0].basicMaterials,false);
});
test('streamed sectors derive eligibility from uploaded material data rather than mesh names',()=>{
 const {r,calls}=renderer(Frontier);r.world={};r.meshes={box:{}};
 const chunk={x:0,z:0,cells:[{ix:0,iz:0,x:42,z:42,seed:.5,type:'woodland',roads:{n:0,s:0,e:0,w:0},buildings:[],pois:[]}]};
 const result=r.buildSector(chunk);assert.equal(result.box.basicMaterials,true);assert.equal(calls[0].upload.length,result.box.count*16);
 const add=r.add;r.add=function(list,name,...args){args[7]=40;return add.call(this,list,name,...args);};
 assert.equal(r.buildSector(chunk).box.basicMaterials,false);
});
test('draw traversal specializes proven static batches and preserves order, dynamic and skinned data',()=>{
 const {r,calls,state,scene,basic}=renderer();r.meshes={one:mesh('one',[batch('basic',2,true),batch('mixed',3,false)],4),skin:mesh('skin',[batch('skin',1,true)],0,{skinned:true,crowd:true}),glass:mesh('glass',[batch('glass',1,true)],0,{transparent:true})};
 r.drawMeshes(true);assert.deepEqual(calls.map(c=>[c.buffer,c.count,c.program,c.skinned]),[['basic',2,basic,0],['mixed',3,scene,0],['one-dynamic',4,scene,0],['skin',1,scene,2],['glass',1,basic,0]]);assert.equal(state.program,scene);
});
test('unknown metadata, hidden batches, empty batches and an absent specialized program fail safe',()=>{
 const {r,calls,scene}=renderer();r.meshes={one:mesh('one',[batch('missing',1),batch('truthy',1,'yes'),batch('empty',0,true),batch('hidden',1,true)])};r.visibleChunk=b=>b.buffer!=='hidden';
 r.drawMeshes();assert.deepEqual(calls.map(c=>[c.buffer,c.program]),[['missing',scene],['truthy',scene]]);
 calls.length=0;r.basicSceneProgram=null;r.meshes.one.chunks=[batch('basic',2,true)];r.drawMeshes();assert.equal(calls[0].program,scene);
});
test('shadow program remains unchanged even for proven static material batches',()=>{
 const {r,calls,state}=renderer(),shadow={name:'shadow'};state.program=shadow;r.meshes={one:mesh('one',[batch('basic',2,true)])};r.drawMeshes();assert.equal(calls[0].program,shadow);assert.equal(state.program,shadow);
});
test('draw failure propagates the same exception and restores the incoming program',()=>{
 const {r,state,scene}=renderer(),failure=new Error('driver draw failure');state.failure=failure;r.meshes={one:mesh('one',[batch('basic',2,true)])};
 assert.throws(()=>r.drawMeshes(),e=>e===failure);assert.equal(state.program,scene);
});
for(const Type of [Base,Realism])test(Type.name+' uploads reflection and texture uniforms to the explicitly targeted scene program',()=>{
 const {r,state,basic}=renderer(Type);Object.assign(r,{setFrustum:()=>{},lightVP:[],reflectVP:[],daylight:.6,sun:[0,1,0],lights:new Float32Array(48),quality:'balanced',shadowSize:1024,humanTextures:{albedo:{},normal:{},roughness:{}}});
 r.sceneUniforms([], [0,1,0],1,{time:5,player:{car:null},cars:[{x:0,z:0,yaw:0}]},basic);
 assert.equal(state.program,basic);assert.equal(state.uniforms.get(basic)?.uPass,1);assert.equal(state.uniforms.get(basic)?.uShadows,0);
 if(Type===Realism)assert.equal(state.uniforms.get(basic)?.uSkinNormal,5);
});
test('constructor owns one additional specialized fragment program and disposes it with its generation',()=>{
 const {gl,sources,deleted}=boundary();class Minimal extends Base{createSigns(){}createWhite(){}makeShadow(){}buildCity(){}resize(){}}
 const r=new Minimal({getContext:()=>gl},{},'balanced');assert.ok(r.basicSceneProgram,'additional program is absent');assert.notEqual(r.basicSceneProgram,r.sceneProgram);
 const specialized=sources.filter(row=>row.source.includes('#define DC_BASIC_MATERIALS'));assert.equal(specialized.length,1);assert.match(specialized[0].source,/bool detailMaterial\(int material\)/);
 const program=r.basicSceneProgram;r.dispose();r.dispose();assert.equal(deleted.filter(x=>x===program).length,1);
});

test('crowd metadata independently prevents specializing a deformed mesh',()=>{
 const {r,calls,scene}=renderer();r.meshes={crowd:mesh('crowd',[batch('crowd',1,true)],0,{crowd:true})};r.drawMeshes();assert.equal(calls[0].program,scene);assert.equal(calls[0].skinned,2);
});

test('program-specific inactive uniform locations are cached rather than queried on every frame',()=>{
 const {r,scene,basic}=renderer();let calls=0;r.gl.getUniformLocation=()=>{calls++;return null;};
 for(let i=0;i<3;i++)assert.equal(r.uniform(basic,'uSkinAlbedo'),null);
 assert.equal(calls,1);assert.equal(r.uniform(scene,'uSkinAlbedo'),null);assert.equal(calls,2);
});
test('uniform setup failure preserves exception identity and the incoming program',()=>{
 const {r,state,scene,basic}=renderer(),failure=new Error('uniform setup failure'),uniform=r.uniform;
 r.uniform=function(program,name){if(program===basic)throw failure;return uniform.call(this,program,name);};
 assert.throws(()=>r.drawMeshes(),e=>e===failure);assert.equal(state.program,scene);
});
