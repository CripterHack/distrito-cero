'use strict';
const {test}=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
class BaseRenderer { renderCar(){ this.farDraws++; } }
const context=vm.createContext({DC:{Renderer:BaseRenderer,Simulation:class {}}});
for(const name of ['core','dynamics','visual-geometry','reactive-renderer']) {
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../src',name+'.js'),'utf8'),context);
}
const {DC}=context;
const geometry=DC.VisualGeometry.build();
function draw({spin=0,steer=0,pitch=0,roll=0,yaw=0,distance=0,quality='balanced'}={}){
 const car={id:1,x:18,z:-12,yaw,wheel:spin,steerAngle:steer,color:[.1,.2,.3],suspension:{pitch,roll,kick:0}};
 const parts=[];
 const renderer={assetParts:[{name:'BODY_shell',key:'asset_BODY_shell'}],meshes:geometry,currentTime:0,dynamic:{},
  quality,farDraws:0,currentSim:{player:{x:car.x+distance,z:car.z}},add(list,key,x,y,z,w,h,d,col,mat,em,yaw,seed,detail,pitch,roll){
   parts.push({key,center:[x,y,z],yaw,pitch,roll,scale:[w,h,d]});
  }};
 DC.Renderer.prototype.renderCar.call(renderer,car);
 return {parts,farDraws:renderer.farDraws,car};
}
function rotateX([x,y,z],a){return [x,y*Math.cos(a)-z*Math.sin(a),y*Math.sin(a)+z*Math.cos(a)];}
function rotateY([x,y,z],a){return [x*Math.cos(a)+z*Math.sin(a),y,-x*Math.sin(a)+z*Math.cos(a)];}
function rotateZ([x,y,z],a){return [x*Math.cos(a)-y*Math.sin(a),x*Math.sin(a)+y*Math.cos(a),z];}
const transform=(p,{yaw,roll,pitch})=>rotateY(rotateZ(rotateX(p,pitch),roll),yaw);
const add=(a,b)=>a.map((v,i)=>v+b[i]);
function close(actual,expected,label){
 assert.ok(Math.hypot(...actual.map((v,i)=>v-expected[i]))<1e-9,label+': '+actual+' vs '+expected);
}
test('all four rim centers remain mounted on their steered tire axes',()=>{
 for(const steer of [-.56,0,.48]) for(const spin of [-.73,1.15]) {
  const pose={steer,spin,yaw:.83,pitch:-.13,roll:.11}, {parts,car}=draw(pose);
  for(const [i,side] of [-1,1].entries())for(const [j,z] of [-1.39,1.36].entries()){
   const ordinal=i*2+j, tire=parts.filter(p=>p.key==='tire')[ordinal],rim=parts.filter(p=>p.key==='rim')[ordinal];
   const pivot=add([car.x,.6,car.z],transform([side*.92,.365-.6,z],pose));
   const axis=transform(rotateY([side,0,0],z>0?steer:0),pose);
   close(tire.center,pivot,'tire pivot');
   close(rim.center,add(pivot,axis.map(x=>x*.132)),'rim offset along rendered axle');
  }
 }
});
test('alloy and disc roll about the tire pivot while the caliper follows only steering and suspension',()=>{
 for(const steer of [-.57,.55])for(const spin of [-1.23,0,1.11,5.8]) {
  const pose={steer,spin,yaw:-1.24,pitch:.12,roll:-.09},{parts}=draw(pose);
  for(const [i,side] of [-1,1].entries())for(const [j,z] of [-1.39,1.36].entries()){
   const ordinal=i*2+j, tire=parts.filter(p=>p.key==='tire')[ordinal];
   for(const key of ['wheelAlloy','wheelBrake','wheelCaliper']){
    const part=parts.filter(p=>p.key===key)[ordinal];
    assert.ok(part,key);close(part.center,tire.center,key+' pivot');
    for(const basis of [[1,0,0],[0,1,0],[0,0,1]]){
     const theta=key==='wheelCaliper'?-side*1.12:side*spin;
     const local=rotateY(rotateX(basis,theta),(z>0?steer:0)+(side<0?Math.PI:0));
     close(transform(basis,part),transform(local,pose),key+' world basis');
    }
   }
  }
 }
});
test('disc and caliper detail follow distance and quality without dropping the mid-distance alloy silhouette',()=>{
 for(const [quality,cutoff] of [['eco',16],['balanced',26],['high',26]]){
  const keys=distance=>draw({distance,quality}).parts.map(p=>p.key);
  const near=keys(cutoff-.01),mid=keys(cutoff);
  for(const key of ['wheelAlloy','tire','rim']){
   assert.equal(near.filter(k=>k===key).length,4);
   assert.equal(mid.filter(k=>k===key).length,4);
  }
  for(const key of ['wheelBrake','wheelCaliper']){
   assert.equal(near.filter(k=>k===key).length,4);assert.ok(!mid.includes(key));
  }
 }
 const far=draw({distance:66});assert.equal(far.farDraws,1);assert.equal(far.parts.length,0);
});
test('wheel hardware is metric, finite and budgeted per visible wheel',()=>{
 let triangles=0;
 for(const key of ['wheelAlloy','wheelBrake','wheelCaliper']){
  const mesh=geometry[key];assert.ok(mesh,key);triangles+=mesh.length/24;
  for(let i=0;i<mesh.length;i+=8){
   const [x,y,z,nx,ny,nz]=mesh.slice(i,i+6);
   assert.ok(x>0 && x<.17 && Math.hypot(y,z)<.25,key+' within wheel envelope');
   assert.ok(Math.abs(Math.hypot(nx,ny,nz)-1)<1e-5,key+' finite unit normal');
  }
 }
 assert.ok(triangles<1200,'shared wheel detail budget');
});
