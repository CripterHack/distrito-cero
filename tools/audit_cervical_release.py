#!/usr/bin/env python3
"""Rebuild v0.14 and verify current evidence against its exact HTML.
Browser tests must be executed separately. No historical passes are counted.
"""
from pathlib import Path
import subprocess,hashlib,json,sys,re
R=Path(__file__).resolve().parents[1];O=R/'qa/v014';O.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,log):
 with (O/log).open('w') as f:
  p=subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError(f'{args}: inspect qa/v014/{log}')
files=['src/hero-asset.js','index.html','assets/dc014-human-cervical.glb']
before={p:sha(R/p) for p in files}
run([sys.executable,'tools/refine_cervical_v014.py'],'mesh-rebuild.txt')
run([sys.executable,'build.py'],'html-rebuild.txt')
run([sys.executable,'tools/export_cervical_glb.py'],'export-rebuild.txt')
after={p:sha(R/p) for p in files}
(O/'rebuild.json').write_text(json.dumps({'before':before,'after':after,'identical':before==after},indent=2));assert before==after,'Nondeterministic construction'
run(['node','--test',*map(str,sorted((R/'tests').glob('*.test.cjs')))],'logic-final.txt')
logic=(O/'logic-final.txt').read_text();m=re.search(r'^# pass (\d+)$',logic,re.M);assert m and '# fail 0' in logic
geom=[]
for script,selection in [
 ('body_geometry',[]),('continuity_anatomy_regression',[]),('continuity_geometry',[]),
 ('surface-polish',['Polish.test_hands_keep_shape_and_weights_with_no_split_normals','Polish.test_no_topology_inflation_or_bone_contract_change','Polish.test_polished_normals_weights_and_winding']),
 ('cervical_geometry',[]),('cervical_deformation',[]),('cervical_export',[])]:
 log=script+'-final.txt';run([sys.executable,'tests/'+script+'.test.py',*selection],log);text=(O/log).read_text();m2=re.search(r'Ran (\d+) test',text);assert m2 and '\nOK' in text;geom.append({'suite':script,'passed':int(m2.group(1)),'selected_tests':selection or 'all'})
reports=[]
for path in ['cervical-browser.json','library-regression.json','legacy/browser-report.json','cervical-continuous.json']:
 d=json.loads((O/path).read_text());assert d['sha256']==after['index.html'],path+' has stale HTML hash';assert not d.get('errors') and not d.get('requests') and not d.get('failed'),path
 count=d.get('passed',len(d['checks']));assert count==len(d['checks']),path+' incomplete';assert all(c.get('pass',c.get('passed',False)) for c in d['checks']),path
 reports.append({'report':path,'passed':count})
frames=[];comparisons=[]
for path in sorted(O.glob('review-*.json')):
 d=json.loads(path.read_text());h=d.get('sha256') or d.get('source_sha256')
 if 'before-' in path.name:
  assert h==json.loads((R/'docs/v014/BASELINE.json').read_text())['html']['sha256'],path
  comparisons.append(path.name);continue
 assert h==after['index.html'],path;assert not d.get('errors') and d.get('gl')==0,path;frames.append(path.name)
clip=json.loads((O/'clip-report.json').read_text());assert clip['sha256']==after['index.html'] and clip['frames']==160 and not clip['errors'] and not clip['requests']
assert len(list((O/'clip-frames').glob('*.jpg')))==160
base=json.loads((R/'docs/v014/BASELINE.json').read_text())['sourceHashes'];current={str(p.relative_to(R)):sha(p) for p in sorted((R/'src').glob('*')) if p.is_file()}
changed=[p for p,h in current.items() if base.get(p)!=h];same=[p for p,h in current.items() if base.get(p)==h]
scope={'changed':changed,'unchanged':same,'note':'Cervical visual rig, mesh, morph/shader and studio controls change. Gameplay simulation, world, occupancy, physical collision, save schema and save-store remain byte-identical to v0.13.'};(O/'behavior-scope.json').write_text(json.dumps(scope,indent=2))
for f in ['simulation.js','occupancy.js','save-store.js','frontier-world.js','frontier-simulation.js','character-motion.js']:
 assert 'src/'+f in same,f
report={'version':'0.14','baseHtml':json.loads((R/'docs/v014/BASELINE.json').read_text())['html'],'html':{'bytes':(R/'index.html').stat().st_size,'sha256':after['index.html']},'glb':{'bytes':(R/files[2]).stat().st_size,'sha256':after[files[2]]},'logic':int(m.group(1)),'geometry':geom,'geometryTotal':sum(t['passed'] for t in geom),'browser':reports,'browserTotal':sum(t['passed'] for t in reports),'currentReviewFrames':frames,'beforeReviewFrames':comparisons,'animationReviewFrames':clip['frames'],'sourceHashes':current,'reproducible':before==after,'scope':scope,'limits':'Chromium / Xvfb / SwiftShader / explicit memory storage fixture. No physical GPU/device, Safari, native file persistence or lengthy sessions tested. Not a photorealism/AAA certification.'}
(O/'release-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in report.items() if k not in ['sourceHashes','scope']},indent=2))
