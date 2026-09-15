/* Character draft + named local sessions. Preview never replaces the live simulation. */
'use strict';
(function(D){
 const $=id=>document.getElementById(id),Base=D.App,A=D.Appearance;
 const safeFile=s=>(s||'partida').normalize('NFKD').replace(/[^a-z0-9_-]+/gi,'-').slice(0,55);
 const date=n=>new Date(n).toLocaleString('es-MX',{dateStyle:'medium',timeStyle:'short'});
 class IdentityApp extends Base{
  constructor(){
   super();this.activeSlot=null;this.detached=false;this.creator=null;this.saveNotice='';
   $('start').onclick=()=>this.openCreator(false);$('freeRoam').onclick=()=>this.openCreator(true);
   $('continue').onclick=()=>this.start(true);
   $('landingSaves').onclick=()=>this.openLibrary('menu');$('pauseSaves').onclick=()=>this.openLibrary('pause');
   $('editAppearance').onclick=()=>{if(!this.started){this.openCreator(false);return;}if(this.sim.access){this.toast('Termina o cancela el acceso al coche antes de editar el personaje.');return;}this.openCreator(this.sim.free,true);};
   $('newGame').textContent='Nueva partida independiente';$('newGame').onclick=()=>this.openCreator(false);
   $('closeCreator').onclick=()=>this.cancelCreator();$('commitCreator').onclick=()=>this.commitCreator(false);
   $('playVolatile').onclick=()=>this.commitCreator(true);$('creatorForm').onsubmit=e=>{e.preventDefault();this.commitCreator(false);};
   $('closeLibrary').onclick=()=>this.closeLibrary();$('libraryNew').onclick=()=>{this.closeLibrary();this.openCreator(false);};
   $('libraryImport').onclick=()=>$('saveFile').click();$('libraryExportAll').onclick=()=>this.exportCatalogue();
   $('librarySaveCopy').onclick=()=>this.saveCopy();$('librarySaveCurrent').onclick=()=>{this.save(true);this.paintLibrary();};
   $('exportRawCatalogue').onclick=()=>{try{this.download(new Blob([this.getStore().raw()||''],{type:'application/json'}),'distrito-cero-catalogo-recuperacion.json');}catch(e){this.libraryMessage(e.message,true);}};
   $('characterName').oninput=()=>this.previewChanged();$('newSaveName').oninput=()=>this.creatorMessage('Tu apariencia y progreso se guardarán juntos.');
   for(const [id,key]of[['characterBuild','build'],['characterFace','face'],['characterNeck','neck'],['characterNeckLength','neckLength'],['characterHairVolume','hairVolume']])$(id).oninput=e=>{if(!this.creator)return;this.creator.look[key]=Number(e.target.value)/100;this.creator.preset=-1;this.previewChanged();};
   for(const [i,name] of A.hairstyles.entries()){const o=document.createElement('option');o.value=i;o.textContent=name;$('characterHairStyle').append(o);}
   $('characterHairStyle').onchange=e=>{this.creator.look.hairStyle=Number(e.target.value);this.creator.preset=-1;this.previewChanged();};
   $('characterBrowMatch').onchange=e=>{if(this.creator){this.creator.look.browMatch=e.target.checked;this.previewChanged();}};
   $('characterPose').onchange=()=>this.previewChanged();
   $('characterTempo').onchange=()=>{};
   $('characterFocus').onchange=e=>this.focusCreator(e.target.value);
   $('characterLight').onchange=e=>this.lightCreator(e.target.value);
   $('compareAppearance').onclick=()=>{const c=this.creator;if(!c)return;c.comparing=!c.comparing;this.showComparison();};
   $('librarySearch').oninput=()=>this.paintLibrary();$('librarySort').onchange=()=>this.paintLibrary();$('previewLeft').onclick=()=>{this.creator.yaw-=Math.PI/6;};$('previewRight').onclick=()=>{this.creator.yaw+=Math.PI/6;};
   $('previewFrame').onclick=()=>this.focusCreator(this.creator.faceFrame?'full':'face');
   $('previewMotion').onclick=()=>{this.creator.animate=!this.creator.animate;this.syncPreviewMotion();};
   $('randomAppearance').onclick=()=>{const c=this.creator,r=()=>Math.random();for(const [key,p]of[['skin',A.skin],['hair',A.hair],['coat',A.coats],['pants',A.pants],['eyes',A.eyes],['hairStyle',A.hairstyles]])c.look[key]=Math.floor(r()*p.length);c.look.build=Math.round((r()*2-1)*100)/100;c.look.face=Math.round((r()*2-1)*100)/100;c.preset=-1;this.syncCreator();};
   $('resetAppearance').onclick=()=>{this.choosePreset(this.creator.preset>=0?this.creator.preset:0);};
   $('mainMenu').onclick=()=>{if(this.started&&!this.detached&&!this.save(false)){this.openLibrary('pause');return;}this.setMode('menu');this.refreshContinue();};
   $('exploreHorizon').onclick=()=>{if(!this.started){this.openCreator(true,false,true);return;}this.openMap();};
   $('applySeed').onclick=()=>{const seed=Number($('worldSeed').value);if(!Number.isInteger(seed)||seed<-2147483648||seed>2147483647){$('mapHint').textContent='La semilla debe ser un entero válido.';return;}this.openCreator(true,false,false,seed);};
   this.buildCreatorChoices();this.bindCreatorInput();this.refreshContinue();
   window.addEventListener('storage',e=>{if(e.key===D.SaveStore.KEY){this.refreshContinue();if(this.mode==='saves')this.paintLibrary();}});
   window.addEventListener('keydown',e=>{
    if(!['creator','saves'].includes(this.mode))return;
    if(e.code==='Escape'){e.preventDefault();if(this.mode==='creator')this.cancelCreator();else this.closeLibrary();return;}
    if(e.code==='Tab'){const panel=$(this.mode==='creator'?'identityCreator':'saveLibrary'),list=[...panel.querySelectorAll('button,input,select')].filter(n=>!n.disabled&&n.getClientRects().length);const first=list[0],last=list.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}}
   });
  }
  getStore(){
   if(!this.slotStore){this.slotStore=new D.SaveStore({getItem:k=>globalThis.localStorage.getItem(k),setItem:(k,v)=>globalThis.localStorage.setItem(k,v)});try{this.slotStore.migrateLegacy();}catch(e){this.storeError=e.message;}}
   return this.slotStore;
  }
  readSave(){try{return this.getStore().active()?.data||null;}catch(e){this.storeError=e.message;return null;}}
  refreshContinue(){const saved=this.readSave();$('continue').hidden=!saved;$('start').textContent='Crear personaje ↗';if(saved){try{const slot=this.getStore().active();$('continue').textContent='Continuar · '+slot.name;}catch(e){}}}
  setMode(mode){
   super.setMode(mode);$('identityCreator').hidden=mode!=='creator';$('saveLibrary').hidden=mode!=='saves';
   if(mode==='creator'||mode==='saves'){$('hud').hidden=true;$('tutorial').hidden=true;$('touchControls').hidden=true;}
   document.body.classList.toggle('creating',mode==='creator');
   if(mode==='pause')this.updateSaveStatus();
  }
  updateSaveStatus(){const node=$('activeSaveStatus');if(!node)return;let name='Sin partida activa';try{name=this.activeSlot?this.getStore().get(this.activeSlot.id)?.name||'Partida eliminada':'Sin partida activa';}catch(e){name='Almacenamiento no disponible';}node.textContent=this.saveNotice||(this.started?(this.detached?'SESIÓN SIN GUARDAR · Exporta una copia.':'Activa: '+name):'Inicia una historia para guardar.');}
  adopt(sim,slot,fresh=false){
   this.sim=sim;this.world=sim.world;this.renderer.world=sim.world;this.activeSlot=slot?{id:slot.id,revision:slot.revision}:null;this.detached=!slot;this.started=true;this.crouched=false;this.autoSave=0;this.saveNotice=slot?'Guardada · '+slot.name:'Sin guardado local. Exporta tu partida desde Pausa.';
   this.renderer.resetSectors();this.renderer.camera.initialized=false;this.renderer.camera.yaw=sim.player.yaw;this.renderer.camera.pitch=.22;this.renderer.lightTime=-1;this.atlasCenter=null;this.mapPaintTag=null;this.refreshStops();this.audio.start();this.setMode('play');this.refreshContinue();
   if(fresh){this.chapter(sim.free?'TU PROPIO CAMINO':'LA LLAMADA');$('tutorialText').textContent='WASD para moverte. F para entrar o salir del coche. E para interactuar. M abre el atlas. Esc abre Pausa, tu personaje y tus partidas.';$('tutorial').hidden=false;this.tutorialUntil=performance.now()+14000;}
  }
  start(resume=false,free=false){
   try{
    if(resume){const saved=this.getStore().active();if(!saved)throw new Error('No hay una partida guardada.');return this.loadSlot(saved.id);}
    const sim=new D.Simulation(new D.World(this.world.seed));sim.free=free;const slot=this.getStore().create('Nueva historia '+(this.getStore().list().length+1),sim.serialize());this.adopt(sim,slot,true);
   }catch(e){this.toast(e.message);}
  }
  save(feedback=false){
   if(!this.started||this.mode==='creator')return false;
   if(this.detached||!this.activeSlot){if(feedback)this.openLibrary(this.mode==='menu'?'menu':'pause');return false;}
   try{const slot=this.getStore().update(this.activeSlot.id,this.sim.serialize(),this.activeSlot.revision);this.activeSlot.revision=slot.revision;this.saveNotice='Guardada · '+slot.name+' · '+new Date(slot.updated).toLocaleTimeString('es-MX');this.updateSaveStatus();if(feedback)this.toast(this.saveNotice);this.storageWarning=false;return true;}
   catch(e){this.saveNotice=e.message;this.updateSaveStatus();if(feedback||!this.storageWarning)this.toast(e.message);this.storageWarning=true;if(this.mode==='saves')this.libraryMessage(e.message,true);return false;}
  }
  openLibrary(returnMode){
   if(this.creator)this.cancelCreator();this.libraryReturn=returnMode||this.mode;this.setMode('saves');$('copySaveName').value=this.started?this.sim.characterName+' · otra ruta':'';this.paintLibrary();$('closeLibrary').focus();
  }
  closeLibrary(){this.setMode(this.libraryReturn||'menu');if(this.mode==='menu')this.refreshContinue();}
  libraryMessage(text,error=false){$('libraryMessage').textContent=text;$('libraryMessage').classList.toggle('error',error);}
  paintLibrary(){
   const panel=$('saveCards');panel.replaceChildren();$('libraryCopyRow').hidden=!this.started;$('librarySaveCurrent').disabled=!this.activeSlot||this.detached;
   try{const total=this.getStore().read().slots.length,slots=this.getStore().list({query:$('librarySearch').value,sort:$('librarySort').value});$('libraryCount').textContent=($('librarySearch').value?slots.length+' resultado(s) · ':'')+total+' / 12 partidas';$('exportRawCatalogue').hidden=true;$('libraryNew').disabled=total>=12;$('libraryExportAll').disabled=!total;
    this.libraryMessage(this.saveNotice||'Cada historia tiene su personaje, semilla y progreso. Importar crea una partida nueva.');
    if(!slots.length){const box=document.createElement('div');box.className='library-empty';box.innerHTML=total?'<h3>No hay coincidencias.</h3><p class="identity-note">Prueba otro nombre o borra la búsqueda. Las partidas siguen guardadas.</p>':'<h3>La ciudad todavía no conoce tu nombre.</h3><p class="identity-note">Crea tu primer personaje o importa una partida anterior.</p>';panel.append(box);}
    for(const s of slots){
     const card=document.createElement('article');card.className='save-card'+(s.id===this.activeSlot?.id?' active':'');card.dataset.slot=s.id;
     const top=document.createElement('div');top.className='slot-eyebrow';const t=document.createElement('span');t.textContent=s.id===this.activeSlot?.id?'EN ESTA SESIÓN':'HISTORIA GUARDADA';const when=document.createElement('span');when.textContent=date(s.updated);top.append(t,when);
     const row=document.createElement('div');row.className='slot-name-row';const input=document.createElement('input');input.className='slot-name';input.value=s.name;input.maxLength=48;input.setAttribute('aria-label','Nombre de la partida '+s.name);const rename=document.createElement('button');rename.textContent='Renombrar';rename.onclick=()=>{try{const fresh=this.getStore().rename(s.id,input.value,s.revision);if(this.activeSlot?.id===s.id&&this.activeSlot.revision===s.revision)this.activeSlot.revision=fresh.revision;this.saveNotice='Nombre actualizado: '+fresh.name;this.paintLibrary();this.refreshContinue();}catch(e){this.libraryMessage(e.message,true);}};row.append(input,rename);
     const details=document.createElement('div');details.className='slot-details';const ident=s.data.identity||{name:'Alex',look:A.default()},line=document.createElement('div');line.textContent=ident.name;const colors=document.createElement('span');colors.className='slot-palette';for(const [p,key]of[[A.skin,'skin'],[A.hair,'hair'],[A.coats,'coat'],[A.pants,'pants']]){const c=document.createElement('i');c.style.background=p[ident.look?.[key]]?.hex||'#777';colors.append(c);}line.append(colors);const meta=document.createElement('div');meta.textContent=(s.data.free?'Exploración libre':'Capítulo '+Math.min(6,s.data.story+1)+' / 6')+' · $'+Math.floor(s.data.cash).toLocaleString('es-MX');const world=document.createElement('div');world.textContent='Semilla '+(s.data.horizon?.seed??1337)+' · '+((s.data.stats?.distance||0)/1000).toFixed(1)+' km';details.append(line,meta,world);
     const actions=document.createElement('div');actions.className='slot-actions';
     const button=(text,cls,fn)=>{const b=document.createElement('button');b.textContent=text;b.className=cls;b.onclick=fn;actions.append(b);return b;};
     button(s.id===this.activeSlot?.id?(s.revision===this.activeSlot.revision?'Reanudar ↗':'Recargar ↗'):'Jugar ↗','slot-load',()=>this.loadSlot(s.id));
     button('Duplicar','slot-duplicate',()=>{try{const copy=this.getStore().duplicate(s.id,s.name+' · copia');this.saveNotice='Copia creada: '+copy.name;this.paintLibrary();}catch(e){this.libraryMessage(e.message,true);}});
     button('Exportar','slot-export',()=>this.exportSlot(s.id));
     button('Eliminar','slot-delete',()=>{if(!confirm('¿Eliminar «'+s.name+'» de este navegador? No se puede deshacer. Exporta una copia antes.'))return;try{this.getStore().remove(s.id,s.revision);if(this.activeSlot?.id===s.id){this.activeSlot=null;this.detached=true;}this.saveNotice='Partida eliminada. Las demás no se modificaron.';this.paintLibrary();this.refreshContinue();}catch(e){this.libraryMessage(e.message,true);}});
     card.append(top,row,details,actions);panel.append(card);
    }
   }catch(e){$('libraryCount').textContent='Almacenamiento no disponible';this.libraryMessage(e.message,true);$('exportRawCatalogue').hidden=false;$('libraryExportAll').disabled=true;}
  }
  loadSlot(id){
   try{
    const slot=this.getStore().get(id);if(!slot)throw new Error('La partida ya no existe.');
    if(this.started&&this.activeSlot?.id===id){
     if(this.activeSlot.revision===slot.revision){this.setMode('play');return;}
     if(!confirm('Esta partida tiene una versión guardada más reciente. ¿Cargarla y descartar los cambios sin guardar de esta sesión? Guarda una copia para conservarlos.'))return;
    }
    const sim=new D.Simulation(new D.World());if(!sim.restore(slot.data))throw new Error('No se pudo cargar: la partida no es válida.');
    if(this.started&&this.activeSlot?.id!==id&&!this.detached&&!this.save(false))throw new Error('No se pudo guardar la sesión actual. Exporta o guarda una copia antes de cambiar de partida.');
    this.getStore().activate(id);this.adopt(sim,slot,false);
   }catch(e){if(this.mode==='saves')this.libraryMessage(e.message,true);else this.toast(e.message);}
  }
  saveCopy(){try{const slot=this.getStore().create($('copySaveName').value,this.sim.serialize());this.activeSlot={id:slot.id,revision:slot.revision};this.detached=false;this.saveNotice='Copia guardada: '+slot.name;this.paintLibrary();this.refreshContinue();}catch(e){this.libraryMessage(e.message,true);}}
  exportSlot(id){try{const s=this.getStore().get(id);if(!s)throw new Error('La partida ya no existe.');this.download(new Blob([JSON.stringify({format:'distrito-cero-slot',version:1,name:s.name,data:s.data},null,2)],{type:'application/json'}),'distrito-cero-'+safeFile(s.name)+'.json');this.libraryMessage('Copia JSON preparada: '+s.name);}catch(e){this.libraryMessage(e.message,true);}}
  exportSave(){if(!this.started){this.openLibrary('pause');return;}let name=this.sim.characterName+' · sesión';try{name=this.getStore().get(this.activeSlot?.id)?.name||name;}catch(e){}this.download(new Blob([JSON.stringify({format:'distrito-cero-slot',version:1,name,data:this.sim.serialize()},null,2)],{type:'application/json'}),'distrito-cero-'+safeFile(name)+'.json');this.toast('Copia JSON de la sesión preparada.');}
  exportCatalogue(){try{const data=this.getStore().exportAll();this.download(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),'distrito-cero-todas-las-partidas.json');this.libraryMessage('Respaldo preparado. Incluye las versiones guardadas de '+data.slots.length+' partidas.');}catch(e){this.libraryMessage(e.message,true);}}
  async importSave(file){
   if(!file)return;
   try{if(file.size>32000000)throw new Error('Archivo demasiado grande.');const data=JSON.parse(await file.text());let items;
    if(data.format==='distrito-cero-collection'){if(data.version!==1)throw new Error('Versión de respaldo no compatible.');items=data.slots;}
    else if(data.format==='distrito-cero-slot'){if(data.version!==1)throw new Error('Versión de partida no compatible.');items=[{name:data.name,data:data.data}];}
    else items=[{name:(file.name||'Partida importada').replace(/\.json$/i,''),data}];
    const imported=this.getStore().createMany(items,{activate:!this.started});this.saveNotice=imported.length+' partida(s) importada(s). Ninguna anterior fue reemplazada.';if(this.mode!=='saves')this.openLibrary(this.mode==='menu'?'menu':'pause');else this.paintLibrary();this.refreshContinue();
   }catch(e){if(this.mode!=='saves')this.openLibrary(this.mode==='menu'?'menu':'pause');this.libraryMessage('No se importó el archivo: '+e.message,true);}finally{$('saveFile').value='';}
  }
  buildCreatorChoices(){
   for(const [i,p]of A.presets.entries()){const b=document.createElement('button');b.type='button';b.className='preset-choice';b.dataset.preset=i;b.setAttribute('aria-pressed','false');const strong=document.createElement('strong');strong.textContent=p.name;const small=document.createElement('small');small.textContent=p.tag;const dot=document.createElement('i');dot.style.background=A.coats[p.look.coat].hex;b.append(strong,small,dot);b.onclick=()=>this.choosePreset(i);$('presetChoices').append(b);}
   for(const [key,p]of[['skin',A.skin],['hair',A.hair],['coat',A.coats],['pants',A.pants],['eyes',A.eyes]])for(const[i,c]of p.entries()){const b=document.createElement('button');b.type='button';b.className='swatch';b.dataset.key=key;b.dataset.value=i;b.title=c.name;b.setAttribute('aria-label',c.name);b.setAttribute('aria-pressed','false');const fill=document.createElement('i');fill.style.background=c.hex;b.append(fill);b.onclick=()=>{this.creator.look[key]=i;this.previewChanged();};$(key+'Choices').append(b);}
  }
  bindCreatorInput(){
   const view=$('creatorViewport');view.addEventListener('pointerdown',e=>{if(e.target.closest('button'))return;this.creator.pointer={id:e.pointerId,x:e.clientX};view.setPointerCapture(e.pointerId);});view.addEventListener('pointermove',e=>{const p=this.creator?.pointer;if(!p||e.pointerId!==p.id)return;this.creator.yaw-=(e.clientX-p.x)*.009;p.x=e.clientX;});const end=()=>{if(this.creator)this.creator.pointer=null;};view.addEventListener('pointerup',end);view.addEventListener('pointercancel',end);view.addEventListener('lostpointercapture',end);
   view.addEventListener('wheel',e=>{if(!this.creator)return;e.preventDefault();this.creator.distance=D.clamp(this.creator.distance+e.deltaY*.0015,this.creator.focus==='hands'?.22:this.creator.faceFrame?.40:this.creator.focus==='neck'?.65:1.6,this.creator.focus==='hands'?.8:this.creator.faceFrame?1.1:this.creator.focus==='neck'?1.7:3.3);},{passive:false});
   this.creatorObserver=new ResizeObserver(()=>{if(this.creator)this.fitCreator();});this.creatorObserver.observe(view);
  }
  openCreator(free=false,edit=false,atlas=false,seed=this.world.seed){
   if(this.creator)return;if(edit&&this.sim.access)return;
   const preview=new D.Simulation(new D.World(1337));preview.free=true;preview.player.x=0;preview.player.z=0;preview.player.yaw=0;preview.peds.forEach(n=>n.hidden=true);preview.cars.forEach(c=>{c.x=5000;c.z=5000;});preview.dynamics.props=[];preview.world.lights=[{x:-3,y:4,z:3,warm:true},{x:3,y:3,z:2,warm:false},{x:1,y:3,z:-3,warm:false}];preview.dynamics.lightActive=()=>true;
   const r=this.renderer;
   this.creator={returnMode:this.mode,edit,free,atlas,seed,preview,focus:'full',comparing:false,preset:edit?-1:0,look:edit?A.copy(this.sim.appearance):A.copy(A.presets[0].look),yaw:.18,distance:2.15,faceFrame:false,animate:!r.reducedMotion,snapshot:{world:r.world,camera:{...r.camera,eye:[...r.camera.eye],target:[...r.camera.target]},rain:r.rain,bloom:r.bloom,daylight:r.daylight},elapsed:1};
   r.world=preview.world;r.previewStudio=true;r.rain=0;r.bloom=0;r.daylight=.64;r.lightTime=-1;r.lightVP=null;
   $('characterName').value=edit?this.sim.characterName:'Alex';$('newSaveName').value='Mi primera noche';$('saveNameLabel').hidden=edit;$('newSaveName').required=!edit;$('characterPose').value='idle';$('characterTempo').value='1';$('previewFrame').textContent='Ver rostro';$('commitCreator').textContent=edit?'Aplicar cambios ↗':free?'Comenzar exploración ↗':'Comenzar historia ↗';$('creatorMode').textContent=edit?'EDITANDO ESTA SESIÓN':(free?'EXPLORACIÓN LIBRE':'HISTORIA · CAPÍTULO 01')+' · SEMILLA '+seed;$('playVolatile').hidden=true;
   this.creator.initialLook=A.copy(this.creator.look);this.creator.initialName=$('characterName').value;$('characterFocus').value='full';$('characterLight').value='neutral';this.setMode('creator');this.syncCreator();this.lightCreator('neutral');this.creatorMessage(edit?'Cancelar conserva tu apariencia anterior. Aplicar actualiza sólo esta partida.':'Crea otra historia sin borrar las anteriores.');this.fitCreator();$('closeCreator').focus();
  }
  choosePreset(i){this.creator.preset=i;this.creator.look=A.copy(A.presets[i].look);this.syncCreator();}
  syncCreator(){const c=this.creator;$('characterBuild').value=Math.round(c.look.build*100);$('characterFace').value=Math.round(c.look.face*100);$('characterHairStyle').value=c.look.hairStyle;$('characterNeck').value=Math.round((c.look.neck||0)*100);$('characterNeckLength').value=Math.round((c.look.neckLength||0)*100);$('characterHairVolume').value=Math.round((c.look.hairVolume||0)*100);$('characterBrowMatch').checked=c.look.browMatch;this.syncPreviewMotion();this.previewChanged();}
  syncPreviewMotion(){const a=!!this.creator?.animate;$('previewMotion').setAttribute('aria-pressed',String(a));$('previewMotion').textContent=a?'Pausar pose':'Animar pose';}
  previewChanged(){const c=this.creator;if(!c)return;c.comparing=false;$('compareAppearance').setAttribute('aria-pressed','false');$('compareAppearance').textContent='Comparar con el inicio';$('comparisonHint').textContent='Mostrando tus cambios. Comparar no modifica la partida.';c.preview.setIdentity($('characterName').value,c.look);$('previewName').textContent=c.preview.characterName;$('previewPreset').textContent=c.preset>=0?A.presets[c.preset].name:'A medida';$('buildValue').textContent=c.look.build<-.28?'Ligera':c.look.build>.28?'Amplia':'Equilibrada';$('neckValue').textContent=(c.look.neck||0)<-.28?'Fino':(c.look.neck||0)>.28?'Robusto':'Neutro';$('faceValue').textContent=c.look.face<-.28?'Estrecho':c.look.face>.28?'Ancho':'Neutro';
   $('neckLengthValue').textContent=c.look.neckLength<-.28?'Compacta':c.look.neckLength>.28?'Extendida':'Integrada';
   $('hairVolumeValue').textContent=c.look.hairVolume<-.28?'Contenido':c.look.hairVolume>.28?'Amplio':'Natural';
   const fixedHair=c.look.hairStyle===1||c.look.hairStyle===3;$('characterHairVolume').disabled=fixedHair;
   if(fixedHair)$('hairVolumeValue').textContent='No aplica';
   $('hairStyleHint').textContent=['Largo corto uniforme, dirección peinada y línea de nacimiento irregular.','Superficie de cabello muy corta. Sin mechones largos.','Volumen frontal y mechones orientados hacia la nuca.','Cuero cabelludo visible. Las cejas permanecen independientes.','Mechones elevados, volumen desigual y contorno quebrado.','Laterales muy cortos con altura concentrada en la parte superior.','Capas sueltas y cabello más largo junto a orejas y nuca.','Flequillo dirigido a un costado, sin cambiar los rasgos faciales.','Lado corto contrastado con un mechón lateral largo.','Mechones hacia atrás y recogido pequeño en la nuca.','Capas rectas laterales y traseras, con el frente despejado.'][c.look.hairStyle];for(const b of $('presetChoices').children)b.setAttribute('aria-pressed',String(Number(b.dataset.preset)===c.preset));for(const b of document.querySelectorAll('.swatch'))b.setAttribute('aria-pressed',String(c.look[b.dataset.key]===Number(b.dataset.value)));}
  showComparison(){
   const c=this.creator;if(!c)return;c.preview.setIdentity(c.comparing?c.initialName:$('characterName').value,c.comparing?c.initialLook:c.look);
   $('compareAppearance').setAttribute('aria-pressed',String(c.comparing));$('compareAppearance').textContent=c.comparing?'Volver a los cambios':'Comparar con el inicio';$('comparisonHint').textContent=c.comparing?'Vista inicial. Tu borrador sigue intacto.':'Mostrando tus cambios. Comparar no modifica la partida.';
  }
  focusCreator(focus){
   const c=this.creator;if(!c)return;c.focus=focus;c.faceFrame=focus==='face';c.distance={full:2.15,face:.59,neck:1.04,hands:.39,feet:1.24}[focus]||2.15;c.yaw=focus==='hands'?.86:.18;$('characterFocus').value=focus;$('previewFrame').textContent=c.faceFrame?'Ver cuerpo':'Ver rostro';
  }
  lightCreator(mode){
   const c=this.creator;if(!c)return;const r=this.renderer;
   r.daylight=mode==='side'?.14:mode==='outdoor'?.73:.50;
   c.preview.world.lights=mode==='side'?[{x:-1.6,y:2.8,z:2,warm:true},{x:1.5,y:2.3,z:-1.2,warm:false}]:[{x:-3,y:4,z:3,warm:true},{x:3,y:3,z:2,warm:false},{x:1,y:3,z:-3,warm:false}];
   r.lightTime=-1;r.lightVP=null;
  }
  creatorMessage(text,error=false){$('creatorMessage').textContent=text;$('creatorMessage').classList.toggle('error',error);}
  fitCreator(){
   if(!this.creator)return;const v=$('creatorViewport').getBoundingClientRect(),canvas=this.renderer.canvas;if(!v.width||!v.height)return;
   Object.assign(canvas.style,{position:'fixed',left:v.left+'px',top:v.top+'px',width:v.width+'px',height:v.height+'px'});this.renderer.previewSize={width:v.width,height:v.height};this.renderer.resize();
  }
  leaveCreator(){
   const c=this.creator;if(!c)return;const r=this.renderer;r.world=c.snapshot.world;r.camera=c.snapshot.camera;r.rain=c.snapshot.rain;r.bloom=c.snapshot.bloom;r.daylight=c.snapshot.daylight;r.previewStudio=false;r.previewSize=null;r.canvas.removeAttribute('style');r.lightTime=-1;r.lightVP=null;r.resize();this.creator=null;document.body.classList.remove('creating');this.renderDirty=true;
  }
  cancelCreator(){if(!this.creator)return;const mode=this.creator.returnMode;this.leaveCreator();this.setMode(mode==='creator'?'menu':mode);if(mode==='menu')$('start').focus();}
  commitCreator(volatile=false){
   if(!this.creator)return;const c=this.creator;
   try{
    if(!$('characterName').value.trim())throw new Error('Escribe un nombre para tu personaje.');
    const name=A.name($('characterName').value),look=A.copy(c.look);
    if(c.edit){
     const oldName=this.sim.characterName,old=A.copy(this.sim.appearance);this.sim.setIdentity(name,look);
     if(!this.detached&&this.activeSlot){try{const s=this.getStore().update(this.activeSlot.id,this.sim.serialize(),this.activeSlot.revision);this.activeSlot.revision=s.revision;this.saveNotice='Apariencia guardada · '+s.name;}catch(e){this.sim.setIdentity(oldName,old);throw e;}}
     this.leaveCreator();this.setMode('pause');return;
    }
    const saveName=D.cleanSaveName($('newSaveName').value),sim=new D.Simulation(new D.World(c.seed));sim.free=c.free;sim.setIdentity(name,look);let slot=null;
    if(!volatile){if(this.started&&!this.detached&&this.activeSlot){const prior=this.getStore().update(this.activeSlot.id,this.sim.serialize(),this.activeSlot.revision);this.activeSlot.revision=prior.revision;}slot=this.getStore().create(saveName,sim.serialize());}
    const atlas=c.atlas;this.leaveCreator();this.adopt(sim,slot,true);if(atlas)this.openMap();
   }catch(e){this.creatorMessage(e.message,true);$('playVolatile').hidden=!!c.edit||!(/almacenamiento|espacio|catálogo/i.test(e.message));}
  }
  updateUI(now){if(['creator','saves'].includes(this.mode))return;super.updateUI(now);}
  loop(now){
   if(this.mode!=='creator'||!this.creator){super.loop(now);return;}
   const dt=Math.max(0,Math.min(.05,(now-this.last)/1000));this.last=now;const c=this.creator,r=this.renderer,p=c.preview.player;
   const tempo=Number($('characterTempo').value)||1,step=c.animate?dt*tempo:0;
   if(c.animate)c.elapsed+=step;c.preview.time=c.elapsed;
   const pose=$('characterPose').value,poseTarget={moveSpeed:pose==='run'?6.1:pose==='walk'?1.4:0,sprintBlend:pose==='run'?1:0,crouch:pose==='crouch'?1:0,seatBlend:pose==='seated'?1:0,reach:pose==='reach'?1:0};
   for(const [k,v]of Object.entries(poseTarget))p[k]=c.animate?D.damp(p[k]||0,v,10,step):v;
   p.walk=(p.walk||0)+D.NaturalMotion.frequency(p.moveSpeed,p.sprintBlend,p.crouch)*step;p.seated=p.seatBlend>.98;p.y=-.29*p.seatBlend;p.grip=pose==='grip'?.82:pose==='hands'?0:undefined;
   // These are preview-only requests; the real simulation and saved identity stay unchanged.
   p.lookYaw=pose==='neck'?Math.sin(c.elapsed*.70)*.72:undefined;
   p.lookPitch=pose==='nod'?Math.sin(c.elapsed*.75)*.22:undefined;
   p.lookRoll=pose==='neck'?Math.sin(c.elapsed*.37)*.07:undefined;
   p.handTargets=pose==='seated'?D.VehicleCabin.hands({x:.38,z:.20,yaw:0,steerAngle:Math.sin(c.elapsed*.65)*.25}):pose==='reach'?{R:{x:.34,y:1.26,z:.36}}:undefined;
   const neckDrop=D.CharacterFit.drop(c.preview.appearance.neckLength);
   const ty=c.faceFrame?1.66-neckDrop:c.focus==='neck'?1.48-neckDrop*.45:c.focus==='feet'?.28:pose==='crouch'?.71:pose==='seated'?.7:.93;const d=c.distance*(c.focus!=='full'?1:Math.max(1,.92/(r.canvas.width/r.canvas.height)));
   let target=[0,ty,0],rise=c.faceFrame?.065:.18;
   if(c.focus==='hands'){const q=D.SkinRig.pose(p,c.preview.time),h=D.SkinRig.handPoint(q,p,'R');target=[h.x-.004,h.y-.082,h.z+.004];rise=.038;}
   r.camera.eye=[target[0]+Math.sin(c.yaw)*d,target[1]+rise,target[2]+Math.cos(c.yaw)*d];r.camera.target=target;
   try{r.render(c.preview);}catch(e){this.creatorMessage('No se pudo dibujar la vista previa: '+e.message,true);console.error(e);this.cancelCreator();}
   this.scheduleFrame();
  }
 }
 D.IdentityApp=IdentityApp;D.App=IdentityApp;
})(DC);
