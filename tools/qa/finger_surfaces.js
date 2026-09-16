/* Development-only audit: actual quantized skin, independent prop envelopes. Not bundled. */
(function(global){
'use strict';
const D=global.DC,R=D.SkinRig;
function shapeSDF(p,shape){
 const c=shape.p,x=p[0]-c[0],y=p[1]-c[1],z=p[2]-c[2];
 if(shape.kind==='box'){const q=[x,y,z].map((v,i)=>Math.abs(v)-shape.s[i]/2);return Math.hypot(...q.map(v=>Math.max(v,0)))+Math.min(Math.max(...q),0);}
 let taper=1;const h=shape.s[1],v=Math.abs(y/h);if(v>.44)taper=.96-(Math.min(.5,v)-.44)/.06*.18;else taper=1-v/.44*.04;
 const a=shape.s[0]*taper/2,b=shape.s[2]*taper/2,k0=Math.hypot(x/a,z/b),k1=Math.hypot(x/a/a,z/b/b),cross=k1>1e-8?k0*(k0-1)/k1:-Math.min(a,b),cap=Math.abs(y)-h/2;
 return Math.hypot(Math.max(cross,0),Math.max(cap,0))+Math.min(Math.max(cross,cap),0);
}
const shapes={grip:{kind:'grip',p:[0,-.11,-.016],s:[.060,.17,.08]},fore:{kind:'box',p:[0,-.005,.31],s:[.09,.08,.20]},magazine:{kind:'box',p:[0,-.135,.12],s:[.058,.18,.095]},pistolMagazine:{kind:'box',p:[0,-.18,-.016],s:[.056,.08,.072]}};
const part=D.HeroAsset.parts.find(p=>p.name==='skin'),raw=Uint8Array.from(atob(part.data),c=>c.charCodeAt(0)),view=new DataView(raw.buffer),samples={};
for(const side of['L','R'])for(const f of R.fingers[side]){
 const ix=f.bones.map(n=>R.ids[n]),out=[],seen=new Set();for(let i=0;i<part.vertices;i++){const b=i*24,j=[16,17,18,19].map(k=>raw[b+k]),w=[20,21,22,23].map(k=>raw[b+k]/255);if(w.reduce((s,v,k)=>s+(ix.includes(j[k])?v:0),0)<.75)continue;
 const p=[0,2,4].map(k=>view.getInt16(b+k,true)/1e4),key=p.join();if(seen.has(key))continue;seen.add(key);out.push({p,j,w});}
 samples[side+f.name]=out;
}
function toLocal(q,m,v,dq,n){let p=D.DualQuaternion.transform(dq,v.p,v.j,v.w);const c=Math.cos(n.yaw||0),sn=Math.sin(n.yaw||0);p=[(n.x||0)+p[0]*c+p[2]*sn,p[1]+q.rootY,(n.z||0)-p[0]*sn+p[2]*c];p=p.map((v,i)=>v-m.origin[i]);return [[1,0,0],[0,1,0],[0,0,1]].map(x=>D.dot(p,m.direction(x)));}
function stats(s,k,name,key,rendered=null){const m=rendered?.mount||D.Equipment.mount(s),n=s.player,q=rendered?.pose||R.pose(D.WeaponHandling.actor(n,m,s.equipment),s.time),dq=D.DualQuaternion.pack(q.matrices);let min=Infinity,worst;
 for(const v of samples[k+name]){let p=toLocal(q,m,v,dq,n);if(key.includes('Magazine')||key==='magazine'){const o=m.magazine.offset,t=m.magazine.rotation[2],pi=m.magazine.pivot;p=p.map((v,i)=>v-o[i]-pi[i]);p=[p[0]*Math.cos(t)+p[1]*Math.sin(t),-p[0]*Math.sin(t)+p[1]*Math.cos(t),p[2]].map((v,i)=>v+pi[i]);}const d=shapeSDF(p,shapes[key]);if(d<min){min=d;worst=p;}}
 return{min:+min.toFixed(6),worst:worst?.map(v=>+v.toFixed(5)),samples:samples[k+name].length};}
global.DC_FINGER_QA={D,R,samples,shapeSDF,shapes,stats};

})(globalThis);
