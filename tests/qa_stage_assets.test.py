"""The QA workspace must exclude historical reports, not its own QA helper modules."""
import sys,tempfile,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa.workspace import stage_workspace
class WorkspaceTests(unittest.TestCase):
    def sample(self,root):
        for name in ['index.html','tools/qa/character_matrix.py','tests/benchmarks/cases.json','src/qa/legitimate.js','qa/old.json','artifacts/old.json','.env','nested/.env.secret','node_modules/a.js']:
            p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('data')
    def test_nested_qa_code_is_retained(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)/'root';s=Path(t)/'stage';self.sample(r);stage_workspace(r,s)
            self.assertTrue((s/'tools/qa/character_matrix.py').is_file())
            self.assertTrue((s/'src/qa/legitimate.js').is_file())
            self.assertTrue((s/'tests/benchmarks/cases.json').is_file())
    def test_history_artifacts_and_secrets_are_not_copied(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)/'root';s=Path(t)/'stage';self.sample(r);stage_workspace(r,s)
            for name in ['qa','artifacts','.env','nested/.env.secret','node_modules']:
                self.assertFalse((s/name).exists(),name)
    def test_existing_workspace_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as t:
            r=Path(t)/'root';s=Path(t)/'stage';self.sample(r);s.mkdir()
            with self.assertRaises(FileExistsError):stage_workspace(r,s)
if __name__=='__main__':unittest.main()
