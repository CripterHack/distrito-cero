#!/usr/bin/env python3
"""Bundle the original sources into one offline HTML, without third-party packages."""
from pathlib import Path
root = Path(__file__).resolve().parent
sources = ['core.js', 'world.js', 'frontier-world.js', 'police.js', 'simulation.js', 'dynamics.js', 'interactions.js', 'frontier-simulation.js', 'occupancy.js', 'appearance.js', 'weapon-handling.js', 'equipment.js', 'equipment-simulation.js', 'save-store.js', 'character-fit.js', 'character-motion.js', 'vehicle-asset.js', 'skin-rig.js', 'dual-quaternion.js', 'crowd-geometry.js', 'visual-geometry.js', 'hero-asset.js', 'hair-geometry.js', 'human-materials.js', 'graphics-resources.js', 'renderer.js', 'reactive-renderer.js', 'realism-renderer.js', 'frontier-renderer.js', 'cast-renderer.js', 'equipment-geometry.js', 'equipment-renderer.js', 'audio.js', 'app.js', 'frontier-ui.js', 'identity-ui.js', 'equipment-ui.js', 'graphics-recovery.js']
page = (root / 'src/page.html').read_text(encoding='utf-8')
css = (root / 'src/style.css').read_text(encoding='utf-8')
js = '\n\n'.join((root / 'src' / name).read_text(encoding='utf-8') for name in sources)
if '</script' in js.lower():
    raise ValueError('Unsafe closing script tag in source')
output = page.replace('/*__CSS__*/', css).replace('/*__JS__*/', js)
(root / 'index.html').write_text(output, encoding='utf-8')
print(f'Created index.html: {len(output.encode("utf-8")):,} bytes, {len(sources)} source files, no external runtime dependencies.')
