'use strict';
// Convert one captured Mercado shop. Vertices, scales, yaw and native colours are in metres/Y-up.
const fs=require('node:fs');
const {buildInstanceDocument}=require('./vehicle_glb.cjs');
const {encodeGlb}=require('./export_human_tangents.cjs');

function exportShop(native, output){
 const {shop,parts:{box,smoke,near}}=native;
 if(box.length!==26 || smoke.length!==2 || near.length!==22 || box[0][7]!==1 ||
    box[4][7]!==53 || box[19][7]!==20 || near[3][4]<5 || near[3][11]<=0)
  throw Error('The selected La Esquina shop no longer matches the captured facade');
 const base=box[4][1]-box[4][5]/2;
 const article=(title,n)=>Array.from({length:n},(_,i)=>title+' '+(i+1));
 const panels=['Fondo de exposición','Antepecho frontal','Antepecho lateral',...article('Montante frontal',4),
  ...article('Montante lateral',2),'Travesaño frontal','Travesaño lateral','Visera frontal','Visera lateral',
  'Friso frontal','Friso lateral','Rótulo','Balda frontal inferior','Balda lateral inferior','Balda frontal superior',
  'Balda lateral superior','Hoja de puerta','Umbral'];
 const details=['Tirador','Soporte bajo del tirador','Soporte alto del tirador','Tira de luz'];
 for(let bay=1;bay<=3;bay++)details.push('Bandeja '+bay,...article('Producto frontal '+bay+'.',4));
 details.push(...article('Producto lateral',3));
 const nodes=[{name:'La Esquina · Mercado',children:[1,2,3],extras:{worldSeed:1337,cell:[1,2],up:'+Y',
  worldOrigin:[shop.x,base,shop.z],buildingCenter:[shop.b.x,shop.b.z],htmlSha256:native.sha256,
  version:native.version,source:'Distrito Cero · WebGL2 · buildCornerShop'}}];
 for(const name of ['Fachada','Vitrinas','Exposición de cerca'])nodes.push({name,children:[]});
 const parts=[],geometry={...native.meshes};
 function add(row,key,name,parent){
  if(row[12]!==0 || row[13]!==0)throw Error('Expected level storefront parts');
  parts.push({name,key,parent,translation:[row[0]-shop.x,row[1]-base,row[2]-shop.z],scale:row.slice(4,7),
   rotation:[0,Math.sin(row[3]/2),0,Math.cos(row[3]/2)],material:row[7],color:row.slice(8,11),
   em:row[7]===53?0:row[11]});
 }
 // The first four box rows form the tower, its plinth, and the two solid building wings.
 // The remaining rows belong to the removable corner module.
 const cube=Buffer.from(geometry.box,'base64'),front=[],casing=[];
 for(let i=0;i<cube.length;i+=32){
  const vertex=Buffer.from(cube.subarray(i,i+32));
  if(vertex.readFloatLE(20)>.5){vertex.writeFloatLE(1-vertex.readFloatLE(28),28);front.push(vertex);}
  else casing.push(vertex);
 }
 if(front.length!==6||casing.length!==30)throw Error('Expected one front face of the native sign');
 geometry.lettering=Buffer.concat(front).toString('base64');
 geometry.casing=Buffer.concat(casing).toString('base64');
 box.slice(4).forEach((row,i)=>{
  if(row[7]===20){add(row,'lettering','Rótulo · cara impresa',1);add(row,'casing','Rótulo · carcasa',1);}
  else add(row,'box',panels[i],1);
 });
 smoke.forEach((row,i)=>add(row,'smoke',i===0?'Cristal frontal':'Cristal lateral',2));
 near.forEach((row,i)=>add(row,'box',details[i],3));

 // The common exporter preserves the flat-shaded interleaved production geometry.
 const {document:doc,binary}=buildInstanceDocument(geometry,parts,nodes,'Distrito Cero · exportación del escaparate nativo');
 parts.forEach((part,i)=>{
  const mesh=doc.meshes[doc.nodes[i+4].mesh], mat=doc.materials[mesh.primitives[0].material];
  const pbr=mat.pbrMetallicRoughness, painted=part.material===3;
  mat.name=part.em ? 'Tira cálida' : part.key==='smoke' ? 'Cristal tintado' : part.key==='lettering' ? 'Rótulo impreso' : part.key==='casing' ? 'Caja del rótulo' :
   (painted?'Metal':part.material===53?'Exposición':'Fachada')+' · '+part.color.map(v=>v.toFixed(2)).join(' / ');
  pbr.metallicFactor=painted?.32:0; pbr.roughnessFactor=painted?.28:.66;
  if(part.material===6){
   pbr.baseColorFactor=[.021+.1*part.color[0],.037+.1*part.color[1],.046+.1*part.color[2],.18];
   pbr.roughnessFactor=.16;pbr.metallicFactor=.06;
  }
  if(part.key==='lettering'){
   pbr.baseColorTexture={index:0};pbr.roughnessFactor=.3;mat.emissiveTexture={index:0};mat.emissiveFactor=[1,1,1];
  }else if(part.key==='casing')pbr.baseColorFactor=[.025,.035,.039,1];
 });
 const image=Buffer.from(native.sign,'base64'),view=doc.bufferViews.length;
 doc.bufferViews.push({buffer:0,byteOffset:binary.length,byteLength:image.length});
 doc.images=[{name:'La Esquina · atlas del juego',bufferView:view,mimeType:'image/png'}];
 doc.textures=[{source:0}];
 doc.buffers[0].byteLength=binary.length+image.length;
 fs.writeFileSync(output,encodeGlb(doc,Buffer.concat([binary,image])));
}

if(require.main===module){
 const [source,output]=process.argv.slice(2);
 exportShop(JSON.parse(fs.readFileSync(source)),output);
}
