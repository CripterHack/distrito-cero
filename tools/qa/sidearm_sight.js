/* QA-only: actual sclera bounds and visible prop sight surfaces, independent of
   the runtime's authored landmark constants. This is a game-art measurement. */
(function(global){
 'use strict'; const D=global.DC,R=D.SkinRig;
 const part=D.HeroAsset.parts.find(p=>p.name==='eye');
 const raw=Uint8Array.from(atob(part.data),c=>c.charCodeAt(0)),view=new DataView(raw.buffer);
 const points=[];for(let i=0;i<part.vertices;i++){const p=[0,2,4].map(k=>view.getInt16(i*24+k,true)/1e4);if(p[0]>0)points.push(p);}
 if(!points.length)throw new Error('Missing right sclera');
 const eyeBind=[0,1,2].map(k=>(Math.min(...points.map(p=>p[k]))+Math.max(...points.map(p=>p[k])))/2);
 const xyz=p=>[p.x,p.y,p.z],sub=(a,b)=>a.map((v,i)=>v-b[i]);
 function scene(id='pistol') {const s=new D.Simulation(new D.World(1337));Object.assign(s.player,{x:0,z:0,yaw:0,car:null});s.time=1.25;Object.assign(s.equipment,{selected:id,aimWeight:1});return s;}
 function inspect(s,rendered=null){
  const m=rendered?.mount||D.Equipment.mount(s),n=D.WeaponHandling.actor(s.player,m,s.equipment),q=rendered?.pose||R.pose(n,s.time);
  const fit=D.CharacterFit.point(eyeBind,m.neckDrop),at=R.transform(q.matrices.subarray(R.ids.head*16,R.ids.head*16+16),fit),c=Math.cos(s.player.yaw),sn=Math.sin(s.player.yaw);
  const eye=[s.player.x+at[0]*c+at[2]*sn,q.rootY+at[1],s.player.z-at[0]*sn+at[2]*c];
  // Centres of top faces from the existing rear/front box dimensions.
  const rear=m.point(0,.061+.025/2,-.01),front=m.point(0,.062+.035/2,.22),axis=D.normalize(sub(front,rear)),delta=sub(eye,rear),along=D.dot(delta,axis);
  const miss=sub(delta,axis.map(v=>v*along));
  return{eyeBind,eye,rear,front,error:Math.hypot(...miss),behind:-along,origin:m.origin,contacts:Object.fromEntries(Object.keys(m.hands).map(k=>[k,Math.hypot(...sub(xyz(R.palmPoint(q,n,k)),xyz(m.palmContacts[k])))]))};
 }
 global.DC_SIDEARM_SIGHT_QA={scene,inspect,eyeBind};
})(globalThis);
