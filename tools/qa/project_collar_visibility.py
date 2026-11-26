#!/usr/bin/env python3
"""Offline visibility of preserved collar probes; no rendering or runtime edits.

Normal-ray misses are not geometric holes. Reports point-ray occlusion and
on-axis triangle scale estimates separately; neither is screenshot coverage.
"""
from pathlib import Path
import argparse, collections, gzip, hashlib, json, math
import numpy as np

EPS = 1e-9


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Surface:
    def __init__(self, world):
        self.triangles = np.asarray(world, dtype=np.float64).reshape(-1, 3, 3)
        require(len(self.triangles) > 0 and np.isfinite(self.triangles).all(), 'Invalid surface')
        self.a = self.triangles[:, 0]
        self.e1 = self.triangles[:, 1] - self.a
        self.e2 = self.triangles[:, 2] - self.a

    def hit(self, origin, direction, signed=False):
        origin = np.asarray(origin); direction = np.asarray(direction)
        cross = np.cross(np.broadcast_to(direction, self.e2.shape), self.e2)
        det = np.einsum('ij,ij->i', self.e1, cross)
        delta = origin - self.a
        with np.errstate(divide='ignore', invalid='ignore'):
            u = np.einsum('ij,ij->i', delta, cross) / det
            q = np.cross(delta, self.e1)
            v = q @ direction / det
            t = np.einsum('ij,ij->i', self.e2, q) / det
        with np.errstate(invalid='ignore'):
            valid = ((np.abs(det) > 1e-12) & (u >= -EPS) & (v >= -EPS) & (u+v <= 1+EPS))
        valid &= np.abs(t) <= .12 if signed else t > 0
        ids = np.flatnonzero(valid)
        if not len(ids):
            return None
        i = int(ids[np.argmin(np.abs(t[ids]) if signed else t[ids])])
        return {'triangle': i, 'distanceM': float(t[i]), 'pointWorld': (origin+t[i]*direction).tolist()}


def project(point, camera, height=720, width=720):
    eye = np.asarray(camera['eye'], dtype=np.float64)
    f = np.asarray(camera['target'], dtype=np.float64)-eye; f /= np.linalg.norm(f)
    right = np.cross(f, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, f); delta = np.asarray(point)-eye; depth = float(delta@f)
    scale = height/(2*math.tan(camera['fov']/2))
    if depth <= 0:
        return {'inFront': False, 'withinViewport': False, 'coordinates': None, 'depthM': depth}
    x = float(width/2+scale*(delta@right)/depth); y = float(height/2-scale*(delta@up)/depth)
    return {'inFront': True, 'withinViewport': 0 <= x < width and 0 <= y < height,
            'coordinates': [x, y], 'depthM': depth}


def pixel_direction(pixel, camera, height=720, width=720):
    forward = np.asarray(camera['target'], dtype=np.float64)-camera['eye']; forward /= np.linalg.norm(forward)
    right = np.cross(forward, [0, 1, 0]); right /= np.linalg.norm(right)
    up = np.cross(right, forward); scale = height/(2*math.tan(camera['fov']/2))
    direction = forward+right*((pixel[0]+.5-width/2)/scale)-up*((pixel[1]+.5-height/2)/scale)
    return direction/np.linalg.norm(direction)


def ray_view(point, camera, surfaces):
    projection = project(point, camera)
    if not projection['inFront']:
        return projection
    eye = np.asarray(camera['eye'], dtype=np.float64); direction = np.asarray(point, dtype=np.float64)-eye
    distance = float(np.linalg.norm(direction)); direction /= distance
    hits = {name: surface.hit(eye, direction) for name, surface in surfaces.items()}
    def winner(hits, jacket):
        valid = [(name, hits[name]['distanceM']) for name in ('skin2', jacket) if hits[name]]
        return min(valid, key=lambda x: x[1])[0] if valid else 'background'
    pixel = [math.floor(x) for x in projection['coordinates']]
    centered = {name: surface.hit(eye, pixel_direction(pixel, camera)) for name, surface in surfaces.items()}
    return {**projection, 'targetDistanceM': distance, 'hits': hits,
            'beforeWinner': winner(hits, 'oldJacket2'), 'afterWinner': winner(hits, 'jacket1'),
            'sourceJacketWinnerAgainstSkin2': winner(hits, 'sourceJacket0'),
            'pixel': pixel, 'pixelCenterHits': centered,
            'beforePixelWinner': winner(centered, 'oldJacket2'), 'afterPixelWinner': winner(centered, 'jacket1')}


def analyze(before_path, after_path, clearance_path, coverage_path, output):
    files = {}
    def read(path):
        raw = path.read_bytes(); files[str(path.resolve())] = sha(raw); return raw
    before = json.loads(read(before_path)); after = json.loads(read(after_path))
    clearance = json.loads(read(clearance_path)); coverage = json.loads(read(coverage_path))
    require(coverage['beforeReportSha256'] == sha(before_path.read_bytes()) and
            coverage['afterReportSha256'] == sha(after_path.read_bytes()), 'Coverage/report mismatch')
    require(clearance['producerReportSha256'] == sha(after_path.read_bytes()), 'Clearance/report mismatch')
    require(before['cohortSha256'] == after['cohortSha256'] == clearance['cohortSha256'], 'Cohort mismatch')
    require(after['captureStatus'] == 'passed' and not after['errors'] and not after['requests'], 'Invalid captures')
    def load(report_path, capture):
        p = (report_path.parent/capture['nativeGeometry']).resolve()
        require(p.is_relative_to(report_path.parent.resolve()), 'Geometry path escape')
        raw = read(p); require(sha(raw) == capture['nativeGeometrySha256'], 'Geometry hash mismatch')
        native = json.loads(gzip.decompress(raw))
        packed = json.dumps(native, separators=(',', ':'), allow_nan=False).encode()
        require(sha(packed) == capture['geometryDataSha256'], 'Geometry data hash mismatch')
        return native
    reference_cameras = {c['id']: c['metrics']['camera'] for c in after['captures']}
    cameras = {'backCloseup': reference_cameras['neutral--idle--back--lod2'],
               'profileCloseup': reference_cameras['visual--closeup--neutral--profile'],
               'backFullbody': reference_cameras['visual--fullbody--neutral--back'],
               'frontFullbody': reference_cameras['visual--fullbody--neutral--front'],
               'profileFullbody': reference_cameras['visual--fullbody--side--profile']}
    rows = []; new_by_condition = {c['condition']: c['newlyUncoveredOutsideCoreIDs'] for c in coverage['conditions']}
    for condition, c in after['conditions'].items():
        expected_new = (set(c['sourceCoveredIDs']) & set(before['conditions'][condition]['candidateCoveredIDs'])
                        - set(c['candidateCoveredIDs']) - set(c['coreIDs']))
        require(set(new_by_condition[condition]) == expected_new and len(new_by_condition[condition]) == len(expected_new),
                'Newly uncovered IDs do not match preserved reports')
        selected = {lod: next(x for x in after['captures'] if x['case'].get('cohortFrame') and
                             x['case']['conditionId'] == condition and x['case']['bodyGeometryLOD'] == lod) for lod in (0, 1, 2)}
        old_capture = next(x for x in before['captures'] if x['id'] == selected[2]['id'])
        native = {lod: load(after_path, cap) for lod, cap in selected.items()}
        old = load(before_path, old_capture)
        require(native[2]['face'] == old['face'], 'Skin changed across policy')
        surfaces = {'skin2': Surface(native[2]['face']['world']), 'jacket1': Surface(native[1]['jacket']['world']),
                    'oldJacket2': Surface(old['jacket']['world']), 'sourceJacket0': Surface(native[0]['jacket']['world'])}
        anchors = {a['sourceTriangle']: a for a in c['posedAnchors']}
        unknown = [a['sourceTriangle'] for a in clearance['conditions'][condition]['anchors'] if a['skin2AgainstJacket2M'] is None]
        require(set(unknown) == {a['sourceTriangle'] for a in c['actualLOD2SkinClearanceDiagnostic'] if a['garmentMinusSkinM'] is None},
                'Unknown IDs do not match preserved producer diagnostic')
        source_world = np.asarray(native[0]['face']['world']).reshape(-1, 3, 3)
        for category, ids in [('newlyUncoveredOutsideCore', new_by_condition[condition]), ('unknownSkinNormalRay', unknown)]:
            for source_id in ids:
                a = anchors[source_id]; point = a['worldCenter']; skin_hit = None
                if category == 'newlyUncoveredOutsideCore':
                    skin_hit = surfaces['skin2'].hit(point, a['worldNormal'], signed=True)
                    if skin_hit: point = skin_hit['pointWorld']
                triangle = source_world[source_id]
                edge = max(float(np.linalg.norm(triangle[i]-triangle[j])) for i,j in ((0,1),(1,2),(2,0)))
                views = {name: ray_view(point, camera, surfaces) for name, camera in cameras.items()}
                for view in views.values():
                    hits = view.get('hits', {}); nearest = hits.get('skin2')
                    view['targetOnNearestSkin'] = bool(skin_hit and nearest and abs(nearest['distanceM']-view['targetDistanceM']) < 1e-7)
                    view['newlyVisibleSkinPoint'] = bool(view['withinViewport'] and view['targetOnNearestSkin'] and
                        view['beforeWinner'] == 'oldJacket2' and view['afterWinner'] == 'skin2')
                    view['newlyExposedPixelCenter'] = bool(view['withinViewport'] and view['beforePixelWinner'] == 'oldJacket2' and view['afterPixelWinner'] == 'skin2')
                for name, view in views.items():
                    projected = [project(p, cameras[name]) for p in triangle]
                    view['sourceTriangleProjectedVertices'] = [p['coordinates'] for p in projected]
                    if all(p['inFront'] for p in projected):
                        xy = np.asarray(view['sourceTriangleProjectedVertices'])
                        view['sourceTriangleMaxProjectedEdgePixels'] = max(float(np.linalg.norm(xy[i]-xy[j])) for i,j in ((0,1),(1,2),(2,0)))
                rows.append({'condition': condition, 'category': category, 'sourceTriangle': source_id,
                             'restCenter': a['restCenter'], 'sourceWorldCenter': a['worldCenter'],
                             'targetWorld': point, 'targetIsSkin2': bool(skin_hit), 'skin2NormalHit': skin_hit,
                             'sourceTriangleMaxEdgeM': edge, 'views': views})
    require(sum(r['category']=='newlyUncoveredOutsideCore' for r in rows) == 190, 'Expected frozen 190 combinations')
    require(sum(r['category']=='unknownSkinNormalRay' for r in rows) == 492, 'Expected frozen 492 combinations')
    summaries = {}
    for category in ('newlyUncoveredOutsideCore', 'unknownSkinNormalRay'):
        subset = [r for r in rows if r['category'] == category]
        summaries[category] = {'combinations': len(subset), 'uniqueSourceTriangles': len({r['sourceTriangle'] for r in subset}),
            'views': {name: {'winnerCounts': dict(collections.Counter(r['views'][name].get('afterWinner','behindCamera') for r in subset)),
                             'newlyVisibleSkinPoints': sum(r['views'][name].get('newlyVisibleSkinPoint',False) for r in subset),
                             'newlyExposedUniquePixelCentersByCondition': len({(r['condition'], *r['views'][name]['pixel']) for r in subset if r['views'][name].get('newlyExposedPixelCenter',False)}),
                             'newlyVisibleAlsoSourceJacketCovered': sum(r['views'][name].get('newlyVisibleSkinPoint',False) and r['views'][name]['sourceJacketWinnerAgainstSkin2']=='sourceJacket0' for r in subset)} for name in cameras}}
    repo = Path(__file__).resolve().parents[2]
    renderer = read(repo/'src/renderer.js').decode(); cast = read(repo/'src/cast-renderer.js').decode()
    require('fov=this.fovOverride||Math.PI*.36' in renderer and "far=this.quality==='eco'?26:43" in cast and 'distance<far*.85' in cast, 'Camera/LOD policy changed; review projection assumptions')
    scale_scenarios=[]
    for quality, far, q in [('eco',26,.65),('balanced',43,.88),('high',43,1.2)]:
        # A conservative Euclidean lower bound; may be outside the camera
        # frustum. LOD selection uses actor/player distance, NOT camera distance.
        for camera_offset in (4.3,10,17):
            minimum_distance = far*.85-camera_offset
            for dpr in (1,1.5):
                height = max(240, math.floor(720*dpr*q+.5)); factor=height/(2*math.tan(math.pi*.36/2))/minimum_distance
                scale_scenarios.append({'quality':quality,'cssViewportHeight':720,'dpr':dpr,'renderHeight':height,
                    'retainedLOD2PlayerDistanceBoundaryM':far*.85,'cameraOffsetM':camera_offset,
                    'actorOriginEuclideanCameraDistanceLowerBoundM':minimum_distance,
                    'onAxisPixelsPerMetreAtThatDistanceEstimate':factor,
                    'largestSourceTriangleEdgePixelsOnAxisEstimate':max(r['sourceTriangleMaxEdgeM'] for r in rows)*factor,
                    'projectionScope':'Transverse on-axis estimate placed at actor origin; not a global bound for triangle offsets, inclined/off-axis triangles or a captured camera.'})
    result={'schema':1,'status':'offline-diagnostic-not-acceptance','producerScriptSha256':sha(Path(__file__).read_bytes()),'inputs':files,'cameras':cameras,'summary':summaries,
            'gameProjectionScenarios':scale_scenarios,'records':rows,
            'limitations':['Only skin/jacket occlusion, excluding hair, equipment, environment and postprocessing.',
              'Continuous target rays and containing pixel-center rays are separate; sparse pixel samples are not full screenshot coverage.',
              'UNKNOWN probes target source anchors, not nonexistent confirmed skin2 intersections; no hole claim follows.',
              'Source-jacket comparison uses the current skin2 target ray; it is not a source0 raster comparison.',
              'Game pixel scales are transverse on-axis estimates for individual source triangles, not bounds on off-axis geometry or connected defect area; scenarios may be offscreen.',
              'On-foot camera offsets4.3/10m and car mode2 offset17m are scenarios; photo mode is unbounded.',
              'LOD hysteresis is player-distance based. Prepared poses do not prove motion, hardware or artistic acceptance.']}
    require(all(sha(Path(p).read_bytes())==h for p,h in files.items()), 'Input changed during analysis')
    require(not output.exists(), 'Refusing to overwrite output');output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summaries,indent=2))
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('before-report','after-report','clearance-report','coverage-report','output'):
        p.add_argument('--'+name,type=Path,required=True)
    a=p.parse_args();analyze(a.before_report,a.after_report,a.clearance_report,a.coverage_report,a.output)


if __name__=='__main__':main()
