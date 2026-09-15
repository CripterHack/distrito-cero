from pathlib import Path
import json,struct,unittest,math
R=Path(__file__).resolve().parents[1]
class ArsenalExport(unittest.TestCase):
 def test_original_kit_matches_exported_node_catalogue(self):
  data=(R/'assets/dc017-equipment.glb').read_bytes();magic,version,size=struct.unpack_from('<4sII',data);self.assertEqual((magic,version,size),(b'glTF',2,len(data)));n,tag=struct.unpack_from('<I4s',data,12);self.assertEqual(tag,b'JSON');g=json.loads(data[20:20+n]);blen,btag=struct.unpack_from('<I4s',data,20+n);self.assertEqual(btag,b'BIN\0');raw=data[28+n:];self.assertEqual(len(raw),blen)
  roots=g['scenes'][0]['nodes'];self.assertEqual(len(roots),13);names={g['nodes'][i]['name']for i in roots};self.assertTrue({'gauss','emp','binoculars'}<=names)
  for m in g['meshes']:
   for p in m['primitives']:
    ac=g['accessors'][p['attributes']['POSITION']];self.assertEqual(ac['count']%3,0);view=g['bufferViews'][ac['bufferView']];self.assertLessEqual(view['byteOffset']+view['byteLength'],blen)
    vals=struct.unpack_from('<'+'f'*(view['byteLength']//4),raw,view['byteOffset']);self.assertTrue(all(math.isfinite(v)for v in vals));self.assertTrue(all(abs(math.sqrt(sum(vals[k+j]**2 for j in [3,4,5]))-1)<1e-5 for k in range(0,len(vals),8)))
  self.assertEqual(g['asset']['version'],'2.0');self.assertFalse(g.get('extensionsRequired'))
if __name__=='__main__':unittest.main()
