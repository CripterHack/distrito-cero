/* Development-only keyframes. Never bundled. No retries, recovery or RAF replacement. */
(function(global){
 'use strict';
 function snapshot(app){const r=app.renderer;return{mode:app.mode,graphics:app.graphics?.state,disposed:!!r.disposed,ledgerDisposed:!!r.resources?.disposed,contextLost:r.gl.isContextLost(),frame:r.frame,resources:r.resources?.stats()};}
 function fail(app,message){throw new Error('DC_QA_GRAPHICS: '+message+' '+JSON.stringify(snapshot(app)));}
 function assertReady(app){const r=app.renderer;
  if(r.disposed||r.resources?.disposed||r.gl.isContextLost()||app.graphics&&app.graphics.state!=='ready')fail(app,'lost or inactive graphics generation');
  return r;
 }
 function start(app){app.stopFrame();assertReady(app);}
 function draw(app,simulation=app.sim){
  const r=assertReady(app),frame=r.frame;r.render(simulation);r.gl.finish();assertReady(app);
  const error=r.gl.getError();if(error!==r.gl.NO_ERROR)fail(app,'WebGL error '+error);
  if(r.frame!==frame+1)fail(app,'frame did not advance exactly once');
  return {frame:r.frame};
 }
 global.DC_MANUAL_FRAMES=Object.freeze({start,draw,assertReady,snapshot});
})(globalThis);
