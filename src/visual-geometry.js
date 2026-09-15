/* Shared original metric recipes also used to author the Higgsfield scene.
   Runtime uses no external geometry library. All arrays are deterministic. */
'use strict';
(function(D){
 function build(){
  const result={};
  function surface(name,points,faces){
   const normals=points.map(()=>[0,0,0]);const tris=[];
   for(const face of faces)for(let k=1;k<face.length-1;k++){
    const idx=[face[0],face[k],face[k+1]],a=points[idx[0]],b=points[idx[1]],c=points[idx[2]],n=D.cross(b.map((v,i)=>v-a[i]),c.map((v,i)=>v-a[i]));
    if(Math.hypot(...n)<1e-9)continue;tris.push(idx);for(const j of idx)for(let t=0;t<3;t++)normals[j][t]+=n[t];
   }
   normals.forEach((n,i)=>normals[i]=D.normalize(n));const data=[];
   for(const tri of tris)for(const i of tri)data.push(...points[i],...normals[i],points[i][0]*.5+.5,points[i][1]*.5+.5);
   result[name]=data;return data;
  }
  function radial(name,profile,segments=40){
   const points=[],faces=[];
   for(const [x,r] of profile)for(let i=0;i<segments;i++){const a=i/segments*Math.PI*2;points.push([x,Math.sin(a)*r,Math.cos(a)*r]);}
   for(let j=0;j<profile.length-1;j++)for(let i=0;i<segments;i++)faces.push([j*segments+i,(j+1)*segments+i,(j+1)*segments+(i+1)%segments,j*segments+(i+1)%segments]);
   return surface(name,points,faces);
  }
  radial('tire',[[-.50,.347],[-.50,.417],[-.40,.478],[-.26,.5],[.26,.5],[.40,.478],[.50,.417],[.50,.347]]);
  radial('rim',[[-.46,.435],[-.5,.483],[-.40,.5],[.44,.5],[.50,.475],[.42,.435],[-.46,.435]]);
  const profile=[[-2.2,.73,.72,.36],[-2.06,.85,.85,.31],[-1.7,.94,.95,.28],[-1.36,.965,.99,.275],[-.92,.94,1.015,.275],[-.35,.923,1.005,.275],[.45,.932,.99,.275],[.9,.951,.975,.275],[1.36,.967,.965,.285],[1.75,.916,.91,.31],[2.06,.84,.81,.36],[2.2,.72,.70,.40]];
  function sample(z){let k=profile.findIndex((p,i)=>i<profile.length-1&&p[0]<=z&&profile[i+1][0]>=z);if(k<0)k=profile.length-2;
   const a=profile[k],b=profile[k+1],p=profile[Math.max(0,k-1)],q=profile[Math.min(profile.length-1,k+2)],u=(z-a[0])/(b[0]-a[0]),dist=b[0]-a[0];
   return [1,2,3].map(j=>(2*u*u*u-3*u*u+1)*a[j]+(u*u*u-2*u*u+u)*(b[j]-p[j])/(b[0]-p[0])*dist+(-2*u*u*u+3*u*u)*b[j]+(u*u*u-u*u)*(q[j]-a[j])/(q[0]-a[0])*dist);
  }
  const p=[],faces=[];const N=97,R=16;
  for(let k=0;k<N;k++){
   const z=-2.2+4.4*k/(N-1),[w,t,b]=sample(z),arch=Math.max(...[-1.39,1.36].map(c=>Math.abs(z-c)<.442?.365+Math.sqrt(Math.max(0,.442**2-(z-c)**2)):b));
   const side=[[0,t+.035],[.35*w,t+.029],[.68*w,t+.009],[.90*w,t-.037],[w,t-.13],[w*.998,Math.max(b+.07,arch)],[w*.87,Math.max(b,arch-.035)],[.65*w,b],[0,b-.012]];
   const ring=side.concat(side.slice(1,-1).reverse().map(([x,y])=>[-x,y]));for(const[x,y]of ring)p.push([x,y,z]);
  }
  // The winding is outward: rings were originally traversed clockwise in the authoring recipe.
  for(let j=0;j<N-1;j++)for(let i=0;i<R;i++)faces.push([j*R+i,(j+1)*R+i,(j+1)*R+(i+1)%R,j*R+(i+1)%R]);
  faces.push(Array.from({length:R},(_,i)=>i));faces.push(Array.from({length:R},(_,i)=>(N-1)*R+R-1-i));surface('coupe',p,faces);
  for(const [name,front]of [['glassFront',true],['glassRear',false]]){
   const p=[],f=[],nx=21,ny=7;for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
    const v=j/(ny-1),u=i/(nx-1)*2-1,w=.795*(1-v)+.645*v,y=1+v*.5,z=front?.98*(1-v)+.42*v:-1.39*(1-v)-.865*v,bulge=(1-u*u)*Math.sin(v*Math.PI)*.027;
    p.push([u*w,y+bulge*.3,z+(front?1:-1)*bulge]);
   }for(let j=0;j<ny-1;j++)for(let i=0;i<nx-1;i++){const a=j*nx+i;f.push(front?[a,a+1,a+1+nx,a+nx]:[a+nx,a+1+nx,a+1,a]);}surface(name,p,f);
  }
  for(const[side,name]of [[-1,'glassLeft'],[1,'glassRight']]){
   const points=[],faces=[],nx=18,ny=6;
   for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
    const v=j/(ny-1),u=i/(nx-1),x=side*(.84*(1-v)+.68*v+.008*Math.sin(u*Math.PI)*Math.sin(v*Math.PI)),y=1+v*.50;
    const back=-1.36*(1-v)-.82*v,front=.88*(1-v)+.36*v;points.push([x,y,D.lerp(back,front,u)]);
   }
   for(let j=0;j<ny-1;j++)for(let i=0;i<nx-1;i++){const a=j*nx+i;faces.push(side>0?[a,a+nx,a+nx+1,a+1]:[a+1,a+nx+1,a+nx,a]);}
   surface(name,points,faces);
  }
  {
   const points=[],faces=[],nx=24,nz=24;
   for(let j=0;j<nz;j++)for(let i=0;i<nx;i++){
    const u=i/(nx-1)*2-1,v=j/(nz-1)*2-1;
    points.push([u*.675,1.51+.055*(1-u*u)+.017*(1-v*v),-.238+v*.626]);
   }
   for(let j=0;j<nz-1;j++)for(let i=0;i<nx-1;i++){const a=j*nx+i;faces.push([a,a+nx,a+nx+1,a+1]);}surface('roof',points,faces);
  }
  // Tree mesh: hierarchical tapering branches, root flare, actual leaves instead of solid spheres.
  const trunkP=[],trunkF=[],leafP=[],leafF=[];const random=D.rng(52455);
  function branch(a,b,r0,r1){
   const axis=D.normalize(b.map((v,i)=>v-a[i])),u=D.normalize(D.cross(axis,Math.abs(axis[1])>.9?[1,0,0]:[0,1,0])),v=D.cross(axis,u),start=trunkP.length,n=9;
   for(let k=0;k<4;k++)for(let j=0;j<n;j++){const t=k/3,q=j/n*Math.PI*2,r=D.lerp(r0,r1,t)*(1+Math.sin(j*2.2)*.10);trunkP.push(a.map((x,i)=>D.lerp(x,b[i],t)+(u[i]*Math.cos(q)+v[i]*Math.sin(q))*r));}
   for(let k=0;k<3;k++)for(let j=0;j<n;j++)trunkF.push([start+k*n+j,start+k*n+(j+1)%n,start+(k+1)*n+(j+1)%n,start+(k+1)*n+j]);
  }
  branch([0,0,0],[.06,3.7,.025],.19,.058);
  for(let i=0;i<6;i++){const a=i*Math.PI/3;branch([0,.34,0],[Math.cos(a)*.5,.02,Math.sin(a)*.5],.10,.018);}
  for(let i=0;i<15;i++){
   const a=i*2.399,level=2.20+(i%5)*.41,len=1.20+(i%3)*.24;
   const from=[.03,level,0],end=[Math.cos(a)*len,level+.8+random()*.25,Math.sin(a)*len];branch(from,end,.07,.022);
   for(let t=0;t<3;t++){
    const an=a+(t-1)*.7,tip=[end[0]+Math.cos(an)*.63,end[1]+.46+random()*.33,end[2]+Math.sin(an)*.63];branch(end,tip,.026,.005);
    for(let k=0;k<29;k++){
     const cx=tip[0]+(random()-.5)*1.10,cy=tip[1]+(random()-.5)*.7,cz=tip[2]+(random()-.5)*1.10;
     const yaw=random()*Math.PI*2,len=.26+random()*.24,width=len*.52,lift=(random()-.5)*.16,si=Math.sin(yaw),co=Math.cos(yaw),id=leafP.length;
     // A folded diamond leaf has visible thickness/readable edges without alpha overdraw.
     const points=[[0,0,-len/2],[-width/2,lift,0],[0,.035,0],[width/2,lift,0],[0,0,len/2]];
     for(const[x,y,z]of points)leafP.push([cx+x*co+z*si,cy+y,cz-x*si+z*co]);
     leafF.push([id,id+1,id+2],[id,id+2,id+3],[id+1,id+4,id+2],[id+2,id+4,id+3]);
    }
   }
  }
  // Force radial branch normals outward. Geometry is shared for all instances.
  surface('treeWood',trunkP,trunkF);surface('treeLeaves',leafP,leafF);
  result.treeWoodLow=[];for(let i=0;i<67;i++)if(i<7||(i-7)%4===0)result.treeWoodLow.push(...result.treeWood.slice(i*1296,(i+1)*1296));
  result.treeLeavesLow=[];for(let i=0;i<result.treeLeaves.length;i+=96*3)result.treeLeavesLow.push(...result.treeLeaves.slice(i,i+96));
  // Metallic lamp mast: true tapered cylinder rather than a four-sided stick.
  const lp=[],lf=[];for(let j=0;j<4;j++){const y=[0,.18,.55,7.2][j],r=[.13,.13,.078,.054][j];for(let i=0;i<16;i++){const a=i*Math.PI/8;lp.push([Math.cos(a)*r,y,Math.sin(a)*r]);}}
  for(let j=0;j<3;j++)for(let i=0;i<16;i++)lf.push([j*16+i,(j+1)*16+i,(j+1)*16+(i+1)%16,j*16+(i+1)%16]);surface('lampMast',lp,lf);
  return result;
 }
 D.VisualGeometry={build};
})(DC);
