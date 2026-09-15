'use strict';
(function(D){
 const VS=`#version 300 es
 precision highp float;
 layout(location=0) in vec3 aPosition; layout(location=1) in vec3 aNormal; layout(location=2) in vec2 aUV;
 layout(location=3) in vec4 iPosition; layout(location=4) in vec4 iScale; layout(location=5) in vec4 iColor; layout(location=6) in vec4 iExtra;
 layout(location=7) in vec4 aJoints;layout(location=8) in vec4 aWeights;
 uniform int uSkinned;uniform mat4 uBones[${D.SkinRig.bones.length}];uniform sampler2D uCrowdBones;uniform sampler2D uCharacterLooks;uniform sampler2D uCrowdDuals;uniform float uTime;
 uniform mat4 uVP; uniform mat4 uLightVP; uniform mat4 uReflectVP; uniform vec3 uChunkOffset;
 flat out vec4 vTraits;flat out vec4 vLook;out vec3 vSurface;out vec3 vWorld; out vec3 vNormal; out vec3 vLocal; out vec3 vFace; out vec2 vUV; out vec4 vColor;
 out vec4 vShadow; out vec4 vReflection; flat out int vMaterial; flat out float vSeed; flat out float vDetail;
 mat4 crowdBone(int joint){int row=clamp(int(iExtra.w+.5)-200,0,127),x=joint*4;return mat4(texelFetch(uCrowdBones,ivec2(x,row),0),texelFetch(uCrowdBones,ivec2(x+1,row),0),texelFetch(uCrowdBones,ivec2(x+2,row),0),texelFetch(uCrowdBones,ivec2(x+3,row),0));}
 vec3 rotateQuaternion(vec4 r,vec3 p){return p+2.*cross(r.xyz,cross(r.xyz,p)+r.w*p);}
 void deformDual(inout vec3 p,inout vec3 n){
  int row=clamp(int(iExtra.w+.5)-200,0,127);
  vec4 reference=texelFetch(uCrowdDuals,ivec2(int(aJoints.x)*2,row),0);
  vec4 realQ=vec4(0.),dualQ=vec4(0.);
  for(int j=0;j<4;j++){
   int x=int(aJoints[j])*2;vec4 r=texelFetch(uCrowdDuals,ivec2(x,row),0),d=texelFetch(uCrowdDuals,ivec2(x+1,row),0);
   float weight=aWeights[j]*(dot(reference,r)<0.?-1.:1.);realQ+=r*weight;dualQ+=d*weight;
  }
  float l=max(length(realQ),1e-8);realQ/=l;dualQ/=l;dualQ-=realQ*dot(realQ,dualQ);
  vec3 translation=2.*(realQ.w*dualQ.xyz-dualQ.w*realQ.xyz+cross(realQ.xyz,dualQ.xyz));
  p=rotateQuaternion(realQ,p)+translation;n=normalize(rotateQuaternion(realQ,n));
 }
 float fittedNeckWeight(float y){float t=clamp(y-1.447,0.,.103);return t<.008?t*t/(2.*.008*.095):t>.095?1.-(.103-t)*(.103-t)/(2.*.008*.095):(t-.004)/.095;}
 float fittedNeckSlope(float y){float t=y-1.447;return t<=0.||t>=.103?0.:t<.008?t/(.008*.095):t>.095?(.103-t)/(.008*.095):1./.095;}
 // Exact Jacobian of the constitution morph, including the neckline transition.
 // A reciprocal uniform scale is insufficient where body/arm masks vary with height.
 float shapeSlope(float a,float b,float x){float t=clamp((x-a)/(b-a),0.,1.);return 6.*t*(1.-t)/(b-a);}
 void morphConstitution(inout vec3 p,inout vec3 n,float amount){
  if(abs(amount)<.000001)return;
  float b0=smoothstep(.91,.98,p.y),b1=smoothstep(1.40,1.49,p.y),body=b0*(1.-b1);
  float by=shapeSlope(.91,.98,p.y)*(1.-b1)-b0*shapeSlope(1.40,1.49,p.y);
  float l0=smoothstep(.79,.91,p.y),l1=smoothstep(.10,.24,p.y),leg=(1.-l0)*l1;
  float ly=-shapeSlope(.79,.91,p.y)*l1+(1.-l0)*shapeSlope(.10,.24,p.y);
  float ax=smoothstep(.17,.235,abs(p.x)),a0=smoothstep(.92,1.01,p.y),a1=smoothstep(1.40,1.45,p.y);
  float arm=ax*a0*(1.-a1),armX=shapeSlope(.17,.235,abs(p.x))*sign(p.x)*a0*(1.-a1);
  float armY=ax*(shapeSlope(.92,1.01,p.y)*(1.-a1)-a0*shapeSlope(1.40,1.45,p.y));
  float anchor=.2637-(p.y-.885)*.072,sg=sign(p.x),center=(arm*anchor+leg*.108)*sg;
  float centerX=armX*anchor*sg,centerY=(armY*anchor-arm*.072+ly*.108)*sg;
  float xs=1.+amount*(body*.14*(1.-arm)+arm*.13+leg*.13),zs=1.+amount*(body*.18+leg*.13);
  float xsX=amount*(.13-body*.14)*armX,xsY=amount*(by*.14*(1.-arm)+(.13-body*.14)*armY+ly*.13);
  float zsY=amount*(by*.18+ly*.13),e=exp(-pow((p.y-1.10)/.12,2.));
  float shift=amount*.006*body*e,shiftY=amount*.006*e*(by-body*2.*(p.y-1.10)/(.12*.12));
  vec3 colX=vec3(xs+(p.x-center)*xsX+centerX*(1.-xs),0.,0.);
  vec3 colY=vec3((p.x-center)*xsY+centerY*(1.-xs),1.,p.z*zsY+shiftY),colZ=vec3(0.,0.,zs);
  n=normalize(cross(colY,colZ)*n.x+cross(colZ,colX)*n.y+cross(colX,colY)*n.z);
  p.x=center+(p.x-center)*xs;p.z=p.z*zs+shift;
 }
 // Neck and neckline share a deformation mask. Jacobian cofactors preserve normals
 // across tapering transitions, rather than treating the whole neck as one scale.
 float cervicalMask(vec3 p,int material){
  float mask=smoothstep(1.446,1.482,p.y)*(1.-smoothstep(1.560,1.615,p.y));
  float jaw=smoothstep(.035,.092,p.z)*smoothstep(1.530,1.549,p.y);
  if(material==40)return mask*(1.-jaw);
  return mask*(1.-smoothstep(.095,.145,abs(p.x)))*(1.-smoothstep(.092,.140,abs(p.z+.010)));
 }
 void morphCervical(inout vec3 p,inout vec3 n,int material,float amount){
  if(abs(amount)<.00001||p.y<1.445||p.y>1.616)return;
  float k=amount,e=.0003,mask=cervicalMask(p,material),scale=1.+k*mask;
  vec3 grad=vec3(cervicalMask(p+vec3(e,0,0),material)-cervicalMask(p-vec3(e,0,0),material),cervicalMask(p+vec3(0,e,0),material)-cervicalMask(p-vec3(0,e,0),material),cervicalMask(p+vec3(0,0,e),material)-cervicalMask(p-vec3(0,0,e),material))*k/(2.*e);
  vec3 colX=vec3(scale+p.x*grad.x,0.,(p.z+.010)*grad.x),colY=vec3(p.x*grad.y,1.,(p.z+.010)*grad.y),colZ=vec3(p.x*grad.z,0.,scale+(p.z+.010)*grad.z);
  n=normalize(cross(colY,colZ)*n.x+cross(colZ,colX)*n.y+cross(colX,colY)*n.z);
  p.x*=scale;p.z=-.010+(p.z+.010)*scale;
 }
 void main(){
  float c=cos(iPosition.w),s=sin(iPosition.w),cx=cos(iExtra.x),sx=sin(iExtra.x),cz=cos(iExtra.y),sz=sin(iExtra.y);
  mat3 ry=mat3(c,0.,-s,0.,1.,0.,s,0.,c);mat3 rx=mat3(1.,0.,0.,0.,cx,sx,0.,-sx,cx);mat3 rz=mat3(cz,sz,0.,-sz,cz,0.,0.,0.,1.);
  mat3 rot=ry*rz*rx;vec3 position=aPosition,normal=aNormal;
  vSurface=position;vLook=vec4(0.);vTraits=vec4(0.);
  if(uSkinned>0){
   int lookRow=uSkinned==2?clamp(int(iExtra.w+.5)-200,0,127):0;
   vLook=texelFetch(uCharacterLooks,ivec2(0,lookRow),0);
   if(uSkinned==2)vTraits=texelFetch(uCharacterLooks,ivec2(1,lookRow),0);

   // Bind-space eyelids close over spherical eyes; shadow and color share lid geometry.
   float phase=mod(uTime+iExtra.z*7.31,3.7+iExtra.z*.8),blink=0.;
   if(phase<.17){float f=1.-abs(phase-.085)/.085;blink=f*f*(3.-2.*f);}
   int humanMaterial=int(iScale.w);
   if(int(aJoints.x)==4&&humanMaterial==40&&position.z>.079){
    float mask=(1.-smoothstep(.012,.019,abs(abs(position.x)-.0307781)))*(1.-smoothstep(.008,.018,abs(position.y-1.6708135)));
    float squeeze=1.-blink*.93*mask;position.y=1.6708135+(position.y-1.6708135)*squeeze;normal=normalize(vec3(normal.x,normal.y/max(squeeze,.08),normal.z));
   }
   // Bound visual volume only. Segment lengths and hand/sole contacts remain unchanged.
   if(humanMaterial==31||humanMaterial==32||humanMaterial==3)morphConstitution(position,normal,vLook.x);
   if(humanMaterial==40||humanMaterial==31)morphCervical(position,normal,humanMaterial,vLook.w*.09+vLook.x*.055);
   if(humanMaterial==40){float jaw=exp(-pow((position.y-1.60)/.043,2.));float xs=1.+vLook.y*.075*jaw;position.x*=xs;normal.x/=xs;position.z+=exp(-pow(position.x/.019,2.)-pow((position.y-1.645)/.029,2.))*vLook.y*.002;}
   if((humanMaterial==46||humanMaterial==47)&&vLook.z!=1.){
    float vol=vTraits.y,sc=1.+vol*.018,dy=vol*.009*shapeSlope(1.68,1.77,position.y);
    normal=normalize(vec3(normal.x/sc,normal.y/(1.+dy),normal.z/sc));
    position.x*=sc;position.z=-.012+(position.z+.012)*sc;position.y+=vol*.009*smoothstep(1.68,1.77,position.y);
   }
   // Low-amplitude gaze on the iris/pupil only; sclera and lid geometry stay anchored.
   if(int(aJoints.x)==4&&(humanMaterial==41||(humanMaterial==34&&dot(iColor.rgb,vec3(1.))<.12))){float gt=(uTime+iExtra.z*7.)/2.4,cell=floor(gt),fade=smoothstep(0.,.075,fract(gt));vec2 from=vec2(sin((cell-1.)*12.71+iExtra.z*4.3),cos((cell-1.)*7.91+iExtra.z*5.6)),to=vec2(sin(cell*12.71+iExtra.z*4.3),cos(cell*7.91+iExtra.z*5.6));position.xy+=mix(from,to,fade)*vec2(.001,.00045);}
   if(uSkinned==2){
    float drop=.045-clamp(vTraits.x,-1.,1.)*.012;
    bool hairPart=humanMaterial==46||humanMaterial==47;
    float w=hairPart?1.:fittedNeckWeight(position.y),slope=hairPart?0.:fittedNeckSlope(position.y);
    normal=normalize(vec3(normal.x,normal.y/max(.1,1.-drop*slope),normal.z));position.y-=drop*w;
    deformDual(position,normal);
   }
   else{mat4 skin=uBones[int(aJoints.x)]*aWeights.x+uBones[int(aJoints.y)]*aWeights.y+uBones[int(aJoints.z)]*aWeights.z+uBones[int(aJoints.w)]*aWeights.w;position=(skin*vec4(position,1.)).xyz;normal=normalize(mat3(skin)*normal);}
  }
  if(int(iScale.w+.1)==36){float wind=sin(uTime*1.18+iPosition.x*.31+iPosition.z*.22+position.y*.85);position.x+=wind*.025*max(position.y-2.,0.);position.z+=sin(uTime*.91+position.x*2.4)*.018*max(position.y-2.,0.);}
  vLocal=position*iScale.xyz;
  if(iExtra.w>=100.&&iExtra.w<=103.){
   float d=iExtra.z;int side=int(iExtra.w-100.+.1);float f=0.;
   if(side==0||side==1){float signZ=side==0?1.:-1.;f=smoothstep(.45,2.16,vLocal.z*signZ);vLocal.z-=signZ*f*d*.54;}
   else{float signX=side==2?-1.:1.;f=smoothstep(.28,.95,vLocal.x*signX);vLocal.x-=signX*f*d*.17;}
   vLocal.y+=f*d*(sin(vLocal.x*13.+vLocal.z*8.)*.055-.04);
  }
  vWorld=rot*vLocal+iPosition.xyz+uChunkOffset;
  vNormal=normalize(rot*(normal/max(iScale.xyz,vec3(.001))));vFace=normal;vUV=aUV;vColor=iColor;
  vMaterial=int(iScale.w+.1);vSeed=iExtra.z;vDetail=iExtra.w;vShadow=uLightVP*vec4(vWorld,1.);vReflection=uReflectVP*vec4(vWorld,1.);
  gl_Position=uVP*vec4(vWorld,1.);
 }`;
 const FS=`#version 300 es
 precision highp float;
 flat in vec4 vTraits;flat in vec4 vLook;in vec3 vSurface;in vec3 vWorld;in vec3 vNormal;in vec3 vLocal;in vec3 vFace;in vec2 vUV;in vec4 vColor;in vec4 vShadow;in vec4 vReflection;
 flat in int vMaterial;flat in float vSeed;flat in float vDetail;
 uniform sampler2D uSkinAlbedo;uniform sampler2D uSkinNormal;uniform sampler2D uSkinRoughness;
 uniform float uStudio;uniform float uDaylight;uniform vec3 uEye;uniform vec3 uSun;uniform vec4 uLights[12];uniform vec3 uHeadPos;uniform vec3 uHeadDir;
 uniform sampler2D uShadow;uniform sampler2D uReflection;uniform sampler2D uSigns;uniform float uTime;uniform float uRain;uniform float uShadowTexel;uniform int uPass;uniform int uShadows;uniform int uLightCount;
 out vec4 frag;
 float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
 vec3 unpack(vec3 c){return min(c/max(vec3(.012),1.-c),vec3(16.));}
 float shadow(vec3 n){
  if(uShadows==0)return 1.;vec3 p=vShadow.xyz/vShadow.w*.5+.5;
  if(p.x<.002||p.y<.002||p.x>.998||p.y>.998||p.z>1.)return 1.;
  float bias=max(.0009,.002*(1.-dot(n,uSun))),sum=0.;
  for(int x=-1;x<=1;x++)for(int y=-1;y<=1;y++){float depth=texture(uShadow,p.xy+vec2(x,y)*uShadowTexel).r;sum+=p.z-bias<=depth?1.:.2;}
  return sum/9.;
 }
 vec3 brdf(vec3 n,vec3 v,vec3 l,vec3 albedo,float rough,float metal){
  float nl=max(dot(n,l),0.),nv=max(dot(n,v),.025);vec3 h=normalize(v+l);
  float nh=max(dot(n,h),0.),vh=max(dot(v,h),0.),a=max(.045,rough*rough),a2=a*a;
  float den=nh*nh*(a2-1.)+1.;float d=a2/max(3.141593*den*den,.00001);
  float k=pow(rough+1.,2.)*.125;float g=(nv/(nv*(1.-k)+k))*(nl/(nl*(1.-k)+k));
  vec3 f0=mix(vec3(vMaterial==30||vMaterial==40?.028:.04),albedo,metal),f=f0+(1.-f0)*pow(1.-vh,5.);
  vec3 spec=d*g*f/max(4.*nv*nl,.001);vec3 diffuse=(1.-f)*(1.-metal)*albedo/3.141593;
  // Clearcoat is a separate restrained lobe, not increased base-color saturation.
  if(vMaterial==5){float ca=.08*.08;float cd=ca/(3.141593*pow(nh*nh*(ca-1.)+1.,2.));spec+=vec3(.04+.96*pow(1.-vh,5.))*min(cd,30.)*.13;}
  return (diffuse+min(spec,vec3(9.)))*nl;
 }
 // Surface-gradient bump uses rest-surface height with world derivatives. It stays
 // attached to skin under both skeletal rotation and character customization.
 vec3 surfaceBump(vec3 normal,float height){
  vec3 dx=dFdx(vWorld),dy=dFdy(vWorld),r1=cross(dy,normal),r2=cross(normal,dx);
  float det=dot(dx,r1);if(abs(det)<1e-12)return normal;
  return normalize(normal-sign(det)*(dFdx(height)*r1+dFdy(height)*r2)/max(abs(det),1e-12));
 }
 vec3 mappedNormal(vec3 normal,vec3 sampleNormal){
  vec3 p1=dFdx(vWorld),p2=dFdy(vWorld);vec2 t1=dFdx(vUV),t2=dFdy(vUV);
  vec3 perp2=cross(p2,normal),perp1=cross(normal,p1);
  vec3 tangent=perp2*t1.x+perp1*t2.x,bitangent=perp2*t1.y+perp1*t2.y;
  float scale=inversesqrt(max(max(dot(tangent,tangent),dot(bitangent,bitangent)),1e-12));
  return normalize(mat3(tangent*scale,bitangent*scale,normal)*sampleNormal);
 }
 void main(){
  if(uPass==1&&vWorld.y<.025)discard;
  bool groom=vMaterial==42||(vMaterial==33&&(vSurface.y>1.706||vSurface.z<.04));
  if(groom&&vMaterial==42)discard;
  if(vMaterial==46){float edge=abs(vUV.x-.5)*2.;float cut=.965-.035*sin(vUV.y*27.);if(edge>cut)discard;}
  if(vMaterial==47&&vUV.y>.963){float cov=1.-smoothstep(.963,1.,vUV.y);vec2 q=floor(vSurface.xz*4100.)+floor(vSurface.y*3600.);if(fract(sin(dot(q,vec2(127.1,311.7)))*43758.5453)>cov)discard;}
  // Render aperture removes the closed shell behind the separately articulated driver door.
  if(vMaterial==5&&vColor.a<-.04&&vSurface.x<-.65&&vSurface.y>.52&&vSurface.y<1.05&&vSurface.z>-.95&&vSurface.z<.81)discard;
  if(vMaterial==37){vec2 p=(vUV-.5)*2.;float f=1.-smoothstep(.06,1.,dot(p,p));if(f<.001)discard;frag=vec4(vColor.rgb,f*f*vColor.a);return;}
  if(vMaterial==9){
   vec2 q=(vUV-.5)*2.;float r=dot(q,q);float turbulent=noise(vUV*5.+vec2(vSeed,uTime*.18));
   float alpha=(1.-smoothstep(.05,1.,r))*(.35+turbulent*.65)*vColor.a;
   if(alpha<.008)discard;vec3 smoke=vColor.rgb*(.70+turbulent*.38);
   frag=vec4(smoke,alpha);return;
  }
  // Clip the ocular opening while lids close; the eyeball stays spherical.
  if((vMaterial==34||vMaterial==41)&&vSurface.y>1.65){float ph=mod(uTime+vSeed*7.31,3.7+vSeed*.8);float blink=0.;if(ph<.17){float t=1.-abs(ph-.085)/.085;blink=t*t*(3.-2.*t);}float dy=abs(vSurface.y-1.6708135);if(blink>.15&&dy>.0125*(1.-blink))discard;}
  vec3 n=normalize(vNormal),view=normalize(uEye-vWorld),base=vColor.rgb,emission=base*max(vColor.a,0.);float rough=.66,metal=0.;
  float grain=noise(vWorld.xz*85.)*.08;
  if(vDetail>=100.&&vDetail<=103.&&vSeed>.05){vec3 gn=normalize(cross(dFdx(vWorld),dFdy(vWorld)));if(dot(gn,n)<0.)gn=-gn;n=normalize(mix(n,gn,clamp(vSeed*.62,0.,.62)));}
  if(vMaterial==0){base*=.91+noise((vWorld.xz+vWorld.y)*12.)*.15;}
  if(vMaterial==1){
   rough=.58;vec2 uv=abs(vFace.x)>.5?vLocal.zy:vLocal.xy;bool wall=abs(vFace.y)<.5;
   if(wall){
    vec2 grid=uv*vec2(vDetail==1.? .62:.43,.34)+vSeed;vec2 f=fract(grid);vec2 cell=floor(grid);
    float window=step(.16,f.x)*step(f.x,.86)*step(.2,f.y)*step(f.y,.78)*step(3.,vWorld.y);
    float lit=step(.77,hash(cell+vSeed))*mix(.3,1.,hash(floor(cell*.5)+vSeed));
    vec3 tint=mix(vec3(1.,.62,.29),vec3(.43,.72,.8),step(.77,hash(cell+vSeed+9.)));
    vec3 glass=vec3(.055,.09,.11)+vec3(.065,.095,.1)*max(n.y,.2);
    float blind=mix(1.,.48,step(.82,fract(f.y*9.))*step(.6,hash(cell+22.)));
    emission+=tint*lit*window*(.30+hash(cell+8.)*.65)*blind*(.64+.36*f.y);
    base=mix(base,glass,window);rough=mix(rough,.16,window);metal=window*.55;
    float floorLine=1.-smoothstep(.012,.026,abs(fract(uv.y*.34)-.03));base*=1.-floorLine*.22;
    if(vDetail==1.){float mullion=step(.945,fract(uv.x*.62));base=mix(base,vec3(.08,.11,.13),mullion);}
   }
   base*=.84+noise(vWorld.xy*.34+vWorld.z)*.20;
   if(wall){float joint=step(.975,fract((uv.x+floor(uv.y*1.5)*.32)*1.1))*step(.85,rough);base*=1.-joint*.16;}
  }
  if(vMaterial==2){
   float puddle=smoothstep(.28,.7,noise(vWorld.xz*.19));rough=mix(.37,.105,puddle*uRain);metal=.14;
   base*=.74+noise(vWorld.xz*35.)*.3;float wave=noise(vWorld.xz*2.3+uTime*.13)-.5;
   n=normalize(n+vec3(wave*.035*uRain,0.,noise(vWorld.zx*3.4-uTime*.2)*.025*uRain));
  }
  if(vMaterial==3){rough=.28;metal=.32;}
  if(vMaterial==4){rough=.88;base*=.65+noise(vWorld.xz*17.)*.4;}
  if(vMaterial==5){rough=.265;metal=.56;base*=.965+grain*.45;}
  if(vMaterial==6){if(dot(n,view)<0.)n=-n;rough=.16;metal=.06;base=vec3(.021,.037,.046)+base*.10;}
  if(vMaterial==7){rough=.12;metal=.35;n=normalize(n+vec3(sin(vWorld.z*.7+uTime*.6)*.07,0.,sin(vWorld.x*.42+uTime*.4)*.055));}
  if(vMaterial==8){rough=.92;base*=.65+noise(vWorld.xy*43.)*.35;}
  if(vMaterial>=10&&vMaterial<26){
   int idx=vMaterial-10;vec2 uv=(vUV+vec2(float(idx%4),float(3-idx/4)))/4.;vec3 tex=texture(uSigns,uv).rgb;
   base=vec3(.025,.035,.039);if(vFace.z>.5){emission+=tex*vColor.rgb*3.;base+=tex*.12;}rough=.3;
  }
  // Material-specific microstructure. Frequencies fade out with distance to avoid shimmer.
  float detailFade=1.-smoothstep(4.,16.,length(uEye-vWorld));
  if(vMaterial==30){
   float sx=sign(vSurface.x),back=smoothstep(-.004,.012,sx*(vSurface.x-sx*.2637));
   float palm=(1.-back)*(1.-smoothstep(.01,.08,abs(vSurface.y-.84)));
   float pores=noise(vSurface.yz*560.),fine=noise(vSurface.yz*1300.);
   float crease=0.;
   for(int finger=0;finger<4;finger++){
    float z=finger==0?.023:finger==1?.003:finger==2?-.017:-.034;
    float y=finger==0?.768:finger==1?.760:finger==2?.768:.790;
    float fz=(vSurface.z-z)/(finger==3?.0068:.0083);
    float mask=exp(-fz*fz*1.8);
    crease+=mask*(exp(-pow((vSurface.y-y+.0019*fz*fz)/.0012,2.))+.65*exp(-pow((vSurface.y-y+.021+.0015*fz*fz)/.0011,2.)));
   }
   // Life/heart/head folds are subtle curved palm grooves, not dark painted lines.
   float life=exp(-pow((vSurface.z-(.030-.028*pow((vSurface.y-.828)/.048,2.)))/.0013,2.));
   float crossPalm=exp(-pow((vSurface.y-.827-vSurface.z*.21)/.0011,2.))+.6*exp(-pow((vSurface.y-.807+vSurface.z*.12)/.0012,2.));
   crease+=palm*(life+crossPalm)*.65;
   float poreAA=1.-smoothstep(.15,1.,max(length(dFdx(vSurface)),length(dFdy(vSurface)))*950.);float height=((pores-.5)*.000045+(fine-.5)*.000015-crease*.000075)*detailFade*poreAA;
   n=surfaceBump(n,height);rough=mix(.57,.74,palm)+.035*(pores-.5);
   base*=.982+.025*pores;float pad=(1.-smoothstep(.752,.824,vSurface.y));base*=mix(vec3(1.),vec3(1.035,.978,.957),pad);base=mix(base,base*vec3(1.08,1.045,1.028)+vec3(.006,.003,.002),palm*.60);
   base*=1.-min(crease,.9)*.045*detailFade;
  }
  if(vMaterial==44){
   rough=.31+.035*noise(vSurface.yz*370.);metal=0.;
   float striae=sin(vSurface.z*4200.)*.000013*detailFade;n=surfaceBump(n,striae);
   base*=1.025+.018*noise(vSurface.yz*150.);
  }
  if(vMaterial==31||vMaterial==32){
   // Woven height in rest space, derivative-filtered instead of world-axis normal noise.
   vec2 cloth=vec2(vSurface.x+vSurface.z*.36,vSurface.y);
   float pixel=max(length(dFdx(cloth)),length(dFdy(cloth))),aa=1.-smoothstep(.00045,.0019,pixel);
   float weave=sin(cloth.x*2450.)*sin(cloth.y*2600.),twill=sin((cloth.x+cloth.y*.6)*1600.);
   float wear=noise(cloth*72.);base*=.98+(wear-.5)*.045+weave*.016*aa;
   rough=clamp((vMaterial==31?.83:.9)+(wear-.5)*.045,.7,.94);
   n=surfaceBump(n,(weave*.000010+twill*.000006)*aa*detailFade);
  }
  if(vMaterial==33||vMaterial==42){
   rough=.67;float strand=noise(vec2(vSurface.x*940.+vSurface.z*230.,vSurface.y*60.));base*=.76+.36*strand;
   // Directional highlights for short groom, an approximation rather than strand transport.
   vec3 h=normalize(view+uSun);float ribbon=pow(max(0.,1.-abs(dot(n,h))),7.);emission+=base*ribbon*.12;
  }
  if(vMaterial==46||vMaterial==47){
   if(!gl_FrontFacing)n=-n;
   float fibers=vMaterial==46?noise(vec2(vUV.x*70.,vUV.y*7.)):noise(vec2(vUV.x*640.,vUV.y*18.));
   base*=.83+fibers*.30;rough=vMaterial==47?.84:.67;metal=0.;
   if(vMaterial==46){vec3 tangent=normalize(dFdy(vWorld)+vec3(.00001)),h=normalize(view+uSun);float anis=pow(max(0.,1.-abs(dot(tangent,h))),24.);emission+=sqrt(max(base,vec3(0.)))*anis*.010;}
  }
  if(vMaterial==40){
   float jawGuard=smoothstep(.035,.092,vSurface.z)*smoothstep(1.530,1.549,vSurface.y);
   float faceBlend=max(smoothstep(1.537,1.605,vSurface.y),jawGuard);
   vec3 neckPigment=textureLod(uSkinAlbedo,vec2(clamp(vUV.x,.23,.77),.095),3.).rgb*vec3(.975,.982,.990);
   base=mix(pow(neckPigment,vec3(2.2)),pow(texture(uSkinAlbedo,vUV).rgb,vec3(2.2)),faceBlend)*vColor.rgb;
   float neckRough=.64+.018*noise(vSurface.xy*170.);
   rough=mix(neckRough,clamp(texture(uSkinRoughness,vUV).r,.42,.80),faceBlend);
   vec3 map=texture(uSkinNormal,vUV).xyz*2.-1.;map.xy*=.30*detailFade;map.z=max(.35,map.z);
   vec3 faceNormal=mappedNormal(n,normalize(map));
   float poreFade=1.-smoothstep(.12,.8,max(length(dFdx(vSurface)),length(dFdy(vSurface)))*650.);
   vec3 neckNormal=surfaceBump(n,(noise(vSurface.xz*570.)-.5)*.000028*detailFade*poreFade);
   n=normalize(mix(neckNormal,faceNormal,faceBlend));
  }
  if(vMaterial==41){
   rough=.19;vec2 q=vec2((abs(vSurface.x)-.0307781)/.00525,(vSurface.y-1.6708135)/.00525);float angle=atan(q.y,q.x),r=length(q);
   float fibers=noise(vec2(angle*38.,r*11.));base*=.55+fibers*.8;base*=1.-smoothstep(.72,1.,r)*.65;
  }
  if(vMaterial==34){rough=.12;float rim=clamp(abs(vSurface.x)-.031,-.01,.01);base*=vec3(1.015,.985,.975);}
  if(vMaterial==35){rough=.96;float bark=noise(vec2(vLocal.x*93.+vLocal.z*47.,vLocal.y*5.));base*=.72+bark*.42;}
  if(vMaterial==36){
   if(!gl_FrontFacing)n=-n;rough=.89;
   base*=.76+noise(vLocal.xz*8.+vLocal.y)*.48;
  }
  if(vMaterial==46){float edge=abs(vUV.x-.5)*2.;float cut=.965-.035*sin(vUV.y*27.);if(edge>cut)discard;}if(vMaterial==42){float coverage=1.-smoothstep(.88,.995,vUV.y);if(hash(floor(vSurface.xz*3800.)+floor(vSurface.y*2600.))>coverage)discard;}
  float nv=max(dot(n,view),.025);vec3 sky=mix(vec3(.10,.12,.13),vec3(.26,.34,.40),n.y*.5+.5);
  vec3 f0=mix(vec3(.04),base,metal),fresnel=f0+(1.-f0)*pow(1.-nv,5.);
  sky=mix(sky,vec3(.34,.42,.49)*(n.y*.25+.75),uDaylight);vec3 light=base*sky*(1.-metal*.72);
  // Analytic environment reflection approximates the city sky; no ray tracing or cubemap claim.
  vec3 re=reflect(-view,n),env=mix(vec3(.048,.065,.075),vec3(.27,.36,.45),smoothstep(-.2,.8,re.y));
  float horizon=exp(-abs(re.y)*10.);env+=vec3(.20,.24,.25)*horizon;
  light+=env*fresnel*(1.-rough*.72)*1.4;
  light+=brdf(n,view,uSun,base,rough,metal)*mix(vec3(1.4,1.65,1.9),vec3(3.8,3.65,3.25),uDaylight)*shadow(n)*mix(1.,.55,uStudio);
  for(int i=0;i<12;i++){
   if(i>=uLightCount)break;vec3 dl=uLights[i].xyz-vWorld;float ds=dot(dl,dl),dist=sqrt(ds);vec3 ld=dl/max(dist,.01);
   float att=(1.-smoothstep(10.,27.,dist))/(1.+ds*.035);vec3 lc=mix(vec3(.42,.74,1.),vec3(1.,.73,.42),uLights[i].w)*10.8*mix(1.,.22,uStudio);
   light+=brdf(n,view,ld,base,rough,metal)*lc*att;
   if(vMaterial==30||vMaterial==40||vMaterial==36){float transmission=pow(max(dot(-n,ld),0.),2.)*(vMaterial==36?.12:.035);light+=base*lc*att*transmission;}
  }
  vec3 hl=uHeadPos-vWorld;float hd=length(hl);vec3 hdir=hl/max(hd,.01);float cone=smoothstep(.89,.99,dot(-hdir,uHeadDir));
  float hatt=cone/(1.+hd*hd*.017);light+=brdf(n,view,hdir,base,rough,metal)*vec3(1.,.93,.77)*hatt*12.;
  if(vMaterial==2&&uPass==0&&uRain>0.){
   vec2 uv=vReflection.xy/vReflection.w*.5+.5;
   vec2 distortion=vec2(noise(vWorld.xz*3.+uTime*.2),noise(vWorld.zx*1.9-uTime*.13))-.5;
   vec3 reflectColor=unpack(texture(uReflection,clamp(uv+distortion*.0025,vec2(.002),vec2(.998))).rgb);
   float fresnel=.06+.59*pow(1.-nv,4.);float puddle=.27+.73*smoothstep(.2,.72,noise(vWorld.xz*.14));
   light=mix(light,reflectColor*.77,fresnel*uRain*puddle);
  }
  if(vMaterial==6){vec3 refl=mix(vec3(.15,.22,.28),vec3(.02,.04,.08),clamp(reflect(-view,n).y,0.,1.));light+=refl*(.22+.65*pow(1.-nv,3.));}
  light+=emission*(1.-uDaylight*.80);
  float dist=length(uEye-vWorld);float fog=1.-exp(-dist*.0045);fog*=.78+.22*exp(-max(vWorld.y,0.)*.02);
  vec3 fogColor=mix(vec3(.115,.175,.205),vec3(.38,.47,.52),uDaylight);light=mix(light,fogColor,clamp(fog,0.,.94));
  frag=vec4(light/(1.+light),vMaterial==6?clamp(.18+.42*pow(1.-nv,4.),.18,.62):1.);
 }`;
 const SHADOW_FS=`#version 300 es\nprecision highp float;flat in vec4 vLook;in vec3 vSurface;in vec4 vColor;flat in int vMaterial;in vec2 vUV;void main(){if(vMaterial==47&&vUV.y>.963){float cov=1.-smoothstep(.963,1.,vUV.y);vec2 q=floor(vSurface.xz*4100.)+floor(vSurface.y*3600.);if(fract(sin(dot(q,vec2(127.1,311.7)))*43758.5453)>cov)discard;}bool groom=vMaterial==42||(vMaterial==33&&(vSurface.y>1.706||vSurface.z<.04));if(groom&&vMaterial==42)discard;if(vMaterial==46){float edge=abs(vUV.x-.5)*2.;float cut=.965-.035*sin(vUV.y*27.);if(edge>cut)discard;}if(vMaterial==42){float coverage=1.-smoothstep(.88,.995,vUV.y);vec2 q=floor(vSurface.xz*3800.)+floor(vSurface.y*2600.);if(fract(sin(dot(q,vec2(127.1,311.7)))*43758.5453)>coverage)discard;}if(vMaterial==5&&vColor.a<-.04&&vSurface.x<-.65&&vSurface.y>.52&&vSurface.y<1.05&&vSurface.z>-.95&&vSurface.z<.81)discard;}`;
 const SCREEN_VS=`#version 300 es
 precision highp float;out vec2 uv;void main(){vec2 p=vec2(float((gl_VertexID<<1)&2),float(gl_VertexID&2));uv=p;gl_Position=vec4(p*2.-1.,0.,1.);}`;
 const SKY_FS=`#version 300 es
 precision highp float;in vec2 uv;out vec4 frag;uniform vec3 uForward;uniform vec3 uRight;uniform vec3 uUp;uniform float uAspect;uniform float uFov;uniform float uTime;uniform float uDaylight;
 float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 float noise(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(hash(i),hash(i+vec2(1,0)),f.x),mix(hash(i+vec2(0,1)),hash(i+1.),f.x),f.y);}
 float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=noise(p)*a;p=p*2.03+17.8;a*=.5;}return v;}
 void main(){vec2 q=(uv*2.-1.)*uFov;vec3 ray=normalize(uForward+q.x*uAspect*uRight+q.y*uUp);float y=max(ray.y,0.);
  vec3 col=mix(vec3(.13,.20,.235),vec3(.018,.036,.072),pow(y,.45));
  vec2 p=ray.xz/(abs(ray.y)+.22)*2.;float cloud=fbm(p+vec2(uTime*.003,0.));
  col=mix(col,vec3(.09,.13,.17),smoothstep(.39,.78,cloud)*.85);
  vec3 moon=normalize(vec3(-.44,.62,.65));float m=dot(ray,moon);col+=vec3(.7,.78,.76)*smoothstep(.9996,.9998,m);col+=vec3(.2,.28,.32)*pow(max(m,0.),100.)*.34;
  vec3 day=mix(vec3(.60,.75,.82),vec3(.14,.37,.72),pow(y,.45));day=mix(day,vec3(.80,.82,.83),smoothstep(.39,.78,cloud)*.70);col=mix(col,day,uDaylight);frag=vec4(col/(1.+col),1.);
 }`;
 const POST_FS=`#version 300 es
 precision highp float;in vec2 uv;out vec4 frag;uniform sampler2D uScene;uniform vec2 uResolution;uniform float uTime;uniform float uRain;uniform float uDamage;uniform float uBloom;
 float hash(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}
 vec3 unpack(vec3 c){return min(c/max(vec3(.015),1.-c),vec3(12.));}
 vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}
 vec3 antialias(vec2 coord){
  vec2 px=1./uResolution;vec3 a=texture(uScene,coord+vec2(-1.,-1.)*px).rgb,b=texture(uScene,coord+vec2(1.,-1.)*px).rgb;
  vec3 c=texture(uScene,coord+vec2(-1.,1.)*px).rgb,d=texture(uScene,coord+vec2(1.,1.)*px).rgb,m=texture(uScene,coord).rgb;
  vec3 luma=vec3(.299,.587,.114);float la=dot(a,luma),lb=dot(b,luma),lc=dot(c,luma),ld=dot(d,luma),lm=dot(m,luma);
  float lo=min(lm,min(min(la,lb),min(lc,ld))),hi=max(lm,max(max(la,lb),max(lc,ld)));
  if(hi-lo<max(.018,hi*.08))return m;
  vec2 dir=vec2(-((la+lb)-(lc+ld)),(la+lc)-(lb+ld));float reduce=max((la+lb+lc+ld)*.03125,.0078125);
  dir=clamp(dir/(min(abs(dir.x),abs(dir.y))+reduce),vec2(-6.),vec2(6.))*px;
  vec3 v=.5*(texture(uScene,coord+dir*(-.166667)).rgb+texture(uScene,coord+dir*.166667).rgb);
  vec3 w=v*.5+.25*(texture(uScene,coord-dir*.5).rgb+texture(uScene,coord+dir*.5).rgb);
  float lw=dot(w,luma);return lw<lo||lw>hi?v:w;
 }
 void main(){vec3 c=unpack(antialias(uv));vec3 glow=vec3(0.);vec2 px=1./uResolution;
  if(uBloom>.01){for(int i=0;i<8;i++){float a=float(i)*.785398;vec2 off=vec2(cos(a),sin(a))*px*(3.+float(i%3)*3.);vec3 s=unpack(texture(uScene,uv+off).rgb);glow+=max(s-vec3(.7),0.);}c+=glow*.048*uBloom;}
  c=aces(c*1.42);c=pow(c,vec3(.91));
  float vignette=1.-smoothstep(.26,.85,length((uv-.5)*vec2(1.,.9)));c*=.78+vignette*.22;
  vec2 rq=uv*vec2(300.,38.);rq.x+=rq.y*.19;rq.y+=uTime*29.;vec2 cell=floor(rq);float rain=step(.986,hash(vec2(cell.x,floor(rq.y*.08))))*(1.-smoothstep(.015,.09,abs(fract(rq.x)-.5)))*(1.-fract(rq.y));
  c+=vec3(.12,.15,.17)*rain*uRain;c+=(hash(gl_FragCoord.xy+fract(uTime)*100.)-.5)*.012;
  c=mix(c,c*vec3(1.,.3,.24),uDamage*(1.-vignette));frag=vec4(c,1.);
 }`;
 function compile(gl,vs,fs){
  const make=(type,source)=>{const s=gl.createShader(type);gl.shaderSource(s,source);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(s));return s;};
  const p=gl.createProgram(),a=make(gl.VERTEX_SHADER,vs),b=make(gl.FRAGMENT_SHADER,fs);gl.attachShader(p,a);gl.attachShader(p,b);gl.linkProgram(p);gl.deleteShader(a);gl.deleteShader(b);if(!gl.getProgramParameter(p,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(p));return p;
 }
 function geometry(){
  function mesh(){return{data:[],tri(a,b,c,uvs=[[0,0],[1,0],[1,1]]){let ab=b.map((v,i)=>v-a[i]),ac=c.map((v,i)=>v-a[i]),n=D.normalize(D.cross(ab,ac));[a,b,c].forEach((p,i)=>this.data.push(...p,...n,...uvs[i]));},quad(a,b,c,d){this.tri(a,b,c);this.tri(a,c,d,[[0,0],[1,1],[0,1]]);}};}
  let box=mesh();
  box.quad([-.5,-.5,.5],[.5,-.5,.5],[.5,.5,.5],[-.5,.5,.5]);box.quad([.5,-.5,-.5],[-.5,-.5,-.5],[-.5,.5,-.5],[.5,.5,-.5]);
  box.quad([.5,-.5,.5],[.5,-.5,-.5],[.5,.5,-.5],[.5,.5,.5]);box.quad([-.5,-.5,-.5],[-.5,-.5,.5],[-.5,.5,.5],[-.5,.5,-.5]);
  box.quad([-.5,.5,.5],[.5,.5,.5],[.5,.5,-.5],[-.5,.5,-.5]);box.quad([-.5,-.5,-.5],[.5,-.5,-.5],[.5,-.5,.5],[-.5,-.5,.5]);
  const bevel=mesh(),ring=(sx,sz,y)=>[[-.39*sx,y,.5*sz],[.39*sx,y,.5*sz],[.5*sx,y,.39*sz],[.5*sx,y,-.39*sz],[.39*sx,y,-.5*sz],[-.39*sx,y,-.5*sz],[-.5*sx,y,-.39*sz],[-.5*sx,y,.39*sz]];
  let rings=[ring(.92,.96,-.5),ring(1,1,-.32),ring(1,1,.26),ring(.91,.94,.5)];
  for(let j=0;j<3;j++)for(let i=0;i<8;i++)bevel.quad(rings[j][i],rings[j][(i+1)%8],rings[j+1][(i+1)%8],rings[j+1][i]);
  for(let i=1;i<7;i++){bevel.tri(rings[3][0],rings[3][i],rings[3][i+1]);bevel.tri(rings[0][0],rings[0][i+1],rings[0][i]);}
  const cabin=mesh();const p=[[-.5,-.5,.5],[.5,-.5,.5],[.5,-.5,-.5],[-.5,-.5,-.5],[-.40,.5,.15],[.40,.5,.15],[.40,.5,-.34],[-.40,.5,-.34]];
  cabin.quad(p[0],p[1],p[5],p[4]);cabin.quad(p[2],p[3],p[7],p[6]);cabin.quad(p[1],p[2],p[6],p[5]);cabin.quad(p[3],p[0],p[4],p[7]);cabin.quad(p[4],p[5],p[6],p[7]);
  const sphere=mesh();let lat=10,lon=14;
  const sp=(a,b)=>[Math.sin(a)*Math.cos(b)*.5,Math.cos(a)*.5,Math.sin(a)*Math.sin(b)*.5];
  for(let i=0;i<lat;i++)for(let j=0;j<lon;j++){let a=i/lat*Math.PI,b=j/lon*Math.PI*2,aa=(i+1)/lat*Math.PI,bb=(j+1)/lon*Math.PI*2;sphere.quad(sp(a,b),sp(a,bb),sp(aa,bb),sp(aa,b));}
  const wheel=mesh();for(let i=0;i<18;i++){let a=i/18*Math.PI*2,b=(i+1)/18*Math.PI*2,A=[-.5,Math.sin(a)*.5,Math.cos(a)*.5],B=[-.5,Math.sin(b)*.5,Math.cos(b)*.5],C=[.5,B[1],B[2]],E=[.5,A[1],A[2]];wheel.quad(A,E,C,B);wheel.tri([-.5,0,0],A,B);wheel.tri([.5,0,0],C,E);}
  for(let i=0;i<sphere.data.length;i+=8){const n=D.normalize(sphere.data.slice(i,i+3));sphere.data.splice(i+3,3,...n);}return{box:box.data,body:bevel.data,cabin:cabin.data,sphere:sphere.data,wheel:wheel.data};
 }
 class Renderer{
  constructor(canvas,world,quality='balanced'){
   this.canvas=canvas;this.world=world;this.quality=quality;this.gl=canvas.getContext('webgl2',{antialias:false,alpha:false,powerPreference:'high-performance',preserveDrawingBuffer:true});
   if(!this.gl)throw new Error('WebGL 2 no está disponible. Activa la aceleración gráfica o abre el juego en otro navegador.');
   const gl=this.gl;this.sceneProgram=compile(gl,VS,FS);this.shadowProgram=compile(gl,VS,SHADOW_FS);this.skyProgram=compile(gl,SCREEN_VS,SKY_FS);this.postProgram=compile(gl,SCREEN_VS,POST_FS);this.uniforms=new Map();
   this.meshes={};this.static={};this.dynamic={};this.camera={eye:[-8,4,0],target:[5,1,13],yaw:0,pitch:.22,mode:0,initialized:false};this.frame=0;this.rain=1;this.bloom=1;this.shadowSize=1024;
   for(const[name,data]of Object.entries(geometry())){this.meshes[name]=this.createMesh(data);this.static[name]=[];this.dynamic[name]=[];}
   this.emptyVAO=gl.createVertexArray();this.createSigns();this.createWhite();this.makeShadow();this.buildCity();
   for(const name of Object.keys(this.meshes)){this.meshes[name].chunks=this.chunkInstances(this.static[name]);this.meshes[name].dynamicBuffer=gl.createBuffer();}
   this.lights=new Float32Array(48);this.lightTime=-1;this.resize();
  }
  uniform(program,name){let m=this.uniforms.get(program);if(!m){m={};this.uniforms.set(program,m);}return m[name]??(m[name]=this.gl.getUniformLocation(program,name));}
  createMesh(data){const gl=this.gl,vao=gl.createVertexArray(),vbo=gl.createBuffer();gl.bindVertexArray(vao);gl.bindBuffer(gl.ARRAY_BUFFER,vbo);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(data),gl.STATIC_DRAW);for(const [i,size,offset]of [[0,3,0],[1,3,12],[2,2,24]]){gl.enableVertexAttribArray(i);gl.vertexAttribPointer(i,size,gl.FLOAT,false,32,offset);}return{vao,vbo,count:data.length/8};}
  add(list,mesh,x,y,z,sx,sy,sz,color,mat=0,emission=0,yaw=0,seed=0,detail=0,pitch=0,roll=0){list[mesh].push(x,y,z,yaw,sx,sy,sz,mat,color[0],color[1],color[2],emission,pitch,roll,seed,detail);}
  createWhite(){let gl=this.gl;this.white=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,this.white);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,1,1,0,gl.RGBA,gl.UNSIGNED_BYTE,new Uint8Array([0,0,0,255]));gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);}
  createSigns(){
   const c=document.createElement('canvas');c.width=2048;c.height=1024;const ctx=c.getContext('2d');
   const signs=['VÉRTICE','HOTEL  NÁCAR','24 / SIETE','MERCADO','CINE  ROXY','TALLER  84','PUERTO CERO','RADIO 94.6','NOCHE AZUL','CASA LÍA','LA ESQUINA','CAFÉ CENTRAL','DISTRITO CERO','TRANSMISIÓN','PARQUE LIBRE','SALIDA'];
   ctx.fillStyle='#071316';ctx.fillRect(0,0,c.width,c.height);signs.forEach((s,i)=>{let x=(i%4)*512,y=Math.floor(i/4)*256;ctx.strokeStyle='#193133';ctx.lineWidth=6;ctx.strokeRect(x+8,y+8,496,240);ctx.textAlign='center';ctx.textBaseline='middle';ctx.font=`700 ${s.length>11?49:60}px Arial, sans-serif`;ctx.fillStyle=i%4===0?'#b9e2d8':i%4===1?'#ffd7a1':'#eef0d1';ctx.fillText(s,x+256,y+116);ctx.font='18px monospace';ctx.fillStyle='#79a59f';ctx.fillText(i===0?'EL FUTURO NOS PERTENECE':'D I S T R I T O   C E R O',x+256,y+181);});
   const gl=this.gl;this.signs=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,this.signs);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,true);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,c);gl.generateMipmap(gl.TEXTURE_2D);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR_MIPMAP_LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL,false);
  }
  targetBuffer(w,h,depth=true){
   const gl=this.gl,fb=gl.createFramebuffer(),tex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,tex);gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA8,w,h,0,gl.RGBA,gl.UNSIGNED_BYTE,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.LINEAR);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);gl.bindFramebuffer(gl.FRAMEBUFFER,fb);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.COLOR_ATTACHMENT0,gl.TEXTURE_2D,tex,0);
   let db=null;if(depth){db=gl.createRenderbuffer();gl.bindRenderbuffer(gl.RENDERBUFFER,db);gl.renderbufferStorage(gl.RENDERBUFFER,gl.DEPTH_COMPONENT24,w,h);gl.framebufferRenderbuffer(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.RENDERBUFFER,db);}
   if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw new Error('No se pudo crear el búfer de imagen.');return{fb,tex,db,w,h};
  }
  deleteTarget(t){if(!t)return;const g=this.gl;g.deleteFramebuffer(t.fb);g.deleteTexture(t.tex);if(t.db)g.deleteRenderbuffer(t.db);}
  makeShadow(){const gl=this.gl;this.shadowTex=gl.createTexture();gl.bindTexture(gl.TEXTURE_2D,this.shadowTex);gl.texImage2D(gl.TEXTURE_2D,0,gl.DEPTH_COMPONENT24,this.shadowSize,this.shadowSize,0,gl.DEPTH_COMPONENT,gl.UNSIGNED_INT,null);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);this.shadowFB=gl.createFramebuffer();gl.bindFramebuffer(gl.FRAMEBUFFER,this.shadowFB);gl.framebufferTexture2D(gl.FRAMEBUFFER,gl.DEPTH_ATTACHMENT,gl.TEXTURE_2D,this.shadowTex,0);gl.drawBuffers([gl.NONE]);gl.readBuffer(gl.NONE);if(gl.checkFramebufferStatus(gl.FRAMEBUFFER)!==gl.FRAMEBUFFER_COMPLETE)throw new Error('El dispositivo no permite crear sombras WebGL.');}
  resize(){const gl=this.gl;let q=this.quality==='eco'?.65:this.quality==='high'?1.2:.88,dpr=Math.min(window.devicePixelRatio||1,1.5),w=Math.max(320,Math.round((this.previewSize?.width||innerWidth)*dpr*q)),h=Math.max(240,Math.round((this.previewSize?.height||innerHeight)*dpr*q));if(this.canvas.width===w&&this.canvas.height===h&&this.scene)return;this.canvas.width=w;this.canvas.height=h;this.deleteTarget(this.scene);this.deleteTarget(this.reflection);this.scene=this.targetBuffer(w,h);this.reflection=this.targetBuffer(Math.max(256,Math.round(w*.5)),Math.max(180,Math.round(h*.5)));gl.bindFramebuffer(gl.FRAMEBUFFER,null);}
  buildCity(){
   const S=this.static,add=(...args)=>this.add(S,...args),r=D.rng(226);const asphalt=[.035,.045,.049],curb=[.29,.31,.30],concrete=[.21,.235,.25];
   add('box',0,-.30,0,872,.5,872,asphalt,2);add('box',0,-1.1,0,2000,.2,2000,[.02,.07,.08],7);
   for(const b of this.world.blocks){
    add('box',b.x,.055,b.z,62,.23,62,b.park?[.045,.07,.047]:curb,b.park?4:0);
    if(b.park){
     add('box',b.x,.19,b.z,5,.03,61,[.24,.255,.24],0);add('box',b.x,.19,b.z,61,.03,5,[.24,.255,.24],0);
     // Park vegetation is supplied by ReactiveWorld.
     continue;
    }
    // Stone seams make the raised pavement read at street level.
    for(let k=-2;k<=2;k++)add('box',b.x+k*10,.177,b.z,.026,.015,62,[.12,.14,.14],0);
   }
   for(const b of this.world.buildings){
    let col=b.style===1?[.115+b.tone*.07,.15+b.tone*.06,.17+b.tone*.07]:[.22+b.tone*.10,.225+b.tone*.065,.22+b.tone*.055];
    add('box',b.x,b.h/2+.16,b.z,b.w,b.h,b.d,col,1,0,0,b.seed,b.style);
    add('box',b.x,1.4,b.z,b.w+.22,2.5,b.d+.22,[.105,.12,.12],0);
    // Parapets, rooftop plant rooms and mechanical equipment.
    add('box',b.x,b.h+.30,b.z,b.w+.42,.28,b.d+.42,[.17,.19,.20],0);
    add('box',b.x+2,b.h+1.35,b.z-2,b.w*.47,2.0,b.d*.35,[.14,.165,.18],0);
    if(b.seed%3<1)add('box',b.x-3,b.h+3.2,b.z+1,.1,5.8,.1,[.28,.32,.34],3);
    if(b.h>58){add('box',b.x,b.h+.51,b.z+b.d/2,.14,.12,.16,[1,.12,.08],0,7);add('box',b.x,b.h*.79,b.z+b.d/2+.01,b.w,.055,.03,[.25,.7,.64],0,1.5);}
    for(let h=3.5;h<b.h;h+=12)add('box',b.x,h,b.z,b.w+.12,.16,b.d+.12,[.13,.16,.175],0);
    let road=Math.round(b.z/84)*84,side=Math.sign(road-b.z),front=b.z+side*(b.d/2+.21),yaw=side>0?0:Math.PI;
    add('box',b.x,2,front,b.w*.78,2.4,.15,[.045,.09,.09],6);
    add('box',b.x,3.43,front+side*.28,b.w*.85,.2,1.5,[.13,.16,.16],3);
    if(b.seed%4<1.8){let sign=b.sign;add('box',b.x,4.6,front+side*.05,Math.min(12,b.w*.7),2.6,.2,[1,1,1],10+sign,0,yaw);}
    if(b.seed%5<1){let rx=Math.round(b.x/84)*84,sign=Math.sign(rx-b.x);add('box',b.x+sign*(b.w/2+.22),7,b.z,3,6,.3,[.6,.95,.83],10+(b.sign%12),0,sign>0?Math.PI/2:-Math.PI/2);}
   }
   for(let i=-5;i<=5;i++)for(let j=-5;j<5;j++){
    const a=i*84,b=(j+.5)*84;
    for(let s of [-1,1]){
     add('box',a+s*.18,-.033,b,.08,.015,61,[.48,.40,.19],3);add('box',b,-.032,a+s*.18,61,.015,.08,[.48,.40,.19],3);
     add('box',a+s*9.6,-.031,b,.09,.016,61,[.56,.58,.54],3);add('box',b,-.031,a+s*9.6,61,.016,.09,[.56,.58,.54],3);
    }
    for(let k=0;k<5;k++){let q=j*84+16+k*12;add('box',a+7.5,-.029,q,.12,.015,4,[.44,.47,.45],3);add('box',q,-.029,a-7.5,4,.015,.12,[.44,.47,.45],3);}
   }
   for(let i=-5;i<=5;i++)for(let j=-5;j<=5;j++){
    let x=i*84,z=j*84;
    for(let s of [-1,1])for(let k=-3;k<=3;k++){
     add('box',x+k*2.3,-.025,z+s*8.4,1.18,.014,2.8,[.53,.54,.50],3);
     add('box',x+s*8.4,-.024,z+k*2.3,2.8,.014,1.18,[.53,.54,.50],3);
    }
    if(Math.abs(i)<5&&Math.abs(j)<5){
     add('box',x+11.8,2.4,z+11.8,.12,4.5,.12,[.17,.2,.2],3);add('box',x+11.8,4.9,z+11.8,.35,.92,.3,[.022,.028,.03],3);add('sphere',x+11.8,5.18,z+11.98,.16,.16,.08,[.9,.12,.045],0,4);
    }
   }
   // Street lamps are rendered from mutable simulation state.
   for(let j=-4;j<5;j++){


    // Bus shelter with glass, roof and bench.
    add('box',-13.5,2.7,j*84+46,2.8,.14,6,[.085,.10,.105],3);add('box',-14.7,1.4,j*84+46,.09,2.55,5.5,[.1,.17,.18],6);
    for(let s of [-1,1])add('box',-13.9,1.4,j*84+46+s*2.6,.12,2.5,.12,[.14,.17,.17],3);

   }
   // Story props are physical, not only floating map icons.
   add('box',13,.95,20,.65,1.8,.5,[.22,.32,.31],3);add('box',13,1.35,19.73,.48,.50,.035,[.1,.75,.64],0,1.1);
   for(const p of this.world.pois){
    if(p.type==='terminal'){add('box',p.x,1.05,p.z,1.5,2.1,.8,[.10,.13,.14],3);add('box',p.x,1.5,p.z-.43,1.1,.6,.03,[.38,.84,.72],0,2);}
    if(p.type==='job'||p.type==='race'){add('box',p.x,1.2,p.z,.25,2.4,.25,[.15,.2,.2],3);add('box',p.x,2.4,p.z,2.5,.8,.15,[.7,.9,.7],p.type==='job'?13:17,0,Math.PI);}
   }
  }
  tree(list,x,z,scale,r){this.add(list,'box',x,2*scale,z,.25*scale,4*scale,.25*scale,[.16,.13,.095],0);for(let i=0;i<4;i++)this.add(list,'sphere',x+(r()-.5)*2*scale,(4.2+r())*scale,z+(r()-.5)*2*scale,(2.4+r())*scale,3*scale,2.7*scale,[.08+r()*.025,.145,.105],8);}
  renderCar(c){
   const L=this.dynamic,a=c.yaw,co=Math.cos(a),si=Math.sin(a),col=c.color;
   const put=(mesh,x,y,z,sx,sy,sz,color,mat=0,em=0,da=0,pitch=0,roll=0)=>this.add(L,mesh,c.x+x*co+z*si,y,c.z-x*si+z*co,sx,sy,sz,color,mat,c.empUntil>this.currentTime?0:em,a+da,0,0,pitch,roll);
   put('body',0,.7,0,1.9,.70,4.45,col,5);put('box',0,.36,0,1.67,.22,3.8,[.025,.03,.03],3);
   put('cabin',0,1.25,-.25,1.64,.78,2.32,[.12,.19,.22],6);put('body',0,1.66,-.46,1.31,.075,1.23,col,5);
   put('box',0,1.17,-.57,1.67,.76,.055,col,5);put('box',0,.98,-.16,1.84,.05,2.2,col,5);
   for(let s of [-1,1]){
    put('body',s*.99,1.09,.48,.28,.16,.4,col,5);put('box',s*.97,.84,-.45,.025,.038,.29,[.45,.5,.49],3);
    for(let f of [-1,1]){put('wheel',s*.96,.40,f*1.34,.24,.76,.76,[.022,.026,.026],4);put('wheel',s*1.092,.40,f*1.34,.018,.48,.48,[.28,.32,.33],3);put('wheel',s*1.105,.40,f*1.34,.024,.17,.17,[.07,.09,.1],3);}
    put('body',s*.64,.79,2.09,.45,.19,.09,[.91,.96,.87],0,5);
    put('box',s*.64,.8,-2.12,.49,.12,.025,[.65,.016,.009],0,c.brake?9:3);
    put('box',s*.62,.51,2.18,.21,.06,.04,[.95,.7,.2],0,1.3);
   }
   put('box',0,.49,2.2,.74,.19,.025,[.022,.027,.028],3);put('box',0,.61,-2.22,.39,.13,.026,[.58,.63,.59],3);
   if(c.police){put('box',0,.82,.03,1.92,.26,1.34,[.63,.7,.7],0);put('box',0,1.77,-.45,.93,.08,.23,[.035,.05,.06],3);
    const blink=Math.sin(this.currentTime*13+c.id)>0;
    put('box',-.26,1.83,-.45,.39,.13,.22,[.08,.25,1],0,blink?9:1);put('box',.26,1.83,-.45,.39,.13,.22,[1,.02,.012],0,blink?1:9);
   }
  }
  renderPerson(n,isPlayer=false){
   const L=this.dynamic,a=n.yaw,co=Math.cos(a),si=Math.sin(a),baseY=n.y||0;
   const skin=isPlayer?[.52,.34,.24]:n.skin,coat=isPlayer?[.105,.135,.13]:n.coat;
   const trousers=isPlayer?[.045,.055,.061]:[.055,.067,.075],shoe=[.018,.022,.023],shirt=isPlayer?[.095,.115,.108]:coat;
   const speed=isPlayer?(n.moveSpeed||0):(n.speed||1.1),sprint=isPlayer?(n.sprintBlend||0):0;
   const pose=D.humanoidPose({phase:isPlayer?n.walk:n.phase,speed,sprint,y:baseY,vy:n.vy||0,turn:isPlayer?(n.turnRate||0)*.14:0,time:this.currentTime,landing:n.landing||0,crouch:n.crouch||0,carry:!!n.carry,reach:n.reach||0,stagger:n.stagger||0,dodge:n.dodge||0});
   const actorScale=n.seated?.86:1;const rootY=baseY+pose.hipBob-(n.crouch||0)*.25-(n.dodge||0)*.28;
   const world=(x,y,z)=>[n.x+(x*co+z*si)*actorScale,y*actorScale+rootY,n.z+(-x*si+z*co)*actorScale];
   const put=(mesh,x,y,z,sx,sy,sz,color,mat=0,pitch=0,roll=0,yawOff=0,em=0)=>{const q=world(x,y,z);this.add(L,mesh,q[0],q[1],q[2],sx*actorScale,sy*actorScale,sz*actorScale,color,mat,em,a+yawOff,0,0,pitch,roll);};
   const limb=(joint,len,pitch,roll,width,depth,color,mat=0)=>{
    const cp=Math.cos(pitch),sp=Math.sin(pitch),sr=Math.sin(roll),cr=Math.cos(roll);
    const d=[sr*cp,-cr*cp,-sp],mid=[joint[0]+d[0]*len*.5,joint[1]+d[1]*len*.5,joint[2]+d[2]*len*.5],end=[joint[0]+d[0]*len,joint[1]+d[1]*len,joint[2]+d[2]*len];
    put('body',mid[0],mid[1],mid[2],width,len,depth,color,mat,pitch,roll);return end;
   };
   // Pelvis and layered torso. Slight opposing yaw sells weight transfer without a skeletal mesh.
   put('body',0,.84,0,.34,.24,.24,trousers,0,0,pose.pelvisRoll,pose.pelvisYaw);
   put('body',0,1.08,-.005,.38,.34,.245,shirt,0,pose.spinePitch,pose.spineRoll,pose.shoulderYaw*.35);
   put('body',0,1.31,-.018,.46,.27,.27,coat,0,pose.spinePitch*.82,pose.spineRoll*.75,pose.shoulderYaw);
   put('body',0,1.43,-.02,.39,.09,.25,coat,0,pose.spinePitch*.7,pose.spineRoll*.55,pose.shoulderYaw);
   // Jacket hem and rear panel give the player a recognisable silhouette from the chase camera.
   if(isPlayer){put('body',0,1.17,-.145,.34,.34,.055,[.035,.046,.043],3,pose.spinePitch,pose.spineRoll,pose.shoulderYaw*.55);put('box',0,1.405,.145,.15,.035,.035,[.56,.67,.58],3,0,0,pose.shoulderYaw);}
   // Legs: independent hip, knee and ankle articulation, including airborne tuck.
   for(const [side,key] of [[-1,'left'],[1,'right']]){
    const lp=isPlayer?D.solveFootPose(n,side,rootY,pose[key]):pose[key],hip=[side*.115,.82,0],thigh=limb(hip,.43,lp.hip,side*-.018,.155,.17,trousers,0);
    put('sphere',thigh[0],thigh[1],thigh[2],.16,.14,.17,trousers,0,0,0);
    const shin=limb(thigh,.42,lp.hip+lp.knee,side*.012,.125,.145,trousers,0);
    put('sphere',shin[0],shin[1],shin[2],.13,.11,.14,trousers,0);
    const footPitch=lp.hip+lp.knee+lp.ankle;
    put('body',shin[0],Math.max(.075,shin[1]-.015),shin[2]+.07,.145,.13,.31,shoe,3,footPitch*.28,0);
   }
   // Clavicles and articulated arms counter-swing against the pelvis.
   for(const [side,key] of [[-1,'left'],[1,'right']]){
    const ap=pose[key],shoulder=[side*.285,1.36,-.015];
    put('sphere',shoulder[0],shoulder[1],shoulder[2],.17,.17,.18,coat,0,0,side*.04,pose.shoulderYaw);
    const elbow=limb(shoulder,.31,ap.shoulder,side*.075,.12,.135,coat,0);
    put('sphere',elbow[0],elbow[1],elbow[2],.12,.12,.13,coat,0);
    const hand=limb(elbow,.285,ap.shoulder-ap.elbow,side*.035,.10,.115,skin,0);
    put('sphere',hand[0],hand[1],hand[2],.105,.14,.09,skin,0,ap.shoulder-ap.elbow,side*.02);
   }
   // Neck and head: separate cranium, jaw, ears, hair and face plane improve readability at close camera distance.
   put('body',0,1.535,-.005,.13,.16,.13,skin,0,pose.headPitch*.45,pose.spineRoll*.25,pose.headYaw*.35);
   put('sphere',0,1.71,.005,.255,.30,.245,skin,0,pose.headPitch,pose.spineRoll*.16,pose.headYaw);
   put('body',0,1.62,.058,.20,.115,.19,skin,0,pose.headPitch,0,pose.headYaw);
   put('sphere',-.132,1.705,.002,.055,.08,.045,skin,0);put('sphere',.132,1.705,.002,.055,.08,.045,skin,0);
   put('sphere',0,1.812,-.015,.266,.13,.25,[.025,.022,.020],0,pose.headPitch,0,pose.headYaw);
   put('body',0,1.76,-.112,.245,.12,.075,[.025,.022,.020],0,pose.headPitch,0,pose.headYaw);
   put('body',0,1.675,.132,.055,.075,.045,skin,0,pose.headPitch,0,pose.headYaw);
   for(const side of [-1,1])put('box',side*.065,1.715,.127,.024,.017,.014,[.018,.016,.015],0,pose.headPitch,0,pose.headYaw);
   put('box',0,1.65,.14,.075,.018,.014,[.14,.055,.045],0,pose.headPitch,0,pose.headYaw);
  }
  updateDynamic(sim){
   for(const k of Object.keys(this.dynamic))this.dynamic[k].length=0;this.currentTime=sim.time;this.currentSim=sim;const p=sim.player;
   for(const c of sim.cars)if(D.distance(c,p)<235||c===sim.actor())this.renderCar(c);
   this.renderPlayer(sim);
   for(const n of sim.peds)if(!n.hidden&&D.distance(n,p)<90)this.renderPerson(n);
   const t=sim.target();if(t){let color=t.custom?[.22,.75,1]:[.72,.88,.30],radius=t.job&&sim.job.type==='race'?6:2.5;
    for(let k=0;k<24;k++){let a=k/24*Math.PI*2;this.add(this.dynamic,'box',t.x+Math.sin(a)*radius,.03,t.z+Math.cos(a)*radius,.16,.06,.6,color,0,2,a);}
    this.add(this.dynamic,'body',t.x,3.9+Math.sin(sim.time*2)*.16,t.z,.46,.46,.46,color,0,2,sim.time*.5,0,0,.65,.65);
    for(let i=1;i<sim.route.length;i++){let a=sim.route[i-1],b=sim.route[i],d=D.distance(a,b),yaw=Math.atan2(b.x-a.x,b.z-a.z);for(let j=7;j<d;j+=12){let x=D.lerp(a.x,b.x,j/d),z=D.lerp(a.z,b.z,j/d);if(Math.hypot(x-p.x,z-p.z)<110)this.add(this.dynamic,'box',x+Math.cos(yaw)*3.5,-.015,z-Math.sin(yaw)*3.5,.18,.025,2.1,color,0,.75,yaw);}}
   }
   for(const c of this.world.crates)if(!sim.collected.includes(c.id)&&D.distance(c,p)<90){this.add(this.dynamic,'body',c.x,.42,c.z,.7,.55,.5,[.24,.28,.14],3);this.add(this.dynamic,'box',c.x,.71,c.z,.4,.03,.25,[.73,.9,.30],0,2);}
   this.renderReactive(sim);
   for(const name of Object.keys(this.meshes)){const m=this.meshes[name];this.gl.bindBuffer(this.gl.ARRAY_BUFFER,m.dynamicBuffer);const data=this.dynamic[name],packed=new Float32Array(data.length),origin=this.renderOrigin||[0,0];for(let i=0;i<data.length;i++)packed[i]=data[i]-(i%16===0?origin[0]:i%16===2?origin[1]:0);this.gl.bufferData(this.gl.ARRAY_BUFFER,packed,this.gl.DYNAMIC_DRAW);m.dynamicCount=this.dynamic[name].length/16;}
  }
  updateCamera(sim,dt,{menu=false,photo=false,look=false}={}){
   const c=this.camera,p=sim.player,a=sim.actor();
   if(menu){const phase=sim.time*.025;let eye=[p.x-10*Math.cos(phase),4.1,p.z-10+Math.sin(phase)*6];c.eye=eye;c.target=[p.x+1,1.2,p.z+6];c.initialized=false;return;}
   if(!photo&&!look){if(p.car!==null)c.yaw=D.turn(c.yaw,a.yaw,dt*1.6);}
   let distance=photo?c.photoDistance||10:p.car!==null?(c.mode===1?4.9:c.mode===2?17:8.5):(c.mode===2?10:4.3);
   let elevation=photo?c.pitch:.19+c.pitch*.6,base=p.car!==null?(photo?.85:1.1):(photo&&c.closeup?1.48:1.3);
   let target=[p.x,base+p.y,p.z],eye=[p.x-Math.sin(c.yaw)*distance*Math.cos(elevation),base+p.y+distance*Math.sin(elevation),p.z-Math.cos(c.yaw)*distance*Math.cos(elevation)];
   // Pull the camera forward when a building occludes the shoulder/chase view.
   for(let i=0;i<16;i++){let f=1-i/17,x=D.lerp(target[0],eye[0],f),z=D.lerp(target[2],eye[2],f);if(!this.world.blocked(x,z,.3)&&this.world.visible(p.x,p.z,x,z)){eye=[x,D.lerp(target[1],eye[1],f),z];break;}}
   if(!c.initialized){c.eye=eye;c.target=target;c.initialized=true;}else{c.eye=c.eye.map((v,i)=>D.damp(v,eye[i],photo?10:8,dt));c.target=c.target.map((v,i)=>D.damp(v,target[i],14,dt));}
  }
  chunkInstances(data){
   const groups=new Map(),gl=this.gl;
   for(let i=0;i<data.length;i+=16){const x=data[i],y=data[i+1],z=data[i+2],sx=data[i+4],sy=data[i+5],sz=data[i+6];const key=Math.max(sx,sz)>120?'global':Math.floor(x/84)+':'+Math.floor(z/84);let g=groups.get(key);if(!g){g={data:[],min:[Infinity,Infinity,Infinity],max:[-Infinity,-Infinity,-Infinity]};groups.set(key,g);}g.data.push(...data.slice(i,i+16));const r=Math.hypot(sx,sz)/2;for(let a=0;a<3;a++){const pos=[x,y,z][a],radius=a===1?sy/2:r;g.min[a]=Math.min(g.min[a],pos-radius);g.max[a]=Math.max(g.max[a],pos+radius);}}
   return [...groups.values()].map(g=>{g.buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,g.buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array(g.data),gl.STATIC_DRAW);g.count=g.data.length/16;delete g.data;return g;});
  }
  setFrustum(m){this.frustum=[];for(let r=0;r<3;r++)for(let sign of [-1,1])this.frustum.push([m[3]+sign*m[r],m[7]+sign*m[4+r],m[11]+sign*m[8+r],m[15]+sign*m[12+r]]);}
  visibleChunk(g){const o=this.renderOrigin||[0,0];return !this.frustum||this.frustum.every(p=>p[0]*((p[0]>=0?g.max[0]:g.min[0])-o[0])+p[1]*(p[1]>=0?g.max[1]:g.min[1])+p[2]*((p[2]>=0?g.max[2]:g.min[2])-o[1])+p[3]>=0);}
  drawMeshes(withTransparent=false){
   const gl=this.gl,program=gl.getParameter(gl.CURRENT_PROGRAM);
   gl.uniform1f(this.uniform(program,'uTime'),this.currentTime||0);if(this.appearanceTexture){gl.activeTexture(gl.TEXTURE7);gl.bindTexture(gl.TEXTURE_2D,this.appearanceTexture);gl.uniform1i(this.uniform(program,'uCharacterLooks'),7);}if(this.crowdTexture){gl.activeTexture(gl.TEXTURE3);gl.bindTexture(gl.TEXTURE_2D,this.crowdTexture);gl.uniform1i(this.uniform(program,'uCrowdBones'),3);}
   if(this.dualTexture){gl.activeTexture(gl.TEXTURE8);gl.bindTexture(gl.TEXTURE_2D,this.dualTexture);gl.uniform1i(this.uniform(program,'uCrowdDuals'),8);}
   const draw=m=>{gl.uniform1i(this.uniform(program,'uSkinned'),m.crowd?2:m.skinned?1:0);if(m.skinned&&!m.crowd&&m.palette)gl.uniformMatrix4fv(this.uniform(program,'uBones[0]'),false,m.palette);gl.bindVertexArray(m.vao);const batches=m.chunks.filter(g=>this.visibleChunk(g));batches.push({buffer:m.dynamicBuffer,count:m.dynamicCount,dynamic:true});for(const batch of batches){const {buffer,count}=batch;if(!count)continue;const o=this.renderOrigin||[0,0];gl.uniform3fv(this.uniform(program,'uChunkOffset'),batch.dynamic?[0,0,0]:[(batch.baseX||0)-o[0],0,(batch.baseZ||0)-o[1]]);gl.bindBuffer(gl.ARRAY_BUFFER,buffer);for(let i=3;i<=6;i++){gl.enableVertexAttribArray(i);gl.vertexAttribPointer(i,4,gl.FLOAT,false,64,(i-3)*16);gl.vertexAttribDivisor(i,1);}gl.drawArraysInstanced(gl.TRIANGLES,0,m.count,count);}};
   for(const m of Object.values(this.meshes))if(!m.transparent)draw(m);
   if(withTransparent){gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE_MINUS_SRC_ALPHA);gl.depthMask(false);for(const m of Object.values(this.meshes))if(m.transparent)draw(m);gl.depthMask(true);gl.disable(gl.BLEND);}
  }
  sky(eye,target,up,time,aspect,fov){const gl=this.gl,p=this.skyProgram;gl.useProgram(p);gl.bindVertexArray(this.emptyVAO);gl.disable(gl.DEPTH_TEST);let forward=D.normalize(target.map((v,i)=>v-eye[i])),right=D.normalize(D.cross(forward,up)),skyUp=D.cross(right,forward);for(const [n,v]of [['uForward',forward],['uRight',right],['uUp',skyUp]])gl.uniform3fv(this.uniform(p,n),v);gl.uniform1f(this.uniform(p,'uTime'),time);gl.uniform1f(this.uniform(p,'uAspect'),aspect);gl.uniform1f(this.uniform(p,'uFov'),Math.tan(fov/2));gl.uniform1f(this.uniform(p,'uDaylight'),this.daylight||0);gl.drawArrays(gl.TRIANGLES,0,3);gl.enable(gl.DEPTH_TEST);}
  sceneUniforms(vp,eye,pass,sim){this.setFrustum(vp);const gl=this.gl,p=this.sceneProgram;gl.useProgram(p);gl.uniformMatrix4fv(this.uniform(p,'uVP'),false,vp);gl.uniformMatrix4fv(this.uniform(p,'uLightVP'),false,this.lightVP);gl.uniformMatrix4fv(this.uniform(p,'uReflectVP'),false,this.reflectVP);gl.uniform3fv(this.uniform(p,'uEye'),eye);gl.uniform1f(this.uniform(p,'uDaylight'),this.daylight||0);gl.uniform1f(this.uniform(p,'uStudio'),this.previewStudio?1:0);gl.uniform3fv(this.uniform(p,'uSun'),this.sun);gl.uniform4fv(this.uniform(p,'uLights[0]'),this.lights);gl.uniform1f(this.uniform(p,'uTime'),sim.time);gl.uniform1f(this.uniform(p,'uRain'),this.rain);gl.uniform1i(this.uniform(p,'uPass'),pass);gl.uniform1i(this.uniform(p,'uShadows'),this.quality==='eco'||pass===1?0:1);gl.uniform1i(this.uniform(p,'uLightCount'),this.quality==='eco'?6:12);gl.uniform1f(this.uniform(p,'uShadowTexel'),1/this.shadowSize);
   const car=sim.player.car!==null?sim.actor():sim.cars[0],h=[car.x+Math.sin(car.yaw)*2.4,.75,car.z+Math.cos(car.yaw)*2.4];h[0]-=(this.renderOrigin?.[0]||0);h[2]-=(this.renderOrigin?.[1]||0);if(car.damage?.front>.8||car.empUntil>sim.time)h[1]=-1000;gl.uniform3fv(this.uniform(p,'uHeadPos'),h);gl.uniform3fv(this.uniform(p,'uHeadDir'),[Math.sin(car.yaw),-.05,Math.cos(car.yaw)]);
   for(const [i,n,tex]of [[0,'uShadow',this.shadowTex],[1,'uReflection',pass===1?this.white:this.reflection.tex],[2,'uSigns',this.signs]]){gl.activeTexture(gl.TEXTURE0+i);gl.bindTexture(gl.TEXTURE_2D,tex);gl.uniform1i(this.uniform(p,n),i);}
  }
  render(sim){
   const gl=this.gl;this.frame++;this.updateDynamic(sim);const c=this.camera,aspect=this.canvas.width/this.canvas.height,fov=this.fovOverride||Math.PI*.36;this.sun=D.normalize([-.55,.8,.42]);
   const o=this.renderOrigin||[0,0],eyeLocal=[c.eye[0]-o[0],c.eye[1],c.eye[2]-o[1]],targetLocal=[c.target[0]-o[0],c.target[1],c.target[2]-o[1]];const projection=D.M4.perspective(fov,aspect,.15,1000);this.vp=D.M4.multiply(projection,D.M4.lookAt(eyeLocal,targetLocal));
   const re=[eyeLocal[0],-eyeLocal[1],eyeLocal[2]],rt=[targetLocal[0],-targetLocal[1],targetLocal[2]];this.reflectVP=D.M4.multiply(projection,D.M4.lookAt(re,rt,[0,-1,0]));
   if(this.lightTime<sim.time-.35||this.lightTime<0||this.lightRevision!==sim.dynamics?.lightRevision||this.lightWorld!==sim.dynamics){const sorted=this.world.lights.filter((l,i)=>!sim.dynamics||sim.dynamics.lightActive(i)).sort((a,b)=>Math.hypot(a.x-c.target[0],a.z-c.target[2])-Math.hypot(b.x-c.target[0],b.z-c.target[2]));for(let i=0;i<12;i++){const l=sorted[i];this.lights.set(l?[l.x-o[0],l.y,l.z-o[1],l.warm?1:0]:[0,-1000,0,0],i*4);}this.lightTime=sim.time;this.lightRevision=sim.dynamics?.lightRevision;this.lightWorld=sim.dynamics;}
   gl.enable(gl.DEPTH_TEST);gl.disable(gl.CULL_FACE);gl.disable(gl.BLEND);
   if(this.frame%3===1||!this.lightVP){let t=[Math.round(targetLocal[0]/4)*4,0,Math.round(targetLocal[2]/4)*4],eye=t.map((v,i)=>v+this.sun[i]*170);this.lightVP=D.M4.multiply(D.M4.ortho(this.previewStudio?-3:-110,this.previewStudio?3:110,this.previewStudio?-3:-110,this.previewStudio?3:110,1,350),D.M4.lookAt(eye,t));
    if(this.quality!=='eco'){gl.bindFramebuffer(gl.FRAMEBUFFER,this.shadowFB);gl.viewport(0,0,this.shadowSize,this.shadowSize);gl.clear(gl.DEPTH_BUFFER_BIT);gl.useProgram(this.shadowProgram);gl.uniform1f(this.uniform(this.shadowProgram,'uTime'),sim.time);gl.uniformMatrix4fv(this.uniform(this.shadowProgram,'uVP'),false,this.lightVP);this.setFrustum(this.lightVP);this.drawMeshes();}
   }
   if(this.rain>.01){gl.bindFramebuffer(gl.FRAMEBUFFER,this.reflection.fb);gl.viewport(0,0,this.reflection.w,this.reflection.h);gl.clear(gl.DEPTH_BUFFER_BIT);this.sky(re,rt,[0,-1,0],sim.time,aspect,fov);this.sceneUniforms(this.reflectVP,re,1,sim);this.drawMeshes(true);}
   gl.bindFramebuffer(gl.FRAMEBUFFER,this.scene.fb);gl.viewport(0,0,this.scene.w,this.scene.h);gl.clear(gl.DEPTH_BUFFER_BIT);this.sky(eyeLocal,targetLocal,[0,1,0],sim.time,aspect,fov);this.sceneUniforms(this.vp,eyeLocal,0,sim);this.drawMeshes(true);
   gl.bindFramebuffer(gl.FRAMEBUFFER,null);gl.viewport(0,0,this.canvas.width,this.canvas.height);gl.disable(gl.DEPTH_TEST);gl.useProgram(this.postProgram);gl.bindVertexArray(this.emptyVAO);gl.activeTexture(gl.TEXTURE0);gl.bindTexture(gl.TEXTURE_2D,this.scene.tex);gl.uniform1i(this.uniform(this.postProgram,'uScene'),0);gl.uniform2f(this.uniform(this.postProgram,'uResolution'),this.canvas.width,this.canvas.height);gl.uniform1f(this.uniform(this.postProgram,'uTime'),sim.time);gl.uniform1f(this.uniform(this.postProgram,'uRain'),this.rain);gl.uniform1f(this.uniform(this.postProgram,'uBloom'),this.bloom);gl.uniform1f(this.uniform(this.postProgram,'uDamage'),Math.max((100-sim.player.health)/100,sim.actor().hit||0));gl.drawArrays(gl.TRIANGLES,0,3);
  }
  project(x,y,z){return D.M4.project(this.vp,[x-(this.renderOrigin?.[0]||0),y,z-(this.renderOrigin?.[1]||0)]);}
 }
 D.Renderer=Renderer;
})(DC);
