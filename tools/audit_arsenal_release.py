#!/usr/bin/env python3
"""Rebuild and verify the exact release. Browser suites must be executed separately.
Uses only Python's standard library; Node is needed for tests and the prop exporter.
Never infers a fresh browser pass from an earlier version's report.
"""
from pathlib import Path
import hashlib, json, re, subprocess

R = Path(__file__).resolve().parents[1]
Q = R / 'qa/v017'
Q.mkdir(parents=True, exist_ok=True)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def run(cmd, output):
    with (Q / output).open('w') as log:
        result = subprocess.run(cmd, cwd=R, stdout=log, stderr=subprocess.STDOUT, timeout=180)
    if result.returncode:
        raise RuntimeError(f'{cmd} failed: see {output}')
    return (Q / output).read_text()

files = ['index.html', 'assets/dc017-equipment.glb']
before = {p: sha(R / p) for p in files}
run(['python', 'build.py'], 'build-final.txt')
run(['python', 'tools/export_equipment.py'], 'export-info.json')
after = {p: sha(R / p) for p in files}
assert before == after, 'Rebuild changed the files that were tested in the browser'
(Q / 'rebuild.json').write_text(json.dumps({'before': before, 'after': after, 'identical': True}, indent=2))
tap = run(['node', '--test', *[str(p.relative_to(R)) for p in sorted((R/'tests').glob('*.test.cjs'))]], 'logic-final.txt')
logic = {k: int(re.search(r'^# ' + k + r' (\d+)$', tap, re.M).group(1)) for k in ['tests','pass','fail','cancelled','skipped']}
assert logic['fail'] == logic['cancelled'] == logic['skipped'] == 0
run(['python', 'tests/arsenal_exports.test.py'], 'export-green.txt')

reports = {}
for name in ['arsenal-browser.json', 'library-regression.json', 'legacy/browser-report.json', 'arsenal-continuous.json']:
    d = json.loads((Q/name).read_text())
    assert d['sha256'] == after['index.html'], name + ' belongs to another HTML'
    assert not d['errors'] and not d['requests'], name + ' has browser errors or requests'
    checks = d['checks']
    passed = sum(bool(c.get('pass', c.get('passed', False))) for c in checks)
    assert passed == len(checks), name + ' has a failing assertion'
    reports[name] = {'passed': passed, 'failed': 0, 'reportSha256': sha(Q/name)}
execution = json.loads((Q/'browser-execution.json').read_text())
assert len(execution) == 4 and all(x['exit']==0 and x['sha256']==after['index.html'] for x in execution)

baseline = json.loads((R/'docs/v017/BASELINE.json').read_text())
scope = {'unchanged': [], 'modified': [], 'new': []}
for path, previous in baseline.items():
    scope['unchanged' if sha(R/path)==previous else 'modified'].append(path)
for path in (R/'src').glob('*'):
    key = path.relative_to(R).as_posix()
    if key not in baseline:
        scope['new'].append(key)
for key in ['src/hero-asset.js','src/hair-geometry.js','src/character-fit.js','src/skin-rig.js',
            'src/appearance.js','src/human-materials.js','src/identity-ui.js','src/save-store.js']:
    assert key in scope['unchanged'], key+' unexpectedly changed'
(Q/'behavior-scope.json').write_text(json.dumps(scope, indent=2))

capture = {}
for mode in ['gauss','emp','optics','reload']:
    meta = json.loads((Q/f'review-{mode}.json').read_text())
    assert meta['html'] == after['index.html'] and meta['gl']==0 and not meta['errors']
    capture[f'review-{mode}.png'] = sha(Q/f'review-{mode}.png')
for name in ['01-selector.png','05-selector-390.png','05-selector-844.png']:
    capture[name]=sha(Q/name)
report = {'version':'0.17','baseHtmlSha256':baseline['index.html'],
          'artifacts':{p:{'bytes':(R/p).stat().st_size,'sha256':after[p]}for p in files},
          'logic':logic,'browser':reports,'browserTotal':sum(x['passed']for x in reports.values()),
          'portableEquipmentExportTests':1,'rebuildIdentical':True,'captures':capture,
          'sourceHashes':{p.relative_to(R).as_posix():sha(p) for p in sorted((R/'src').glob('*')) if p.is_file()},
          'geometry':json.loads((Q/'export-info.json').read_text()),
          'limits':'Browser reports are from the separately executed final suites, not rerun by this audit. Software WebGL and isolated storage. No hardware FPS, native persistent storage, Safari or physical mobile certification.'}
(Q/'release-report.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({'logic':logic,'browserTotal':report['browserTotal'],'artifacts':report['artifacts'],'rebuilt':True},indent=2))
