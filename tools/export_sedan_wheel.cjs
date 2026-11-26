'use strict';
// Export one production wheel in metres. Steering belongs to the root, rolling
// to its axle child. The caliper stays on the upright when the axle rotates.
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),out=process.argv[2]||path.join(root,'assets/dc-sedan-wheel.glb');
const context=vm.createContext({DC:{Renderer:class {},Simulation:class {}}});
for(const name of ['core','dynamics','visual-geometry','reactive-renderer']){
 vm.runInContext(fs.readFileSync(path.join(root,'src',name+'.js'),'utf8'),context);
}
const {DC}=context,meshes=DC.VisualGeometry.build(),instances=[];
const renderer={assetParts:[{name:'BODY_shell',key:'asset_BODY_shell'}],meshes,currentTime:0,dynamic:{},quality:'high',
 add(list,key,x,y,z,w,h,d,color,material,em,yaw,seed,detail,pitch,roll){
  instances.push({key,at:[x,y,z],scale:[w,h,d],color,material,yaw,pitch,roll});
 }};
DC.Renderer.prototype.renderCar.call(renderer,{id:0,x:0,z:0,yaw:0,wheel:0,steerAngle:0,color:[.1,.1,.1]});
const frontRight=instances.filter(p=>p.key==='tire'&&p.at[0]>0&&p.at[2]>0);
if(frontRight.length!==1)throw Error('Expected a single front-right tire');
const tire=frontRight[0],parts=instances.slice(instances.indexOf(tire),instances.indexOf(tire)+5);
if(parts.map(p=>p.key).join()!=='tire,rim,wheelBrake,wheelCaliper,wheelAlloy')throw Error('Recheck the wheel components against the native renderer');

const nodes=[{name:'Steering',children:[1]},{name:'Rolling axle',children:[]}];
for(const part of parts){
 if(part.yaw!==0||part.roll!==0)throw Error('Expected an unsteered, level right wheel');
 part.parent=part.key==='wheelCaliper'?0:1;
 part.translation=part.at.map((v,i)=>v-tire.at[i]);
 part.rotation=[Math.sin(part.pitch*.5),0,0,Math.cos(part.pitch*.5)];
}
require('./vehicle_glb.cjs').writeVehicleGlb(out,meshes,parts,nodes);
console.log(out);
