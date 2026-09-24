"""Native mode must not accidentally run or relabel the storage fixtures."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa.run import select_suites
class SelectionTests(unittest.TestCase):
    def test_all_filters_by_storage_contract(self):
        self.assertEqual(len(select_suites(['all'],'fixture')),15)
        self.assertEqual([s.name for s in select_suites(['all'],'http')],['release','native','reload'])
    def test_explicit_native_does_not_mislabel_fixture(self):
        with self.assertRaises(ValueError):select_suites(['handling'],'http')
        self.assertEqual(len(select_suites(['native','native'],'http')),1)
    def test_character_matrix_has_a_separate_fixed_smoke_contract(self):
        q=select_suites(['characters'],'fixture')
        self.assertEqual(q[0].expected_checks,36)
        with self.assertRaises(ValueError):select_suites(['characters'],'http')
    def test_optical_cycle_cannot_be_mislabeled_as_native_persistence(self):
        self.assertEqual(select_suites(['optical'],'fixture')[0].expected_checks,14)
        with self.assertRaises(ValueError):select_suites(['optical'],'http')
    def test_finger_surfaces_are_not_native_storage_evidence(self):
        self.assertEqual(select_suites(['fingers'],'fixture')[0].expected_checks,15)
        with self.assertRaises(ValueError):select_suites(['fingers'],'http')
    def test_thumb_contact_remains_a_graphical_fixture(self):
        self.assertEqual(select_suites(['thumbs'],'fixture')[0].expected_checks,15)
        with self.assertRaises(ValueError):select_suites(['thumbs'],'http')
    def test_sidearm_contacts_cannot_count_as_native_storage(self):
        self.assertEqual(select_suites(['sidearms'],'fixture')[0].expected_checks,20)
        with self.assertRaises(ValueError):select_suites(['sidearms'],'http')
    def test_thenar_surface_cannot_masquerade_as_native_persistence(self):
        self.assertEqual(select_suites(['thenar'],'fixture')[0].expected_checks,15)
        with self.assertRaises(ValueError):select_suites(['thenar'],'http')
    def test_release_identity_has_a_native_http_contract(self):
        self.assertEqual(select_suites(['release'],'http')[0].expected_checks,14)
        with self.assertRaises(ValueError):select_suites(['release'],'fixture')
    def test_sight_alignment_is_a_graphical_not_native_contract(self):
        self.assertEqual(select_suites(['sight'],'fixture')[0].expected_checks,26)
        with self.assertRaises(ValueError):select_suites(['sight'],'http')
    def test_reload_input_suite_requires_native_http_and_fixed_coverage(self):
        self.assertEqual(select_suites(['reload'],'http')[0].expected_checks,31)
        with self.assertRaises(ValueError):select_suites(['reload'],'fixture')
    def test_longarm_audit_is_not_a_native_or_artistic_acceptance_suite(self):
        self.assertEqual(select_suites(['longarms'],'fixture')[0].expected_checks,28)
        with self.assertRaises(ValueError):select_suites(['longarms'],'http')
    def test_equipment_handoff_is_canonical_graphics_not_native_storage(self):
        self.assertEqual(select_suites(['handoff'],'fixture')[0].expected_checks,16)
        with self.assertRaises(ValueError):select_suites(['handoff'],'http')
if __name__=='__main__':unittest.main()
