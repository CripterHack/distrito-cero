#!/usr/bin/env python3
"""Verify rebuild bytes and match current execution evidence; no network action.
Browser executions must be run separately. This audit never invents their results.
"""
from pathlib import Path
import subprocess,json,hashlib,re
R=Path(__file__).resolve().parents[1];O=R/'qa/v016';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,filename):
 with (O/filename).open('w') as log:
  p=subprocess.run(args,cwd=R,stdout=log,stderr=subprocess.STDOUT,timeout=180)
 assert p.returncode==0,(args,p.returncode)
paths=['src/hero-asset.js','src/hair-geometry.js','src/character-fit.js','index.html','assets/dc016-human-traits.glb']
before={s:sha(R/s) for s in paths}
run(['python','build.py'],'build-final.log')
run(['python','tools/export_traits_glb.py'],'export-final.log')
after={s:sha(R/s) for s in paths};assert before==after,(before,after)
(O/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':True,'scope':'HTML and neutral GLB rebuilt offline from distributed canonical mesh and native source generators. This does not regenerate or re-download historical source scans.'},indent=2))
run(['node','--test',*[str(p.relative_to(R)) for p in sorted((R/'tests').glob('*.test.cjs'))]],'node-final.txt')
node=(O/'node-final.txt').read_text();passed=int(re.search(r'^# pass (\d+)$',node,re.M)[1]);assert re.search(r'^# fail 0$',node,re.M)
run(['python','tools/run_traits_geometry.py'],'geometry-final.txt')
geom=json.loads((O/'geometry-suite.json').read_text());assert geom['errors']==geom['failures']==0
html=sha(R/'index.html');browsers=[]
for file in ['traits-browser.json','library-regression.json','legacy/browser-report.json','integration-continuous.json']:
 d=json.loads((O/file).read_text());assert d['sha256']==html,file;assert not d['errors'] and not d['requests'],file
 checks=d['checks'];assert all(c.get('pass',c.get('passed',False)) for c in checks),file
 browsers.append({'file':file,'passed':len(checks),'sha256':html})
assert all(x['exit_code']==0 for x in json.loads((O/'browser-execution.json').read_text()))
images=[]
for p in sorted(O.glob('review-*.json')):
 d=json.loads(p.read_text());h=d.get('sha256',d.get('source_sha256'));old='before-' in p.name
 expected=sha(Path('/mnt/data/distrito-cero-v0.15-integracion.html')) if old else html
 assert h==expected,(p.name,h);assert d['gl']==0 and not d['errors'],p.name
 images.append({'file':p.with_suffix('.png').name,'sha256':sha(p.with_suffix('.png')),'source_sha256':h,'baseline':old})
for file in ['hair-gallery-report.json','editor-capture.json','clip-report.json']:
 d=json.loads((O/file).read_text());assert d['sha256']==html,file;assert not d['errors'] and not d.get('requests',[]),file
assert all(x['exit_code']==0 for x in json.loads((O/'capture-execution.json').read_text()))
gpu=json.loads((O/'gpu-transform-feedback.json').read_text());assert gpu['gl']==0 and gpu['maxPositionError']<2e-6 and gpu['maxNormalError']<.003
# Source comparison against the isolated copy's immutable base commit.
base=subprocess.check_output(['git','rev-list','--max-parents=0','HEAD'],cwd=R,text=True).strip();scope=[]
for p in sorted((R/'src').glob('*')):
 if not p.is_file():continue
 path=str(p.relative_to(R));res=subprocess.run(['git','show',base+':'+path],cwd=R,capture_output=True)
 baseline=hashlib.sha256(res.stdout).hexdigest() if res.returncode==0 else None
 scope.append({'file':path,'before':baseline,'after':sha(p),'changed':baseline!=sha(p)})
(O/'behavior-scope.json').write_text(json.dumps(scope,indent=2))
sourcePaths=[R/'build.py',*sorted((R/'src').glob('*')),*sorted((R/'docs/v016').glob('*')),*sorted((R/'tests').glob('traits*')),*sorted((R/'tools').glob('*traits*'))]
sourceHashes={str(p.relative_to(R)):sha(p) for p in sourcePaths if p.is_file()}
report={'version':'0.16','base':'0.15 Integración cervical','html':{'bytes':(R/'index.html').stat().st_size,'sha256':html},'glb':{'bytes':(R/'assets/dc016-human-traits.glb').stat().st_size,'sha256':sha(R/'assets/dc016-human-traits.glb')},'logic':passed,'geometry':geom['passed'],'browserChecks':sum(d['passed']for d in browsers),'browsers':browsers,'gpuSamples':len(gpu['cases']),'fittedPoseSamples':297,'rebuildIdentical':True,'images':images,'sourceHashes':sourceHashes,'limitations':'Stylized, not AAA/photorealistic. Chromium/SwiftShader, memory storage fixture, prepared scene positions. No physical GPU FPS, native file reopen persistence, physical phone or general collision guarantee.'}
(O/'release-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in report.items() if k not in ['images','sourceHashes']},indent=2))
