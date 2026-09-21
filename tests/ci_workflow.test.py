"""Protect this repository's CI gate layout, not a general YAML parser.
No extra dependency is needed on the Python-only core runner.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
READY = "${{ !cancelled() && steps.checkout.outcome == 'success' && steps.node.outcome == 'success' && steps.python.outcome == 'success' }}"
NODE = 'node --test tests/*.test.cjs'
COMMANDS = [
    'python3 tools/refine_thenar.py --check',
    'python3 tests/thenar_contour.test.py',
    'python3 tools/rebind_garment.py --check',
    'python3 tests/garment_binding.test.py',
    'python3 build.py --check',
    'python3 tests/release_build.test.py',
    'python3 tests/release_checkout.test.py',
    NODE,
    'python3 tests/qa_runner.test.py',
    'python3 tests/qa_reporting.test.py',
    'python3 tests/qa_selection.test.py',
    'python3 tests/native_support.test.py',
    'python3 tests/reload_contract.test.py',
    'python3 tests/longarm_gallery.test.py',
    'python3 tools/export_contact.py',
    'python3 tests/contact_exports.test.py',
    'git diff --exit-code -- index.html assets/dc019-equipment.glb',
]


def core_steps(source):
    core = source.split('\n  core:\n', 1)[1].split('\n  browser:\n', 1)[0]
    return re.split(r'\n      - ', core)[1:]


def script(step):
    match = re.search(r'(?:^|\n        )run: (.*)', step)
    if not match:
        return ''
    value = match.group(1)
    if value != '|':
        return value
    return '\n'.join(line[10:] for line in step[match.end():].splitlines()
                     if line.startswith('          '))


class WorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / '.github/workflows/ci.yml').read_text()
        cls.steps = core_steps(cls.source)
        cls.gates = [step for step in cls.steps if script(step)]

    def test_each_validation_has_an_explicit_diagnostic_name(self):
        self.assertGreaterEqual(len(self.gates), 8)
        for step in self.gates:
            self.assertRegex(step, r'^name: .+')

    def test_node_is_a_standalone_unfiltered_gate(self):
        steps = [step for step in self.gates if NODE in script(step)]
        self.assertEqual(len(steps), 1)
        self.assertEqual(script(steps[0]).strip(), NODE)
        self.assertIn('name: Run all Node logic and pose tests', steps[0])

    def test_original_commands_are_retained_exactly_once(self):
        lines = [line.strip() for step in self.gates for line in script(step).splitlines()]
        for command in COMMANDS:
            self.assertEqual(lines.count(command), 1, command)
        self.assertEqual(lines.count('python3 tests/ci_workflow.test.py'), 1)

    def test_later_checks_do_not_depend_on_node_success(self):
        for step in self.gates:
            self.assertIn('        if: ' + READY, step)
            self.assertNotIn('continue-on-error', step)
        for ident in ['checkout', 'node', 'python']:
            self.assertEqual(sum('        id: ' + ident + '\n' in step for step in self.steps), 1)

    def test_node_failure_and_cancellation_are_not_masked(self):
        node = next(step for step in self.gates if NODE in script(step))
        self.assertNotIn('||', script(node))
        self.assertNotIn('continue-on-error', self.source)
        self.assertNotIn('always()', '\n'.join(self.gates))
        self.assertIn('!cancelled()', node)

    def test_permissions_and_browser_commands_are_not_expanded(self):
        self.assertIn('permissions:\n  contents: read\n', self.source)
        self.assertNotIn('contents: write', self.source)
        self.assertIn('--suite reload --origin http --headed --timeout 1800', self.source)
        self.assertIn('--suite longarms --suite sight --suite thenar', self.source)


if __name__ == '__main__':
    unittest.main()
