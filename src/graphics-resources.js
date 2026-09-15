/* GPU allocations belong to one renderer generation. No simulation or save ownership. */
'use strict';
(function(D){
 const active=new WeakMap(),kinds=['Buffer','Texture','Framebuffer','Renderbuffer','VertexArray','Program','Shader'];
 class GLResources{
  constructor(gl){
   active.get(gl)?.dispose();this.gl=gl;this.disposed=false;this.handles=new Map();this.original=new Map();
   for(const kind of kinds){
    const make='create'+kind,remove='delete'+kind,create=gl[make],drop=gl[remove],set=new Set();
    this.handles.set(kind,set);this.original.set(kind,{create,drop});
    gl[make]=(...args)=>{const value=create.apply(gl,args);if(value&&!this.disposed)set.add(value);return value;};
    gl[remove]=(value)=>{set.delete(value);return drop.call(gl,value);};
   }
   active.set(gl,this);
  }
  static current(gl){return active.get(gl);}
  stats(){const counts={};let total=0;for(const[k,v]of this.handles){counts[k]=v.size;total+=v.size;}return{total,counts,disposed:this.disposed};}
  dispose(){
   if(this.disposed)return;this.disposed=true;const gl=this.gl;
   for(const[k,set]of this.handles){const{create,drop}=this.original.get(k);if(!gl.isContextLost())for(const v of set)drop.call(gl,v);set.clear();
    if(active.get(gl)===this){gl['create'+k]=create;gl['delete'+k]=drop;}
   }
   if(active.get(gl)===this)active.delete(gl);
  }
 }
 // State machine is independent of DOM/WebGL, so failures and stale callbacks are testable.
 class RecoveryController{
  constructor(hooks){this.hooks=hooks;this.state='ready';this.epoch=0;this.attempts=0;this.promise=null;this.error=null;}
  lose(){
   if(this.state==='lost')return;
   const first=this.state==='ready';if(first)this.attempts=0;
   this.state='lost';this.epoch++;this.promise=null;this.hooks.lost(first);
  }
  async restore(){
   if(this.state==='restoring')return this.promise;
   if(!['lost','failed'].includes(this.state)||this.attempts>=3)return false;
   this.state='restoring';this.attempts++;const epoch=this.epoch;
   this.promise=(async()=>{let value;try{
    value=await this.hooks.build();if(epoch!==this.epoch){this.hooks.dispose(value);return false;}
    this.hooks.ready(value);this.state='recovered';this.error=null;return true;
   }catch(e){if(value)this.hooks.dispose(value);if(epoch===this.epoch){this.error=e;this.state='failed';this.hooks.failed(e);}return false;}
   finally{if(epoch===this.epoch)this.promise=null;}})();return this.promise;
  }
  resume(){if(this.state!=='recovered')return false;this.state='ready';return true;}
 }
 D.GLResources=GLResources;D.RecoveryController=RecoveryController;
})(DC);
