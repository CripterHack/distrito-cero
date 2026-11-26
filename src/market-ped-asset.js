/* Unpack the two indexed pedestrian meshes into the existing 16-float skinned vertex layout. */
'use strict';
(function(D){
 const data=D.MarketPedData;
 function bytes(s){
  const raw=atob(s), b=new Uint8Array(raw.length);
  for(let i=0;i<raw.length;i++)b[i]=raw.charCodeAt(i);
  return new DataView(b.buffer);
 }
 function decodeLevel(lod){
  const level=data.levels[lod];
  if(!level)throw new RangeError('Unknown market pedestrian LOD');
  const vertices=bytes(data.vertices),indices=bytes(level.indices),count=level.triangles*3;
  if(indices.byteLength!==count*2||vertices.byteLength%21)throw new Error('Invalid market pedestrian buffers');
  const out=new Float32Array(count*16);
  for(let i=0;i<count;i++){
   const src=indices.getUint16(i*2,true)*21,dst=i*16;
   for(let k=0;k<3;k++)out[dst+k]=vertices.getInt16(src+k*2,true)/16000;
   const nx=vertices.getInt8(src+6),ny=vertices.getInt8(src+7),nz=vertices.getInt8(src+8),scale=1/Math.hypot(nx,ny,nz);
   out[dst+3]=nx*scale;out[dst+4]=ny*scale;out[dst+5]=nz*scale;
   out[dst+6]=vertices.getUint16(src+9,true)/65535;out[dst+7]=vertices.getUint16(src+11,true)/65535;
   for(let k=0;k<4;k++){
    out[dst+8+k]=vertices.getUint8(src+13+k);
    out[dst+12+k]=vertices.getUint8(src+17+k)/255;
   }
  }
  return out;
 }
 D.MarketPedAsset=Object.freeze({levels:data.levels,atlas:data.atlas,decodeLevel,
                                 clips:D.MarketPedPose.clips,writePalette:D.MarketPedPose.writePalette});
})(DC);
