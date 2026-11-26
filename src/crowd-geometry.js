/* Position-cluster LOD construction at startup, never per frame. No external decoder. */
'use strict';
(function(D){
 function weldSeamClusters(data,indices,verts){
  const parents=Int32Array.from({length:verts.length},(_,i)=>i),seen=new Map();
  const root=i=>{while(parents[i]!==i){parents[i]=parents[parents[i]];i=parents[i];}return i;};
  // Compare all fourteen geometry/skinning attributes bit-for-bit. UVs alone
  // may differ; different normals, joint order or zero-weight IDs are not seams.
  const bits=new Uint32Array(data.buffer,data.byteOffset,data.length);let joined=false;
  for(let i=0;i<indices.length;i++){
   const o=i*16,key=[bits[o],bits[o+1],bits[o+2],bits[o+3],bits[o+4],bits[o+5],
    bits[o+8],bits[o+9],bits[o+10],bits[o+11],bits[o+12],bits[o+13],bits[o+14],bits[o+15]].join(':');
   const previous=seen.get(key),id=indices[i];
   if(previous===undefined)seen.set(key,id);
   else{const a=root(previous),b=root(id);if(a!==b){parents[Math.max(a,b)]=Math.min(a,b);joined=true;}}
  }
  if(!joined)return;
  const united=new Map();
  for(let i=0;i<verts.length;i++){
   const id=root(i);if(id===i)continue;let group=united.get(id);
   if(!group){const v=verts[id];group={sum:v.sum.slice(),weights:new Map(v.weights),count:v.count};united.set(id,group);}
   const v=verts[i];group.count+=v.count;for(let k=0;k<8;k++)group.sum[k]+=v.sum[k];
   for(const[j,w]of v.weights)group.weights.set(j,(group.weights.get(j)||0)+w);
  }
  for(const[id,group]of united)verts[id]=group;
  for(let i=0;i<indices.length;i++)indices[i]=root(indices[i]);
 }
 function islandClusterUV(data,clusters){
  const corners=data.length/16,parents=Int32Array.from({length:corners/3},(_,i)=>i);
  const root=i=>{while(parents[i]!==i){parents[i]=parents[parents[i]];i=parents[i];}return i;};
  const vertices=new Map(),ids=new Uint32Array(corners),edges=new Map();
  for(let i=0;i<corners;i++){
   const o=i*16,key=[data[o],data[o+1],data[o+2],data[o+6],data[o+7]].join(':');
   let id=vertices.get(key);if(id===undefined){id=vertices.size;vertices.set(key,id);}ids[i]=id;
  }
  // Shared position+UV edges join a chart. A point contact or equal UVs on
  // unrelated geometry cannot join islands and leak one atlas region to another.
  for(let i=0;i<corners;i+=3)for(let k=0;k<3;k++){
   const a=ids[i+k],b=ids[i+(k+1)%3];if(a===b)continue;
   const key=a<b?a+':'+b:b+':'+a,prior=edges.get(key),triangle=i/3;
   if(prior===undefined)edges.set(key,triangle);
   else{const x=root(prior),y=root(triangle);if(x!==y)parents[Math.max(x,y)]=Math.min(x,y);}
  }
  const groups=new Map(),cornerGroups=[];
  for(let i=0;i<corners;i++){
   const key=clusters[i]+':'+root(Math.floor(i/3));let group=groups.get(key);
   if(group===undefined){group=[0,0,0];groups.set(key,group);}cornerGroups.push(group);
   group[0]+=data[i*16+6];group[1]+=data[i*16+7];group[2]++;
  }
  const uv=new Float32Array(corners*2);
  for(let i=0;i<corners;i++){const g=cornerGroups[i];uv[i*2]=g[0]/g[2];uv[i*2+1]=g[1]/g[2];}
  return uv;
 }
 // Grid centers are in the canonical character's rest space (metres).
 // Lock the authored neckline and its first torso ring as whole cells so
 // that neighboring reduced faces attach to the same boundary vertices.
 function necklineCell(gridX,gridY,gridZ,cell){
  const x=gridX*cell, z=gridZ*cell+.01;
  return gridY*cell>=1.45 && x*x+z*z<=.112*.112;
 }
 function reduce(data,cell,options={}){
  if(!(data instanceof Float32Array)||data.length%48||!Number.isFinite(cell)||cell<=0)throw new Error('Invalid LOD input');
  // Optional authoring metadata preserves pre-atlas spatial/UV clusters. New
  // atlas coordinates average only within each connected island of a cluster.
  const clusterUV=options.clusterUV;
  if(clusterUV!==undefined&&(!(clusterUV instanceof Uint16Array)||!options.preserveUV||clusterUV.length!==data.length/16||clusterUV.some(v=>v>1088)))throw new Error('Invalid LOD cluster UV metadata');
  if(options.weldUVSeams!==undefined&&typeof options.weldUVSeams!=='boolean'||options.weldUVSeams&&!options.preserveUV)throw new Error('Invalid LOD seam welding: UV preservation is required');
  const keepCollar=options.preserveJacketNeckline===true;
  if(keepCollar&&options.preserveUV)throw new Error('Jacket neckline and face UV policies are distinct');
  const clusters=new Map(),indices=[],verts=[];
  for(let i=0;i<data.length;i+=16){
   const gx=Math.round(data[i]/cell),gy=Math.round(data[i+1]/cell),gz=Math.round(data[i+2]/cell);
   if(keepCollar && necklineCell(gx,gy,gz,cell)){
    const sourceRow=data.subarray(i,i+16);
    // Include UV, normal and skinning attributes: equal positions alone
    // would weld distinct source corners at seams.
    const key='source:'+sourceRow.join(':');
    let id=clusters.get(key);
    if(id===undefined){id=verts.length;clusters.set(key,id);verts.push({sourceRow});}
    indices.push(id);
    continue;
   }
   let dominant=0;for(let j=1;j<4;j++)if(data[i+12+j]>data[i+12+dominant])dominant=j;
   const uvBin=clusterUV?.[i/16];
   const key=[gx,gy,gz,data[i+8+dominant],...(options.preserveUV?(clusterUV?[uvBin%33,Math.floor(uvBin/33)]:[Math.floor(data[i+6]*32),Math.floor(data[i+7]*32)]):[])].join(':');
   let id=clusters.get(key);if(id===undefined){id=verts.length;clusters.set(key,id);verts.push({sum:new Float64Array(8),weights:new Map(),count:0});}
   const v=verts[id];v.count++;for(let k=0;k<8;k++)v.sum[k]+=data[i+k];for(let k=0;k<4;k++){const j=data[i+8+k];v.weights.set(j,(v.weights.get(j)||0)+data[i+12+k]);}indices.push(id);
  }
  if(options.weldUVSeams)weldSeamClusters(data,indices,verts);
  const rows=verts.map(v=>{if(v.sourceRow)return v.sourceRow;const row=new Float32Array(16);for(let j=0;j<8;j++)row[j]=v.sum[j]/v.count;const l=Math.hypot(row[3],row[4],row[5])||1;for(let j=3;j<6;j++)row[j]/=l;
   const weights=[...v.weights].sort((a,b)=>b[1]-a[1]).slice(0,4),sum=weights.reduce((a,b)=>a+b[1],0);weights.forEach(([joint,w],i)=>{row[8+i]=joint;row[12+i]=w/sum;});return row;
  });
  const atlasUV=clusterUV||options.weldUVSeams?islandClusterUV(data,indices):null;
  const out=[],seen=new Set();for(let i=0;i<indices.length;i+=3){let a=indices[i],b=indices[i+1],c=indices[i+2];if(a===b||a===c||b===c)continue;const key=[a,b,c].sort((a,b)=>a-b).join(':');if(seen.has(key))continue;seen.add(key);const A=rows[a],B=rows[b],C=rows[c],cross=D.cross([B[0]-A[0],B[1]-A[1],B[2]-A[2]],[C[0]-A[0],C[1]-A[1],C[2]-A[2]]);if(Math.hypot(...cross)<1e-8)continue;
   if(atlasUV){for(let k=0;k<3;k++){const start=out.length;out.push(...rows[indices[i+k]]);out[start+6]=atlasUV[(i+k)*2];out[start+7]=atlasUV[(i+k)*2+1];}}
   else out.push(...A,...B,...C);
  }
  return new Float32Array(out);
 }
 D.CrowdGeometry={reduce};
})(DC);
