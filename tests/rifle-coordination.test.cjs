'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {D, R, scene} = require('./helpers/sidearm_sight.cjs');
vm.runInThisContext(fs.readFileSync('tools/qa/longarm_contact.js', 'utf8'));
vm.runInThisContext(fs.readFileSync('tools/qa/stock_clearance.js', 'utf8'));
const Q = globalThis.DC_LONGARM_QA;

test('rifle neutral coordinates the mesh eye and stock without stretching arms', () => {
  const sim = scene('rifle');
  const before = JSON.stringify(sim.serialize());
  const m = Q.inspect(sim);
  assert.ok(m.eyeError < .010, `eye/sight: ${m.eyeError} m`);
  assert.ok(m.stockError < .030, `stock/shoulder: ${m.stockError} m`);
  assert.ok(m.behind > .05, `eye must be behind the sight: ${m.behind}`);
  assert.ok(Math.max(...Object.values(m.palmErrors)) < .012);
  assert.ok(Math.max(...Object.values(m.segmentErrors)) < .000001);
  const mount = D.Equipment.mount(sim);
  const actor = D.WeaponHandling.actor(sim.player, mount, sim.equipment);
  const surface = DC_STOCK_CLEARANCE.inspect(sim, {mount, actor, pose:R.pose(actor, sim.time)});
  for (const part of ['face', 'jacket']) {
    assert.ok(surface.minimum[part].distance >= -.002, `${part} penetrates the stock: ${surface.minimum[part].distance} m`);
  }
  assert.equal(JSON.stringify(sim.serialize()), before);
});
