/* Position-cluster LOD construction at startup, never per frame. No external decoder. */
'use strict';
(function(D){
 function reduce(data,cell,options={}){
  if(!(data instanceof Float32Array)||data.length%48||!Number.isFinite(cell)||cell<=0)throw new Error('Invalid LOD input');
  const clusters=new Map(),indices=[],verts=[];
  for(let i=0;i<data.length;i+=16){
   let dominant=0;for(let j=1;j<4;j++)if(data[i+12+j]>data[i+12+dominant])dominant=j;
   const key=[Math.round(data[i]/cell),Math.round(data[i+1]/cell),Math.round(data[i+2]/cell),data[i+8+dominant],...(options.preserveUV?[Math.floor(data[i+6]*32),Math.floor(data[i+7]*32)]:[])].join(':');
   let id=clusters.get(key);if(id===undefined){id=verts.length;clusters.set(key,id);verts.push({sum:new Float64Array(8),weights:new Map(),count:0});}
   const v=verts[id];v.count++;for(let k=0;k<8;k++)v.sum[k]+=data[i+k];for(let k=0;k<4;k++){const j=data[i+8+k];v.weights.set(j,(v.weights.get(j)||0)+data[i+12+k]);}indices.push(id);
  }
  const rows=verts.map(v=>{const row=new Float32Array(16);for(let j=0;j<8;j++)row[j]=v.sum[j]/v.count;const l=Math.hypot(row[3],row[4],row[5])||1;for(let j=3;j<6;j++)row[j]/=l;
   const weights=[...v.weights].sort((a,b)=>b[1]-a[1]).slice(0,4),sum=weights.reduce((a,b)=>a+b[1],0);weights.forEach(([joint,w],i)=>{row[8+i]=joint;row[12+i]=w/sum;});return row;
  });
  const out=[],seen=new Set();for(let i=0;i<indices.length;i+=3){let a=indices[i],b=indices[i+1],c=indices[i+2];if(a===b||a===c||b===c)continue;const key=[a,b,c].sort((a,b)=>a-b).join(':');if(seen.has(key))continue;seen.add(key);const A=rows[a],B=rows[b],C=rows[c],cross=D.cross([B[0]-A[0],B[1]-A[1],B[2]-A[2]],[C[0]-A[0],C[1]-A[1],C[2]-A[2]]);if(Math.hypot(...cross)<1e-8)continue;out.push(...A,...B,...C);}
  return new Float32Array(out);
 }
 D.CrowdGeometry={reduce};
})(DC);
