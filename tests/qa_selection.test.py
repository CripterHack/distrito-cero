"""Native mode must not accidentally run or relabel the storage fixtures."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa.run import select_suites
class SelectionTests(unittest.TestCase):
    def test_all_filters_by_storage_contract(self):
        self.assertEqual(len(select_suites(['all'],'fixture')),17)
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
        q=select_suites(['sight'],'fixture')
        self.assertEqual([x.name for x in q],['sight-base','sight-cross-family','sight-revolver-reload'])
        self.assertEqual([x.expected_checks for x in q],[40,26,28])
        self.assertEqual(sum(x.expected_checks for x in q),94)
        with self.assertRaises(ValueError):select_suites(['sight'],'http')
    def test_reload_input_suite_requires_native_http_and_fixed_coverage(self):
        self.assertEqual(select_suites(['reload'],'http')[0].expected_checks,31)
        with self.assertRaises(ValueError):select_suites(['reload'],'fixture')
    def test_longarm_audit_is_not_a_native_or_artistic_acceptance_suite(self):
        self.assertEqual(select_suites(['longarms'],'fixture')[0].expected_checks,28)
        with self.assertRaises(ValueError):select_suites(['longarms'],'http')
    def test_equipment_handoff_is_canonical_graphics_not_native_storage(self):
        self.assertEqual(select_suites(['handoff'],'fixture')[0].expected_checks,28)
        with self.assertRaises(ValueError):select_suites(['handoff'],'http')
    def test_sight_alias_deduplicates_explicit_partitions_without_losing_order(self):
        from tools.qa.run import SUITES
        self.assertIn('sight-base',SUITES)
        q=select_suites(['sight','sight-base','sight-cross-family','sight'],'fixture')
        self.assertEqual([x.name for x in q],['sight-base','sight-cross-family','sight-revolver-reload'])
        self.assertEqual(len({x.report for x in q}),3)
        self.assertEqual([x.command for x in q],[
            ('tests/sidearm_sight_browser.py','--partition','base'),
            ('tests/sidearm_sight_browser.py','--partition','cross-family'),
            ('tests/sidearm_sight_browser.py','--partition','revolver-reload')])

    def test_sight_partitions_reject_native_mode_and_unknown_names(self):
        from tools.qa.run import SUITES
        self.assertIn('sight-base',SUITES)
        for name in ['sight-base','sight-cross-family','sight-revolver-reload']:
            with self.assertRaises(ValueError):select_suites([name],'http')
        with self.assertRaises(KeyError):select_suites(['sight-imaginary'],'fixture')

    def test_sight_partitions_keep_old_exchanges_and_add_only_smg_revolver_reload(self):
        from tools.qa.sight_contract import sight_cases
        cases=sight_cases
        expected=(('pistol','revolver',None),('revolver','pistol',None),
            ('pistol','revolver',.46),('revolver','pistol',.46),
            ('rifle','pistol',None),('pistol','rifle',None),
            ('rifle','pistol',.46),('pistol','rifle',.46),
            ('rifle','revolver',None),('revolver','rifle',None),
            ('rifle','revolver',.46),('revolver','rifle',.46),
            ('smg','revolver',None),('revolver','smg',None),
            ('smg','revolver',.46),('revolver','smg',.46))
        self.assertEqual(cases('all'),expected)
        self.assertEqual(cases('base'),expected[:4])
        self.assertEqual(cases('cross-family'),expected[4:10])
        self.assertEqual(cases('revolver-reload'),expected[10:])
        self.assertEqual(cases('all')[:14],expected[:14])
        self.assertEqual(cases('all')[14:],(('smg','revolver',.46),('revolver','smg',.46)))
        self.assertEqual(cases('base')+cases('cross-family')+cases('revolver-reload'),cases('all'))
        self.assertEqual(len(cases('all')),len(set(cases('all'))))
        self.assertEqual(len(cases('all')),16)
        self.assertFalse(set(cases('revolver-reload')) & set(cases('cross-family')))
        with self.assertRaises(ValueError):cases('imaginary')

    def test_invalid_sight_partition_fails_before_loading_browser_or_writing_output(self):
        import subprocess,tempfile,os
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'evidence'
            blocked=Path(d)/'blocked';(blocked/'playwright').mkdir(parents=True)
            (blocked/'playwright/__init__.py').write_text('')
            (blocked/'playwright/sync_api.py').write_text("raise AssertionError('Browser import must follow argument validation')\n")
            result=subprocess.run([sys.executable,'tests/sidearm_sight_browser.py',
                '--partition','imaginary'],cwd=Path(__file__).resolve().parents[1],
                env={**os.environ,'DC_SIGHT_OUTPUT':str(out),'PYTHONPATH':str(blocked)},capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,2,result.stderr)
            self.assertIn('invalid choice',result.stderr)
            self.assertFalse(out.exists())


    def _guard_scope(self, base=False, comparison=False):
        import ast
        path=Path(__file__).with_name('sidearm_sight_browser.py')
        tree=ast.parse(path.read_text())
        functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='guard']
        self.assertEqual(len(functions),1,'Every partition needs the same fail-closed shared guard')
        checks=[];guards=[]
        scope={'base':base,'comparison':comparison,'guards':guards,
            'ck':lambda name,value:checks.append({'name':name,'pass':bool(value)})}
        exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),'exec'),scope)
        return scope,checks,guards

    def test_cross_family_shared_guards_fail_closed_without_double_counting(self):
        import contextlib,io
        scope,checks,guards=self._guard_scope()
        with contextlib.redirect_stdout(io.StringIO()):
            scope['guard']('decoded',True)
            with self.assertRaises(AssertionError):scope['guard']('selector',False)
        self.assertEqual(checks,[])
        self.assertEqual(guards,[{'name':'decoded','pass':True},{'name':'selector','pass':False}])
        comparison,_,record=self._guard_scope(comparison=True)
        with contextlib.redirect_stdout(io.StringIO()):comparison['guard']('failed comparison',False)
        self.assertEqual(record,[{'name':'failed comparison','pass':False}])

    def test_base_and_all_count_shared_guards_only_once(self):
        scope,checks,guards=self._guard_scope(base=True)
        scope['guard']('decoded',True)
        self.assertEqual(checks,[{'name':'decoded','pass':True}])
        self.assertEqual(guards,[])

    def test_shared_ui_guards_run_after_the_final_exchange_in_every_partition(self):
        import ast
        tree=ast.parse(Path(__file__).with_name('sidearm_sight_browser.py').read_text())
        calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call)
            and isinstance(n.func,ast.Name) and n.func.id=='guard']
        from tools.qa.sight_contract import SIGHT_GUARDS
        names=[]
        for call in calls:
            label=call.args[0]
            self.assertIsInstance(label,ast.Subscript,'Producer must use the shared guard contract')
            self.assertIsInstance(label.value,ast.Name)
            self.assertEqual(label.value.id,'SIGHT_GUARDS')
            self.assertIsInstance(label.slice,ast.Constant)
            self.assertIn(label.slice.value,SIGHT_GUARDS)
            names.append(SIGHT_GUARDS[label.slice.value])
        self.assertEqual(set(names),{
            'Embedded skin maps decode in the production renderer',
            'Translucent selector remains paused and blocks game actions',
            'Closing selection does not restore a trigger or aiming request',
            'Visual inspection never overwrites the saved catalogue',
            'No JavaScript or graphics exceptions or external requests'})
        self.assertEqual(len(calls),5)
        parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
        for call in calls:
            node=call
            while node in parents:
                node=parents[node]
                self.assertFalse(isinstance(node,ast.If) and any(
                    isinstance(n,ast.Name) and n.id in ('base','partition') for n in ast.walk(node.test)),
                    'Shared UI coverage cannot depend on partition selection')
        ui=next(n for n in ast.walk(tree) if isinstance(n,ast.Constant)
            and n.value=='DC_APP.setMode("play")')
        node=ui
        while node in parents:
            node=parents[node]
            self.assertFalse(isinstance(node,ast.If) and any(
                isinstance(n,ast.Name) and n.id in ('base','partition') for n in ast.walk(node.test)))

if __name__=='__main__':unittest.main()
