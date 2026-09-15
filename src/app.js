'use strict';
(function(D){
 const $=id=>document.getElementById(id);
 const SAVE_KEY='distrito-cero:save:v1',SETTINGS_KEY='distrito-cero:settings:v1';
 class App{
  constructor(){
   this.renderDirty=true;this.mode='menu';this.returnMode='play';this.started=false;this.keys=new Set();this.stick={x:0,y:0};this.lookUntil=0;this.drag=null;this.touchBrake=false;this.surrenderHeld=false;this.repairHeld=false;this.jumpHeld=false;this.crouched=false;this.toastQueue=[];this.toastUntil=0;this.chapterUntil=0;this.autoSave=0;this.accumulator=0;this.last=performance.now();this.fps=0;this.frameCount=0;this.lastUI=0;this.mapTransform=null;this.settings={quality:'balanced',sound:true,volume:50,rain:true,bloom:true,touch:null};
   try{let s=JSON.parse(localStorage.getItem(SETTINGS_KEY)||'null');if(s&&typeof s==='object')Object.assign(this.settings,s);}catch(e){}
   if(!['eco','balanced','high'].includes(this.settings.quality))this.settings.quality='balanced';
   this.world=new D.World(1337);this.sim=new D.Simulation(this.world);this.renderer=new D.Renderer($('world'),this.world,this.settings.quality);this.audio=new D.Audio();this.audio.enabled=!!this.settings.sound;this.audio.volume=D.clamp(Number(this.settings.volume)/100,0,1);this.renderer.rain=this.settings.rain?1:0;this.renderer.bloom=this.settings.bloom?1:0;
   this.touchAuto=matchMedia('(pointer: coarse)').matches||navigator.maxTouchPoints>0;this.setTouch(this.settings.touch??this.touchAuto);this.bind();this.syncSettings();this.refreshContinue();this.renderer.updateCamera(this.sim,0,{menu:true});this.renderer.render(this.sim);
   $('loading').hidden=true;this.setMode('menu');this.loop=this.loop.bind(this);this.scheduleFrame();
   globalThis.render_game_to_text=()=>JSON.stringify({mode:this.mode,player:this.sim.player,wanted:this.sim.wanted,heat:this.sim.heat,cash:this.sim.cash,story:this.sim.story,target:this.sim.target(),job:this.sim.job,police:this.sim.getPoliceStatus()});
   if(new URLSearchParams(location.search).has('debug')){globalThis.__DC_DEBUG=this;$('fps').hidden=false;}
  }
  setTouch(value){this.touch=!!value;document.body.classList.toggle('touch',this.touch);if($('touchToggle'))$('touchToggle').textContent=this.settings.touch===null?'AUTO':this.touch?'SÍ':'NO';}
  saveSettings(){this.renderDirty=true;try{localStorage.setItem(SETTINGS_KEY,JSON.stringify(this.settings));}catch(e){}}
  syncSettings(){
   $('quality').value=this.settings.quality;$('volume').value=this.settings.volume;$('soundToggle').textContent=this.settings.sound?'SÍ':'NO';$('rainToggle').textContent=this.settings.rain?'SÍ':'NO';$('bloomToggle').textContent=this.settings.bloom?'SÍ':'NO';$('landingAudio').textContent=this.settings.sound?'♫':'♪';$('landingAudio').setAttribute('aria-pressed',String(this.settings.sound));$('touchToggle').textContent=this.settings.touch===null?'AUTO':this.touch?'SÍ':'NO';
  }
  bind(){
   $('start').onclick=()=>{if(this.readSave()&&!confirm('¿Comenzar una nueva partida? El guardado anterior se reemplazará.'))return;this.start(false,false);};
   $('continue').onclick=()=>this.start(true,false);$('freeRoam').onclick=()=>{if(this.readSave()&&!confirm('¿Iniciar una nueva partida libre? El guardado anterior se reemplazará.'))return;this.start(false,true);};
   for(const id of ['landingSettings','landingControls','pauseButton'])$(id).onclick=()=>this.pause();
   $('landingAudio').onclick=()=>this.toggleSound();$('soundToggle').onclick=()=>this.toggleSound();
   $('closePause').onclick=()=>this.resume();$('resume').onclick=()=>this.resume();
   for(const id of ['mapButton','miniMapButton','openMapPause'])$(id).onclick=()=>this.openMap();
   $('closeMap').onclick=()=>this.setMode(this.mapReturn||'play');$('clearPin').onclick=()=>{this.sim.pin=null;this.sim.routeClock=0;this.drawMap(true);$('mapHint').textContent='GPS borrado. Se muestra el objetivo activo.';};
   $('photoFocus').onclick=()=>this.focusPhoto();$('photoButton').onclick=()=>this.photo();$('exitPhoto').onclick=()=>this.setMode('play');$('capture').onclick=()=>this.capture();
   $('saveGame').onclick=()=>this.save(true);$('mainMenu').onclick=()=>{if(this.started)this.save(false);this.setMode('menu');this.refreshContinue();};
   $('toggleStory').onclick=()=>{if(!this.started){this.start(false,true);return;}this.sim.free=!this.sim.free;this.sim.pin=null;this.setMode('play');this.toast(this.sim.free?'EXPLORACIÓN LIBRE · La historia está en pausa.':'HISTORIA ACTIVADA · Tu progreso continúa.');this.save(false);};
   $('newGame').onclick=()=>{if(confirm('¿Reiniciar esta partida? La historia y el dinero volverán a su estado inicial.'))this.start(false,false);};
   $('cancelJob').onclick=()=>{if(this.sim.job){this.sim.job=null;this.sim.pin=null;this.toast('Encargo cancelado.');}else this.toast('No hay ningún encargo activo.');};
   $('radioButton').onclick=()=>this.toggleRadio();$('context').onclick=()=>{const ctx=this.sim.getContext();if(ctx&&ctx.action)this.action(ctx.action==='car'?'car':'use');};
   $('dismissTutorial').onclick=()=>{$('tutorial').hidden=true;this.renderer.canvas.focus({preventScroll:true});};
   $('quality').onchange=e=>{this.settings.quality=e.target.value;this.renderer.quality=e.target.value;this.renderer.resize();this.saveSettings();};
   $('volume').oninput=e=>{this.settings.volume=Number(e.target.value);this.audio.setVolume(this.settings.volume/100);this.saveSettings();};
   $('rainToggle').onclick=()=>{this.settings.rain=!this.settings.rain;this.renderer.rain=this.settings.rain?1:0;this.syncSettings();this.saveSettings();};
   $('bloomToggle').onclick=()=>{this.settings.bloom=!this.settings.bloom;this.renderer.bloom=this.settings.bloom?1:0;this.syncSettings();this.saveSettings();};
   $('touchToggle').onclick=()=>{this.settings.touch=!this.touch;this.setTouch(this.settings.touch);this.saveSettings();};
   $('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else if(document.documentElement.requestFullscreen)await document.documentElement.requestFullscreen();else this.toast('La pantalla completa no está disponible en este navegador.');}catch(e){this.toast('El navegador no permitió entrar en pantalla completa.');}};
   $('exportSave').onclick=()=>this.exportSave();$('importSave').onclick=()=>$('saveFile').click();$('saveFile').onchange=e=>this.importSave(e.target.files[0]);
   window.addEventListener('keydown',e=>{
    if(e.code==='Tab'&&['pause','map','dialog'].includes(this.mode)){
     const panel=$(this.mode==='pause'?'pause':this.mode==='map'?'mapOverlay':'dialogue');const focusable=[...panel.querySelectorAll('button,input,select')].filter(el=>!el.hidden&&!el.disabled&&el.getClientRects().length);const first=focusable[0],last=focusable.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}return;
    }
    if(['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName))return;
    if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Tab'].includes(e.code)&&this.mode==='play'&&e.code!=='Tab')e.preventDefault();
    if([ $('surrenderButton'),$('repairButton') ].includes(document.activeElement)&&['Space','Enter'].includes(e.code))return;
    if(e.repeat)return;
    if(e.code==='Escape'){e.preventDefault();if(this.mode==='play')this.pause();else if(this.mode==='pause')this.resume();else if(this.mode==='map')this.setMode(this.mapReturn||'play');else if(this.mode==='photo')this.setMode('play');return;}
    if(e.code==='KeyM'&&(this.mode==='play'||this.mode==='map')){if(this.mode==='map')this.setMode('play');else this.openMap();return;}
    if(e.code==='KeyP'&&(this.mode==='play'||this.mode==='photo')){if(this.mode==='photo')this.setMode('play');else this.photo();return;}
    if(this.mode!=='play')return;this.keys.add(e.code);
    if(e.code==='KeyF')this.action('car');if(e.code==='KeyE')this.action('use');if(e.code==='KeyQ')this.action('dodge');if(e.code==='KeyG')this.action('push');if(e.code==='KeyX')this.crouched=!this.crouched;if(e.code==='KeyI')$('interactionDrawer').hidden=!$('interactionDrawer').hidden;
    if(e.code==='KeyC'){this.renderer.camera.mode=(this.renderer.camera.mode+1)%3;this.toast(['CÁMARA · Seguimiento','CÁMARA · Cercana','CÁMARA · Panorámica'][this.renderer.camera.mode]);}
    if(e.code==='KeyT')this.toggleRadio();
   });
   window.addEventListener('keyup',e=>this.keys.delete(e.code));window.addEventListener('blur',()=>{this.resetInput();if(this.mode==='play')this.pause();});
   document.addEventListener('visibilitychange',()=>{if(document.hidden){this.resetInput();if(this.mode==='play')this.pause();}});
   window.addEventListener('resize',()=>{this.renderer.resize();this.renderDirty=true;if(this.mode==='map')this.drawMap(true);});
   const canvas=$('world');canvas.addEventListener('contextmenu',e=>e.preventDefault());
   canvas.addEventListener('pointerdown',e=>{if(this.mode!=='play'&&this.mode!=='photo')return;this.drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);this.lookUntil=performance.now()+2200;});
   canvas.addEventListener('pointermove',e=>{if(!this.drag||e.pointerId!==this.drag.id)return;const dx=e.clientX-this.drag.x,dy=e.clientY-this.drag.y;this.drag.x=e.clientX;this.drag.y=e.clientY;this.renderer.camera.yaw-=dx*.006;this.renderer.camera.pitch=D.clamp(this.renderer.camera.pitch+dy*.004,-.04,1.05);this.lookUntil=performance.now()+2400;});
   const stopDrag=e=>{if(this.drag?.id===e.pointerId)this.drag=null;};canvas.addEventListener('pointerup',stopDrag);canvas.addEventListener('pointercancel',stopDrag);canvas.addEventListener('lostpointercapture',stopDrag);
   canvas.addEventListener('wheel',e=>{if(this.mode==='photo'){e.preventDefault();const c=this.renderer.camera;c.photoDistance=D.clamp((c.photoDistance||10)+e.deltaY*.013,1.1,35);}},{passive:false});
   const joy=$('joystick');let joyID=null;
   const moveJoy=e=>{if(e.pointerId!==joyID)return;e.preventDefault();let rect=joy.getBoundingClientRect(),dx=e.clientX-rect.left-rect.width/2,dy=e.clientY-rect.top-rect.height/2,len=Math.hypot(dx,dy),r=rect.width*.32;if(len>r){dx*=r/len;dy*=r/len;}this.stick={x:dx/r,y:-dy/r};$('joystickKnob').style.transform=`translate(${dx}px,${dy}px)`;};
   joy.addEventListener('pointerdown',e=>{if(this.mode!=='play')return;joyID=e.pointerId;joy.setPointerCapture(e.pointerId);moveJoy(e);});joy.addEventListener('pointermove',moveJoy);
   const resetJoy=e=>{if(e.pointerId===joyID){joyID=null;this.stick={x:0,y:0};$('joystickKnob').style.transform='';}};joy.addEventListener('pointerup',resetJoy);joy.addEventListener('pointercancel',resetJoy);joy.addEventListener('lostpointercapture',resetJoy);
   $('touchCar').onclick=()=>this.action('car');$('touchAction').onclick=()=>this.action('use');$('touchHorn').onclick=()=>this.action('dodge');$('touchPush').onclick=()=>this.action('push');$('interactionsButton').onclick=()=>$('interactionDrawer').hidden=!$('interactionDrawer').hidden;$('closeInteractions').onclick=()=>$('interactionDrawer').hidden=true;$('crouchButton').onclick=()=>{this.crouched=!this.crouched;$('crouchButton').setAttribute('aria-pressed',String(this.crouched));};
   for(const [id,prop]of [['repairButton','repairHeld'],['touchJump','jumpHeld']]){
    const el=$(id);el.addEventListener('pointerdown',e=>{if(this.mode!=='play')return;this[prop]=true;el.setPointerCapture(e.pointerId);e.preventDefault();});
    for(const name of ['pointerup','pointercancel','lostpointercapture','blur'])el.addEventListener(name,()=>this[prop]=false);
    el.addEventListener('keydown',e=>{if(['Space','Enter'].includes(e.code)){e.preventDefault();this[prop]=true;}});el.addEventListener('keyup',e=>{if(['Space','Enter'].includes(e.code)){e.preventDefault();this[prop]=false;}});
   }
   const brake=$('touchBrake');brake.addEventListener('pointerdown',e=>{this.touchBrake=true;brake.setPointerCapture(e.pointerId);brake.classList.add('pressed');e.preventDefault();});for(const name of ['pointerup','pointercancel','lostpointercapture'])brake.addEventListener(name,()=>{this.touchBrake=false;brake.classList.remove('pressed');});
   // Holding is deliberate on both keyboard and pointer. Losing focus cancels it.
   const surrender=$('surrenderButton');
   surrender.addEventListener('pointerdown',e=>{if(this.mode!=='play'||!this.sim.canSurrender())return;e.preventDefault();this.surrenderHeld=true;surrender.setPointerCapture(e.pointerId);surrender.classList.add('pressed');});
   for(const name of ['pointerup','pointercancel','lostpointercapture'])surrender.addEventListener(name,()=>{this.surrenderHeld=false;surrender.classList.remove('pressed');});
   surrender.addEventListener('keydown',e=>{if(['Space','Enter'].includes(e.code)&&this.mode==='play'){e.preventDefault();this.surrenderHeld=true;}});
   surrender.addEventListener('keyup',e=>{if(['Space','Enter'].includes(e.code)){e.preventDefault();this.surrenderHeld=false;}});
   surrender.addEventListener('blur',()=>{this.surrenderHeld=false;});
   $('citymap').addEventListener('click',e=>this.mapClick?.(e));
   canvas.addEventListener('webglcontextlost',e=>{e.preventDefault();this.graphics?.lose();});
   canvas.addEventListener('webglcontextrestored',()=>this.graphics?.restore());
  }
  resetInput(){this.repairHeld=false;this.jumpHeld=false;this.keys.clear();this.stick={x:0,y:0};this.drag=null;this.touchBrake=false;this.surrenderHeld=false;$('surrenderButton').classList.remove('pressed');this.sim.policeState.surrender=0;$('joystickKnob').style.transform='';$('touchBrake').classList.remove('pressed');}
  setMode(mode){
   this.renderDirty=true;this.mode=mode;this.resetInput();$('landing').hidden=mode!=='menu';$('hud').hidden=!this.started||mode==='menu'||mode==='photo';$('pause').hidden=mode!=='pause';$('mapOverlay').hidden=mode!=='map';$('dialogue').hidden=mode!=='dialog';$('photoUI').hidden=mode!=='photo';$('touchControls').hidden=mode!=='play';
   if(mode!=='play'){$('tutorial').hidden=true;$('interactionDrawer').hidden=true;$('repairButton').hidden=true;$('impactRibbon').hidden=true;}
   if(mode==='play'){$('world').focus({preventScroll:true});this.accumulator=0;}
   if(mode==='pause'){$('pauseTitle').textContent=this.started?'Pausa':'Ajustes';$('toggleStory').textContent=this.sim.free?'Retomar la historia':'Cambiar a exploración libre';$('pauseStats').textContent=`RECORRIDO ${(this.sim.stats.distance/1000).toFixed(1)} KM · ENCARGOS ${this.sim.stats.jobs}\nALIJOS ${this.sim.collected.length}/16 · FUGAS ${this.sim.stats.escapes}`;$('resume').focus();}
   if(mode==='map'){this.drawMap(true);$('closeMap').focus();}
  }
  readSave(){try{const text=localStorage.getItem(SAVE_KEY);if(!text)return null;const data=JSON.parse(text);return data&&data.version===1?data:null;}catch(e){return null;}}
  refreshContinue(){$('continue').hidden=!this.readSave();$('start').innerHTML=this.readSave()?'Nueva partida <span class="arrow">↗</span>':'Entrar a la ciudad <span class="arrow">↗</span>';}
  start(resume=false,free=false){
   const sim=new D.Simulation(this.world);if(resume){const data=this.readSave();if(!sim.restore(data)){this.toast('No se pudo recuperar la partida. El archivo no es válido.');return;}}
   else sim.free=free;
   this.sim=sim;this.crouched=false;this.started=true;this.renderer.camera.initialized=false;this.renderer.camera.yaw=sim.player.yaw;this.renderer.camera.pitch=.22;this.renderer.lightTime=-1;this.audio.start();this.setMode('play');this.autoSave=0;
   if(!resume){this.chapter(free?'LA CIUDAD ES TUYA':'LA LLAMADA');$('tutorialText').textContent=this.touch?'Mueve el joystick izquierdo. Arrastra la ciudad con el otro dedo para mirar. SUBIR inicia la entrada. Tócalo de nuevo para cancelar. Los coches ocupados tienen conductor. ACCIÓN interactúa con el entorno.':'Muévete con WASD. Arrastra el ratón para mirar. F inicia la entrada al coche. F o moverte cancela. Espera al cierre de la puerta antes de acelerar. E recoge cajas o responde al teléfono. G lanza o empuja. I muestra todas las interacciones.';$('tutorial').hidden=false;this.tutorialUntil=performance.now()+14000;}this.save(false);
  }
  pause(){if(this.mode==='dialog'||this.mode==='error')return;this.returnMode=this.mode==='menu'?'menu':'play';this.setMode('pause');}
  resume(){this.setMode(this.returnMode||'play');}
  openMap(){if(!this.started){this.toast('Entra a la ciudad para explorar el mapa.');return;}this.mapReturn=this.mode==='pause'?'pause':'play';this.setMode('map');}
  focusPhoto(){
   if(this.mode!=='photo')return;const c=this.renderer.camera;c.closeup=!c.closeup;const car=this.sim.player.car!==null;
   c.photoDistance=c.closeup?(car?5.5:1.4):(car?9:5);c.pitch=c.closeup?.055:.22;
   if(c.closeup)c.yaw=this.sim.actor().yaw+Math.PI-.26;
   $('photoFocus').setAttribute('aria-pressed',String(c.closeup));$('photoFocus').textContent=c.closeup?'Plano general':'Primer plano';this.renderDirty=true;
  }
  photo(){if(this.mode!=='play')return;this.renderer.camera.closeup=false;$('photoFocus').setAttribute('aria-pressed','false');$('photoFocus').textContent='Primer plano';this.renderer.camera.photoDistance=this.sim.player.car!==null?9:5;this.setMode('photo');}
  action(kind){if(this.mode!=='play')return;this.audio.start();this.sim.interact(kind);this.processEvents();}
  toggleSound(){this.settings.sound=!this.settings.sound;this.audio.start();this.audio.mute(!this.settings.sound);this.syncSettings();this.saveSettings();}
  toggleRadio(){this.audio.start();this.audio.music=!this.audio.music;$('radioButton').textContent=this.audio.music?'♫  RADIO 94.6 · NOCHE ABIERTA':'♫  RADIO 94.6 · APAGADA';}
  toast(text){if(!text)return;this.toastQueue.push(text);if(this.toastQueue.length>6)this.toastQueue.shift();}
  chapter(text){$('chapterText').textContent=text;$('chapter').classList.add('visible');this.chapterUntil=performance.now()+3500;$('screenStatus').textContent=text;}
  processEvents(){
   for(const e of this.sim.events.splice(0)){
    if(e.kind==='toast')this.toast(e.text);if(e.kind==='chapter')this.chapter(e.text);if(e.kind==='sound')this.audio.effect(e.text);if(e.kind==='save')this.save(false);
    if(e.kind==='dialog'){
     this.setMode('dialog');$('speaker').textContent=e.speaker;$('portrait').textContent=e.speaker.charAt(0);$('dialogTitle').textContent=e.title;$('dialogText').textContent=e.text;$('dialogOptions').replaceChildren();
     e.choices.forEach((text,index)=>{let b=document.createElement('button');b.textContent=text;b.onclick=()=>{this.sim.confirmStory(index);this.setMode('play');this.processEvents();};$('dialogOptions').append(b);});$('dialogOptions').firstElementChild?.focus();
    }
   }
  }
  save(feedback){
   if(!this.started){if(feedback)this.toast('Todavía no hay una partida iniciada.');return false;}
   try{localStorage.setItem(SAVE_KEY,JSON.stringify(this.sim.serialize()));if(feedback)this.toast('Partida guardada en este navegador.');return true;}catch(e){if(feedback||!this.storageWarning){this.toast('El navegador bloqueó el guardado local. Usa «Exportar partida» para conservar tu progreso.');this.storageWarning=true;}return false;}
  }
  download(blob,name,parent=document.body){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;parent.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);}
  exportSave(){if(!this.started){this.toast('Inicia una partida antes de exportarla.');return;}this.download(new Blob([JSON.stringify(this.sim.serialize(),null,2)],{type:'application/json'}),'distrito-cero-partida.json');this.toast('Copia de la partida exportada.');}
  async importSave(file){if(!file)return;try{if(file.size>2500000)throw new Error('El archivo es demasiado grande.');const data=JSON.parse(await file.text()),sim=new D.Simulation(this.world);if(!sim.restore(data))throw new Error('Formato de partida no válido.');this.sim=sim;this.crouched=false;this.started=true;this.renderer.camera.initialized=false;this.renderer.camera.yaw=sim.player.yaw;this.setMode('play');this.save(false);this.toast('Partida importada.');}catch(e){this.toast(`No se pudo importar: ${e.message}`);}finally{$('saveFile').value='';}}
  capture(){this.renderer.render(this.sim);try{$('world').toBlob(blob=>{if(blob){this.download(blob,'distrito-cero-captura.png');this.toast('Captura guardada.');}else this.toast('No se pudo crear la captura.');},'image/png');}catch(e){this.toast('El navegador no permitió guardar la imagen.');}}
  input(){
   const k=this.keys,throttle=(k.has('KeyW')||k.has('ArrowUp')?1:0)-(k.has('KeyS')||k.has('ArrowDown')?1:0),steer=(k.has('KeyD')||k.has('ArrowRight')?1:0)-(k.has('KeyA')||k.has('ArrowLeft')?1:0);
   return{throttle:D.clamp(throttle+this.stick.y,-1,1),steer:D.clamp(steer+this.stick.x,-1,1),brake:this.jumpHeld||k.has('Space')||(this.touchBrake&&this.sim.player.car!==null),sprint:k.has('ShiftLeft')||k.has('ShiftRight')||(this.touchBrake&&this.sim.player.car===null),lookYaw:this.renderer.camera.yaw,surrender:k.has('KeyR')||this.surrenderHeld,repair:k.has('KeyV')||this.repairHeld,crouch:this.crouched};
  }
  drawMap(full=false){
   const canvas=$(full?'citymap':'minimap'),ctx=canvas.getContext('2d');let w,h,dpr=full?Math.min(devicePixelRatio||1,2):2;
   if(full){let rect=canvas.getBoundingClientRect();w=rect.width;h=rect.height;if(!w||!h)return;if(canvas.width!==Math.round(w*dpr)||canvas.height!==Math.round(h*dpr)){canvas.width=Math.round(w*dpr);canvas.height=Math.round(h*dpr);}}
   else{w=160;h=160;}
   ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,w,h);ctx.fillStyle='#0b1718';ctx.fillRect(0,0,w,h);
   const p=this.sim.player,cx=full?0:p.x,cz=full?0:p.z,scale=full?(Math.min(w,h)-28)/880:w/215,point=(x,z)=>D.mapProject(x,z,cx,cz,w,h,scale);if(full)this.mapTransform={w,h,scale};
   ctx.save();ctx.beginPath();ctx.rect(0,0,w,h);ctx.clip();
   for(const b of this.world.blocks){let q=point(b.x+31,b.z+31);ctx.fillStyle=b.park?'#1e3429':'#17282b';ctx.fillRect(q[0],q[1],62*scale,62*scale);}
   for(const b of this.world.buildings){let q=point(b.x+b.w/2,b.z+b.d/2);ctx.fillStyle=b.h>55?'#314441':'#243835';ctx.fillRect(q[0],q[1],b.w*scale,b.d*scale);}
   ctx.strokeStyle='#75968515';ctx.lineWidth=.5;for(let n=-5;n<=5;n++){ctx.beginPath();let a=point(n*84,-420),b=point(n*84,420);ctx.moveTo(...a);ctx.lineTo(...b);let c=point(-420,n*84),d=point(420,n*84);ctx.moveTo(...c);ctx.lineTo(...d);ctx.stroke();}
   const t=this.sim.target();if(t&&this.sim.route.length){ctx.beginPath();ctx.strokeStyle=t.custom?'#70c9df':'#d5ee94';ctx.lineWidth=full?2:1.8;ctx.setLineDash([4,3]);let path=[p,...this.sim.route,t];path.forEach((q,i)=>{let xy=point(q.x,q.z);if(i===0)ctx.moveTo(...xy);else ctx.lineTo(...xy);});ctx.stroke();ctx.setLineDash([]);}
   for(const poi of this.world.pois){const[x,y]=point(poi.x,poi.z);if(x<-15||x>w+15||y<-15||y>h+15)continue;const color=poi.type==='garage'?'#75cad9':poi.type==='safe'?'#e2e6d7':'#b9ccab';ctx.fillStyle='#0c1b1b';ctx.strokeStyle=color;ctx.lineWidth=1;ctx.beginPath();ctx.arc(x,y,full?4:3,0,Math.PI*2);ctx.fill();ctx.stroke();if(full){ctx.fillStyle=color;ctx.font='8px Arial';ctx.textAlign='left';ctx.fillText(poi.name,x+8,y+3);}}
   const police=this.sim.policeState;
   if(this.sim.wanted&&!this.sim.seen&&police.lastSeen){
    const [sx,sy]=point(police.lastSeen.x,police.lastSeen.z);ctx.save();ctx.strokeStyle='#d5ee9480';ctx.fillStyle='#d5ee940d';ctx.setLineDash([4,4]);ctx.lineWidth=1;ctx.beginPath();ctx.arc(sx,sy,28*scale,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.setLineDash([]);ctx.beginPath();ctx.moveTo(sx-4,sy-4);ctx.lineTo(sx+4,sy+4);ctx.moveTo(sx+4,sy-4);ctx.lineTo(sx-4,sy+4);ctx.stroke();if(full){ctx.font='9px Arial';ctx.fillStyle='#d5ee94';ctx.fillText('ÚLTIMA POSICIÓN CONOCIDA',sx+9,sy-9);}ctx.restore();
   }
   if(this.sim.wanted)for(const c of this.sim.cars)if(c.police&&!c.stolen&&c!==this.sim.actor()){let[x,y]=point(c.x,c.z);ctx.fillStyle='#f18776';ctx.beginPath();ctx.arc(x,y,full?3:2.5,0,Math.PI*2);ctx.fill();}
   if(t){let[x,y]=point(t.x,t.z);ctx.save();ctx.translate(x,y);ctx.rotate(Math.PI/4);ctx.fillStyle=t.custom?'#70c9df':'#d5ee94';ctx.fillRect(-3,-3,6,6);ctx.strokeStyle=ctx.fillStyle;ctx.globalAlpha=.5;ctx.strokeRect(-6,-6,12,12);ctx.restore();}
   const[x,y]=point(p.x,p.z);ctx.save();ctx.translate(x,y);ctx.rotate(-p.yaw);ctx.fillStyle='#edf6df';ctx.shadowBlur=5;ctx.shadowColor='#cfe8ae';ctx.beginPath();ctx.moveTo(0,-6);ctx.lineTo(4.5,4.5);ctx.lineTo(0,2.5);ctx.lineTo(-4.5,4.5);ctx.closePath();ctx.fill();ctx.restore();ctx.restore();
   if(full){ctx.fillStyle='#7c9a8a';ctx.font='9px Courier New';ctx.textAlign='left';ctx.fillText('N ↑',12,20);ctx.textAlign='right';ctx.fillText('840 m × 840 m',w-14,h-12);}
  }
  updateUI(now){
   const s=this.sim,p=s.player,car=p.car!==null?s.actor():null,m=s.storyTarget(),target=s.target();let title,desc,meta;
   if(s.job){title=s.job.type==='race'?'CIRCUITO NOCTURNO':'ENTREGA PENDIENTE';desc=s.job.type==='race'?'Cruza todos los controles antes de que termine el tiempo.':'Entrega el paquete en el punto marcado.';meta=`${Math.ceil(s.job.time)} S · ${s.job.index}/${s.job.points.length} · $${s.job.reward}`;}
   else if(s.free){title='LA CIUDAD ES TUYA';desc='Explora, encuentra alijos o acepta un encargo en el mapa.';meta=`MODO LIBRE · ${s.collected.length}/16 ALIJOS`;}
   else if(m){title=m.name;desc=m.label;meta=`CAPÍTULO ${String(s.story+1).padStart(2,'0')} / 06`;if(s.uploading)meta=`TRANSMISIÓN · ${Math.floor(s.upload/12*100)}% · NO TE ALEJES`;}
   else{title='HISTORIA COMPLETADA';desc=s.ending==='publicado'?'La ciudad conoce la verdad. Tu noche todavía no termina.':'Cobraste por tu silencio. La ciudad sigue abierta.';meta=`${s.collected.length}/16 ALIJOS · ${s.stats.jobs} ENCARGOS`;}
   if(target)meta+=` · ${Math.round(D.distance(p,target))} M`;
   $('objectiveTitle').textContent=title;$('objectiveText').textContent=desc;$('objectiveMeta').textContent=meta;$('wallet').textContent='$'+Math.floor(s.cash).toLocaleString('es-MX');$('healthFill').style.width=D.clamp(p.health,0,100)+'%';
   const stars=$('wanted').children;for(let i=0;i<5;i++)stars[i].className=i<s.wanted?(s.seen?'active':'active search'):'';$('wanted').setAttribute('aria-label',`Nivel de búsqueda ${s.wanted} de 5`);
   $('wantedLabel').textContent=s.wanted?s.seen?'TE TIENEN A LA VISTA':s.unseen>6?'PERDIENDO EL RASTRO':'ROMPE LA LÍNEA DE VISIÓN':'';
   $('speedometer').hidden=!car;$('onfootLabel').hidden=!!car;
   if(car){$('speed').textContent=String(Math.round(Math.abs(car.speed)*3.6)).padStart(3,'0');$('gear').textContent=car.speed<-.5?'R':Math.abs(car.speed)<.6?'N':String(Math.min(6,1+Math.floor(Math.abs(car.speed)/7)));$('carHealth').style.width=car.health+'%';}
   $('districtLabel').textContent=this.world.district(p.x,p.z);const minutes=41+Math.floor(s.time/12),hour=23+Math.floor(minutes/60);$('coordsLabel').textContent=`${String(hour%24).padStart(2,'0')}:${String(minutes%60).padStart(2,'0')} · ${this.settings.rain?'LLUVIA LIGERA':'CIELO CUBIERTO'}`;
   const ctx=s.getContext();$('context').hidden=!ctx||this.mode!=='play';if(ctx){$('contextKey').hidden=!ctx.key;$('contextKey').textContent=ctx.key;$('contextText').textContent=ctx.text;}
   $('touchCar').textContent=s.access?'CANCELAR':car?'BAJAR':'SUBIR';$('touchCar').setAttribute('aria-label',s.access?'Cancelar entrada o salida del vehículo':car?'Salir del vehículo':'Entrar al vehículo');$('touchBrake').textContent=car?'FRENO':'CORRER';$('touchAction').textContent=s.uploading?'ENVIANDO':p.carry?'SOLTAR':'ACCIÓN';$('touchHorn').textContent=car?'BOCINA':'ESQUIVAR';$('touchPush').textContent=p.carry?'LANZAR':'EMPUJAR';$('touchJump').hidden=!!car;
   const damage=car?.damage;
   $('reactiveReadout').textContent=damage?`FRENTE ${Math.round(damage.front*100)}% · COSTADOS ${Math.round(Math.max(damage.left,damage.right)*100)}%` :p.carry?'OBJETO EN MANOS · E SOLTAR / G LANZAR':p.crouch>.6?'AGACHADO · X PARA LEVANTARTE':'I · INTERACCIONES';
   const nearest=s.nearestCar(),repairCar=Number.isInteger(nearest)&&nearest>=0?s.cars[nearest]:null;
   $('repairButton').hidden=!!car||!repairCar||repairCar.health>=99.9||this.mode!=='play'||D.distance(p,repairCar)>3.8;
   $('repairFill').style.width=(s.repairProgress*100)+'%';$('repairText').textContent=s.repairProgress?`REPARANDO ${Math.round(s.repairProgress*100)}% · NO TE MUEVAS`:'MANTÉN V · REPARAR $90';
   $('impactRibbon').hidden=s.time>=s.impactUntil||this.mode!=='play';$('impactRibbon').textContent=s.impactLabel;
   const encounter=s.getPoliceStatus();$('policePanel').hidden=!s.wanted||this.mode!=='play';$('policePanel').dataset.phase=encounter.phase;
   $('policePhase').textContent=encounter.label;$('policeHint').textContent=encounter.hint;
   const capture=Math.round(encounter.capture*100);$('bustWrap').hidden=capture<1;$('bustFill').style.width=capture+'%';$('capturePercent').textContent=capture+'%';$('captureProgress').setAttribute('aria-valuenow',String(capture));
   $('searchWrap').hidden=encounter.phase!=='search';$('searchFill').style.width=(encounter.searchProgress*100)+'%';$('searchTime').textContent=encounter.searchSeconds+' s';$('searchProgress').setAttribute('aria-valuenow',String(Math.round(encounter.searchProgress*100)));
   $('surrenderButton').hidden=!encounter.surrenderAvailable;$('surrenderFill').style.width=(encounter.surrenderProgress*100)+'%';$('surrenderText').textContent=encounter.surrenderProgress>0?'MANTÉN · '+Math.round(encounter.surrenderProgress*100)+'%':'MANTÉN PARA RENDIRTE · $150';

   this.drawMap();if(this.mode==='map')this.drawMap(true);
   if(this.toastUntil<now&&this.toastQueue.length){$('toast').textContent=this.toastQueue.shift();$('toast').classList.add('visible');this.toastUntil=now+5500;}else if(this.toastUntil<now)$('toast').classList.remove('visible');
   if(this.chapterUntil<now)$('chapter').classList.remove('visible');if(this.tutorialUntil<now)$('tutorial').hidden=true;
   if(target&&this.mode==='play'){
    let q=this.renderer.project(target.x,4.6,target.z),x=(q[0]*.5+.5)*innerWidth,y=(-q[1]*.5+.5)*innerHeight;const visible=q[3]>0&&Math.abs(q[0])<.92&&q[1]>-.6&&q[1]<.78&&D.distance(p,target)<300;
    $('marker').hidden=!visible;if(visible){$('marker').style.left=x+'px';$('marker').style.top=y+'px';$('markerDistance').textContent=Math.round(D.distance(p,target))+' m';}
   }else $('marker').hidden=true;
  }
  scheduleFrame(){if(this.frameRequest!=null||this.graphics&&this.graphics.state!=='ready')return;this.frameRequest=requestAnimationFrame(now=>{this.frameRequest=null;this.loop(now);});}
  stopFrame(){if(this.frameRequest!=null)cancelAnimationFrame(this.frameRequest);this.frameRequest=null;}
  loop(now){
   if(this.mode==='error')return;
   const raw=(now-this.last)/1000,dt=Math.min(.12,Math.max(0,raw));this.last=now;this.frameCount++;this.fps=D.damp(this.fps,1/Math.max(.001,raw),1,dt);
   if(this.mode==='play'){
    this.accumulator+=dt;let steps=0;while(this.accumulator>=1/60&&steps<8){this.sim.step(1/60,this.input());this.accumulator-=1/60;steps++;}
    this.processEvents();this.autoSave+=dt;if(this.autoSave>25){this.autoSave=0;this.save(false);}
   }else if(this.mode==='menu'){
    this.sim.time+=dt;for(const car of this.sim.cars)if(car!==this.sim.cars[0])this.sim.traffic(car,dt);this.sim.pedestrians(dt);
   }
   if(['play','menu','photo'].includes(this.mode))this.renderer.updateCamera(this.sim,dt,{menu:this.mode==='menu',photo:this.mode==='photo',look:!!this.drag||now<this.lookUntil});
   try{if(['play','menu','photo'].includes(this.mode)||this.renderDirty){this.renderer.render(this.sim);this.renderDirty=false;}}catch(e){console.error(e);this.mode='error';$('error').hidden=false;$('errorText').textContent=e.message;return;}
   this.audio.update(this.sim,this.mode!=='play',this.renderer.rain);
   if(now-this.lastUI>90){this.updateUI(now);this.lastUI=now;$('fps').textContent=`${this.fps.toFixed(0)} FPS · ${this.renderer.canvas.width}×${this.renderer.canvas.height}`;}
   this.scheduleFrame();
  }
 }
 D.App=App;
 function boot(){try{globalThis.DC_APP=new D.App();}catch(e){console.error(e);$('loading').hidden=true;$('error').hidden=false;$('errorText').textContent=e.message||'No se pudo iniciar el motor gráfico.';}}
 requestAnimationFrame(()=>setTimeout(boot,40));
})(DC);
