#!/usr/bin/env python3
"""Publish an audited source snapshot and standalone conversation artifacts."""
from pathlib import Path
import json,hashlib,zipfile,shutil
R=Path(__file__).resolve().parents[1];O=R/'qa/v014';out=Path('/mnt/data')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((O/'release-report.json').read_text())
assert sha(R/'index.html')==report['html']['sha256']
assert sha(R/'assets/dc014-human-cervical.glb')==report['glb']['sha256']
for p,h in report['sourceHashes'].items():assert sha(R/p)==h,p
files=[]
for p in sorted(R.rglob('*')):
 if not p.is_file() or any(s in {'.git','__pycache__','.pytest_cache'} for s in p.relative_to(R).parts):continue
 if p.name in ['SOURCE-MANIFEST.json','.DS_Store'] or p.suffix in ['.pyc','.pyo']:continue
 if p.suffix.lower() in ['.ttf','.otf','.woff','.woff2']:raise RuntimeError('Font distribution is not permitted: '+str(p))
 files.append(p)
manifest={'version':'0.14','htmlSha256':report['html']['sha256'],'files':{str(p.relative_to(R)):sha(p) for p in files}}
(R/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=False))
archive=out/'distrito-cero-v0.14-codigo.zip'
with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in [*files,R/'SOURCE-MANIFEST.json']:
  info=zipfile.ZipInfo('distrito-cero/'+str(p.relative_to(R)),date_time=(2026,9,14,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o644<<16
  z.writestr(info,p.read_bytes())
with zipfile.ZipFile(archive) as z:
 assert z.testzip() is None
 for name,h in manifest['files'].items():assert hashlib.sha256(z.read('distrito-cero/'+name)).hexdigest()==h,name
 assert z.read('distrito-cero/index.html')==(R/'index.html').read_bytes()
publish={
 'index.html':'distrito-cero-v0.14-equilibrio.html',
 'assets/dc014-human-cervical.glb':'distrito-cero-v0.14-personaje.glb',
 'docs/v014/VERIFICACION.md':'distrito-cero-v0.14-verificacion.md',
 'docs/v014/GUIA.md':'distrito-cero-v0.14-guia.md',
 'qa/v014/comparacion-cervical.jpg':'distrito-cero-v0.14-comparacion.jpg',
 'qa/v014/review-neck.png':'distrito-cero-v0.14-cuello.png',
 'qa/v014/review-cast.png':'distrito-cero-v0.14-reparto.png',
 'qa/v014/editor-cervical.png':'distrito-cero-v0.14-editor.png',
 'qa/v014/movilidad-cervical.mp4':'distrito-cero-v0.14-movilidad.mp4'}
for p,target in publish.items():shutil.copyfile(R/p,out/target)
result={'version':'0.14','source_files_verified':len(manifest['files']),'zip_integrity':'passed','artifacts':{n:{'bytes':(out/n).stat().st_size,'sha256':sha(out/n)} for n in [archive.name,*publish.values()]}}
(out/'distrito-cero-v0.14-entrega.json').write_text(json.dumps(result,indent=2,ensure_ascii=False));print(json.dumps(result,indent=2))
