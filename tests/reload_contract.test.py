"""Negative controls for the observations made by the real HTTP reload suite."""
import copy
import json
import tempfile
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.qa.reload_contract import pause_errors, completion_errors
from tools.qa.reload_progress import write_progress


def sample():
    return dict(mode='arsenal', frame=10, time=3.0, selected='rifle', remaining=.5,
                reloadId='rifle', ammo={'rifle': {'loaded': 28, 'reserve': 5},
                                      'pistol': {'loaded': 12, 'reserve': 48}},
                shots=0, charge=0, trigger=False, aiming=False, inputs=False,
                completed=0, glError=0, frozen=True,
                rendered={'selected': 'rifle', 'instances': {'body': 1, 'magazine': 1},
                          'magazine': {'attachedToHand': True, 'offset': [0, -.1, 0], 'rotation': [0, 0, .1]}})


def finished():
    s=sample();s.update(mode='pause', frame=50, time=3.6, remaining=0,
                        reloadId=None, completed=1, frozen=False)
    s['ammo']['rifle']={'loaded': 30, 'reserve': 3}
    s['rendered']['magazine']={'attachedToHand': False, 'offset': [0, 0, 0], 'rotation': [0, 0, 0]}
    return s


class ReloadContractTests(unittest.TestCase):
    def test_paused_observation_requires_live_frames(self):
        a=sample();b=copy.deepcopy(a);b['frame']+=3
        self.assertEqual(pause_errors(a,b),[])
        b['frame']=a['frame'];self.assertTrue(pause_errors(a,b))

    def test_timer_and_world_cannot_advance_in_pause(self):
        for key,value in [('time',3.01),('remaining',.49),('reloadId',None),('selected','pistol')]:
            with self.subTest(key=key):
                a=sample();b=copy.deepcopy(a);b['frame']+=3;b[key]=value
                self.assertTrue(pause_errors(a,b))

    def test_paused_ammo_cannot_transfer_or_change_another_item(self):
        for item in ['rifle','pistol']:
            a=sample();b=copy.deepcopy(a);b['frame']+=3;b['ammo'][item]['loaded']+=1
            self.assertTrue(pause_errors(a,b))

    def test_modes_and_frozen_mount_are_real(self):
        for key,value in [('mode','play'),('frozen',False)]:
            a=sample();b=copy.deepcopy(a);b['frame']+=3;b[key]=value
            self.assertTrue(pause_errors(a,b))

    def test_held_inputs_charge_and_phantom_shots_are_rejected(self):
        for key,value in [('inputs',True),('trigger',True),('aiming',True),('charge',.2),('shots',1)]:
            a=sample();b=copy.deepcopy(a);b['frame']+=3;b[key]=value
            self.assertTrue(pause_errors(a,b),key)

    def test_stale_missing_duplicate_or_erroring_render_is_rejected(self):
        for key,value in [('selected','pistol'),('instances',{}),('instances',{'body':1,'magazine':2})]:
            a=sample();b=copy.deepcopy(a);b['frame']+=3;b['rendered'][key]=value
            self.assertTrue(pause_errors(a,b))
        a=sample();b=copy.deepcopy(a);b['frame']+=3;b['glError']=1282
        self.assertTrue(pause_errors(a,b))

    def test_rendered_piece_cannot_drift_while_paused(self):
        a=sample();b=copy.deepcopy(a);b['frame']+=3;b['rendered']['magazine']['offset'][1]-=.01
        self.assertTrue(pause_errors(a,b))

    def test_completed_reload_transfers_exactly_once(self):
        self.assertEqual(completion_errors(sample(),finished(),30),[])
        for key,value in [('remaining',.01),('reloadId','rifle'),('completed',2),('time',3.1)]:
            b=finished();b[key]=value;self.assertTrue(completion_errors(sample(),b,30),key)
        b=finished();b['ammo']['rifle']['reserve']-=2
        self.assertTrue(completion_errors(sample(),b,30))

    def test_partial_reserve_is_not_assumed_to_fill_magazine(self):
        a=sample();a['ammo']['rifle']['reserve']=1;b=finished();b['ammo']['rifle']={'loaded':29,'reserve':0}
        self.assertEqual(completion_errors(a,b,30),[])

    def test_switch_cancels_without_any_transfer(self):
        a=sample();b=finished();b.update(selected='binoculars',completed=0)
        b['ammo']=copy.deepcopy(a['ammo']);b['rendered']['selected']='binoculars'
        self.assertEqual(completion_errors(a,b,30,selected='binoculars'),[])
        b['ammo']['rifle']['loaded']+=2
        self.assertTrue(completion_errors(a,b,30,selected='binoculars'))

    def test_completed_or_switched_action_cannot_leave_a_detached_piece(self):
        b=finished();b['rendered']['magazine']['attachedToHand']=True
        self.assertTrue(completion_errors(sample(),b,30))
        b=finished();b['rendered']['magazine']['rotation'][2]=.1
        self.assertTrue(completion_errors(sample(),b,30))

    def test_nonfinite_clock_is_never_accepted(self):
        a=sample();b=finished();b['time']=float('nan')
        self.assertTrue(completion_errors(a,b,30))

class ReloadProgressTests(unittest.TestCase):
    def test_partial_journal_never_claims_a_completed_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'reload.progress.json'
            write_progress(path, {'status':'passed','finishedUtc':'not-a-completed-run',
                                  'checks':[{'pass':True}], 'expectedChecks':31,
                                  'sha256':'canonical-html','nativeStorage':True})
            saved=json.loads(path.read_text())
            self.assertEqual(saved['status'],'in_progress')
            self.assertEqual(saved['completedChecks'],1)
            self.assertEqual(saved['expectedChecks'],31)
            self.assertEqual(saved['sha256'],'canonical-html')
            self.assertTrue(saved['nativeStorage'])
            self.assertNotIn('finishedUtc',saved)

    def test_progress_cannot_overwrite_the_canonical_runner_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'reload.json'
            with self.assertRaises(ValueError):write_progress(path, {'checks':[]})
            self.assertFalse(path.exists())

    def test_checkpoint_keeps_the_latest_observations_without_duplicates(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'reload.progress.json'
            write_progress(path, {'checks':[{'pass':True}], 'cases':[{'name':'one'}]})
            write_progress(path, {'checks':[{'pass':True},{'pass':False}],
                                  'cases':[{'name':'one'},{'name':'two'}], 'errors':['failure retained']})
            saved=json.loads(path.read_text())
            self.assertEqual(saved['completedChecks'],2)
            self.assertEqual(len(saved['cases']),2)
            self.assertFalse(saved['checks'][1]['pass'])
            self.assertEqual(saved['errors'],['failure retained'])
            self.assertFalse(list(Path(tmp).glob('*.tmp')))

    def test_progress_writer_does_not_mutate_its_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            source={'checks':[{'pass':True}], 'cases':[{'ammo':{'loaded':3}}]}
            before=copy.deepcopy(source)
            write_progress(Path(tmp)/'reload.progress.json',source)
            self.assertEqual(source,before)

if __name__=='__main__':unittest.main()
