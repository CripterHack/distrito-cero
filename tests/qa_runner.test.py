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


    # Literal expected names deliberately pin the producer/consumer contract.
    SIGHT_GUARD_NAMES = (
        'Embedded skin maps decode in the production renderer',
        'Translucent selector remains paused and blocks game actions',
        'Closing selection does not restore a trigger or aiming request',
        'Visual inspection never overwrites the saved catalogue',
        'No JavaScript or graphics exceptions or external requests',
    )

    def sight_report(self, partition='revolver-reload'):
        counts={'base':40,'cross-family':26,'revolver-reload':28}
        guards=[{'name':name,'pass':True} for name in self.SIGHT_GUARD_NAMES]
        count=counts[partition]
        checks=[{'name':f'continuity {i}','pass':True} for i in range(count)]
        if partition=='base':
            checks[:len(guards)]=guards
            guards=[]
        return dict(partition=partition,checks=checks,guards=guards,
                    comparisonOnly=False,sha256=self.sha,errors=[],requests=[])

    def run_sight_report(self, report, partition='revolver-reload', output='run-one'):
        probe=self.suite(self.report_code(**report))
        suite=Suite('sight-'+partition,probe.command,probe.report,
                    {'base':40,'cross-family':26,'revolver-reload':28}[partition])
        cfg=Config(self.root,self.root/'artifacts'/output,timeout=3)
        result=run_suites(cfg,[suite])
        self.assertEqual(result['suites'][0]['exitCode'],0,'Probe failure must not impersonate gate rejection.')
        return result

    def test_sight_accepts_complete_base_and_separate_guards_without_double_counting(self):
        for partition in ('base','cross-family','revolver-reload'):
            with self.subTest(partition=partition):
                report=self.sight_report(partition)
                result=self.run_sight_report(report,partition,partition)
                self.assertEqual(result['status'],'passed')
                self.assertEqual(result['suites'][0]['checks'],len(report['checks']))

    def test_comparison_report_is_not_acceptance_even_with_all_checks_passed(self):
        result=run_suites(self.cfg,[self.suite(self.report_code(comparisonOnly=True))])
        self.assertEqual(result['suites'][0]['exitCode'],0)
        self.assertEqual(result['status'],'failed')
        self.assertIn('compar',result['suites'][0]['error'].lower())

    def test_sight_failed_guard_cannot_hide_behind_exit_zero_and_green_checks(self):
        report=self.sight_report()
        report['guards'][1]['pass']=False
        result=self.run_sight_report(report)
        self.assertEqual(result['suites'][0]['exitCode'],0)
        self.assertEqual(result['status'],'failed')
        # Keep the actual rejected report, not a reconstructed success summary.
        saved=json.loads((self.cfg.output/'sight-revolver-reload.json').read_text())
        self.assertEqual(saved,report)

    def test_sight_requires_all_five_separate_guards(self):
        for i,guards in enumerate((None,[],[{'name':n,'pass':True} for n in self.SIGHT_GUARD_NAMES[:4]])):
            with self.subTest(guards=guards):
                report=self.sight_report()
                if guards is None:report.pop('guards')
                else:report['guards']=guards
                self.assertEqual(self.run_sight_report(report,output=f'missing-{i}')['status'],'failed')

    def test_sight_rejects_duplicate_and_unknown_guard_names(self):
        for i,name in enumerate((self.SIGHT_GUARD_NAMES[1],'unrelated passing guard','')):
            with self.subTest(name=name):
                report=self.sight_report();report['guards'][0]['name']=name
                self.assertEqual(self.run_sight_report(report,output=f'guard-name-{i}')['status'],'failed')

    def test_sight_rejects_malformed_guard_values_and_container(self):
        variants=(None,{},True,'passed',[None],
                  [{'name':n,'pass':1} for n in self.SIGHT_GUARD_NAMES],
                  [{'name':n,'pass':'true'} for n in self.SIGHT_GUARD_NAMES])
        for i,guards in enumerate(variants):
            with self.subTest(guards=guards):
                report=self.sight_report();report['guards']=guards
                self.assertEqual(self.run_sight_report(report,output=f'guard-type-{i}')['status'],'failed')

    def test_sight_rejects_another_or_missing_partition(self):
        for i,partition in enumerate((None,'base','all','imaginary')):
            with self.subTest(partition=partition):
                report=self.sight_report()
                if partition is None:report.pop('partition')
                else:report['partition']=partition
                self.assertEqual(self.run_sight_report(report,output=f'partition-{i}')['status'],'failed')

    def test_sight_rejects_duplicate_empty_or_missing_check_names(self):
        for i,name in enumerate(('continuity 1','',None,7)):
            with self.subTest(name=name):
                report=self.sight_report()
                if name is None:report['checks'][0].pop('name')
                else:report['checks'][0]['name']=name
                self.assertEqual(self.run_sight_report(report,output=f'check-name-{i}')['status'],'failed')

    def test_sight_base_must_contain_its_guards_in_checks_not_count_replacements(self):
        report=self.sight_report('base');report['checks'][0]['name']='unrelated passing check'
        self.assertEqual(self.run_sight_report(report,'base')['status'],'failed')

    def test_sight_base_rejects_duplicate_separate_guards(self):
        report=self.sight_report('base')
        report['guards']=[{'name':n,'pass':True} for n in self.SIGHT_GUARD_NAMES]
        self.assertEqual(self.run_sight_report(report,'base')['status'],'failed')

    def test_sight_requires_explicit_acceptance_mode(self):
        for i,mode in enumerate(('missing',True,None,'false',0)):
            with self.subTest(mode=mode):
                report=self.sight_report()
                if mode=='missing':report.pop('comparisonOnly')
                else:report['comparisonOnly']=mode
                self.assertEqual(self.run_sight_report(report,output=f'mode-{i}')['status'],'failed')

if __name__=='__main__': unittest.main()
