#!/usr/bin/env python3
"""Package the verified standalone game, source and current GLB kit.
No runtime dependencies or font files are redistributed.
"""
from pathlib import Path
import hashlib,json,zipfile,shutil
R=Path(__file__).resolve().parents[1];D=R.parent.parent;Q=R/'qa/v08'
# Prefer the stable deliverable location used throughout this project.
D=Path('/mnt/data') if Path('/mnt/data').is_dir() else R/'dist'
D.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((Q/'release-report.json').read_text())
assert (Q/'final-suite.status').read_text().strip()=='0'
assert sha(R/'index.html')==report['build']['sha256'],'Build changed since testing'
assert (Q/'media-final.status').read_text().strip()=='0','Media review was not completed'
clip=json.loads((Q/'clip-report.json').read_text());assert not clip['errors']
for view in ['head','driver','pull','cast','police']:
 data=json.loads((Q/f'review-{view}.json').read_text());assert not data['errors'] and data['gl']==0
 if 'source_sha256' in data:assert data['source_sha256']==report['build']['sha256']
# Keep exploratory failures in the source package as diagnostics, but label them
# separately in VERIFICACION.md. Exclude only caches and optional historical QA images.
def include(p):
 rel=p.relative_to(R)
 return (p.is_file() and not any(x in ['.git','__pycache__','clip-frames','dist'] for x in rel.parts)
         and p.suffix.lower() not in {'.ttf','.otf','.woff','.woff2','.pyc','.mp4','.zip'}
         and rel.name not in {'SOURCE-MANIFEST.json','.DS_Store'})
items=sorted(p for p in R.rglob('*') if include(p))
manifest={'release':'v0.8 Presencia','html_sha256':report['build']['sha256'],
          'files':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p)} for p in items]}
(R/'SOURCE-MANIFEST.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
source=D/'distrito-cero-v0.8-codigo.zip'
with zipfile.ZipFile(source,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in items+[R/'SOURCE-MANIFEST.json']:z.write(p,Path('distrito-cero')/p.relative_to(R))
with zipfile.ZipFile(source) as z:
 assert z.testzip() is None
 for f in manifest['files']:
  b=z.read('distrito-cero/'+f['path']);assert hashlib.sha256(b).hexdigest()==f['sha256']
 assert z.read('distrito-cero/index.html')==(R/'index.html').read_bytes()
model_readme='''Distrito Cero v0.8 · modelos nativos de estudio\n\nEl humano tiene 17 huesos y cinco clips procedurales de reposo, caminar, correr, agacharse y sostener. La extracción de ocupantes, los objetivos de manos y el parpadeo del shader NO se exportan como clips. El kit del coche contiene carrocería, techo, cristales y ruedas. Las piezas extra de cabina y la simulación pertenecen al código del juego.\n\nSon recursos originales procedurales, no escaneos ni nueva geometría remota de Higgsfield. Se verificaron estructura y atributos, no compatibilidad certificada con todos los importadores. Estos archivos no son necesarios para jugar. No incluyen fuentes tipográficas.\n'''
models=D/'distrito-cero-v0.8-modelos-3d.zip'
with zipfile.ZipFile(models,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for p in sorted((R/'assets').glob('dc08-*.glb')):z.write(p,p.name)
 z.writestr('LEEME.txt',model_readme)
 z.write(R/'assets/presence-exports.json','modelos.json')
with zipfile.ZipFile(models) as z:assert z.testzip() is None
pairs={
 R/'index.html':D/'distrito-cero-v0.8-presencia.html',
 R/'docs/v08/VERIFICACION.md':D/'distrito-cero-v0.8-verificacion.md',
 Q/'review-driver.png':D/'distrito-cero-v0.8-vista-previa.png',
 Q/'review-head.png':D/'distrito-cero-v0.8-personaje.png',
 Q/'review-cast.png':D/'distrito-cero-v0.8-reparto.png'}
for src,dst in pairs.items():shutil.copy2(src,dst)
outputs=[source,models,*pairs.values(),D/'distrito-cero-v0.8-acceso.mp4']
assert all(p.is_file() and p.stat().st_size>0 for p in outputs)
shipping={'version':'v0.8 Presencia','files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':sha(p)} for p in outputs]}
(D/'distrito-cero-v0.8-entrega.json').write_text(json.dumps(shipping,indent=2)+'\n')
print(json.dumps(shipping,indent=2))
