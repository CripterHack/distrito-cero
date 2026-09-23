/* QA only. Cooperative measurements of fictional props, not a pose solver.
 * The renderer's supplied palette is authoritative. Screening is not art approval.
 */
(function(global){
 'use strict';
 const D=global.DC,R=D.SkinRig,eyeBind=global.DC_SIDEARM_SIGHT_QA?.eyeBind;
 if(!eyeBind)throw new Error('Load the mesh-derived eye observer before long-arm QA');
 const items=Object.freeze(['smg','rifle','shotgun','sniper']);
 const thresholds=Object.freeze({eye:.010,stock:.030,palm:.012,limb:.000001,minBehind:.05});
 const sub=(a,b)=>a.map((v,i)=>v-b[i]),add=(a,b)=>a.map((v,i)=>v+b[i]);
 const distance=(a,b)=>Math.hypot(...sub(a,b));
 const xyz=p=>[p.x,p.y,p.z];
 const vector=v=>Array.isArray(v)&&v.length===3&&v.every(Number.isFinite);
 const cache=new Map();
 function landmarks(item,parts){
  if(!items.includes(item))throw new Error('Unsupported long-arm family: '+item);
  if(parts===undefined&&cache.has(item))return structuredClone(cache.get(item));
  const supplied=parts!==undefined,geometry=parts??D.EquipmentGeometry.build(item),points=[];
  for(const part of geometry){
   if(!part.data||part.data.length%8)throw new Error('Invalid geometry vertex layout');
   for(let i=0;i<part.data.length;i+=8)points.push(Array.from(part.data.subarray(i,i+3)));
  }
  const requirePoint=p=>{if(!points.some(q=>distance(p,q)<.000002))throw new Error(item+' missing geometry landmark '+p.join(','));};
  // Existing buttplate rear face, independent of mount.brace.stock/target.
  const lift=item==='sniper'?.0595:0,stock=[0,-.0745+lift,-.2385];
  for(const x of [-.026,.026])for(const y of [-.114+lift,-.035+lift])requirePoint([x,y,stock[2]]);
  let rear,front,kind;
  if(item==='sniper'){
   kind='scope';rear=[0,.133,-.02];front=[0,.133,.302];
   for(const [center,radius] of [[rear,.036],[front,.028]])for(let i=0;i<4;i++){
    const a=i*Math.PI/2;requirePoint([radius*Math.cos(a),center[1]+radius*Math.sin(a),center[2]]);
   }
  }else{
   kind='open-sight';rear=[0,.0735,-.01];front=[0,.0795,.42];
   for(const [p,halfX,halfZ] of [[rear,.0225,.0065],[front,.006,.0115]])
    for(const x of [-halfX,halfX])for(const z of [-halfZ,halfZ])requirePoint([x,p[1],p[2]+z]);
  }
  const result={item,kind,rear,front,stock,geometryVerified:true};
  if(!supplied)cache.set(item,structuredClone(result));
  return structuredClone(result);
 }
 function inspect(sim,rendered){
  const item=sim.equipment.selected,ref=landmarks(item);
  let mount,pose,actor;
  if(rendered!==undefined){
   if(!rendered?.mount||!rendered?.pose)throw new Error('Incomplete rendered mount/pose evidence');
   ({mount,pose}=rendered);actor=rendered.actor||sim.player;
  }else{
   mount=D.Equipment.mount(sim);actor=D.WeaponHandling.actor(sim.player,mount,sim.equipment);pose=R.pose(actor,sim.time);
  }
  if(pose.matrices?.length!==R.bones.length*16||!Array.from(pose.matrices).every(Number.isFinite)||
     !Number.isFinite(pose.rootY)||!Number.isFinite(pose.scale)||pose.scale<=0)
   throw new Error('Invalid rendered palette or nonfinite pose');
  const c=Math.cos(actor.yaw||0),s=Math.sin(actor.yaw||0);
  const world=p=>[(actor.x||0)+(p[0]*c+p[2]*s)*pose.scale,pose.rootY+p[1]*pose.scale,(actor.z||0)+(-p[0]*s+p[2]*c)*pose.scale];
  const transform=(name,p)=>world(R.transform(pose.matrices.subarray(R.ids[name]*16,R.ids[name]*16+16),p));
  const joint=name=>transform(name,R.bones[R.ids[name]][2]);
  const eye=transform('head',D.CharacterFit.point(eyeBind,mount.neckDrop));
  const rear=mount.point(...ref.rear),front=mount.point(...ref.front),stockCenter=mount.point(...ref.stock);let stock=stockCenter;
  const shoulder=joint('upperArmR');
  // Preserve the legacy rig-reference convention. This is NOT garment collision.
  let shoulderTarget=add(shoulder,[.010*c+.024*s,-.040,-.010*s+.024*c]);
  const legacyShoulderTarget=shoulderTarget,legacyStockError=distance(stockCenter,shoulderTarget);
  let shoulderReference='legacy articulated rig anchor, not garment surface';
  if(items.includes(item)){
   const part=D.HeroAsset.parts.find(p=>p.name==='jacket');
   if(!part||part.vertices<26697)throw new Error('Missing jacket reference triangle');
   const bytes=Uint8Array.from(atob(part.data),c=>c.charCodeAt(0)),v=new DataView(bytes.buffer),dq=D.DualQuaternion.pack(pose.matrices),a=sim.appearance||D.Appearance.default();
   const expected=[[.0561,1.455,.0867],[.0584,1.463,.0807],[.0434,1.4566,.0884]],patch=[];
   for(let i=26694;i<26697;i++){
    const b=i*24,p=[0,2,4].map(k=>v.getInt16(b+k,true)/1e4),j=[16,17,18,19].map(k=>bytes[b+k]),w=[20,21,22,23].map(k=>bytes[b+k]/255);
    if(distance(p,expected[i-26694])>1e-6||j[0]!==R.ids.chest||w[0]!==1)throw new Error('Jacket reference triangle changed');
    patch.push(world(D.DualQuaternion.transform(dq,D.CharacterFit.point(D.Appearance.shapePoint(p,part.material,a.build,a.face,a.neck||0),mount.neckDrop),j,w)));
   }
   shoulderTarget=[0,1,2].map(k=>patch.reduce((sum,p)=>sum+p[k],0)/3);
   const origin=mount.point(0,0,0),local=[[1,0,0],[0,1,0]].map(p=>D.dot(sub(shoulderTarget,origin),mount.direction(p)));
   const lift=item==='sniper'?.0595:0;
   stock=mount.point(D.clamp(local[0],-.026,.026),D.clamp(local[1],-.114+lift,-.035+lift),ref.stock[2]);
   shoulderReference='rendered jacket triangle 8898';
  }
  if(![eye,rear,front,stock,shoulderTarget].every(vector)||distance(front,rear)<1e-6)
   throw new Error('Nonfinite or degenerate rendered landmarks');
  const axis=D.normalize(sub(front,rear)),delta=sub(eye,rear),along=D.dot(delta,axis),eyeOffset=sub(delta,axis.map(v=>v*along));
  const palmErrors={},segmentErrors={};
  for(const side of ['L','R']){
   if(!mount.palmContacts?.[side])throw new Error('Missing rendered palm reference');
   palmErrors[side]=distance(xyz(R.palmPoint(pose,actor,side)),xyz(mount.palmContacts[side]));
   for(const [label,a,b] of [['upper','upperArm','forearm'],['lower','forearm','hand']]){
    const first=a+side,last=b+side,expected=distance(R.bones[R.ids[first]][2],R.bones[R.ids[last]][2])*pose.scale;
    segmentErrors[label+side]=Math.abs(distance(joint(first),joint(last))-expected);
   }
  }
  if(![...Object.values(palmErrors),...Object.values(segmentErrors)].every(Number.isFinite))
   throw new Error('Nonfinite contact or inter-joint measurement');
  return{item,source:rendered===undefined?'simulation':'renderer',units:'metres',reference:ref,
   shoulderReference,eye,axis,rear,front,stock,stockCenter,shoulderTarget,legacyShoulderTarget,legacyStockError,
   eyeError:Math.hypot(...eyeOffset),eyeOffset,behind:-along,stockError:distance(stock,shoulderTarget),palmErrors,segmentErrors};
 }
 function screen(v){
  const failures=[];
  const numbers=[v.eyeError,v.stockError,v.behind,...['L','R'].map(k=>v.palmErrors?.[k]),
   ...['upperL','lowerL','upperR','lowerR'].map(k=>v.segmentErrors?.[k])];
  if(!numbers.every(Number.isFinite)||numbers.some((n,i)=>i!==2&&n<0))failures.push('invalid');
  if(v.eyeError>thresholds.eye)failures.push('eye');
  if(v.stockError>thresholds.stock)failures.push('stock');
  if(v.behind<thresholds.minBehind)failures.push('sight-behind');
  if(Object.values(v.palmErrors||{}).some(n=>n>thresholds.palm))failures.push('palms');
  if(Object.values(v.segmentErrors||{}).some(n=>n>thresholds.limb))failures.push('limb-length');
  return{status:failures.length?'needs-coordination':'screened',failures,thresholds,
   artisticAcceptance:false,note:'Diagnostic screening only; surface contact and motion still require review.'};
 }
 function translateToEye(v){
  const translation=v.eyeOffset.slice(),rear=add(v.rear,translation),stock=add(v.stock,translation);
  const delta=sub(v.eye,rear),along=D.dot(delta,v.axis);
  return{counterfactual:true,translation,stock,stockError:distance(stock,v.shoulderTarget),
   eyeError:Math.hypot(...sub(delta,v.axis.map(x=>x*along))),
   note:'Rigid translation algebra only. No re-solved arms, rendered correction or gameplay change.'};
 }
 global.DC_LONGARM_QA=Object.freeze({items,thresholds,landmarks,inspect,screen,translateToEye});
})(globalThis);
