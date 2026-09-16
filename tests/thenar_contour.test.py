"""Canonical thenar authoring: bounded shape, correct normals, immutable contracts."""
from pathlib import Path
import base64,hashlib,importlib.util,json,math,struct,unittest,zlib
R=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('thenar',R/'tools/refine_thenar.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class ThenarContour(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=(R/'src/hero-asset.js').read_bytes();cls.header=cls.source.decode().split('DC.HeroAsset=',1)[0]
        cls.data=json.loads(cls.source.decode().split('DC.HeroAsset=',1)[1].strip().rstrip(';'));cls.seed=json.loads((R/'assets/thenar-contour-source.json').read_text())
        cls.part=next(p for p in cls.data['parts']if p['name']=='skin');cls.raw=base64.b64decode(cls.part['data']);cls.base=bytearray(cls.raw)
        records=zlib.decompress(base64.b64decode(cls.seed['recordsZlibBase64']));cls.indices=set()
        for i in range(0,len(records),28):
            index=struct.unpack_from('<I',records,i)[0];cls.indices.add(index);cls.base[index*24:(index+1)*24]=records[i+4:i+28]
    def source_of(self,data):return (self.header+'DC.HeroAsset='+json.dumps(data,separators=(',',':'))+';\n').encode()
    def test_recovers_original_input_and_reproduces_exact_output(self):
        self.assertEqual(hashlib.sha256(self.base).hexdigest(),self.seed['partSha256'])
        d=json.loads(json.dumps(self.data));next(p for p in d['parts']if p['name']=='skin')['data']=base64.b64encode(self.base).decode();d.pop('thenarContour',None)
        self.assertEqual(mod.refine(self.source_of(d))[0],self.source)
        self.assertEqual(mod.refine(self.source)[0],self.source)
    def test_only_positions_and_normals_in_seed_corners_change(self):
        for i,(a,b)in enumerate(zip(mod.ROW.iter_unpack(self.base),mod.ROW.iter_unpack(self.raw))):
            self.assertEqual(a[6:],b[6:],'UV/weights are not a shape corrective')
            self.assertEqual(a[1:3],b[1:3]);self.assertLessEqual(abs(a[0]-b[0]),40)
            if i not in self.indices:self.assertEqual(a,b)
        self.assertEqual(len(self.data['bones']),49)
    def test_mirrored_map_does_not_move_wrist_nails_dorsal_hand_or_face(self):
        for p in [[.2507,.836,0],[.25,.90,.02],[.24,.798,.055],[.28,.85,.02],[0,1.65,0],[.1,1.3,0]]:
            self.assertEqual(mod.deform(p,[1.,0.,0.])[0],p)
        for y in [.825,.84,.85,.875]:
            for z in[-.005,.005,.02,.045]:
                a,_=mod.deform([.245,y,z],[1.,0.,0.]);b,_=mod.deform([-.245,y,z],[-1.,0.,0.]);self.assertAlmostEqual(a[0],-b[0],12)
    def test_jacobian_is_positive_and_normals_are_covariant(self):
        for x in [.241,.249,.256,.269]:
            p=[x,.844,.016];normal=[.5,.6,.7];length=math.sqrt(sum(v*v for v in normal));normal=[v/length for v in normal]
            q,n=mod.deform(p,normal);f,(dx,dy,dz),side=mod.field(p);self.assertGreaterEqual(1+side*dx,.538)
            tangent=[-normal[1],normal[0],0];eps=1e-7
            r,_=mod.deform([p[i]+eps*tangent[i]for i in range(3)],normal)
            self.assertAlmostEqual(sum(n[i]*(r[i]-q[i])/eps for i in range(3)),0,places=4)
            self.assertAlmostEqual(sum(v*v for v in n),1,places=10)
    def test_seams_keep_identical_positions_and_existing_duplicate_counts(self):
        mapping={}
        for a,b in zip(mod.ROW.iter_unpack(self.base),mod.ROW.iter_unpack(self.raw)):
            if a[:3]in mapping:self.assertEqual(mapping[a[:3]],b[:3])
            else:mapping[a[:3]]=b[:3]
        self.assertEqual(len(set(mapping.values())),len(mapping),'Quantization must not merge distinct skin vertices')
    def test_other_material_parts_and_metadata_are_preserved(self):
        out,_=mod.refine(self.source);d=json.loads(out.decode().split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
        for a,b in zip(self.data['parts'],d['parts']):self.assertEqual(a,b)
        self.assertEqual(self.data['bones'],d['bones'])
    def test_seed_rejects_truncation_duplicates_and_unknown_vertex_edits(self):
        bad=dict(self.seed);bad['recordCount']+=1
        with self.assertRaisesRegex(ValueError,'payload'):mod.refine(self.source,bad)
        bad=dict(self.seed);records=bytearray(zlib.decompress(base64.b64decode(bad['recordsZlibBase64'])));records[28:32]=records[:4];bad['recordsZlibBase64']=base64.b64encode(zlib.compress(records)).decode()
        with self.assertRaisesRegex(ValueError,'repeated'):mod.refine(self.source,bad)
        d=json.loads(json.dumps(self.data));p=next(p for p in d['parts']if p['name']=='skin');raw=bytearray(self.raw);raw[0]^=1;p['data']=base64.b64encode(raw).decode()
        with self.assertRaisesRegex(ValueError,'outside'):mod.refine(self.source_of(d))
    def test_conflicting_author_weights_are_not_silently_overwritten(self):
        d=json.loads(json.dumps(self.data));p=next(p for p in d['parts']if p['name']=='skin');raw=bytearray(self.raw);i=min(self.indices);raw[i*24+20]^=1;p['data']=base64.b64encode(raw).decode()
        with self.assertRaisesRegex(ValueError,'Conflicting'):mod.refine(self.source_of(d))
if __name__=='__main__':unittest.main()
