/* Distrito Cero — native runtime. All distances are metres; Y is up, +Z forward. */
'use strict';
var DC = globalThis.DC = globalThis.DC || {};
(function(D){
 D.clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
 D.lerp=(a,b,t)=>a+(b-a)*t;
 D.damp=(a,b,k,dt)=>D.lerp(a,b,1-Math.exp(-k*dt));
 D.wrap=a=>Math.atan2(Math.sin(a),Math.cos(a));
 D.turn=(a,b,max)=>a+D.clamp(D.wrap(b-a),-max,max);
 D.distance=(a,b)=>Math.hypot(a.x-b.x,a.z-b.z);
 D.mapProject=(x,z,cx,cz,w,h,scale)=>[w/2-(x-cx)*scale,h/2-(z-cz)*scale];
 D.mapUnproject=(x,y,cx,cz,w,h,scale)=>({x:cx-(x-w/2)/scale,z:cz-(y-h/2)/scale});
 D.rng=function(seed){let a=seed|0;return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};};
 D.circleBox=function(x,z,r,b){let qx=D.clamp(x,b.x-b.w/2,b.x+b.w/2),qz=D.clamp(z,b.z-b.d/2,b.z+b.d/2);return (x-qx)**2+(z-qz)**2<r*r;};
 D.moveCircle=function(x,z,dx,dz,r,boxes){
  const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/Math.max(.4,r*.75)));let hit=false;
  for(let i=0;i<steps;i++){
   let nx=x+dx/steps;if(!boxes.some(b=>D.circleBox(nx,z,r,b)))x=nx;else hit=true;
   let nz=z+dz/steps;if(!boxes.some(b=>D.circleBox(x,nz,r,b)))z=nz;else hit=true;
  }
  return{x,z,hit};
 };
 D.segmentBox=function(ax,az,bx,bz,b,pad=0){
  let lo=0,hi=1,dx=bx-ax,dz=bz-az;
  for(const [p,q] of [[-dx,ax-(b.x-b.w/2-pad)],[dx,b.x+b.w/2+pad-ax],[-dz,az-(b.z-b.d/2-pad)],[dz,b.z+b.d/2+pad-az]]){
   if(Math.abs(p)<1e-8){if(q<0)return false;}else{let t=q/p;if(p<0)lo=Math.max(lo,t);else hi=Math.min(hi,t);if(lo>hi)return false;}
  }
  return true;
 };
 D.M4={
  identity:()=>new Float32Array([1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]),
  multiply(a,b){let o=new Float32Array(16);for(let c=0;c<4;c++)for(let r=0;r<4;r++)o[c*4+r]=a[r]*b[c*4]+a[4+r]*b[c*4+1]+a[8+r]*b[c*4+2]+a[12+r]*b[c*4+3];return o;},
  perspective(fov,aspect,near,far){let f=1/Math.tan(fov/2),nf=1/(near-far);return new Float32Array([f/aspect,0,0,0,0,f,0,0,0,0,(far+near)*nf,-1,0,0,2*far*near*nf,0]);},
  ortho(l,r,b,t,n,f){return new Float32Array([2/(r-l),0,0,0,0,2/(t-b),0,0,0,0,-2/(f-n),0,-(r+l)/(r-l),-(t+b)/(t-b),-(f+n)/(f-n),1]);},
  lookAt(eye,target,up=[0,1,0]){let z=D.normalize(eye.map((v,i)=>v-target[i])),x=D.normalize(D.cross(up,z)),y=D.cross(z,x);return new Float32Array([x[0],y[0],z[0],0,x[1],y[1],z[1],0,x[2],y[2],z[2],0,-D.dot(x,eye),-D.dot(y,eye),-D.dot(z,eye),1]);},
  project(m,p){let x=p[0],y=p[1],z=p[2],w=m[3]*x+m[7]*y+m[11]*z+m[15];return[(m[0]*x+m[4]*y+m[8]*z+m[12])/w,(m[1]*x+m[5]*y+m[9]*z+m[13])/w,(m[2]*x+m[6]*y+m[10]*z+m[14])/w,w];}
 };
 D.dot=(a,b)=>a[0]*b[0]+a[1]*b[1]+a[2]*b[2];
 D.cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 D.normalize=a=>{let n=Math.hypot(...a)||1;return a.map(x=>x/n);};
 D.humanoidPose=function({phase=0,speed=0,sprint=0,y=0,vy=0,turn=0,time=0,landing=0}={}){
  const move=D.clamp(speed/3.3,0,1),run=D.clamp(sprint,0,1),airborne=y>.035||Math.abs(vy)>.05?1:0;
  const stride=(.36+run*.34)*move*(1-airborne),cycle=Math.sin(phase),cycle2=Math.sin(phase+Math.PI),lift=(1-Math.cos(phase*2))*.5;
  const idle=(1-move)*(1-airborne),breath=Math.sin(time*1.65)*.008*idle;
  const crouch=airborne*D.clamp(.18-Math.abs(vy)*.012,.06,.18)+landing*.10;
  const pelvisYaw=cycle*stride*.16,shoulderYaw=-pelvisYaw*.82;
  const turnLean=D.clamp(turn,-1,1)*(.09+.04*run)*(move*.75+.25);
  const hipBob=(Math.abs(cycle)*.035*move+lift*.014*run)*(1-airborne)-crouch*.08+breath;
  const kneeBase=airborne?D.clamp(.42-vy*.025,.22,.55):.05;
  const leftHip=airborne?D.clamp(-.12-vy*.025,-.28,.03):cycle*stride;
  const rightHip=airborne?D.clamp(.06-vy*.018,-.12,.18):cycle2*stride;
  const leftKnee=kneeBase+(airborne?.18:Math.max(0,-cycle)*(.34+.32*run)*move);
  const rightKnee=kneeBase+(airborne?.20:Math.max(0,-cycle2)*(.34+.32*run)*move);
  const armAmp=(.30+run*.48)*move*(1-airborne);
  const leftShoulder=airborne?-.22:cycle2*armAmp;
  const rightShoulder=airborne?-.18:cycle*armAmp;
  const elbow=.08+run*.18*move+airborne*.34;
  return{
   airborne,hipBob,pelvisYaw,shoulderYaw,
   spinePitch:run*.075*move+airborne*.055-crouch*.14,
   spineRoll:-turnLean,
   headYaw:D.clamp(turn,-1,1)*.11,
   headPitch:-run*.025*move-airborne*.035,
   pelvisRoll:turnLean*.32,
   left:{hip:leftHip,knee:leftKnee,ankle:-leftKnee*.32,shoulder:leftShoulder,elbow:elbow+(cycle>0?.03:0)},
   right:{hip:rightHip,knee:rightKnee,ankle:-rightKnee*.32,shoulder:rightShoulder,elbow:elbow+(cycle<0?.03:0)}
  };
 };
 D.stories=[
  {name:'LA LLAMADA',label:'Contesta el teléfono de Lía.',x:13,z:20,foot:true,button:'Contestar la llamada'},
  {name:'MOTOR FRÍO',label:'Consigue un vehículo. El coupé te está esperando.',x:5,z:11,button:'Subir al vehículo'},
  {name:'CARGA SENSIBLE',label:'Recoge el archivo en el taller del Mercado.',x:168,z:96,foot:true,button:'Recoger el archivo'},
  {name:'FUERA DEL RADAR',label:'Pierde a la policía y llega al refugio de Lía.',x:-84,z:264,foot:true,button:'Entrar al refugio'},
  {name:'LA FRECUENCIA',label:'Transmite el archivo desde la terminal de Vértice.',x:252,z:-72,foot:true,button:'Iniciar la transmisión'},
  {name:'ÚLTIMA SALIDA',label:'Pierde a la policía. Reúnete con Lía en el muelle.',x:-252,z:-156,foot:true,button:'Decidir el destino del archivo'}
 ];
})(DC);
