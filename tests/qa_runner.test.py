"""Contract tests for SPEC-001. No browser or personal profile is used."""
from pathlib import Path
import hashlib, json, os, sys, tempfile, unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.qa.config import Config
from tools.qa.run import Suite, execute_suite, run_suites

class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'src').mkdir(); (self.root/'tests').mkdir()
        (self.root/'index.html').write_text('<html>test</html>')
        self.sha = hashlib.sha256((self.root/'index.html').read_bytes()).hexdigest()
        self.cfg = Config(self.root, self.root/'artifacts'/'run-one', timeout=3)

    def suite(self, body, expected=1):
        script = self.root/'tests/probe.py'
        script.write_text(body)
        return Suite('probe', ('tests/probe.py',), 'qa/v019/probe.json', expected, 'fixture')

    def report_code(self, **extra):
        report = dict(checks=[{'pass': True}], sha256=self.sha, errors=[], requests=[])
        report.update(extra)
        return "from pathlib import Path\nPath('qa/v019').mkdir(parents=True,exist_ok=True)\nPath('qa/v019/probe.json').write_text("+repr(json.dumps(report))+")\n"

    def test_accept_fresh_success_with_exact_hash(self):
        result=run_suites(self.cfg,[self.suite(self.report_code())])
        self.assertEqual(result['status'],'passed')
        self.assertEqual(result['suites'][0]['checks'],1)
        self.assertTrue(result['runId'])
        self.assertFalse((self.root/'qa').exists())

    def test_nonzero_process_cannot_be_hidden_by_green_report(self):
        r=run_suites(self.cfg,[self.suite(self.report_code()+'raise SystemExit(7)')])
        self.assertEqual(r['status'],'failed'); self.assertEqual(r['suites'][0]['exitCode'],7)

    def test_old_report_without_execution_is_rejected(self):
        p=self.root/'qa/v019';p.mkdir(parents=True)
        old=json.dumps(dict(checks=[{'pass':True}],sha256=self.sha,errors=[],requests=[]))
        (p/'probe.json').write_text(old)
        r=run_suites(self.cfg,[self.suite('pass')])
        self.assertEqual(r['status'],'failed')
        self.assertEqual((p/'probe.json').read_text(),old)

    def test_missing_report_is_rejected(self):
        self.assertEqual(run_suites(self.cfg,[self.suite('pass')])['status'],'failed')

    def test_changed_html_fails_even_with_green_report(self):
        s=self.suite(self.report_code()+"Path('index.html').write_text('mutated')")
        r=run_suites(self.cfg,[s]); self.assertEqual(r['status'],'failed')
        self.assertEqual((self.root/'index.html').read_text(),'<html>test</html>')

    def test_wrong_hash_is_rejected(self):
        r=run_suites(self.cfg,[self.suite(self.report_code(sha256='0'*64))])
        self.assertEqual(r['status'],'failed')

    def test_timeout_is_not_success(self):
        cfg=Config(self.root,self.root/'artifacts/run-one',timeout=.15)
        r=run_suites(cfg,[self.suite('import time\ntime.sleep(4)')])
        self.assertEqual(r['suites'][0]['exitCode'],124); self.assertEqual(r['status'],'failed')

    def test_failed_or_incomplete_checks_are_rejected(self):
        for i, code in enumerate([self.report_code(checks=[{'pass':False}]),self.report_code(checks=[]) ]):
            cfg=Config(self.root,self.root/f'artifacts/run-{i}')
            self.assertEqual(run_suites(cfg,[self.suite(code)])['status'],'failed')

    def test_external_requests_and_console_errors_fail(self):
        for i, code in enumerate([self.report_code(errors=['bad']), self.report_code(requests=['https://invalid.test'])]):
            cfg=Config(self.root,self.root/f'artifacts/run-{i}')
            self.assertEqual(run_suites(cfg,[self.suite(code)])['status'],'failed')

    def test_artifact_destination_cannot_replace_source_or_leave_root(self):
        for path in [self.root,self.root/'src',self.root/'qa',self.root.parent/'outside']:
            with self.assertRaises(ValueError): Config(self.root,path).validate()

    def test_symlink_destination_escape_is_rejected(self):
        (self.root/'artifacts').symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError): Config(self.root,self.root/'artifacts/escape').validate()

    def test_existing_output_is_never_overwritten(self):
        self.cfg.output.mkdir(parents=True); p=self.cfg.output/'keep';p.write_text('preserve')
        with self.assertRaises(FileExistsError): run_suites(self.cfg,[self.suite('pass')])
        self.assertEqual(p.read_text(),'preserve')

    def test_empty_suite_selection_is_not_green(self):
        with self.assertRaises(ValueError): run_suites(self.cfg,[])

    def test_origin_mismatch_is_rejected(self):
        with self.assertRaises(ValueError): run_suites(Config(self.root,self.cfg.output,origin='http'),[self.suite('pass')])

    def test_browser_path_is_explicit_and_validated(self):
        with self.assertRaises(ValueError): Config(self.root,self.cfg.output,browser='/no/such/browser').validate()

if __name__=='__main__': unittest.main()
