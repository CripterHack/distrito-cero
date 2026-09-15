/* Render-only projection of reactive state. Meshes are authored locally / in Higgsfield. */
'use strict';
(function(D){
 const Base=D.Renderer;
 class ReactiveRenderer extends Base{
  constructor(...args){super(...args);this.reducedMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
   this.assetParts=[];
   // Smoke is a soft, depth-tested billboard pass, never an opaque sphere or a shadow caster.
   const quad=[-.5,-.5,0,0,0,1,0,0,.5,-.5,0,0,0,1,1,0,.5,.5,0,0,0,1,1,1,-.5,-.5,0,0,0,1,0,0,.5,.5,0,0,0,1,1,1,-.5,.5,0,0,0,1,0,1];
   const sm=this.createMesh(quad);sm.chunks=[];sm.dynamicBuffer=this.gl.createBuffer();sm.transparent=true;this.meshes.smoke=sm;this.static.smoke=[];this.dynamic.smoke=[];
   for(const part of D.VehicleAsset?.parts||[]){const raw=atob(part.data),bytes=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)bytes[i]=raw.charCodeAt(i);const data=new Float32Array(bytes.buffer),key='asset_'+part.name;
    const mesh=this.createMesh(data);mesh.chunks=[];mesh.dynamicBuffer=this.gl.createBuffer();this.meshes[key]=mesh;this.static[key]=[];this.dynamic[key]=[];this.assetParts.push({...part,key});
   }
  }
  renderCar(c){
   D.ensureVehicle(c);const near=D.distance(c,this.currentSim?.player||c)<66;
   if(!near||!this.assetParts.length){super.renderCar(c);return;}
   const L=this.dynamic,a=c.yaw,co=Math.cos(a),si=Math.sin(a),col=c.color,body=c.suspension;
   const pitch=body.pitch+Math.sin(this.currentTime*20)*(body.kick||0),roll=body.roll;
   const rotate=(x,y,z)=>{y-=.6;const yy=y*Math.cos(pitch)-z*Math.sin(pitch),zz=y*Math.sin(pitch)+z*Math.cos(pitch),xx=x*Math.cos(roll)-yy*Math.sin(roll),y2=x*Math.sin(roll)+yy*Math.cos(roll);return[c.x+xx*co+zz*si,y2+.6,c.z-xx*si+zz*co];};
   const put=(mesh,x,y,z,sx,sy,sz,color,mat=0,em=0,yaw=0,spin=0)=>{const q=rotate(x,y,z);this.add(L,mesh,...q,sx,sy,sz,color,mat,c.empUntil>this.currentTime?0:em,a+yaw,0,0,pitch+spin,roll);};
   const damage=c.damage,sideNames=['front','rear','left','right'],dominant=sideNames.reduce((best,k)=>damage[k]>damage[best]?k:best,'front'),d=damage[dominant];
   const open=c.boarding?c.doorOpen||0:c.doorUntil>this.currentTime?Math.sin(D.clamp((c.doorUntil-this.currentTime)/.85,0,1)*Math.PI):0;
   for(const part of this.assetParts){
    const glass=part.name.startsWith('GLASS');if(glass&&damage.front>.88&&part.name==='GLASS_windshield')continue;
    if(open>.05&&((part.name==='GLASS_side_L'&&c.doorSide<0)||(part.name==='GLASS_side_R'&&c.doorSide>0)))continue;
    const q=rotate(0,0,0);this.add(L,part.key,...q,1,1,1,glass?[.055,.13,.16]:col,glass?6:5,part.name==='BODY_shell'&&open>.04?-open:0,a,d,100+sideNames.indexOf(dominant),pitch,roll);
   }
   if(this.meshes.roof)put('roof',0,0,0,1,1,1,col,5);else put('body',0,1.53,-.25,1.40,.095,1.27,col,5);
   if(!this.meshes.roof)put('body',0,.95+damage.front*.09,1.44,1.36,.038,.85*(1-damage.front*.3),col.map(x=>x*(1-damage.front*.3)),5,0,0,-damage.front*.18);
   put('body',0,.937,-1.76,1.37,.036,.63*(1-damage.rear*.25),col,5,0,0,damage.rear*.14);
   put('body',0,.48,2.17-damage.front*.4,1.57,.21,.13,[.025,.034,.04],3);
   put('body',0,.48,-2.19+damage.rear*.4,1.6,.17,.12,[.025,.034,.04],3);
   put('box',0,.69,2.205-damage.front*.4,.78,.14,.026,[.018,.022,.03],3);
   for(let k=0;k<5;k++)put('box',0,.645+k*.024,2.222-damage.front*.4,.71,.012,.008,[.22,.30,.32],3);
   for(const side of [-1,1]){
    const sd=damage[side<0?'left':'right'],opening=c.doorSide===side?open:0,da=-side*opening*1.12;
    const doorX=side*.944-.85*Math.sin(da),doorZ=.78-.85*Math.cos(da);
    put('body',doorX-side*sd*.12,.81,doorZ,.035,.30,1.7,col,5,0,da);
    put('body',side*.946,.34,-.17,.06,.11,2.07,[.024,.034,.038],3);
    put('box',doorX+side*.023,.96,doorZ-.48,.03,.036,.21,[.33,.40,.42],3,0,da);
    if(opening>.05)put(this.meshes.glassPanel?'glassPanel':'body',doorX,.123+1.1,doorZ,.028,.40,1.25,[.055,.13,.16],6,0,da);
    put('body',side*1.065,1.1,.62,.22,.14,.27,col,5);
    put('box',side*.755,1.27,-.4,.044,.54,.06,[.025,.03,.037],3);
    put('body',side*.761,1.255,.715,.045,.79,.045,col,5,0,0,-.77);put('body',side*.760,1.255,-1.03,.064,.69,.051,col,5,0,0,.61);
    put('body',side*.66,.79-damage.front*.06,2.105-damage.front*.42,.36,.105,.058,damage.front>.75?[.055,.08,.09]:[.70,.90,1],0,damage.front>.75?0:5);
    put('body',side*.65,.77,-2.16+damage.rear*.35,.37,.09,.045,[.8,.025,.016],0,damage.rear>.85?0:c.brake?6:2);
    for(const front of [-1,1]){
     const z=front>0?1.36:-1.39,steer=front>0?c.steerAngle:0;
     put(this.meshes.tire?'tire':'wheel',side*.92,.365,z,.27,.73,.73,[.018,.023,.028],4,0,steer,c.wheel||0);
     put(this.meshes.rim?'rim':'wheel',side*1.052,.365,z,.025,.528,.528,[.3,.39,.43],3,0,steer,c.wheel||0);
     put('wheel',side*1.066,.365,z,.026,.42,.42,[.025,.034,.045],3,0,steer);
     for(let k=0;k<5;k++){const theta=(c.wheel||0)+k*Math.PI*2/5,dy=Math.cos(theta)*.145,dz=Math.sin(theta)*.145;put('body',side*1.085,.365+dy,z+dz,.030,.27,.041,[.38,.44,.47],3,0,steer,theta);}
     put('wheel',side*1.09,.365,z,.035,.14,.14,[.36,.4,.42],3,0,steer);
    }
    put('body',side*.37,.53,-.16,.48,.15,.57,[.05,.065,.067]);put('body',side*.37,.84,-.44,.45,.60,.16,[.043,.052,.056]);
   }
   put('body',0,.89,.67,1.44,.16,.30,[.024,.031,.037],4);if(this.meshes.steeringRing){const w=D.VehicleCabin?.wheel||{x:-.38,y:.995,z:.31,tilt:-.48};put('steeringRing',w.x,w.y,w.z,1,1,1,[.02,.025,.031],4,0,0,w.tilt);}
   if(damage.front>.28){for(let i=0;i<9;i++){const x=-.35+i*.085;put('box',x,1.10+(i%3)*.085,.76-i*.065,.014,.014,.22,[.49,.63,.67],3,0,.6+i*.2);}}
   if(d>.4){for(let k=0;k<8;k++){const front=dominant==='front'||dominant==='rear',sign=dominant==='rear'||dominant==='left'?-1:1;put('box',front?-.45+k*.11:sign*.943,.64+(k%3)*.039,front?sign*(2.08-d*.36):-.35+k*.09,front?.07:.02,.012,front?.012:.13,[.21,.26,.27],3);}}
   if(c.police){put('box',0,1.64,-.25,.90,.08,.23,[.027,.04,.05],3);const blink=Math.sin(this.currentTime*13+c.id)>0;put('body',-.24,1.72,-.25,.38,.13,.22,[.08,.25,1],0,blink?8:1);put('body',.24,1.72,-.25,.38,.13,.22,[1,.02,.012],0,blink?1:8);}
  }
  renderPlayer(sim){
   const p=sim.player,t=p.transition;
   if(t){const c=sim.cars[t.carIndex],f=D.clamp(t.elapsed/t.duration,0,1),e=f*f*(3-2*f),co=Math.cos(c.yaw),si=Math.sin(c.yaw),seat={x:c.x-.37*co,z:c.z+.37*si-.12};
    const from=t.enter?t.from:seat,to=t.enter?seat:t.to;
    this.renderPerson({...p,x:D.lerp(from.x,to.x,e),z:D.lerp(from.z,to.z,e),y:t.enter?-e*.05:-(1-e)*.05,yaw:D.turn(t.from.yaw,c.yaw,e*4),moveSpeed:1.5,walk:f*4,reach:.8,seated:t.enter?f>.8:f<.2,crouch:Math.sin(f*Math.PI)*.5},true);return;
   }
   if(p.car===null){this.renderPerson(p,true);return;}
   const c=sim.actor(),co=Math.cos(c.yaw),si=Math.sin(c.yaw);this.renderPerson({...p,x:c.x-.37*co,z:c.z+.37*si-.12,y:-.045,yaw:c.yaw,seated:true,moveSpeed:0,crouch:0,reach:.7},true);
  }
  renderReactive(sim){
   const env=sim.dynamics;if(!env)return;const L=this.dynamic,player=sim.player;
   for(const p of env.hash.query(player.x,player.z,this.quality==='eco'?105:155)){
    const col=p.color,s=p.scale||1;
    const put=(mesh,x,y,z,sx,sy,sz,color=col,mat=0,em=0,pitch=0,roll=0,yaw=0)=>{
     let X=x,Y=y,Z=z,a=p.yaw;
     if(p.hinged){const xx=x,yy=y*Math.cos(p.angle)-z*Math.sin(p.angle),zz=y*Math.sin(p.angle)+z*Math.cos(p.angle);X=xx;Y=yy;Z=zz;a=p.fallYaw;pitch+=p.angle;}
     const co=Math.cos(a),si=Math.sin(a);this.add(L,mesh,p.x+(X*co+Z*si)*s,p.y+Y*s+.02,p.z+(-X*si+Z*co)*s,sx*s,sy*s,sz*s,color,mat,em,a+yaw,0,0,pitch,roll);
    };
    if(p.type==='lamp'){
     put('body',0,.22,0,.40,.44,.40,col,3);if(this.meshes.lampMast)put('lampMast',0,0,0,1,1,1,col,3);else put('body',0,3.6,0,.12,7.2,.12,col,3);put('body',0,7.2,.82,.13,.15,1.8,col,3);put('body',0,7.18,1.5,.56,.12,.88,col,3);put('box',0,7.105,1.5,.45,.025,.73,(p.broken||p.empUntil>sim.time)?[.14,.15,.13]:p.warm?[1,.74,.42]:[.42,.73,1],0,(p.broken||p.empUntil>sim.time)?0:6);
     if(p.broken)put('body',0,.6,0,.19,.13,.19,[.25,.27,.23],3);
    }else if(p.type==='tree'){
     if(this.renderTreeDetail){this.renderTreeDetail(p,put);continue;}put('body',0,1.8,0,.32,3.6,.32,col);for(let i=0;i<5;i++){const a=i*2.4,r=.4+(i%2)*.48;put('body',Math.cos(a)*r*.35,3.2+i*.12,Math.sin(a)*r*.35,.15,1.7,.15,col,0,0,.35,-.35,a);put('sphere',Math.cos(a)*r,4.05+(i%3)*.42,Math.sin(a)*r,2.25+(i%2)*.4,2.1,2.4,[.075,.145+(i%3)*.016,.10],8);}
    }else if(p.type==='crate'){
     if(p.broken){for(let k=0;k<4;k++)put('body',(k-1.5)*.17,.06,Math.sin(k)*.23,.40,.075,.12,col,0,0,.03*k,.05*k,k*.7);}else{put('body',0,.32,0,.67,.64,.67,col);for(let k of [-1,1]){put('box',k*.22,.32,.347,.058,.64,.024,[.17,.13,.07]);put('box',k*.22,.32,-.347,.058,.64,.024,[.17,.13,.07]);}put('box',0,.65,0,.25,.018,.23,[.64,.57,.39],3);}
    }else if(p.type==='bin'){
     const tilt=p.broken?1.3:Math.min(.3,Math.hypot(p.vx,p.vz)*.04);put('body',0,p.broken?.23:.48,0,.72,p.broken?.32:.94,.68,col,3,0,tilt);put('body',0,p.broken?.22:.98,.08,.80,.10,.76,[.10,.29,.28],3,0,tilt);if(!p.broken)put('box',0,.59,.35,.28,.18,.012,[.60,.73,.58]);
    }else if(p.type==='cone'){
     put('body',0,.04,0,.49,.08,.49,[.05,.06,.05],4);for(let k=0;k<6;k++)put('body',0,p.broken?.10:.12+k*.078,0,.34-k*.045,.08,.34-k*.045,k===3?[.79,.83,.78]:col,0,0,p.broken?1.5:0);
    }else if(p.type==='bench'){
     for(let k=0;k<4;k++)put('body',0,p.broken?.13:.53,k*.16-.25,1.65,.08,.13,col,0,0,0,p.broken?k*.1:0);if(!p.broken){for(const side of [-1,1])put('body',side*.62,.26,0,.08,.48,.57,[.07,.09,.085],3);put('body',0,.85,-.36,1.65,.45,.07,col);}
    }
   }
   const eye=this.camera.eye;
   for(const f of [...env.particles].sort((a,b)=>Math.hypot(b.x-eye[0],b.z-eye[2])-Math.hypot(a.x-eye[0],a.z-eye[2]))){
    if(D.distance(f,player)>100)continue;const smoke=f.material==='smoke',fade=D.clamp(f.life/f.total,0,1);
    if(smoke){const dx=eye[0]-f.x,dz=eye[2]-f.z,dy=eye[1]-f.y,alpha=Math.sin((1-fade)*Math.PI)*.48;
     this.add(L,'smoke',f.x,f.y,f.z,f.size*2.8,f.size*2.8,1,[.17,.19,.20],9,alpha,Math.atan2(dx,dz),f.angle,0,-Math.atan2(dy,Math.hypot(dx,dz)),0);
    }else this.add(L,'body',f.x,f.y,f.z,f.size*2,f.size,f.size,f.color,0,f.material==='metal'?fade*2.4:0,0,0,0,f.angle,f.angle*.7);
   }
   for(const m of env.marks)if(D.distance(m,player)<100)this.add(L,'box',m.x,-.008,m.z,.19,.012,.8,[.012,.016,.018],4,0,m.yaw);
  }
  updateCamera(sim,dt,options={}){
   super.updateCamera(sim,dt,options);
   if(!options.menu&&!options.photo&&!this.reducedMotion&&sim.trauma>0){const a=sim.trauma*sim.trauma*.10,t=sim.time;this.camera.eye[0]+=Math.sin(t*83)*a;this.camera.eye[1]+=Math.sin(t*67)*a;}
  }
 }
 D.Renderer=ReactiveRenderer;
})(DC);
