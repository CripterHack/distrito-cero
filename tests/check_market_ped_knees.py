"""Run with blender -b --python-exit-code 1 --python tests/check_market_ped_knees.py."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

import numpy as np
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
PHASES = 129
# Exercise the same packed vertex data and local pose sampler used by WebGL.
EXPORT = """
const fs = require('node:fs'), vm = require('node:vm'), path = require('node:path');
const [dir, phases] = process.argv.slice(1);
const ctx = vm.createContext({DC: {}, atob, Uint8Array, Float32Array, DataView});
for (const name of ['data', 'pose', 'asset'])
  vm.runInContext(fs.readFileSync('src/market-ped-' + name + '.js', 'utf8'), ctx);
const asset = ctx.DC.MarketPedAsset;
function save(name, values) {
  fs.writeFileSync(path.join(dir, name), Buffer.from(values.buffer));
}
for (const lod of [0, 1]) save('mesh' + lod, asset.decodeLevel(lod));
for (const [name, walk, run] of [['Reposo', 0, 0], ['Marcha', 1, 0], ['Carrera', 1, 1], ['Transicion', 1, .5]]) {
  const matrices = new Float32Array(phases * 49 * 16);
  for (let i = 0; i < phases; i++) {
    const phase = i / (phases - 1);
    asset.writePalette(matrices.subarray(i * 49 * 16), phase, phase, walk, run);
  }
  save(name, matrices);
}
"""


def self_contacts(points, triangles, canonical):
    tree = BVHTree.FromPolygons(points.tolist(), triangles, all_triangles=True)
    return {(a, b) for a, b in tree.overlap(tree)
            if a < b and not set(canonical[a]).intersection(canonical[b])}


def check_leg(vertices, sign, clips, lod):
    centers = vertices[:, :, :3].mean(axis=1)
    # Capture the full 30 cm band around each knee in the GLB's Y-up bind pose.
    band = vertices[(sign * centers[:, 0] > .015) & (np.abs(centers[:, 1] - .5) < .15)]
    assert len(band) > 0
    rows = band.reshape(-1, 16)
    skin, indices = np.unique(rows[:, [0, 1, 2, 8, 9, 10, 11, 12, 13, 14, 15]],
                              axis=0, return_inverse=True)
    faces = indices.reshape(-1, 3)
    _, same_position = np.unique(skin[:, :3], axis=0, return_inverse=True)
    canonical = same_position[faces]
    triangles = faces.tolist()
    rest = self_contacts(skin[:, :3], triangles, canonical)
    homogeneous = np.column_stack([skin[:, :3], np.ones(len(skin))])
    joints, weights = skin[:, 3:7].astype(int), skin[:, 7:]
    for name, clip in clips.items():
        for frame, palette in enumerate(clip):
            transforms = np.einsum('ij,ijxy->ixy', weights, palette[joints])
            deformed = np.einsum('ixy,iy->ix', transforms, homogeneous)[:, :3]
            contacts = self_contacts(deformed, triangles, canonical) - rest
            assert not contacts, (lod, sign, name, frame, contacts)


with TemporaryDirectory() as directory:
    out = Path(directory)
    subprocess.run(['node', '-e', EXPORT, directory, str(PHASES)], cwd=ROOT, check=True)
    clips = {}
    for name in ['Reposo', 'Marcha', 'Carrera', 'Transicion']:
        column_major = np.fromfile(out / name, dtype='<f4').reshape(PHASES, 49, 4, 4)
        clips[name] = column_major.swapaxes(-1, -2)
    for lod in [0, 1]:
        vertices = np.fromfile(out / f'mesh{lod}', dtype='<f4').reshape(-1, 3, 16)
        for sign in [-1, 1]:
            check_leg(vertices, sign, clips, lod)
print(f"Street LOD knees passed {PHASES} phases of four poses on both legs and both meshes.")
