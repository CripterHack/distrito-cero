'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {D,R,scene}=require('./helpers/sidearm_sight.cjs');
const path='tools/qa/longarm_contact.js';
if(fs.existsSync(path))vm.runInThisContext(fs.readFileSync(path,'utf8'));
const api=globalThis.DC_LONGARM_QA||{};
const dist=(a,b)=>Math.hypot(...a.map((v,i)=>v-b[i]));
function rendered(s){const mount=D.Equipment.mount(s),actor=D.WeaponHandling.actor(s.player,mount,s.equipment);return{mount,actor,pose:R.pose(actor,s.time)};}

test('long-arm auditor exposes independent measurements and a separate screening decision',()=>{
 assert.equal(typeof api.inspect,'function');assert.equal(typeof api.screen,'function');
});
test('each family verifies its visible sight and stock references against actual vertices',()=>{
 for(const id of ['smg','rifle','shotgun','sniper']){
  const v=api.landmarks(id);assert.equal(v.item,id);assert.equal(v.kind,id==='sniper'?'scope':'open-sight');
  assert.ok(v.stock[2]<-.23);assert.ok(v.front[2]>.29);
  assert.ok(dist(v.front,v.rear)>.25);
 }
 assert.throws(()=>api.landmarks('pistol'),/unsupported/i);
 assert.throws(()=>api.landmarks('gauss'),/unsupported/i);
});
test('missing sight or stock geometry cannot silently produce credible measurements',()=>{
 for(const id of ['rifle','sniper']){
  assert.throws(()=>api.landmarks(id,[]),/geometry|landmark/i);
  const parts=D.EquipmentGeometry.build(id).map(p=>({...p,data:p.data.slice()}));
  for(const p of parts)for(let i=0;i<p.data.length;i+=8)p.data[i+2]+=10;
  assert.throws(()=>api.landmarks(id,parts),/landmark/i);
 }
});
test('sniper never reuses open-sight references or missing tubular rings',()=>{
 assert.throws(()=>api.landmarks('sniper',D.EquipmentGeometry.build('rifle')),/landmark/i);
 const v=api.landmarks('sniper');assert.ok(Math.abs(v.rear[1]-.133)<1e-8);
});
test('inspection reads the supplied rendered palette instead of recomputing a matching pose',()=>{
 const s=scene('rifle'),r=rendered(s),a=api.inspect(s,r);
 r.pose.matrices=r.pose.matrices.slice();r.pose.matrices[R.ids.head*16+12]+=.025;
 const b=api.inspect(s,r);assert.ok(Math.abs(b.eye[0]-a.eye[0]-.025)<1e-6);
 assert.ok(dist(a.stock,b.stock)<1e-9);
});
test('invalid or incomplete rendered evidence fails closed without a simulation fallback',()=>{
 const s=scene('rifle');for(const bad of [{},{mount:D.Equipment.mount(s)},{...rendered(s),pose:{matrices:new Float32Array(16),rootY:0,scale:1}}])
  assert.throws(()=>api.inspect(s,bad),/render|palette|pose/i);
 const r=rendered(s);r.pose.matrices=r.pose.matrices.slice();r.pose.matrices[0]=NaN;
 assert.throws(()=>api.inspect(s,r),/palette|finite/i);
});
test('arm-length audit compares endpoints from different joint matrices',()=>{
 const s=scene('rifle'),r=rendered(s),a=api.inspect(s,r);
 assert.ok(Math.max(...Object.values(a.segmentErrors))<1e-6);
 r.pose.matrices=r.pose.matrices.slice();r.pose.matrices[R.ids.handL*16+12]+=.1;
 const b=api.inspect(s,r);assert.ok(Math.max(...Object.values(b.segmentErrors))>.01);
 assert.ok(api.screen(b).failures.includes('limb-length'));
});
test('screening rejects eye-only success, behind-facing sights and nonfinite evidence',()=>{
 const base=api.inspect(scene('rifle'));
 const valid={...base,eyeError:0,behind:.2,stockError:0,palmErrors:{L:0,R:0},segmentErrors:{upperL:0,lowerL:0,upperR:0,lowerR:0}};
 assert.equal(api.screen(valid).status,'screened');
 for(const [key,value,label] of [['stockError',.2,'stock'],['eyeError',.2,'eye'],['behind',-.2,'sight-behind'],['eyeError',NaN,'invalid']]){
  const v=api.screen({...valid,[key]:value});assert.equal(v.status,'needs-coordination');assert.ok(v.failures.includes(label));
 }
 assert.equal(api.screen(valid).artisticAcceptance,false);
 assert.ok(api.screen({...valid,palmErrors:{}}).failures.includes('invalid'));
});
test('eye-only counterfactual is explicitly not a corrected mount or saved gameplay state',()=>{
 const s=scene('rifle'),before=JSON.stringify(s.serialize()),v=api.inspect(s),c=api.translateToEye(v);
 assert.equal(c.counterfactual,true);assert.ok(c.eyeError<1e-8);
 assert.ok(Math.abs(c.stockError-dist(c.stock,v.shoulderTarget))<1e-10);
 assert.deepEqual(c.stock,v.stock.map((x,i)=>x+c.translation[i]));
 assert.equal(JSON.stringify(s.serialize()),before);assert.notEqual(c.stock,v.stock);
});
test('72-pose matrix is finite and read-only without requiring the current defect to persist',()=>{
 for(const id of ['smg','rifle','shotgun','sniper'])for(const neck of [-1,0,1])for(const crouch of [0,1])for(const pitch of [-.3,0,.3]){
  const s=scene(id);s.appearance.neckLength=neck;s.player.crouch=crouch;s.equipment.pitch=pitch;
  const before=JSON.stringify(s.serialize()),a=api.inspect(s),b=api.inspect(s);
  assert.ok(Number.isFinite(a.eyeError)&&Number.isFinite(a.stockError));assert.deepEqual(a,b);
  assert.equal(JSON.stringify(s.serialize()),before);assert.ok(Math.max(...Object.values(a.palmErrors))<.012);
 }
});
test('rig anchor and sight residuals are equivariant to world translation and yaw',()=>{
 const s=scene('shotgun'),a=api.inspect(s);
 for(const yaw of [-2.4,.8,2.9]){
  Object.assign(s.player,{x:6800,z:-7300,yaw});const b=api.inspect(s);
  for(const key of ['eyeError','stockError','behind'])assert.ok(Math.abs(a[key]-b[key])<1e-5,key);
 }
});
test('measured stock comes from visible buttplate rather than diagnostic mount brace values',()=>{
 const s=scene('rifle'),r=rendered(s),a=api.inspect(s,r);
 r.mount.brace={target:[900,900,900],stock:[800,800,800],error:0};const b=api.inspect(s,r);
 assert.deepEqual(a.stock,b.stock);assert.deepEqual(a.shoulderTarget,b.shoulderTarget);
 assert.equal(a.stockError,b.stockError);
});
test('nonfinite palm landmarks fail closed rather than producing an apparently valid report',()=>{
 const s=scene('rifle'),r=rendered(s);
 r.mount.palmContacts={...r.mount.palmContacts,L:{...r.mount.palmContacts.L,x:NaN}};
 assert.throws(()=>api.inspect(s,r),/nonfinite|landmark|measurement/i);
});
