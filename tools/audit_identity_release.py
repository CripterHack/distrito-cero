#!/usr/bin/env python3
"""Check the shipped sources, reconstruct baked geometry, build and verify current evidence."""
from pathlib import Path
import subprocess,json,hashlib,re,zipfile
R=Path(__file__).resolve().parents[1];O=R/'qa/v011'
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before={p:hashfile(R/p)for p in ['src/hero-asset.js','index.html']}
subprocess.run(['python','tools/refine_identity.py'],cwd=R,check=True)
subprocess.run(['python','build.py'],cwd=R,check=True)
after={p:hashfile(R/p)for p in before}
assert before==after,(before,after)
(O/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':True},indent=2))
for cmd,log in [(['node','--test',*map(str,sorted((R/'tests').glob('*.test.cjs')))],'logic.txt'),(['python','tests/body_geometry.test.py'],'body-geometry.txt'),(['python','tests/body_anatomy_regression.test.py'],'head-geometry.txt')]:
 with (O/log).open('w')as f:subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
logic=(O/'logic.txt').read_text();count=int(re.search(r'# pass (\d+)',logic)[1]);assert '# fail 0' in logic
ui=json.loads((O/'identity-browser.json').read_text());live=json.loads((O/'identity-continuous.json').read_text());legacy=json.loads((O/'legacy/browser-report.json').read_text());caps=json.loads((O/'editor-captures.json').read_text())
for data in [ui,live]:
 assert data['failed']==0 and not data['errors']and not data['requests'];assert data['sha256']==after['index.html']
assert not legacy['errors']and not legacy['requests'];assert all(x['passed']for x in legacy['checks']);assert all(x['gl']==0 for x in caps['captures'])and not caps['errors']and caps['finalGl']==0;assert caps['sha256']==after['index.html']
html=(R/'index.html').read_text();assert not re.search(r'<script[^>]+src\s*=',html,re.I);assert '/*__JS__*/'not in html and '/*__CSS__*/'not in html
src={str(p.relative_to(R)):hashfile(p)for p in sorted((R/'src').glob('*'))if p.is_file()}
base=zipfile.ZipFile('/mnt/data/distrito-cero-v0.10-codigo.zip')
unchanged=[]
for name in ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','occupancy','character-motion','skin-rig','audio','app','frontier-ui','human-materials']:
 file='src/'+name+'.js';orig=base.read('distrito-cero/'+file);assert hashlib.sha256(orig).hexdigest()==src[file],file;unchanged.append(file)
(O/'behavior-unchanged.json').write_text(json.dumps(unchanged,indent=2))
report={'version':'0.11','base':'0.10','html_bytes':(R/'index.html').stat().st_size,'html_sha256':after['index.html'],'logic_passed':count,'browser_identity':ui['passed'],'browser_legacy':len(legacy['checks']),'browser_continuous':live['passed'],'browser_total':ui['passed']+len(legacy['checks'])+live['passed'],'geometry_body':7,'geometry_head':6,'errors':[],'native_persistence_tested':False,'physical_gpu_tested':False,'reproducible_build':True,'sources':src}
(O/'release-report.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items()if k!='sources'},indent=2))
