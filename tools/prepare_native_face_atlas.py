#!/usr/bin/env python3
"""Prepare a native atlas preview without overwriting runtime or historical files.

Only uint16 UV bytes of the canonical face change. Lossless maps and immutable
source UV recovery data accompany the preview; applying it is a separate step.
"""
from pathlib import Path
import argparse
import base64
import hashlib
import io
import json
import math
import platform
import re
import struct
import zlib
import numpy as np
from PIL import Image, __version__ as PILLOW_VERSION

ROOT=Path(__file__).resolve().parents[1]
SIZES={'albedo':1024,'normal':512,'roughness':256}
ATLAS={'version':2,'normalScale':1,'uvConvention':'native-bottom-left',
       'material':'cervical-color','mapSizes':SIZES}

def sha(data): return hashlib.sha256(data).hexdigest()
def packed_json(value): return (json.dumps(value,indent=2,sort_keys=True)+'\n').encode()

def face_data(source):
    text=source.decode('utf-8')
    if text.count('DC.HeroAsset=')!=1: raise ValueError('Invalid canonical asset assignment')
    data=json.loads(text.split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
    if len(data.get('bones',[]))!=49 or data.get('stride')!=24:
        raise ValueError('Unsupported canonical rig or stride')
    faces=[p for p in data.get('parts',[]) if p.get('name')=='face']
    if len(faces)!=1: raise ValueError('Expected one canonical face')
    face=faces[0];count=face.get('vertices')
    if type(count) is not int or not 0<count<=1000000 or count%3:
        raise ValueError('Invalid canonical face corner count')
    raw=base64.b64decode(face['data'],validate=True)
    if len(raw)!=count*24 or face.get('material')!=40:
        raise ValueError('Unsupported canonical face data')
    if source.count(face['data'].encode())!=1:
        raise ValueError('Ambiguous face data assignment')
    return face,raw

def non_uv(raw):
    return b''.join(raw[i:i+12]+raw[i+16:i+24] for i in range(0,len(raw),24))

def replace_face(source,face,raw):
    return source.replace(face['data'].encode(),base64.b64encode(raw),1)

def cluster_uv(uv_bytes):
    pairs=np.frombuffer(uv_bytes,dtype='<u2').reshape(-1,2)
    decoded=(pairs.astype(np.float64)/65535).astype(np.float32)
    bins=np.floor(decoded.astype(np.float64)*32).astype(np.uint16)
    return (bins[:,0]+33*bins[:,1]).astype('<u2').tobytes()

def add_lod_metadata(source,face,old_raw):
    if 'lodClusterUV' in face: raise ValueError('Original face already has LOD cluster metadata')
    uv=b''.join(old_raw[i+12:i+16] for i in range(0,len(old_raw),24))
    current_face,_=face_data(source)
    token=b'"'+current_face['data'].encode()+b'"'
    return source.replace(token,token+b',"lodClusterUV":"'+base64.b64encode(cluster_uv(uv))+b'"',1)

def restore_source(current,seed):
    face,raw=face_data(current)
    if (seed.get('schema')!=1 or seed.get('part')!='face' or
        seed.get('recordStride')!=4 or seed.get('corners')!=face['vertices'] or
        sha(non_uv(raw))!=seed.get('nonUvSha256')):
        raise ValueError('Canonical non-UV attributes or seed contract changed')
    expected=face['vertices']*4
    try:
        decoder=zlib.decompressobj()
        uv=decoder.decompress(base64.b64decode(seed['uvZlibBase64'],validate=True),expected+1)
        if len(uv)!=expected or not decoder.eof or decoder.unused_data:
            raise ValueError('Invalid bounded original UV seed')
    except (KeyError,zlib.error,ValueError) as error:
        raise ValueError('Invalid original UV seed payload') from error
    original=bytearray(raw)
    for i in range(face['vertices']): original[i*24+12:i*24+16]=uv[i*4:i*4+4]
    result=replace_face(current,face,original)
    if 'lodClusterUV' in face:
        expected=base64.b64encode(cluster_uv(uv)).decode()
        if face['lodClusterUV']!=expected: raise ValueError('LOD cluster metadata differs from original UV bins')
        token=(',"lodClusterUV":"'+expected+'"').encode()
        if result.count(token)!=1: raise ValueError('Invalid LOD metadata placement')
        result=result.replace(token,b'',1)
    if sha(original)!=seed.get('faceSha256') or sha(result)!=seed.get('heroAssetSha256'):
        raise ValueError('Canonical source differs outside original UV seed')
    return result

def material_template(source):
    text=source.decode('utf-8')
    match=re.search(r'\bconst maps=(.*?)(;\n\s*const referenceSkin=)',text,re.S)
    if not match: raise ValueError('Unsupported HumanMaterials template')
    json.loads(match.group(1))
    prefix=text[:match.start(1)];suffix=text[match.end(1):]
    if ',version:2,atlas:Object.freeze(' in suffix:
        suffix,count=re.subn(r',version:2,atlas:Object\.freeze\(\{[^\n]*\}\)\}\);',',version:1});',suffix)
        if count!=1: raise ValueError('Invalid v2 HumanMaterials atlas declaration')
    if suffix.count(',version:1});')!=1:
        raise ValueError('Unsupported HumanMaterials version')
    return prefix,suffix

def resize_float(pixels,size):
    planes=[]
    for channel in range(pixels.shape[2]):
        image=Image.fromarray(pixels[:,:,channel].astype(np.float32))
        planes.append(np.asarray(image.resize((size,size),Image.Resampling.LANCZOS),dtype=np.float64))
    return np.stack(planes,axis=2)

def resize_albedo(pixels,size):
    srgb=pixels.astype(np.float64)/255
    linear=np.where(srgb<=.04045,srgb/12.92,((srgb+.055)/1.055)**2.4)
    linear=np.clip(resize_float(linear,size),0,1)
    encoded=np.where(linear<=.0031308,linear*12.92,1.055*linear**(1/2.4)-.055)
    return np.rint(np.clip(encoded,0,1)*255).astype(np.uint8)

def resize_normal(pixels,size):
    vectors=pixels.astype(np.float64)/255*2-1
    vectors[:,:,1]*=-1  # glTF top-left atlas back to native bottom-left UVs.
    vectors=resize_float(vectors,size)
    lengths=np.linalg.norm(vectors,axis=2,keepdims=True)
    if not np.isfinite(vectors).all() or np.any(lengths<1e-8):
        raise ValueError('Normal filtering produced undefined vectors')
    vectors/=lengths
    return np.rint(np.clip(vectors*.5+.5,0,1)*255).astype(np.uint8)

def resize_roughness(pixels,size):
    scalar=resize_float(pixels[:,:,1:2].astype(np.float64)/255,size)[:,:,0]
    return np.rint(np.clip(scalar,0,1)*255).astype(np.uint8)

def load_png(payload,coverage=False):
    if coverage and (len(payload)<26 or payload[:8]!=b'\x89PNG\r\n\x1a\n' or
                     payload[12:16]!=b'IHDR' or payload[24]!=8 or payload[25] not in (0,2)):
        raise ValueError('Coverage requires an opaque grayscale or RGB PNG with exact 8-bit samples')
    with Image.open(io.BytesIO(payload)) as image:
        if image.format!='PNG' or min(image.size)<1 or max(image.size)>8192:
            raise ValueError('Unsupported bounded bake image')
        if coverage and 'transparency' in image.info:
            raise ValueError('Coverage PNG must not contain transparent samples')
        return np.asarray(image.convert('RGB'))

def pad_unbaked(layers,native):
    """Extend fully covered bake samples into partial and uncovered atlas texels.

    The separate white-EMIT coverage bake determines validity, never map color.
    All maps use the same nearest sample; fully covered black remains untouched.
    """
    if native.get('colorCoveragePolicy')!='coverage-mask-full-white-is-valid-source':
        raise ValueError('Padding requires the explicit full-white coverage bake policy')
    if set(layers)!={'baseColor','normal','orm','coverage'}:
        raise ValueError('Padding requires three baked maps and an explicit coverage mask')
    shape=layers['baseColor'].shape
    if (len(shape)!=3 or shape[2]!=3 or min(shape[:2])<1 or
        any(v.dtype!=np.uint8 or v.shape!=shape for v in layers.values())):
        raise ValueError('Padding requires equal RGB8 bake dimensions')
    mask=layers['coverage']
    if np.any(mask[:,:,0]!=mask[:,:,1]) or np.any(mask[:,:,0]!=mask[:,:,2]):
        raise ValueError('Coverage mask must contain equal grayscale RGB samples')
    scalar=mask[:,:,0];coverage=scalar==255
    covered=int(coverage.sum());unbaked=int(np.count_nonzero(scalar==0))
    partial=int(np.count_nonzero((scalar>0)&(scalar<255)));extended=unbaked+partial
    if not covered:raise ValueError('Bake has no fully covered texels')
    material_layers={key:layers[key] for key in ['baseColor','normal','orm']}
    scipy_version=None
    if extended:
        # Authoring only. Compact authored replay never imports SciPy.
        from scipy import __version__ as scipy_version
        from scipy.ndimage import distance_transform_edt
        nearest=distance_transform_edt(~coverage,return_distances=False,return_indices=True)
        padded={key:value[tuple(nearest)] for key,value in material_layers.items()}
    else:padded={key:value.copy() for key,value in material_layers.items()}
    if any(not np.array_equal(padded[key][coverage],value[coverage]) for key,value in material_layers.items()):
        raise ValueError('Padding altered a covered texel')
    report={'policy':'nearest-fully-covered-texel-extension-before-resampling',
        'coveragePolicy':native['colorCoveragePolicy'],'sourceBaseColorMinEncoded':native.get('sourceBaseColorMinEncoded'),
        'width':shape[1],'height':shape[0],'coveredPixels':covered,'unbakedPixels':unbaked,
        'partialCoveragePixels':partial,'extendedPixels':extended,
        'preservedCoveredTexels':True,'sharedNearestIndicesForAllMaps':True,
        'algorithm':'scipy.ndimage.distance_transform_edt' if extended else 'all texels fully covered',
        'scipyVersion':scipy_version}
    return padded,report

def webp(pixels):
    stream=io.BytesIO()
    Image.fromarray(pixels).save(stream,format='WEBP',lossless=True,quality=100,method=6,exact=True)
    return stream.getvalue()

def gpu_bytes(size):
    total=0
    while size:
        total+=size*size*4;size//=2
    return total

def embed_maps(materials,payloads):
    prefix,suffix=material_template(materials);embedded={}
    for key,payload in payloads.items():
        embedded[key]={'width':SIZES[key],'height':SIZES[key],'colorSpace':'srgb' if key=='albedo' else 'linear',
                      'uri':'data:image/webp;base64,'+base64.b64encode(payload).decode()}
    atlas=json.dumps(ATLAS,separators=(',',':'))
    suffix=suffix.replace(',version:1});',',version:2,atlas:Object.freeze('+atlas+')});')
    return (prefix+json.dumps(embedded,separators=(',',':'))+suffix).encode()

def apply_uv_bytes(hero,uv_bytes):
    face,raw=face_data(hero);count=face['vertices']
    if len(uv_bytes)!=count*4: raise ValueError('Invalid authored UV byte count')
    pairs=list(struct.iter_unpack('<2H',uv_bytes))
    for i in range(0,count,3):
        a,b,c=pairs[i:i+3]
        if (b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1])==0:
            raise ValueError('Collapsed authored native UV triangle: '+str(i//3))
    new=bytearray(raw)
    for i in range(count):new[i*24+12:i*24+16]=uv_bytes[i*4:i*4+4]
    return add_lod_metadata(replace_face(hero,face,new),face,raw)

def replay_authored(hero,materials,authored,seed,payloads):
    if authored.get('schema')!=1 or authored.get('atlas')!=ATLAS:
        raise ValueError('Unsupported authored native atlas contract')
    if sha(packed_json(seed))!=authored.get('seedSha256'):
        raise ValueError('Authored UV recovery seed hash mismatch')
    hero=restore_source(hero,seed)
    native=authored.get('nativeSource',{})
    face,_=face_data(hero)
    if (sha(hero)!=native.get('heroAssetSha256') or native.get('faceCornerCount')!=face['vertices'] or
        native.get('cornerOrder')!='native-face-triangle-corners'):
        raise ValueError('Authored atlas source correspondence mismatch')
    prefix,suffix=material_template(materials)
    if sha((prefix+'<maps>'+suffix).encode())!=seed.get('materialsWrapperSha256'):
        raise ValueError('Authored HumanMaterials wrapper changed')
    uv=authored.get('uv',{});expected=face['vertices']*4
    if uv.get('recordStride')!=4 or uv.get('corners')!=face['vertices']:
        raise ValueError('Invalid authored UV record contract')
    try:
        decoder=zlib.decompressobj();raw=decoder.decompress(base64.b64decode(uv['zlibBase64'],validate=True),expected+1)
        if len(raw)!=expected or not decoder.eof or decoder.unused_data or sha(raw)!=uv.get('sha256'):
            raise ValueError('Invalid bounded authored UV payload')
    except (KeyError,zlib.error,ValueError) as error:raise ValueError('Invalid authored UV payload') from error
    for key,size in SIZES.items():
        payload=payloads[key]
        if sha(payload)!=authored.get('maps',{}).get(key,{}).get('sha256'):
            raise ValueError('Authored map hash mismatch: '+key)
        with Image.open(io.BytesIO(payload)) as image:
            if image.format!='WEBP' or image.size!=(size,size):
                raise ValueError('Invalid authored map dimensions or format: '+key)
    files={'src/hero-asset.js':apply_uv_bytes(hero,raw),
           'src/human-materials.js':embed_maps(materials,payloads),
           'assets/native-face-uv-source.json':packed_json(seed)}
    for name,data in files.items():
        if sha(data)!=authored.get('runtimeSha256',{}).get(name):
            raise ValueError('Authored output hash mismatch: '+name)
    return files

def prepare(hero,materials,recipe,images,seed=None):
    if recipe.get('schema')!=1 or recipe.get('mode')!='cervical-color' or recipe.get('normalScale')!=1:
        raise ValueError('Expected cervical-color recipe with baked normalScale 1')
    native=recipe.get('nativeSource',{})
    if native.get('cornerOrder')!='native-face-triangle-corners':
        raise ValueError('Native corner correspondence was not verified')
    prefix,suffix=material_template(materials)
    wrapper_sha=sha((prefix+'<maps>'+suffix).encode())
    if seed is not None:
        hero=restore_source(hero,seed)
        if seed.get('materialsWrapperSha256')!=wrapper_sha:
            raise ValueError('HumanMaterials tint/reference/template changed')
    if sha(hero)!=native.get('heroAssetSha256'):
        raise ValueError('Native source asset hash mismatch')
    face,raw=face_data(hero);count=face['vertices']
    if native.get('faceCornerCount')!=count:
        raise ValueError('Native face corner count mismatch')
    uv=recipe.get('cornerUvs')
    if not isinstance(uv,list) or len(uv)!=count:
        raise ValueError('Native UV recipe corner count mismatch')
    quantized=[]
    for row in uv:
        if (not isinstance(row,list) or len(row)!=2 or
            any(type(v) not in (int,float) or not math.isfinite(v) or not 0<=v<=1 for v in row)):
            raise ValueError('Invalid native UV coordinates')
        quantized.append((round(row[0]*65535),round((1-row[1])*65535)))
    for i in range(0,count,3):
        a,b,c=quantized[i:i+3]
        det=(b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1])
        if det==0: raise ValueError('Collapsed native UV triangle after uint16 quantization: '+str(i//3))
    if seed is None:
        old_uv=b''.join(raw[i+12:i+16] for i in range(0,len(raw),24))
        seed={'schema':1,'part':'face','recordStride':4,'corners':count,
              'heroAssetSha256':sha(hero),'faceSha256':sha(raw),'nonUvSha256':sha(non_uv(raw)),
              'humanMaterialsSha256':sha(materials),'materialsWrapperSha256':wrapper_sha,
              'uvZlibBase64':base64.b64encode(zlib.compress(old_uv,9)).decode()}
    new=bytearray(raw)
    for i,pair in enumerate(quantized): struct.pack_into('<2H',new,i*24+12,*pair)
    if non_uv(new)!=non_uv(raw): raise ValueError('Unexpected non-UV asset change')
    layers,padding=pad_unbaked({key:load_png(images[key],coverage=key=='coverage') for key in ['baseColor','normal','orm','coverage']},native)
    maps={
        'albedo':resize_albedo(layers['baseColor'],SIZES['albedo']),
        'normal':resize_normal(layers['normal'],SIZES['normal']),
        'roughness':resize_roughness(layers['orm'],SIZES['roughness'])}
    files={'src/hero-asset.js':add_lod_metadata(replace_face(hero,face,new),face,raw),
           'assets/native-face-uv-source.json':packed_json(seed)}
    payloads={}
    for key,pixels in maps.items():
        payload=webp(pixels);files['maps/'+key+'.webp']=payload;payloads[key]=payload
    files['src/human-materials.js']=embed_maps(materials,payloads)
    uv_bytes=b''.join(struct.pack('<2H',*pair) for pair in quantized)
    authored={'schema':1,'atlas':ATLAS,'nativeSource':native,'seedSha256':sha(packed_json(seed)),
        'uv':{'recordStride':4,'corners':count,'sha256':sha(uv_bytes),'zlibBase64':base64.b64encode(zlib.compress(uv_bytes,9)).decode()},
        'maps':{key:{'file':key+'.webp','sha256':sha(payloads[key])} for key in SIZES},
        'runtimeSha256':{name:sha(value) for name,value in files.items() if name.startswith(('src/','assets/'))},
        'bakeProvenance':{'recipeCanonicalSha256':sha(json.dumps(recipe,separators=(',',':'),sort_keys=True).encode()),
            'sourceGlbSha256':recipe.get('sourceSha256'),'sourceImageSha256':{key:sha(value) for key,value in images.items()},
            'toolchain':recipe.get('toolchain'),'atlasPadding':padding}}
    for key,payload in payloads.items():files['assets/native-face-atlas/'+key+'.webp']=payload
    files['assets/native-face-atlas/source.json']=packed_json(authored)
    report={'schema':1,'status':'prepared-not-applied','sourceHeroAssetSha256':sha(hero),
        'sourceHumanMaterialsSha256':seed['humanMaterialsSha256'],'sourceFaceSha256':sha(raw),
        'recipeCanonicalSha256':sha(json.dumps(recipe,separators=(',',':'),sort_keys=True).encode()),
        'sourceImageSha256':{key:sha(value) for key,value in images.items()},
        'corners':count,'triangles':count//3,'degenerateUvTriangles':0,
        'changedUvCorners':sum(raw[i+12:i+16]!=new[i+12:i+16] for i in range(0,len(raw),24)),
        'preserved':'Every non-UV face byte, all other parts, rig, topology and original asset metadata; face.lodClusterUV added from original UV bins',
        'atlas':ATLAS,'atlasPadding':padding,'estimatedGpuBytesRGBA8WithMipmaps':sum(gpu_bytes(s) for s in SIZES.values()),
        'gpuBudgetAssumption':'RGBA8 storage and complete mip chains; excludes drivers, other materials and duplicate context resources',
        'toolchain':{'python':platform.python_version(),'numpy':np.__version__,'pillow':PILLOW_VERSION,'toolSha256':sha(Path(__file__).read_bytes())},
        'outputs':{name:{'bytes':len(value),'sha256':sha(value)} for name,value in files.items()},
        'limitations':['Preview only; shader, exporter, build and visual/runtime tests must change atomically before acceptance.',
                       'Normal PNG decoder uses RGB8 samples; output normal vectors are linearly filtered and normalized.']}
    files['native-atlas-manifest.json']=packed_json(report)
    return files,report

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--recipe',type=Path)
    inputs.add_argument('--authored',type=Path,help='Compact authored atlas directory or source.json; no original PNG/Blender dependency')
    parser.add_argument('--source',type=Path,default=ROOT/'src/hero-asset.js')
    parser.add_argument('--materials',type=Path,default=ROOT/'src/human-materials.js')
    parser.add_argument('--seed',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    input_path=(args.recipe or args.authored).resolve()
    if input_path.is_dir():input_path=input_path/'source.json'
    input_bytes=input_path.read_bytes();document=json.loads(input_bytes)
    output=(args.output or (ROOT if args.authored and args.check else ROOT/'artifacts/native-face-atlas')).resolve()
    if not args.check and not output.is_relative_to(ROOT/'artifacts'):
        raise ValueError('Use an artifacts-only preview output inside this repository')
    if output.exists() and not args.check: raise ValueError('Output directory already exists')
    if args.check and not output.is_dir(): raise ValueError('Missing output directory to check')
    source_bytes=args.source.read_bytes();materials_bytes=args.materials.read_bytes()
    seed_path=args.seed or (ROOT/'assets/native-face-uv-source.json')
    seed_bytes=seed_path.read_bytes() if seed_path.exists() else None
    images={};image_paths={}
    for key in (SIZES if args.authored else ['baseColor','normal','orm','coverage']):
        name=document.get('maps',{}).get(key,{}).get('file') if args.authored else document.get('images',{}).get(key)
        if not isinstance(name,str): raise ValueError('Missing recipe image path')
        path=(input_path.parent/name).resolve()
        if not path.is_relative_to(input_path.parent): raise ValueError('Recipe image escapes bake directory')
        image_paths[key]=path;images[key]=path.read_bytes()
    if args.authored:
        if seed_bytes is None:raise ValueError('Authored replay requires the original UV recovery seed')
        files=replay_authored(source_bytes,materials_bytes,document,json.loads(seed_bytes),images)
        report={'status':'authored-replay','corners':document['uv']['corners'],'triangles':document['uv']['corners']//3,
            'degenerateUvTriangles':0,'changedUvCorners':'recorded in original preparation','estimatedGpuBytesRGBA8WithMipmaps':sum(gpu_bytes(s) for s in SIZES.values())}
    else:files,report=prepare(source_bytes,materials_bytes,document,images,json.loads(seed_bytes) if seed_bytes else None)
    if (args.source.read_bytes()!=source_bytes or args.materials.read_bytes()!=materials_bytes or input_path.read_bytes()!=input_bytes or
        any(image_paths[key].read_bytes()!=images[key] for key in images) or (seed_bytes is not None and seed_path.read_bytes()!=seed_bytes)):
        raise ValueError('Inputs changed during native atlas preparation')
    if args.check:
        for name,data in files.items():
            if not (output/name).is_file() or (output/name).read_bytes()!=data:
                raise ValueError('Prepared output differs: '+name)
    else:
        output.mkdir(parents=True,exist_ok=False)
        for name,data in files.items():
            target=output/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    print(json.dumps({key:report[key] for key in ['status','corners','triangles','degenerateUvTriangles','changedUvCorners','estimatedGpuBytesRGBA8WithMipmaps']}))

if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,OSError) as error: raise SystemExit(str(error))
