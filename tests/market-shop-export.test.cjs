'use strict';
const {test}=require('node:test'),assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path');
const {decodeGlb,accessor}=require('../tools/export_human_tangents.cjs');
const root=path.resolve(__dirname,'..'),file=path.join(root,'assets/mercado-20261126/escaparate-esquina.glb');
const {document:d,binary:b}=decodeGlb(fs.readFileSync(file));
const parts=d.nodes.filter(n=>n.mesh!==undefined);
const meshes=n=>d.meshes[n.mesh].primitives;
const material=n=>d.materials[meshes(n)[0].material];
const named=name=>parts.find(n=>n.name===name);

test('the Mercado shop kit keeps the two windows, fixture, stock and native sign',()=>{
 assert.deepEqual(d.nodes[0].extras.cell,[1,2]);
 assert.deepEqual(d.nodes[0].extras.buildingCenter,[140.5,195.5]);
 assert.equal(d.nodes[0].extras.worldSeed,1337);
 assert.equal(parts.length,47);
 assert.equal(parts.filter(n=>n.name.startsWith('Producto')).length,15);
 assert.equal(parts.filter(n=>n.name.startsWith('Bandeja')).length,3);
 assert.equal(parts.filter(n=>n.name.startsWith('Balda')).length,4);
 const lamp=named('Tira de luz');
 assert.ok(Math.abs(lamp.scale[0]-5.4)<.0001);
 assert.ok(material(lamp).emissiveFactor.every(c=>c>0));
 for(const n of parts.filter(n=>n.name.startsWith('Producto')||n.name.startsWith('Balda')))
  assert.equal(material(n).emissiveFactor,undefined);
 for(const name of ['Cristal frontal','Cristal lateral']){
  assert.equal(material(named(name)).alphaMode,'BLEND');
  assert.equal(material(named(name)).doubleSided,true);
 }
 const front=material(named('Rótulo · cara impresa'));
 assert.equal(front.pbrMetallicRoughness.baseColorTexture.index,front.emissiveTexture.index);
 assert.equal(material(named('Rótulo · carcasa')).pbrMetallicRoughness.baseColorTexture,undefined);
 const view=d.bufferViews[d.images[d.textures[front.emissiveTexture.index].source].bufferView];
 const header=b.subarray(view.byteOffset,view.byteOffset+24);
 assert.equal(header.toString('ascii',1,4),'PNG');
 assert.deepEqual([header.readUInt32BE(16),header.readUInt32BE(20)],[512,256]);
});

test('the sign split preserves 12 triangles and the installed module totals 532',()=>{
 let triangles=0;
 for(const n of parts)for(const p of meshes(n)){
  const pos=accessor(d,b,p.attributes.POSITION);triangles+=pos.a.count/3;
  if(n.name==='Rótulo · cara impresa'){
   const uv=accessor(d,b,p.attributes.TEXCOORD_0),normals=accessor(d,b,p.attributes.NORMAL);
   assert.equal(pos.a.count,6);
   for(let i=0;i<pos.a.count;i++){
    assert.equal(normals.value(i,2),1);
    assert.equal(uv.value(i,1),.5-pos.value(i,1));
   }
  }
  if(n.name==='Rótulo · carcasa')assert.equal(pos.a.count,30);
 }
 assert.equal(triangles,532);
});
