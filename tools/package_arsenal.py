#!/usr/bin/env python3
"""Package the audited source tree, including a hash manifest, without fonts/caches."""
from pathlib import Path
import hashlib, json, zipfile, shutil, sys
R=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else R.parent/'distrito-cero-v0.17-codigo.zip'
out=out.resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((R/'qa/v017/release-report.json').read_text())
assert sha(R/'index.html')==report['artifacts']['index.html']['sha256']
assert sha(R/'assets/dc017-equipment.glb')==report['artifacts']['assets/dc017-equipment.glb']['sha256']
for p,h in report['sourceHashes'].items():assert sha(R/p)==h, p+' changed since audit'
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or p.resolve()==out:continue
 if any(x in {'.git','node_modules','__pycache__'} for x in p.relative_to(R).parts):continue
 if p.name in {'SOURCE-MANIFEST.json','.DS_Store'} or p.suffix.lower() in {'.pyc','.pid','.ttf','.otf','.woff','.woff2'}:continue
 files.append(p)
manifest={'version':'0.17','htmlSha256':sha(R/'index.html'),'files':{p.relative_to(R).as_posix():sha(p) for p in files}}
(R/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
files.append(R/'SOURCE-MANIFEST.json')
out.parent.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6)as z:
 for p in files:z.write(p,'distrito-cero/'+p.relative_to(R).as_posix())
with zipfile.ZipFile(out)as z:
 for p,h in manifest['files'].items():assert hashlib.sha256(z.read('distrito-cero/'+p)).hexdigest()==h,p
 assert z.testzip() is None
print(json.dumps({'zip':str(out),'bytes':out.stat().st_size,'sha256':sha(out),'filesVerified':len(manifest['files']),'manifestIncluded':True},indent=2))
