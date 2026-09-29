/* QA-only synchronous wall timing. Never bundled, never an acceptance gate.
 * Render time includes CPU submission and gl.finish, not a physical GPU query. */
(function(global){
 'use strict';
 let operations=Object.create(null);
 function call(name,work){
  const row=operations[name]??=( {calls:0,failures:0,milliseconds:0,maximumMilliseconds:0} );
  const start=global.performance.now();row.calls++;
  try{return work();}
  catch(error){row.failures++;throw error;}
  finally{const elapsed=global.performance.now()-start;row.milliseconds+=elapsed;row.maximumMilliseconds=Math.max(row.maximumMilliseconds,elapsed);}
 }
 function snapshot(){return Object.fromEntries(Object.entries(operations).map(([name,row])=>[name,{...row}]));}
 function reset(){operations=Object.create(null);}
 global.DC_SIGHT_TIMING=Object.freeze({call,snapshot,reset});
})(globalThis);
