"""Round-trip structural checks for the exported native glTF assets."""
from pathlib import Path
import json,struct,unittest,math
ROOT=Path(__file__).resolve().parents[1]
class Exports(unittest.TestCase):
 def read_asset(self,name):
  p=ROOT/'assets'/name
  self.assertTrue(p.is_file(),f'{name} missing')
  b=p.read_bytes();magic,version,length=struct.unpack_from('<4sII',b)
  self.assertEqual((magic,version,length),(b'glTF',2,len(b)))
  n,t=struct.unpack_from('<II',b,12);self.assertEqual(t,0x4e4f534a)
  d=json.loads(b[20:20+n]);self.assertEqual(d['asset']['version'],'2.0')
  bn,bt=struct.unpack_from('<II',b,20+n);self.assertEqual(bt,0x004e4942)
  self.assertEqual(bn,len(b)-28-n)
  self.assertFalse(any('uri' in v for v in d['buffers']))
  for v in d['bufferViews']:self.assertLessEqual(v.get('byteOffset',0)+v['byteLength'],bn)
  for mesh in d['meshes']:
   for p in mesh['primitives']:
    attrs=p['attributes'];self.assertIn('POSITION',attrs);self.assertIn('NORMAL',attrs)
    self.assertEqual(d['accessors'][attrs['POSITION']]['count'],d['accessors'][attrs['NORMAL']]['count'])
  raw=b[28+n:]
  def read(index):
   a=d['accessors'][index];v=d['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];code={5126:'f',5123:'H',5125:'I',5121:'B'}[a['componentType']];size=struct.calcsize(code)*count;offset=v.get('byteOffset',0)+a.get('byteOffset',0)
   return [struct.unpack_from('<'+code*count,raw,offset+j*size) for j in range(a['count'])]
  for m in d['meshes']:
   for p in m['primitives']:
    attrs=p['attributes'];count=d['accessors'][attrs['POSITION']]['count']
    self.assertTrue(all(0<=i[0]<count for i in read(p['indices'])))
    self.assertTrue(all(all(math.isfinite(v) for v in row) for row in read(attrs['POSITION'])))
    self.assertTrue(all(abs(math.sqrt(sum(v*v for v in row))-1)<.002 for row in read(attrs['NORMAL'])))
    if 'WEIGHTS_0' in attrs:
     self.assertTrue(all(sum(row)==255 for row in read(attrs['WEIGHTS_0'])))
     self.assertTrue(all(all(0<=v<17 for v in row) for row in read(attrs['JOINTS_0'])))
  for anim in d.get('animations',[]):
   for channel in anim['channels']:
    sample=anim['samplers'][channel['sampler']];times=read(sample['input']);self.assertTrue(all(a[0]<b[0] for a,b in zip(times,times[1:])))
    out=read(sample['output']);self.assertTrue(all(all(math.isfinite(v) for v in row) for row in out))
    self.assertTrue(all(abs(a-b)<.00001 for a,b in zip(out[0],out[-1])))
    if channel['target']['path']=='rotation':self.assertTrue(all(abs(sum(v*v for v in row)-1)<.00001 for row in out))
  return d,raw
 def test_hero(self):
  d,raw=self.read_asset('dc08-hero-native.glb');self.assertEqual(len(d['skins'][0]['joints']),17);self.assertEqual(len(d['meshes']),11)
  self.assertEqual(len(d['animations']),5)
  for m in d['meshes']:
   a=m['primitives'][0]['attributes'];self.assertIn('JOINTS_0',a);self.assertIn('WEIGHTS_0',a)
  for anim in d['animations']:
   self.assertEqual(len(anim['channels']),18)
   for s in anim['samplers']:self.assertEqual(d['accessors'][s['input']]['count'],d['accessors'][s['output']]['count'])
 def test_car(self):
  d,raw=self.read_asset('dc08-coupe-native.glb');self.assertGreaterEqual(len(d['meshes']),5);self.assertGreaterEqual(len(d['nodes']),13)
  self.assertTrue(any('wheel' in n.get('name','') for n in d['nodes']))
if __name__=='__main__':unittest.main()
