"""A visual matrix is coverage, not an automatic approval of anatomy."""
import copy, json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa.character_matrix import load_matrix, make_cases, validate_matrix, render_gallery, accept_review
ROOT=Path(__file__).resolve().parents[1]
class MatrixTests(unittest.TestCase):
    def setUp(self): self.matrix=load_matrix(ROOT/'tests/benchmarks/characters.json')
    def test_full_cartesian_matrix_and_hair_coverage(self):
        cases=make_cases(self.matrix,'full')
        self.assertEqual(len(cases),586)
        self.assertEqual(len({c['id'] for c in cases}),586)
        self.assertEqual({c['look']['hairStyle'] for c in cases},set(range(11)))
    def test_smoke_covers_every_axis_without_claiming_full_cartesian(self):
        cases=make_cases(self.matrix,'smoke')
        self.assertEqual(len(cases),30)
        for axis in ('profile','pose','light','camera'):
            self.assertEqual({c[axis] for c in cases},set(self.matrix[axis+'s']))
    def test_construction_is_deterministic_and_independent(self):
        before=copy.deepcopy(self.matrix);a=make_cases(self.matrix,'smoke');b=make_cases(self.matrix,'smoke')
        self.assertEqual(a,b);a[0]['look']['neck']=.9
        self.assertEqual(self.matrix,before);self.assertNotEqual(a,b)
    def test_nonfinite_and_out_of_range_parameters_rejected(self):
        for v in (float('nan'),float('inf'),1.1):
            m=copy.deepcopy(self.matrix);m['profiles']['neutral']['neck']=v
            with self.assertRaises(ValueError):validate_matrix(m)
    def test_unknown_axes_and_profile_fields_are_not_silently_ignored(self):
        m=copy.deepcopy(self.matrix);m['profiles']['neutral']['neckLenght']=.2
        with self.assertRaises(ValueError):validate_matrix(m)
        m=copy.deepcopy(self.matrix);m['poses']['invented']={}
        with self.assertRaises(ValueError):validate_matrix(m)
    def test_no_untrusted_path_or_html_in_case_ids(self):
        m=copy.deepcopy(self.matrix);m['cameras']['../../escape']=m['cameras'].pop('front')
        with self.assertRaises(ValueError):validate_matrix(m)
    def test_mode_must_be_explicitly_supported(self):
        with self.assertRaises(ValueError):make_cases(self.matrix,'almost-full')
    def test_gallery_escapes_text_and_does_not_mark_art_accepted(self):
        s=render_gallery({'htmlSha256':'0'*64,'matrix':'smoke'},[{'id':'<script>x</script>','image':'images/a.png','pose':'idle','profile':'neutral','camera':'front','light':'neutral','metrics':{'glError':0}}])
        self.assertNotIn('<script>x</script>',s);self.assertIn('&lt;script&gt;',s)
        self.assertIn('Revisión artística pendiente',s)
    def test_approval_requires_real_reviewer_matching_evidence_and_decision(self):
        h='1'*64
        for value in ({},{'status':'accepted','reviewer':'','htmlSha256':h},{'status':'accepted','reviewer':'Edgar','htmlSha256':'2'*64}):
            with self.assertRaises(ValueError):accept_review(value,h)
        self.assertTrue(accept_review({'status':'accepted','reviewer':'Edgar','htmlSha256':h,'evidence':'report.html','decision':'Referencia evaluada'},h))
if __name__=='__main__':unittest.main()
