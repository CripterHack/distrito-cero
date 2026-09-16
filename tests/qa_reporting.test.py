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
if __name__=='__main__':unittest.main()
