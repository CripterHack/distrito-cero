#!/usr/bin/env python3
"""Deterministic offline build. Product identity is not a save-schema version."""
from pathlib import Path
from datetime import date
import argparse
import hashlib
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parent
SOURCES = ['core.js', 'world.js', 'frontier-world.js', 'police.js', 'simulation.js', 'dynamics.js', 'interactions.js', 'frontier-simulation.js', 'occupancy.js', 'appearance.js', 'weapon-handling.js', 'equipment.js', 'equipment-simulation.js', 'save-store.js', 'character-fit.js', 'character-motion.js', 'vehicle-asset.js', 'skin-rig.js', 'dual-quaternion.js', 'crowd-geometry.js', 'visual-geometry.js', 'hero-asset.js', 'hair-geometry.js', 'human-materials.js', 'graphics-resources.js', 'renderer.js', 'reactive-renderer.js', 'realism-renderer.js', 'frontier-renderer.js', 'cast-renderer.js', 'equipment-geometry.js', 'equipment-renderer.js', 'audio.js', 'app.js', 'frontier-ui.js', 'identity-ui.js', 'equipment-ui.js', 'graphics-recovery.js']


def load_release(root):
    data = json.loads((root / 'version.json').read_text(encoding='utf-8'))
    fields = {'schema', 'version', 'name', 'channel', 'date'}
    if not isinstance(data, dict) or set(data) != fields:
        raise ValueError('version.json must contain only the documented product identity fields')
    if type(data['schema']) is not int or data['schema'] != 1:
        raise ValueError('Unsupported version manifest schema')
    if not isinstance(data['version'], str) or not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)', data['version']):
        raise ValueError('Product version must be three non-negative integers')
    name = data['name']
    if not isinstance(name, str) or not 1 <= len(name) <= 48 or name != name.strip() or not all(c.isalnum() or c in ' .·' for c in name):
        raise ValueError('Invalid release name')
    if data['channel'] != 'prototype':
        raise ValueError('This project has not approved another release channel')
    if not isinstance(data['date'], str) or date.fromisoformat(data['date']).isoformat() != data['date']:
        raise ValueError('Release date must be a canonical calendar date')
    version = data['version']
    label = 'v' + (version[:-2] if version.endswith('.0') else version)
    return dict(data, label=label)


def render(root=ROOT):
    root = Path(root)
    release = load_release(root)
    # Hash declared inputs, not wall time, absolute paths or a future Git commit.
    paths = ['version.json', 'build.py', 'src/page.html', 'src/style.css'] + ['src/' + n for n in SOURCES]
    digest = hashlib.sha256()
    inputs = {}
    for name in paths:
        raw = (root / name).read_bytes()
        digest.update(name.encode('utf-8') + b'\0' + raw + b'\0')
        inputs[name] = raw.decode('utf-8')
    source_sha = digest.hexdigest()
    info = dict(release, product='Distrito Cero', sourceSha256=source_sha)
    payload = json.dumps(info, ensure_ascii=True, separators=(',', ':'))
    # Embedded in the single script: no version request while playing.
    identity = '\nDC.BuildInfo = Object.freeze(' + payload + ');\n'
    chunks = [inputs['src/' + name] + (identity if name == 'core.js' else '') for name in SOURCES]
    js = '\n\n'.join(chunks)
    if '</script' in js.lower():
        raise ValueError('Unsafe closing script tag in source')
    page = inputs['src/page.html']
    for marker in ['/*__CSS__*/', '/*__JS__*/']:
        if page.count(marker) != 1:
            raise ValueError('Template requires exactly one ' + marker)
    tokens = {
        '{{BUILD_TITLE}}': 'Distrito Cero ' + release['label'] + ' · ' + release['name'],
        '{{BUILD_VERSION}}': release['version'],
        '{{BUILD_LABEL}}': release['label'],
        '{{BUILD_NAME}}': release['name'],
        '{{BUILD_NAME_UPPER}}': release['name'].upper(),
        '{{BUILD_SOURCE}}': source_sha,
        '{{BUILD_SHORT}}': source_sha[:12],
    }
    for token, value in tokens.items():
        page = page.replace(token, html.escape(value, quote=True))
    if '{{BUILD_' in page:
        raise ValueError('Unresolved release template marker')
    output = page.replace('/*__CSS__*/', inputs['src/style.css']).replace('/*__JS__*/', js).encode('utf-8')
    sidecar = dict(info, htmlSha256=hashlib.sha256(output).hexdigest(), htmlBytes=len(output))
    return {'index.html': output, 'build-info.json': (json.dumps(sidecar, ensure_ascii=False, indent=2) + '\n').encode('utf-8')}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Verify outputs without mutating them')
    args = parser.parse_args(argv)
    try:
        outputs = render()
        if args.check:
            stale = [n for n, b in outputs.items() if not (ROOT/n).is_file() or (ROOT/n).read_bytes() != b]
            if stale:
                raise ValueError('Stale or missing generated outputs: ' + ', '.join(stale))
        else:
            for name, content in outputs.items():
                temporary = ROOT / (name + '.tmp')
                temporary.write_bytes(content)
                temporary.replace(ROOT / name)
        release = json.loads(outputs['build-info.json'])
        print(('Verified' if args.check else 'Created') + ' Distrito Cero ' + release['label'] +
              ': ' + str(release['htmlBytes']) + ' HTML bytes; source ' + release['sourceSha256'][:12] +
              '; no external runtime dependencies.')
        return 0
    except (OSError, ValueError, TypeError, KeyError) as error:
        print('Build failed: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
