#!/usr/bin/env python3
"""Package sources, current assets and verification, with a verified manifest."""
from pathlib import Path
import zipfile,hashlib,json
R=Path(__file__).resolve().parents[1];target=Path('/mnt/data/distrito-cero-v0.13-codigo.zip')
exclude={'.ttf','.otf','.woff','.woff2','.pyc'}
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R)
 if any(s in ['.git','__pycache__','node_modules','clip-frames']for s in rel.parts)or p.suffix.lower()in exclude:continue
 if rel.parts[0]=='qa' and (len(rel.parts)<2 or rel.parts[1]!='v013'):continue
 if str(rel)=='SOURCE-MANIFEST.json':continue
 files.append(p)
manifest={'version':'0.13','html_sha256':hashlib.sha256((R/'index.html').read_bytes()).hexdigest(),'files':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest()for p in files},'excluded':'Prior QA folders, raw review video frames, caches, git and fonts. Historical builders and assets are labelled in README.'}
(R/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2))
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=8)as z:
 for p in [*files,R/'SOURCE-MANIFEST.json']:z.write(p,'distrito-cero/'+str(p.relative_to(R)))
with zipfile.ZipFile(target)as z:
 assert z.testzip()is None
 for rel,h in manifest['files'].items():assert hashlib.sha256(z.read('distrito-cero/'+rel)).hexdigest()==h,rel
 assert hashlib.sha256(z.read('distrito-cero/index.html')).hexdigest()==manifest['html_sha256']
print(json.dumps({'zip':str(target),'bytes':target.stat().st_size,'files':len(files)+1,'source_manifest_verified':True,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()},indent=2))
