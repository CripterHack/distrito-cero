"""Artist-directed neck acceptance. Bounds are for this avatar, not population norms."""
import json,base64,unittest
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def parts(path):
 d=json.loads(path.read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
 return {p['name']:np.frombuffer(base64.b64decode(p['data']),DT) for p in d['parts']}
a=parts(R/'src/hero-asset.js');b=parts(R/'assets/hero-v013-baseline.js')
class Cervical(unittest.TestCase):
 def test_lateral_submandibular_not_a_midneck_nodule(self):
  v=a['face']['p']/10000
  m=(v[:,1]>1.543)&(v[:,1]<1.573)&(v[:,2]<.039)&(np.abs(v[:,0])>.028)
  self.assertGreater(m.sum(),90)
  self.assertLess(float(np.max(np.abs(v[m,0]))),.0530)
 def test_low_neck_is_still_welded_with_the_head(self):
  d=a['face'];p=d['p'];unique,inv=np.unique(p,axis=0,return_inverse=True);f=inv.reshape(-1,3)
  edges=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);edges.sort(axis=1);e,c=np.unique(edges,axis=0,return_counts=True)
  # Only the inherited mouth/eye openings and the lower shirt-hidden neck rim may be open.
  exposed=unique[e[c==1]]/10000
  m=(exposed[:,:,1].min(1)>1.46)&(exposed[:,:,1].max(1)<1.60)
  self.assertEqual(int(m.sum()),0)
 def test_jaw_chin_and_facial_landmarks_preserved(self):
  p=b['face']['p']/10000;m=(p[:,1]>1.625)|((p[:,2]>.092)&(p[:,1]>1.544))
  np.testing.assert_array_equal(a['face']['p'][m],b['face']['p'][m])
 def test_chin_moves_with_head_not_spine(self):
  d=a['face'];p=d['p']/10000;m=(p[:,2]>.098)&(p[:,1]>1.55)&(p[:,1]<1.582)
  w=np.where(d['j']==4,d['w'],0).sum(1)/255
  self.assertGreater(float(np.min(w[m])),.94)
 def test_normals_continuous_at_cervical_shared_positions(self):
  d=a['face'];p=d['p']/10000;m=p[:,1]<1.60;d=d[m];u,inv=np.unique(d['p'],axis=0,return_inverse=True)
  lo=np.full((len(u),3),1e9);hi=-lo.copy()
  np.minimum.at(lo,inv,d['n']);np.maximum.at(hi,inv,d['n'])
  self.assertLess(float(np.max(hi-lo)),2)
 def test_valid_weights_and_no_degenerate_cervical_triangles(self):
  d=a['face'];np.testing.assert_array_equal(d['w'].astype(int).sum(1),255)
  self.assertTrue(np.all(d['j']<49));v=(d['p']/10000).reshape(-1,3,3)
  area=np.linalg.norm(np.cross(v[:,1]-v[:,0],v[:,2]-v[:,0]),axis=1)
  m=v[:,:,1].max(1)<1.615
  self.assertGreater(float(area[m].min()),1e-9)
  self.assertLess(float(np.max(np.abs(np.linalg.norm(d['n']/32767,axis=1)-1))),.001)
 def test_unrelated_geometry_and_all_lods_budget(self):
  for name in ['skin','pants','eye','iris','pupil','hair','scalp','nails','rubber','sole','metal']:np.testing.assert_array_equal(a[name],b[name])
  self.assertLess(sum(len(v)//3 for v in a.values()),100000)
if __name__=='__main__':unittest.main()
