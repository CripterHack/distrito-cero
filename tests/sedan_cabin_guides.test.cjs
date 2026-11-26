'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const {sampleCabin} = require('../tools/sample_sedan_cabin.cjs');

test('in vehicle space the access path reaches the seated actor origin and approaches from the driver side', () => {
  const data = sampleCabin();
  const {entry, seatOrigin, openingHand, approach} = data;
  assert.ok(approach[0] < -1 && openingHand[0] < seatOrigin[0]);
  assert.deepEqual(entry.at(-1), seatOrigin);
  assert.ok(entry.every(p => p.every(Number.isFinite)));
  assert.ok(data.skeleton.find(b => b.name === 'head').point[1] > 1);
  assert.equal(data.skeleton.length, 49);
});

test('driver seat, steering grips and panel stay in the same vehicle-local frame after a world translation', () => {
  const base = sampleCabin(), moved = sampleCabin(84, 0);
  for (const key of ['seatOrigin','openingHand','approach','wheelCenter','cushionCenter','backrestCenter','hinge']) {
    assert.ok(base[key].every((v,i) => Math.abs(v-moved[key][i]) < 1e-9), key);
  }
  assert.ok(base.cushionCenter[1] > base.seatOrigin[1]);
  assert.ok(base.grips.L[0] < base.wheelCenter[0] && base.wheelCenter[0] < base.grips.R[0]);
  assert.ok(base.closedHandle[0] < base.hinge[0] && base.closedHandle[2] < base.hinge[2]);
});
