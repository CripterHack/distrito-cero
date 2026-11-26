"""Synthetic policy regressions. Native captures supply the integration evidence."""
from pathlib import Path
import sys
import json
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.qa import verify_neckline_detail as detail


class NecklineDetailTests(unittest.TestCase):
    def test_missing_any_source_anchor_fails_even_when_another_is_gained(self):
        result = detail.coverage_delta([3, 7], [3, 9])
        self.assertEqual(result, {'lost': [7], 'extra': [9]})

    def test_empty_or_duplicate_source_and_duplicate_candidate_are_invalid(self):
        for source, candidate in [([], [3]), ([3, 3], [3]), ([3], [7, 7])]:
            with self.subTest(source=source, candidate=candidate):
                with self.assertRaises(ValueError):
                    detail.coverage_delta(source, candidate)

    def test_frozen_rays_include_two_views_of_anchor_9216(self):
        samples = detail.load_pixels()
        self.assertEqual(len(samples), 85)
        self.assertEqual(len({(s[0], s[1], s[3], s[4]) for s in samples}), 84)
        self.assertIn(['neutral/idle', 'backCloseup', 9216, 263, 524], samples)
        self.assertIn(['neutral/idle', 'profileCloseup', 9216, 406, 533], samples)

    def test_valid_but_reselected_pixel_is_rejected(self):
        payload=json.loads(detail.PIXELS.read_bytes())
        payload['samples'][0][3]+=1
        with tempfile.TemporaryDirectory() as folder:
            altered=Path(folder)/'pixels.json'
            altered.write_text(json.dumps(payload))
            with self.assertRaisesRegex(ValueError,'Fixed pixel selection'):
                detail.load_pixels(altered)

    def test_only_lod0_image_and_jacket_and_all_skin_are_immutable(self):
        base = dict(id='frame', case={'bodyGeometryLOD': 1}, metrics={'camera':{}},
                    imageSha256='old',partGeometrySha256={'face':'f','jacket':'j'})
        import copy
        changed=copy.deepcopy(base)
        changed['imageSha256']='new'
        changed['partGeometrySha256']['jacket']='different'
        self.assertTrue(detail.permitted_capture_change(base, changed))
        changed['partGeometrySha256']['face']='different'
        self.assertFalse(detail.permitted_capture_change(base, changed))
        changed['partGeometrySha256']['face']='f'
        base['case']['bodyGeometryLOD']=changed['case']['bodyGeometryLOD']=0
        self.assertFalse(detail.permitted_capture_change(base, changed))

    def test_residual_pixel_winner_must_match_source_and_explicit_opening(self):
        self.assertTrue(detail.matches_source_winner(.028, .028, 'jacket'))
        self.assertFalse(detail.matches_source_winner(.028, -.110, 'jacket'))
        self.assertTrue(detail.matches_source_winner(-.787, -.787, 'skin'))
        self.assertFalse(detail.matches_source_winner(.021, .075, 'skin'))
        for missing, tied in [(None, 0.1), (-0.2, None), (0.0, 0.1)]:
            self.assertFalse(detail.matches_source_winner(missing, tied, 'jacket'))

    def test_clearance_requires_distinct_front_depths_and_both_hits(self):
        self.assertIsNone(detail.garment_lead_mm(None, {'depthM':1.}))
        self.assertEqual(detail.garment_lead_mm({'depthM':1.}, {'depthM':1.}), 0.)
        self.assertAlmostEqual(detail.garment_lead_mm({'depthM':.8}, {'depthM':1.}), 200.)


if __name__ == '__main__':
    unittest.main()
