/* Recover the graphics generation, never replace the live simulation or creator draft. */
'use strict';
(function(D){
 const $=id=>document.getElementById(id),Base=D.App;
 const viewKeys=['quality','rain','bloom','daylight','previewStudio','previewSize','fovOverride','frozenHandling'];
 class RecoverableApp extends Base{
  constructor(){
   super();this.recoveryExtension=this.renderer.gl.getExtension('WEBGL_lose_context');this.recoverySnapshot=null;this.recoveryCandidate=null;this.recoveryStats={losses:0,restores:0};
   this.installRecoveryPanel();
   this.graphics=new D.RecoveryController({lost:first=>this.graphicsLost(first),build:()=>this.rebuildGraphics(),ready:r=>this.graphicsReady(r),failed:e=>this.graphicsFailed(e),dispose:r=>r?.dispose()});
  }
  loop(now){
   if(this.graphics&&this.graphics.state!=='ready')return;
   if(this.renderer.gl.isContextLost()){this.graphics?.lose();return;}
   super.loop(now);
  }
  installRecoveryPanel(){
   const panel=document.createElement('section');panel.id='graphicsRecovery';panel.hidden=true;panel.className='graphics-recovery';panel.setAttribute('role','dialog');panel.setAttribute('aria-modal','true');panel.setAttribute('aria-labelledby','recoveryTitle');
   const card=document.createElement('div');card.className='recovery-card';
   const label=document.createElement('p');label.className='eyebrow';label.textContent='DISTRITO CERO · RECUPERACIÓN GRÁFICA';
   const title=document.createElement('h2');title.id='recoveryTitle';title.textContent='La sesión está a salvo en memoria.';
   const status=document.createElement('p');status.id='recoveryStatus';status.setAttribute('aria-live','polite');
   const note=document.createElement('p');note.textContent='No se ha reiniciado la partida. Puedes exportarla antes de recargar la página. El guardado local anterior no se reemplaza automáticamente.';
   const actions=document.createElement('div');actions.className='recovery-actions';
   const button=(id,text,fn)=>{const b=document.createElement('button');b.id=id;b.type='button';b.textContent=text;b.onclick=fn;actions.append(b);return b;};
   button('recoveryRetry','Reintentar gráficos',()=>this.retryGraphics());
   button('recoveryResume','Reanudar sesión',()=>this.resumeGraphics());
   button('recoveryExport','Exportar sesión JSON',()=>this.exportRecovery());
   button('recoveryDraft','Exportar borrador del personaje',()=>this.exportRecovery(true));
   card.append(label,title,status,note,actions);panel.append(card);document.body.append(panel);
   this.recoveryPanel=panel;
   // Capture before legacy controls. Only recovery controls receive inputs while blocked.
   const gate=e=>{
    if(!this.graphics||this.graphics.state==='ready')return;
    if(e.type==='keydown'&&e.code==='Tab'){
     const items=[...panel.querySelectorAll('button')].filter(b=>!b.disabled&&!b.hidden),i=items.indexOf(document.activeElement);
     e.preventDefault();e.stopImmediatePropagation();items[(i+(e.shiftKey?-1:1)+items.length)%items.length]?.focus();return;
    }
    if(panel.contains(e.target)){if(e.type.startsWith('key')&&!['Enter','Space'].includes(e.code)){e.preventDefault();e.stopImmediatePropagation();}return;}
    e.preventDefault();e.stopImmediatePropagation();
   };
   for(const name of ['keydown','keyup','pointerdown','pointermove','pointerup','click','wheel'])window.addEventListener(name,gate,{capture:true,passive:false});
  }
  graphicsLost(first){
   this.stopFrame();this.recoveryStats.losses++;
   const r=this.renderer;
   if(first){this.recoverySnapshot={mode:this.mode,world:r.world,camera:{...r.camera,eye:r.camera.eye?.slice(),target:r.camera.target?.slice()},view:Object.fromEntries(viewKeys.map(k=>[k,r[k]])),focus:document.activeElement};}
   this.mode='recovering';this.resetInput();if(this.creator)this.creator.pointer=null;
   this.audio.update(this.sim,true,r.rain);this.recoveryCandidate?.dispose();r.dispose();
   this.renderDirty=false;this.last=performance.now();this.accumulator=0;
   this.recoveryPanel.hidden=false;$('recoveryStatus').textContent='Se interrumpió el contexto WebGL. Esperando la recuperación del navegador.';
   $('recoveryResume').hidden=true;$('recoveryRetry').disabled=false;$('recoveryExport').hidden=!this.started;$('recoveryDraft').hidden=!this.creator;$('recoveryRetry').focus();
  }
  async rebuildGraphics(){
   const previous=this.renderer,gl=previous.gl,s=this.recoverySnapshot;
   if(gl.isContextLost())throw new Error('El navegador todavía no ha restablecido el contexto gráfico.');
   $('recoveryRetry').disabled=true;$('recoveryStatus').textContent='Reconstruyendo geometría, texturas y sectores…';
   let r;
   try{
    r=new D.Renderer(previous.canvas,s.world,s.view.quality);this.recoveryCandidate=r;
    Object.assign(r,s.view);r.camera={...s.camera,eye:s.camera.eye?.slice(),target:s.camera.target?.slice()};r.resize();
    await r.humanReady;
    if(r.disposed||gl.isContextLost())throw new Error('Se interrumpió la reconstrucción gráfica.');
    if(r.humanTextureStatus.failed||r.humanTextureStatus.loaded!==3)throw new Error('No se pudieron recuperar los mapas del personaje.');
    return r;
   }catch(e){if(r)r.dispose();else D.GLResources.current(gl)?.dispose();throw e;}
  }
  graphicsReady(r){
   // Draw first. A failed draw does not publish a half-initialized renderer.
   const sim=this.creator?.preview||this.sim;r.render(sim);r.gl.finish();
   if(r.gl.isContextLost()||r.gl.getError()!==r.gl.NO_ERROR)throw new Error('La verificación del dibujo recuperado falló.');
   this.renderer=r;this.recoveryCandidate=null;this.recoveryStats.restores++;this.recoveryStats.resources=r.resources.stats();
   $('recoveryStatus').textContent='Gráficos recuperados. La partida y el borrador permanecen en su estado anterior.';
   $('recoveryResume').hidden=false;$('recoveryRetry').disabled=true;$('recoveryResume').focus();
  }
  graphicsFailed(e){
   this.recoveryCandidate=null;$('recoveryStatus').textContent='No se pudo recuperar la imagen: '+e.message+' Exporta tu sesión antes de recargar.';
   $('recoveryRetry').disabled=this.graphics.attempts>=3;$('recoveryResume').hidden=true;
  }
  retryGraphics(){
   if(this.graphics.attempts>=3)return;
   if(this.renderer.gl.isContextLost()){
    const ext=this.recoveryExtension;
    // getExtension may return null during a real loss; restoration is browser-controlled.
    if(ext)ext.restoreContext();else $('recoveryStatus').textContent='El navegador controla la restauración. Puedes conservar la sesión con Exportar JSON.';
   }else this.graphics.restore();
  }
  resumeGraphics(){
   if(!this.graphics.resume())return;
   this.recoveryPanel.hidden=true;const s=this.recoverySnapshot;this.mode=s.mode;this.last=performance.now();this.accumulator=0;this.renderDirty=true;
   this.recoverySnapshot=null;if(s.focus?.isConnected)s.focus.focus({preventScroll:true});else this.renderer.canvas.focus({preventScroll:true});
   if(this.creator)this.fitCreator();this.scheduleFrame();
  }
  exportRecovery(draft=false){
   try{const c=this.creator;
    const data=draft?{format:'distrito-cero-appearance-draft',version:1,name:$('characterName').value,appearance:D.Appearance.copy(c.look)}:{format:'distrito-cero-slot',version:1,name:(this.sim.characterName||'Partida')+' · recuperada',data:this.sim.serialize()};
    this.download(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}),draft?'distrito-cero-borrador.json':'distrito-cero-recuperada.json',this.recoveryPanel);
    $('recoveryStatus').textContent=draft?'Borrador JSON preparado. Conserva los valores de personalización para recuperación manual.':'Copia de la sesión preparada. Puede importarse desde Mis partidas.';
   }catch(e){$('recoveryStatus').textContent='No se pudo exportar: '+e.message;}
  }
 }
 D.RecoverableApp=RecoverableApp;D.App=RecoverableApp;
})(DC);
