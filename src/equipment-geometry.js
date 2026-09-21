/* Original, shared equipment meshes. Metric fictional silhouettes, never a fabrication model. */
'use strict';
(function(D){
 const steel=[.13,.18,.21],dark=[.035,.052,.060],grip=[.030,.038,.041],silver=[.43,.51,.55],cyan=[.14,.72,1],amber=[.8,.46,.12];
 const specs={};
 for(const w of D.Equipment.catalog){const parts=[];const box=(p,s,c=steel,m=3,role='body')=>parts.push({kind:'box',p,s,c,m,role});const tube=(p,r,len,c=steel,m=3,inner=0)=>parts.push({kind:'tube',p,r,len,c,m,inner});
  if(w.kind==='none'){specs[w.id]=parts;continue;}
  if(w.kind==='optics'){
   box([0,-.008,.025],[.18,.025,.07],dark);for(const side of [-1,1]){tube([side*.064,0,.05],.050,.15,dark,4);tube([side*.064,0,.117],.052,.018,silver);tube([side*.064,0,.128],.043,.004,[.035,.22,.27],6);tube([side*.064,0,-.052],.027,.06,grip,4);}tube([0,.028,.017],.017,.035,silver);
  }else if(w.id==='baton'){
   tube([0,0,.21],.025,.52,dark,3);tube([0,0,-.08],.031,.16,grip,4);tube([0,0,.003],.040,.019,silver);for(let j=0;j<6;j++)tube([0,0,-.13+j*.022],.033,.006,steel,4);
  }else if(w.id==='blade'){
   box([0,-.004,-.085],[.045,.047,.16],grip,4);box([0,0,.007],[.10,.030,.016],silver);parts.push({kind:'blade',c:silver,m:3});
  }else if(w.id==='grenade'){
   tube([0,0,.01],.059,.14,[.14,.19,.12],4);tube([0,0,.085],.03,.022,steel);box([0,.035,.03],[.017,.035,.14],silver);for(let z=-.04;z<.07;z+=.025)tube([0,0,z],.062,.003,dark);
  }else{
   const sidearm=['pistol','revolver'].includes(w.id),tech=['emp','gauss'].includes(w.id),len=w.length;
   box([0,0,.08],[sidearm?.061:tech?.15:.10,sidearm?.07:.115,sidearm?.23:.31],tech?dark:steel);
   parts.push({kind:'grip',p:[0,-.11,-.016],s:[.060,.17,.080],c:grip,m:4,role:'grip'});box([0,-.055,.052],[.026,.065,.024],silver);box([0,-.086,.066],[.059,.019,.11],dark);
   if(w.id==='pistol')box([0,-.18,-.016],[.056,.08,.072],dark,3,'magazine');
   if(!sidearm){box([0,-.135,.12],[.058,.18,.095],dark,3,['smg','rifle','sniper','gauss','emp'].includes(w.id)?'magazine':'body');if(w.id==='rifle'){box([0,-.050,-.15],[.048,.052,.15],grip,4);box([0,-.0745,-.2295],[.052,.079,.018],dark);}else{box([0,-.012,-.14],[.064,.097,.14],grip,4);box([0,-.012,-.222],[.068,.14,.033],dark);}}
   const barrelStart=sidearm?.21:.26,barrelLength=len-barrelStart;
   if(w.id==='launcher'){
    tube([0,.06,.16],.105,.98,dark,4,.067);tube([0,.06,.68],.11,.035,silver,3,.067);box([.11,.065,.07],[.04,.047,.15],[.07,.25,.20]);
   }else if(w.id==='gauss'){
    box([0,.012,.36],[.145,.115,.50],steel);for(const x of[-.074,.074])box([x,.012,.52],[.024,.09,.64],silver);
    for(let j=0;j<7;j++){tube([0,.012,.24+j*.080],.11,.032,steel,3,.054);tube([0,.012,.26+j*.080],.088,.012,cyan,0,.059);}
    box([0,.078,.10],[.10,.015,.105],cyan,0);tube([0,.012,.83],.07,.045,dark,3,.043);
   }else if(w.id==='emp'){
    tube([0,.035,.21],.122,.23,steel,3,.065);tube([0,.035,.35],.13,.038,silver,3,.055);tube([0,.035,.34],.057,.05,cyan,0);
    for(const x of[-.135,.135])box([x,.038,.21],[.025,.13,.23],dark);box([0,.117,.08],[.085,.016,.09],cyan,0);
   }else{
    tube([0,.014,barrelStart+barrelLength/2],sidearm?.018:.019,barrelLength,steel,3,.008);tube([0,.014,len-.012],.028,.042,dark,3,.010);
    if(w.id==='revolver')tube([0,-.025,.08],.057,.09,silver);if(w.id==='shotgun')tube([0,-.045,.31],.034,.22,grip,4);
    if(w.id==='smg'||w.id==='rifle'||w.id==='sniper'){box([0,.066,.15],[.047,.019,.28],dark);for(let j=0;j<7;j++)box([0,.079,.045+j*.03],[.06,.009,.010],silver);}
    if(w.id==='sniper'){tube([0,.133,.12],.036,.28,dark);tube([0,.133,.275],.047,.054,silver,3,.029);tube([0,.133,.30],.028,.004,[.04,.2,.24],6);box([0,.085,.07],[.046,.075,.026],steel);}
    else{box([0,.062,sidearm?.22:.42],[.012,.035,.023],dark);box([0,.061,-.01],[.045,.025,.013],dark);}
    if(!sidearm)box([0,-.005,.31],[.09,.08,.20],grip,4);
   }
   for(const x of[-1,1]){box([x*(tech?.077:.053),-.006,.06],[.006,.031,.055],silver);for(let j=0;j<3;j++)box([x*.032,-.075-j*.033,-.016],[.006,.007,.064],steel,4);}
  }
  specs[w.id]=parts;
 }
 function build(id){const buckets=new Map(),out=[];
  for(const p of specs[id]||[]){const key=(p.role||'body')+':'+p.m+':'+p.c.join(),v=buckets.get(key)||{name:'part'+buckets.size,role:p.role||'body',material:p.m,color:p.c,data:[]};buckets.set(key,v);
   const tri=(a,b,c,na,nb,nc)=>{const n=na||D.normalize(D.cross(b.map((v,i)=>v-a[i]),c.map((v,i)=>v-a[i])));for(const [q,norm]of[[a,n],[b,nb||n],[c,nc||n]])v.data.push(...q,...norm,q[2],q[1]);};
   if(p.kind==='box'){const [x,y,z]=p.p,[a,b,c]=p.s.map(v=>v*.5),pts=[[-a,-b,-c],[a,-b,-c],[a,b,-c],[-a,b,-c],[-a,-b,c],[a,-b,c],[a,b,c],[-a,b,c]].map(q=>[q[0]+x,q[1]+y,q[2]+z]);for(const f of[[0,3,2,1],[4,5,6,7],[0,4,7,3],[1,2,6,5],[3,7,6,2],[0,1,5,4]]){tri(pts[f[0]],pts[f[1]],pts[f[2]]);tri(pts[f[0]],pts[f[2]],pts[f[3]]);}}
   if(p.kind==='grip'){
    const N=20,[x,y,z]=p.p,[rx,h,rz]=[p.s[0]/2,p.s[1],p.s[2]/2],ring=[[-.5,.78],[-.44,.96],[0,1],[.44,.96],[.5,.78]];
    const pt=(j,i)=>{const a=i*2*Math.PI/N,[v,r]=ring[j];return[x+rx*r*Math.cos(a),y+v*h,z+rz*r*Math.sin(a)];};
    const normal=(j,i)=>{const a=i*2*Math.PI/N,lo=Math.max(0,j-1),hi=Math.min(ring.length-1,j+1),slope=(ring[hi][1]-ring[lo][1])/((ring[hi][0]-ring[lo][0])*h);return D.normalize([Math.cos(a)/rx,-slope,Math.sin(a)/rz]);};
    for(let j=0;j<ring.length-1;j++)for(let i=0;i<N;i++){const A=pt(j,i),B=pt(j,i+1),C=pt(j+1,i+1),F=pt(j+1,i),na=normal(j,i),nb=normal(j,i+1),nc=normal(j+1,i+1),nf=normal(j+1,i);tri(A,F,C,na,nf,nc);tri(A,C,B,na,nc,nb);}
    for(let i=0;i<N;i++){tri([x,y-h/2,z],pt(0,i),pt(0,i+1),[0,-1,0],[0,-1,0],[0,-1,0]);tri([x,y+h/2,z],pt(ring.length-1,i+1),pt(ring.length-1,i),[0,1,0],[0,1,0],[0,1,0]);}
   }
   if(p.kind==='blade'){const a=[-.026,0,.015],b=[.026,0,.015],c=[.016,0,.22],tip=[-.017,0,.32],t=[0,.006,.15],u=[0,-.006,.15];for(const [s,e]of[[a,b],[b,c],[c,tip],[tip,a]]){tri(s,e,t);tri(e,s,u);}}
   if(p.kind==='tube'){const [x,y,z]=p.p,lo=z-p.len*.5,hi=z+p.len*.5,N=16,r=p.r,ri=p.inner||0;for(let i=0;i<N;i++){const a=i*2*Math.PI/N,b=(i+1)*2*Math.PI/N,pt=(ang,rad,zz)=>[x+Math.cos(ang)*rad,y+Math.sin(ang)*rad,zz],A=pt(a,r,lo),B=pt(b,r,lo),C=pt(b,r,hi),F=pt(a,r,hi),na=[Math.cos(a),Math.sin(a),0],nb=[Math.cos(b),Math.sin(b),0];tri(A,B,C,na,nb,nb);tri(A,C,F,na,nb,na);
     if(ri){const aa=pt(a,ri,lo),bb=pt(b,ri,lo),cc=pt(b,ri,hi),ff=pt(a,ri,hi);tri(bb,aa,ff);tri(bb,ff,cc);tri(F,C,cc);tri(F,cc,ff);tri(B,A,aa);tri(B,aa,bb);}else{tri([x,y,hi],F,C);tri([x,y,lo],B,A);}}}
  }
  for(const p of buckets.values())out.push({...p,data:new Float32Array(p.data)});return out;
 }
 function icon(id){if(id==='unarmed')return'<svg viewBox="0 0 160 64" aria-hidden="true"><path d="M57 51V28c0-6 7-6 7 0V14c0-5 7-5 7 0v13V10c0-5 7-5 7 0v17V13c0-5 7-5 7 0v20l7-7c5-4 10 1 6 6L83 51Z" fill="currentColor"/></svg>';
  if(id==='binoculars')return'<svg viewBox="0 0 160 64" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="4"><circle cx="57" cy="37" r="19"/><circle cx="103" cy="37" r="19"/><circle cx="57" cy="37" r="12"/><circle cx="103" cy="37" r="12"/><path d="m39 31 6-20h22l6 20m12 0 7-20h22l7 20M74 25h12"/></g></svg>';
  const p=specs[id]||[],pts=p.flatMap(s=>(s.kind==='box'||s.kind==='grip')?[s.p[2]-s.s[2]/2,s.p[2]+s.s[2]/2]:s.kind==='tube'?[s.p[2]-s.len/2,s.p[2]+s.len/2]:[0,.32]),min=Math.min(...pts),max=Math.max(...pts),scale=130/Math.max(.5,max-min),x=z=>15+(z-min)*scale,y=h=>28-h*scale;
  const shapes=p.map(s=>(s.kind==='box'||s.kind==='grip')?`<rect x="${x(s.p[2]-s.s[2]/2)}" y="${y(s.p[1]+s.s[1]/2)}" width="${s.s[2]*scale}" height="${s.s[1]*scale}" rx="1"/>`:s.kind==='tube'?`<rect x="${x(s.p[2]-s.len/2)}" y="${y(s.p[1]+s.r)}" width="${s.len*scale}" height="${s.r*2*scale}" rx="2"/>`:`<path d="M${x(.01)} 27 L${x(.25)} 27 L${x(.32)} 31 L${x(.01)} 34Z"/>`).join('');return`<svg viewBox="0 0 160 64" aria-hidden="true"><g fill="currentColor">${shapes}</g></svg>`;
 }
 D.EquipmentGeometry=Object.freeze({build,icon});
})(DC);
