"""Read-only source / asset verification for the v0.10 delivery."""
from pathlib import Path
import hashlib,json,subprocess,platform,importlib.metadata
import numpy as np
import trimesh
R=Path(__file__).resolve().parents[1];O=R/'qa/v010';O.mkdir(parents=True,exist_ok=True)
behavior=['core','world','police','simulation','dynamics','interactions','frontier-world','frontier-simulation','frontier-renderer','frontier-ui','occupancy','character-motion','audio','app','human-materials']
baseline=json.loads((R/'docs/v010/BASELINE-SOURCE-MANIFEST-v09.json').read_text());records=[]
for name in behavior:
 path='src/'+name+'.js';now=(R/path).read_bytes();digest=hashlib.sha256(now).hexdigest()
 records.append({'path':path,'unchanged':baseline['files'][path]['sha256']==digest,'sha256':digest})
assert all(x['unchanged']for x in records),'gameplay or head-map source changed unexpectedly'
(O/'behavior-unchanged.json').write_text(json.dumps({'baseline':'docs/v010/BASELINE-SOURCE-MANIFEST-v09.json','files':records},indent=2))
p=R/'assets/dc010-human-articulated.glb';s=trimesh.load(p,force='scene',process=False)
v=[m.vertices for m in s.geometry.values()];assert all(np.isfinite(x).all() for x in v)
a={'file':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'meshes':len(s.geometry),'triangles':sum(len(m.faces)for m in s.geometry.values()),'bounds':s.bounds.tolist(),'finite':True,'note':'Independent geometry parse, not a visual animation playback validation or official Khronos validation.'}
assert a['triangles']==79278;assert a['meshes']==13
(O/'independent-glb-parse.json').write_text(json.dumps(a,indent=2))
e={'python':platform.python_version(),'node':subprocess.check_output(['node','--version']).decode().strip(),'chromium':subprocess.check_output(['/usr/bin/chromium','--version']).decode().strip(),'python_packages':{n:importlib.metadata.version(n)for n in ['numpy','scipy','scikit-image','Pillow','playwright','trimesh']}}
(O/'environment.json').write_text(json.dumps(e,indent=2))
print(json.dumps({'unchanged_files':len(records),'independent_glb':a,'environment':e},indent=2))
