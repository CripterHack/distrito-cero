'use strict';
const fs=require('node:fs');
const {encodeGlb}=require('./export_human_tangents.cjs');
function buildInstanceDocument(meshes,parts,nodes,generator){
 const gltf={asset:{version:'2.0',generator},scene:0,
  scenes:[{nodes:[0]}],nodes,
  meshes:[],materials:[],accessors:[],bufferViews:[],buffers:[]};
 const chunks=[];let byteOffset=0;
 const sharedGeometry=new Map(),sharedMeshes=new Map();
 function attributesFor(key){
  if(sharedGeometry.has(key))return sharedGeometry.get(key);
  const raw=meshes[key],data=typeof raw==='string'?Buffer.from(raw,'base64'):Buffer.alloc(raw.length*4);
  if(typeof raw!=='string')for(let i=0;i<raw.length;i++)data.writeFloatLE(raw[i],i*4);
  const count=data.length/32,min=[Infinity,Infinity,Infinity],max=[-Infinity,-Infinity,-Infinity];
  if(!Number.isInteger(count)||count%3)throw Error('Invalid native triangle list: '+key);
  for(let i=0;i<count;i++)for(let axis=0;axis<3;axis++){
   const value=data.readFloatLE(i*32+axis*4);
   min[axis]=Math.min(min[axis],value);max[axis]=Math.max(max[axis],value);
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
  sharedGeometry.set(key,attributes);
  return attributes;
 }
 for(const part of parts){
  const signature=JSON.stringify([part.key,part.material,part.color,part.em||0]);
  let mesh=sharedMeshes.get(signature);
  if(mesh===undefined){
   const attributes=attributesFor(part.key);
   const material=gltf.materials.length;
   const glass=part.material===6,paint=part.material===5,metal=part.material===3;
   const mat={name:part.key,pbrMetallicRoughness:{baseColorFactor:[...part.color,glass?.32:1],
    metallicFactor:metal?.82:paint?.60:glass?.08:0,roughnessFactor:metal?.36:paint?.27:glass?.14:.84}};
   if(glass)Object.assign(mat,{alphaMode:'BLEND',doubleSided:true});
   if(part.em>0)mat.emissiveFactor=part.color.map(v=>Math.min(1,v*part.em));
   gltf.materials.push(mat);mesh=gltf.meshes.length;
   gltf.meshes.push({name:part.key,primitives:[{attributes,material}]});
   sharedMeshes.set(signature,mesh);
  }
  gltf.nodes[part.parent].children.push(gltf.nodes.length);
  gltf.nodes.push({name:part.name||part.key,mesh,scale:part.scale,translation:part.translation,rotation:part.rotation});
 }
 gltf.buffers.push({byteLength:byteOffset});
 return {document:gltf,binary:Buffer.concat(chunks)};
}
function writeVehicleGlb(out,meshes,parts,nodes){
 const {document,binary}=buildInstanceDocument(meshes,parts,nodes,'Distrito Cero · mallas nativas del sedán');
 fs.writeFileSync(out,encodeGlb(document,binary));
}
module.exports={buildInstanceDocument,writeVehicleGlb};
if(require.main===module){
 const [source,out]=process.argv.slice(2),{geometry,parts,nodes}=JSON.parse(fs.readFileSync(source));
 writeVehicleGlb(out,geometry,parts,nodes);
}
