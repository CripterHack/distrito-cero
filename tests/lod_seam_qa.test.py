#!/usr/bin/env python3
"""Regression tests for the seam QA's geometric acceptance, not its renderer."""
from pathlib import Path
import sys
import unittest
import copy
import contextlib
import hashlib
import io
import json
import struct
import tempfile
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.qa import render_lod_seam as qa

class SeamMetricsTest(unittest.TestCase):
    def test_closed_surface_and_open_edge_classification_uses_rest_region(self):
        a=[0,1.5,-.06];b=[.01,1.5,-.06];c=[0,1.51,-.06];d=[0,1.5,-.05]
        closed=[a,c,b,a,b,d,a,d,c,b,c,d]
        world=[[p[0]+5,p[1]-1,p[2]+9] for p in closed]
        self.assertEqual(qa.boundary_metrics(closed,world)['posteriorBoundaryEdges'],0)
        opened=qa.boundary_metrics(closed[:-3],world[:-3])
        self.assertEqual(opened['posteriorBoundaryEdges'],3)
        self.assertTrue(all(e['world'][0][0]>=5 for e in opened['boundaries']))

    def test_shared_world_position_divergence_is_measured(self):
        rest=[[0,1.5,-.06],[.01,1.5,-.06],[0,1.51,-.06]]*2
        world=[list(p) for p in rest];world[3][0]+=.001
        self.assertAlmostEqual(qa.boundary_metrics(rest,world)['maxSharedWorldSpreadM'],.001)

    def test_double_sided_ray_distinguishes_exterior_from_interior(self):
        camera={'eye':[0,0,0],'target':[0,0,-1],'fov':.62}
        front=[[-1,-1,-2],[1,-1,-2],[0,1,-2]]
        back=list(reversed([[-1,-1,-3],[1,-1,-3],[0,1,-3]]))
        a=qa.ray_hit(front+back,camera,(359,359));b=qa.ray_hit(back,camera,(359,359))
        self.assertAlmostEqual(a['depthM'],2);self.assertTrue(a['frontFacing'])
        self.assertAlmostEqual(b['depthM'],3);self.assertFalse(b['frontFacing'])

    def test_old_gap_fails_even_when_capture_and_internal_ray_exist(self):
        sample={'id':'sample','case':{'pose':'idle','camera':'back','bodyGeometryLOD':2},
            'geometry':{'posteriorBoundaryEdges':22,'maxSharedWorldSpreadM':0},
            'exteriorRay':{'frontFacing':False,'depthM':.907}}
        envelope={'minDepthM':.782,'maxDepthM':.785}
        checks=qa.geometric_acceptance([sample],envelope)
        self.assertEqual(sum(not c['pass'] for c in checks),2)
        sample['geometry']['posteriorBoundaryEdges']=0;sample['exteriorRay']={'frontFacing':True,'depthM':.783}
        self.assertTrue(all(c['pass'] for c in qa.geometric_acceptance([sample],envelope)))
        sample['exteriorRay']['depthM']=.786
        self.assertFalse(qa.geometric_acceptance([sample],envelope)[-1]['pass'])

    def test_contract_has_six_neutral_views_and_ten_controlled_neck_poses(self):
        cases=qa.selections(qa.base.load_matrix(qa.ROOT/'tests/benchmarks/characters.json'))
        self.assertEqual(len(cases),16);self.assertEqual(len({c['id'] for c in cases}),16)
        self.assertEqual([(c['camera'],c['bodyGeometryLOD']) for c in cases[:6]],
            [(v,l) for v in ('back','profile') for l in (0,1,2)])
        self.assertTrue(all(c['bodyGeometryLOD']==2 and c['sequence']['continuousSimulation'] is False for c in cases[6:]))


class ReferenceIntegrityTest(unittest.TestCase):
    """Exercise the CLI's evidence gate with a browser adapter, not WebGL QA."""

    def setUp(self):
        (qa.ROOT/'artifacts').mkdir(exist_ok=True)
        self.temp=tempfile.TemporaryDirectory(dir=qa.ROOT/'artifacts',prefix='seam-reference-test-')
        self.addCleanup(self.temp.cleanup)
        self.directory=Path(self.temp.name)
        self.html=self.directory/'fixture.html';self.html.write_text('<script></script>')
        self.reference_path=self.directory/'reference.json'
        self.output=self.directory/'output'
        self.cases=qa.selections(qa.base.load_matrix(qa.ROOT/'tests/benchmarks/characters.json'))
        self.camera={'eye':[0,0,0],'target':[0,0,-1],'fov':.62}
        self.png=b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',720,720)
        self.image_hash=hashlib.sha256(self.png).hexdigest()
        inputs={name:qa.base.digest(path) for name,path in {
            'html':self.html,'stage':qa.ROOT/'tools/qa/character_stage.js',
            'matrix':qa.ROOT/'tests/benchmarks/characters.json',
            'sharedHelper':Path(qa.base.__file__),'fixture':qa.ROOT/'tests/character_benchmark.py',
            'tool':Path(qa.__file__)}.items()}
        depths=[.99+i*.0025 for i in range(len(qa.ENVELOPE_PIXELS))]
        self.reference={'schema':1,'contract':qa.CONTRACT,'captureStatus':'passed',
            'geometricStatus':'failed','inputHashes':inputs,
            'viewport':copy.deepcopy(qa.base.VIEWPORT),'cameraContract':copy.deepcopy(qa.base.CAMERA),
            'errors':[],'requests':[],'captureChecks':[{'name':'Fixture captured','pass':True}],
            'exteriorEnvelope':{'minDepthM':min(depths),'maxDepthM':max(depths),
                'rays':[{'pixel':list(pixel),'triangle':i,'depthM':depth,'frontFacing':True}
                    for i,(pixel,depth) in enumerate(zip(qa.ENVELOPE_PIXELS,depths))]},
            'captures':[{'id':case['id'],'case':copy.deepcopy(case),
                'metrics':{'camera':copy.deepcopy(self.camera)},'imageSha256':self.image_hash}
                for case in self.cases]}

    def run_main(self):
        argv=['render_lod_seam.py','--html',str(self.html),'--output',str(self.output),
            '--label','Reference contract test','--reference',str(self.reference_path)]
        with patch.object(sys,'argv',argv),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            return qa.main()

    def write_reference(self,value):
        self.reference_path.write_text(json.dumps(value))

    def browser_adapter(self,on_capture=None):
        owner=self
        class Page:
            captures=0
            def set_default_timeout(self,*args):pass
            def on(self,*args):pass
            def set_content(self,*args,**kwargs):pass
            def wait_for_function(self,*args,**kwargs):pass
            def wait_for_timeout(self,*args):pass
            def add_script_tag(self,*args,**kwargs):pass
            def close(self):pass
            def screenshot(self,path,**kwargs):Path(path).write_bytes(owner.png)
            def evaluate(self,script,arg=None):
                if script==qa.CAPTURE:
                    if on_capture:on_capture(self.captures)
                    self.captures+=1
                    return {'geometry':{'face':{'rest':[0,0,0]*3,'world':[0,0,0]*3}},
                        'vertexShader':'Test adapter; not a GPU result','camera':copy.deepcopy(owner.camera),
                        'storageUntouched':True,'liveSimulationUntouched':True,'bodyGeometryRestored':True,
                        'drawMethodRestored':True,'glError':0,'cullAtDraw':[False]}
                return {} if script=='DCCharacterBenchmark.init()' else True
        class Browser:
            version='Test adapter; no browser launched'
            def new_page(self,**kwargs):return Page()
            def close(self):pass
        class Playwright:
            def __init__(self):self.chromium=self
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def launch(self,**kwargs):return Browser()
        return Playwright

    @contextlib.contextmanager
    def captured_fixture(self,on_capture=None):
        with patch.object(qa,'sync_playwright',self.browser_adapter(on_capture)),\
             patch.object(qa.base,'launch_options',return_value={'headless':True}),\
             patch.object(qa,'boundary_metrics',return_value={'posteriorBoundaryEdges':0,'maxSharedWorldSpreadM':0}),\
             patch.object(qa,'ray_hit',side_effect=lambda world,camera,pixel:{'pixel':list(pixel),'frontFacing':True,'depthM':1.0}):
            yield

    def test_explicit_empty_reference_is_rejected_before_browser(self):
        for index,value in enumerate(({},[],None,False)):
            with self.subTest(value=value):
                self.output=self.directory/('output-empty-'+str(index))
                self.write_reference(value)
                with patch.object(qa,'sync_playwright',side_effect=AssertionError('Invalid reference reached browser')) as browser:
                    with self.assertRaises(SystemExit) as raised:self.run_main()
                    self.assertEqual(raised.exception.code,2)
                    browser.assert_not_called()
                self.assertFalse(self.output.exists())

    def test_malformed_reference_schema_is_rejected_before_browser(self):
        def changed(key,value):
            result=copy.deepcopy(self.reference);result[key]=value;return result
        bad=[('schema',changed('schema',2)),('viewport',changed('viewport',{'width':1,'height':1})),
            ('camera-contract',changed('cameraContract',{})),('errors',changed('errors',['shader failure'])),
            ('requests',changed('requests',['https://example.invalid/asset'])),
            ('checks-empty',changed('captureChecks',[])),('checks-failed',changed('captureChecks',[{'name':'bad','pass':False}])),
            ('capture-count',changed('captures',self.reference['captures'][:-1]))]
        for field in ('html','stage','matrix','sharedHelper','fixture','tool'):
            value=copy.deepcopy(self.reference);value['inputHashes'][field]='not-a-sha256';bad.append(('hash-'+field,value))
        for name,edit in [
            ('duplicate-id',lambda r:r['captures'][1].update(id=r['captures'][0]['id'])),
            ('different-case',lambda r:r['captures'][0]['case'].update(time=999)),
            ('image-hash',lambda r:r['captures'][0].update(imageSha256='bad')),
            ('camera-nan',lambda r:r['captures'][0]['metrics']['camera']['eye'].__setitem__(0,float('nan'))),
            ('camera-fov',lambda r:r['captures'][0]['metrics']['camera'].update(fov=0)),
            ('envelope-order',lambda r:r['exteriorEnvelope'].update(minDepthM=2)),
            ('envelope-nan',lambda r:r['exteriorEnvelope'].update(maxDepthM=float('nan'))),
            ('envelope-wrong-bounds',lambda r:r['exteriorEnvelope'].update(maxDepthM=99)),
            ('ray-count',lambda r:r['exteriorEnvelope']['rays'].pop()),
            ('ray-pixel',lambda r:r['exteriorEnvelope']['rays'][0].update(pixel=[0,0])),
            ('ray-inside',lambda r:r['exteriorEnvelope']['rays'][0].update(frontFacing=False)),
            ('ray-depth',lambda r:r['exteriorEnvelope']['rays'][0].update(depthM=float('inf'))),
        ]:
            value=copy.deepcopy(self.reference);edit(value);bad.append((name,value))
        for name,value in bad:
            with self.subTest(name=name):
                self.output=self.directory/('output-malformed-'+name)
                self.write_reference(value)
                with patch.object(qa,'sync_playwright',side_effect=AssertionError('Invalid reference reached browser')) as browser:
                    with self.assertRaises(SystemExit) as raised:self.run_main()
                    self.assertEqual(raised.exception.code,2)
                    browser.assert_not_called()
                self.assertFalse(self.output.exists())

    def test_stable_reference_with_failed_old_geometry_can_pass_new_capture(self):
        self.write_reference(self.reference)
        with self.captured_fixture():self.assertEqual(self.run_main(),0)
        report=json.loads((self.output/'report.json').read_text())
        self.assertEqual(report['captureStatus'],'passed');self.assertEqual(report['geometricStatus'],'passed')
        self.assertEqual(report['referenceReportSha256'],qa.base.digest(self.reference_path))
        self.assertEqual(sum(c['name'].startswith('LOD0/1 pixels unchanged:') for c in report['geometricChecks']),4)

    def test_reference_mutation_rejects_capture_and_preserves_failure_report(self):
        self.write_reference(self.reference);original_hash=qa.base.digest(self.reference_path)
        def mutate(first):
            if first==0:self.write_reference({**self.reference,'label':'changed during capture'})
        with self.captured_fixture(mutate):
            with self.assertRaisesRegex(AssertionError,'[Rr]eference|[Ii]nput'):self.run_main()
        report=json.loads((self.output/'report.json').read_text())
        self.assertEqual(report['captureStatus'],'failed');self.assertNotEqual(report['geometricStatus'],'passed')
        self.assertRegex(report['failure'],'[Rr]eference|[Ii]nput')
        self.assertEqual(report['referenceReportSha256'],original_hash)
        self.assertNotEqual(report['referenceReportSha256'],qa.base.digest(self.reference_path))

if __name__=='__main__':unittest.main()
