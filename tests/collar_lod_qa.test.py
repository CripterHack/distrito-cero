#!/usr/bin/env python3
"""Contracts for collar coverage evidence; these tests do not render WebGL."""
from pathlib import Path
import copy
import contextlib
import hashlib
import io
import json
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.qa import render_collar_lod as qa


def source_triangles():
    """Two outward collar triangles, four intentionally excluded triangles."""
    small = np.array([[-.003, 1.450, -.06], [-.003, 1.459, -.06], [.006, 1.450, -.06]])
    large = np.array([[-.006, 1.455, -.06], [-.006, 1.473, -.06], [.012, 1.455, -.06]])
    return np.array([
        small,
        small + [0, .2, 0],       # Above the source rest band.
        small + [.25, 0, 0],      # Outside its radial limit.
        small[::-1],             # Inward-facing geometry.
        large,
        np.repeat(small[:1], 3, axis=0),
    ])


class CollarMetricsTest(unittest.TestCase):
    def test_cohort_uses_source_rest_region_and_stable_triangle_ids(self):
        cohort = qa.make_cohort(source_triangles())
        self.assertEqual([a['sourceTriangle'] for a in cohort], [0, 4])
        for anchor in cohort:
            self.assertEqual(anchor['barycentric'], [1 / 3] * 3)
            np.testing.assert_allclose(anchor['restNormal'], [0, 0, -1], atol=1e-14)
        np.testing.assert_allclose(cohort[0]['restCenter'], [0, 1.453, -.06], atol=1e-14)
        self.assertAlmostEqual(cohort[0]['restAreaM2'], .0000405)
        self.assertAlmostEqual(cohort[1]['restAreaM2'], .000162)

    def test_anchors_follow_world_triangles_without_reselecting_rest_cohort(self):
        rest = source_triangles()
        cohort = qa.make_cohort(rest)
        world = np.stack([rest[:, :, 2] + 3, rest[:, :, 1] + 4,
                          -rest[:, :, 0] + 5], axis=-1)
        placed = qa.place_anchors(cohort, world)
        self.assertEqual([a['sourceTriangle'] for a in placed], [0, 4])
        np.testing.assert_allclose(placed[0]['worldCenter'], [2.94, 5.453, 5], atol=1e-14)
        for actual, source in zip(placed, cohort):
            np.testing.assert_allclose(actual['worldNormal'], [-1, 0, 0], atol=1e-14)
            self.assertEqual(actual['restAreaM2'], source['restAreaM2'])
            self.assertEqual(actual['barycentric'], source['barycentric'])

    def test_empty_invalid_and_nonfinite_source_cannot_create_a_cohort(self):
        outside = source_triangles()[1:2]
        nonfinite = source_triangles()
        nonfinite[0, 0, 0] = float('nan')
        for value in ([], [1, 2], outside, nonfinite):
            with self.subTest(value=str(value)[:60]):
                with self.assertRaises(ValueError):
                    qa.make_cohort(value)

    def test_nonfinite_or_collapsed_world_anchors_cannot_be_evidence(self):
        cohort = qa.make_cohort(source_triangles())
        nonfinite = source_triangles()
        nonfinite[0, 0, 0] = float('inf')
        collapsed = source_triangles()
        collapsed[0] = collapsed[0, 0]
        for value in (nonfinite, collapsed):
            with self.subTest(kind='nonfinite' if value is nonfinite else 'collapsed'):
                with self.assertRaises(ValueError):
                    qa.place_anchors(cohort, value)

    def test_normal_probe_separates_inward_outward_and_local_range(self):
        def plane(z):
            return [[-.1, -.1, z], [.1, -.1, z], [0, .1, z]]

        triangles = np.array([plane(-.02), plane(.03), plane(.13)])
        probe = qa.normal_probe([0, 0, 0], [0, 0, 1], triangles)
        self.assertAlmostEqual(probe['inwardM'], .02)
        self.assertEqual(probe['inwardTriangle'], 0)
        self.assertAlmostEqual(probe['outwardM'], .03)
        self.assertEqual(probe['outwardTriangle'], 1)
        reversed_winding = qa.normal_probe([0, 0, 0], [0, 0, 1], triangles[:, ::-1])
        self.assertEqual(probe, reversed_winding)
        uncovered = qa.normal_probe([0, 0, 0], [0, 0, 1], triangles[[0, 2]])
        self.assertIsNone(uncovered['outwardM'])
        self.assertIsNone(uncovered['outwardTriangle'])
        self.assertAlmostEqual(uncovered['inwardM'], .02)

    def test_coverage_weights_source_triangle_area_and_preserves_ids(self):
        cohort = qa.make_cohort(source_triangles())
        probes = [dict(outwardM=.01), dict(outwardM=None)]
        summary = qa.coverage_summary(cohort, probes, [0, 4])
        self.assertEqual(summary['anchors'], 2)
        self.assertEqual(summary['lostAnchors'], 1)
        self.assertEqual(summary['lostSourceTriangleIDs'], [4])
        self.assertAlmostEqual(summary['referenceAreaM2'], .0002025)
        self.assertAlmostEqual(summary['lostAreaM2'], .000162)
        self.assertAlmostEqual(summary['lostAreaM2'] / summary['referenceAreaM2'], .8)
        # The LOD0+1 core is additional evidence, not a replacement for source coverage.
        core = qa.coverage_summary(cohort, probes, [0])
        self.assertEqual(core['lostAnchors'], 0)
        self.assertEqual(summary['lostAnchors'], 1)

    def test_one_lost_core_anchor_fails_even_when_other_anchors_gain_coverage(self):
        self.assertEqual(qa.fixed_core_failures([0, 4], [0, 7, 8, 9]), [4])
        self.assertEqual(qa.fixed_core_failures([4, 0], [4, 0, 7]), [])
        with self.assertRaises(ValueError):
            qa.fixed_core_failures([], [0, 7, 8, 9])

    def test_coverage_rejects_empty_duplicate_unknown_and_incomplete_references(self):
        cohort = qa.make_cohort(source_triangles())
        probes = [dict(outwardM=.01), dict(outwardM=None)]
        for ids, results in (([], probes), ([0, 0], probes), ([1], probes), ([0, 4], probes[:1])):
            with self.subTest(ids=ids, count=len(results)):
                with self.assertRaises(ValueError):
                    qa.coverage_summary(cohort, results, ids)
        with self.assertRaises(ValueError):
            qa.fixed_core_failures([0, 0], [0])

    def test_declared_cases_cover_four_profiles_three_poses_and_all_body_lods(self):
        matrix = qa.base.load_matrix(qa.ROOT / 'tests/benchmarks/characters.json')
        cases = qa.selections(matrix)
        self.assertEqual(len(cases), 42)
        self.assertEqual(len({c['id'] for c in cases}), 42)
        cohort_cases = [c for c in cases if c['cohortFrame']]
        actual = {(c['profile'], c['pose'], c['bodyGeometryLOD']) for c in cohort_cases}
        expected = {(profile, pose, lod)
                    for profile in ('neutral', 'light', 'robust', 'extreme')
                    for pose in ('idle', 'neck-left', 'neck-right') for lod in (0, 1, 2)}
        self.assertEqual(len(cohort_cases), 36)
        self.assertEqual(actual, expected)
        self.assertTrue(all(c['camera'] == 'back' and c['light'] == 'neutral' for c in cohort_cases))
        self.assertEqual(sum(c['framing'] == 'fullbody' for c in cases), 4)


class CollarReferenceTest(unittest.TestCase):
    """Synthetic records exercise validation only; no images or GPU evidence are claimed."""

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='collar-reference-test-')
        self.addCleanup(self.temporary.cleanup)
        self.path = Path(self.temporary.name) / 'reference.json'
        self.planned = qa.selections(qa.base.load_matrix(qa.ROOT / 'tests/benchmarks/characters.json'))
        self.inputs = {name: hashlib.sha256(name.encode()).hexdigest() for name in (
            'html', 'stage', 'matrix', 'nativeNeckHelper', 'nativeSeamHelper', 'fixture', 'tool')}
        # Valid synthetic metadata, not a substitute for the runtime's source-SHA check.
        source = source_triangles()[0]
        cohort = qa.make_cohort(np.repeat(source[None, :, :], 611, axis=0))
        self.reference = {
            'schema': 1, 'contract': qa.CONTRACT,
            'captureStatus': 'passed', 'geometricStatus': 'failed',
            'inputHashes': copy.deepcopy(self.inputs), 'errors': [], 'requests': [],
            'cameraContract': {'closeup': copy.deepcopy(qa.base.CAMERA),
                               'fullbody': {'targetY': .93, 'distance': 3.3, 'eyeOffsetY': .10, 'fov': .62}},
            'viewport': copy.deepcopy(qa.base.VIEWPORT),
            'vertexShaderSha256': hashlib.sha256(b'synthetic test shader identity').hexdigest(),
            'sourceRestSha256': qa.SOURCE_REST_SHA256,
            'cohort': cohort, 'cohortSha256': qa.digest_data(cohort),
            'captureChecks': [{'name': 'Synthetic fixture guards', 'pass': True}],
            'captures': [{
                'id': case['id'], 'case': copy.deepcopy(case),
                'imageSha256': hashlib.sha256((case['id'] + ':image').encode()).hexdigest(),
                'nativeGeometrySha256': hashlib.sha256((case['id'] + ':geometry').encode()).hexdigest(),
                'geometryDataSha256': hashlib.sha256((case['id'] + ':data').encode()).hexdigest(),
                'partGeometrySha256': {part: hashlib.sha256((case['id'] + ':' + part).encode()).hexdigest()
                                       for part in ('face', 'jacket')},
                'metrics': {'camera': {'eye': [0, 0, 0], 'target': [0, 0, -1], 'fov': .62},
                            'storageUntouched': True, 'liveSimulationUntouched': True,
                            'bodyGeometryRestored': True, 'drawMethodRestored': True,
                            'glError': 0, 'cullAtDraw': [False]},
            } for case in self.planned],
            'conditions': {profile + '/' + pose: {
                'sourceCoveredIDs': [0, 4, 8], 'lod1CoveredIDs': [0, 4, 12], 'coreIDs': [0, 4],
            } for profile in ('neutral', 'light', 'robust', 'extreme')
              for pose in ('idle', 'neck-left', 'neck-right')},
        }

    def validate(self, reference):
        return qa.validate_reference(reference, self.inputs, self.planned)

    def test_complete_baseline_with_failed_geometry_is_a_valid_fixed_reference(self):
        result = self.validate(self.reference)
        self.assertEqual(result['captureStatus'], 'passed')
        self.assertEqual(result['geometricStatus'], 'failed')
        self.assertEqual(len(result['conditions']), 12)

    def test_face_invariance_allows_jacket_changes_but_rejects_changed_skin(self):
        reference = self.reference['captures'][2]
        candidate = copy.deepcopy(reference)
        candidate['partGeometrySha256']['jacket'] = hashlib.sha256(b'changed jacket').hexdigest()
        qa.validate_face_invariance(candidate, reference)
        candidate['partGeometrySha256']['face'] = hashlib.sha256(b'changed face').hexdigest()
        with self.assertRaises(ValueError):
            qa.validate_face_invariance(candidate, reference)

    def test_empty_or_malformed_references_are_rejected(self):
        for value in ({}, [], None, False, {'schema': 1}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.validate(value)
        self.path.write_bytes(b'{ invalid json')
        with self.assertRaises(ValueError):
            qa.snapshot_reference(self.path, self.inputs, self.planned)

    def test_incomplete_duplicate_or_changed_capture_scenarios_are_rejected(self):
        edits = {
            'missing': lambda r: r['captures'].pop(),
            'extra': lambda r: r['captures'].append(copy.deepcopy(r['captures'][0])),
            'duplicate-id': lambda r: r['captures'][1].update(id=r['captures'][0]['id']),
            'different-pose': lambda r: r['captures'][0]['case'].update(pose='uncaptured-pose'),
            'different-clock': lambda r: r['captures'][0]['case'].update(time=999),
            'missing-image-hash': lambda r: r['captures'][0].pop('imageSha256'),
            'invalid-geometry-hash': lambda r: r['captures'][0].update(nativeGeometrySha256='bad'),
            'invalid-data-hash': lambda r: r['captures'][0].update(geometryDataSha256='bad'),
            'storage-mutated': lambda r: r['captures'][0]['metrics'].update(storageUntouched=False),
            'simulation-mutated': lambda r: r['captures'][0]['metrics'].update(liveSimulationUntouched=False),
            'body-not-restored': lambda r: r['captures'][0]['metrics'].update(bodyGeometryRestored=False),
            'draw-not-restored': lambda r: r['captures'][0]['metrics'].update(drawMethodRestored=False),
            'culling-enabled': lambda r: r['captures'][0]['metrics'].update(cullAtDraw=[True]),
            'culling-nonboolean': lambda r: r['captures'][0]['metrics'].update(cullAtDraw=['']),
            'culling-empty': lambda r: r['captures'][0]['metrics'].update(cullAtDraw=[]),
            'gl-error': lambda r: r['captures'][0]['metrics'].update(glError=1280),
        }
        for name, edit in edits.items():
            with self.subTest(name=name):
                reference = copy.deepcopy(self.reference)
                edit(reference)
                with self.assertRaises(ValueError):
                    self.validate(reference)

    def test_cohort_and_core_cannot_be_emptied_or_selected_from_candidate_failures(self):
        def condition(reference):
            return reference['conditions']['neutral/idle']

        edits = {
            'empty-cohort': lambda r: r.update(cohort=[]),
            'incomplete-cohort': lambda r: r['cohort'].pop(),
            'duplicate-anchor': lambda r: r['cohort'][1].update(sourceTriangle=0),
            'anchor-out-of-range': lambda r: r['cohort'][0].update(sourceTriangle=9672),
            'anchor-not-integer': lambda r: r['cohort'][0].update(sourceTriangle=True),
            'changed-barycentric': lambda r: r['cohort'][0].update(barycentric=[1, 0, 0]),
            'nonfinite-area': lambda r: r['cohort'][0].update(restAreaM2=float('nan')),
            'zero-area': lambda r: r['cohort'][0].update(restAreaM2=0),
            'nonfinite-normal': lambda r: r['cohort'][0].update(restNormal=[0, 0, float('inf')]),
            'changed-cohort-sha': lambda r: r.update(cohortSha256='a' * 64),
            'missing-condition': lambda r: r['conditions'].pop('extreme/neck-right'),
            'extra-condition': lambda r: r['conditions'].update(unplanned=copy.deepcopy(condition(r))),
            'empty-source': lambda r: condition(r).update(sourceCoveredIDs=[]),
            'empty-lod1': lambda r: condition(r).update(lod1CoveredIDs=[]),
            'empty-core': lambda r: condition(r).update(coreIDs=[]),
            'duplicate-core': lambda r: condition(r).update(coreIDs=[0, 0, 4]),
            'unknown-core-anchor': lambda r: condition(r).update(coreIDs=[0, 999]),
            'shrunken-core': lambda r: condition(r).update(coreIDs=[0]),
            'source-only-in-core': lambda r: condition(r).update(coreIDs=[0, 4, 8]),
            'lod1-only-in-core': lambda r: condition(r).update(coreIDs=[0, 4, 12]),
        }
        for name, edit in edits.items():
            with self.subTest(name=name):
                reference = copy.deepcopy(self.reference)
                edit(reference)
                if name not in ('changed-cohort-sha', 'nonfinite-area', 'nonfinite-normal'):
                    # Isolate structural guards rather than rejecting only a stale checksum.
                    reference['cohortSha256'] = qa.digest_data(reference['cohort'])
                with self.assertRaises(ValueError):
                    self.validate(reference)

    def test_source_helper_identity_and_capture_guards_are_required(self):
        edits = {
            'schema': lambda r: r.update(schema=2),
            'schema-bool': lambda r: r.update(schema=True),
            'contract': lambda r: r.update(contract='unrelated-contract'),
            'capture-failed': lambda r: r.update(captureStatus='failed'),
            'geometry-status-absent': lambda r: r.pop('geometricStatus'),
            'geometry-status-unknown': lambda r: r.update(geometricStatus='unreviewed'),
            'camera-contract': lambda r: r.update(cameraContract={}),
            'viewport': lambda r: r.update(viewport={'width': 1, 'height': 1}),
            'shader-sha': lambda r: r.update(vertexShaderSha256='bad'),
            'runtime-error': lambda r: r.update(errors=['WebGL failed']),
            'external-request': lambda r: r.update(requests=['https://example.invalid/asset']),
            'empty-checks': lambda r: r.update(captureChecks=[]),
            'failed-check': lambda r: r.update(captureChecks=[{'name': 'guard', 'pass': False}]),
            'source-sha': lambda r: r.update(sourceRestSha256='a' * 64),
        }
        for key in self.inputs:
            edits['malformed-' + key] = lambda r, key=key: r['inputHashes'].update({key: 'bad'})
            if key != 'html':
                edits['changed-' + key] = lambda r, key=key: r['inputHashes'].update({key: 'a' * 64})
        for name, edit in edits.items():
            with self.subTest(name=name):
                reference = copy.deepcopy(self.reference)
                edit(reference)
                with self.assertRaises(ValueError):
                    self.validate(reference)

    def test_exact_reference_bytes_are_snapshotted_and_mutation_is_rejected(self):
        raw = json.dumps(self.reference, indent=2).encode() + b'\n'
        self.path.write_bytes(raw)
        reference, sha = qa.snapshot_reference(self.path, self.inputs, self.planned)
        self.assertEqual(reference, self.reference)
        self.assertEqual(sha, hashlib.sha256(raw).hexdigest())
        qa.require_reference_unchanged(self.path, sha)
        # Semantically identical JSON is still different evidence bytes.
        self.path.write_bytes(json.dumps(self.reference, separators=(',', ':')).encode())
        with self.assertRaisesRegex(ValueError, '[Rr]eference.*changed'):
            qa.require_reference_unchanged(self.path, sha)

    @contextlib.contextmanager
    def cli_fixture(self, on_capture=None):
        """Browser adapter tests producer orchestration, never renderer correctness."""
        (qa.ROOT / 'artifacts').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=qa.ROOT / 'artifacts', prefix='collar-cli-test-') as temporary:
            directory = Path(temporary)
            html = directory / 'fixture.html'
            html.write_text('<script></script>')
            self.path = directory / 'reference.json'
            self.output = directory / 'output'
            paths = {'html': html, 'stage': qa.ROOT / 'tools/qa/character_stage.js',
                     'matrix': qa.ROOT / 'tests/benchmarks/characters.json',
                     'nativeNeckHelper': Path(qa.base.__file__), 'nativeSeamHelper': Path(qa.seam.__file__),
                     'fixture': qa.ROOT / 'tests/character_benchmark.py', 'tool': Path(qa.__file__)}
            self.reference['inputHashes'] = {key: qa.base.digest(path) for key, path in paths.items()}
            self.path.write_text(json.dumps(self.reference))
            owner = self
            png = b'\x89PNG\r\n\x1a\n' + b'\0' * 8 + struct.pack('>II', 720, 720)

            class Page:
                captures = 0

                def set_default_timeout(self, *args): pass
                def on(self, *args): pass
                def set_content(self, *args, **kwargs): pass
                def wait_for_function(self, *args, **kwargs): pass
                def wait_for_timeout(self, *args): pass
                def add_script_tag(self, *args, **kwargs): pass
                def close(self): pass
                def screenshot(self, path, **kwargs): Path(path).write_bytes(png)

                def evaluate(self, script, arg=None):
                    if script == qa.CAPTURE:
                        if on_capture:
                            on_capture(self.captures)
                        self.captures += 1
                        metrics = copy.deepcopy(owner.reference['captures'][0]['metrics'])
                        geometry = {'rest': [0, 0, 0] * 3, 'world': [0, 0, 0] * 3, 'count': 3}
                        return {**metrics, 'geometry': {'face': copy.deepcopy(geometry), 'jacket': geometry},
                                'vertexShader': 'synthetic test shader identity'}
                    return {} if script == 'DCCharacterBenchmark.init()' else True

            class Browser:
                version = 'Test adapter; no browser launched'

                def new_page(self, **kwargs): return Page()
                def close(self): pass

            class Playwright:
                def __init__(self): self.chromium = self
                def __enter__(self): return self
                def __exit__(self, *args): pass
                def launch(self, **kwargs): return Browser()

            argv = ['render_collar_lod.py', '--html', str(html), '--output', str(self.output),
                    '--label', 'Synthetic orchestration test', '--reference', str(self.path)]
            with patch.object(sys, 'argv', argv), patch.object(qa, 'sync_playwright', Playwright), \
                 patch.object(qa.base, 'launch_options', return_value={'headless': True}), \
                 contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                yield

    def test_invalid_reference_is_rejected_before_browser_or_output_creation(self):
        with self.cli_fixture():
            self.path.write_text('{}')
            with patch.object(qa, 'sync_playwright') as browser:
                with self.assertRaises(ValueError):
                    qa.main()
                browser.assert_not_called()
            self.assertFalse(self.output.exists())

    def test_reference_mutation_during_capture_or_analysis_invalidates_the_result(self):
        for phase in ('capture', 'analysis'):
            with self.subTest(phase=phase):
                def mutate():
                    self.path.write_bytes(self.path.read_bytes() + b'\n')

                def captured(index):
                    if phase == 'capture' and index == 0:
                        mutate()

                def analyzed(report, native, reference):
                    report['geometricChecks'] = [{'name': 'Synthetic acceptance for orchestration', 'pass': True}]
                    report['geometricStatus'] = 'passed'
                    if phase == 'analysis':
                        mutate()

                with self.cli_fixture(captured):
                    original_hash = qa.base.digest(self.path)
                    with patch.object(qa, 'analyze', side_effect=analyzed):
                        with self.assertRaisesRegex(ValueError, '[Rr]eference.*changed'):
                            qa.main()
                    report = json.loads((self.output / 'report.json').read_text())
                    self.assertEqual(report['captureStatus'], 'failed')
                    self.assertNotEqual(report['geometricStatus'], 'passed')
                    self.assertEqual(report['referenceReportSha256'], original_hash)
                    self.assertNotEqual(original_hash, qa.base.digest(self.path))
                    self.assertRegex(report['failure'], '[Rr]eference.*changed')


if __name__ == '__main__':
    unittest.main()
