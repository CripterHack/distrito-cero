'use strict';
// Offline authoring gate. It locates collapsed charts; it never repairs an asset.
const fs=require('node:fs'),crypto=require('node:crypto');
const {decodeGlb,accessor}=require('../export_human_tangents.cjs');
const integer=n=>Number.isSafeInteger(n)&&n>=0;
function auditUv(doc,bytes){
 if(!Buffer.isBuffer(bytes)||doc.buffers?.length!==1||doc.buffers[0].uri||
    !integer(doc.buffers[0].byteLength)||doc.buffers[0].byteLength>bytes.length||!Array.isArray(doc.meshes))throw new Error('Unsupported embedded GLB layout');
 const charts=[],uvTriangles=new Set(),geometryTriangles=new Set();let skipped=0;
 const bounds=width=>({min:Array(width).fill(Infinity),max:Array(width).fill(-Infinity)});
 const include=(b,row)=>row.forEach((v,k)=>{b.min[k]=Math.min(b.min[k],v);b.max[k]=Math.max(b.max[k],v);});
 for(const [mi,mesh]of doc.meshes.entries())for(const [pi,p]of mesh.primitives.entries()){
  if(p.material!==undefined&&(!integer(p.material)||!doc.materials?.[p.material]))throw new Error('Invalid material index');
  const material=doc.materials?.[p.material];
  if(material?.extensions)throw new Error('Unsupported material extension');
  const roles={baseColorTexture:material?.pbrMetallicRoughness?.baseColorTexture,
   metallicRoughnessTexture:material?.pbrMetallicRoughness?.metallicRoughnessTexture,
   normalTexture:material?.normalTexture,occlusionTexture:material?.occlusionTexture,emissiveTexture:material?.emissiveTexture};
  const sets=new Map();
  for(const [role,texture]of Object.entries(roles))if(texture){
   if(texture.extensions||!integer(texture.index)||!integer(texture.texCoord??0))throw new Error('Unsupported texture coordinates or transform');
   if(!doc.textures?.[texture.index])throw new Error('Invalid texture index');
   const set=texture.texCoord??0;if(!sets.has(set))sets.set(set,[]);sets.get(set).push(role);
  }
  if(!sets.size){skipped++;continue;}
  if((p.mode??4)!==4||p.targets||p.extensions)throw new Error('Unsupported textured primitive, morph or compression');
  const position=accessor(doc,bytes,p.attributes?.POSITION);
  if(position.width!==3||position.a.componentType!==5126||position.a.normalized||position.a.extensions)throw new Error('Unsupported position layout');
  const count=position.a.count,indices=p.indices===undefined?null:accessor(doc,bytes,p.indices);
  if(indices&&(indices.width!==1||![5121,5123,5125].includes(indices.a.componentType)||indices.a.normalized||indices.a.extensions))throw new Error('Invalid index layout');
  const corners=indices?.a.count??count;
  if(corners%3)throw new Error('Invalid triangle count');
  const order=Array.from({length:corners},(_,i)=>indices?indices.value(i):i);
  if(order.some(i=>!integer(i)||i>=count))throw new Error('Invalid triangle index');
  const points=Array.from({length:count},(_,i)=>Array.from({length:3},(_,k)=>position.value(i,k)));
  if(points.some(v=>!v.every(Number.isFinite)))throw new Error('Nonfinite position');
  for(const [set,textureRoles]of [...sets].sort((a,b)=>a[0]-b[0])){
   const uv=accessor(doc,bytes,p.attributes?.['TEXCOORD_'+set]);
   if(uv.width!==2||uv.a.count!==count||uv.a.extensions||
      !(uv.a.componentType===5126&&!uv.a.normalized||[5121,5123].includes(uv.a.componentType)&&uv.a.normalized===true))throw new Error('Unsupported UV layout or mismatched count');
   const divisor=uv.a.componentType===5121?255:uv.a.componentType===5123?65535:1;
   const rawCoordinates=Array.from({length:count},(_,i)=>[uv.value(i,0),uv.value(i,1)]);
   const coordinates=rawCoordinates.map(row=>row.map(v=>v/divisor));
   if(coordinates.some(v=>!v.every(Number.isFinite)))throw new Error('Nonfinite UV coordinate');
   const bad=[],geometryBad=[],positionBounds=bounds(3),uvBounds=bounds(2);
   let constantUTriangles=0,constantVTriangles=0,boundaryVTriangles=0;
   for(let i=0;i<corners;i+=3){
    const ids=order.slice(i,i+3),[a,b,c]=ids.map(j=>coordinates[j]);
    const [pa,pb,pc]=ids.map(j=>points[j]),ab=pb.map((v,k)=>v-pa[k]),ac=pc.map((v,k)=>v-pa[k]);
    const cross=[ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0]];
    if(cross.every(v=>v===0)){geometryBad.push(i/3);geometryTriangles.add(mi+':'+pi+':'+i/3);}
    // A shared positive normalization cannot change collinearity. Compute on
    // the stored integers to avoid turning an exact zero into rounding noise.
    const [ra,rb,rc]=ids.map(j=>rawCoordinates[j]);
    const det=(rb[0]-ra[0])*(rc[1]-ra[1])-(rc[0]-ra[0])*(rb[1]-ra[1]);
    if(det!==0)continue;
    bad.push(i/3);uvTriangles.add(mi+':'+pi+':'+i/3);
    if(a[0]===b[0]&&a[0]===c[0])constantUTriangles++;
    if(a[1]===b[1]&&a[1]===c[1]){constantVTriangles++;if(a[1]===0||a[1]===1)boundaryVTriangles++;}
    for(const id of ids){include(positionBounds,points[id]);include(uvBounds,coordinates[id]);}
   }
   charts.push({mesh:mi,meshName:mesh.name??null,primitive:pi,material:p.material,materialName:material?.name??null,texCoord:set,textureRoles,
    triangleCount:corners/3,degenerateUvTriangles:bad.length,triangleIndices:bad,
    geometricallyDegenerateTriangles:geometryBad.length,geometricallyDegenerateTriangleIndices:geometryBad,
    constantUTriangles,constantVTriangles,boundaryVTriangles,
    positionBounds:bad.length?positionBounds:null,uvBounds:bad.length?uvBounds:null});
  }
 }
 return {schema:1,status:uvTriangles.size?'blocked':charts.length?'passed':'not-applicable',
  policy:'Exact zero UV determinant blocks acceptance; no repair or artistic approval. Geometry counts cover audited textured primitives only.',
  degenerateUvTriangles:uvTriangles.size,degenerateUvTriangleCharts:charts.reduce((n,c)=>n+c.degenerateUvTriangles,0),
  geometricallyDegenerateTriangles:geometryTriangles.size,skippedUntexturedPrimitives:skipped,charts};
}
module.exports={auditUv};
if(require.main===module){
 try{
  if(process.argv.length!==3)throw new Error('Usage: node tools/qa/audit_uv.cjs INPUT_GLB > REPORT_JSON');
  const bytes=fs.readFileSync(process.argv[2]),{document,binary}=decodeGlb(bytes),report=auditUv(document,binary);
  report.sourceSha256=crypto.createHash('sha256').update(bytes).digest('hex');
  console.log(JSON.stringify(report,null,2));process.exitCode=report.status==='blocked'?1:0;
 }catch(error){console.error(error.message);process.exitCode=2;}
}
