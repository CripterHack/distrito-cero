"""Git checkout identity regression. Uses temporary repos, never global settings."""
from pathlib import Path
import hashlib
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('git'), 'Git is required for checkout integration')
class ReleaseCheckout(unittest.TestCase):
    def test_autocrlf_checkout_keeps_build_and_binary_bytes(self):
        with tempfile.TemporaryDirectory(prefix='dc-release-checkout-') as directory:
            base = Path(directory)
            source = base / 'source'
            source.mkdir()
            for name in ['build.py', 'version.json', 'index.html', 'build-info.json']:
                shutil.copy2(ROOT / name, source / name)
            shutil.copytree(ROOT / 'src', source / 'src')
            attributes = ROOT / '.gitattributes'
            if attributes.is_file():
                shutil.copy2(attributes, source / '.gitattributes')
            binary = bytes(range(256)) + b'\r\n\x00binary-probe\r\n'
            (source / 'binary-probe.glb').write_bytes(binary)
            def git(*args):
                return subprocess.run(['git', *args], cwd=source, capture_output=True, text=True, check=True)
            git('init', '--quiet')
            git('-c', 'core.autocrlf=false', 'add', '--all')
            git('-c', 'user.name=Checkout fixture', '-c', 'user.email=qa@example.invalid',
                '-c', 'commit.gpgsign=false', 'commit', '--quiet', '-m', 'Synthetic checkout fixture')
            for mode in ['true', 'input', 'false']:
                with self.subTest(autocrlf=mode):
                    checkout = base / ('checkout-' + mode)
                    git('clone', '--quiet', '--no-hardlinks', '--config', 'core.autocrlf=' + mode,
                        str(source), str(checkout))
                    result = subprocess.run([sys.executable, str(checkout / 'build.py'), '--check'],
                                            capture_output=True, text=True)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    for name in ['index.html', 'build-info.json']:
                        self.assertEqual(hashlib.sha256((checkout / name).read_bytes()).hexdigest(),
                                         hashlib.sha256((source / name).read_bytes()).hexdigest(), name)
                    self.assertEqual((checkout / 'binary-probe.glb').read_bytes(), binary)

if __name__ == '__main__':
    unittest.main()
