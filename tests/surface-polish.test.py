"""Checks the actual quantized model, not authoring intentions."""
from pathlib import Path
import json,base64,unittest
import numpy as np
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def load(path):return json.loads(path.read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
class Polish(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.new=load(R/'src/hero-asset.js');cls.old=load(R/'assets/hero-v012-baseline.js')
 def test_shoulders_are_revised_without_unbounded_volume_change(self):
  get=lambda d:np.frombuffer(base64.b64decode(next(p for p in d['parts'] if p['name']=='jacket')['data']),DT)
  n,o=get(self.new),get(self.old);delta=np.linalg.norm(n['p'].astype(float)-o['p'],axis=1)/1e4
  self.assertGreater(np.count_nonzero(delta>.00015),200);self.assertLess(delta.max(),.007)
 def test_head_hands_and_skin_maps_are_not_accidentally_replaced(self):
  for key in ['face','nails','scalp']:
   get=lambda d:next(p for p in d['parts']if p['name']==key)['data'];self.assertEqual(get(self.new),get(self.old))
 def test_hands_keep_shape_and_weights_with_no_split_normals(self):
  get=lambda d:np.frombuffer(base64.b64decode(next(p for p in d['parts'] if p['name']=='skin')['data']),DT)
  n,o=get(self.new),get(self.old)
  for field in ['p','j','w','uv']:self.assertTrue(np.array_equal(n[field],o[field]))
  keys={}
  for point,normal in zip(n['p'],n['n']):
   key=tuple(point)
   if key in keys:self.assertTrue(np.array_equal(normal,keys[key]),'quantized shared vertices must not have split skin normals')
   keys[key]=normal
 def test_no_topology_inflation_or_bone_contract_change(self):
  self.assertEqual(self.new['bones'],self.old['bones']);self.assertEqual(sum(x['vertices'] for x in self.new['parts']),sum(x['vertices']for x in self.old['parts']))
 def test_polished_normals_weights_and_winding(self):
  for n,o in zip(self.new['parts'],self.old['parts']):
   a=np.frombuffer(base64.b64decode(n['data']),DT);b=np.frombuffer(base64.b64decode(o['data']),DT)
   self.assertTrue(np.allclose(np.linalg.norm(a['n']/32767,axis=1),1,atol=.002));self.assertTrue(np.all(a['w'].sum(1)==255))
   if n['name']in ['jacket','pants']:
    va=a['p'].astype(float).reshape(-1,3,3);vb=b['p'].astype(float).reshape(-1,3,3)
    na=np.cross(va[:,1]-va[:,0],va[:,2]-va[:,0]);nb=np.cross(vb[:,1]-vb[:,0],vb[:,2]-vb[:,0])
    self.assertGreaterEqual(np.sum(na*nb,axis=1).min(),0)
if __name__=='__main__':unittest.main()
