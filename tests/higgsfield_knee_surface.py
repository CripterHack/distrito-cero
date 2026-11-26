"""Detect crossings between separate faces of the animated trouser knees.

blender -b -t 2 --python-exit-code 1 -P tests/higgsfield_knee_surface.py -- CHARACTER.glb REPORT.json
"""
from hashlib import sha256
import json
from math import floor
from pathlib import Path
import sys

import bpy
from mathutils.bvhtree import BVHTree
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from higgsfield_body_motion import positions


class KneePatch:
    def __init__(self, triangles, rest_ids):
        self.vertices, local = np.unique(triangles, return_inverse=True)
        self.faces = local.reshape(-1, 3).tolist()
        # Treat UV splits as shared vertices, including edges between material islands.
        self.corners = [set(t) for t in rest_ids[triangles]]

    def crossings(self, points):
        tree = BVHTree.FromPolygons(points[self.vertices].tolist(), self.faces, all_triangles=True)
        return {(a, b) for a, b in tree.overlap(tree) if a < b and self.corners[a].isdisjoint(self.corners[b])}


def verify(path, output):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    scene = bpy.context.scene
    rig, = [o for o in scene.objects if o.type == "ARMATURE"]
    mesh, = [o for o in scene.objects if o.type == "MESH" and o.data.shape_keys]
    graph = bpy.context.evaluated_depsgraph_get()
    rig.data.pose_position = "REST"
    graph.update()
    base = positions(mesh.evaluated_get(graph))
    _, rest_ids = np.unique(np.round(base, 7), axis=0, return_inverse=True)
    mesh.data.calc_loop_triangles()
    triangles = np.array([tuple(t.vertices) for t in mesh.data.loop_triangles])
    mid = base[triangles].mean(axis=1)
    patches = {side: KneePatch(triangles[(mid[:, 0]*sign > .015) & (np.abs(mid[:, 1] - .50) < .15)], rest_ids)
               for side, sign in (("L", 1), ("R", -1))}
    assert all(len(p.faces) >= 700 for p in patches.values()), "Knee inspection area missing"
    assert all(not p.crossings(base) for p in patches.values()), "Crossing faces in the bind pose"

    rig.data.pose_position = "POSE"
    rig.animation_data.action = rig.animation_data.nla_tracks["Marcha"].strips[0].action
    start, end = rig.animation_data.action.frame_range
    counts, unique = {s: [] for s in patches}, {s: set() for s in patches}
    for phase in np.linspace(0, 1, 129):
        f = start + phase * (end - start)
        scene.frame_set(floor(f), subframe=f - floor(f))
        points = positions(mesh.evaluated_get(graph))
        for side, patch in patches.items():
            pairs = patch.crossings(points)
            counts[side].append(len(pairs))
            unique[side].update(pairs)
    metrics = {side: {"triangles": len(p.faces), "distinctCrossingPairs": len(unique[side]),
                      "framesWithCrossings": sum(n > 0 for n in counts[side]),
                      "maximumSimultaneousPairs": max(counts[side])}
               for side, p in patches.items()}
    report = {"sha256": sha256(path.read_bytes()).hexdigest(), "clip": "Marcha", "samples": 129,
              "blender": bpy.app.version_string, "knees": metrics}
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
    assert not any(unique.values()), f"Trouser faces cross during the walk: {metrics}"


if __name__ == "__main__":
    verify(*map(Path, sys.argv[sys.argv.index("--") + 1:]))
