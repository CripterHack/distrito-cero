"""Current authoring export, not runtime equivalence or artistic acceptance."""
from pathlib import Path
import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('current_export', ROOT / 'tools/export_current_human.py')
try:
    M = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(M)
except FileNotFoundError:
    M = None


class CurrentExport(unittest.TestCase):
    def test_exporter_is_available_without_running_or_writing_at_import(self):
        self.assertIsNotNone(M, 'Current human exporter is missing')
        self.assertTrue(callable(getattr(M, 'export_current', None)))

    def test_current_export_is_self_contained_and_keeps_historical_assets(self):
        self.assertIsNotNone(M, 'Current human exporter is missing')
        historical = ROOT / 'assets/dc016-human-traits.glb'
        before = hashlib.sha256(historical.read_bytes()).hexdigest()
        with tempfile.TemporaryDirectory() as temp:
            destination = Path(temp) / 'current'
            record = M.export_current(destination)
            raw = (destination / record['file']).read_bytes()
            self.assertEqual(struct.unpack_from('<4sII', raw), (b'glTF', 2, len(raw)))
            size, kind = struct.unpack_from('<II', raw, 12)
            self.assertEqual(kind, 0x4e4f534a)
            gltf = json.loads(raw[20:20 + size])
            version = json.loads((ROOT / 'version.json').read_text())['version']
            self.assertEqual(record['productVersion'], version)
            self.assertIn(version, gltf['asset']['generator'])
            self.assertEqual(len(gltf['skins'][0]['joints']), 49)
            self.assertEqual(len(gltf['animations']), 11)
            self.assertEqual(len(gltf['images']), 3)
            self.assertTrue(all('uri' not in image for image in gltf['images']))
            self.assertTrue(all('uri' not in buffer for buffer in gltf['buffers']))
            self.assertEqual(record['sha256'], hashlib.sha256(raw).hexdigest())
            self.assertFalse(record['runtimeSkinningEquivalent'])
            self.assertEqual(record['officialValidation'], 'not-run')
            self.assertEqual(record['artisticAcceptance'], 'pending')
            self.assertEqual(record['ownContentLicense'], 'owner-decision-pending')
            self.assertIn('src/hero-asset.js', record['sources'])
            for path, digest in record['sources'].items():
                self.assertEqual(hashlib.sha256((ROOT / path).read_bytes()).hexdigest(), digest)
            saved = json.loads((destination / 'source-manifest.json').read_text())
            self.assertEqual(saved, record)
            with self.assertRaises(FileExistsError):
                M.export_current(destination)
        self.assertEqual(hashlib.sha256(historical.read_bytes()).hexdigest(), before)

    def test_export_refuses_destinations_inside_versioned_assets(self):
        self.assertIsNotNone(M, 'Current human exporter is missing')
        original = M.source_hashes
        def unexpected_read():
            raise AssertionError('Protected destination reached source generation')
        M.source_hashes = unexpected_read
        try:
            for folder in ('assets', 'src', 'tools', 'tests', 'docs'):
                with self.subTest(folder=folder), self.assertRaises(ValueError):
                    M.export_current(ROOT / folder / 'never-write-here')
        finally:
            M.source_hashes = original

    def test_sources_include_all_native_export_inputs(self):
        self.assertIsNotNone(M, 'Current human exporter is missing')
        sources = M.source_hashes()
        for path in ('src/skin-rig.js', 'src/character-motion.js', 'src/character-fit.js',
                     'src/hair-geometry.js', 'assets/anatomy-source/skin-repaired.webp',
                     'assets/anatomy-source/normal.webp', 'assets/anatomy-source/roughness.webp',
                     'tools/export_traits_glb.py', 'tools/export_current_human.py', 'version.json'):
            self.assertIn(path, sources)


if __name__ == '__main__':
    unittest.main()
