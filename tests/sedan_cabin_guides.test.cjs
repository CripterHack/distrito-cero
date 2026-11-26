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
  assert.equal(data.skeleton.length, 49);
});

test('seated head and neck match the appearance-fitted cast renderer at 1.25 s', () => {
  const {skeleton} = sampleCabin();
  const joints = Object.fromEntries(skeleton.map(bone => [bone.name, bone.point]));
  const expected = {
    neck: [-.380000, 1.189205, -.178733],
    head: [-.380023, 1.300012, -.172419]
  };
  for (const [name, point] of Object.entries(expected)) {
    assert.ok(Math.hypot(...point.map((v, i) => joints[name][i] - v)) < 1e-6,
      `${name}: expected ${point}, got ${joints[name]}`);
  }
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
