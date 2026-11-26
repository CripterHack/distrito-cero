"""Reopen the delivered edit scene and compare it with a fresh import of its GLB.
blender -b -P tests/higgsfield_hand_scene.py -- INPUT.glb FILE.blend
"""
import hashlib
import sys
from pathlib import Path

import bpy
from mathutils import Vector

source, scene_path = map(Path, sys.argv[sys.argv.index("--")+1:])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
original = next(obj for obj in bpy.context.selected_objects if obj.type == "MESH")


def rest(obj):
    return {
        "positions": [tuple(vertex.co) for vertex in obj.data.vertices],
        "faces": [tuple(face.vertices) for face in obj.data.polygons],
        "normals": [tuple(normal.vector) for normal in obj.data.corner_normals],
        "uv": [tuple(uv.uv) for uv in obj.data.uv_layers.active.data],
        "world": [tuple(row) for row in obj.matrix_world],
        "images": {image.name: hashlib.sha256(image.packed_file.data).hexdigest()
                   for image in bpy.data.images if image.packed_file},
    }


reference = rest(original)
assert len(reference["images"]) == 3
bpy.ops.wm.open_mainfile(filepath=str(scene_path.resolve()))
meshes = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
assert len(meshes) == 1
obj, = meshes
assert rest(obj) == reference, "Rest geometry, normals, UVs, transforms or packed maps changed"
assert obj.data.shape_keys is not None, "Missing index flex probes"
keys = obj.data.shape_keys.key_blocks
assert obj.active_shape_key.name == "Basis"
assert all(k.value == 0 for k in keys)

for side, sign in (("L", 1), ("R", -1)):
    prefix = side+"."
    groups = {group.name: group for group in obj.vertex_groups if group.name.startswith(prefix)}
    assert set(groups) == {prefix + n for n in
        ("Mano", "Pulgar", "Indice", "Medio", "Anular", "Menique", "Puente.IM", "Puente.MA", "Puente.Am")}
    def ids(group):
        return {v.index for v in obj.data.vertices if any(m.group == group.index for m in v.groups)}
    assert all(ids(group) for group in groups.values())
    digit_ids = set()
    for digit in ("Pulgar", "Indice", "Medio", "Anular", "Menique"):
        indices = ids(groups[prefix+digit])
        assert digit_ids.isdisjoint(indices)
        digit_ids.update(indices)
        marker = bpy.data.objects[f"Punta.{digit}.{side}"]
        index = marker["source_vertex"]
        assert index in indices and marker.parent == obj
        p = obj.matrix_world @ obj.data.vertices[index].co
        assert (marker.matrix_world.translation-p).length < 1e-6
        assert p.y*sign == max((obj.matrix_world @ obj.data.vertices[i].co).y*sign for i in indices)
    flex = keys["Prueba.Indice."+side]
    changed = {v.index for v in obj.data.vertices if (v.co-flex.data[v.index].co).length > 1e-7}
    assert len(changed) >= 8
    assert changed <= ids(groups[prefix+"Indice"])
    target = ids(groups[prefix+"Mano"])
    assert all((obj.matrix_world @ obj.data.vertices[i].co).y*sign > .7 for i in target)
    for group in groups.values():
        assert ids(group) <= target
    flex.value = 1.0
    bp = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(bp)
    assert max((ev.data.vertices[i].co-obj.data.vertices[i].co).length for i in changed) > .004
    flex.value = 0
    for view in ("Palma", "Dorso"):
        assert bpy.data.objects[view+"."+side].type == "CAMERA"

assert not obj.find_armature()
print("PASS reopened Blender scene, GLB equality, 18 selection groups, 2 independent flex samples, 4 cameras and 3 packed maps.")
