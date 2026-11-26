"use strict";
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const test = require("node:test");
const { decodeGlb, accessor } = require("../tools/export_human_tangents.cjs");
const {
  contactEnvelope,
  encodeProxy,
  prepare,
} = require("../tools/prepare_sedan_contact_proxy.cjs");

const close = (a, b, tol = 1e-11) =>
  assert.ok(Math.abs(a - b) < tol, `${a} vs ${b}`);

test("continuous support takes the minimum from an edge between samples", () => {
  // A square and a duplicate/interior point, rotated by an angle off the sampling grid.
  const angle = 0.15317;
  const points = [
    [-1, -1],
    [1, -1],
    [1, 1],
    [-1, 1],
    [0, 0],
    [1, 1],
  ].map(([y, z]) => [
    Math.cos(angle) * y - Math.sin(angle) * z,
    Math.sin(angle) * y + Math.cos(angle) * z,
  ]);
  const { min, max } = contactEnvelope(points);
  close(min, 1);
  close(max, Math.SQRT2);
  assert.throws(
    () =>
      contactEnvelope([
        [2, 1],
        [1, 2],
        [2, 2],
      ]),
    /axle/,
  );
});

test("preview cylinder has an outward closed manifold, correct axis and a rest contact at Y=0", () => {
  const spec = {
    id: "wheel_front_left",
    center: [-0.8, 0.35, 1.3],
    radius: 0.35,
    width: 0.22,
  };
  const { document: d, binary: b } = decodeGlb(encodeProxy([spec]));
  assert.deepEqual(d.nodes[0].translation, spec.center);
  assert.deepEqual(d.nodes[0].scale, [0.22, 0.35, 0.35]);
  const prim = d.meshes[0].primitives[0],
    pos = accessor(d, b, prim.attributes.POSITION),
    ix = accessor(d, b, prim.indices);
  const points = Array.from({ length: pos.a.count }, (_, i) =>
    [0, 1, 2].map((j) => pos.value(i, j)),
  );
  const minY = Math.min(
    ...points.map((p) => spec.center[1] + p[1] * spec.radius),
  );
  close(minY, 0);
  const faceEdges = new Map();
  for (let i = 0; i < ix.a.count; i += 3) {
    const ids = [0, 1, 2].map((k) => ix.value(i + k)),
      [a, c, e] = ids.map((k) => points[k]);
    const u = c.map((x, j) => x - a[j]),
      v = e.map((x, j) => x - a[j]);
    const n = [
      u[1] * v[2] - u[2] * v[1],
      u[2] * v[0] - u[0] * v[2],
      u[0] * v[1] - u[1] * v[0],
    ];
    assert.ok(n.reduce((sum, x, j) => sum + x * (a[j] + c[j] + e[j]), 0) > 0);
    for (let k = 0; k < 3; k++) {
      const from = ids[k],
        to = ids[(k + 1) % 3],
        key = [Math.min(from, to), Math.max(from, to)].join(",");
      const edge = faceEdges.get(key) || [];
      edge.push(Math.sign(to - from));
      faceEdges.set(key, edge);
    }
  }
  for (const edge of faceEdges.values()) {
    assert.equal(edge.length, 2);
    assert.equal(edge[0] + edge[1], 0);
  }
  assert.equal(ix.a.count / 3, 256);
  const tyre = points
    .filter((p) => Math.hypot(p[1], p[2]) > 0.9)
    .map((p) => p.slice(1));
  close(contactEnvelope(tyre).min, Math.cos(Math.PI / 64), 1e-7);
});

test("unregistered GLB bytes fail before any output is created", (t) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "dc-wheel-proxy-"));
  t.after(() => fs.rmSync(dir, { force: true, recursive: true }));
  const input = path.join(dir, "other.glb"),
    output = path.join(dir, "out");
  fs.writeFileSync(input, "different");
  assert.throws(() => prepare(input, output), /SHA/);
  assert.equal(fs.existsSync(output), false);
});
