"""Authoring invariants, including the trouser/cuff semantic boundary."""
from pathlib import Path
import base64, hashlib, importlib.util, json, unittest
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('rebind',R/'tools/rebind_garment.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class GarmentBinding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(R/'src/hero-asset.js').read_bytes();cls.data=json.loads(cls.source.decode().split('DC.HeroAsset=',1)[1].strip().rstrip(';'));cls.result,cls.report=mod.rebind(cls.source)
        cls.output=json.loads(cls.result.decode().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
    def test_rebinding_is_reproducible_without_baseline_geometry_duplicate(self):
        self.assertEqual(self.source,self.result)
    def test_geometry_uv_normals_counts_and_bone_contract_unchanged(self):
        self.assertEqual(self.data['bones'],self.output['bones'])
        for a,b in zip(self.data['parts'],self.output['parts']):
            va,vb=mod.unpack(a),mod.unpack(b)
            self.assertEqual([x[:8] for x in va],[x[:8] for x in vb],a['name'])
            self.assertEqual(a['vertices'],b['vertices'])
    def test_only_garment_and_cuff_binding_can_change(self):
        seeds=json.loads((R/'assets/garment-binding-source.json').read_text())
        for part in self.output['parts']:
            if part['name'] not in seeds['parts']: continue
            raw=mod.zlib.decompress(base64.b64decode(seeds['parts'][part['name']]['weightsZlibBase64']))
            for i,row in enumerate(mod.unpack(part)):
                self.assertEqual(sum(row[12:16]),255)
                if part['name']=='pants':
                    old=tuple(raw[i*8:i*8+8]);x,y,z=[v/1e4 for v in row[:3]]
                    cuff=.865<y<.935 and abs(x)>.195 and any(mod.arm(self.data['bones'][j]) and w for j,w in zip(old[:4],old[4:]))
                    if not cuff: self.assertEqual(row[8:],old,'Do not bind a trouser hip to an upper arm')
    def test_authoring_rejects_changed_geometry_instead_of_guessing(self):
        d=json.loads(json.dumps(self.data));part=d['parts'][0];b=bytearray(base64.b64decode(part['data']));b[0]^=1;part['data']=base64.b64encode(b).decode()
        with self.assertRaisesRegex(ValueError,'geometry/UV/normal changed'):mod.rebind(('DC.HeroAsset='+json.dumps(d)+';').encode())
    def test_unrelated_parts_are_not_reencoded(self):
        for a,b in zip(self.data['parts'],self.output['parts']):
            if a['name'] not in ('jacket','pants'): self.assertEqual(a,b)
if __name__=='__main__':unittest.main()
