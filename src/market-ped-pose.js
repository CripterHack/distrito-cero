/* Local glTF clip playback for the market pedestrian. Giro and the two stopping steps play once.
   walkBlend mixes idle/locomotion; runBlend mixes walk/run at the same foot phase. */
'use strict';
(function(D) {
 const rig=D.MarketPedData.pose, joints=rig.parents.length;
 function decodeFloats(encoded) {
  const bytes=Uint8Array.from(atob(encoded),c=>c.charCodeAt(0));
  const source=new DataView(bytes.buffer), result=new Float32Array(bytes.length/4);
  for(let i=0;i<result.length;i++)result[i]=source.getFloat32(i*4,true);
  return result;
 }
 function makeSample() {
  const rotations=new Float64Array(joints*4);
  for(let i=0;i<joints;i++)rotations[i*4+3]=1;
  return {rotations, root:new Float64Array(rig.localBind.slice(rig.root*3,rig.root*3+3))};
 }
 function slerp(a,i,b,j,t,out,k) {
  const ax=a[i],ay=a[i+1],az=a[i+2],aw=a[i+3];
  const bx=b[j],by=b[j+1],bz=b[j+2],bw=b[j+3];
  const dot=ax*bx+ay*by+az*bz+aw*bw, cosine=Math.min(1,Math.abs(dot));
  let left=1-t, right=t;
  if(cosine<.9995) {
   const angle=Math.acos(cosine), sin=Math.sin(angle);
   left=Math.sin(left*angle)/sin;right=Math.sin(right*angle)/sin;
  }
  if(dot<0)right=-right;
  const x=ax*left+bx*right, y=ay*left+by*right, z=az*left+bz*right, w=aw*left+bw*right;
  const inv=1/Math.sqrt(x*x+y*y+z*z+w*w);
  out[k]=x*inv;out[k+1]=y*inv;out[k+2]=z*inv;out[k+3]=w*inv;
 }
 const clips={},metadata={};
 for(const [name,source] of Object.entries(rig.clips)) {
  const sample=makeSample(), animated=[];
  for(const {joint,translation,data} of source.tracks) {
   const keys=decodeFloats(data), components=translation?3:4;
   const target=translation?sample.root:sample.rotations, index=translation?0:joint*4;
   if(keys.length===components)target.set(keys,index);
   else animated.push({keys,translation,components,target,index});
  }
  clips[name]={sample,animated,intervals:source.frames-1,oneShot:['Giro','FrenadaL','FrenadaR'].includes(name)};
  metadata[name]=Object.freeze({duration:source.duration});
 }
 function sampleClip(clip,phase) {
  const progress=clip.oneShot?Math.max(0,Math.min(1,phase)):phase-Math.floor(phase);
  const at=progress*clip.intervals;
  const frame=Math.min(clip.intervals-1,Math.floor(at)), t=at-frame;
  for(let k=0;k<clip.animated.length;k++) {
   const track=clip.animated[k], a=frame*track.components, b=a+track.components;
   if(track.translation) {
    for(let i=0;i<3;i++)track.target[i]=track.keys[a+i]*(1-t)+track.keys[b+i]*t;
   } else slerp(track.keys,a,track.keys,b,t,track.target,track.index);
  }
  return clip.sample;
 }
 const locomotion=makeSample(), finalPose=makeSample();
 function blendLocal(a,b,t,out) {
  if(t<=0)return a;
  if(t>=1)return b;
  for(let k=0;k<joints*4;k+=4)slerp(a.rotations,k,b.rotations,k,t,out.rotations,k);
  for(let k=0;k<3;k++)out.root[k]=a.root[k]*(1-t)+b.root[k]*t;
  return out;
 }
 const local=new Float64Array(16);
 function localMatrix(pose,joint) {
  const i=joint*4, q=pose.rotations, x=q[i], y=q[i+1], z=q[i+2], w=q[i+3];
  local[0]=1-2*(y*y+z*z);local[1]=2*(x*y+w*z);local[2]=2*(x*z-w*y);
  local[4]=2*(x*y-w*z);local[5]=1-2*(x*x+z*z);local[6]=2*(y*z+w*x);
  local[8]=2*(x*z+w*y);local[9]=2*(y*z-w*x);local[10]=1-2*(x*x+y*y);
  const t=joint===rig.root?pose.root:rig.localBind, j=joint===rig.root?0:joint*3;
  local[12]=t[j];local[13]=t[j+1];local[14]=t[j+2];local[15]=1;
 }
 function sampleMotion(walkPhase,idlePhase,walkBlend,runBlend) {
  if(walkBlend<=0)return sampleClip(clips.Reposo,idlePhase);
  let stride;
  if(!clips.Carrera || runBlend<=0)stride=sampleClip(clips.Marcha,walkPhase);
  else if(runBlend>=1)stride=sampleClip(clips.Carrera,walkPhase);
  else stride=blendLocal(sampleClip(clips.Marcha,walkPhase),sampleClip(clips.Carrera,walkPhase),runBlend,locomotion);
  return walkBlend>=1?stride:blendLocal(sampleClip(clips.Reposo,idlePhase),stride,walkBlend,finalPose);
 }
 function writePalette(out,walkPhase,idlePhase,walkBlend,runBlend=0,actionProgress=null,actionBlend=1,actionName='Giro') {
  let pose;
  if(actionProgress!==null && clips[actionName]) {
   pose=sampleClip(clips[actionName],actionProgress);
   if(actionBlend<1)pose=blendLocal(sampleMotion(walkPhase,idlePhase,walkBlend,runBlend),pose,actionBlend,finalPose);
  } else pose=sampleMotion(walkPhase,idlePhase,walkBlend,runBlend);
  // Build world matrices parent-first into the caller's palette. The source
  // joint index order places each clavicle after its upper arm.
  for(let k=0;k<joints;k++) {
   const joint=rig.order[k], parent=rig.parents[joint], target=joint*16;
   localMatrix(pose,joint);
   if(parent<0)out.set(local,target);
   else {
    const p=parent*16;
    for(let col=0;col<16;col+=4) {
     const x=local[col], y=local[col+1], z=local[col+2], w=local[col+3];
     for(let row=0;row<3;row++)out[target+col+row]=out[p+row]*x+out[p+4+row]*y+out[p+8+row]*z+out[p+12+row]*w;
     out[target+col+3]=w;
    }
   }
  }
  // Multiply by the validated glTF inverse binds, all pure translations.
  for(let joint=0;joint<joints;joint++) {
   const i=joint*16, t=joint*3, b=rig.globalBind;
   for(let r=0;r<3;r++)out[i+12+r]-=out[i+r]*b[t]+out[i+4+r]*b[t+1]+out[i+8+r]*b[t+2];
  }
  return out;
 }
 D.MarketPedPose=Object.freeze({writePalette,clips:Object.freeze(metadata)});
})(DC);
