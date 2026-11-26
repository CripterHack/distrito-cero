#!/usr/bin/env python3
"""Portable-viewer acceptance regressions; adapters do not certify rendering."""
import contextlib
import functools
import hashlib
import http.server
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('uv_viewer', ROOT/'tools/qa/render_uv_rebake.py')
viewer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viewer)


class ViewerAcceptance(unittest.TestCase):
    def run_adapter(self, change=None, console_error=False):
        # Real CLI orchestration and report writes, fake browser only. The
        # adapter explicitly reports its identity, never physical/WebGL QA.
        with tempfile.TemporaryDirectory(prefix='viewer-contract-', dir=ROOT/'artifacts') as temp:
            directory = Path(temp)
            before, after = directory/'before.glb', directory/'after.glb'
            before.write_bytes(b'before fixture'); after.write_bytes(b'after fixture')
            initial = {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in (before, after)}
            changed = False
            class Page:
                def __init__(self): self.events = {}
                def on(self, name, callback): self.events[name] = callback
                def goto(self, url):
                    nonlocal changed
                    if change and not changed:
                        (before if change == 'before' else after).write_bytes(b'changed during capture')
                        changed = True
                def wait_for_function(self, *args, **kwargs): pass
                def evaluate(self, expression, options):
                    return {**options, 'renderer':'acceptance-test-adapter'}
                def screenshot(self, path):
                    Path(path).write_bytes(b'capture adapter; not an image')
                    if console_error and 'console' in self.events:
                        self.events['console'](types.SimpleNamespace(type='error', text='THREE.WebGLProgram: Shader Error injected'))
                def close(self): pass
            browser = types.SimpleNamespace(version='test-adapter', new_page=lambda **kwargs:Page(), close=lambda:None)
            playwright = types.SimpleNamespace(chromium=types.SimpleNamespace(launch=lambda **kwargs:browser))
            output = directory/'output'
            argv = ['render_uv_rebake.py',str(before),str(after),'--output',str(output)]
            exception = None
            with patch.object(viewer,'sync_playwright',lambda:contextlib.nullcontext(playwright)), patch.object(sys,'argv',argv), contextlib.redirect_stdout(io.StringIO()):
                try: viewer.run()
                except RuntimeError as error: exception = error
            report = json.loads((output/'report.json').read_text())
            self.assertEqual(report['inputs'],initial)
            return exception,report

    def test_stable_inputs_preserve_24_cases_and_hash_provenance(self):
        error, report = self.run_adapter()
        self.assertIsNone(error)
        self.assertEqual(len(report['cases']),24)
        self.assertFalse(report['nativeRuntime'])
        self.assertEqual(report['errors'],[])

    def test_console_shader_errors_reject_acceptance_and_preserve_report(self):
        error, report = self.run_adapter(console_error=True)
        self.assertIsNotNone(error)
        self.assertTrue(any('Shader Error' in item for item in report['errors']))

    def test_each_input_changed_during_capture_rejects_acceptance(self):
        for source in ('before','after'):
            with self.subTest(source=source):
                error, report = self.run_adapter(change=source)
                self.assertIsNotNone(error)
                self.assertTrue(any('Input changed' in item for item in report['errors']))


class RealShaderRegression(unittest.TestCase):
    def test_invalid_normal_shader_throws_in_real_browser(self):
        from playwright.sync_api import sync_playwright, Error
        # Use the shipped portable human, independent of generated UV artifacts.
        source = '/assets/dc016-human-traits.glb'
        class Handler(http.server.SimpleHTTPRequestHandler):
            def log_message(self,*args): pass
        server = http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(ROOT)))
        threading.Thread(target=server.serve_forever,daemon=True).start()
        origin = 'http://127.0.0.1:'+str(server.server_port)
        html = (ROOT/'tools/qa/uv_rebake_viewer.html').read_text()
        # Reuse only a test-route asset alias. No production fault-injection API.
        broken = html.replace('shader.fragmentShader=shader.fragmentShader.replace', "shader.fragmentShader='INVALID_SHADER_TOKEN;'+shader.fragmentShader; shader.fragmentShader=shader.fragmentShader.replace")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--disable-dev-shm-usage'])
                try:
                    for bad, content in ((False,html),(True,broken)):
                        with self.subTest(invalid_shader=bad):
                            page = browser.new_page(viewport={'width':800,'height':800})
                            def route(request):
                                url=request.request.url.split('?')[0]
                                if url.endswith('/uv_rebake_viewer.html'):
                                    request.fulfill(status=200,content_type='text/html',body=content)
                                elif url.endswith('/artifacts/viewer-test.glb'):
                                    request.fulfill(status=200,content_type='model/gltf-binary',body=(ROOT/source.lstrip('/')).read_bytes())
                                else: request.continue_()
                            page.route('**/*',route)
                            page.goto(origin+'/tools/qa/uv_rebake_viewer.html?asset=/artifacts/viewer-test.glb')
                            page.wait_for_function('window.ready === true',timeout=120000)
                            if bad:
                                with self.assertRaisesRegex(Error,'shader|Shader'):
                                    page.evaluate("window.capture({mode:'normal'})")
                            else:
                                info=page.evaluate("window.capture({mode:'normal'})")
                                self.assertEqual(info['mode'],'normal')
                                self.assertGreater(info['triangles'],0)
                            page.close()
                finally: browser.close()
        finally:
            server.shutdown();server.server_close()


if __name__=='__main__': unittest.main()
