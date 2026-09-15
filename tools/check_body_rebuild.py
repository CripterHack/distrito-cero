"""Deterministic rebuild from included offline authoring data."""
from pathlib import Path
import subprocess,hashlib,json,time
R=Path(__file__).resolve().parents[1];O=R/'qa/v010'
paths=['src/hero-asset.js','src/human-materials.js','index.html','assets/dc010-human-articulated.glb']
def digest():return {n:hashlib.sha256((R/n).read_bytes()).hexdigest()for n in paths}
a=digest();t=time.monotonic()
for args in [['python','tools/build_hero_v010.py'],['python','build.py'],['python','tools/export_body_glb.py']]:subprocess.run(args,cwd=R,check=True)
b=digest();record={'before':a,'after':b,'identical':a==b,'seconds':time.monotonic()-t,'offline_inputs':'assets/anatomy-source/compact.bin and included maps. No new source downloads.'}
(O/'rebuild.json').write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2));assert a==b,'nondeterministic output'
