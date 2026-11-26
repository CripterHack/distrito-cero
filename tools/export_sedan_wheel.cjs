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

const gltf={asset:{version:'2.0',generator:'Distrito Cero · mallas nativas del sedán'},scene:0,
 scenes:[{nodes:[0]}],nodes:[{name:'Steering',children:[1]},{name:'Rolling axle',children:[]}],
 meshes:[],materials:[],accessors:[],bufferViews:[],buffers:[]};
const chunks=[];let byteOffset=0;
for(const part of parts){
 if(part.yaw!==0||part.roll!==0)throw Error('Expected an unsteered, level right wheel');
 const raw=meshes[part.key],count=raw.length/8,data=Buffer.alloc(raw.length*4);
 const min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
 for(let i=0;i<raw.length;i++){
  data.writeFloatLE(raw[i],i*4);
  const component=i%8;
  if(component<3){
   min[component]=Math.min(min[component],Math.fround(raw[i]));
   max[component]=Math.max(max[component],Math.fround(raw[i]));
  }
 }
 const bufferView=gltf.bufferViews.length;
 gltf.bufferViews.push({buffer:0,byteOffset,byteLength:data.length,byteStride:32,target:34962});
 byteOffset+=data.length;chunks.push(data);
 const attributes={};
 for(const [name,offset,type] of [['POSITION',0,'VEC3'],['NORMAL',12,'VEC3'],['TEXCOORD_0',24,'VEC2']]){
  attributes[name]=gltf.accessors.length;
  const accessor={bufferView,byteOffset:offset,componentType:5126,count,type};
  if(name==='POSITION')Object.assign(accessor,{min,max});
  gltf.accessors.push(accessor);
 }
 const material=gltf.materials.length;
 gltf.materials.push({name:part.key,pbrMetallicRoughness:{baseColorFactor:[...part.color,1],
  metallicFactor:part.material===3?.82:0,roughnessFactor:part.material===3?.36:.84}});
 const mesh=gltf.meshes.length;
 gltf.meshes.push({name:part.key,primitives:[{attributes,material}]});
 const parent=part.key==='wheelCaliper'?0:1;
 gltf.nodes[parent].children.push(gltf.nodes.length);
 gltf.nodes.push({name:part.key,mesh,scale:part.scale,translation:part.at.map((v,i)=>v-tire.at[i]),
  rotation:[Math.sin(part.pitch*.5),0,0,Math.cos(part.pitch*.5)]});
}
gltf.buffers.push({byteLength:byteOffset});
const json=Buffer.from(JSON.stringify(gltf)),padding=Buffer.alloc((4-json.length%4)%4,0x20);
const jsonSize=json.length+padding.length,header=Buffer.alloc(20),binHeader=Buffer.alloc(8);
header.write('glTF');header.writeUInt32LE(2,4);header.writeUInt32LE(28+jsonSize+byteOffset,8);
header.writeUInt32LE(jsonSize,12);header.write('JSON',16);
binHeader.writeUInt32LE(byteOffset);binHeader.write('BIN\x00',4);
fs.writeFileSync(out,Buffer.concat([header,json,padding,binHeader,...chunks]));
console.log(out);
