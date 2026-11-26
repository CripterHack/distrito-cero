'use strict';
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const ctx = vm.createContext({DC: {Renderer: class {}, Simulation: class {}}});
for (const file of ['core', 'dynamics', 'reactive-renderer']) {
  vm.runInContext(fs.readFileSync(path.join(__dirname, '../src', file + '.js'), 'utf8'), ctx);
}
const {DC} = ctx;
function draw(side, open, {yaw=0, pitch=0, roll=0, damage=0, timed=false}={}) {
  const color=[.17,.21,.2], time=1.25;
  const car={id:1,x:12,z:30,yaw,color,boarding:!timed,doorOpen:open,
    doorUntil:timed ? time+.425 : 0,doorSide:side,suspension:{pitch,roll,kick:0},
    damage:{left:damage,right:damage,front:0,rear:0}};
  const parts=[];
  DC.Renderer.prototype.renderCar.call({assetParts:[{name:'BODY_shell',key:'body-shell'}],currentTime:time,
    meshes:{roof:{},tire:{},rim:{}}, dynamic:{}, currentSim:{player:car},
    add(_list,mesh,x,y,z,w,h,d,_color,_material,_em,yaw,_seed,_detail,pitch,roll) {
      parts.push({mesh,x,y,z,w,h,d,yaw,pitch,roll});
    }},car);
  const panels=parts.filter(p=>p.mesh==='body' && p.w===.035 && p.d===1.7);
  const handles=parts.filter(p=>p.mesh==='box' && p.w===.03 && p.d===.21);
  assert.equal(panels.length,2);assert.equal(handles.length,2);
  return panels.map((panel,i)=>({panel, handle:handles[i], side:i===0 ? -1 : 1}));
}

function near(actual,expected,label) {
  assert.ok(Math.abs(actual-expected)<1e-10, label+' '+actual+' differs from '+expected);
}

function checkSocket({panel,handle,side}) {
  // Undo the production shader's yaw, roll then pitch to recover metres
  // in the rendered panel's frame, including when suspension is tilted.
  const x=handle.x-panel.x,y=handle.y-panel.y,z=handle.z-panel.z;
  const x1=x*Math.cos(panel.yaw)-z*Math.sin(panel.yaw);
  const z1=x*Math.sin(panel.yaw)+z*Math.cos(panel.yaw);
  const y2=-x1*Math.sin(panel.roll)+y*Math.cos(panel.roll);
  near(x1*Math.cos(panel.roll)+y*Math.sin(panel.roll),side*.023,'outside');
  near(y2*Math.cos(panel.pitch)+z1*Math.sin(panel.pitch),.15,'height');
  near(-y2*Math.sin(panel.pitch)+z1*Math.cos(panel.pitch),-.48,'rearward');
  assert.deepEqual([handle.pitch,handle.roll,handle.yaw],[panel.pitch,panel.roll,panel.yaw]);
}
test('undamaged closed handles retain the authored midpoint on both doors',()=>{
  for(const p of draw(-1,0)) {
    near(p.handle.x,12+p.side*.967,'closed X');
    near(p.handle.y,.96,'closed Y');
    near(p.handle.z,30-.55,'closed Z');
    checkSocket(p);
  }
});
test('handles follow the opening and closing panels through the complete sweep',()=>{
  for(const side of [-1,1])
    for(const open of [0,.125,.5,.875,1,.5,.125,0])
      draw(side,open,{yaw:.73}).forEach(checkSocket);
});
test('damaged panels keep the handle under suspension pitch, roll and timed opening',()=>{
  for(const side of [-1,1])
    for(const open of [0,.25,1])
      for(const timed of [false,true])
        draw(side,open,{damage:.65,pitch:.11,roll:-.08,yaw:-.92,timed}).forEach(checkSocket);
});
