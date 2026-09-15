"""Native mode must not accidentally run or relabel the storage fixtures."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa.run import select_suites
class SelectionTests(unittest.TestCase):
    def test_all_filters_by_storage_contract(self):
        self.assertEqual(len(select_suites(['all'],'fixture')),6)
        self.assertEqual([s.name for s in select_suites(['all'],'http')],['native'])
    def test_explicit_native_does_not_mislabel_fixture(self):
        with self.assertRaises(ValueError):select_suites(['handling'],'http')
        self.assertEqual(len(select_suites(['native','native'],'http')),1)
if __name__=='__main__':unittest.main()
