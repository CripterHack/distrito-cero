#!/usr/bin/env python3
"""Export a version-identified neutral authoring asset without replacing history.

Reuses the existing textured rig/animation exporter. A current source snapshot is
not equivalent to native DQ deformation or an artistic approval. No network use.
"""
from pathlib import Path
import argparse
import hashlib
from importlib.metadata import version as package_version
import shutil
import struct
import subprocess
import sys
import tempfile
import json

ROOT = Path(__file__).resolve().parents[1]
INPUTS = (
    'version.json', 'build-info.json', 'tools/export_current_human.py',
    'tools/export_traits_glb.py', 'src/core.js', 'src/character-fit.js',
    'src/character-motion.js', 'src/skin-rig.js', 'src/hero-asset.js',
    'src/hair-geometry.js', 'src/visual-geometry.js',
    'assets/anatomy-source/skin-repaired.webp',
    'assets/anatomy-source/normal.webp', 'assets/anatomy-source/roughness.webp',
    'assets/ATTRIBUTION-v09.md',
)


def source_hashes():
    """Identify every byte consumed by the legacy exporter and its declaration."""
    return {path: hashlib.sha256((ROOT / path).read_bytes()).hexdigest() for path in INPUTS}


def normalize_portable_structure(description, binary):
    """Fix only schema-empty leaves and mathematically unused influence IDs.

    Positions, normals, UVs, weights, indices, matrices, clips and node parents
    are untouched. This deliberately does not attempt a new material or rig.
    The historical byte-weight layout is required, not guessed from bytes.
    """
    empty_leaves = 0
    for node in description['nodes']:
        if node.get('children') == []:
            del node['children']
            empty_leaves += 1
    edits = {}
    for mesh in description['meshes']:
        for primitive in mesh['primitives']:
            attrs = primitive['attributes']
            if 'JOINTS_0' not in attrs and 'WEIGHTS_0' not in attrs:
                continue
            joints = description['accessors'][attrs['JOINTS_0']]
            weights = description['accessors'][attrs['WEIGHTS_0']]
            if any(a.get('componentType') != 5121 or a.get('type') != 'VEC4'
                   or 'sparse' in a for a in (joints, weights)) or not weights.get('normalized'):
                raise ValueError('Unsupported portable influence layout')
            count = joints.get('count')
            if not isinstance(count, int) or count < 1 or weights.get('count') != count:
                raise ValueError('Mismatched portable influence counts')
            layouts = []
            for accessor in (joints, weights):
                view = description['bufferViews'][accessor['bufferView']]
                offset = view.get('byteOffset', 0) + accessor.get('byteOffset', 0)
                stride = view.get('byteStride', 4)
                end = offset + (count - 1) * stride + 4
                if (view.get('buffer') != 0 or stride < 4 or offset < 0
                        or end > len(binary)
                        or end > view.get('byteOffset', 0) + view['byteLength']):
                    raise ValueError('Portable influence range exceeds its buffer')
                layouts.append((offset, stride))
            (jo, js), (wo, ws) = layouts
            for index in range(count):
                for component in range(4):
                    jp, wp = jo + index * js + component, wo + index * ws + component
                    required = binary[jp] if binary[wp] else 0
                    if jp in edits and edits[jp] != required:
                        raise ValueError('Aliased joint accessor has contradictory influences')
                    edits[jp] = required
    cleared = sum(binary[offset] != value for offset, value in edits.items())
    for offset, value in edits.items():
        binary[offset] = value
    return {'emptyLeafPropertiesRemoved': empty_leaves, 'zeroWeightJointIdsCleared': cleared}


def normalize_skinned_roots(description):
    """Promote leaf skin instances, preserving every joint's world transform.

    glTF ignores the transform of a skinned mesh instance and its parents;
    joint transforms still apply. Only scene membership and links to these
    leaves change. Unsupported graphs fail before any mutation.
    """
    nodes, scenes = description['nodes'], description.get('scenes')
    if not nodes or not scenes:
        raise ValueError('Portable hierarchy requires nodes and scenes')
    valid_id = lambda i: type(i) is int and 0 <= i < len(nodes)
    parents = {}
    for i, node in enumerate(nodes):
        for child in node.get('children', []):
            if not valid_id(child) or child in parents:
                raise ValueError('Invalid node index or multiple parents')
            parents[child] = i
    roots = {}
    for i in range(len(nodes)):
        current, seen = i, set()
        while current in parents:
            if current in seen:
                raise ValueError('Cycle in portable hierarchy')
            seen.add(current)
            current = parents[current]
        roots[i] = current
    for scene in scenes:
        entries = scene.get('nodes', [])
        if any(not valid_id(i) or i in parents for i in entries) or len(set(entries)) != len(entries):
            raise ValueError('Scene must contain unique root node indices')
    moving = [i for i, node in enumerate(nodes) if 'mesh' in node and 'skin' in node and i in parents]
    joints = {i for skin in description.get('skins', []) for i in skin['joints']}
    animated = {channel['target'].get('node') for clip in description.get('animations', [])
                for channel in clip['channels']}
    for i in moving:
        node = nodes[i]
        if (node.get('children') or i in joints or i in animated
                or any(key in node for key in ('matrix', 'translation', 'rotation', 'scale'))):
            raise ValueError('Only untransformed, unanimated, non-joint leaf instances can be promoted')
        if not any(roots[i] in scene.get('nodes', []) for scene in scenes):
            raise ValueError('Skinned instance is not reachable from a scene')
    additions = [[i for i in moving if roots[i] in scene.get('nodes', [])] for scene in scenes]
    moving_set = set(moving)
    for node in nodes:
        if moving_set.intersection(node.get('children', [])):
            remaining = [i for i in node['children'] if i not in moving_set]
            if remaining:
                node['children'] = remaining
            else:
                del node['children']
    for scene, added in zip(scenes, additions):
        if added:
            scene['nodes'] = scene.get('nodes', []) + added
    return {'promotedMeshNodes': moving}


def export_current(destination):
    destination = Path(destination).resolve()
    if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / 'artifacts'):
        raise ValueError('Use a fresh artifacts directory, never a versioned source directory')
    version = json.loads((ROOT / 'version.json').read_text())['version']
    sources = source_hashes()
    destination.mkdir(parents=True, exist_ok=False)
    # The historical command writes fixed v0.16 filenames. Run it only in a
    # private copy of its exact inputs. Normalize only empty leaves and unused
    # joint IDs in the portable result; tracked historical files stay put.
    filename = 'dc-human-' + version + '-neutral.glb'
    with tempfile.TemporaryDirectory(prefix='dc-current-human-') as scratch:
        staged = Path(scratch)
        for path in INPUTS:
            target = staged / path
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / path, target)
        subprocess.run([sys.executable, str(staged / 'tools/export_traits_glb.py')],
                       cwd=staged, check=True, capture_output=True, text=True, timeout=180)
        raw = (staged / 'assets/dc016-human-traits.glb').read_bytes()
        magic, revision, length = struct.unpack_from('<4sII', raw)
        if (magic, revision, length) != (b'glTF', 2, len(raw)):
            raise ValueError('Invalid historical exporter output')
        json_length, kind = struct.unpack_from('<II', raw, 12)
        if kind != 0x4e4f534a:
            raise ValueError('Missing GLB JSON chunk')
        binary_offset = 20 + json_length
        binary_length, binary_kind = struct.unpack_from('<II', raw, binary_offset)
        if binary_kind != 0x004e4942 or binary_offset + 8 + binary_length != len(raw):
            raise ValueError('Expected one complete embedded GLB binary chunk')
        binary = bytearray(raw[binary_offset + 8:])
        description = json.loads(raw[20:20 + json_length])
        normalization = normalize_portable_structure(description, binary)
        hierarchy = normalize_skinned_roots(description)
        description['asset']['generator'] = 'Distrito Cero current human exporter v' + version
        description['nodes'][0]['name'] = 'DC human ' + version + ' neutral fitted neck and classic groom'
        description['extras']['sourceManifest'] = sources
        encoded = json.dumps(description, separators=(',', ':'), ensure_ascii=False).encode()
        encoded += b' ' * (-len(encoded) % 4)
        tail = struct.pack('<II', len(binary), 0x004e4942) + binary
        output = (struct.pack('<4sII', b'glTF', 2, 20 + len(encoded) + len(tail))
                  + struct.pack('<II', len(encoded), 0x4e4f534a) + encoded + tail)
        (destination / filename).write_bytes(output)
        result = {'file': filename, 'bytes': len(output), 'meshes': len(description['meshes']),
                  'nodes': len(description['nodes']), 'animations': len(description['animations'])}
    if source_hashes() != sources:
        raise RuntimeError('An export input changed during generation')
    result.update({
        'schema': 1, 'assetId': 'human-neutral-authoring', 'productVersion': version,
        'sha256': hashlib.sha256((destination / filename).read_bytes()).hexdigest(),
        'sources': sources, 'portableNormalization': normalization, 'portableHierarchy': hierarchy,
        'toolchain': {'python': sys.version.split()[0],
                      'node': subprocess.check_output(['node', '--version'], text=True).strip(),
                      **{name: package_version(name) for name in ('numpy', 'scipy', 'Pillow')}},
        'units': 'metres', 'upAxis': '+Y', 'forwardAxis': '+Z',
        'profile': 'neutral, neckLength=0, classic groom, detailed mesh',
        'runtimeSkinningEquivalent': False, 'officialValidation': 'not-run',
        'artisticAcceptance': 'pending', 'ownContentLicense': 'owner-decision-pending',
        'thirdPartyDeclaration': 'assets/ATTRIBUTION-v09.md; no new license granted',
        'limitations': [
            'Native DQ skinning and standard glTF linear skinning can differ in posed surfaces.',
            'Eleven sampled procedural clips, not motion capture or all equipment interactions.',
            'One neutral fitted profile, not every creator setting or crowd LOD.',
            'Portable material approximation; native blink, gaze and shader detail are not exported.',
            'Structural validation does not approve visual quality or physical GPU performance.',
        ],
    })
    (destination / 'source-manifest.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='Fresh output directory; existing directories are refused')
    args = parser.parse_args()
    result = export_current(args.output)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
