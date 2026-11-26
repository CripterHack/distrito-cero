"""Native UV atlas preparation preserves canonical contracts and map meaning."""
from pathlib import Path
import base64, copy, hashlib, importlib.util, io, json, struct, tempfile, unittest
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'tools/prepare_native_face_atlas.py'
if TARGET.exists():
    spec=importlib.util.spec_from_file_location('native_atlas',TARGET)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
else: mod=None
ROW=struct.Struct('<6h2H8B')
def sha(data): return hashlib.sha256(data).hexdigest()
def fixture():
    rows=[ROW.pack(i,12000+i,2,0,32767,0,10,20,0,0,0,0,255,0,0,0) for i in range(6)]
    data={'bones':['bone'+str(i) for i in range(49)],'stride':24,'parts':[
        {'name':'face','vertices':6,'material':40,'data':base64.b64encode(b''.join(rows)).decode()},
        {'name':'jacket','vertices':3,'data':base64.b64encode(b''.join(rows[:3])).decode()}]}
    hero=('/* kept exactly */\nDC.HeroAsset='+json.dumps(data,separators=(',',':'))+';\n').encode()
    recipe={'schema':1,'mode':'cervical-color','sourceSha256':'a'*64,'normalScale':1,
        'nativeSource':{'heroAssetSha256':sha(hero),'faceCornerCount':6,'cornerOrder':'native-face-triangle-corners',
                        'sourceBaseColorMinEncoded':[180,130,90],'colorCoveragePolicy':'coverage-mask-full-white-is-valid-source'},
        'cornerUvs':[[.05,.05],[.45,.05],[.45,.45],[.55,.55],[.95,.55],[.95,.95]]}
    materials=("'use strict';(function(D){\n const maps={};\n const referenceSkin=Object.freeze([.44,.275,.185]);\n"
        " function tint(skin){return referenceSkin.map((v,i)=>Math.max(.12,Math.min(3.5,(Number.isFinite(skin?.[i])?skin[i]:v)/v)));}\n"
        " D.HumanMaterials=Object.freeze({...maps,referenceSkin,tint,source:'MakeHuman HM08 / Aksel Skin by Mindfront; CC0',version:1});\n})(DC);\n").encode()
    images={}
    for key,color in [('baseColor',(180,130,90)),('normal',(128,200,240)),('orm',(255,90,0)),('coverage',(255,255,255))]:
        out=io.BytesIO();Image.new('RGB',(8,8),color).save(out,format='PNG');images[key]=out.getvalue()
    return hero,materials,recipe,images
class NativeAtlas(unittest.TestCase):
    def setUp(self): self.assertIsNotNone(mod,'Missing native atlas preparation tool')
    def test_only_face_uv_bytes_change_and_source_is_recoverable(self):
        hero,materials,recipe,images=fixture();files,report=mod.prepare(hero,materials,recipe,images)
        old=json.loads(hero.decode().split('DC.HeroAsset=')[1].strip().rstrip(';'))
        new=json.loads(files['src/hero-asset.js'].decode().split('DC.HeroAsset=')[1].strip().rstrip(';'))
        self.assertEqual(old['bones'],new['bones']);self.assertEqual(old['parts'][1],new['parts'][1])
        a=base64.b64decode(old['parts'][0]['data']);b=base64.b64decode(new['parts'][0]['data'])
        for i in range(6):
            self.assertEqual(a[i*24:i*24+12],b[i*24:i*24+12]);self.assertEqual(a[i*24+16:i*24+24],b[i*24+16:i*24+24])
            uv=struct.unpack_from('<2H',b,i*24+12)
            self.assertEqual(uv,(round(recipe['cornerUvs'][i][0]*65535),round((1-recipe['cornerUvs'][i][1])*65535)))
        self.assertEqual(report['degenerateUvTriangles'],0)
        self.assertEqual(len(base64.b64decode(new['parts'][0]['lodClusterUV'])),12)
        seed=json.loads(files['assets/native-face-uv-source.json'])
        self.assertEqual(mod.restore_source(files['src/hero-asset.js'],seed),hero)
        repeated,_=mod.prepare(files['src/hero-asset.js'],files['src/human-materials.js'],recipe,images,seed)
        self.assertEqual(repeated,files)
    def test_hash_mode_normal_scale_corner_order_and_quantized_collapse_are_required(self):
        for key in ['hash','mode','normal','order','count','collapse','nan']:
            hero,materials,recipe,images=fixture()
            if key=='hash':recipe['nativeSource']['heroAssetSha256']='0'*64
            if key=='mode':recipe['mode']='plain'
            if key=='normal':recipe['normalScale']=.3
            if key=='order':recipe['nativeSource']['cornerOrder']='unknown'
            if key=='count':recipe['nativeSource']['faceCornerCount']=9
            if key=='collapse':recipe['cornerUvs'][:3]=[[.5,.5],[.5+1e-8,.5],[.5,.5+1e-8]]
            if key=='nan':recipe['cornerUvs'][0][0]=float('nan')
            with self.subTest(key=key),self.assertRaises(ValueError):mod.prepare(hero,materials,recipe,images)
    def test_srgb_filtering_is_linear_light_not_byte_average(self):
        pixels=np.array([[[0,0,0],[255,255,255]]],dtype=np.uint8)
        resized=mod.resize_albedo(pixels,1)
        self.assertTrue(np.all(np.abs(resized.astype(int)-188)<=1),resized)
    def test_lod_clusters_use_original_float32_uv_bins(self):
        pairs=[(65535,0),(32768,32767),(2048,65535),(10,20)]
        raw=b''.join(struct.pack('<2H',*p) for p in pairs)
        result=struct.unpack('<4H',mod.cluster_uv(raw))
        expected=tuple(int(np.floor(np.float32(u/65535)*32))+33*int(np.floor(np.float32(v/65535)*32)) for u,v in pairs)
        self.assertEqual(result,expected);self.assertTrue(all(0<=v<=1088 for v in result))
    def test_normal_resampling_flips_green_and_renormalizes_vectors(self):
        pixels=np.full((8,8,3),[128,200,240],dtype=np.uint8)
        encoded=mod.resize_normal(pixels,4);vectors=encoded.astype(float)/255*2-1
        self.assertTrue(np.all(vectors[:,:,1]<0));self.assertTrue(np.all(np.abs(np.linalg.norm(vectors,axis=2)-1)<.007))
        expected=np.array([128,55,240],float)/255*2-1;expected/=np.linalg.norm(expected)
        self.assertTrue(np.allclose(vectors,expected,atol=1/255+.00001))
    def test_unbaked_gutters_do_not_create_dark_downsampled_texels(self):
        hero,materials,recipe,images=fixture()
        pixels=np.zeros((32,32,3),dtype=np.uint8);pixels[12:20,12:20]=[180,130,90]
        source=io.BytesIO();Image.fromarray(pixels).save(source,format='PNG');images['baseColor']=source.getvalue()
        for key,color in [('normal',(128,128,255)),('orm',(255,90,0)),('coverage',(255,255,255))]:
            layer=np.zeros_like(pixels);layer[12:20,12:20]=color
            source=io.BytesIO();Image.fromarray(layer).save(source,format='PNG');images[key]=source.getvalue()
        files,report=mod.prepare(hero,materials,recipe,images)
        with Image.open(io.BytesIO(files['maps/albedo.webp'])) as image:
            self.assertTrue(np.all(np.asarray(image.convert('RGB'))==[180,130,90]))
        self.assertEqual(report['atlasPadding']['unbakedPixels'],32*32-8*8)
        self.assertTrue(report['atlasPadding']['preservedCoveredTexels'])
    def test_padding_preserves_covered_samples_and_uses_one_nearest_index_for_all_maps(self):
        native=fixture()[2]['nativeSource'];base=np.zeros((8,8,3),dtype=np.uint8)
        normal=np.zeros_like(base);orm=np.zeros_like(base)
        base[1,1]=[180,130,90];base[6,6]=[190,140,100]
        normal[1,1]=[10,20,30];normal[6,6]=[100,110,120]
        orm[1,1]=[1,2,3];orm[6,6]=[4,5,6]
        coverage=np.zeros_like(base);coverage[1,1]=255;coverage[6,6]=255
        original={'baseColor':base,'normal':normal,'orm':orm,'coverage':coverage}
        copies={key:value.copy() for key,value in original.items()}
        padded,report=mod.pad_unbaked(original,native)
        for key in ['baseColor','normal','orm']:
            np.testing.assert_array_equal(original[key],copies[key])
            np.testing.assert_array_equal(padded[key][[1,6],[1,6]],original[key][[1,6],[1,6]])
        for y in range(8):
            for x in range(8):
                i=0 if np.array_equal(padded['baseColor'][y,x],base[1,1]) else 1
                np.testing.assert_array_equal(padded['normal'][y,x],normal[1,1] if i==0 else normal[6,6])
                np.testing.assert_array_equal(padded['orm'][y,x],orm[1,1] if i==0 else orm[6,6])
        self.assertEqual(report['coveredPixels'],2)
    def test_missing_colored_partial_only_or_mismatched_coverage_is_rejected(self):
        native=fixture()[2]['nativeSource'];layers={key:np.ones((4,4,3),dtype=np.uint8)*50 for key in ['baseColor','normal','orm']}
        layers['coverage']=np.full((4,4,3),255,dtype=np.uint8)
        for kind in ['missing','colored','partial-only','size','policy']:
            bad={key:value.copy() for key,value in layers.items()};info=copy.deepcopy(native)
            if kind=='missing':bad.pop('coverage')
            if kind=='colored':bad['coverage'][0,0]=[255,0,255]
            if kind=='partial-only':bad['coverage'][:]=128
            if kind=='size':bad['coverage']=bad['coverage'][:3]
            if kind=='policy':info['colorCoveragePolicy']='unknown'
            with self.subTest(kind=kind),self.assertRaises(ValueError):mod.pad_unbaked(bad,info)
    def test_partial_gray_coverage_does_not_propagate_dark_fringe_colors(self):
        native=fixture()[2]['nativeSource'];layers={key:np.full((5,5,3),[9,4,2],dtype=np.uint8) for key in ['baseColor','normal','orm']}
        layers['coverage']=np.full((5,5,3),128,dtype=np.uint8);layers['coverage'][2,2]=255
        valid={'baseColor':[180,130,90],'normal':[128,128,255],'orm':[255,90,0]}
        for key,value in valid.items():layers[key][2,2]=value
        padded,report=mod.pad_unbaked(layers,native)
        for key,value in valid.items():np.testing.assert_array_equal(padded[key],np.broadcast_to(value,(5,5,3)))
        self.assertEqual(report['partialCoveragePixels'],24);self.assertEqual(report['coveredPixels'],1)
    def test_fully_covered_black_is_preserved_without_color_thresholds(self):
        native=fixture()[2]['nativeSource'];native['sourceBaseColorMinEncoded']=[0,0,0]
        layers={key:np.full((4,4,3),90,dtype=np.uint8) for key in ['baseColor','normal','orm']}
        layers['coverage']=np.full((4,4,3),255,dtype=np.uint8);layers['baseColor'][1,1]=0
        padded,report=mod.pad_unbaked(layers,native)
        np.testing.assert_array_equal(padded['baseColor'],layers['baseColor']);self.assertEqual(report['extendedPixels'],0)
    def test_coverage_png_cannot_round_partial_16_bit_or_transparent_samples_to_full(self):
        hero,materials,recipe,images=fixture()
        for kind in ['16-bit','alpha','rgb-tRNS','gray-tRNS']:
            stream=io.BytesIO()
            if kind=='16-bit':Image.fromarray(np.full((8,8),65534,dtype=np.uint16)).save(stream,format='PNG')
            elif kind=='rgb-tRNS':Image.new('RGB',(8,8),(255,255,255)).save(stream,format='PNG',transparency=(255,255,255))
            elif kind=='gray-tRNS':Image.new('L',(8,8),255).save(stream,format='PNG',transparency=255)
            else:Image.new('RGBA',(8,8),(255,255,255,128)).save(stream,format='PNG')
            images['coverage']=stream.getvalue()
            with self.subTest(kind=kind),self.assertRaises(ValueError):mod.prepare(hero,materials,recipe,images)
    def test_maps_are_lossless_correct_dimensions_and_orm_green_becomes_roughness(self):
        hero,materials,recipe,images=fixture();files,report=mod.prepare(hero,materials,recipe,images)
        for key,size in [('albedo',1024),('normal',512),('roughness',256)]:
            with Image.open(io.BytesIO(files['maps/'+key+'.webp'])) as image:
                self.assertEqual(image.size,(size,size));self.assertEqual(image.format,'WEBP')
                if key=='roughness':self.assertTrue(np.all(np.asarray(image.convert('RGB'))==90))
        self.assertEqual(report['estimatedGpuBytesRGBA8WithMipmaps'],7340028)
        code=files['src/human-materials.js'].decode()
        self.assertIn('version:2,atlas:Object.freeze(',code);self.assertIn('native-bottom-left',code)
        self.assertIn(materials.decode().split(' const referenceSkin=')[1].split(' D.HumanMaterials')[0],code)
    def test_seed_rejects_non_uv_changes_and_malformed_payload(self):
        hero,materials,recipe,images=fixture();files,_=mod.prepare(hero,materials,recipe,images);seed=json.loads(files['assets/native-face-uv-source.json'])
        data=json.loads(files['src/hero-asset.js'].decode().split('DC.HeroAsset=')[1].strip().rstrip(';'))
        raw=bytearray(base64.b64decode(data['parts'][0]['data']));raw[0]^=1;data['parts'][0]['data']=base64.b64encode(raw).decode()
        changed=('DC.HeroAsset='+json.dumps(data,separators=(',',':'))+';').encode()
        with self.assertRaises(ValueError):mod.restore_source(changed,seed)
        broken=copy.deepcopy(seed);broken['uvZlibBase64']='invalid'
        with self.assertRaises(ValueError):mod.restore_source(files['src/hero-asset.js'],broken)
    def test_compact_authored_replay_needs_no_original_bake_and_checks_hashes(self):
        hero,materials,recipe,images=fixture();files,_=mod.prepare(hero,materials,recipe,images)
        authored=json.loads(files['assets/native-face-atlas/source.json']);seed=json.loads(files['assets/native-face-uv-source.json'])
        maps={key:files['assets/native-face-atlas/'+key+'.webp'] for key in mod.SIZES}
        result=mod.replay_authored(files['src/hero-asset.js'],files['src/human-materials.js'],authored,seed,maps)
        for name,payload in result.items():self.assertEqual(payload,files[name])
        broken=copy.deepcopy(authored);broken['uv']['sha256']='0'*64
        with self.assertRaises(ValueError):mod.replay_authored(hero,materials,broken,seed,maps)
        broken_maps=dict(maps);broken_maps['normal']+=b'changed'
        with self.assertRaises(ValueError):mod.replay_authored(hero,materials,authored,seed,broken_maps)
if __name__=='__main__':unittest.main()
