/* Police encounter tuning and vehicle geometry. Native JS, metres and seconds. */
'use strict';
(function(D){
 D.POLICE=Object.freeze({
  sightRange:72,searchDelay:6,heatDecay:3.2,
  carArrestSpeed:1.15,footArrestSpeed:.65,carArrestRange:7.2,footArrestRange:3.6,
  carArrestSeconds:6,footArrestSeconds:4.5,arrestDecay:.85,
  impactGrace:1.6,recoverySeconds:1.25,recoveryCooldown:3,
  surrenderRange:18,surrenderSeconds:1.8,surrenderFee:150,arrestFee:300,
  halfWidth:1.0,halfLength:2.23
 });
 // Separating-axis test for oriented car bodies. A contact normal points B -> A.
 // Unlike the old 3.2 m circle, the footprint matches the long, narrow car mesh.
 D.vehicleOverlap=function(a,b){
  const dx=a.x-b.x,dz=a.z-b.z;if(Math.hypot(dx,dz)>5)return null;
  const ar={x:Math.cos(a.yaw),z:-Math.sin(a.yaw)},af={x:Math.sin(a.yaw),z:Math.cos(a.yaw)};
  const br={x:Math.cos(b.yaw),z:-Math.sin(b.yaw)},bf={x:Math.sin(b.yaw),z:Math.cos(b.yaw)};
  const dot=(v,w)=>v.x*w.x+v.z*w.z,{halfWidth:w,halfLength:l}=D.POLICE;
  let depth=Infinity,normal=null;
  for(const axis of [ar,af,br,bf]){
   const signed=dx*axis.x+dz*axis.z;
   const overlap=w*(Math.abs(dot(ar,axis))+Math.abs(dot(br,axis)))+l*(Math.abs(dot(af,axis))+Math.abs(dot(bf,axis)))-Math.abs(signed);
   if(overlap<=0)return null;
   if(overlap<depth){depth=overlap;const sign=signed===0?((a.id||0)<(b.id||0)?-1:1):Math.sign(signed);normal={x:axis.x*sign,z:axis.z*sign};}
  }
  const av={x:af.x*a.speed,z:af.z*a.speed},bv={x:bf.x*b.speed,z:bf.z*b.speed};
  return{...normal,depth,closing:Math.max(0,-((av.x-bv.x)*normal.x+(av.z-bv.z)*normal.z))};
 };
 D.vehicleContains=function(c,x,z,r=.4){
  const dx=x-c.x,dz=z-c.z,u=dx*Math.cos(c.yaw)-dz*Math.sin(c.yaw),v=dx*Math.sin(c.yaw)+dz*Math.cos(c.yaw);
  const qx=Math.max(0,Math.abs(u)-D.POLICE.halfWidth),qz=Math.max(0,Math.abs(v)-D.POLICE.halfLength);
  return qx*qx+qz*qz<r*r;
 };
})(DC);
