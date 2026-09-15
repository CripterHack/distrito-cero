/* Named slots. One atomic localStorage value keeps index and snapshots together.
   No destructive fallback: corruption/quota/privacy failures leave prior bytes intact. */
'use strict';
(function(D){
 const KEY='distrito-cero:saves:v2',LEGACY='distrito-cero:save:v1',MAX=12;
 const clone=value=>JSON.parse(JSON.stringify(value));
 function label(value){if(typeof value!=='string')throw new Error('Escribe un nombre para la partida.');const n=value.normalize('NFC').replace(/[\u0000-\u001f\u007f-\u009f]/g,'').trim().replace(/\s+/g,' ').slice(0,48);if(!n)throw new Error('Escribe un nombre para la partida.');return n;}
 function validate(data){
  if(!data||typeof data!=='object'||JSON.stringify(data).length>2500000)throw new Error('Partida inválida o demasiado grande.');
  const world=new D.World(),probe=new D.Simulation(world);
  if(!probe.restore(data))throw new Error('El formato de partida es inválido.');
  return clone(probe.serialize());
 }
 class SaveStore{
  static KEY=KEY;static LEGACY=LEGACY;static MAX=MAX;
  constructor(storage){this.storage=storage;}
  raw(){try{return this.storage.getItem(KEY);}catch(e){throw new Error('El navegador bloquea el almacenamiento local. Exporta tu partida.');}}
  read(){
   const raw=this.raw();if(!raw)return{version:2,revision:0,activeId:null,migrated:false,slots:[]};
   try{const b=JSON.parse(raw),ids=new Set();if(b.version!==2||!Number.isSafeInteger(b.revision)||!Array.isArray(b.slots)||b.slots.length>MAX)throw 0;
    for(const s of b.slots){if(!s||typeof s.id!=='string'||s.id.length>100||ids.has(s.id)||typeof s.name!=='string'||!s.name.trim()||s.name.length>48||!Number.isSafeInteger(s.revision)||s.revision<1||![s.created,s.updated].every(Number.isFinite)||!s.data||s.data.version!==1)throw 0;ids.add(s.id);}
    if(b.activeId!==null&&!ids.has(b.activeId))throw 0;return b;
   }catch(e){throw new Error('El catálogo de partidas está dañado. No se ha reemplazado. Conserva una copia antes de recuperarlo.');}
  }
  commit(b){b.revision++;const raw=JSON.stringify(b);try{this.storage.setItem(KEY,raw);}catch(e){throw new Error('No se pudo guardar: almacenamiento bloqueado o sin espacio. Las partidas anteriores siguen intactas. Exporta una copia.');}return b;}
  list({query='',sort='recent'}={}){
   const fold=s=>String(s).normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLocaleLowerCase('es-MX');
   const term=fold(query).trim(),slots=clone(this.read().slots).filter(s=>!term||fold(s.name+' '+(s.data.identity?.name||'Alex')).includes(term));
   const byName=(a,b)=>a.name.localeCompare(b.name,'es-MX',{sensitivity:'base'})||a.id.localeCompare(b.id);
   return slots.sort(sort==='name'?byName:sort==='progress'?(a,b)=>(b.data.story||0)-(a.data.story||0)||b.updated-a.updated||byName(a,b):(a,b)=>b.updated-a.updated||byName(a,b));
  }
  get(id){const s=this.read().slots.find(x=>x.id===id);return s?clone(s):null;}
  active(){return this.get(this.read().activeId);}
  id(b){let id;do{id=globalThis.crypto?.randomUUID?.()||'dc-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,13);}while(b.slots.some(x=>x.id===id));return id;}
  create(name,data,{activate=true}={}){return this.createMany([{name,data}],{activate})[0];}
  createMany(items,{activate=true}={}){
   if(!Array.isArray(items)||!items.length||items.length>MAX)throw new Error('El archivo debe contener entre 1 y 12 partidas.');
   const entries=items.map(x=>({name:label(x.name),data:validate(x.data)})),b=this.read();
   if(b.slots.length+entries.length>MAX)throw new Error('Hay 12 espacios como máximo. Exporta y elimina una partida antes de crear otra.');
   const now=Date.now(),added=[];
   for(const e of entries){const s={id:this.id(b),name:e.name,revision:1,created:now,updated:now,data:e.data};b.slots.push(s);added.push(s);}
   if(activate)b.activeId=added[0].id;b.migrated=true;this.commit(b);return clone(added);
  }
  current(b,id,revision){const s=b.slots.find(x=>x.id===id);if(!s)throw new Error('Esta partida ya no existe. Guarda una copia nueva.');if(revision!==s.revision)throw new Error('Partida modificada en otra ventana: conflicto de revisión. Guarda una copia nueva o vuelve a cargarla.');return s;}
  update(id,data,revision){const clean=validate(data),b=this.read(),s=this.current(b,id,revision);s.data=clean;s.updated=Date.now();s.revision++;b.activeId=id;this.commit(b);return clone(s);}
  rename(id,name,revision){const clean=label(name),b=this.read(),s=this.current(b,id,revision);s.name=clean;s.revision++;this.commit(b);return clone(s);}
  remove(id,revision){const b=this.read();this.current(b,id,revision);b.slots=b.slots.filter(s=>s.id!==id);if(b.activeId===id)b.activeId=b.slots[0]?.id||null;this.commit(b);}
  duplicate(id,name){const s=this.get(id);if(!s)throw new Error('La partida ya no existe.');return this.create(name||s.name+' · copia',s.data,{activate:false});}
  activate(id){const b=this.read();if(!b.slots.some(x=>x.id===id))throw new Error('No existe esta partida.');b.activeId=id;this.commit(b);}
  migrateLegacy(){
   const b=this.read();if(b.migrated||b.slots.length)return false;
   let raw;try{raw=this.storage.getItem(LEGACY);}catch(e){throw new Error('El navegador bloquea el almacenamiento.');}
   if(!raw)return false;let data;try{data=JSON.parse(raw);}catch(e){return false;}
   try{validate(data);}catch(e){return false;}this.create('Partida anterior',data);return true;
  }
  exportAll(){return{format:'distrito-cero-collection',version:1,slots:this.list().map(s=>({name:s.name,data:s.data}))};}
 }
 D.SaveStore=SaveStore;D.cleanSaveName=label;D.validateSnapshot=validate;
})(DC);
