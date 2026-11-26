"use strict";
// Authoring only: uniform normalization and connected wheel separation. No runtime loader.
const fs = require("node:fs"),
  path = require("node:path"),
  crypto = require("node:crypto");
const {
  decodeGlb,
  encodeGlb,
  accessor,
} = require("./export_human_tangents.cjs");
const ROOT = path.resolve(__dirname, ".."),
  hash = (b) => crypto.createHash("sha256").update(b).digest("hex");
const IDENTITY = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1];
const bounds = (points) => {
  const min = [Infinity, Infinity, Infinity],
    max = [-Infinity, -Infinity, -Infinity];
  for (const p of points)
    for (let k = 0; k < 3; k++) {
      min[k] = Math.min(min[k], p[k]);
      max[k] = Math.max(max[k], p[k]);
    }
  return {
    min,
    max,
    size: max.map((v, k) => v - min[k]),
    center: max.map((v, k) => (v + min[k]) / 2),
  };
};
function inspect(document, binary, options) {
  if (options.sourceForward !== undefined && options.sourceForward !== "+Z")
    throw new Error("Source front must be verified +Z");
  if (options.sourceUp !== undefined && options.sourceUp !== "+Y")
    throw new Error("Source up must be verified +Y");
  if (
    !Number.isFinite(options.targetLength) ||
    options.targetLength < 1 ||
    options.targetLength > 20
  )
    throw new Error("Invalid target length in metres");
  if (
    document.animations?.length ||
    document.skins?.length ||
    document.extensionsUsed?.length ||
    document.extensionsRequired?.length ||
    document.extras?.sedanPreparation
  )
    throw new Error("Unsupported animated, extended or already prepared asset");
  if (
    document.buffers?.length !== 1 ||
    document.buffers[0].uri ||
    document.buffers[0].byteLength > binary.length ||
    document.images?.some((i) => i.uri)
  )
    throw new Error("Expected embedded source buffers and images");
  if (
    document.nodes?.length !== 1 ||
    document.meshes?.length !== 1 ||
    document.scenes?.length !== 1 ||
    document.scene !== 0 ||
    JSON.stringify(document.scenes[0].nodes) !== "[0]"
  )
    throw new Error("Expected one source node, mesh and scene");
  const node = document.nodes[0];
  if (
    node.mesh !== 0 ||
    node.children ||
    node.skin !== undefined ||
    node.translation ||
    node.rotation ||
    node.scale
  )
    throw new Error("Expected source matrix-only mesh node");
  const matrix = node.matrix || IDENTITY;
  if (matrix.length !== 16 || !matrix.every(Number.isFinite))
    throw new Error("Invalid source transform");
  const scale = matrix[0];
  if (
    scale <= 0 ||
    matrix[5] !== scale ||
    matrix[10] !== scale ||
    matrix[15] !== 1 ||
    [1, 2, 3, 4, 6, 7, 8, 9, 11].some((i) => matrix[i] !== 0)
  )
    throw new Error("Source must have positive uniform axis-aligned transform");
  if (document.meshes[0].primitives.length !== 1)
    throw new Error("Expected one source primitive");
  const primitive = document.meshes[0].primitives[0];
  if ((primitive.mode ?? 4) !== 4 || primitive.targets || primitive.extensions)
    throw new Error("Unsupported topology");
  const a = primitive.attributes;
  if (
    !["POSITION", "NORMAL", "TEXCOORD_0", "TANGENT"].every((k) =>
      Number.isInteger(a[k]),
    )
  )
    throw new Error("Source requires explicit tangents and PBR attributes");
  const pos = accessor(document, binary, a.POSITION),
    ix = accessor(document, binary, primitive.indices);
  if (
    pos.a.componentType !== 5126 ||
    pos.width !== 3 ||
    pos.a.normalized ||
    ix.width !== 1 ||
    ![5121, 5123, 5125].includes(ix.a.componentType) ||
    ix.a.count % 3
  )
    throw new Error("Unsupported position/index layout");
  for (const id of Object.values(a))
    if (accessor(document, binary, id).a.count !== pos.a.count)
      throw new Error("Attribute count mismatch");
  const local = Array.from({ length: pos.a.count }, (_, i) => [
    pos.value(i, 0),
    pos.value(i, 1),
    pos.value(i, 2),
  ]);
  if (local.some((v) => !v.every(Number.isFinite)))
    throw new Error("Nonfinite source positions");
  const indices = Array.from({ length: ix.a.count }, (_, i) => ix.value(i));
  if (indices.some((i) => !Number.isInteger(i) || i < 0 || i >= local.length))
    throw new Error("Invalid triangle index");
  const world = local.map((v) => v.map((x, k) => x * scale + matrix[12 + k]));
  return {
    primitive,
    local,
    world,
    indices,
    matrix,
    worldBounds: bounds(indices.map((i) => world[i])),
  };
}
function connectedComponents(source) {
  const parent = Array.from({ length: source.local.length }, (_, i) => i),
    root = (i) => {
      while (parent[i] !== i) {
        parent[i] = parent[parent[i]];
        i = parent[i];
      }
      return i;
    };
  const join = (a, b) => {
    a = root(a);
    b = root(b);
    if (a !== b) parent[b] = a;
  };
  const exact = new Map();
  source.local.forEach((v, i) => {
    const key = v.join(",");
    if (exact.has(key)) join(i, exact.get(key));
    else exact.set(key, i);
  });
  for (let i = 0; i < source.indices.length; i += 3) {
    join(source.indices[i], source.indices[i + 1]);
    join(source.indices[i], source.indices[i + 2]);
  }
  const groups = new Map();
  for (let i = 0; i < source.indices.length; i += 3) {
    const r = root(source.indices[i]);
    if (!groups.has(r)) groups.set(r, []);
    groups.get(r).push(i / 3);
  }
  return [...groups.values()]
    .map((triangles) => {
      const indices = triangles.flatMap((t) =>
        source.indices.slice(t * 3, t * 3 + 3),
      );
      return {
        triangles,
        indices,
        localBounds: bounds(indices.map((i) => source.local[i])),
        worldBounds: bounds(indices.map((i) => source.world[i])),
      };
    })
    .sort(
      (a, b) =>
        b.triangles.length - a.triangles.length ||
        b.worldBounds.size.reduce((a, b) => a * b, 1) -
          a.worldBounds.size.reduce((a, b) => a * b, 1),
    );
}
function wheelComponents(source) {
  const parts = connectedComponents(source);
  if (parts.length !== 5)
    throw new Error(
      "Wheel separation requires exactly five disconnected position components",
    );
  parts[0].id = "body";
  const used = new Set(),
    b = source.worldBounds;
  for (const part of parts.slice(1)) {
    const q = part.worldBounds,
      c = q.center,
      d = q.size,
      dx = c[0] - b.center[0],
      dz = c[2] - b.center[2];
    if (
      d[0] > 0.7 * Math.min(d[1], d[2]) ||
      Math.abs(d[1] / d[2] - 1) > 0.1 ||
      c[1] > b.min[1] + b.size[1] * 0.45 ||
      Math.abs(dx) < b.size[0] * 0.25 ||
      Math.abs(dz) < b.size[2] * 0.15
    )
      throw new Error(
        "Disconnected component does not satisfy measured wheel geometry",
      );
    // D.carPoint keeps local +Z forward at yaw 0; the driver/left door is X<0
    // in src/occupancy.js. These labels follow the vehicle, not the camera.
    part.id =
      "wheel_" +
      (dz > 0 ? "front" : "rear") +
      "_" +
      (dx < 0 ? "left" : "right");
    if (used.has(part.id)) throw new Error("Duplicate wheel quadrant");
    used.add(part.id);
  }
  return parts;
}
function normalizeSedan(input, bytes, options = { targetLength: 4.4 }) {
  const source = inspect(input, bytes, options),
    doc = structuredClone(input),
    s = options.targetLength / source.worldBounds.size[2];
  if (!Number.isFinite(s) || s <= 0)
    throw new Error("Collapsed longitudinal bounds");
  const translation = [
    -source.worldBounds.center[0] * s,
    -source.worldBounds.min[1] * s,
    -source.worldBounds.center[2] * s,
  ];
  const toNative = (p) => p.map((v, k) => v * s + translation[k]);
  const report = {
    units: "metres",
    upAxis: "+Y",
    forwardAxis: "+Z",
    targetLength: options.targetLength,
    sourceBounds: source.worldBounds,
    normalizedBounds: bounds(
      source.indices.map((i) => toNative(source.world[i])),
    ),
    uniformScale: s,
    translation,
    triangles: source.indices.length / 3,
    vertices: source.local.length,
    sourceBinaryBytes: bytes.length,
    sourceBinarySha256: hash(bytes),
    mapsAndAttributesPreserved: true,
    articulation: false,
  };
  let binary = Buffer.from(bytes);
  const chunks = [binary];
  let length = binary.length;
  if (options.articulate) {
    const parts = wheelComponents(source);
    delete doc.nodes[0].mesh;
    doc.nodes[0].children = [];
    doc.meshes = [];
    report.articulation = true;
    report.components = [];
    for (const part of parts) {
      const padding = (4 - (length % 4)) % 4;
      if (padding) {
        chunks.push(Buffer.alloc(padding));
        length += padding;
      }
      const indexBytes = Buffer.alloc(part.indices.length * 4);
      part.indices.forEach((v, i) => indexBytes.writeUInt32LE(v, i * 4));
      const view = doc.bufferViews.length;
      doc.bufferViews.push({
        buffer: 0,
        byteOffset: length,
        byteLength: indexBytes.length,
        target: 34963,
      });
      chunks.push(indexBytes);
      length += indexBytes.length;
      const index = doc.accessors.length;
      doc.accessors.push({
        bufferView: view,
        componentType: 5125,
        count: part.indices.length,
        type: "SCALAR",
        min: [part.indices.reduce((a, b) => Math.min(a, b), Infinity)],
        max: [part.indices.reduce((a, b) => Math.max(a, b), -Infinity)],
      });
      const mesh = doc.meshes.length;
      doc.meshes.push({
        name: part.id,
        primitives: [{ ...structuredClone(source.primitive), indices: index }],
      });
      const center = part.localBounds.center;
      let pivot = null;
      if (part.id === "body") {
        const id = doc.nodes.length;
        doc.nodes.push({ name: "sedan_body", mesh });
        doc.nodes[0].children.push(id);
      } else {
        pivot = doc.nodes.length;
        const child = pivot + 1;
        doc.nodes.push({
          name: "pivot_" + part.id,
          translation: center,
          children: [child],
          extras: {
            role: "measured-wheel-pivot",
            method: "exact-position-connected-component-AABB-center",
            rotationAxis: [1, 0, 0],
            mechanicalAxisCertified: false,
          },
        });
        doc.nodes.push({
          name: part.id,
          mesh,
          translation: center.map((v) => -v),
        });
        doc.nodes[0].children.push(pivot);
      }
      report.components.push({
        id: part.id,
        triangles: part.triangles.length,
        sourceTriangleIdsSha256: hash(
          Buffer.from(JSON.stringify(part.triangles)),
        ),
        sourceWorldBounds: part.worldBounds,
        nativeBounds: bounds(
          part.indices.map((i) => toNative(source.world[i])),
        ),
        pivotNode: pivot,
        pivotNative:
          part.id === "body" ? null : toNative(part.worldBounds.center),
        axleAxis: part.id === "body" ? null : "+X",
        radiusFromBounds:
          part.id === "body"
            ? null
            : ((part.worldBounds.size[1] + part.worldBounds.size[2]) * s) / 4,
      });
    }
    binary = Buffer.concat(chunks);
    doc.buffers[0].byteLength = length;
    report.addedIndexBytes = length - bytes.length;
  }
  const root = doc.nodes.length;
  doc.nodes.push({
    name: "Distrito_Cero_sedan_metres_grounded",
    children: [0],
    scale: [s, s, s],
    translation,
  });
  doc.scenes[0].nodes = [root];
  doc.extras = {
    ...(doc.extras || {}),
    sedanPreparation: {
      schema: 1,
      units: "metres",
      up: "+Y",
      forward: "+Z",
      groundY: 0,
      centerPolicy: "whole-mesh AABB midpoint XZ",
      articulation: report.articulation,
      authoringOnly: true,
    },
  };
  report.resultBinarySha256 = hash(binary);
  return { document: doc, binary, report };
}
function exportPrepared(inputDirectory, outputDirectory) {
  const input = path.resolve(inputDirectory),
    output = path.resolve(outputDirectory),
    artifacts = path.join(ROOT, "artifacts");
  if (
    !output.startsWith(artifacts + path.sep) ||
    fs.existsSync(output) ||
    !fs.realpathSync(path.dirname(output)).startsWith(artifacts + path.sep)
  )
    throw new Error("Use a fresh confined artifacts subdirectory");
  const manifestPath = path.join(input, "source-manifest.json"),
    manifestBytes = fs.readFileSync(manifestPath),
    manifest = JSON.parse(manifestBytes);
  if (
    typeof manifest.file !== "string" ||
    path.basename(manifest.file) !== manifest.file ||
    !manifest.file.endsWith(".glb")
  )
    throw new Error("Invalid source filename");
  const registryPath = path.join(
      ROOT,
      "assets/higgsfield-20261125/manifest.json",
    ),
    registryBytes = fs.readFileSync(registryPath),
    registry = JSON.parse(registryBytes),
    registered = registry.assets.find(
      (a) => a.asset_id === "dc-hf-vehicle-sedan-01",
    );
  const sourcePath = path.join(input, manifest.file),
    raw = fs.readFileSync(sourcePath);
  if (
    manifest.assetId !== "dc-hf-vehicle-sedan-01-tangents" ||
    manifest.sha256 !== hash(raw) ||
    registered.portableDerivative.sha256 !== hash(raw) ||
    manifest.derivedFrom?.sha256 !== registered.sourceSha256
  )
    throw new Error("Source hash or registered sedan lineage mismatch");
  const decoded = decodeGlb(raw),
    prepared = normalizeSedan(decoded.document, decoded.binary, {
      targetLength: 4.4,
      articulate: true,
    });
  const blob = encodeGlb(prepared.document, prepared.binary),
    file = "urban-sedan-native-authoring.glb";
  const report = {
    ...prepared.report,
    sourceGlbSha256: hash(raw),
    sourceManifestSha256: hash(manifestBytes),
    registeredManifestSha256: hash(registryBytes),
    frontEvidence:
      "Source render urban-sedan-front.png camera Blender (X+,Y-,Z+) shows grille/headlights; Blender -Y maps to glTF +Z.",
    nativeContract: {
      forward: "+Z",
      up: "+Y",
      wheelAxle: "+X",
      nativeWheelCentres: {
        front: [0.92, 0.365, 1.36],
        rear: [0.92, 0.365, -1.39],
      },
      nativeWheelRadius: 0.365,
    },
    limits: [
      "Wheel pivots are measured component AABB centers, not certified mechanical axes.",
      "Wheel rotation and steering hierarchy is authoring only; no native runtime buffers, collision, doors or cabin alignment supplied.",
      "Uniform length normalization preserves proportions; resulting width includes mirrors and differs from requested 1.8m.",
      "Three source 4096-square maps retained; no LOD or texture budget reduction.",
      "Source rights and artistic acceptance remain pending; validation does not establish AAA quality.",
    ],
  };
  const record = {
    schema: 1,
    assetId: "dc-hf-vehicle-sedan-01-native-authoring",
    file,
    bytes: blob.length,
    sha256: hash(blob),
    derivedFrom: {
      sha256: hash(raw),
      sourceManifestSha256: hash(manifestBytes),
    },
    officialValidation: "not-run",
    artisticAcceptance: "pending",
    runtimeIntegrated: false,
    rights: manifest.rights,
    provider: manifest.provider,
    model: manifest.model,
    jobId: manifest.jobId,
    sources: {
      "tools/prepare_higgsfield_sedan.cjs": hash(fs.readFileSync(__filename)),
      "tools/export_human_tangents.cjs": hash(
        fs.readFileSync(path.join(__dirname, "export_human_tangents.cjs")),
      ),
      "assets/higgsfield-20261125/manifest.json": hash(registryBytes),
    },
    limitations: report.limits,
  };
  if (
    hash(fs.readFileSync(sourcePath)) !== hash(raw) ||
    hash(fs.readFileSync(manifestPath)) !== hash(manifestBytes) ||
    hash(fs.readFileSync(registryPath)) !== hash(registryBytes)
  )
    throw new Error("Source changed during preparation");
  fs.mkdirSync(output);
  for (const [name, payload] of [
    [file, blob],
    ["source-manifest.json", JSON.stringify(record, null, 2) + "\n"],
    ["preparation-report.json", JSON.stringify(report, null, 2) + "\n"],
  ])
    fs.writeFileSync(path.join(output, name), payload, { flag: "wx" });
  return record;
}
module.exports = { normalizeSedan, connectedComponents, exportPrepared };
if (require.main === module) {
  try {
    if (process.argv.length !== 4)
      throw new Error(
        "Usage: node tools/prepare_higgsfield_sedan.cjs INPUT_DIR OUTPUT_DIR",
      );
    console.log(JSON.stringify(exportPrepared(...process.argv.slice(2))));
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
