#!/usr/bin/env python3
"""Export a version-identified neutral authoring asset without replacing history.

Reuses the existing textured rig/animation exporter. A current source snapshot is
not equivalent to native DQ deformation or an artistic approval. No network use.
"""
from pathlib import Path
import argparse
import hashlib
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


def export_current(destination):
    destination = Path(destination).resolve()
    if destination.is_relative_to(ROOT) and not destination.is_relative_to(ROOT / 'artifacts'):
        raise ValueError('Use a fresh artifacts directory, never a versioned source directory')
    version = json.loads((ROOT / 'version.json').read_text())['version']
    sources = source_hashes()
    destination.mkdir(parents=True, exist_ok=False)
    # The historical command writes fixed v0.16 filenames. Run it only in a
    # private copy of its exact inputs, then relabel JSON metadata. Mesh and
    # animation buffers are not rewritten, and tracked historical files stay put.
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
        description = json.loads(raw[20:20 + json_length])
        description['asset']['generator'] = 'Distrito Cero current human exporter v' + version
        description['nodes'][0]['name'] = 'DC human ' + version + ' neutral fitted neck and classic groom'
        description['extras']['sourceManifest'] = sources
        encoded = json.dumps(description, separators=(',', ':'), ensure_ascii=False).encode()
        encoded += b' ' * (-len(encoded) % 4)
        tail = raw[20 + json_length:]
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
        'sources': sources, 'units': 'metres', 'upAxis': '+Y', 'forwardAxis': '+Z',
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
