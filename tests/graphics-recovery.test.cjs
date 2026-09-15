'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const ctx={DC:{},console,Map,Set,WeakMap,Promise};vm.createContext(ctx);
const file='src/graphics-resources.js';
if(fs.existsSync(file))vm.runInContext(fs.readFileSync(file,'utf8'),ctx);
function fakeGL(){let n=0;const g={lost:false,isContextLost(){return this.lost;}};for(const kind of ['Buffer','Texture','Framebuffer','Renderbuffer','VertexArray','Program','Shader']){g['create'+kind]=function(){return {id:++n,kind};};g['delete'+kind]=function(v){this.deleted=(this.deleted||0)+1;};}return g;}
test('resource ledger owns and deletes allocations once including shared references',()=>{
 const g=fakeGL(),s=new ctx.DC.GLResources(g),b=g.createBuffer(),t=g.createTexture();assert.equal(s.stats().total,2);g.deleteBuffer(b);assert.equal(s.stats().total,1);s.dispose();assert.equal(g.deleted,2);s.dispose();assert.equal(g.deleted,2);assert.equal(s.stats().total,0);
});
test('context loss abandons invalid handles without calling delete; new generation stays independent',()=>{
 const g=fakeGL(),a=new ctx.DC.GLResources(g);g.createTexture();g.lost=true;a.dispose();assert.equal(g.deleted,undefined);g.lost=false;const b=new ctx.DC.GLResources(g);g.createBuffer();a.dispose();assert.equal(b.stats().total,1);b.dispose();assert.equal(g.deleted,1);
});
test('null allocations and delete null are not counted as live GPU resources',()=>{const g=fakeGL();g.createBuffer=()=>null;const s=new ctx.DC.GLResources(g);g.createBuffer();g.deleteBuffer(null);assert.equal(s.stats().total,0);s.dispose();});
test('late old scope cleanup cannot remove a new active generation',()=>{const g=fakeGL(),a=new ctx.DC.GLResources(g);g.createBuffer();const b=new ctx.DC.GLResources(g);g.createTexture();a.dispose();assert.equal(ctx.DC.GLResources.current(g),b);assert.equal(b.stats().total,1);b.dispose();});
test('recovery stops on loss, reconstructs once, and requires explicit resume',async()=>{
 const events=[];let builds=0;const r=new ctx.DC.RecoveryController({lost:()=>events.push('lost'),build:async()=>{builds++;return {id:1};},ready:v=>events.push('ready'+v.id),dispose:()=>{},failed:()=>{}});
 r.lose();r.lose();assert.equal(r.state,'lost');assert.deepEqual(events,['lost']);await Promise.all([r.restore(),r.restore()]);assert.equal(builds,1);assert.equal(r.state,'recovered');assert.equal(r.resume(),true);assert.equal(r.state,'ready');assert.equal(r.resume(),false);
});
test('loss while building invalidates the old candidate and permits a fresh restore',async()=>{
 let resolve,disposed=0,ready=0;const r=new ctx.DC.RecoveryController({lost(){},build:()=>new Promise(x=>resolve=x),dispose(){disposed++;},ready(){ready++;},failed(){}});
 r.lose();const old=r.restore();r.lose();resolve({});await old;assert.equal(ready,0);assert.equal(disposed,1);const newer=r.restore();resolve({});await newer;assert.equal(ready,1);assert.equal(r.state,'recovered');
});
test('rebuild failure remains blocked with a bounded explicit retry budget',async()=>{let calls=0;const r=new ctx.DC.RecoveryController({lost(){},build:async()=>{calls++;throw Error('GPU failed');},dispose(){},ready(){},failed(){}});r.lose();for(let i=0;i<5;i++)await r.restore();assert.equal(calls,3);assert.equal(r.state,'failed');assert.equal(r.resume(),false);});
test('failed publication disposes its candidate and can retry without a leaked renderer',async()=>{let disposed=0;const r=new ctx.DC.RecoveryController({lost(){},build:async()=>({}),dispose(){disposed++;},ready(){throw Error('publish');},failed(){}});r.lose();await r.restore();assert.equal(disposed,1);assert.equal(r.state,'failed');});
test('unrequested restoration while running does not construct another renderer',async()=>{let calls=0;const r=new ctx.DC.RecoveryController({lost(){},build:async()=>calls++,dispose(){},ready(){},failed(){}});await r.restore();assert.equal(calls,0);assert.equal(r.state,'ready');});
