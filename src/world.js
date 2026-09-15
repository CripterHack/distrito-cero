'use strict';
(function(D){
 class World{
  constructor(seed=1337){
   this.seed=seed;this.size=840;this.half=420;this.spacing=84;this.buildings=[];this.blocks=[];this.lights=[];this.props=[];this.rand=D.rng(seed);
   this.pois=[{type:'safe',name:'Refugio de Lía',x:-84,z:264},{type:'garage',name:'Taller del Mercado',x:168,z:96},{type:'garage',name:'Mecánica del Muelle',x:-252,z:-72},{type:'job',name:'Encargos de mensajería',x:0,z:-72},{type:'race',name:'Circuito nocturno',x:-168,z:12},{type:'terminal',name:'Terminal Vértice',x:252,z:-72},{type:'safe',name:'Muelle de los Olvidos',x:-252,z:-156}];
   const r=this.rand;
   for(let ix=-5;ix<5;ix++)for(let iz=-5;iz<5;iz++){
    const cx=(ix+.5)*84,cz=(iz+.5)*84,park=(ix===-2&&iz===0)||(ix===1&&iz===-3);
    this.blocks.push({x:cx,z:cz,park,seed:r()});
    if(park)continue;
    for(let a=0;a<2;a++)for(let b=0;b<2;b++){
     let x=cx+(a-.5)*29,z=cz+(b-.5)*29,w=20+r()*6,d=20+r()*6;
     const downtown=Math.exp(-((cx-95)**2+(cz+70)**2)/90000);
     let h=9+Math.pow(r(),1.5)*45+downtown*26,style=Math.floor(r()*4),tone=r();
     if(r()<.08)h+=30;
     this.buildings.push({x,z,w,d,h,style,tone,seed:r()*500,sign:Math.floor(r()*12)});
    }
   }
   for(let n=-5;n<=5;n++)for(let j=-5;j<5;j++){
    for(let s of [-1,1]){
     this.lights.push({x:n*84+s*12.5,z:(j+.25)*84,y:7.6,warm:(n+j)%3!==0});
     this.lights.push({x:(j+.72)*84,z:n*84+s*12.5,y:7.6,warm:(n+j)%3===0});
    }
   }
   this.crates=[];
   for(let i=0;i<16;i++){
    let ix=Math.floor(r()*9)-4,iz=Math.floor(r()*9)-4;
    this.crates.push({x:ix*84+13,z:iz*84+30+r()*24,id:i});
   }
  }
  nearby(x,z,r=10){return this.buildings.filter(b=>Math.abs(b.x-x)<b.w/2+r&&Math.abs(b.z-z)<b.d/2+r);}
  blocked(x,z,r=.5){return Math.abs(x)>this.half+8||Math.abs(z)>this.half+8||this.nearby(x,z,r).some(b=>D.circleBox(x,z,r,b));}
  move(x,z,dx,dz,r){let p=D.moveCircle(x,z,dx,dz,r,this.nearby(x,z,Math.hypot(dx,dz)+r));p.x=D.clamp(p.x,-426+r,426-r);p.z=D.clamp(p.z,-426+r,426-r);return p;}
  visible(ax,az,bx,bz){return !this.buildings.some(b=>D.segmentBox(ax,az,bx,bz,b,.1));}
  node(x,z){return{x:D.clamp(Math.round(x/84),-5,5)*84,z:D.clamp(Math.round(z/84),-5,5)*84};}
  route(ax,az,bx,bz){
   const start=this.node(ax,az),end=this.node(bx,bz),path=[start];let x=start.x,z=start.z;
   let horizontal=Math.abs(bx-ax)>Math.abs(bz-az);
   while(x!==end.x||z!==end.z){if((horizontal&&x!==end.x)||z===end.z)x+=Math.sign(end.x-x)*84;else z+=Math.sign(end.z-z)*84;path.push({x,z});horizontal=!horizontal;}
   return path;
  }
  district(x,z){if(x<-170)return'MUELLE DE LOS OLVIDOS';if(z<-130)return'DISTRITO FINANCIERO';if(z>150)return'BARRIO DEL MERCADO';if(x>180)return'ZONA VÉRTICE';return'CENTRO / DISTRITO CERO';}
 }
 D.World=World;
})(DC);
