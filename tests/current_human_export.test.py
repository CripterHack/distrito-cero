"""Current authoring export, not runtime equivalence or artistic acceptance."""
from pathlib import Path
import hashlib
import copy
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


class PortableSchema(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.destination = Path(cls.temp.name) / 'export'
        original = M.normalize_portable_structure
        def inspected(description, binary):
            cls.before_normalization = (copy.deepcopy(description), bytes(binary))
            return original(description, binary)
        M.normalize_portable_structure = inspected
        try:
            cls.record = M.export_current(cls.destination)
        finally:
            M.normalize_portable_structure = original
        cls.raw = (cls.destination / cls.record['file']).read_bytes()
        json_size = struct.unpack_from('<I', cls.raw, 12)[0]
        cls.gltf = json.loads(cls.raw[20:20 + json_size])
        cls.binary = cls.raw[28 + json_size:]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_real_recipe_buffers_change_only_for_zero_weight_joint_ids(self):
        prior, binary = self.before_normalization
        prior = copy.deepcopy(prior)
        expected = bytearray(binary)
        for mesh in prior['meshes']:
            for primitive in mesh['primitives']:
                j = prior['accessors'][primitive['attributes']['JOINTS_0']]
                w = prior['accessors'][primitive['attributes']['WEIGHTS_0']]
                jv, wv = (prior['bufferViews'][a['bufferView']] for a in (j, w))
                for index in range(j['count']):
                    for k in range(4):
                        jp = jv.get('byteOffset', 0) + j.get('byteOffset', 0) + index * jv.get('byteStride', 4) + k
                        wp = wv.get('byteOffset', 0) + w.get('byteOffset', 0) + index * wv.get('byteStride', 4) + k
                        if binary[wp] == 0:
                            expected[jp] = 0
        self.assertEqual(self.binary, bytes(expected))
        for key in ('accessors', 'bufferViews', 'meshes', 'skins', 'materials', 'images', 'animations'):
            self.assertEqual(self.gltf[key], prior[key], key)
        instances = {i for i, node in enumerate(prior['nodes']) if 'skin' in node and 'mesh' in node}
        for node in prior['nodes']:
            if 'children' in node:
                children = [i for i in node['children'] if i not in instances]
                if children: node['children'] = children
                else: del node['children']
        self.assertEqual(self.gltf['nodes'][0]['children'], prior['nodes'][0]['children'])
        self.assertEqual(self.gltf['nodes'][1:], prior['nodes'][1:])

    def test_real_export_promotes_mesh_instances_without_reparenting_any_joint(self):
        prior, _ = self.before_normalization
        parent = {child: i for i, node in enumerate(self.gltf['nodes'])
                  for child in node.get('children', [])}
        meshes = [i for i, n in enumerate(self.gltf['nodes']) if 'skin' in n and 'mesh' in n]
        self.assertEqual(len(meshes), 14)
        self.assertEqual([i for i in meshes if i in parent], [], 'Khronos non-root skinned meshes')
        before_parent = {child: i for i, node in enumerate(prior['nodes'])
                         for child in node.get('children', [])}
        for skin in self.gltf['skins']:
            for joint in skin['joints']:
                node = joint
                while node in before_parent:
                    self.assertEqual(parent.get(node), before_parent[node])
                    node = before_parent[node]
        self.assertEqual(self.gltf['scenes'][0]['nodes'], prior['scenes'][0]['nodes'] + meshes)

    def test_leaves_omit_empty_children_instead_of_emitting_invalid_entities(self):
        invalid = [i for i, node in enumerate(self.gltf['nodes']) if node.get('children') == []]
        self.assertEqual(invalid, [], 'Khronos EMPTY_ENTITY on exported leaf nodes')

    def test_joint_indices_with_zero_influence_are_canonical_zero(self):
        violations = 0
        for mesh in self.gltf['meshes']:
            for primitive in mesh['primitives']:
                attrs = primitive['attributes']
                joints = self.gltf['accessors'][attrs['JOINTS_0']]
                weights = self.gltf['accessors'][attrs['WEIGHTS_0']]
                self.assertEqual((joints['componentType'], weights['componentType']), (5121, 5121))
                joint_view = self.gltf['bufferViews'][joints['bufferView']]
                weight_view = self.gltf['bufferViews'][weights['bufferView']]
                jo = joint_view.get('byteOffset', 0) + joints.get('byteOffset', 0)
                wo = weight_view.get('byteOffset', 0) + weights.get('byteOffset', 0)
                for index in range(joints['count']):
                    for component in range(4):
                        j = self.binary[jo + index * joint_view.get('byteStride', 4) + component]
                        w = self.binary[wo + index * weight_view.get('byteStride', 4) + component]
                        violations += int(w == 0 and j != 0)
        self.assertEqual(violations, 0, 'Khronos ACCESSOR_JOINTS_USED_ZERO_WEIGHT')

class PortableNormalization(unittest.TestCase):
    def fixture(self):
        description = {'nodes': [{'children': [1]}, {'name': 'leaf', 'children': []}],
            'meshes': [{'primitives': [{'attributes': {'JOINTS_0': 0, 'WEIGHTS_0': 1}}]}],
            'accessors': [{'componentType': 5121, 'type': 'VEC4', 'count': 1, 'bufferView': 0},
                          {'componentType': 5121, 'type': 'VEC4', 'count': 1, 'bufferView': 1, 'normalized': True}],
            'bufferViews': [{'buffer': 0, 'byteOffset': 4, 'byteLength': 4},
                            {'buffer': 0, 'byteOffset': 8, 'byteLength': 4}]}
        return description, bytearray([19, 20, 21, 22, 3, 4, 5, 6, 255, 0, 0, 0, 23, 24])

    def test_only_zero_weight_ids_and_empty_child_properties_change(self):
        description, binary = self.fixture()
        before = bytes(binary)
        counts = M.normalize_portable_structure(description, binary)
        self.assertEqual(binary, bytearray([19, 20, 21, 22, 3, 0, 0, 0, 255, 0, 0, 0, 23, 24]))
        self.assertEqual(description['nodes'], [{'children': [1]}, {'name': 'leaf'}])
        self.assertEqual(counts, {'emptyLeafPropertiesRemoved': 1, 'zeroWeightJointIdsCleared': 3})
        for transforms in ([2, 3, 5, 7, 11, 13, 17], [-2, 8, -5, 9, -11, 4, 12]):
            prior = sum(transforms[before[4 + k]] * before[8 + k] for k in range(4))
            after = sum(transforms[binary[4 + k]] * binary[8 + k] for k in range(4))
            self.assertEqual(prior, after)
        self.assertEqual(M.normalize_portable_structure(description, binary),
            {'emptyLeafPropertiesRemoved': 0, 'zeroWeightJointIdsCleared': 0})

    def test_unexpected_layouts_and_buffer_ranges_are_rejected(self):
        for target, key, value in [('accessor', 'componentType', 5123),
                                   ('accessor', 'count', 5), ('view', 'byteOffset', 1000)]:
            description, binary = self.fixture()
            before = bytes(binary)
            entry = description['accessors'][0] if target == 'accessor' else description['bufferViews'][0]
            entry[key] = value
            with self.assertRaises(ValueError):
                M.normalize_portable_structure(description, binary)
            self.assertEqual(bytes(binary), before)


class PortableHierarchy(unittest.TestCase):
    def fixture(self):
        return {'nodes': [{'name': 'animated-root', 'children': [1, 2]},
                          {'name': 'joint', 'translation': [0, 1, 0]},
                          {'name': 'mesh-instance', 'mesh': 0, 'skin': 0}],
                'skins': [{'joints': [1], 'skeleton': 1}],
                'scenes': [{'nodes': [0]}, {'nodes': [0]}],
                'animations': [{'channels': [{'target': {'node': 0, 'path': 'translation'}}]}]}

    def normalize(self, document):
        self.assertTrue(callable(getattr(M, 'normalize_skinned_roots', None)), 'Missing portable hierarchy normalizer')
        return M.normalize_skinned_roots(document)

    def test_promotes_to_every_original_scene_preserving_joints_and_animation(self):
        d = self.fixture()
        before = copy.deepcopy(d)
        self.assertEqual(self.normalize(d), {'promotedMeshNodes': [2]})
        self.assertEqual(d['nodes'][0]['children'], [1])
        self.assertEqual(d['nodes'][1:], before['nodes'][1:])
        self.assertEqual(d['animations'], before['animations'])
        self.assertEqual(d['skins'], before['skins'])
        self.assertEqual(d['scenes'], [{'nodes': [0, 2]}, {'nodes': [0, 2]}])
        after = copy.deepcopy(d)
        self.assertEqual(self.normalize(d), {'promotedMeshNodes': []})
        self.assertEqual(d, after)

    def test_scene_membership_is_not_expanded_to_unrelated_scenes(self):
        d = self.fixture()
        d['nodes'].append({'name': 'unrelated'})
        d['scenes'][1]['nodes'] = [3]
        self.normalize(d)
        self.assertEqual(d['scenes'], [{'nodes': [0, 2]}, {'nodes': [3]}])

    def test_nested_instance_is_promoted_without_changing_joint_ancestors(self):
        d = self.fixture()
        d['nodes'][0]['children'] = [1, 3]
        d['nodes'].append({'name': 'group', 'children': [2]})
        self.normalize(d)
        self.assertEqual(d['nodes'][0]['children'], [1, 3])
        self.assertNotIn('children', d['nodes'][3])
        self.assertEqual(d['scenes'][0]['nodes'], [0, 2])

    def test_invalid_graphs_and_out_of_scope_instances_reject_without_mutation(self):
        def change(kind):
            d = self.fixture()
            if kind == 'cycle': d['nodes'][1]['children'] = [0]
            if kind == 'duplicate-parent': d['nodes'][1]['children'] = [2]
            if kind == 'bad-index': d['nodes'][0]['children'].append(99)
            if kind == 'bool-index': d['nodes'][0]['children'].append(True)
            if kind == 'non-leaf': d['nodes'][2]['children'] = [3]; d['nodes'].append({})
            if kind == 'mesh-is-joint': d['skins'][0]['joints'].append(2)
            if kind == 'local-transform': d['nodes'][2]['translation'] = [0, 1, 0]
            if kind == 'animated-instance': d['animations'][0]['channels'][0]['target']['node'] = 2
            if kind == 'missing-scene': d['scenes'] = []
            if kind == 'unreachable': d['scenes'] = [{'nodes': [3]}]; d['nodes'].append({})
            if kind == 'non-root-scene': d['scenes'][0]['nodes'] = [1]
            return d
        for kind in ('cycle', 'duplicate-parent', 'bad-index', 'bool-index', 'non-leaf',
                     'mesh-is-joint', 'local-transform', 'animated-instance',
                     'missing-scene', 'unreachable', 'non-root-scene'):
            with self.subTest(kind=kind):
                d = change(kind); before = copy.deepcopy(d)
                self.assertTrue(callable(getattr(M, 'normalize_skinned_roots', None)))
                with self.assertRaises(ValueError): M.normalize_skinned_roots(d)
                self.assertEqual(d, before)


if __name__ == '__main__':
    unittest.main()
