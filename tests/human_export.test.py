"""Structural checks on the actual v0.9 textured authoring export, not historical GLBs."""
from pathlib import Path
import unittest, json, struct, io, math
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parents[1]
class HumanExport(unittest.TestCase):
 def test_textured_rigged_export(self):
  f=R/'assets/dc09-human-textured.glb'
  self.assertTrue(f.is_file(),'v0.9 textured export is missing')
  b=f.read_bytes();self.assertEqual(struct.unpack_from('<4sII',b),(b'glTF',2,len(b)))
  n,t=struct.unpack_from('<II',b,12);self.assertEqual(t,0x4e4f534a);d=json.loads(b[20:20+n]);raw=b[28+n:]
  self.assertEqual(len(d['meshes']),12);self.assertEqual(len(d['skins'][0]['joints']),17);self.assertEqual(len(d['animations']),5)
  self.assertIn('MakeHuman',d['asset']['copyright']);self.assertEqual(len(d['images']),3)
  for v in d['bufferViews']:self.assertLessEqual(v.get('byteOffset',0)+v['byteLength'],len(raw))
  for im in d['images']:
   self.assertEqual(im['mimeType'],'image/png');self.assertNotIn('uri',im);v=d['bufferViews'][im['bufferView']];png=raw[v.get('byteOffset',0):v.get('byteOffset',0)+v['byteLength']]
   p=Image.open(io.BytesIO(png));p.load();self.assertLessEqual(max(p.size),512)
  face=next(m for m in d['materials'] if m['name']=='face');self.assertIn('baseColorTexture',face['pbrMetallicRoughness']);self.assertIn('metallicRoughnessTexture',face['pbrMetallicRoughness']);self.assertIn('normalTexture',face)
  self.assertEqual(face['pbrMetallicRoughness']['baseColorFactor'],[1,1,1,1])
  def read(i):
   a=d['accessors'][i];v=d['bufferViews'][a['bufferView']];k={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];typ={5126:'<f4',5123:'<u2',5125:'<u4',5121:'u1'}[a['componentType']]
   return np.frombuffer(raw,dtype=typ,count=a['count']*k,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,k)
  for mesh in d['meshes']:
   p=mesh['primitives'][0];a=p['attributes'];pos=read(a['POSITION']);no=read(a['NORMAL']);self.assertTrue(np.isfinite(pos).all());self.assertTrue(np.allclose(np.linalg.norm(no,axis=1),1,atol=.002))
   self.assertLess(int(read(p['indices']).max()),len(pos));self.assertTrue((read(a['WEIGHTS_0']).sum(1)==255).all());self.assertLess(int(read(a['JOINTS_0']).max()),17)
  for anim in d['animations']:
   self.assertEqual(len(anim['channels']),18)
   for c in anim['channels']:
    s=anim['samplers'][c['sampler']];ti=read(s['input']);o=read(s['output']);self.assertEqual(len(ti),len(o));self.assertTrue((np.diff(ti[:,0])>0).all());self.assertTrue(np.isfinite(o).all());self.assertTrue(np.allclose(o[0],o[-1],atol=1e-5))
    if c['target']['path']=='rotation':self.assertTrue(np.allclose(np.linalg.norm(o,axis=1),1,atol=1e-5))
if __name__=='__main__':unittest.main()
