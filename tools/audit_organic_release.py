#!/usr/bin/env python3
"""Rebuild the current release and verify evidence against exact bytes.
Does not rerun browser tests, invent their coverage, or execute older builders.
"""
from pathlib import Path
import subprocess,hashlib,json,sys,re
R=Path(__file__).resolve().parents[1];O=R/'qa/v013';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (O/log).open('w')as f:
  p=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(f'{args}: inspect {log}')
files=['src/hero-asset.js','index.html','assets/dc013-human-motion.glb']
before={p:sha(R/p)for p in files}
run([sys.executable,'tools/polish_surface_v013.py'],'mesh-rebuild.txt')
run([sys.executable,'build.py'],'html-rebuild.txt')
run([sys.executable,'tools/export_organic_glb.py'],'export-rebuild.txt')
after={p:sha(R/p)for p in files}
(O/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':before==after},indent=2));assert before==after,'Nondeterministic construction'
run(['node','--test',*map(str,sorted((R/'tests').glob('*.test.cjs')))],'logic-final.txt')
logic=(O/'logic-final.txt').read_text();m=re.search(r'^# pass (\d+)$',logic,re.M);assert m and '# fail 0' in logic
geom=[]
for script in ['body_geometry','continuity_anatomy_regression','continuity_geometry','surface-polish','organic_export']:
 log=script+'-final.txt';run([sys.executable,'tests/'+script+'.test.py'],log);text=(O/log).read_text();m2=re.search(r'Ran (\d+) test',text);assert m2 and '\nOK' in text;geom.append({'suite':script,'passed':int(m2.group(1))})
reports=[]
for path in ['organic-browser.json','library-regression.json','legacy/browser-report.json','organic-continuous.json']:
 d=json.loads((O/path).read_text());assert d['sha256']==after['index.html'],path+' has stale HTML hash';assert not d.get('errors') and not d.get('requests') and not d.get('failed'),path
 count=d.get('passed',len(d['checks']));assert count==len(d['checks']),path+' incomplete';assert all(c.get('pass',c.get('passed',False))for c in d['checks']),path
 reports.append({'report':path,'passed':count})
frames=[]
for path in sorted(O.glob('review-*.json')):
 if 'before-' in path.name or 'first-' in path.name:continue
 d=json.loads(path.read_text());assert (d.get('sha256')or d.get('source_sha256'))==after['index.html'],path;assert not d.get('errors') and d.get('gl')==0,path;frames.append(path.name)
clip=json.loads((O/'clip-report.json').read_text());assert clip['sha256']==after['index.html'] and clip['frames']==180 and not clip['errors'] and not clip['requests']
base=json.loads((R/'docs/v013/BASELINE.json').read_text());current={str(p.relative_to(R)):sha(p)for p in sorted((R/'src').glob('*'))if p.is_file()}
# Baseline may contain either a map or a wrapped metadata map.
base=base.get('files',base.get('sha256',base))
changed=[p for p,h in current.items()if base.get(p)!=h];same=[p for p,h in current.items()if base.get(p)==h]
scope={'changed':changed,'unchanged':same,'note':'Animation phase updates in simulation/interactions/occupancy are intentional. Gameplay positions, collision rules and saved schema are not sourced from visual foot tracking.'};(O/'behavior-scope.json').write_text(json.dumps(scope,indent=2))
report={'version':'0.13','html':{'bytes':(R/'index.html').stat().st_size,'sha256':after['index.html']},'glb':{'bytes':(R/files[2]).stat().st_size,'sha256':after[files[2]]},'logic':int(m.group(1)),'geometry':geom,'geometryTotal':sum(t['passed']for t in geom),'browser':reports,'browserTotal':sum(t['passed']for t in reports),'currentReviewFrames':frames,'animationReviewFrames':clip['frames'],'sourceHashes':current,'limits':'Chromium 144 / Xvfb / SwiftShader / isolated memory storage. No physical GPU/device, Safari or native file:// persistence verification. No AAA or photorealism certification.'}
(O/'release-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in report.items()if k not in ['sourceHashes','currentReviewFrames']},indent=2))
