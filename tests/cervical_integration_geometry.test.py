"""v0.15 measured art constraints, not anthropometric population assertions."""
import base64,json,unittest
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def parts(path):
 d=json.loads(path.read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
 return {p['name']:np.frombuffer(base64.b64decode(p['data']),DT) for p in d['parts']}
a=parts(R/'src/hero-asset.js');b=parts(R/'assets/hero-v014-baseline.js')
class Integration(unittest.TestCase):
 def test_mid_neck_has_mass_relative_to_existing_head(self):
  v=a['face']['p']/1e4;neck=v[(v[:,1]>1.504)&(v[:,1]<1.536)];head=v[(v[:,1]>1.633)&(v[:,1]<1.695)]
  ratio=np.ptp(neck[:,0])/np.ptp(head[:,0]);self.assertGreater(ratio,.62);self.assertLess(ratio,.80)
  self.assertGreater(np.ptp(neck[:,2]),.112);self.assertLess(np.ptp(neck[:,2]),.148)
 def test_lower_lateral_neck_is_not_a_stalk(self):
  v=a['face']['p']/1e4;mid=v[(v[:,1]>1.512)&(v[:,1]<1.527)]
  self.assertGreater(np.ptp(mid[:,0]),.12);self.assertLess(np.ptp(mid[:,0]),.14)
 def test_no_ring_nodule_from_base_to_upper_neck(self):
  v=a['face']['p']/1e4;widths=[]
  for y in np.arange(1.480,1.581,.008):
   q=v[(abs(v[:,1]-y)<.0045)&(v[:,2]<.044)]
   self.assertGreater(len(q),10);widths.append(float(np.ptp(q[:,0])))
  self.assertLess(np.max(np.abs(np.diff(widths))),.013)
 def test_posterior_contour_recedes_toward_skull_without_a_new_hump(self):
  triangles=(a['face']['p']/1e4).reshape(-1,3,3)
  def section(height):
   points=[]
   for i,j in [(0,1),(1,2),(2,0)]:
    lo=triangles[:,i];hi=triangles[:,j];dy=hi[:,1]-lo[:,1]
    valid=(abs(dy)>1e-9)&((lo[:,1]-height)*(hi[:,1]-height)<=0)
    u=(height-lo[valid,1])/dy[valid];points.extend(lo[valid]+u[:,None]*(hi[valid]-lo[valid]))
   return np.array(points)
  lower=section(1.500);upper=section(1.553)
  lower=lower[(abs(lower[:,0])<.016)&(lower[:,2]<0)]
  upper=upper[(abs(upper[:,0])<.016)&(upper[:,2]<0)]
  self.assertGreater(len(lower),3);self.assertGreater(len(upper),3)
  self.assertGreater(float(upper[:,2].min()-lower[:,2].min()),.004)
 def test_no_lateral_bulge_below_ear_after_increasing_mass(self):
  t=(a['face']['p']/1e4).reshape(-1,3,3);widths=[]
  for height in np.linspace(1.544,1.600,15):
   points=[]
   for i,j in [(0,1),(1,2),(2,0)]:
    lo=t[:,i];hi=t[:,j];dy=hi[:,1]-lo[:,1]
    valid=(abs(dy)>1e-9)&((lo[:,1]-height)*(hi[:,1]-height)<=0)
    u=(height-lo[valid,1])/dy[valid];points.extend(lo[valid]+u[:,None]*(hi[valid]-lo[valid]))
   points=np.array(points);widths.append(float(np.max(abs(points[:,0]))))
  self.assertLess(max(widths)-max(widths[0],widths[-1]),.0015)
 def test_eyes_mouth_ears_hair_hands_lower_body_preserved(self):
  old=b['face']['p']/1e4;m=(old[:,1]>1.625)|((old[:,2]>.098)&(old[:,1]>1.55))
  np.testing.assert_array_equal(a['face']['p'][m],b['face']['p'][m])
  for name in ['skin','eye','iris','pupil','pants','rubber','sole','nails','hair','scalp']:
   np.testing.assert_array_equal(a[name],b[name])
 def test_same_topology_and_valid_skinned_data(self):
  for k,d in a.items():
   self.assertEqual(len(d),len(b[k]));self.assertTrue(np.all(d['w'].astype(int).sum(1)==255));self.assertTrue(np.all(d['j']<49))
   self.assertTrue(np.allclose(np.linalg.norm(d['n']/32767,axis=1),1,atol=.001))
  self.assertLess(sum(len(d)//3 for d in a.values()),100000)
 def test_neck_surface_weld_and_facial_weights(self):
  d=a['face'];v=d['p']/1e4;m=v[:,1]<1.60;u,inv=np.unique(d['p'][m],axis=0,return_inverse=True)
  lo=np.full((len(u),3),1e9);hi=-lo.copy();np.minimum.at(lo,inv,d['n'][m]);np.maximum.at(hi,inv,d['n'][m]);self.assertLess(float(np.max(hi-lo)),2)
  chin=(v[:,2]>.098)&(v[:,1]>1.55)&(v[:,1]<1.582);w=np.where(d['j']==4,d['w'],0).sum(1)/255;self.assertGreater(w[chin].min(),.94)
  unique,inv=np.unique(d['p'],axis=0,return_inverse=True);f=inv.reshape(-1,3)
  e=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);e.sort(axis=1);e,c=np.unique(e,axis=0,return_counts=True);v=unique[e[c==1]]/1e4
  self.assertEqual(int(((v[:,:,1].min(1)>1.46)&(v[:,:,1].max(1)<1.60)).sum()),0)
if __name__=='__main__':unittest.main()
