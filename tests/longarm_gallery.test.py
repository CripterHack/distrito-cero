"""Diagnostics must not imply that a currently misaligned pose is accepted."""
import copy
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
    from tools.qa.longarm_gallery import render_gallery
except ImportError:
    render_gallery = None

class GalleryTests(unittest.TestCase):
    def record(self):
        return {'sha256':'abc','status':'passed','cases':[{'name':'rifle-neutral',
                'image':'images/rifle-neutral.png','measurement':{'eyeError':.2,'stockError':.01},
                'screening':{'status':'needs-coordination','failures':['eye']}}]}
    def test_writer_exists(self):
        self.assertTrue(callable(render_gallery))
    def test_diagnostic_success_never_claims_artistic_acceptance(self):
        text=render_gallery(self.record())
        self.assertIn('CONTACT-03 pendiente',text)
        self.assertIn('needs-coordination',text)
        self.assertIn('200.00 mm',text)
    def test_images_stay_local_and_cannot_escape_the_gallery(self):
        for path in ['https://example.org/a.png','../outside.png','images/../../a.png','images/a.png" onerror="x']:
            record=self.record();record['cases'][0]['image']=path
            with self.assertRaises(ValueError):render_gallery(record)
    def test_labels_are_escaped_and_input_is_never_mutated(self):
        record=self.record();record['cases'][0]['name']='<script>bad()</script>';before=copy.deepcopy(record)
        text=render_gallery(record)
        self.assertNotIn('<script>',text);self.assertIn('&lt;script&gt;',text)
        self.assertEqual(record,before)
if __name__=='__main__':unittest.main()
