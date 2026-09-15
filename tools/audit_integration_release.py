#!/usr/bin/env python3
"""Bind final logic, geometry, browser evidence and captures to exact release bytes.
No browser is re-run by this audit: run the documented suites first.
"""
from pathlib import Path
import hashlib,json,re,subprocess,base64
import numpy as np
R=Path(__file__).resolve().parents[1];O=R/'qa/v015';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
html=sha(R/'index.html');glb=R/'assets/dc015-human-integrated.glb'
# Rebuild from offline baseline without changing the deliverable.
paths=[R/'src/hero-asset.js',R/'index.html',glb];before={str(p.relative_to(R)):sha(p)for p in paths}
for cmd in [['python','tools/integrate_cervical_v015.py'],['python','build.py'],['python','tools/export_integration_glb.py']]:subprocess.run(cmd,cwd=R,stdout=subprocess.DEVNULL,check=True)
after={str(p.relative_to(R)):sha(p)for p in paths};assert before==after
(O/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':True},indent=2))
with (O/'logic-final.txt').open('w') as out:subprocess.run(['node','--test',*[str(p.relative_to(R))for p in sorted((R/'tests').glob('*.test.cjs'))]],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=True)
logic=(O/'logic-final.txt').read_text();assert re.search(r'# fail 0\b',logic)
logic_count=int(re.search(r'# tests (\d+)',logic).group(1))
with (O/'geometry-final.txt').open('w')as out:subprocess.run(['python','tools/run_integration_geometry.py'],cwd=R,stdout=out,stderr=subprocess.STDOUT,check=True)
geometry=load(O/'geometry-suite.json');assert geometry['failures']==geometry['errors']==0
browser=[]
for file in ['integration-browser.json','library-regression.json','legacy/browser-report.json','integration-continuous.json']:
 d=load(O/file);assert d['sha256']==html,(file,'stale HTML');assert not d['errors'] and not d['requests'],file
 assert d.get('failed',0)==0,file
 checks=d['checks'];assert all(c.get('pass',c.get('passed',False))for c in checks),file
 browser.append({'report':file,'passed':len(checks),'sha256':d['sha256']})
assert len(load(O/'browser-execution.json'))==4
assert all(x['exit_code']==0 for x in load(O/'browser-execution.json'))
captures=[];baseline=sha(O/'baseline-v014.html');assert baseline=='82c535a0d25d3f5ba1753ae2248cb284745608bd53e2590b1e07237be8d40883'
for run in load(O/'capture-execution.json'):
 assert run['exit_code']==0,run
 label=run['capture'];j=O/('review-'+label+'.json');d=load(j);expected=baseline if label.startswith('before-')else html
 assert d.get('sha256',d.get('source_sha256'))==expected,j
 assert d['gl']==0 and not d['errors'],j
 p=O/('review-'+label+'.png');assert p.is_file();captures.append({'name':label,'sha256':sha(p),'source_html':expected})
assert len(captures)==17
clip=load(O/'clip-report.json');assert clip['sha256']==html and clip['frames']==160
assert not clip['errors'] and not clip['requests'];assert (O/'movilidad-integrada.mp4').is_file()
# Runtime scope versus the immutable base commit in the working checkout.
scope={}
try:
 for p in sorted((R/'src').glob('*')):
  previous=subprocess.check_output(['git','show','HEAD:src/'+p.name],cwd=R,stderr=subprocess.DEVNULL)
  scope[p.name]='unchanged' if previous==p.read_bytes() else 'modified'
except subprocess.CalledProcessError:scope={'note':'Git baseline unavailable; see the distributed source manifest.'}
(O/'behavior-scope.json').write_text(json.dumps(scope,indent=2))
DT=np.dtype([('p','<i2',3),('n','<i2',3),('uv','<u2',2),('j','u1',4),('w','u1',4)])
metrics={}
for key,path in [('before',R/'assets/hero-v014-baseline.js'),('after',R/'src/hero-asset.js')]:
 d=json.loads(path.read_text().split('DC.HeroAsset=')[1].strip().rstrip(';'));q=next(p for p in d['parts']if p['name']=='face');v=np.unique(np.frombuffer(base64.b64decode(q['data']),DT)['p'],axis=0)/1e4
 n=v[(v[:,1]>1.504)&(v[:,1]<1.536)];h=v[(v[:,1]>1.633)&(v[:,1]<1.695)];mid=v[(v[:,1]>1.512)&(v[:,1]<1.527)]
 metrics[key]={'midneck_width_m':float(np.ptp(mid[:,0])),'neck_head_width_ratio':float(np.ptp(n[:,0])/np.ptp(h[:,0])),'neck_depth_m':float(np.ptp(n[:,2])),'triangles':sum(p['vertices']//3 for p in d['parts'])}
(O/'morphology-measurements.json').write_text(json.dumps(metrics,indent=2))
report={'version':'0.15','name':'Integración cervical','html':{'bytes':(R/'index.html').stat().st_size,'sha256':html},'glb':{'bytes':glb.stat().st_size,'sha256':sha(glb)},'logic':logic_count,'geometry':geometry['passed'],'browser':browser,'browser_total':sum(x['passed']for x in browser),'captures':captures,'clip':{'frames':160,'playback_fps':20,'sha256':sha(O/'movilidad-integrada.mp4'),'source_sha256':html,'controlled_time':True},'geometry_selection':geometry,'measurements':metrics,'sourceHashes':{str(p.relative_to(R)):sha(p)for p in sorted((R/'src').glob('*'))},'limits':['Not AAA or photorealistic','No hardware GPU or physical mobile validation','In-memory localStorage fixtures; not native persistence between restarts','Prepared camera/positions for review; no full-session performance certification','No exhaustive self-collision validation']}
(O/'release-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:report[k]for k in ['version','html','glb','logic','geometry','browser_total']},indent=2))
