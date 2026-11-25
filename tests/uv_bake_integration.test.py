#!/usr/bin/env python3
"""Explicit authoring test: requires Blender, NumPy and Pillow, never runtime."""
from pathlib import Path
import hashlib
import io
import json
import shutil
import struct
import subprocess
import tempfile
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def fixture(path):
    doc = {'asset': {'version': '2.0'}, 'buffers': [], 'bufferViews': [], 'accessors': [],
           'images': [], 'textures': [], 'samplers': [{'wrapS': 10497, 'wrapT': 33071, 'magFilter': 9729}],
           'materials': [{'pbrMetallicRoughness': {'baseColorTexture': {'index': 0},
              'metallicRoughnessTexture': {'index': 2}, 'metallicFactor': 0}, 'normalTexture': {'index': 1, 'scale': .30}}],
           'nodes': [{'mesh': 0}], 'scenes': [{'nodes': [0]}], 'scene': 0}
    binary = bytearray()
    def view(data):
        binary.extend(b'\0' * (-len(binary) % 4)); start = len(binary); binary.extend(data)
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': start, 'byteLength': len(data)})
        return len(doc['bufferViews']) - 1
    def accessor(rows, kind, component=5126):
        data = np.array(rows, dtype='<f4' if component == 5126 else '<u2')
        doc['accessors'].append({'bufferView': view(data.tobytes()), 'componentType': component,
                                  'count': len(data), 'type': kind})
        return len(doc['accessors']) - 1
    position = accessor([[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], 'VEC3')
    normal = accessor([[0, 0, 1]] * 4, 'VEC3')
    tangent = accessor([[1, 0, 0, 1]] * 4, 'VEC4')
    uv = accessor([[0, 0], [1, 0], [1, 1], [0, 1]], 'VEC2')
    indices = accessor([0, 1, 2, 0, 2, 3], 'SCALAR', 5123)
    for color in [(160, 120, 80), (180, 205, 230), (255, 160, 0)]:
        stream = io.BytesIO(); Image.new('RGB', (16, 16), color).save(stream, format='PNG')
        doc['images'].append({'bufferView': view(stream.getvalue()), 'mimeType': 'image/png'})
        doc['textures'].append({'source': len(doc['images']) - 1, 'sampler': 0})
    doc['meshes'] = [{'primitives': [{'attributes': {'POSITION': position, 'NORMAL': normal,
       'TANGENT': tangent, 'TEXCOORD_0': uv}, 'indices': indices, 'material': 0}]}]
    doc['buffers'] = [{'byteLength': len(binary)}]
    js = json.dumps(doc).encode(); js += b' ' * (-len(js) % 4); binary.extend(b'\0' * (-len(binary) % 4))
    raw = struct.pack('<5I', 0x46546C67, 2, 28 + len(js) + len(binary), len(js), 0x4E4F534A) + js
    raw += struct.pack('<2I', len(binary), 0x004E4942) + binary
    path.write_bytes(raw)
    return raw


class BakeIntegration(unittest.TestCase):
    def test_tracked_output_is_rejected_before_writing(self):
        blender = shutil.which('blender')
        self.assertIsNotNone(blender, 'Explicit authoring test requires Blender')
        with tempfile.TemporaryDirectory(prefix='dc-uv-bake-guard-') as directory:
            root = Path(directory); source = root / 'input.glb'; fixture(source)
            forbidden = ROOT / 'src' / root.name
            self.assertFalse(forbidden.exists())
            run = subprocess.run([blender, '-b', '--python-exit-code', '1', '--python',
                                  str(ROOT / 'tools/bake_human_uv.py'), '--', str(source), str(forbidden)],
                                 capture_output=True, text=True, timeout=30)
            self.assertEqual(run.returncode, 1)
            self.assertIn('must use artifacts/', run.stdout + run.stderr)
            self.assertFalse(forbidden.exists())

    def test_normal_handedness_strength_and_source_integrity(self):
        blender = shutil.which('blender')
        self.assertIsNotNone(blender, 'Explicit authoring test requires Blender')
        with tempfile.TemporaryDirectory(prefix='dc-uv-bake-fixture-') as directory:
            root = Path(directory); source = root / 'input.glb'; raw = fixture(source); output = root / 'bake'
            run = subprocess.run([blender, '-b', '-t', '4', '--python-exit-code', '1', '--python', str(ROOT / 'tools/bake_human_uv.py'),
                                  '--', str(source), str(output)], capture_output=True, text=True, timeout=180)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            recipe = json.loads((output / 'recipe.json').read_text())
            self.assertEqual(source.read_bytes(), raw)
            self.assertEqual(recipe['sourceSha256'], hashlib.sha256(raw).hexdigest())
            self.assertEqual(recipe['normalScale'], 1)
            uv = np.array(recipe['cornerUvs'], dtype=np.float32).reshape(2, 3, 2)
            xy = np.array([[[0, 0, 0], [1, 0, 0], [1, 1, 0]], [[0, 0, 0], [1, 1, 0], [0, 1, 0]]], float)
            im = np.asarray(Image.open(output / recipe['images']['normal']).convert('RGB'), float) / 255
            expected = np.array([180, 205, 230], float) / 255 * 2 - 1
            expected[:2] *= .3; expected /= np.linalg.norm(expected)
            errors = []
            for q, p in zip(uv, xy):
                e1, e2 = p[1] - p[0], p[2] - p[0]
                d1, d2 = q[1] - q[0], q[2] - q[0]
                det = d1[0] * d2[1] - d1[1] * d2[0]
                self.assertNotEqual(det, 0)
                tangent = (e1 * d2[1] - e2 * d1[1]) / det; tangent /= np.linalg.norm(tangent)
                bitangent = (-e1 * d2[0] + e2 * d1[0]) / det; bitangent /= np.linalg.norm(bitangent)
                center = q.mean(0); sample = im[int(center[1] * im.shape[0]), int(center[0] * im.shape[1])] * 2 - 1
                world = sample[0] * tangent + sample[1] * bitangent + sample[2] * np.array([0, 0, 1])
                world /= np.linalg.norm(world)
                angle = np.degrees(np.arccos(np.clip(np.dot(expected, world), -1, 1))); errors.append(float(angle))
                self.assertLess(angle, 1.0, f'Incorrect green convention or double normal strength: {angle}°')
                wrong = sample[0] * tangent - sample[1] * bitangent + sample[2] * np.array([0, 0, 1])
                wrong /= np.linalg.norm(wrong)
                self.assertGreater(np.degrees(np.arccos(np.clip(np.dot(expected, wrong), -1, 1))), 3,
                                   'Fixture must detect an inverted green channel')
            print('Portable normal angular errors (degrees):', errors)


if __name__ == '__main__':
    unittest.main()
