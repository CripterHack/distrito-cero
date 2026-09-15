"""Acceptance checks on quantized shipped geometry, independent of the authoring generator."""
import unittest,base64,json,subprocess
from pathlib import Path
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'src/hero-asset.js').read_text().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
def get(n):return np.frombuffer(base64.b64decode(next(x for x in d['parts'] if x['name']==n)['data']),dtype=DT)
class Constitution(unittest.TestCase):
 def test_rig_and_asset_share_the_full_definition(self):
  js="const fs=require('fs'),vm=require('vm');for(const n of ['core','character-motion','skin-rig'])vm.runInThisContext(fs.readFileSync('src/'+n+'.js','utf8'));console.log(JSON.stringify(DC.SkinRig.bones.map(x=>x[0])));"
  names=json.loads(subprocess.check_output(['node','-e',js],cwd=R));self.assertEqual(names,d['bones']);self.assertEqual(len(names),49)
 def test_each_hand_is_a_single_connected_surface(self):
  a=get('skin');v,ix=np.unique(a['p'],axis=0,return_inverse=True);tri=ix.reshape(-1,3);edges=np.vstack((tri[:,[0,1]],tri[:,[1,2]],tri[:,[2,0]]));graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(v),len(v))).tocsr();nc,lab=connected_components(graph,directed=False)
  self.assertEqual(nc,2,'palms, webbing and digits must be connected, not floating finger pieces');self.assertGreater(len(v),2400)
 def test_hand_vertices_use_all_thirty_digit_bones(self):
  a=get('skin');active=set(a['j'][a['w']>0].tolist())
  for k in ['L','R']:
   for f in ['thumb','index','middle','ring','little']:
    for j in range(3):self.assertIn(d['bones'].index(f+str(j)+k),active)
 def test_shoulder_silhouette_is_fitted_not_padded(self):
  p=get('jacket')['p']/1e4;q=p[(p[:,1]>1.395)&(p[:,1]<1.44)];self.assertTrue(.46<np.ptp(q[:,0])<.56,np.ptp(q[:,0]))
 def test_hands_have_wrist_overlap_and_adult_length(self):
  p=get('skin')['p']/1e4;q=p[p[:,0]>0];self.assertTrue(.700<q[:,1].min()<.740);self.assertTrue(.887<q[:,1].max()<.915);self.assertTrue(.16<np.ptp(q[:,1])<.22)
 def test_fitted_flat_outsoles_and_distinct_nails(self):
  self.assertIn('nails',[p['name'] for p in d['parts']]);a=get('sole')['p']/1e4;self.assertGreaterEqual(a[:,1].min(),.008);self.assertLess(np.ptp(a[:,2]),.29);self.assertGreater(np.sum(np.abs(a[:,1]-.015)<.001),20)
 def test_all_quantized_vertices_are_valid_with_bounded_budget(self):
  count=0
  for part in d['parts']:
   a=get(part['name']);count+=len(a)//3;self.assertTrue(np.all(a['w'].sum(1)==255));self.assertLess(a['j'].max(),49);self.assertTrue(np.allclose(np.linalg.norm(a['n']/32767,axis=1),1,atol=.001))
  self.assertLess(count,100000);self.assertGreater(count,40000)
if __name__=='__main__':unittest.main()
