'use strict';
// Offline recipe for the single, identified static character. Its bind pose is
// sideways in glTF: Y is vertical and the spread arms run along Z.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {decodeGlb, encodeGlb, accessor, addTangents, loadGenerator} = require('./export_human_tangents.cjs');

const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const source = require('../assets/higgsfield-20261125/manifest.json').assets.find(a => a.asset_id === 'dc-hf-character-urban-01');
const options = {targetFraction: .60, relativeErrorLimit: .012, weights: [.25, .25, .25, 1, 1]};

function floatStream(attr) {
  return Float32Array.from({length:attr.a.count * attr.width}, (_,i) => attr.value(Math.floor(i/attr.width), i%attr.width));
}

// The tangent exporter deliberately retains provenance buffers. This delivery
// only needs the current primitive and the embedded image buffer views.
function packCurrentPrimitive(doc, binary) {
  const views = [], acc = [], chunks = [];
  let size = 0;
  function copyView(id) {
    const view = doc.bufferViews[id], start = view.byteOffset || 0;
    const pad = (4-size%4)%4;
    if (pad) chunks.push(Buffer.alloc(pad));
    size += pad;
    const newIndex = views.length;
    views.push({...view, byteOffset:size});
    chunks.push(binary.subarray(start,start+view.byteLength));
    size += view.byteLength;
    return newIndex;
  }
  function copyAccessor(id) {
    const a = doc.accessors[id];
    acc.push({...a, bufferView:copyView(a.bufferView)});
    return acc.length-1;
  }
  const p = doc.meshes[0].primitives[0];
  for (const key of Object.keys(p.attributes)) p.attributes[key] = copyAccessor(p.attributes[key]);
  p.indices = copyAccessor(p.indices);
  for (const image of doc.images) image.bufferView = copyView(image.bufferView);
  doc.accessors = acc;
  doc.bufferViews = views;
  doc.buffers[0].byteLength = size;
  return encodeGlb(doc, Buffer.concat(chunks));
}

async function main() {
  const [filename, output, meshoptDir, mikkDir] = process.argv.slice(2);
  if (process.argv.length !== 6) throw Error('Usage: node tools/prepare_higgsfield_character_lod.cjs PORTABLE_GLB NEW_DIRECTORY MESHOPTIMIZER_DIR MIKKTSPACE_DIR');
  const raw = fs.readFileSync(filename);
  if (sha256(raw) !== source.portableDerivative.sha256) throw Error('Expected the manifest-matched character GLB with tangents');
  if (fs.existsSync(output)) throw Error('Output directory already exists');
  const meshoptPath = path.resolve(meshoptDir);
  const pkg = JSON.parse(fs.readFileSync(path.join(meshoptPath,'package.json')));
  if (pkg.name !== 'meshoptimizer' || pkg.version !== '0.23.0') throw Error('Expected meshoptimizer 0.23.0');
  const {MeshoptSimplifier} = require(meshoptPath);
  await MeshoptSimplifier.ready;
  const {document:doc, binary} = decodeGlb(raw);
  const p = doc.meshes[0].primitives[0];
  const read = key => accessor(doc,binary,p.attributes[key]);
  const pos = read('POSITION'), normal = read('NORMAL'), uv = read('TEXCOORD_0');
  const indices = accessor(doc,binary,p.indices);
  const all = Uint32Array.from({length:indices.a.count}, (_,i) => indices.value(i));
  const attrs = new Float32Array(pos.a.count*5);
  const lock = new Uint8Array(pos.a.count);
  for (let i=0;i<pos.a.count;i++) {
    attrs.set([normal.value(i,0),normal.value(i,1),normal.value(i,2),uv.value(i,0),uv.value(i,1)], i*5);
    // A collar of locked neighbours around the protected test zones prevents
    // a collapse just outside the head or hands from swallowing their edges.
    lock[i] = +(pos.value(i,1) >= .35 || Math.abs(pos.value(i,2)) >= .415);
  }
  // Weld positions only for edge incidence, keeping UV/normal seam vertices
  // distinct in the export. Keep inherited defects tied to their source IDs.
  const unique = new Map();
  const geomId = Array.from({length: pos.a.count}, (_,i) => {
    const key = pos.row(i).toString('hex');
    if (!unique.has(key)) unique.set(key, unique.size);
    return unique.get(key);
  });
  const xyz = id => [0,1,2].map(k => pos.value(id,k));
  function violations(order, baseline) {
    const incident = new Map(), opposed = new Set(), retain = new Set();
    function preserve(ids) { for (const id of ids) retain.add(id); }
    for (let i = 0; i < order.length; i += 3) {
      const ids = [order[i],order[i+1],order[i+2]];
      const [a,b,c] = ids;
      const det = (uv.value(b,0)-uv.value(a,0)) * (uv.value(c,1)-uv.value(a,1))
        - (uv.value(c,0)-uv.value(a,0)) * (uv.value(b,1)-uv.value(a,1));
      if (det >= 0) preserve(ids);
      const [v,w,x] = ids.map(xyz);
      const ab = w.map((n,k) => n-v[k]), ac = x.map((n,k) => n-v[k]);
      const fn = [0,1,2].map(k => ab[(k+1)%3]*ac[(k+2)%3] - ab[(k+2)%3]*ac[(k+1)%3]);
      const agreement = ids.reduce((s,id) => s+fn.reduce((t,n,k) => t+n*normal.value(id,k),0),0);
      if (agreement <= 0) {
        const tri = [...ids].sort((x,y) => x-y).join('/');
        opposed.add(tri);
        if (baseline && !baseline.opposed.has(tri)) preserve(ids);
      }
      for (let j=0; j<3; j++) {
        const from=geomId[ids[j]], to=geomId[ids[(j+1)%3]];
        const edge = from < to ? from+'/'+to : to+'/'+from;
        if (!incident.has(edge)) incident.set(edge, []);
        incident.get(edge).push(ids[j],ids[(j+1)%3]);
      }
    }
    if (baseline) for (const [edge,ends] of incident) {
      if (ends.length !== 4 && baseline.incident.get(edge)?.length !== ends.length) preserve(ends);
    }
    return {incident,opposed,retain};
  }
  const topology = violations(all);
  if (topology.retain.size) throw Error('Unrecognized source UV orientation');
  const positions = floatStream(pos);
  let order, error, attempts = 0;
  for (;;) {
    [order,error] = MeshoptSimplifier.simplifyWithAttributes(all, positions, 3, attrs, 5, options.weights, lock,
      Math.floor(all.length/3*options.targetFraction)*3, options.relativeErrorLimit, ['LockBorder']);
    attempts++;
    const folds = violations(order,topology).retain;
    if (!folds.size) break;
    if (attempts >= 12) throw Error('Unable to preserve UV winding and edge topology at this budget');
    // Preserve each incident source triangle on the next attempt. Locking
    // just the final three vertices would still permit the same collapse.
    for (let i=0; i<all.length; i+=3) {
      const a=all[i], b=all[i+1], c=all[i+2];
      if (folds.has(a) || folds.has(b) || folds.has(c)) lock[a]=lock[b]=lock[c]=1;
    }
  }
  if (order.length > all.length*.65) throw Error('Protected source exceeds the intermediate LOD budget');

  const bytes = Buffer.alloc(order.length*4);
  order.forEach((v,i) => bytes.writeUInt32LE(v,4*i));
  const newView = doc.bufferViews.length;
  doc.bufferViews.push({buffer:0, byteOffset:binary.length, byteLength:bytes.length,target:34963});
  p.indices = doc.accessors.length;
  doc.accessors.push({bufferView:newView,componentType:5125,type:'SCALAR',count:order.length});
  doc.buffers[0].byteLength = binary.length + bytes.length;
  delete p.attributes.TANGENT;
  const generator = loadGenerator(mikkDir);
  const result = addTangents(doc, Buffer.concat([binary,bytes]), generator.generateTangents);
  if (result.report.primitives[0].degenerateUvTriangles) throw Error('Reduction produced a collapsed UV triangle');
  const blob = packCurrentPrimitive(result.document,result.binary);
  const file = 'urban-character-intermediate.glb';
  const record = {assetId:'dc-hf-character-urban-01-intermediate',file,sha256:sha256(blob),bytes:blob.length,
    derivedFrom:{sha256:source.portableDerivative.sha256,assetId:source.asset_id},recipeSha256:sha256(fs.readFileSync(__filename)),
    simplifier:{name:pkg.name,version:pkg.version,...options,attempts,relativeAttributeWeightedError:error,lockedVertices:lock.reduce((a,b) => a+b,0)},
    sourceTriangles:all.length/3,triangles:order.length/3,tangents:result.report.primitives[0],tangentToolchain:generator.provenance,
    officialValidation:'not-run',artisticAcceptance:'pending',scope:'Static authoring LOD of the unrigged Higgsfield character'};
  fs.mkdirSync(output);
  try {
    fs.writeFileSync(path.join(output,file),blob,{flag:'wx'});
    fs.writeFileSync(path.join(output,'source-manifest.json'), JSON.stringify(record,null,2)+'\n',{flag:'wx'});
  } catch (error) {
    for (const name of [file,'source-manifest.json']) fs.rmSync(path.join(output,name),{force:true});
    fs.rmdirSync(output);
    throw error;
  }
  console.log(JSON.stringify({file,triangles:record.triangles,bytes:record.bytes,sha256:record.sha256}));
}
main().catch(error => {console.error(error.message);process.exitCode=1;});
