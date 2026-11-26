#!/usr/bin/env python3
"""Evaluate native collar captures after preserving neck detail in both jacket LODs.

Use render_collar_lod.py separately on each HTML, without its --reference
(which deliberately requires the old jacket LOD1 to remain byte-identical).
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.qa import project_collar_visibility as visibility
from tools.qa import render_collar_lod as collar

PIXELS = ROOT / 'tests/benchmarks/neckline-pixels-v02025.json'
PIXEL_SOURCE = 'a35c0f0421a9cdec461f8fa670512274264fef4e5adb1a8e8af99648a854653b'
PIXEL_ROWS_SHA256 = '04568a4c52c0f4f35fb464b82572a91d6489474293f1c32ece0c322eb7db4632'
REFERENCE_HTML = '81c9f68654e0e14eddb9cfa73f6408038120d87943bb438c7d713adf64859003'
CAMERAS = {'backCloseup': 'neutral--idle--back--lod2',
           'profileCloseup': 'visual--closeup--neutral--profile'}
# Opposite sides of the authored opening, identified in the first native review.
RESIDUAL_PIXELS = (('light/neck-right', 'backCloseup', (293, 536), 'jacket'),
                   ('light/idle', 'profileCloseup', (465, 527), 'skin'))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load_pixels(path=PIXELS):
    data = json.loads(path.read_bytes())
    require(data['sourceReportSha256'] == PIXEL_SOURCE, 'Wrong pixel provenance')
    rows = data['samples']
    require(collar.digest_data(rows) == PIXEL_ROWS_SHA256, 'Fixed pixel selection changed')
    require(len(rows) == 85 and len(set(map(tuple, rows))) == 85, 'Incomplete source pixel selection')
    conditions = {p+'/'+s for p in collar.PROFILES for s in collar.POSES}
    for condition, camera, anchor, x, y in rows:
        require(condition in conditions and camera in CAMERAS, 'Unknown pixel camera or condition')
        require(type(anchor) is int and type(x) is int and type(y) is int
                and anchor >= 0 and 0 <= x < 720 and 0 <= y < 720, 'Invalid source ID or pixel')
    return rows


def coverage_delta(source, observed):
    require(source and len(source)==len(set(source)) and len(observed)==len(set(observed)),
            'Empty source coverage or duplicate IDs')
    return {'lost': sorted(set(source)-set(observed)), 'extra': sorted(set(observed)-set(source))}


def permitted_capture_change(previous, current):
    if not (previous['id'] == current['id'] and previous['case'] == current['case'] and
            previous['metrics']['camera'] == current['metrics']['camera'] and
            previous['partGeometrySha256']['face'] == current['partGeometrySha256']['face']):
        return False
    if current['case']['bodyGeometryLOD'] == 0:
        return (previous['partGeometrySha256']['jacket'] == current['partGeometrySha256']['jacket']
                and previous['imageSha256'] == current['imageSha256'])
    return True


def clearance_summary(records, ids):
    require({r['sourceTriangle'] for r in records} >= set(ids),
            'Missing required reduced-skin clearance sample')
    chosen = [r for r in records if r['sourceTriangle'] in ids]
    margins = [r['garmentMinusSkinM'] for r in chosen if r['garmentMinusSkinM'] is not None]
    return {'tested':len(chosen), 'unknown':len(chosen)-len(margins),
            'negative':sum(m<0 for m in margins), 'minimumMm':1000*min(margins) if margins else None}


def garment_lead_mm(jacket, skin):
    if jacket is None or skin is None:
        return None
    return 1000*(skin['depthM']-jacket['depthM'])


def matches_source_winner(source_lead, candidate_lead, expected):
    if source_lead is None or candidate_lead is None:
        return False
    if expected == 'jacket':
        return source_lead > 0 and candidate_lead > 0
    return expected == 'skin' and source_lead < 0 and candidate_lead < 0


class Capture:
    def __init__(self, path, frozen):
        self.path = path.resolve()
        self.frozen = frozen
        data = self.read(self.path)
        self.report = json.loads(data)
        self.sha = sha(data)
        self.views = {c['id']: c for c in self.report['captures']}
        matrix = ROOT/'tests/benchmarks/characters.json'
        paths = {'stage': ROOT/'tools/qa/character_stage.js', 'matrix': matrix,
                 'nativeNeckHelper': Path(collar.base.__file__), 'nativeSeamHelper': Path(collar.seam.__file__),
                 'fixture': ROOT/'tests/character_benchmark.py', 'tool': Path(collar.__file__)}
        hashes = {name: sha(self.read(file)) for name,file in paths.items()}
        hashes['html'] = self.report['inputHashes']['html']
        collar.validate_reference(self.report, hashes, collar.selections(collar.base.load_matrix(matrix)))
        require(self.report['geometricStatus']=='passed' and self.report['geometricChecks']
                and all(c['pass'] is True for c in self.report['geometricChecks']),
                'The native collar capture must pass its original geometric gates')

    def read(self, path):
        data = path.read_bytes()
        digest = sha(data)
        require(self.frozen.setdefault(path, digest) == digest, 'Input changed: '+str(path))
        return data

    def artifact(self, capture, field):
        path = (self.path.parent/capture[field]).resolve()
        require(path.is_relative_to(self.path.parent), 'Artifact path escapes capture directory')
        data = self.read(path)
        require(sha(data) == capture[field+'Sha256'], 'Artifact hash mismatch: '+str(path))
        return data

    def geometry(self, capture):
        native = json.loads(gzip.decompress(self.artifact(capture, 'nativeGeometry')))
        require(set(native) == {'face','jacket'} and collar.digest_data(native) == capture['geometryDataSha256'],
                'Geometry envelope mismatch: '+capture['id'])
        for name, part in native.items():
            require(collar.digest_data(part) == capture['partGeometrySha256'][name], 'Geometry hash mismatch')
        return native

    def verify_images(self):
        for data in self.views.values():
            self.artifact(data, 'image')


def verify(candidate_path, reference_path=None):
    frozen = {p:sha(p.read_bytes()) for p in (PIXELS, Path(__file__).resolve(), Path(visibility.__file__).resolve())}
    current = Capture(candidate_path, frozen)
    current.verify_images()
    previous = None
    checks = []
    def check(name, ok):
        checks.append({'name': name, 'pass': bool(ok)})
    if reference_path:
        previous = Capture(reference_path, frozen)
        previous.verify_images()
        require(previous.report['inputHashes']['html'] == REFERENCE_HTML, 'Expected unmodified v0.20.25 HTML reference')
        require(previous.report['cohortSha256'] == current.report['cohortSha256'], 'Source cohort changed')
        require(previous.report['vertexShaderSha256'] == current.report['vertexShaderSha256'], 'Vertex shader changed')
        for key, capture in current.views.items():
            check('Only lower jacket may differ: '+key, permitted_capture_change(previous.views[key], capture))
            # Authenticate raw reference files independently of their report claims.
            previous.geometry(previous.views[key])
    samples = load_pixels()
    rows, rays, residual_pixels = {}, [], []
    cohort_ids = [a['sourceTriangle'] for a in current.report['cohort']]
    def depth(data, camera, pixel):
        with np.errstate(invalid='ignore'):
            hits = {part: collar.seam.ray_hit(data[part]['world'], camera, pixel) for part in ('jacket','face')}
        return garment_lead_mm(hits['jacket'], hits['face'])
    for condition, metrics in current.report['conditions'].items():
        group = {c['case']['bodyGeometryLOD']: c for c in current.views.values()
                 if c['case'].get('cohortFrame') and c['case']['conditionId'] == condition}
        native = {lod:current.geometry(cap) for lod,cap in group.items()}
        ids = [[i for i,probe in zip(cohort_ids,metrics['probes'][str(lod)], strict=True)
                if probe['outwardM'] is not None] for lod in (0,1,2)]
        require(ids==[metrics['sourceCoveredIDs'], metrics['lod1CoveredIDs'], metrics['candidateCoveredIDs']],
                'Source ID and probe records disagree: '+condition)
        if previous:
            require(ids[0]==previous.report['conditions'][condition]['sourceCoveredIDs'],
                    'Source coverage changed: '+condition)
        gap = coverage_delta(ids[0],ids[2])
        rows[condition] = {'source':len(ids[0]), 'candidate':len(ids[2]), **gap}
        # Excess coverage is disclosed as well. Reusing a closed/larger shell
        # would otherwise pass by covering every source anchor indiscriminately.
        check('Recover all original LOD0 covered anchors: '+condition, not gap['lost'])
        check('Preserve the authored opening: '+condition, not gap['extra'])
        check('Identical intermediate and distant coverage: '+condition, ids[1]==ids[2])
        check('Shared geometry in both native lower jacket LODs: '+condition,
              native[1]['jacket']==native[2]['jacket'])
        clearance = metrics['actualLOD2SkinClearanceDiagnostic']
        rows[condition]['skinDiagnostic'] = clearance_summary(clearance, set(metrics['coreIDs']))
        if previous:
            old_metrics = previous.report['conditions'][condition]
            common = set(old_metrics['coreIDs'])
            baseline = old_metrics['actualLOD2SkinClearanceDiagnostic']
            same_ids = common & set(metrics['coreIDs'])
            rows[condition]['priorCoreSize'] = len(common)
            rows[condition]['priorCoreInCandidate'] = len(same_ids)
            rows[condition]['priorCoreBefore'] = clearance_summary(baseline, same_ids)
            rows[condition]['priorCoreAfter'] = clearance_summary(clearance, same_ids)
            prior = previous.geometry(previous.views[group[2]['id']])
        negative_records = []
        if previous:
            surfaces = {'skin2':visibility.Surface(native[2]['face']['world']),
                        'jacket1':visibility.Surface(native[2]['jacket']['world']),
                        'oldJacket2':visibility.Surface(prior['jacket']['world']),
                        'sourceJacket0':visibility.Surface(native[0]['jacket']['world'])}
        for item in clearance:
            if item['garmentMinusSkinM'] is None or item['garmentMinusSkinM'] >= 0:
                continue
            source_id = item['sourceTriangle']
            ordinal = cohort_ids.index(source_id)
            skin_offset = item['skinOffsetM']
            source_offset = metrics['probes']['0'][ordinal]['outwardM']
            row = {'sourceTriangle':source_id, 'candidateMarginMm':1000*item['garmentMinusSkinM'],
                   'sourceJacketAgainstSameSkinMm':1000*(source_offset-skin_offset)}
            if previous:
                old_offset = old_metrics['probes']['2'][ordinal]['outwardM']
                row.update(wasInBaselineCore=source_id in common,
                           baselineJacketAgainstSameSkinMm=None if old_offset is None else 1000*(old_offset-skin_offset))
                anchor=metrics['posedAnchors'][ordinal]
                hit=np.asarray(anchor['worldCenter'])+skin_offset*np.asarray(anchor['worldNormal'])
                residual_views={}
                for case_id in [*CAMERAS.values(), 'visual--fullbody--neutral--back',
                                'visual--fullbody--neutral--front','visual--fullbody--side--profile']:
                    camera=current.views[case_id]['metrics']['camera']
                    v=visibility.ray_view(hit,camera,surfaces)
                    skin=v['hits']['skin2']
                    on_nearest=bool(skin and abs(skin['distanceM']-v['targetDistanceM'])<1e-7)
                    centered=v['pixelCenterHits']
                    visible=[(part,centered[part]['distanceM']) for part in ('skin2','sourceJacket0') if centered[part]]
                    source_pixel=min(visible,key=lambda hit:hit[1])[0] if visible else 'background'
                    residual_views[case_id]={'pixel':v['pixel'],'targetIsNearestSkin':on_nearest,
                        'sourcePixelWinner':source_pixel,
                        'oldWinner':v['beforeWinner'],'newWinner':v['afterWinner'],
                        'sourceWinner':v['sourceJacketWinnerAgainstSkin2'],
                        'oldPixelWinner':v['beforePixelWinner'],'newPixelWinner':v['afterPixelWinner'],
                        'newlyVisibleTarget':on_nearest and v['beforeWinner']=='oldJacket2' and v['afterWinner']=='skin2'}
                row['occlusionBySkinAndJacket']=residual_views
            negative_records.append(row)
        rows[condition]['negativeRecords'] = negative_records
        if previous:
            projected = [view for record in negative_records for view in record['occlusionBySkinAndJacket'].values()]
            check('Match source at projected reduced-skin clearance pixels: '+condition,
                  all(v['newPixelWinner'] == ('jacket1' if v['sourcePixelWinner']=='sourceJacket0'
                                              else v['sourcePixelWinner']) for v in projected))
        for key, view, pixel, expected in RESIDUAL_PIXELS:
            if key != condition:
                continue
            camera = current.views[CAMERAS[view]]['metrics']['camera']
            candidate_lead = depth(native[2],camera,pixel)
            source_lead = depth({'face':native[2]['face'], 'jacket':native[0]['jacket']},camera,pixel)
            residual_pixels.append({'condition':key, 'camera':view, 'pixel':list(pixel),
                                    'sourceTriangle':9352, 'expectedWinner':expected,
                                    'candidateLeadMm':candidate_lead, 'sourceJacketLeadAgainstLOD2SkinMm':source_lead})
            check(f'Preserve 9352 pixel {pixel} authored {expected} winner: {key}',
                  matches_source_winner(source_lead,candidate_lead,expected))
        for key, view, anchor, x, y in samples:
            if key != condition:
                continue
            camera = current.views[CAMERAS[view]]['metrics']['camera']
            lead = depth(native[2],camera,(x,y))
            with np.errstate(invalid='ignore'):
                source_jacket = collar.seam.ray_hit(native[0]['jacket']['world'],camera,(x,y))
                reduced_skin = collar.seam.ray_hit(native[2]['face']['world'],camera,(x,y))
            source_lead = garment_lead_mm(source_jacket,reduced_skin)
            before_lead = depth(prior,camera,(x,y)) if previous else None
            rays.append({'condition':key,'camera':view,'sourceTriangle':anchor,'pixel':[x,y],
                         'beforeLeadMm':before_lead,'candidateLeadMm':lead,'sourceJacketLeadAgainstLOD2SkinMm':source_lead})
            check(f'Authored coverage at {key} {view} {anchor}', source_lead is not None and source_lead>0)
            if previous:
                check(f'Reproduced v0.20.25 exposed skin at {key} {view} {anchor}', before_lead is not None and before_lead<0)
            check(f'Restore native depth at {key} {view} {anchor}', lead is not None and lead>0)
    # The six additional visual captures use separate camera/light conditions.
    for capture in current.views.values():
        if not capture['case'].get('cohortFrame'):
            current.geometry(capture)
    historical=[]
    for view,xy in [('backCloseup',(267,547)),('profileCloseup',(447,548))]:
        cap=current.views[CAMERAS[view]]
        current_lead=depth(current.geometry(cap),cap['metrics']['camera'],xy)
        check('Keep prior repaired ray: '+view,current_lead is not None and current_lead>0)
        historical.append({'camera':view,'pixel':list(xy),'candidateLeadMm':current_lead})
    for path,digest in frozen.items():
        require(sha(path.read_bytes())==digest,'Input changed during evaluation: '+str(path))
    return {'schema':2,'contract':'native-neckline-detail-v2', 'status':'passed' if all(c['pass'] for c in checks) else 'failed',
            'candidateReportSha256':current.sha,'candidateHtmlSha256':current.report['inputHashes']['html'],
            'referenceReportSha256':previous.sha if previous else None,
            'comparison':'external-v0.20.25' if previous else 'same-build source; external invariants not evaluated',
            'pixelFixtureSha256':sha(PIXELS.read_bytes()),'producerSha256':sha(Path(__file__).read_bytes()),
            'conditions':rows,'samples':rays,'historicalRays':historical,'residualPixels':residual_pixels,'checks':checks,
            'limitations':'Finite source-normal probes and two-surface camera rays; skin clearance diagnostics include unknowns. Prepared poses on software WebGL.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',required=True,type=Path)
    parser.add_argument('--reference',type=Path)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():
        parser.error('Output already exists')
    result=verify(args.candidate,args.reference)
    with args.output.open('x') as file:
        json.dump(result,file,indent=2,allow_nan=False)
        file.write('\n')
    passed=sum(c['pass'] for c in result['checks'])
    print(f"{result['status']}: {passed}/{len(result['checks'])} checks")
    return 0 if result['status']=='passed' else 1


if __name__=='__main__':
    raise SystemExit(main())
