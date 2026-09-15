#!/usr/bin/env python3
"""Rebuild the current standalone release and verify exact-hash test evidence."""
from pathlib import Path
import hashlib,json,subprocess,re
R=Path(__file__).resolve().parents[1];O=R/'qa/v012'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(cmd,log):
 with (O/log).open('w')as f:subprocess.run(cmd,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
paths=['src/hero-asset.js','index.html','assets/dc012-human-continuity.glb']
before={p:sha(R/p)for p in paths}
run(['python','tools/build_hero_v012.py'],'rebuild-geometry.txt')
run(['python','build.py'],'rebuild-html.txt')
run(['python','tools/export_continuity_glb.py'],'rebuild-export.txt')
after={p:sha(R/p)for p in paths};assert before==after,(before,after)
(O/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':True},indent=2))
run(['node','--test',*[str(p)for p in sorted((R/'tests').glob('*.test.cjs'))]],'node-final.txt')
logic=(O/'node-final.txt').read_text();assert '# fail 0' in logic
counts={}
for script,log in [('body_geometry.test.py','body-final.txt'),('continuity_anatomy_regression.test.py','head-final.txt'),('continuity_geometry.test.py','geometry-final.txt'),('continuity_export.test.py','export-tests.txt')]:
 run(['python','tests/'+script],log);text=(O/log).read_text();assert '\nOK\n' in text
 counts[script]=int(re.search(r'Ran (\d+) test',text)[1])
reports={}
for name,path in [('creator','continuity-browser.json'),('library','library-regression.json'),('campaign','legacy/browser-report.json'),('continuous','continuity-continuous.json')]:
 data=json.loads((O/path).read_text());assert not data['errors']and not data['requests'],(name,data)
 assert data['sha256']==after['index.html'],(name,'stale HTML')
 checks=data['checks'];assert all(c.get('pass',c.get('passed',False))for c in checks),(name,checks)
 assert data.get('failed',0)==0;reports[name]={'passed':len(checks),'path':path,'sha256':data['sha256']}
reviews={}
for name in ['neck','hand','grip','full','run','crouch','driver','pull','cast']:
 data=json.loads((O/('review-'+name+'.json')).read_text());assert data.get('sha256',data.get('source_sha256'))==after['index.html'],(name,'stale image')
 assert data['gl']==0 and not data['errors'],(name,data)
 image=O/('review-'+name+'.png');assert image.stat().st_size>10000
 reviews[name]={'image_sha256':sha(image),'data':data}
for name in ['neck','hand']:
 old=json.loads((O/('review-before-'+name+'.json')).read_text());new=reviews[name]['data'];assert old['gl']==0 and not old['errors'];assert old['quality']==new['quality'] and old['deviceScale']==new['deviceScale'] and old['camera']==new['camera'],('comparison-mismatch',name)
html=(R/'index.html').read_text();assert not re.search(r'<script[^>]+src\s*=',html,re.I);assert '/*__JS__*/'not in html and '/*__CSS__*/'not in html
sources={str(p.relative_to(R)):sha(p)for p in sorted((R/'src').glob('*'))if p.is_file()}
unchanged=[]
for name in ['core','world','frontier-world','police','simulation','dynamics','interactions','frontier-simulation','frontier-renderer','frontier-ui','occupancy','character-motion','skin-rig','audio','app','human-materials']:
 file='src/'+name+'.js';prior=subprocess.check_output(['git','show','e812215:'+file],cwd=R);assert hashlib.sha256(prior).hexdigest()==sources[file],file;unchanged.append(file)
(O/'behavior-unchanged.json').write_text(json.dumps(unchanged,indent=2))
# Independent geometry parser, in addition to the structural exporter unit test.
import trimesh
scene=trimesh.load(R/'assets/dc012-human-continuity.glb',force='scene');independent={'meshes':len(scene.geometry),'triangles':sum(len(m.faces)for m in scene.geometry.values()),'bounds':scene.bounds.tolist(),'sha256':after['assets/dc012-human-continuity.glb']}
assert independent['triangles']==85209;(O/'independent-glb.json').write_text(json.dumps(independent,indent=2))
report={'version':'0.12','base':'0.11','html_bytes':(R/'index.html').stat().st_size,'html_sha256':after['index.html'],'glb_bytes':(R/paths[2]).stat().st_size,'glb_sha256':after[paths[2]],'logic_passed':int(re.search(r'# pass (\d+)',logic)[1]),'browser_reports':reports,'browser_total':sum(d['passed']for d in reports.values()),'geometry_export':counts,'geometry_export_total':sum(counts.values()),'reviews':reviews,'sources':sources,'errors':[],'native_persistence_tested':False,'hardware_gpu_tested':False,'physical_mobile_tested':False,'reproducible_build':True}
(O/'release-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:v for k,v in report.items()if k not in ['sources','reviews']},indent=2))
