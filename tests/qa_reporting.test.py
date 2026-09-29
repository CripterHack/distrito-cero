"""Failure diagnostics must expose fresh causes without accepting or rerunning failures."""
import sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
try:
    from tools.qa.reporting import failure_summary
except ImportError:
    failure_summary=None
class ReportingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.log=Path(self.temp.name)/'handling.log'
        self.entry={'suite':'handling','status':'failed','exitCode':1,'expectedChecks':51,'error':'Producer failed or timed out. See its log.'}
    def test_failed_producer_traceback_is_visible(self):
        self.log.write_text('PASS early check\nTraceback\nTypeError: invalid disposed renderer\n')
        text=failure_summary(self.entry,self.log)
        self.assertIn('handling',text);self.assertIn('51',text);self.assertIn('TypeError',text)
    def test_missing_log_does_not_hide_original_failure(self):
        text=failure_summary(self.entry,self.log)
        self.assertIn('Producer failed',text);self.assertIn('unavailable',text)
    def test_output_is_bounded_and_preserves_the_tail(self):
        self.log.write_text('x'*300000+'\nlast frame exception\n')
        text=failure_summary(self.entry,self.log)
        self.assertLess(len(text),18000);self.assertIn('last frame exception',text)
    def test_workflow_command_and_control_characters_are_not_replayed(self):
        self.log.write_bytes(b'::error::forged\r\x1b[31mred\x1b[0m\n')
        text=failure_summary(self.entry,self.log)
        self.assertNotIn('::',text);self.assertNotIn('\x1b',text);self.assertNotIn('\r',text)
    def test_success_has_no_failure_summary_or_log_read(self):
        self.entry['status']='passed';self.assertEqual(failure_summary(self.entry,self.log),'')
try:
    from tools.qa.sight_timing import SightTiming
except ImportError:
    SightTiming=None

class SightTimingTests(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(SightTiming, 'QA timing collector is not implemented')
        self.now=0;self.messages=[]
        self.timer=SightTiming(clock=lambda:self.now, emit=self.messages.append)
    def advance(self,n):self.now+=n
    def test_returns_original_value_once_and_preserves_arguments(self):
        value=[];calls=[]
        def work(arg,*,other):
            calls.append((arg,other));self.advance(25_000_000);return value
        with self.timer.section('exchange'):
            self.assertIs(self.timer.call('evaluate',work,value,other=value),value)
        self.assertEqual(calls,[(value,value)])
        section=self.timer.snapshot()['sections'][0]
        self.assertEqual(section['durationSeconds'],.025)
        self.assertEqual(section['operations']['evaluate'],dict(calls=1,failures=0,seconds=.025,maximumSeconds=.025))
    def test_rethrows_original_exception_and_logs_failed_section(self):
        failure=ValueError('graphics lost');calls=[]
        def work():calls.append(1);self.advance(1_000_000);raise failure
        with self.assertRaises(ValueError) as caught:
            with self.timer.section('broken'):self.timer.call('evaluate',work)
        self.assertIs(caught.exception,failure);self.assertEqual(calls,[1])
        section=self.timer.snapshot()['sections'][0]
        self.assertEqual(section['status'],'failed')
        self.assertEqual(section['operations']['evaluate']['failures'],1)
        self.assertIn('failed',self.messages[-1])
    def test_sections_and_snapshots_are_independent(self):
        for name in ['one','two']:
            with self.timer.section(name):self.timer.call('screenshot',self.advance,2_000_000)
        snapshot=self.timer.snapshot();snapshot['sections'][0]['name']='changed'
        self.assertEqual([s['name'] for s in self.timer.snapshot()['sections']],['one','two'])
        self.assertTrue(snapshot['diagnosticOnly']);self.assertFalse(snapshot['physicalGpu'])
    def test_section_start_is_flushed_before_a_possible_kill(self):
        with self.timer.section('long'):
            self.assertIn('start',self.messages[-1]);self.advance(4_000_000)
        self.assertIn('completed',self.messages[-1])
    def test_browser_times_are_kept_separate_from_host_wall_time(self):
        with self.timer.section('case'):
            self.timer.browser({'render':{'calls':2,'failures':0,'milliseconds':30,'maximumMilliseconds':20}})
            self.advance(40_000_000)
        row=self.timer.snapshot()['sections'][0]
        self.assertEqual(row['durationSeconds'],.04)
        self.assertEqual(row['browser']['render']['milliseconds'],30)
    def test_environment_description_is_copied_and_never_an_acceptance_result(self):
        self.assertTrue(hasattr(self.timer,'describe'),'Environment metadata is missing')
        value={'logical':4};self.timer.describe(cpu=value, browser='test browser')
        value['logical']=99
        snapshot=self.timer.snapshot();self.assertEqual(snapshot['environment']['cpu']['logical'],4)
        snapshot['environment']['cpu']['logical']=88
        self.assertEqual(self.timer.snapshot()['environment']['cpu']['logical'],4)
        self.assertTrue(snapshot['diagnosticOnly'])

    def test_nested_sections_and_unscoped_operations_are_rejected(self):
        with self.assertRaises(ValueError):self.timer.call('evaluate',lambda:None)
        with self.timer.section('one'):
            with self.assertRaises(ValueError):
                with self.timer.section('nested'):pass

if __name__=='__main__':unittest.main()

