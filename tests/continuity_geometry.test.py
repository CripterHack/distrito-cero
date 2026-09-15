"""Checks of actual quantized production data, independent of the authoring recipe."""
import unittest,json,base64
from pathlib import Path
import numpy as np
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'src/hero-asset.js').read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def get(n):return np.frombuffer(base64.b64decode(next(x for x in d['parts'] if x['name']==n)['data']),dtype=DT)
class Continuity(unittest.TestCase):
 def test_neck_reaches_torso_and_flares_into_base(self):
  p=get('face')['p']/1e4;self.assertAlmostEqual(float(p[:,1].min()),1.447,places=3)
  lower=p[p[:,1]<1.468];upper=p[(p[:,1]>1.488)&(p[:,1]<1.506)];self.assertGreater(np.ptp(lower[:,0]),np.ptp(upper[:,0])*1.15)
 def test_cervical_contour_has_no_inherited_lateral_spike(self):
  p=get('face')['p']/1e4;neck=p[(p[:,1]>1.515)&(p[:,1]<1.541)]
  self.assertLess(np.abs(neck[:,0]).max(),.059)
 def test_neck_root_is_anchored_to_chest_and_not_just_to_head(self):
  a=get('face');m=a['p'][:,1]<14750;self.assertTrue(np.any((a['j'][m]==2)&(a['w'][m]>80)))
 def test_no_neck_uv_stretch_across_cylindrical_seam(self):
  a=get('face');u=a['uv'].astype(float).reshape(-1,3,2)/65535;self.assertLess(np.ptp(u[:,:,0],axis=1).max(),.51)
 def test_hands_and_neck_normals_and_weights_are_unit(self):
  for n in ['jacket','face','skin','nails']:
   a=get(n);self.assertTrue(np.all(a['w'].sum(1)==255));self.assertTrue(np.allclose(np.linalg.norm(a['n']/32767,axis=1),1,atol=.001));self.assertLess(a['j'].max(),49)
 def test_nails_follow_actual_dorsal_skin_not_nominal_finger_radius(self):
  skin=get('skin')['p'].astype(float).reshape(-1,3,3)/1e4;nails=np.unique(get('nails')['p'],axis=0).astype(float)/1e4;clearance=[]
  for point in nails[::7]:
   sign=np.sign(point[0]);t=skin[np.sign(skin[:,:,0].mean(1))==sign];a=t[:,0,1:];u=t[:,1,1:]-a;v=t[:,2,1:]-a;q=point[1:]-a
   den=u[:,0]*v[:,1]-u[:,1]*v[:,0];ok=np.abs(den)>1e-12;d=np.where(ok,den,1)
   b=(q[:,0]*v[:,1]-q[:,1]*v[:,0])/d;c=(u[:,0]*q[:,1]-u[:,1]*q[:,0])/d;ok&=(b>=-1e-5)&(c>=-1e-5)&(b+c<=1.00001)
   if ok.any():
    x=t[:,0,0]+b*(t[:,1,0]-t[:,0,0])+c*(t[:,2,0]-t[:,0,0]);clearance.append(sign*point[0]-np.max(sign*x[ok]))
  self.assertGreater(len(clearance),30);self.assertGreater(min(clearance),-.00015);self.assertLess(max(clearance),.0009)
 def test_runtime_geometry_budget(self):self.assertLess(sum(p['vertices']//3 for p in d['parts']),100000)
if __name__=='__main__':unittest.main()
