"use strict";
const test = require("node:test"),
  assert = require("node:assert/strict"),
  fs = require("node:fs"),
  path = require("node:path");
const M = require("../tools/prepare_higgsfield_sedan.cjs");
function fixture() {
  const positions = [
    [-1, -0.5, -2],
    [1, -0.5, -2],
    [1, 0.5, -2],
    [-1, 0.5, -2],
    [-1, -0.5, 2],
    [1, -0.5, 2],
    [1, 0.5, 2],
    [-1, 0.5, 2],
  ];
  const floats = (a) => {
    const b = Buffer.alloc(a.length * 4);
    a.forEach((v, i) => b.writeFloatLE(v, i * 4));
    return b;
  };
  const chunks = [
    floats(positions.flat()),
    floats(positions.flatMap(() => [0, 1, 0])),
    floats(positions.flatMap(() => [0, 0])),
    floats(positions.flatMap(() => [1, 0, 0, 1])),
    Buffer.from([0, 1, 2, 0, 2, 3, 4, 6, 5, 4, 7, 6]),
  ];
  let offset = 0;
  const views = chunks.map((b) => {
    const v = { buffer: 0, byteOffset: offset, byteLength: b.length };
    offset += b.length;
    return v;
  });
  const document = {
    asset: { version: "2.0", generator: "fixture" },
    buffers: [{ byteLength: offset }],
    bufferViews: views,
    accessors: [
      { bufferView: 0, componentType: 5126, count: 8, type: "VEC3" },
      { bufferView: 1, componentType: 5126, count: 8, type: "VEC3" },
      { bufferView: 2, componentType: 5126, count: 8, type: "VEC2" },
      { bufferView: 3, componentType: 5126, count: 8, type: "VEC4" },
      { bufferView: 4, componentType: 5121, count: 12, type: "SCALAR" },
    ],
    meshes: [
      {
        primitives: [
          {
            attributes: { POSITION: 0, NORMAL: 1, TEXCOORD_0: 2, TANGENT: 3 },
            indices: 4,
            material: 0,
          },
        ],
      },
    ],
    materials: [{ name: "paint", normalTexture: { index: 0 } }],
    textures: [{ source: 0 }],
    images: [{ name: "preserved", bufferView: 4, mimeType: "image/png" }],
    nodes: [
      {
        mesh: 0,
        name: "source",
        matrix: [2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 1, 3, 5, 1],
      },
    ],
    scenes: [{ name: "preserved", nodes: [0] }],
    scene: 0,
  };
  return { document, binary: Buffer.concat(chunks) };
}
test("normalization gives 4.4m length, grounded Y, centered XZ and positive uniform scale", () => {
  const { document, binary } = fixture();
  const o = M.normalizeSedan(document, binary, { targetLength: 4.4 });
  const b = o.report.normalizedBounds;
  assert.ok(Math.abs(b.size[2] - 4.4) < 1e-12);
  assert.equal(b.min[1], 0);
  for (const i of [0, 2]) assert.ok(Math.abs(b.min[i] + b.max[i]) < 1e-12);
  assert.deepEqual(o.document.nodes.at(-1).scale, [0.55, 0.55, 0.55]);
  assert.equal(o.report.forwardAxis, "+Z");
  assert.equal(o.report.upAxis, "+Y");
});
test("source BIN, geometry, tangents, textures, all original nodes and input objects remain exact", () => {
  const { document, binary } = fixture(),
    saved = structuredClone(document),
    bytes = Buffer.from(binary);
  const o = M.normalizeSedan(document, binary, { targetLength: 4.4 });
  assert.deepEqual(document, saved);
  assert.deepEqual(binary, bytes);
  assert.deepEqual(o.binary, bytes);
  for (const key of [
    "meshes",
    "materials",
    "textures",
    "images",
    "accessors",
    "bufferViews",
    "buffers",
  ])
    assert.deepEqual(o.document[key], saved[key]);
  assert.deepEqual(o.document.nodes.slice(0, saved.nodes.length), saved.nodes);
  assert.deepEqual(o.document.scenes[0], { name: "preserved", nodes: [1] });
  assert.equal(o.report.triangles, 4);
});
test("unknown axes, nonuniform/reflected scale, missing tangents, malformed topology and nonfinite positions fail closed", () => {
  for (const kind of [
    "axis",
    "scale",
    "reflected",
    "tangent",
    "index",
    "nonfinite",
    "animated",
    "external",
    "scene",
  ]) {
    const { document: d, binary: b } = fixture();
    const options = { targetLength: 4.4 };
    if (kind === "axis") options.sourceForward = "-Z";
    if (kind === "scale") d.nodes[0].matrix[0] = 3;
    if (kind === "reflected") d.nodes[0].matrix[0] = -2;
    if (kind === "tangent") delete d.meshes[0].primitives[0].attributes.TANGENT;
    if (kind === "index") b[b.length - 1] = 90;
    if (kind === "nonfinite") b.writeFloatLE(Infinity, 0);
    if (kind === "animated") d.animations = [{}];
    if (kind === "external") d.buffers[0].uri = "remote.bin";
    if (kind === "scene") d.scenes[0].nodes.push(0);
    assert.throws(() => M.normalizeSedan(d, b, options), undefined, kind);
  }
  for (const length of [0, -1, NaN, Infinity, 100]) {
    const f = fixture();
    assert.throws(() =>
      M.normalizeSedan(f.document, f.binary, { targetLength: length }),
    );
  }
});
test("repeated preparation is deterministic and refuses already prepared scene", () => {
  const f = fixture(),
    a = M.normalizeSedan(f.document, f.binary, { targetLength: 4.4 }),
    b = M.normalizeSedan(f.document, f.binary, { targetLength: 4.4 });
  assert.deepEqual(a, b);
  assert.throws(() =>
    M.normalizeSedan(a.document, a.binary, { targetLength: 4.4 }),
  );
});
function articulatedFixture() {
  const boxes = [
    [-0.8, 0.4, -2, 0.8, 1.4, 2],
    [-1, 0, 1, -0.8, 0.6, 1.6],
    [0.8, 0, 1, 1, 0.6, 1.6],
    [-1, 0, -1.6, -0.8, 0.6, -1],
    [0.8, 0, -1.6, 1, 0.6, -1],
  ];
  const points = [],
    indices = [],
    cube = [
      0, 2, 1, 0, 3, 2, 4, 5, 6, 4, 6, 7, 0, 1, 5, 0, 5, 4, 3, 7, 6, 3, 6, 2, 1,
      2, 6, 1, 6, 5, 0, 4, 7, 0, 7, 3,
    ];
  for (const [x, y, z, X, Y, Z] of boxes) {
    const base = points.length;
    points.push(
      [x, y, z],
      [X, y, z],
      [X, Y, z],
      [x, Y, z],
      [x, y, Z],
      [X, y, Z],
      [X, Y, Z],
      [x, Y, Z],
    );
    indices.push(...cube.map((i) => i + base));
  }
  const f = fixture(),
    floats = (a) => {
      const b = Buffer.alloc(a.length * 4);
      a.forEach((v, i) => b.writeFloatLE(v, i * 4));
      return b;
    };
  const ib = Buffer.alloc(indices.length * 2);
  indices.forEach((v, i) => ib.writeUInt16LE(v, i * 2));
  const chunks = [
    floats(points.flat()),
    floats(points.flatMap(() => [0, 1, 0])),
    floats(points.flatMap(() => [0, 0])),
    floats(points.flatMap(() => [1, 0, 0, 1])),
    ib,
  ];
  let offset = 0;
  f.document.bufferViews = chunks.map((b) => {
    const v = { buffer: 0, byteOffset: offset, byteLength: b.length };
    offset += b.length;
    return v;
  });
  f.document.buffers[0].byteLength = offset;
  f.document.accessors.forEach(
    (a, i) => (a.count = i === 4 ? indices.length : points.length),
  );
  f.document.accessors[4].componentType = 5123;
  f.binary = Buffer.concat(chunks);
  return f;
}
const I = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
function mul(a, b) {
  return Array.from({ length: 16 }, (_, i) => {
    const row = i % 4,
      col = Math.floor(i / 4);
    let sum = 0;
    for (let k = 0; k < 4; k++) sum += a[row + k * 4] * b[k + col * 4];
    return sum;
  });
}
function worldPoints(document, binary) {
  const A = require("../tools/export_human_tangents.cjs").accessor,
    out = {};
  function visit(id, parent) {
    const n = document.nodes[id];
    let local = n.matrix?.slice() || I.slice();
    if (!n.matrix) {
      if (n.rotation) {
        const [x, y, z, w] = n.rotation;
        local = [
          1 - 2 * (y * y + z * z),
          2 * (x * y + z * w),
          2 * (x * z - y * w),
          0,
          2 * (x * y - z * w),
          1 - 2 * (x * x + z * z),
          2 * (y * z + x * w),
          0,
          2 * (x * z + y * w),
          2 * (y * z - x * w),
          1 - 2 * (x * x + y * y),
          0,
          0,
          0,
          0,
          1,
        ];
      }
      for (let k = 0; k < 3; k++) {
        for (let row = 0; row < 3; row++)
          local[row + k * 4] *= n.scale?.[k] ?? 1;
        local[12 + k] = n.translation?.[k] ?? 0;
      }
    }
    const m = mul(parent, local);
    if (n.mesh !== undefined) {
      const mesh = document.meshes[n.mesh],
        p = mesh.primitives[0],
        pos = A(document, binary, p.attributes.POSITION),
        ix = A(document, binary, p.indices);
      out[mesh.name || "source"] = Array.from(
        { length: ix.a.count },
        (_, i) => {
          const index = ix.value(i),
            v = [0, 1, 2].map((k) => pos.value(index, k));
          return [0, 1, 2].map(
            (k) => m[k] * v[0] + m[k + 4] * v[1] + m[k + 8] * v[2] + m[k + 12],
          );
        },
      );
    }
    for (const child of n.children || []) visit(child, m);
  }
  for (const id of document.scenes[document.scene].nodes) visit(id, I);
  return out;
}
test("five connected components reuse attributes and cover every original triangle once", () => {
  const f = articulatedFixture(),
    out = M.normalizeSedan(f.document, f.binary, {
      targetLength: 4.4,
      articulate: true,
    });
  assert.deepEqual(out.binary.subarray(0, f.binary.length), f.binary);
  assert.equal(out.report.components.length, 5);
  assert.equal(
    out.report.components.reduce((n, p) => n + p.triangles, 0),
    60,
  );
  const A = require("../tools/export_human_tangents.cjs").accessor,
    seen = [];
  for (const m of out.document.meshes) {
    const p = m.primitives[0];
    assert.deepEqual(
      p.attributes,
      f.document.meshes[0].primitives[0].attributes,
    );
    assert.equal(p.material, 0);
    const ix = A(out.document, out.binary, p.indices);
    for (let i = 0; i < ix.a.count; i += 3)
      seen.push([ix.value(i), ix.value(i + 1), ix.value(i + 2)].join(","));
  }
  const old = A(f.document, f.binary, 4),
    expected = [];
  for (let i = 0; i < old.a.count; i += 3)
    expected.push([old.value(i), old.value(i + 1), old.value(i + 2)].join(","));
  assert.deepEqual(seen.sort(), expected.sort());
  const normal = M.normalizeSedan(f.document, f.binary, { targetLength: 4.4 }),
    before = worldPoints(normal.document, normal.binary).source,
    after = Object.values(worldPoints(out.document, out.binary)).flat();
  const sorted = (a) =>
    a.map((p) => p.map((v) => v.toFixed(10)).join(",")).sort();
  assert.deepEqual(sorted(after), sorted(before));
});
test("a wheel spins around its measured local X center without moving body or other wheels", () => {
  const f = articulatedFixture(),
    out = M.normalizeSedan(f.document, f.binary, {
      targetLength: 4.4,
      articulate: true,
    }),
    before = worldPoints(out.document, out.binary),
    part = out.report.components.find((p) => p.id === "wheel_front_left");
  const doc = structuredClone(out.document);
  doc.nodes[part.pivotNode].rotation = [Math.SQRT1_2, 0, 0, Math.SQRT1_2];
  const after = worldPoints(doc, out.binary),
    c = part.pivotNative;
  for (const name of Object.keys(before))
    if (name !== part.id) assert.deepEqual(after[name], before[name]);
  let moved = 0;
  before[part.id].forEach((p, i) => {
    const expected = [p[0], c[1] - (p[2] - c[2]), c[2] + (p[1] - c[1])];
    for (let k = 0; k < 3; k++)
      assert.ok(Math.abs(expected[k] - after[part.id][i][k]) < 1e-12);
    if (Math.hypot(...p.map((v, k) => v - after[part.id][i][k])) > 0.1) moved++;
  });
  assert.ok(moved > 0);
});
test("articulation rejects disconnected geometry without four verifiable wheel components", () => {
  const f = fixture();
  assert.throws(
    () =>
      M.normalizeSedan(f.document, f.binary, {
        targetLength: 4.4,
        articulate: true,
      }),
    /five disconnected/,
  );
});
test("CLI rejects unregistered bytes, unsafe filenames and occupied destinations before writing", () => {
  const directory = fs.mkdtempSync(
    path.join(__dirname, "../artifacts/sedan-test-"),
  );
  try {
    const input = path.join(directory, "input"),
      output = path.join(directory, "output");
    fs.mkdirSync(input);
    const bytes = Buffer.from("not the registered sedan");
    fs.writeFileSync(path.join(input, "source.glb"), bytes);
    const manifest = {
      assetId: "dc-hf-vehicle-sedan-01-tangents",
      file: "source.glb",
      sha256: require("node:crypto")
        .createHash("sha256")
        .update(bytes)
        .digest("hex"),
      derivedFrom: { sha256: "0".repeat(64) },
    };
    fs.writeFileSync(
      path.join(input, "source-manifest.json"),
      JSON.stringify(manifest),
    );
    assert.throws(
      () => M.exportPrepared(input, output),
      /registered sedan lineage/,
    );
    assert.equal(fs.existsSync(output), false);
    manifest.file = "../source.glb";
    fs.writeFileSync(
      path.join(input, "source-manifest.json"),
      JSON.stringify(manifest),
    );
    assert.throws(() => M.exportPrepared(input, output), /source filename/);
    assert.equal(fs.existsSync(output), false);
    assert.throws(() => M.exportPrepared(input, directory), /fresh confined/);
    assert.throws(
      () => M.exportPrepared(input, path.resolve(__dirname, "../src")),
      /fresh confined/,
    );
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});
