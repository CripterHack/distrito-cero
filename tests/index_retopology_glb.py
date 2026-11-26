"""Verify the delivered character GLB against the editable scene in fresh Blender."""
import hashlib
import json
import struct
import sys
from pathlib import Path

import bpy
import numpy as np

source, glb = map(Path, sys.argv[sys.argv.index("--") + 1:])
blob = glb.read_bytes()
json_size = struct.unpack_from("<I", blob, 12)[0]
doc = json.loads(blob[20:20 + json_size])
binary = memoryview(blob)[28 + json_size:]


def floats(index, width):
    accessor = doc["accessors"][index]
    assert accessor["componentType"] == 5126 and accessor["type"] == f"VEC{width}"
    view = doc["bufferViews"][accessor["bufferView"]]
    start = view.get("byteOffset", 0) + accessor.get("byteOffset", 0)
    return np.ndarray((accessor["count"], width), dtype="<f4", buffer=binary, offset=start,
                      strides=(view.get("byteStride", 4 * width), 4))


def packed_maps():
    images = [image for image in bpy.data.images if image.packed_file]
    assert len(images) == 3 and all(tuple(im.size) == (4096, 4096) for im in images)
    return {im.name: hashlib.sha256(im.packed_file.data).hexdigest() for im in images}


mesh, = doc["meshes"]
node, = doc["nodes"]
assert node["mesh"] == 0 and len(doc["materials"]) == 2
names = ["Prueba.Indice.L", "Prueba.Indice.R"]
assert mesh["extras"]["targetNames"] == names and mesh["weights"] == [0, 0]
outside, wall = mesh["primitives"]
outer_material = doc["materials"][outside["material"]]
assert "baseColorTexture" in outer_material["pbrMetallicRoughness"] and "normalTexture" in outer_material
assert "COLOR_0" not in outside["attributes"], "Vertex color would tint the textured exterior"
assert "COLOR_0" in wall["attributes"] and outside["material"] != wall["material"]
for primitive in mesh["primitives"]:
    attrs = primitive["attributes"]
    tangent = floats(attrs["TANGENT"], 4)
    normals = floats(attrs["NORMAL"], 3)
    assert np.isfinite(tangent).all() and np.all(np.abs(tangent[:, 3]) == 1)
    assert np.max(np.abs(np.linalg.norm(tangent[:, :3], axis=1) - 1)) < .001
    assert np.max(np.abs(np.sum(tangent[:, :3] * normals, axis=1))) < .001
    assert len(primitive["targets"]) == 2
    for target in primitive["targets"]:
        assert "POSITION" in target and "NORMAL" in target
bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
expected = packed_maps()
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(glb.resolve()))
obj, = bpy.context.scene.objects
assert obj.type == "MESH" and packed_maps() == expected
basis, left, right = obj.data.shape_keys.key_blocks
assert [left.name, right.name] == names and left.value == right.value == 0
for key, side in ((left, 1), (right, -1)):
    moved = [(b.co, (v.co - b.co).length) for v, b in zip(key.data, basis.data, strict=True)
             if (v.co - b.co).length > 1e-6]
    assert max(distance for _, distance in moved) > .005
    assert all((obj.matrix_world @ position).y * side > .7 for position, _ in moved)
print("Reopened one mesh, two independent index morphs and three byte-identical 4K images.")
print("Verified material-specific vertex colors and finite orthonormal tangent frames on both primitives.")
