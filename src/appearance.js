/* Identity belongs to the save, not to renderer global state. All data is whitelisted. */
'use strict';
(function(D){
 const palette=(list)=>Object.freeze(list.map(([name,rgb,hex])=>Object.freeze({name,rgb:Object.freeze(rgb),hex})));
 const skin=palette([['Arena',[.63,.425,.30],'#c5a07d'],['Trigo',[.50,.32,.21],'#ad805f'],['Cobre',[.40,.235,.143],'#9c6949'],['Umber',[.255,.128,.075],'#78503a'],['Ébano',[.145,.070,.043],'#553b30'],['Marfil',[.72,.51,.405],'#d8b79e'],['Oliva',[.44,.30,.18],'#ac8b63'],['Bronce',[.33,.18,.10],'#926146']]);
 const hair=palette([['Negro',[.014,.011,.009],'#201d1b'],['Castaño',[.063,.033,.017],'#64412e'],['Avellana',[.14,.077,.031],'#967045'],['Ceniza',[.22,.20,.17],'#a7a095'],['Plateado',[.36,.38,.39],'#c1c7c9'],['Cobrizo',[.18,.061,.026],'#ae6444']]);
 const coats=palette([['Petróleo',[.060,.135,.13],'#346866'],['Pizarra',[.085,.105,.15],'#475771'],['Arcilla',[.20,.100,.068],'#885c47'],['Hueso',[.44,.42,.33],'#b4b19b'],['Grafito',[.035,.045,.050],'#323d43'],['Borgoña',[.13,.033,.053],'#662e40'],['Salvia',[.16,.205,.12],'#758666']]);
 const pants=palette([['Índigo',[.045,.062,.094],'#3a4b61'],['Carbón',[.022,.029,.036],'#29333e'],['Tierra',[.115,.085,.060],'#665747'],['Piedra',[.24,.245,.23],'#89918a']]);
 const eyes=palette([['Ámbar',[.16,.094,.025],'#a78347'],['Café',[.085,.045,.021],'#6c4c35'],['Gris',[.12,.17,.18],'#829ea4'],['Verde',[.095,.14,.067],'#779b63']]);
 const hairstyles=Object.freeze(['Corto clásico','Rapado','Peinado hacia atrás','Sin cabello','Corto texturizado','Degradado alto','Media melena','Flequillo lateral','Undercut asimétrico','Recogido corto','Melena recta']);
 const baseline={version:1,skin:1,hair:1,coat:0,pants:0,eyes:1,hairStyle:0,build:0,face:0,neck:0,neckLength:0,hairVolume:0,browMatch:true};
 function defaults(){return {...baseline};}
 function valid(q){return !!q&&q.version===1&&[[skin,'skin'],[hair,'hair'],[coats,'coat'],[pants,'pants'],[eyes,'eyes'],[hairstyles,'hairStyle']].every(([p,k])=>Number.isInteger(q[k])&&q[k]>=0&&q[k]<p.length)&&['build','face'].every(k=>Number.isFinite(q[k])&&Math.abs(q[k])<=1)&&['neck','neckLength','hairVolume'].every(k=>q[k]===undefined||(Number.isFinite(q[k])&&Math.abs(q[k])<=1))&&(q.browMatch===undefined||typeof q.browMatch==='boolean');}
 function copy(q){if(!valid(q))throw new Error('La apariencia no es válida o pertenece a otra versión.');return Object.fromEntries(Object.keys(baseline).map(k=>[k,q[k]??baseline[k]]));}
 function name(value,fallback='Alex'){return typeof value==='string'?(value.normalize('NFC').replace(/[\u0000-\u001f\u007f-\u009f]/g,'').trim().replace(/\s+/g,' ').slice(0,32)||fallback):fallback;}
 const presets=Object.freeze([
  {id:'nomada',name:'Nómada',tag:'Petróleo · contorno ligero',look:{...baseline,build:-.25,face:-.24}},
  {id:'nacar',name:'Nácar',tag:'Piedra · volumen equilibrado',look:{...baseline,skin:3,hair:0,coat:3,pants:3,eyes:0,hairStyle:1,build:.20,face:.50}},
  {id:'aurora',name:'Aurora',tag:'Salvia · perfil definido',look:{...baseline,skin:5,hair:5,coat:6,pants:2,eyes:3,hairStyle:2,build:-.10,face:-.65}},
  {id:'asfalto',name:'Asfalto',tag:'Grafito · contorno amplio',look:{...baseline,skin:2,hair:4,coat:4,pants:1,eyes:2,hairStyle:0,build:.7,face:.2}}
 ].map(p=>Object.freeze({...p,look:Object.freeze(p.look)})));
 // Volume morphs leave wrists, finger bones and the soles untouched. Skeleton/IK lengths do not change.
 function shapePoint(point,mat,build=0,face=0,neck=0){
  let [x,y,z]=point;const smooth=(a,b,v)=>{let t=D.clamp((v-a)/(b-a),0,1);return t*t*(3-2*t);};
  if(mat===31||mat===32||mat===3){
   const body=smooth(.91,.98,y)*(1-smooth(1.40,1.49,y)),leg=(1-smooth(.79,.91,y))*smooth(.10,.24,y),arm=smooth(.17,.235,Math.abs(x))*smooth(.92,1.01,y)*(1-smooth(1.40,1.45,y));
   const center=(arm*(.2637-(y-.885)*.072)+leg*.108)*Math.sign(x);
   const scale=1+build*(body*.14*(1-arm)+arm*.13+leg*.13);x=center+(x-center)*scale;z*=1+build*(body*.18+leg*.13);z+=build*.006*body*Math.exp(-Math.pow((y-1.10)/.12,2));
  }
  if(mat===40||mat===31){
   const jawGuard=smooth(.035,.092,z)*smooth(1.530,1.549,y);
   let mask=smooth(1.446,1.482,y)*(1-smooth(1.560,1.615,y));
   mask*=mat===40?1-jawGuard:(1-smooth(.095,.145,Math.abs(x)))*(1-smooth(.092,.140,Math.abs(z+.010)));
   const ns=1+(neck*.09+build*.055)*mask;x*=ns;z=-.010+(z+.010)*ns;
  }
  if(mat===40){const jaw=Math.exp(-Math.pow((y-1.60)/.043,2));x*=1+face*.075*jaw;z+=Math.exp(-Math.pow(x/.019,2)-Math.pow((y-1.645)/.029,2))*face*.002;}
  return [x,y,z];
 }
 function actorLook(n,player=false,sim=null){
  if(player)return copy(sim?.appearance||n.appearance||defaults());
  const v=Math.abs(n.variant||0),look={...baseline,skin:v%skin.length,hair:v%hair.length,coat:v%coats.length,pants:v%pants.length,eyes:v%eyes.length,hairStyle:v%hairstyles.length,hairVolume:Math.sin(v*3.11)*.5,neckLength:Math.sin(v*1.87)*.5,build:Math.sin(v*2.4)*.65,face:Math.sin(v*1.73)*.7,neck:Math.sin(v*2.73)*.45};return look;
 }
 D.Appearance=Object.freeze({skin,hair,coats,pants,eyes,hairstyles,presets,default:defaults,copy,valid,name,actorLook,shapePoint});
 const Base=D.Simulation;
 class IdentitySimulation extends Base{
  constructor(world){super(world);this.appearance=defaults();this.characterName='Alex';}
  setIdentity(label,look){this.appearance=copy(look);this.characterName=name(label);}
  serialize(){const data=super.serialize();data.identity={version:1,name:this.characterName,look:copy(this.appearance)};return data;}
  restore(data){
   const identity=data?.identity;
   if(identity!==undefined&&(!identity||identity.version!==1||typeof identity.name!=='string'||identity.name.length>128||!valid(identity.look)))return false;
   if(!super.restore(data))return false;
   this.setIdentity(identity?.name||'Alex',identity?.look||defaults());return true;
  }
 }
 D.IdentitySimulation=IdentitySimulation;D.Simulation=IdentitySimulation;
})(DC);
