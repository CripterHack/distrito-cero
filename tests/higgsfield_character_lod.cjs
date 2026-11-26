'use strict';
// Integration check with the portable Higgsfield model from the review archive.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {decodeGlb, accessor} = require('../tools/export_human_tangents.cjs');

function load(file) {
  const {document: doc, binary} = decodeGlb(fs.readFileSync(file));
  const primitive = doc.meshes[0].primitives[0];
  const read = id => accessor(doc, binary, id);
  const images = doc.images.map(image => {
    const view = doc.bufferViews[image.bufferView];
    return crypto.createHash('sha256').update(binary.subarray(view.byteOffset, view.byteOffset + view.byteLength)).digest('hex');
  });
  const vertices = Object.fromEntries(Object.entries(primitive.attributes).map(([key, id]) => [key, read(id)]));
  const indices = read(primitive.indices);
  const protectedFaces = [];
  const edges = new Map(), opposed = new Set();
  let degenerateUVs = 0, reversedUVs = 0;
  for (let i = 0; i < indices.a.count; i += 3) {
    const tri = [0, 1, 2].map(j => indices.value(i+j));
    const v = vertices.POSITION, uv = vertices.TEXCOORD_0;
    // The authored head and extremities are the two high-detail review zones.
    if (tri.every(k => v.value(k, 1) >= .36 || Math.abs(v.value(k, 2)) >= .425)) {
      const keys = tri.map(k => Buffer.concat([v.row(k), vertices.NORMAL.row(k), uv.row(k)]).toString('hex'));
      // Cyclic rotations index the same oriented triangle.
      protectedFaces.push([0, 1, 2].map(j => [...keys.slice(j), ...keys.slice(0, j)].join('/')).sort()[0]);
    }
    const [a,b,c] = tri.map(k => [uv.value(k, 0), uv.value(k, 1)]);
    const determinant = (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0]);
    if (!determinant) degenerateUVs++;
    if (determinant > 0) reversedUVs++;
    const keys = tri.map(k => v.row(k).toString('hex'));
    for (let j=0; j<3; j++) {
      const edge = [keys[j],keys[(j+1)%3]].sort().join('/');
      edges.set(edge, (edges.get(edge)||0)+1);
    }
    const xyz = tri.map(k => [0,1,2].map(axis => v.value(k,axis)));
    const x = xyz[1].map((v,j) => v-xyz[0][j]), y = xyz[2].map((v,j) => v-xyz[0][j]);
    const cross = [0,1,2].map(k => x[(k+1)%3]*y[(k+2)%3] - x[(k+2)%3]*y[(k+1)%3]);
    assert.ok(Math.hypot(...cross) > 0);
    if (tri.reduce((s,id) => s+cross.reduce((q,v,k) => q+v*vertices.NORMAL.value(id,k),0),0) <= 0) {
      opposed.add(tri.map(k => Buffer.concat([v.row(k), vertices.NORMAL.row(k), uv.row(k)]).toString('hex')).sort().join('/'));
    }
  }
  return {doc, images, vertices, reversedUVs, opposed, edges, triangles: indices.a.count/3, protectedFaces: protectedFaces.sort(), degenerateUVs};
}

const [originalFile, derivativeFile] = process.argv.slice(2);
const source = load(originalFile), lod = load(derivativeFile);
assert.equal(source.triangles, 47321);
assert.ok(lod.triangles <= source.triangles * .65, 'reduce drawn triangles by at least 35 percent');
assert.deepEqual(lod.images, source.images);
for (const key of ['materials', 'textures', 'scenes','nodes']) assert.deepEqual(lod.doc[key], source.doc[key]);
assert.ok(source.protectedFaces.length > 1000);
assert.deepEqual(lod.protectedFaces, source.protectedFaces);
assert.equal(lod.degenerateUVs, 0);
assert.equal(lod.reversedUVs, 0);
for (const [key,count] of lod.edges) if (count !== 2) assert.equal(source.edges.get(key),count,'new anomalous geometric edge');
for (const key of lod.opposed) assert.ok(source.opposed.has(key),'new opposed face/vertex normal');
const {NORMAL: normal, TANGENT: tangent} = lod.vertices;
for (let i = 0; i < normal.a.count; i++) {
  const n = [0,1,2].map(k => normal.value(i,k)), t = [0,1,2].map(k => tangent.value(i,k));
  assert.ok(Math.abs(Math.hypot(...n)-1) < 1e-4 && Math.abs(Math.hypot(...t)-1) < 1e-4);
  assert.ok(Math.abs(t.reduce((sum,x,k) => sum+x*n[k],0)) < 1e-4 && Math.abs(tangent.value(i,3)) === 1);
}
console.log(JSON.stringify({sourceTriangles:source.triangles, triangles:lod.triangles, protectedFaces:source.protectedFaces.length,
  comparedImageHashes:source.images, zeroAreaUVs:lod.degenerateUVs, reversedUVs:lod.reversedUVs, checkedFrames:normal.a.count,
  sourceOpposed:source.opposed.size, retainedOpposed:lod.opposed.size,
  boundary:[...lod.edges.values()].filter(n=>n===1).length, nonmanifold:[...lod.edges.values()].filter(n=>n>2).length}));
