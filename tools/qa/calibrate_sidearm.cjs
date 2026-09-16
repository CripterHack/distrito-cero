// Offline artistic calibration of the avatar's two-hand support. Never bundled.
// Fixed seed and bounded coordinate search over pose angles only.
// Proxies describe existing game art, not real-world equipment engineering.
const {D,R,samples,shapeSDF,shapes}=require('../../tests/helpers/finger_surfaces.cjs');
const sub=(a,b)=>a.map((v,i)=>v-b[i]),add=(a,b)=>a.map((v,i)=>v+b[i]);
const candidates=[];
for(const id of ['pistol','revolver'])for(const triggerWeight of [0,.5,1]){
 const s=new D.Simulation(new D.World());Object.assign(s.player,{x:0,z:0,yaw:0,car:null});s.time=1.25;s.equipment.selected=id;s.equipment.aimWeight=1;s.equipment.handling={item:id,ready:1,triggerWeight};
 const m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=R.pose(n,s.time),original=q.matrices.slice(),caps=[];
 for(const f of R.fingers.R)for(let j=0;j<3;j++){const a=q.matrices.subarray(R.ids[f.bones[j]]*16,R.ids[f.bones[j]]*16+16);caps.push({name:f.name,a:R.transform(a,f.joints[j]),b:R.transform(a,j<2?f.joints[j+1]:f.tip),r:f.radius*[.94,.85,.70][j]});}
 const local=p=>{p=p.map((v,i)=>v+(i===1?q.rootY:0)-m.origin[i]);return [[1,0,0],[0,1,0],[0,0,1]].map(v=>D.dot(p,m.direction(v)));};
 candidates.push({s,m,n,q,original,caps,local});
}
function distance(p,c){const d=sub(c.b,c.a),t=D.clamp(D.dot(sub(p,c.a),d)/D.dot(d,d),0,1);return Math.hypot(...sub(p,add(c.a,d.map(v=>v*t))))-c.r;}
const result={fingers:{}};
function update(q,f,values,opposition=null){
 for(let j=0;j<3;j++){
  const id=R.ids[f.bones[j]],[,parent,bind]=R.bones[id],pi=R.ids[parent],pb=R.bones[pi][2];
  let world=R.multiply(q.matrices.subarray(pi*16,pi*16+16),R.matrix(pb));
  const rot=f.name==='thumb'?[values[j],-.61*.06,.61*[.14,.23,.18][j]]:[0,0,values[j]];
  if(j===0&&opposition){const pivot=[pb[0]+.002,pb[1]-.018,pb[2]+.012];world=R.multiply(world,R.multiply(R.multiply(R.matrix(sub(pivot,pb)),R.matrix([0,0,0],opposition[0],-opposition[1],-opposition[2])),R.matrix(sub(bind,pivot),...rot)));}
  else world=R.multiply(world,R.matrix(sub(bind,pb),...rot));
  q.matrices.set(R.multiply(world,R.matrix(bind.map(v=>-v))),id*16);
 }
}
function score(f,p,detail=false){let loss=0,worstHand=1,worstProp=1,minGap=1;const thumb=f.name==='thumb';
 for(const c of candidates){
  const q=c.q;q.matrices.set(c.original);
  for(const o of R.fingers.L)if(result.fingers[o.name])update(q,o,result.fingers[o.name],o.name==='thumb'?result.opposition:null);
  update(q,f,thumb?p.slice(3):p,thumb?p.slice(0,3):null);
  const dq=D.DualQuaternion.pack(q.matrices),points=samples['L'+f.name];let gap=1,padGap=1;
  for(const v of points){const x=D.DualQuaternion.transform(dq,v.p,v.j,v.w),prop=shapeSDF(c.local(x),shapes.grip);let hand=1;
   for(const a of c.caps)hand=Math.min(hand,distance(x,a));
   const near=Math.min(prop,hand);worstHand=Math.min(worstHand,hand);worstProp=Math.min(worstProp,prop);gap=Math.min(gap,near);if(v.j[0]===R.ids[f.bones[2]]&&v.w[0]>.9)padGap=Math.min(padGap,near);
   loss+=Math.pow(Math.min(0,prop-.00065)*140,2)+Math.pow(Math.min(0,hand-.00065)*140,2);
  }
  minGap=Math.min(minGap,gap);loss+=Math.pow(Math.max(0,padGap-.002)*60,2);
  if(thumb){
   for(const o of R.fingers.L.filter(o=>o.name!=='thumb'))for(let j=0;j<3;j++){
    const mat=q.matrices.subarray(R.ids[o.bones[j]]*16,R.ids[o.bones[j]]*16+16),cap={a:R.transform(mat,o.joints[j]),b:R.transform(mat,j<2?o.joints[j+1]:o.tip),r:o.radius*.85};
    for(let k=1;k<3;k++){const mat=q.matrices.subarray(R.ids[f.bones[k]]*16,R.ids[f.bones[k]]*16+16),a=R.transform(mat,f.joints[k]),b=R.transform(mat,k<2?f.joints[k+1]:f.tip);for(const t of[0,.25,.5,.75,1]){const d=distance(add(a,sub(b,a).map(v=>v*t)),cap)-f.radius*.80;loss+=Math.pow(Math.min(0,d-.0005)*180,2);}}
   }
  }
 }
 loss+=p.reduce((n,v)=>n+.0002*v*v,0);
 return detail?{finger:f.name,params:p,worstHand,worstProp,minGap,loss}:loss;
}
let seed=21167;function rnd(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
for(const f of R.fingers.L){
 const thumb=f.name==='thumb',bounds=thumb?[[-.8,.8],[-1.1,1.1],[0,1.1],[-.4,1.1],[-.1,.9],[-.1,.9]]:[[.03,1.25],[.03,1.5],[.03,1.3]];
 let best={loss:Infinity};
 for(let restart=0;restart<(thumb?7:5);restart++){
  let p=restart?bounds.map(([lo,hi])=>lo+rnd()*(hi-lo)):thumb?[0,0,.3,.3,.2,.1]:[.4,.8,.5],loss=score(f,p);
  for(const step of [.25,.10,.04,.015,.005])for(let iter=0;iter<7;iter++){let moved=false;for(let j=0;j<p.length;j++)for(const d of[-step,step]){const v=p.slice();v[j]=D.clamp(v[j]+d,...bounds[j]);const l=score(f,v);if(l<loss){loss=l;p=v;moved=true;}}if(!moved)break;}
  if(loss<best.loss)best={p,loss};
 }
 const d=score(f,best.p,true);console.log(JSON.stringify(d));result.fingers[f.name]=thumb?best.p.slice(3):best.p;if(thumb)result.opposition=best.p.slice(0,3);
}
require('fs').mkdirSync('artifacts/sidearm-calibration',{recursive:true});
require('fs').writeFileSync('artifacts/sidearm-calibration/fitted.json',JSON.stringify(result,null,2));
