"""Checks on distributed source bytes and quantized skin/scalp geometry, independent of authoring code."""
from pathlib import Path
import json,struct,base64,lzma,hashlib,unittest,io
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree
R=Path(__file__).resolve().parents[1]
text=(R/'src/hero-asset.js').read_text();D=json.loads(text.split('DC.HeroAsset=',1)[1].rstrip().rstrip(';'))
dtype=np.dtype([('pos','<i2',3),('normal','<i2',3),('uv','<u2',2),('joints','u1',4),('weights','u1',4)])
def part(name):
 a=next(p for p in D['parts'] if p['name']==name)
 return np.frombuffer(base64.b64decode(a['data']),dtype=dtype)
class Anatomy(unittest.TestCase):
 def test_immutable_cc0_transport_and_indices(self):
  raw=(R/'assets/anatomy-source/compact.bin').read_bytes();self.assertEqual(hashlib.sha256(raw).hexdigest(),'4bdcd196342f4ec13e3f616deffa7176ca59cee8fabc891d7339f9161c6ecccf')
  lengths=struct.unpack_from('<4I',raw);self.assertEqual(sum(lengths)+16,len(raw));b=lzma.decompress(raw[16:16+lengths[0]]);nv,nf=struct.unpack_from('<II',b);self.assertEqual((nv,nf),(2174,2106));ix=np.cumsum(np.frombuffer(b,dtype='<i2',offset=8+nv*6).astype(int));self.assertEqual(len(ix),nf*4);self.assertGreaterEqual(ix.min(),0);self.assertLess(ix.max(),nv)
 def test_anatomical_dimensions_and_neck_connection(self):
  a=part('face');p=a['pos']/10000.;self.assertAlmostEqual(p[:,1].min(),1.475,places=3);self.assertTrue(1.77<p[:,1].max()<1.80);self.assertTrue(.17<np.ptp(p[:,0])<.21)
  for low in [1.475,1.49,1.51,1.535]:self.assertGreater(np.sum((p[:,1]>=low-.006)&(p[:,1]<low+.021)),15)
  self.assertTrue(np.any(a['joints'][p[:,1]<1.53]==3));self.assertTrue(np.all(a['weights'].sum(1)==255))
 def test_uv_seam_and_normal_integrity(self):
  a=part('face');u=a['uv'].astype(float)/65535.;t=u.reshape(-1,3,2);self.assertLessEqual(np.max(np.ptp(t[:,:,0],axis=1)),.51)
  for d in D['parts']:
   a=part(d['name']);self.assertTrue(np.isfinite(a['pos']).all());self.assertTrue(np.allclose(np.linalg.norm(a['normal']/32767.,axis=1),1,atol=.001));self.assertLess(a['joints'].max(),49);self.assertTrue(np.all(a['weights'].sum(1)==255))
 def test_scalp_has_positive_clearance_against_actual_anatomy(self):
  h=np.unique(part('face')['pos'],axis=0)/10000.;h=h[h[:,1]>1.66];c=np.array([0,1.68,-.012]);v=h-c;r=np.linalg.norm(v,axis=1);tree=cKDTree(v/r[:,None]);p=np.unique(part('scalp')['pos'],axis=0)/10000.;v=p-c;pr=np.linalg.norm(v,axis=1);dist,ix=tree.query(v/pr[:,None],k=1);clearance=pr-r[ix]
  self.assertGreater(len(p),1500);self.assertGreater(float(clearance.min()),.0004)  # Four 0.1mm quantization steps, measured against nearest actual head sample.
  self.assertLess(float(clearance.max()),.04)
 def test_embedded_texture_budget_and_validity(self):
  s=(R/'src/human-materials.js').read_text();import re
  images=re.findall(r'data:image/webp;base64,([A-Za-z0-9+/=]+)',s);self.assertEqual(len(images),3)
  sizes=[]
  for b in images:
   im=Image.open(io.BytesIO(base64.b64decode(b)));im.load();sizes.append(im.size)
  self.assertEqual(sizes,[(512,512),(256,256),(128,128)])
  self.assertLess(sum(w*h*4*4/3 for w,h in sizes),2*1024*1024)
 def test_authoring_export_uses_expected_family(self):
  self.assertEqual(D['bones'][4],'head');self.assertIn('MakeHuman',D['provenance']);self.assertEqual(len(D['parts']),13);self.assertTrue(50000<sum(len(part(p['name']))//3 for p in D['parts'])<100000)
if __name__=='__main__':unittest.main()
