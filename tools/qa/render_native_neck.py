#!/usr/bin/env python3
"""Comparable neck closeups in the production renderer with a prepared fixture.

Uses the canonical character stage without changing it. Fixed clock/poses and
in-memory storage are explicit; captures are not FPS or artistic acceptance.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import copy
import hashlib
import json
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tests'))
from character_benchmark import FIX
from tools.qa.character_matrix import load_matrix, render_gallery
from qa_support import launch_options
from playwright.sync_api import sync_playwright

CAMERA = {'targetY': 1.58, 'distance': .85, 'eyeOffsetY': .015, 'fov': .62}
VIEWPORT = {'width': 720, 'height': 720}
CAPTURE = r'''c=>{
 const base=DCCharacterBenchmark.applyCase(c),r=DC_APP.renderer,s=r.currentSim;
 if(!s||s===DC_APP.sim)throw new Error('Expected isolated canonical fixture simulation');
 const a=s.player,k=c.closeup,center=[a.x,k.targetY,a.z];
 r.camera.eye=[center[0]+Math.sin(c.yaw)*k.distance,center[1]+k.eyeOffsetY,center[2]+Math.cos(c.yaw)*k.distance];
 r.camera.target=center;r.camera.initialized=true;r.fovOverride=k.fov;
 const originalBodyParts=r.lodParts[0];
 try{
  if(![0,1,2].includes(c.bodyGeometryLOD)||!r.lodParts[c.bodyGeometryLOD]?.length)throw new Error('Missing requested body geometry');
  r.lodParts[0]=r.lodParts[c.bodyGeometryLOD];
  r.lightTime=-1;r.lightVP=null;r.frame=0;r.render(s);r.gl.finish();
 }finally{r.lodParts[0]=originalBodyParts;}
 const g=r.gl,glError=g.getError(),finitePalette=Array.from(r.heroPalette).every(Number.isFinite);
 const storageUntouched=base.storageUntouched&&JSON.stringify([...qaCharacterStorage.entries()])===qaNeckBaseline.storage;
 const liveSimulationUntouched=base.liveSimulationUntouched&&JSON.stringify(DC_APP.sim.serialize())===qaNeckBaseline.live;
 if(g.isContextLost()||glError!==g.NO_ERROR||!finitePalette||r.castStats.actors<1||!storageUntouched||!liveSimulationUntouched)
  throw new Error('Invalid closeup sample: '+JSON.stringify({glError,finitePalette,storageUntouched,liveSimulationUntouched}));
 return {...base,glError,finitePalette,storageUntouched,liveSimulationUntouched,
  actors:r.castStats.actors,triangles:r.castStats.triangles,drawBatches:r.castStats.drawBatches,
  camera:{eye:[...r.camera.eye],target:[...r.camera.target],fov:r.fovOverride},
  bodyGeometryLOD:c.bodyGeometryLOD,forcedBodyGeometry:c.bodyGeometryLOD!==0,
  bodyGeometryRestored:r.lodParts[0]===originalBodyParts,hairGeometryLOD:0,
  preparedActor:{lookYaw:a.lookYaw||0,lookPitch:a.lookPitch||0,lookRoll:a.lookRoll||0},
  fixtureTime:s.time,materialVersion:DC.HumanMaterials.version,
  normalScale:DC.HumanMaterials.atlas?.normalScale??.30};
}'''


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cases(matrix):
    result = []
    for pose in ('idle', 'neck'):
        for light in ('neutral', 'side'):
            for camera in ('front', 'profile', 'back', 'three-quarter'):
                result.append({'id': '--'.join((pose, light, camera)),
                    'profile': 'neutral', 'pose': pose, 'light': light, 'camera': camera,
                    'look': {**copy.deepcopy(matrix['profiles']['neutral']), 'hairStyle': 0},
                    'sample': copy.deepcopy(matrix['poses'][pose]),
                    'yaw': matrix['cameras'][camera], 'daylight': matrix['lights'][light],
                    'seed': matrix['seed'], 'time': matrix['time'], 'closeup': dict(CAMERA),
                    'bodyGeometryLOD': 0})
    # Exact lower body mesh buffers at the same closeup camera; this explicitly
    # does not exercise chooseLOD distance/hysteresis or lower-LOD groom selection.
    for lod in (1, 2):
        for reference in result[:16]:
            if reference['pose'] != 'idle' or reference['camera'] == 'three-quarter':
                continue
            sample = copy.deepcopy(reference)
            sample.update(id=reference['id'] + '--body-lod' + str(lod), bodyGeometryLOD=lod)
            result.append(sample)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--html', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--label', required=True)
    parser.add_argument('--browser', type=Path)
    parser.add_argument('--headed', action='store_true')
    args = parser.parse_args()
    html, out = args.html.resolve(), args.output.resolve()
    artifacts = ROOT / 'artifacts'
    if not out.is_relative_to(artifacts) or out == artifacts or artifacts.resolve() != artifacts:
        parser.error('Output must be a fresh directory beneath repository artifacts/.')
    if not html.is_file():
        parser.error('HTML input does not exist.')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'images').mkdir()
    stage = ROOT / 'tools/qa/character_stage.js'
    matrix_path = ROOT / 'tests/benchmarks/characters.json'
    inputs = {'html': digest(html), 'stage': digest(stage), 'matrix': digest(matrix_path),
              'benchmarkFixture': digest(ROOT / 'tests/character_benchmark.py'), 'tool': digest(__file__)}
    report = {'schema': 1, 'label': args.label, 'status': 'running',
        'startedUtc': datetime.now(timezone.utc).isoformat(),
        'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'htmlSha256': inputs['html'], 'inputHashes': inputs,
        'matrix': 'native-neck-closeups-v2', 'cameraContract': CAMERA, 'viewport': VIEWPORT,
        'nativeStorage': False, 'physicalGpu': False, 'artisticAcceptance': 'pending',
        'scenario': 'Canonical character benchmark fixture; neutral profile, hair 0, idle/neck poses, fixed time 1.25; camera-only closeup after applyCase.',
        'limitations': ['Prepared frames, not continuous motion or a playthrough.',
            'In-memory storage fixture, not native persistence.',
            'LOD1/2 samples force existing body buffers into the player slot, retaining LOD0 groom; not distance selection or full crowd LOD behavior.',
            'Software WebGL capture; no FPS or physical GPU performance claim.'],
        'checks': [], 'errors': [], 'requests': [], 'captures': []}
    def save():
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    def check(name, ok):
        report['checks'].append({'name': name, 'pass': bool(ok)})
        print(('PASS ' if ok else 'FAIL ') + name, flush=True)
        if not ok:
            raise AssertionError(name)
    save()
    try:
        matrix = load_matrix(matrix_path)
        selections = cases(matrix)
        report['plannedCases'] = len(selections)
        raw = html.read_text(encoding='utf-8')
        if '<script>' not in raw:
            raise ValueError('Expected standalone script injection point')
        with sync_playwright() as pw:
            options = launch_options(['--no-sandbox', '--use-gl=angle', '--use-angle=swiftshader',
                '--enable-unsafe-swiftshader', '--disable-dev-shm-usage'])
            if args.browser:
                options['executable_path'] = str(args.browser.resolve())
            if args.headed:
                options['headless'] = False
            browser = pw.chromium.launch(**options)
            try:
                page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
                page.set_default_timeout(120000)
                page.on('pageerror', lambda e: report['errors'].append(str(e)))
                page.on('console', lambda m: report['errors'].append(m.text) if m.type == 'error' else None)
                page.on('request', lambda r: report['requests'].append(r.url) if r.url.startswith(('http:', 'https:')) else None)
                page.set_content(raw.replace('<script>', '<script>' + FIX, 1), timeout=120000)
                page.wait_for_function("!!window.DC_APP || (document.getElementById('error') && !document.getElementById('error').hidden)", timeout=120000)
                if not page.evaluate('!!window.DC_APP'):
                    raise RuntimeError('Game boot failed: ' + page.locator('#errorText').inner_text())
                page.evaluate('DC_APP.renderer.humanReady')
                page.evaluate('()=>{DC_APP.stopFrame?.();qaStopFrames();window.requestAnimationFrame=()=>0;}')
                page.wait_for_timeout(100)
                page.add_script_tag(content=stage.read_text())
                report['environment'] = {'browser': browser.version,
                    'executablePath': options.get('executable_path', 'Playwright-managed'),
                    'headless': options['headless'], **page.evaluate('DCCharacterBenchmark.init()')}
                page.evaluate('()=>{window.qaNeckBaseline={storage:JSON.stringify([...qaCharacterStorage.entries()]),live:JSON.stringify(DC_APP.sim.serialize())};}')
                for case in selections:
                    metrics = page.evaluate(CAPTURE, case)
                    image = out / 'images' / (case['id'] + '.png')
                    page.screenshot(path=str(image), timeout=120000)
                    png = image.read_bytes()
                    check('Production closeup ' + case['id'], png[:8] == b'\x89PNG\r\n\x1a\n'
                        and struct.unpack('>II', png[16:24]) == (720, 720) and len(png) > 4000
                        and metrics['storageUntouched'] and metrics['liveSimulationUntouched']
                        and metrics['bodyGeometryRestored'])
                    report['captures'].append({**case, 'label': case['sample']['label'],
                        'image': 'images/' + image.name, 'imageSha256': hashlib.sha256(png).hexdigest(),
                        'metrics': metrics})
                    save()
                page.close()
            finally:
                browser.close()
        check('All twenty-eight declared closeups captured', len(report['captures']) == 28)
        check('HTML, stage and matrix stayed unchanged', inputs['html'] == digest(html)
              and inputs['stage'] == digest(stage) and inputs['matrix'] == digest(matrix_path))
        check('No JavaScript or console errors', not report['errors'])
        check('No external runtime or fixture requests', not report['requests'])
        report['status'] = 'passed'
    except Exception as error:
        report['status'] = 'failed'
        report['failure'] = str(error)
        print('FAILED:', error, flush=True)
    finally:
        report['finishedUtc'] = datetime.now(timezone.utc).isoformat()
        save()
        (out / 'report.html').write_text(render_gallery(report, report['captures']), encoding='utf-8')
    print('REPORT:', out / 'report.json', flush=True)
    return 0 if report['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
