/* Original native rigid dual-quaternion skinning. XYZW convention, metres.
   Blending follows Kavan et al. (2008). No copied library implementation.
   Bone transforms must be rigid. Non-uniform appearance morphs happen before skinning. */
'use strict';
(function(D){
 function pack(matrices,out=new Float32Array(matrices.length/2),offset=0){
  if(!matrices.length||matrices.length%16||!Number.isInteger(offset)||offset<0||out.length<offset+matrices.length/2)throw new Error('Invalid dual quaternion palette size');
  for(let i=0;i<matrices.length;i+=16){
   for(let j=0;j<16;j++)if(!Number.isFinite(matrices[i+j]))throw new Error('Nonfinite bone transform');
   const m=matrices.subarray(i,i+16),tr=m[0]+m[5]+m[10];let x,y,z,w,s;
   if(tr>0){s=Math.sqrt(tr+1)*2;w=s/4;x=(m[6]-m[9])/s;y=(m[8]-m[2])/s;z=(m[1]-m[4])/s;}
   else if(m[0]>m[5]&&m[0]>m[10]){s=Math.sqrt(Math.max(0,1+m[0]-m[5]-m[10]))*2;w=(m[6]-m[9])/s;x=s/4;y=(m[4]+m[1])/s;z=(m[8]+m[2])/s;}
   else if(m[5]>m[10]){s=Math.sqrt(Math.max(0,1+m[5]-m[0]-m[10]))*2;w=(m[8]-m[2])/s;x=(m[4]+m[1])/s;y=s/4;z=(m[9]+m[6])/s;}
   else{s=Math.sqrt(Math.max(0,1+m[10]-m[0]-m[5]))*2;w=(m[1]-m[4])/s;x=(m[8]+m[2])/s;y=(m[9]+m[6])/s;z=s/4;}
   const len=Math.hypot(x,y,z,w);if(!Number.isFinite(len)||len<1e-8)throw new Error('Invalid rotation');x/=len;y/=len;z/=len;w/=len;
   const tx=m[12],ty=m[13],tz=m[14],j=offset+i/2;
   out.set([x,y,z,w,.5*(tx*w+ty*z-tz*y),.5*(-tx*z+ty*w+tz*x),.5*(tx*y-ty*x+tz*w),-.5*(tx*x+ty*y+tz*z)],j);
  }return out;
 }
 // CPU reference for deterministic validation and authoring, not per-vertex runtime work.
 function transform(palette,point,joints,weights){
  if(joints.length!==weights.length||!joints.length)throw new Error('Invalid influences');
  let ref=null,r=[0,0,0,0],d=[0,0,0,0];
  for(let k=0;k<joints.length;k++){
   const off=joints[k]*8,weight=weights[k];if(!Number.isFinite(weight)||weight<0||!Number.isInteger(joints[k])||off<0||off+7>=palette.length)throw new Error('Invalid influence');if(!weight)continue;
   const q=palette.subarray(off,off+4);if(!ref)ref=q;const sign=q.reduce((sum,v,i)=>sum+v*ref[i],0)<0?-1:1;
   for(let i=0;i<4;i++){r[i]+=q[i]*weight*sign;d[i]+=palette[off+4+i]*weight*sign;}
  }
  const len=Math.hypot(...r);if(len<1e-8)throw new Error('Empty skin weight');r=r.map(x=>x/len);d=d.map(x=>x/len);
  const [x,y,z,w]=r,[dx,dy,dz,dw]=d,[px,py,pz]=point;
  const cx=2*(y*pz-z*py),cy=2*(z*px-x*pz),cz=2*(x*py-y*px);
  return [px+w*cx+y*cz-z*cy+2*(w*dx-dw*x+y*dz-z*dy),py+w*cy+z*cx-x*cz+2*(w*dy-dw*y+z*dx-x*dz),pz+w*cz+x*cy-y*cx+2*(w*dz-dw*z+x*dy-y*dx)];
 }
 D.DualQuaternion=Object.freeze({pack,transform});
})(DC);
