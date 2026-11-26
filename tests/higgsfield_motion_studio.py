"""Run on the saved four-action .blend with Blender's --python-exit-code 1."""

import math

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector


def set_frame(scene, value):
    whole = math.floor(value)
    scene.frame_set(whole, subframe=value - whole)


def pose(rig):
    return {bone.name: bone.matrix.copy() for bone in rig.pose.bones}


def assert_pose_equal(rig, expected):
    for bone in rig.pose.bones:
        matrix = expected[bone.name]
        error = max(abs(a - b) for row_a, row_b in zip(bone.matrix, matrix) for a, b in zip(row_a, row_b))
        assert error < 1e-4, (bone.name, error)


scene = bpy.context.scene
(rig,) = [obj for obj in scene.objects if obj.type == "ARMATURE"]
(body,) = [obj for obj in scene.objects if obj.type == "MESH" and obj.data.shape_keys]
tracks = rig.animation_data.nla_tracks
assert rig.animation_data.action is None and len(rig.data.bones) == 49
assert {key.name for key in body.data.shape_keys.key_blocks} >= {"Prueba.Indice.L", "Prueba.Indice.R"}
images = [image for image in bpy.data.images if image.source == "FILE"]
assert len(images) == 3 and all(image.packed_file and tuple(image.size) == (4096, 4096) for image in images)
assert {track.name for track in tracks} == {"Marcha", "Reposo", "Carrera", "Giro"}

expected_start = scene.frame_start
for name, repeats in (("Marcha", 4), ("Reposo", 1), ("Carrera", 4), ("Giro", 1)):
    track = tracks[name]
    (strip,) = track.strips
    assert not track.mute and not strip.mute
    assert strip.repeat == repeats and abs(strip.scale - 1) < 1e-5
    assert strip.frame_start == expected_start, (name, strip.frame_start, expected_start)
    assert any(m.frame == strip.frame_start and m.name.startswith(name) for m in scene.timeline_markers)
    first, last = strip.action.frame_range
    assert abs(strip.frame_end - strip.frame_start - repeats * (last - first)) < .001
    expected_start = math.ceil(strip.frame_end)

    for phase in (.25, .625):
        set_frame(scene, strip.frame_start + (repeats - 1 + phase) * (last - first))
        expected = pose(rig)
        rig.animation_data.use_nla = False
        for bone in rig.pose.bones:
            bone.matrix_basis = Matrix.Identity(4)
        rig.animation_data.action = strip.action
        set_frame(scene, first + phase * (last - first))
        assert_pose_equal(rig, expected)
        rig.animation_data.action = None
        rig.animation_data.use_nla = True

turn = tracks["Giro"].strips[0]
duration = (turn.frame_end - turn.frame_start) * scene.render.fps_base / scene.render.fps
assert abs(duration - 1.4) < .001 and scene.frame_end >= math.ceil(turn.frame_end) + 6
assert turn.extrapolation == "HOLD_FORWARD"

orientations = []
for offset in range(math.ceil(turn.frame_end - turn.frame_start) + 1):
    frame = min(turn.frame_start + offset, turn.frame_end)
    set_frame(scene, frame)
    orientations.append((rig.matrix_world @ rig.pose.bones["pelvis"].matrix).to_quaternion())
    evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    for corner in evaluated.bound_box:
        point = world_to_camera_view(scene, scene.camera, evaluated.matrix_world @ Vector(corner))
        assert .015 < point.x < .985 and .015 < point.y < .985 and point.z > 0, (frame, point)

rotation = orientations[-1] @ orientations[0].inverted()
axis, angle = rotation.to_axis_angle()
assert abs(math.pi - angle) < .02 and abs(axis.z) > .99, (axis, angle)
# Guard the last keyed sample. Some looping NLA settings return to frame zero at the strip end.
finish = pose(rig)
scene.frame_set(scene.frame_end)
assert_pose_equal(rig, finish)
print(f"Estudio verificado: 4 acciones, 49 huesos, 3 mapas empaquetados 4K, giro {duration:.3f} s y pose final retenida.")
