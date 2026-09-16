"""Version-of-product contracts. No network or third-party packages required."""
from pathlib import Path
import hashlib, json, shutil, subprocess, sys, tempfile, unittest
R = Path(__file__).resolve().parents[1]
class ReleaseBuild(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copy2(R/'build.py', self.root/'build.py')
        shutil.copytree(R/'src', self.root/'src')
        if (R/'version.json').exists(): shutil.copy2(R/'version.json', self.root/'version.json')
        self.release=json.loads((R/'version.json').read_text())
        version=self.release['version'];self.label='v'+(version[:-2] if version.endswith('.0') else version)
    def run_build(self,*args):
        return subprocess.run([sys.executable,str(self.root/'build.py'),*args],capture_output=True,text=True)
    def test_product_has_explicit_canonical_version(self):
        self.assertTrue((R/'version.json').is_file(),'Canonical product version is missing')
        data=json.loads((R/'version.json').read_text()); self.assertRegex(data['version'],r'^[0-9]+\.[0-9]+\.[0-9]+$')
        self.assertTrue(data['name']); self.assertEqual(data['channel'],'prototype')
    def test_check_rejects_missing_artifact_without_creating_it(self):
        result=self.run_build('--check'); self.assertNotEqual(result.returncode,0,result.stdout)
        self.assertFalse((self.root/'index.html').exists(),'--check must not create outputs')
    def test_check_rejects_stale_html_without_repairing_it(self):
        self.assertEqual(self.run_build().returncode,0)
        p=self.root/'index.html'; p.write_bytes(b'stale HTML'); result=self.run_build('--check')
        self.assertNotEqual(result.returncode,0,result.stdout); self.assertEqual(p.read_bytes(),b'stale HTML')
    def test_rebuild_is_deterministic_without_git_metadata(self):
        self.assertEqual(self.run_build().returncode,0)
        first=(self.root/'index.html').read_bytes(); self.assertEqual(self.run_build().returncode,0)
        self.assertEqual((self.root/'index.html').read_bytes(),first)
        self.assertEqual(self.run_build('--check').returncode,0)
    def test_sidecar_records_exact_html_and_source_identity(self):
        self.assertEqual(self.run_build().returncode,0)
        self.assertTrue((self.root/'build-info.json').exists(),'No build identity sidecar')
        data=json.loads((self.root/'build-info.json').read_text()); payload=(self.root/'index.html').read_bytes()
        self.assertEqual(data['htmlSha256'],hashlib.sha256(payload).hexdigest()); self.assertEqual(data['htmlBytes'],len(payload))
        self.assertRegex(data['version'],r'^[0-9]+\.[0-9]+\.[0-9]+$'); self.assertRegex(data['sourceSha256'],r'^[0-9a-f]{64}$')
        self.assertNotIn(str(self.root),json.dumps(data)); self.assertNotIn('builtAt',data)
    def test_ui_and_runtime_share_identity_without_version_fetch(self):
        self.assertEqual(self.run_build().returncode,0); page=(self.root/'index.html').read_text()
        self.assertTrue('<title>Distrito Cero '+self.label+' · '+self.release['name']+'</title>' in page, 'Active title is stale')
        self.assertTrue('name="application-version" content="'+self.release['version']+'"' in page)
        self.assertEqual(page.count('data-build-version="'+self.release['version']+'"'),3)
        self.assertIn('DC.BuildInfo',page); self.assertNotIn('{{BUILD_',page)
        self.assertNotIn('fetch("version.json")',page); self.assertNotIn('fetch("build-info.json")',page)
    def test_source_change_invalidates_identity(self):
        self.assertEqual(self.run_build().returncode,0)
        old=json.loads((self.root/'build-info.json').read_text())
        with (self.root/'src/core.js').open('a') as f: f.write('\n// build-identity regression\n')
        self.assertNotEqual(self.run_build('--check').returncode,0)
        self.assertEqual(self.run_build().returncode,0)
        new=json.loads((self.root/'build-info.json').read_text()); self.assertNotEqual(new['sourceSha256'],old['sourceSha256'])
        self.assertNotEqual(new['htmlSha256'],old['htmlSha256'])
    def test_invalid_manifest_does_not_replace_good_outputs(self):
        self.assertEqual(self.run_build().returncode,0); original=(self.root/'index.html').read_bytes()
        manifest={'schema':1,'version':'0.20.0','name':'Coherencia','channel':'prototype','date':'2026-09-16'}
        for field,value in [('version','../1'),('name','</script><script>bad</script>'),('date','2026-02-31'),('channel','production'),('schema',True)]:
            data=dict(manifest);data[field]=value;(self.root/'version.json').write_text(json.dumps(data))
            with self.subTest(field=field):
                self.assertNotEqual(self.run_build().returncode,0); self.assertEqual((self.root/'index.html').read_bytes(),original)
    def test_unknown_template_marker_fails_without_writing(self):
        with (self.root/'src/page.html').open('a') as f:f.write('{{BUILD_UNKNOWN}}')
        self.assertNotEqual(self.run_build().returncode,0)
        self.assertFalse((self.root/'index.html').exists())
    def test_stale_sidecar_is_rejected_without_mutation(self):
        self.assertEqual(self.run_build().returncode,0); p=self.root/'build-info.json';p.write_text('{}')
        self.assertNotEqual(self.run_build('--check').returncode,0);self.assertEqual(p.read_text(),'{}')
    def test_current_readme_and_asset_index_advertise_canonical_label(self):
        for path in ['README.md','assets/README.md','docs/project/STATE.md']:
            self.assertIn(self.label,(R/path).read_text(),path)
    def test_missing_script_marker_is_rejected(self):
        p=self.root/'src/page.html';p.write_text(p.read_text().replace('/*__JS__*/',''))
        self.assertNotEqual(self.run_build().returncode,0)
        self.assertFalse((self.root/'index.html').exists())
if __name__=='__main__':unittest.main()
