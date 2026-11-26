"use strict";
// Offline contact guide for the articulated Higgsfield sedan published with PR #66.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const {
  decodeGlb,
  encodeGlb,
  accessor,
} = require("./export_human_tangents.cjs");

const SOURCE_SHA =
  "1b3d9ef2f0824f18a9ef0146031deee55cde568b722456bda246ff81ade74a89";
const SIDES = 64;
const sha = (data) => crypto.createHash("sha256").update(data).digest("hex");

function cross2(a, b, c) {
  return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0]);
}

function convexHull(points) {
  const sorted = [...points].sort((a, b) => a[0] - b[0] || a[1] - b[1]);
  const unique = sorted.filter(
    (p, i) => !i || p[0] !== sorted[i - 1][0] || p[1] !== sorted[i - 1][1],
  );
  function chain(ordered) {
    const half = [];
    for (const p of ordered) {
      while (half.length >= 2 && cross2(half.at(-2), half.at(-1), p) <= 0)
        half.pop();
      half.push(p);
    }
    return half.slice(0, -1);
  }
  return [...chain(unique), ...chain(unique.reverse())];
}

// At every roll angle ground support is the largest projection of a tyre point
// on the downward direction. The full angular range is the centred inradius
// through the circumradius of its 2D convex hull.
function contactEnvelope(points) {
  const hull = convexHull(points);
  if (hull.length < 3) throw Error("Degenerate wheel profile");
  let min = Infinity,
    max = 0;
  for (let i = 0; i < hull.length; i++) {
    const a = hull[i],
      b = hull[(i + 1) % hull.length];
    const distance =
      (a[0] * b[1] - a[1] * b[0]) / Math.hypot(b[0] - a[0], b[1] - a[1]);
    if (!(distance > 0))
      throw Error("Expected the axle inside the projected tyre");
    min = Math.min(min, distance);
    max = Math.max(max, Math.hypot(...a));
  }
  return { min, max, hull };
}

function measureWheels(doc, binary) {
  // The SHA-pinned authoring GLB has a positive uniform scale at its root,
  // an original uniformly scaled mesh group, and counter-translated wheel children.
  const root = doc.nodes[doc.scenes[doc.scene].nodes[0]];
  const group = doc.nodes[root.children[0]];
  const scale = root.scale[0] * group.matrix[0];
  return doc.nodes
    .filter((n) => n.name?.startsWith("pivot_wheel_"))
    .map((pivot) => {
      const child = doc.nodes[pivot.children[0]];
      const prim = doc.meshes[child.mesh].primitives[0];
      const indices = accessor(doc, binary, prim.indices);
      const pos = accessor(doc, binary, prim.attributes.POSITION);
      const ids = new Set(
        Array.from({ length: indices.a.count }, (_, i) => indices.value(i)),
      );
      const center = pivot.translation.map(
        (v, k) =>
          (v * group.matrix[0] + group.matrix[12 + k]) * root.scale[0] +
          root.translation[k],
      );
      // All coordinates below are in metres, relative to the actual imported pivot.
      const local = [...ids].map((i) =>
        [0, 1, 2].map((k) => (pos.value(i, k) + child.translation[k]) * scale),
      );
      const width =
        Math.max(...local.map((p) => p[0])) -
        Math.min(...local.map((p) => p[0]));
      const tyre = contactEnvelope(local.map((p) => p.slice(1)));
      const radius = center[1];
      const minBottom = radius - tyre.max,
        maxBottom = radius - tyre.min;
      const faceting = radius * (1 - Math.cos(Math.PI / SIDES));
      let squaredSum = 0;
      for (let degree = 0; degree < 360; degree++) {
        const theta = (degree * Math.PI) / 180;
        const support = Math.max(
          ...tyre.hull.map(
            ([y, z]) => -y * Math.cos(theta) + z * Math.sin(theta),
          ),
        );
        squaredSum += (radius - support) ** 2;
      }
      return {
        id: child.name,
        center,
        radius,
        width,
        axle: [1, 0, 0],
        referencedSourceVertices: ids.size,
        projectedHullVertices: tyre.hull.length,
        sourceGroundRangeContinuousM: [minBottom, maxBottom],
        sourceGroundRestM: radius + Math.min(...local.map((p) => p[1])),
        analyticGroundM: 0,
        maximumAbsoluteAnalyticContactErrorM: Math.max(-minBottom, maxBottom),
        analyticContactRmsAtOneDegreeM: Math.sqrt(squaredSum / 360),
        previewFacetingUpperBoundM: faceting,
        conservativeMeshToSourceSupportErrorM:
          Math.max(-minBottom, maxBottom) + faceting,
      };
    })
    .sort((a, b) => a.id.localeCompare(b.id, "en"));
}

function encodeProxy(wheels) {
  const positions = [],
    indices = [];
  // Left/right rings and cap centres share positions, closing every mesh edge.
  for (const x of [-0.5, 0.5]) {
    for (let i = 0; i < SIDES; i++) {
      const t = (2 * Math.PI * i) / SIDES;
      positions.push(x, Math.cos(t), Math.sin(t));
    }
  }
  positions.push(-0.5, 0, 0, 0.5, 0, 0);
  for (let i = 0; i < SIDES; i++) {
    const j = (i + 1) % SIDES;
    indices.push(
      i,
      j,
      j + SIDES,
      i,
      j + SIDES,
      i + SIDES,
      2 * SIDES,
      j,
      i,
      2 * SIDES + 1,
      i + SIDES,
      j + SIDES,
    );
  }
  const vertices = Buffer.alloc(positions.length * 4),
    faces = Buffer.alloc(indices.length * 2);
  positions.forEach((v, i) => vertices.writeFloatLE(v, 4 * i));
  indices.forEach((v, i) => faces.writeUInt16LE(v, 2 * i));
  const binary = Buffer.concat([vertices, faces]);
  const nodes = wheels.map((w) => ({
    name: "contact_" + w.id,
    mesh: 0,
    translation: w.center,
    scale: [w.width, w.radius, w.radius],
    extras: { radiusMetres: w.radius, widthMetres: w.width, axle: [1, 0, 0] },
  }));
  const doc = {
    asset: { version: "2.0", generator: "Distrito Cero wheel contact guide" },
    scene: 0,
    scenes: [{ nodes: nodes.map((_, i) => i) }],
    nodes,
    meshes: [
      {
        name: "wheel_contact_cylinder",
        primitives: [{ attributes: { POSITION: 0 }, indices: 1, material: 0 }],
      },
    ],
    materials: [
      {
        name: "contact guide",
        pbrMetallicRoughness: {
          baseColorFactor: [0.03, 0.65, 0.39, 1],
          metallicFactor: 0,
          roughnessFactor: 0.8,
        },
      },
    ],
    buffers: [{ byteLength: binary.length }],
    bufferViews: [
      { buffer: 0, byteLength: vertices.length, target: 34962 },
      {
        buffer: 0,
        byteOffset: vertices.length,
        byteLength: faces.length,
        target: 34963,
      },
    ],
    accessors: [
      {
        bufferView: 0,
        componentType: 5126,
        type: "VEC3",
        count: positions.length / 3,
        min: [-0.5, -1, -1],
        max: [0.5, 1, 1],
      },
      {
        bufferView: 1,
        componentType: 5123,
        type: "SCALAR",
        count: indices.length,
        min: [0],
        max: [positions.length / 3 - 1],
      },
    ],
  };
  return encodeGlb(doc, binary);
}

function prepare(file, output) {
  const bytes = fs.readFileSync(file);
  if (sha(bytes) !== SOURCE_SHA)
    throw Error("Input SHA must match the reviewed articulated sedan");
  const { document: doc, binary } = decodeGlb(bytes);
  const wheels = measureWheels(doc, binary);
  if (wheels.length !== 4) throw Error("Expected four wheel pivots");
  const glb = encodeProxy(wheels);
  const report = {
    schema: 1,
    sourceSha256: SOURCE_SHA,
    units: "metres",
    axes: "Y up; Z forward; X axle",
    method:
      "Flat undeformed ground at Y=0, fixed chassis. Use pivot height as analytic radius; measure source indexed triangles in every roll direction using their YZ convex hull.",
    preview: {
      sides: SIDES,
      meshVertices: 2 * SIDES + 2,
      meshTriangles: 4 * SIDES,
      meshInstances: 4,
    },
    wheels,
  };
  const reportBytes = JSON.stringify(report, null, 2) + "\n";
  const manifest = {
    schema: 1,
    file: "wheel-contact-proxy.glb",
    sha256: sha(glb),
    bytes: glb.length,
    derivedFrom: { sha256: SOURCE_SHA },
    producerSha256: sha(fs.readFileSync(__filename)),
    contactReportSha256: sha(reportBytes),
    role: "Offline static flat-ground authoring guide",
    officialValidation: "not-run",
    runtimeIntegrated: false,
  };
  fs.mkdirSync(output);
  try {
    fs.writeFileSync(path.join(output, manifest.file), glb, { flag: "wx" });
    fs.writeFileSync(path.join(output, "wheel-contact.json"), reportBytes, {
      flag: "wx",
    });
    fs.writeFileSync(
      path.join(output, "source-manifest.json"),
      JSON.stringify(manifest, null, 2) + "\n",
      { flag: "wx" },
    );
  } catch (error) {
    // mkdir succeeded exclusively for this attempt, so only its partial output is removed.
    fs.rmSync(output, { recursive: true, force: true });
    throw error;
  }
  return manifest;
}

module.exports = { contactEnvelope, encodeProxy, prepare };
if (require.main === module) {
  try {
    if (process.argv.length !== 4)
      throw Error(
        "Usage: node tools/prepare_sedan_contact_proxy.cjs ARTICULATED_GLB NEW_DIRECTORY",
      );
    console.log(JSON.stringify(prepare(...process.argv.slice(2))));
  } catch (e) {
    console.error(e.message);
    process.exitCode = 1;
  }
}
