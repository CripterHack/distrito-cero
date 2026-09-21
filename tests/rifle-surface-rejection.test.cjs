'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
const path='tools/qa/stock_clearance.js';
if(fs.existsSync(path))vm.runInThisContext(fs.readFileSync(path,'utf8'));
const api=()=>{assert.ok(globalThis.DC_STOCK_CLEARANCE,'stock surface rejection helper is missing');return globalThis.DC_STOCK_CLEARANCE;};
function evidence(s){const mount=D.Equipment.mount(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment);return{mount,actor,pose:R.pose(actor,s.time)};}
function shifted(r,offset){return {...r,mount:{...r.mount,point:(...p)=>r.mount.point(...p).map((v,i)=>v+offset[i])}};}
test('stock boxes must match complete rendered triangles, not diagnostic brace metadata',()=>{
 const q=api();assert.equal(q.verifyGeometry().length,2);
 const parts=D.EquipmentGeometry.build('rifle').map(p=>({...p,data:p.data.slice()}));
 const part=parts.find(p=>Array.from(p.data).some((v,i)=>i%8===2&&Math.abs(v+.2385)<1e-6));
 assert.ok(part);for(let i=0;i<part.data.length;i+=8)if(Math.abs(part.data[i+2]+.2385)<1e-6)part.data[i+2]+=.003;
 assert.throws(()=>q.verifyGeometry(parts),/stock|geometry|triangle/i);
});
test('surface inspection is finite, deterministic and does not alter the simulation or palette',()=>{
 const s=scene('rifle'),r=evidence(s),before=JSON.stringify(s.serialize()),palette=Array.from(r.pose.matrices),a=api().inspect(s,r),b=api().inspect(s,r);
 assert.deepEqual(a,b);assert.equal(JSON.stringify(s.serialize()),before);assert.deepEqual(Array.from(r.pose.matrices),palette);
 for(const part of ['face','jacket']){assert.ok(a.samples[part]>100);assert.ok(Number.isFinite(a.minimum[part].distance));}
 assert.equal(a.artisticAcceptance,false);
});
test('known interior placement rejects real face/neck vertices even with a zero brace error',()=>{
 const s=scene('rifle'),r=evidence(s),q=api(),first=q.inspect(s,r),point=first.minimum.face.world;
 const center=r.mount.point(0,-.012,-.14),bad=shifted(r,point.map((v,i)=>v-center[i]));
 bad.mount.brace={error:0};const result=q.inspect(s,bad);
 assert.ok(result.minimum.face.distance<-.020);assert.ok(q.screen(result).failures.includes('face-penetration'));
});
test('known interior placement rejects real jacket vertices independently of the eye distance',()=>{
 const s=scene('rifle'),r=evidence(s),q=api(),point=q.inspect(s,r).minimum.jacket.world;
 const center=r.mount.point(0,-.012,-.14),bad=shifted(r,point.map((v,i)=>v-center[i]));
 const result=q.inspect(s,bad);assert.ok(result.minimum.jacket.distance<-.020);assert.ok(q.screen(result).failures.includes('jacket-penetration'));
});
test('a distant object passes only the clearance screen, never contact or artistic acceptance',()=>{
 const s=scene('rifle'),q=api(),result=q.inspect(s,shifted(evidence(s),[5,0,0])),screen=q.screen(result);
 assert.equal(screen.status,'clearance-screened');assert.equal(screen.artisticAcceptance,false);assert.equal(screen.contactAcceptance,false);
});
test('the cohort is fixed in bind space and retains its counts when the supplied palette is translated',()=>{
 const s=scene('rifle'),r=evidence(s),q=api(),a=q.inspect(s,r);
 r.pose.matrices=r.pose.matrices.slice();for(let i=12;i<r.pose.matrices.length;i+=16)r.pose.matrices[i]+=.03;
 const b=q.inspect(s,r);assert.deepEqual(a.samples,b.samples);assert.notDeepEqual(a.minimum.face,b.minimum.face);
});
test('world translations and yaw preserve the clearance measurements',()=>{
 const s=scene('rifle'),q=api(),a=q.inspect(s,evidence(s));
 Object.assign(s.player,{x:6400,z:-7100,yaw:1.4});const b=q.inspect(s,evidence(s));
 for(const part of ['face','jacket'])assert.ok(Math.abs(a.minimum[part].distance-b.minimum[part].distance)<2e-5,part);
});
test('missing and nonfinite evidence fails closed rather than recomputing a pose',()=>{
 const s=scene('rifle'),q=api();assert.throws(()=>q.inspect(s),/palette|evidence/i);
 const r=evidence(s);r.pose.matrices=r.pose.matrices.slice();r.pose.matrices[0]=NaN;
 assert.throws(()=>q.inspect(s,r),/palette|finite/i);
});
test('a nonrigid or nonfinite prop frame cannot produce a credible clearance',()=>{
 const s=scene('rifle'),q=api(),r=evidence(s);
 assert.throws(()=>q.inspect(s,{...r,mount:{...r.mount,direction:p=>p.map(v=>v*2)}}),/frame|rigid/i);
 assert.throws(()=>q.inspect(s,{...r,mount:{...r.mount,point:()=>[NaN,0,0]}}),/frame|finite/i);
});
test('screening rejects missing cohorts, nonfinite minima and an unverified prop',()=>{
 const s=scene('rifle'),q=api(),v=q.inspect(s,shifted(evidence(s),[5,0,0]));
 for(const bad of [{...v,geometryVerified:false},{...v,samples:{face:0,jacket:100}},
  {...v,minimum:{...v.minimum,face:{distance:NaN}}},{...v,minimum:{}}]){
  assert.ok(q.screen(bad).failures.includes('invalid'));assert.equal(q.screen(bad).status,'needs-review');
 }
});
