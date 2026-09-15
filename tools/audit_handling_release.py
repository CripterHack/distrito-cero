#!/usr/bin/env python3
"""Rebuild and audit current artifacts; browser suites must be run separately first."""
from pathlib import Path
import json,hashlib,subprocess,re
R=Path(__file__).resolve().parents[1];Q=R/'qa/v018'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (Q/log).open('w') as f:subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
paths=['index.html','assets/dc018-equipment.glb'];before={p:sha(R/p)for p in paths}
run(['python','build.py'],'build-final.txt');run(['python','tools/export_handling.py'],'export-final.json')
after={p:sha(R/p)for p in paths};assert before==after,'Non-deterministic rebuild'
(Q/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':True},indent=2))
run(['node','--test','tests/handling.test.cjs'],'handling-final.txt')
# Node needs shell glob expansion on supported dev shells, or expand explicitly here.
run(['node','--test',*[str(p.relative_to(R))for p in sorted((R/'tests').glob('*.test.cjs'))]],'logic-final.txt')
logic=(Q/'logic-final.txt').read_text();passes=int(re.search(r'# pass (\d+)',logic).group(1));assert int(re.search(r'# fail (\d+)',logic).group(1))==0
run(['python','tests/handling_exports.test.py'],'export-test.txt')
H=sha(R/'index.html');execution=json.loads((Q/'browser-execution.json').read_text());assert execution['html']==H and len(execution['suites'])==5 and all(x['code']==0 for x in execution['suites'])
expected={'handling-browser.json':40,'arsenal-browser.json':78,'library-regression.json':64,'legacy/browser-report.json':52,'arsenal-continuous.json':26};browser=[]
for name,count in expected.items():
 d=json.loads((Q/name).read_text());assert d['sha256']==H,name+' hash mismatch';assert not d['errors'] and not d['requests'],name+' runtime failure'
 items=d['checks'];actual=sum(bool(c.get('pass',c.get('passed',False)))for c in items);assert actual==count and len(items)==count,name+' count mismatch'
 browser.append({'file':name,'passed':actual,'failed':0,'sha256':sha(Q/name)})
captures=[]
for name in ['rifle','gauss','reload','pistol','binoculars']:
 p=Q/('review-'+name+'.json');d=json.loads(p.read_text());assert d['html']==H and d['gl']==0 and not d['errors'],str(p)
 captures.append({'file':'review-'+name+'.png','sha256':sha(Q/('review-'+name+'.png'))})
clip=json.loads((Q/'clip-report.json').read_text());assert clip['sha256']==H and not clip['errors'] and all(x['gl']==0 for x in clip['states']);assert (Q/'manejo.mp4').is_file()
base=subprocess.check_output(['git','rev-list','--max-parents=0','HEAD'],cwd=R,text=True).strip()
scope={'baseCommit':base,'modified':[],'unchanged':[],'new':[]}
for p in sorted((R/'src').glob('*')):
 if not p.is_file():continue
 rel=p.relative_to(R).as_posix();old=subprocess.run(['git','show',base+':'+rel],cwd=R,capture_output=True)
 scope['new' if old.returncode else 'unchanged' if hashlib.sha256(old.stdout).hexdigest()==sha(p) else 'modified'].append(rel)
for unchanged in ['src/hero-asset.js','src/hair-geometry.js','src/appearance.js','src/character-fit.js','src/human-materials.js','src/identity-ui.js','src/save-store.js','src/world.js','src/frontier-world.js','src/frontier-simulation.js','src/police.js','src/occupancy.js']:
 assert unchanged in scope['unchanged'],unchanged+' unexpectedly changed'
(Q/'behavior-scope.json').write_text(json.dumps(scope,indent=2))
source={p.relative_to(R).as_posix():sha(p)for folder in ['src','tools','tests','docs/v018']for p in sorted((R/folder).rglob('*'))if p.is_file() and '__pycache__' not in p.parts}
source.update({p:sha(R/p)for p in ['README.md','build.py']})
report={'version':'0.18','artifacts':{p:{'bytes':(R/p).stat().st_size,'sha256':sha(R/p)}for p in paths},'logic':{'passed':passes,'failed':0},'browser':{'passed':sum(x['passed']for x in browser),'suites':browser},'exportTests':1,'captures':captures,'clip':{'frames':clip['frames'],'duration':clip['duration'],'sha256':sha(Q/'manejo.mp4')},'sourceHashes':source,'scope':scope,'rebuildIdentical':True,'note':'Browser reports were executed separately. This audit rebuilds, runs Node and export tests, and verifies hashes. Not a GPU hardware or native persistence benchmark.'}
(Q/'release-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps({'logic':passes,'browser':report['browser']['passed'],'export':1,'html':report['artifacts']['index.html'],'rebuild':True},indent=2))
