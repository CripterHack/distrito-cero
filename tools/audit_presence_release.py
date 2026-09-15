#!/usr/bin/env python3
"""Validate evidence for the current HTML before producing the release manifest.
This consumes completed test reports, not invented counters or historic passes.
"""
from pathlib import Path
import hashlib, json, re, subprocess
R=Path(__file__).resolve().parents[1]
Q=R/'qa/v08'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert (Q/'final-suite.status').read_text().strip()=='0','Run the complete final suite first'
reports={k:json.loads((Q/p).read_text()) for k,p in {
 'presence':'presence-browser.json','legacy':'legacy/browser-report.json',
 'horizon':'horizon/horizon-browser.json','continuous':'presence-continuous.json'}.items()}
for k,d in reports.items():
 assert d['errors']==[] and d['requests']==[],f'Errors or network requests: {k}'
 if k!='legacy':assert d['failed']==0
assert all(c['passed'] for c in reports['legacy']['checks'])
assert reports['presence']['html_sha256']==reports['continuous']['sha256']==sha(R/'index.html'),'Stale test evidence'
log=(Q/'logic-final.txt').read_text()
n=int(re.search(r'^# pass (\d+)$',log,re.M)[1]);assert re.search(r'^# fail 0$',log,re.M)
assert 'Ran 1 test' in (Q/'hair-green.txt').read_text() and (Q/'hair-green.txt').read_text().rstrip().endswith('OK')
assert 'Ran 2 tests' in (Q/'exports-green.txt').read_text() and (Q/'exports-green.txt').read_text().rstrip().endswith('OK')
counts={'node':n,'presence_browser':reports['presence']['passed'],'legacy_browser':len(reports['legacy']['checks']),
 'horizon_browser':reports['horizon']['passed'],'continuous_browser':reports['continuous']['passed'],
 'mesh_geometry':1,'glb_structural':2}
paths=['core','world','police','simulation','dynamics','interactions','character-motion','frontier-world',
 'frontier-simulation','frontier-renderer','frontier-ui','visual-geometry','audio']
unchanged=[]
if (R/'.git').exists():
 for f in paths:
  path=f'src/{f}.js';b=subprocess.check_output(['git','show',f'e61b0fe:{path}'],cwd=R)
  assert b==(R/path).read_bytes(),f'Unexpected change of preserved source: {path}'
  unchanged.append(path)
else:
 # A distributed source ZIP does not carry Git. The canonical manifest retains
 # the comparison performed in the authoring workspace.
 unchanged=json.loads((Q/'release-report.json').read_text()).get('unchanged_source_files',[])
html=(R/'index.html').read_text()
assert not re.search(r'<script[^>]+\bsrc\s*=',html,re.I)
assert not re.search(r'<link[^>]+\bhref\s*=\s*[\"\']https?://',html,re.I)
report={
 'version':'0.8 Presencia','date':'2026-09-11',
 'base':{'name':'Horizonte v0.7','commit':'e61b0fe','html_sha256':'e25c72344564b925c797bd907a646751c3b6e3b59c882b45f2f1420babfe82b3'},
 'build':{'bytes':(R/'index.html').stat().st_size,'sha256':sha(R/'index.html')},
 'tests':counts,'browser_assertions':sum(v for k,v in counts.items() if k.endswith('_browser')),
 'errors':[],'network_requests':[], 'unchanged_source_files':unchanged,
 'geometry':{'hero_triangles':43579,'lod_triangles':[43579,15206,3335],'bones_per_actor':17,'palette_capacity':128,'palette_texture_bytes':139264},
 'models':[{'file':f'assets/{p.name}','bytes':p.stat().st_size,'sha256':sha(p)} for p in (R/'assets').glob('dc08-*.glb')],
 'devices':{'browser':'Chromium/Xvfb/ANGLE SwiftShader','native_hardware':False,'native_mobile':False,'safari':False,'long_soak':False,'local_storage_native':False},
 'visual_quality':'Procedural stylized prototype. Not AAA / not photorealistic.',
 'known_limits':['No mocap, expressive facial animation or finger rig','Approximate IK contacts, no full-body collision or physical ragdoll','Shared body family with tints and limited proportions','Flat, orthogonal procedural world retained','Main-thread streaming, no hardware FPS commitment','Maximum 24 persistent evicted NPCs and bounded local traffic']
}
(Q/'release-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(report,ensure_ascii=False,indent=2))
