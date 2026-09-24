/* Offline equipment interface. Input ownership ends at menus, blur and cancelled pointers. */
'use strict';
(function(D){
 const E=D.Equipment,$=id=>document.getElementById(id);
 class ArsenalAudio extends D.Audio{
  effect(name){
   const spec={equip:[260,.07,.035,'triangle',430],reload:[170,.11,.04,'triangle',90],reloadDone:[340,.08,.035,'triangle',470],dry:[120,.06,.04,'square',80],shot:[115,.13,.12,'sawtooth',35],gauss:[1100,.46,.1,'sawtooth',64],emp:[750,.70,.09,'sine',60],swing:[140,.11,.05,'triangle',55],throw:[210,.09,.03,'triangle',85],launch:[95,.32,.13,'sawtooth',28],explosion:[55,.65,.18,'triangle',19]};
   if(!spec[name]){super.effect(name);return;}if(!this.ctx||!this.enabled)return;
   const c=this.ctx,[hz,dur,volume,type,end]=spec[name],o=c.createOscillator(),g=c.createGain();o.type=type;o.frequency.setValueAtTime(hz,c.currentTime);o.frequency.exponentialRampToValueAtTime(end,c.currentTime+dur);g.gain.setValueAtTime(volume,c.currentTime);g.gain.exponentialRampToValueAtTime(.001,c.currentTime+dur);o.connect(g);g.connect(this.master);o.onended=()=>{o.disconnect();g.disconnect();};o.start();o.stop(c.currentTime+dur+.02);
  }
  update(sim,paused,rain){super.update(sim,paused,rain);if(!this.ctx)return;if(sim.actor().empUntil>sim.time)this.engineGain.gain.setTargetAtTime(0,this.ctx.currentTime,.08);if(sim.wanted&&!paused){const live=sim.cars.some(c=>c.police&&!c.stolen&&!(c.empUntil>sim.time)&&D.distance(c,sim.player)<100);if(!live)this.sirenGain.gain.setTargetAtTime(0,this.ctx.currentTime,.06);}}
 }
 D.Audio=ArsenalAudio;
 class EquipmentApp extends D.App{
  constructor(){super();this.weaponKeys=new Set();this.weaponPointers=new Map();this.aimToggle=false;this.fireQueued=false;this.weaponLook=null;this.weaponFilter='Todas';this.pendingWeapon='unarmed';this.arsenalReturn='play';this.opticStamp=0;this.opticHit=null;
   $('openArsenal').onclick=()=>this.openArsenal();$('pauseArsenal').onclick=()=>this.openArsenal();$('closeArsenal').onclick=()=>this.closeArsenal();$('commitEquipment').onclick=()=>this.selectEquipment(this.pendingWeapon,true);$('weaponReload').onclick=()=>this.sim.reloadWeapon();$('weaponAim').onclick=()=>{this.aimToggle=!this.aimToggle;};
   $('opticDown').onclick=()=>this.sim.cycleOptics(-1);$('opticUp').onclick=()=>this.sim.cycleOptics(1);$('opticMark').onclick=()=>this.sim.markOptics();$('weaponSupply').onclick=()=>{this.sim.resupplyWeapon();this.processEvents();this.paintWeaponDetail();};
   $('weaponSupplyRoute').onclick=()=>{const q=this.sim.nearestSupply();if(q){this.sim.pin={x:q.x,z:q.z};this.sim.routeClock=0;this.toast('GPS · '+q.name);this.closeArsenal();}};
   const groups=['Todas',...new Set(E.catalog.map(w=>w.group))];for(const group of groups){const button=document.createElement('button');button.type='button';button.textContent=group;button.dataset.group=group;button.onclick=()=>{this.weaponFilter=group;this.paintArsenal();};$('weaponFilters').append(button);}
   this.bindWeapons();this.updateEquipmentHUD(performance.now());
  }
  adopt(sim,slot,fresh=false){super.adopt(sim,slot,fresh);this.renderer.camera.weaponPitch=0;if(fresh)$('tutorialText').textContent+=' TAB abre el equipamiento. 9 selecciona Gauss, 0 EMP y B binoculares. L recarga. R sigue siendo rendición.';}
  resetInput(){super.resetInput();this.clearWeaponInput();}
  clearWeaponInput(){this.weaponKeys?.clear();this.weaponPointers?.clear();this.fireQueued=false;this.aimToggle=false;this.weaponLook=null;this.sim?.cancelEquipment?.();for(const id of ['touchFire','touchAim'])$(id)?.classList.remove('pressed');}
  setMode(mode){if(mode!=='arsenal'&&this.renderer)this.renderer.frozenHandling=null;document.body.classList.toggle('arsenal-open',mode==='arsenal');super.setMode(mode);if($('arsenal'))$('arsenal').hidden=mode!=='arsenal';if(mode==='arsenal'){$('hud').hidden=true;$('touchControls').hidden=true;}
   if(mode!=='play'){for(const id of ['equipmentHUD','weaponReticle','opticsOverlay'])if($(id))$(id).hidden=true;document.body.classList.remove('equipped','optic-view');this.renderer.fovOverride=null;}
  }
  openArsenal(){if(!this.started||!['play','pause'].includes(this.mode))return;this.arsenalReturn=this.mode;this.pendingWeapon=this.sim.equipment.selected;this.weaponFilter='Todas';const fov=this.renderer.fovOverride;this.renderer.freezeHandling(this.sim);this.setMode('arsenal');this.renderer.fovOverride=fov;this.paintArsenal();$('closeArsenal').focus();}
  closeArsenal(){const frozen=this.renderer.frozenHandling?.equipment,mode=this.arsenalReturn==='pause'?'pause':'play';this.setMode(mode);if(mode==='play'&&frozen?.selected===this.sim.equipment.selected)this.sim.equipment.aimWeight=D.clamp(frozen.aimWeight||0,0,1);}
  selectEquipment(id,close=false){if(!E.get(id))return;const changed=id!==this.sim.equipment.selected,actor=changed?this.renderer.handlingActor?.(this.sim):null;this.clearWeaponInput();this.sim.equipWeapon(id,actor);if(changed)this.renderer.camera.weaponPitch=0;this.renderDirty=true;this.pendingWeapon=id;if(close)this.closeArsenal();this.toast(E.get(id).name+(id==='gauss'?' · mantén y suelta para disparar':id==='binoculars'?' · Z para observar, rueda para zoom':''));this.updateEquipmentHUD(performance.now());}
  paintArsenal(){
   const host=$('weaponCards');host.replaceChildren();for(const b of $('weaponFilters').children)b.setAttribute('aria-pressed',String(b.dataset.group===this.weaponFilter));
   for(const w of E.catalog){if(this.weaponFilter!=='Todas'&&w.group!==this.weaponFilter)continue;const b=document.createElement('button');b.type='button';b.className='weapon-card';b.dataset.weapon=w.id;b.setAttribute('aria-pressed',String(this.pendingWeapon===w.id));
    const top=document.createElement('span');top.className='weapon-card-top';const cat=document.createElement('span');cat.textContent=w.group;const key=document.createElement('kbd');key.textContent=w.key||'TAB';top.append(cat,key);
    const art=document.createElement('span');art.className='weapon-card-art';art.innerHTML=D.EquipmentGeometry.icon(w.id);art.setAttribute('aria-hidden','true');const title=document.createElement('strong');title.textContent=w.name;const count=document.createElement('span');count.className='weapon-card-count';const a=this.sim.equipment.ammo[w.id];count.textContent=a?a.loaded+' / '+a.reserve+' · '+(w.kind==='gauss'||w.kind==='emp'?'celdas':'munición'):w.kind==='optics'?'2× · 4× · 8× · 12×':'Sin munición';b.append(top,art,title,count);b.onclick=()=>{this.pendingWeapon=w.id;for(const x of host.children)x.setAttribute('aria-pressed',String(x===b));this.paintWeaponDetail();};host.append(b);
   }this.paintWeaponDetail();
  }
  paintWeaponDetail(){const w=E.get(this.pendingWeapon),a=this.sim.equipment.ammo[w.id];$('weaponDetailArt').innerHTML=D.EquipmentGeometry.icon(w.id);$('weaponGroup').textContent=w.group;$('weaponDetailName').textContent=w.name;$('weaponDescription').textContent=w.desc;
   $('weaponNumbers').textContent=w.kind==='none'?'F · vehículo / E · entorno':w.kind==='optics'?'600 m de consulta · observación sin daño':w.kind==='emp'?'26 m de radio · 8 s de interrupción':w.range+' m · '+(w.automatic?'automático':w.kind==='gauss'?'carga de 1.5 s':w.kind==='grenade'?'arco y rebote':w.kind==='melee'?'contacto cercano':'cadencia individual');
   $('weaponAmmunition').textContent=a?a.loaded+' en equipo / '+a.reserve+' de reserva':'No requiere consumibles';$('commitEquipment').textContent=w.id==='unarmed'?'Guardar equipo y volver ↗':'Equipar '+w.name+' ↗';
   const q=this.sim.nearestSupply();$('supplyStatus').textContent=q?q.name+' · '+Math.round(q.distance)+' m':'Sin punto de suministro';$('weaponSupply').disabled=!q||q.distance>9||!!this.sim.wanted||this.sim.actualSpeed()>.6||!!this.sim.access;$('arsenalSave').textContent='EQUIPO POR PARTIDA · '+(this.sim.characterName||'Personaje')+' · $'+Math.floor(this.sim.cash);
  }
  bindWeapons(){
   const stop=e=>{e.preventDefault();e.stopImmediatePropagation();};const editable=()=>['INPUT','SELECT','TEXTAREA'].includes(document.activeElement?.tagName);const active=()=>this.mode==='play'&&this.sim.equipmentAvailable()&&this.sim.equipment.selected!=='unarmed';
   window.addEventListener('keydown',e=>{
    if(this.mode==='arsenal'){
     if(e.code==='Escape'){stop(e);this.closeArsenal();return;}
     if(e.code==='Tab'){const f=[...$('arsenal').querySelectorAll('button')].filter(x=>!x.disabled&&x.getClientRects().length);if(e.shiftKey&&document.activeElement===f[0]){stop(e);f.at(-1)?.focus();}else if(!e.shiftKey&&document.activeElement===f.at(-1)){stop(e);f[0]?.focus();}return;}
     if(!['Tab','Enter','Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight','Home','End','PageUp','PageDown'].includes(e.code))stop(e);else e.stopImmediatePropagation();return;
    }
    if(this.mode!=='play'||editable())return;
    if(e.code==='Tab'){stop(e);if(!e.repeat)this.openArsenal();return;}
    if(e.code==='KeyJ'){stop(e);if(active()&&!e.repeat){this.fireQueued=true;this.weaponKeys.add('fire');}return;}
    if(e.repeat)return;
    const digit=e.code.startsWith('Digit')?e.code.slice(5):null,w=E.catalog.find(w=>w.key===digit);
    if(w){stop(e);this.selectEquipment(w.id);return;}
    if(e.code==='Backquote'){stop(e);this.selectEquipment('unarmed');return;}
    if(e.code==='KeyB'){stop(e);this.selectEquipment(this.sim.equipment.selected==='binoculars'?'unarmed':'binoculars');return;}
    if(e.code==='BracketLeft'||e.code==='BracketRight'){stop(e);const i=E.catalog.findIndex(w=>w.id===this.sim.equipment.selected);this.selectEquipment(E.catalog[(i+(e.code==='BracketLeft'?-1:1)+E.catalog.length)%E.catalog.length].id);return;}
    if(active()&&e.code==='KeyZ'){stop(e);this.aimToggle=!this.aimToggle;return;}
    if(active()&&e.code==='KeyL'){stop(e);this.sim.reloadWeapon();return;}
    if(active()&&e.code==='KeyH'&&this.sim.equipment.selected==='binoculars'){stop(e);this.sim.markOptics();return;}
    if(active()&&['Equal','Minus','NumpadAdd','NumpadSubtract'].includes(e.code)&&this.sim.equipment.selected==='binoculars'){stop(e);this.sim.cycleOptics(['Equal','NumpadAdd'].includes(e.code)?1:-1);}
   },true);
   window.addEventListener('keyup',e=>{if(e.code==='KeyJ')this.weaponKeys.delete('fire');},true);
   const canvas=this.renderer.canvas;
   canvas.addEventListener('pointerdown',e=>{if(!active())return;stop(e);this.audio.start();canvas.setPointerCapture(e.pointerId);if(e.pointerType==='touch'||e.button===2){this.weaponLook={id:e.pointerId,x:e.clientX,y:e.clientY};if(e.pointerType!=='touch')this.weaponPointers.set(e.pointerId,'aim');}else if(e.button===0){this.weaponPointers.set(e.pointerId,'fire');this.fireQueued=true;}},true);
   canvas.addEventListener('pointermove',e=>{if(!active()||this.weaponLook?.id!==e.pointerId)return;stop(e);const c=this.renderer.camera,zoom=this.sim.equipment.selected==='binoculars'&&this.sim.equipment.aiming?Math.sqrt(E.zoom[this.sim.equipment.zoom]):1;
    c.yaw-=(e.clientX-this.weaponLook.x)*.004/zoom;c.weaponPitch=D.clamp((c.weaponPitch||0)-(e.clientY-this.weaponLook.y)*.003/zoom,-.7,.7);this.weaponLook.x=e.clientX;this.weaponLook.y=e.clientY;this.lookUntil=performance.now()+2400;
   },true);
   const release=(e,cancel=false)=>{const had=this.weaponPointers.has(e.pointerId)||this.weaponLook?.id===e.pointerId;if(!had)return;this.weaponPointers.delete(e.pointerId);if(this.weaponLook?.id===e.pointerId)this.weaponLook=null;if(cancel)this.clearWeaponInput();for(const id of ['touchFire','touchAim'])$(id).classList.remove('pressed');};
   window.addEventListener('pointerup',e=>release(e),true);window.addEventListener('pointercancel',e=>release(e,true),true);canvas.addEventListener('lostpointercapture',e=>release(e,true),true);
   canvas.addEventListener('wheel',e=>{if(!active()||this.sim.equipment.selected!=='binoculars')return;stop(e);this.sim.cycleOptics(e.deltaY<0?1:-1);},{capture:true,passive:false});
   for(const [id,kind]of[['touchFire','fire'],['touchAim','aim']]){const el=$(id);el.addEventListener('pointerdown',e=>{stop(e);if(!active())return;this.weaponPointers.set(e.pointerId,kind);if(kind==='fire')this.fireQueued=true;el.classList.add('pressed');try{el.setPointerCapture(e.pointerId);}catch(_){/* Synthetic tests need no capture. */}this.audio.start();});el.addEventListener('pointerup',e=>release(e));el.addEventListener('pointercancel',e=>release(e,true));el.addEventListener('lostpointercapture',e=>release(e,true));}
  }
  input(){const out=super.input();if(this.mode!=='play'||!this.weaponKeys)return out;out.firePressed=!!this.fireQueued;out.fire=this.fireQueued||this.weaponKeys.has('fire')||[...this.weaponPointers.values()].includes('fire');this.fireQueued=false;out.aim=this.aimToggle||[...this.weaponPointers.values()].includes('aim');
   const c=this.renderer.camera;if(this.renderer.equipmentView&&c.eye&&c.target)out.aimRay={origin:c.eye.slice(),direction:D.normalize(c.target.map((v,i)=>v-c.eye[i]))};return out;
  }
  updateUI(now){super.updateUI(now);this.updateEquipmentHUD(now);}
  updateEquipmentHUD(now){if(!$('equipmentHUD'))return;const s=this.sim,e=s.equipment,w=E.get(e.selected),play=this.mode==='play',ready=play&&s.equipmentAvailable(),armed=ready&&w.kind!=='none',optic=armed&&w.kind==='optics'&&e.aiming;
   $('equipmentHUD').hidden=!play;$('weaponReticle').hidden=!armed||optic;$('opticsOverlay').hidden=!optic;$('touchWeaponRow').hidden=!armed;document.body.classList.toggle('equipped',armed);document.body.classList.toggle('optic-view',optic);
   if(!play)return;
   $('weaponName').textContent=w.name;$('weaponMode').textContent=!ready?'GUARDADO · TERMINA LA INTERACCIÓN':w.kind==='none'?'TAB · EQUIPAMIENTO':e.handling?.handoff?.serial===(e.shotSerial||0)&&!e.reloading?'CAMBIANDO EQUIPO':e.reloading>0?'RECARGANDO':w.kind==='gauss'?'MANTÉN Y SUELTA':w.kind==='emp'?'PULSO ELECTRÓNICO':w.kind==='optics'?'Z / APUNTAR · OBSERVAR':w.automatic?'AUTOMÁTICO':'PULSACIÓN INDIVIDUAL';
   const a=e.ammo[w.id];$('weaponAmmo').textContent=a?String(a.loaded).padStart(2,'0')+' / '+a.reserve:w.kind==='optics'?E.zoom[e.zoom]+'×':'—';$('weaponReload').hidden=!a||!ready;$('weaponReload').disabled=!a||e.reloading>0||a.loaded>=w.mag||!a.reserve;$('weaponAim').hidden=!armed;$('weaponAim').setAttribute('aria-pressed',String(e.aiming));
   $('weaponGauge').hidden=!(e.charge>0||e.reloading>0);$('weaponGaugeFill').style.width=100*(e.charge>0?e.charge:1-e.reloading/(w.reload||1))+'%';$('weaponReticle').dataset.kind=w.kind;$('weaponReticle').classList.toggle('confirmed',e.lastHitAge!==undefined&&e.lastHitAge<.18);$('chargeText').textContent=e.charge>0?Math.round(e.charge*100)+'%':'';
   $('touchFire').textContent=w.kind==='gauss'?'CARGAR':w.kind==='emp'?'PULSO':w.kind==='optics'?'MARCAR':w.kind==='melee'?'GOLPE':'FUEGO';$('touchAim').textContent=w.kind==='optics'?'OBSERVAR':'APUNTAR';
   for(const id of ['opticDown','opticUp','opticMark'])$(id).hidden=!(ready&&w.kind==='optics');$('opticDown').disabled=e.zoom===0;$('opticUp').disabled=e.zoom===3;
   if(optic){if(!this.opticStamp||now-this.opticStamp>220){this.opticHit=s.aimTrace(600).hit;this.opticStamp=now;}const h=this.opticHit;$('opticMagnification').textContent=E.zoom[e.zoom]+'×';$('opticRange').textContent=h?Math.round(h.distance)+' m':'SIN RETORNO';$('opticTarget').textContent=h?({wall:'ESTRUCTURA',car:h.ref?.police?'VEHÍCULO POLICIAL':'VEHÍCULO',prop:'OBJETO',npc:'PERSONA',ground:'TERRENO'})[h.type]:'HORIZONTE > 600 m';$('opticHeading').textContent=String(Math.round(((this.renderer.camera.yaw*180/Math.PI)%360+360)%360)).padStart(3,'0')+'°';$('marker').hidden=true;}
  }
 }
 D.EquipmentApp=EquipmentApp;D.App=EquipmentApp;
})(DC);
