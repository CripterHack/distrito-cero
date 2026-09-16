/* Offline mesh/rig diagnosis for the avatar, never included in runtime. */
const {D,R,samples,shapes,shapeSDF}=require('../../tests/helpers/finger_surfaces.cjs');
const sub=(a,b)=>a.map((v,i)=>v-b[i]);
const s=new D.Simulation(new D.World());Object.assign(s.player,{x:0,z:0,yaw:0,car:null});s.time=1.25;
function prepare(side,key,rel=0,item='rifle'){
 Object.assign(s.equipment,{selected:item,aimWeight:1,reloading:rel*(D.Equipment.get(item).reload||0)});
 const m=D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=R.pose(n,s.time),original=q.matrices.slice(),f=R.fingers[side].find(f=>f.name==='thumb'),shape=shapes[key];
 const toLocal=p=>{p=p.map((v,i)=>v+(i===1?q.rootY:0)-m.origin[i]);p=[[1,0,0],[0,1,0],[0,0,1]].map(x=>D.dot(p,m.direction(x)));if(key.includes('Magazine')||key==='magazine'){const o=m.magazine.offset,t=m.magazine.rotation[2],pi=m.magazine.pivot;p=p.map((v,i)=>v-o[i]-pi[i]);p=[p[0]*Math.cos(t)+p[1]*Math.sin(t),-p[0]*Math.sin(t)+p[1]*Math.cos(t),p[2]].map((v,i)=>v+pi[i]);}return p;};
 const base=toLocal(R.transform(q.matrices.subarray(R.ids[f.bones[0]]*16,R.ids[f.bones[0]]*16+16),f.joints[0]));
 const others=[];
 for(const other of R.fingers[side].filter(f=>f.name!=='thumb'))for(let j=0;j<3;j++)for(const t of[0,.25,.5,.75,1]){const a=other.joints[j],b=j<2?other.joints[j+1]:other.tip,mat=original.subarray(R.ids[other.bones[j]]*16,R.ids[other.bones[j]]*16+16);others.push({p:toLocal(R.transform(mat,a.map((v,i)=>v+(b[i]-v)*t))),radius:other.radius*.9});}
 function evaluate(params,detail=false){
  q.matrices.set(original);const sign=side==='R'?1:-1;
  const amount=m.grips[side].amount;const rotations=[0,1,2].map(j=>[params[3+j],sign*amount*.06,-sign*amount*[.14,.23,.18][j]]);
  for(let j=0;j<3;j++){
   const id=R.ids[f.bones[j]],[,parentName,bind]=R.bones[id],pi=R.ids[parentName],pb=R.bones[pi][2];
   let parent=R.multiply(q.matrices.subarray(pi*16,pi*16+16),R.matrix(pb));
   if(j===0){const pivot=[pb[0]-.002*sign,pb[1]-.018,.012];parent=R.multiply(parent,R.multiply(R.multiply(R.matrix(sub(pivot,pb)),R.matrix([0,0,0],params[0],sign*params[1],sign*params[2])),R.matrix(sub(bind,pivot))));}else parent=R.multiply(parent,R.matrix(sub(bind,pb)));
   const world=R.multiply(parent,R.matrix([0,0,0],...rotations[j]));
   q.matrices.set(R.multiply(world,R.matrix(bind.map(v=>-v))),id*16);
  }
  const dq=D.DualQuaternion.pack(q.matrices);let worst=1,inside=0,energy=0,padGap=1,padPoint=null;
  for(const v of samples[side+'thumb']){const p=toLocal(D.DualQuaternion.transform(dq,v.p,v.j,v.w)),dist=shapeSDF(p,shape);worst=Math.min(worst,dist);if(dist<0)inside++;
   energy+=Math.pow(Math.min(0,dist-.0005)*100,2);
   if(v.j[0]===R.ids[f.bones[2]]&&v.w[0]>.9&&v.p[1]<.791&&Math.abs(dist)<Math.abs(padGap)){padGap=dist;padPoint=p;}
  }
  const tip=toLocal(R.transform(q.matrices.subarray(R.ids[f.bones[2]]*16,R.ids[f.bones[2]]*16+16),f.tip));
  // Minimise intersection first, then keep the tip pad near the prop with a modest rotation cost.
  let collisionMin=1,selfEnergy=0;
  for(let j=1;j<3;j++)for(const t of[0,.25,.5,.75,1]){const a=f.joints[j],b=j<2?f.joints[j+1]:f.tip,mat=q.matrices.subarray(R.ids[f.bones[j]]*16,R.ids[f.bones[j]]*16+16),p=toLocal(R.transform(mat,a.map((v,i)=>v+(b[i]-v)*t)));
   for(const other of others){const d=Math.hypot(...p.map((v,i)=>v-other.p[i]))-f.radius*.8-other.radius;collisionMin=Math.min(collisionMin,d);selfEnergy+=Math.pow(Math.min(0,d-.001)*100,2);}
  }
  const objective=energy+selfEnergy+Math.pow(padGap*80,2)+params.reduce((n,v,i)=>n+.002*v*v,0);
  return detail?{key,side,params,base,tip,worst,inside,padGap,padPoint,objective,collisionMin}:objective;
 }
 return evaluate;
}
let seed=12345;function rnd(){seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;}
const bounds=[[-.7,.8],[-1.1,1.1],[0,1.15],[-.4,1.0],[-.1,.8],[-.1,.8]];
const all=[];
for(const [side,key,rel,item]of[['R','grip',0,'rifle'],['L','fore',0,'rifle'],['L','magazine',.5,'rifle'],['L','pistolMagazine',.5,'pistol']]){
 const evaluate=prepare(side,key,rel,item);let best={e:Infinity};
 for(let restart=0;restart<8;restart++){
  let p=restart?bounds.map(([lo,hi])=>lo+(hi-lo)*rnd()):[0,0,.45,.4,.2,.15],e=evaluate(p);
  for(const step of [.35,.16,.07,.025,.009])for(let pass=0;pass<8;pass++){let changed=false;for(let j=0;j<p.length;j++)for(const d of [-step,step]){const c=p.slice();c[j]=Math.max(bounds[j][0],Math.min(bounds[j][1],c[j]+d));const ce=evaluate(c);if(ce<e){p=c;e=ce;changed=true;}}if(!changed)break;}
  if(e<best.e)best={e,p};
 }
 const result=evaluate(best.p,true);all.push(result);console.log(JSON.stringify(result));
}
require('fs').mkdirSync('artifacts/thumb-investigation',{recursive:true});
require('fs').writeFileSync('artifacts/thumb-investigation/fit-collision.json',JSON.stringify(all,null,2));
