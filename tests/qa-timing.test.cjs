'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),file=path.join(root,'tools/qa/sight_timing.js');
function timer(){
 assert.ok(fs.existsSync(file),'QA timing helper is not implemented');
 let now=0;const scope={performance:{now:()=>now}};vm.runInNewContext(fs.readFileSync(file,'utf8'),scope);
 return {q:scope.DC_SIGHT_TIMING,tick:n=>{now+=n}};
}
test('browser timing calls the operation exactly once and preserves its value',()=>{
 const {q,tick}=timer(),value={id:3};let calls=0;
 assert.equal(q.call('render',()=>{calls++;tick(17);return value}),value);assert.equal(calls,1);
 assert.deepEqual(JSON.parse(JSON.stringify(q.snapshot())),{render:{calls:1,failures:0,milliseconds:17,maximumMilliseconds:17}});
});
test('browser timing propagates the identical exception without retrying',()=>{
 const {q,tick}=timer(),error=new Error('lost context');let calls=0;
 assert.throws(()=>q.call('render',()=>{calls++;tick(9);throw error}),e=>e===error);
 assert.equal(calls,1);assert.equal(q.snapshot().render.failures,1);
});
test('browser timing snapshots and resets do not contaminate later sections',()=>{
 const {q,tick}=timer();q.call('stock',()=>tick(5));q.call('stock',()=>tick(3));
 const snapshot=q.snapshot();snapshot.stock.calls=99;
 assert.equal(q.snapshot().stock.calls,2);assert.equal(q.snapshot().stock.milliseconds,8);
 assert.equal(q.snapshot().stock.maximumMilliseconds,5);q.reset();assert.deepEqual(Object.keys(q.snapshot()),[]);
});
test('instrumentation is QA-only and cannot be bundled in the standalone game',()=>{
 timer();assert.ok(!fs.readFileSync(path.join(root,'index.html'),'utf8').includes('DC_SIGHT_TIMING'));
});
