"""Run on the saved Mercado resident .blend with Blender's --python-exit-code 1."""

import math
import sys

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
strips = {strip.action.name.split("_")[0]: strip for track in tracks for strip in track.strips}
brakes = ("FrenadaL", "FrenadaR")
assert all(not t.mute for t in tracks)
has_brakes = any(name.startswith("Frenada") for name in strips)
expected = {"Marcha", "Reposo", "Carrera", "Giro"}
assert set(strips) == (expected.union(brakes) if has_brakes else expected)
if "--brakes" in sys.argv:
    assert has_brakes, "Faltan las dos frenadas en el estudio"
hold_frames = round(.5 * scene.render.fps / scene.render.fps_base)


expected_start = scene.frame_start
sequence = [("Marcha", 4), ("Reposo", 1), ("Carrera", 4), ("Giro", 1)]
if has_brakes:
    sequence.extend((name, 1) for name in brakes)
for name, repeats in sequence:
    strip = strips[name]
    assert not strip.mute
    assert strip.repeat == repeats and abs(strip.scale - 1) < 1e-5
    assert strip.frame_start == expected_start, (name, strip.frame_start, expected_start)
    assert any(m.frame == strip.frame_start and m.name.startswith(name) for m in scene.timeline_markers)
    first, last = strip.action.frame_range
    assert abs(strip.frame_end - strip.frame_start - repeats * (last - first)) < .001
    expected_start = math.ceil(strip.frame_end)
    if name == "Giro" or name.startswith("Frenada"):
        expected_start += hold_frames + 1

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

turn = strips["Giro"]
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
scene.frame_set(math.ceil(turn.frame_end) + hold_frames)
assert_pose_equal(rig, finish)

if has_brakes:
    walk = strips["Marcha"]
    set_frame(scene, strips["Reposo"].frame_start)
    idle = pose(rig)
    # Orthographic views must include both shoes on the saved rig and in the landscape stills.
    shoe = [v.index for v in body.data.vertices if (body.matrix_world @ v.co).z < .12]
    assert len(shoe) > 100
    scene.render.resolution_x, scene.render.resolution_y = 400, 320
    for name, phase, side in (("FrenadaL", .15, "izquierdo"), ("FrenadaR", .65, "derecho")):
        strip = strips[name]
        duration_s = (strip.frame_end - strip.frame_start) * scene.render.fps_base / scene.render.fps
        assert abs(duration_s - .4898584) < .001
        assert strip.extrapolation == "HOLD_FORWARD"
        set_frame(scene, walk.frame_start + phase * (walk.action_frame_end - walk.action_frame_start))
        entry = pose(rig)
        set_frame(scene, strip.frame_start)
        assert_pose_equal(rig, entry)
        camera = scene.objects[f"Estudio · apoyo {side}"]
        for step in range(5):
            set_frame(scene, strip.frame_start + (strip.frame_end - strip.frame_start) * step / 4)
            evaluated = body.evaluated_get(bpy.context.evaluated_depsgraph_get())
            for i in shoe:
                p = world_to_camera_view(scene, camera, evaluated.matrix_world @ evaluated.data.vertices[i].co)
                assert .04 < p.x < .96 and .04 < p.y < .96 and p.z > 0, (name, step, i, p)
        finish = pose(rig)
        forward = Matrix.Translation((0, -.16532721, 0))  # +Z in glTF becomes -Y in Blender.
        assert_pose_equal(rig, {bone: forward @ m for bone, m in idle.items()})
        scene.frame_set(math.ceil(strip.frame_end) + hold_frames)
        assert_pose_equal(rig, finish)
    assert scene.frame_end == math.ceil(strips["FrenadaR"].frame_end) + hold_frames

print(f"Estudio verificado: {len(strips)} acciones, 49 huesos, 3 mapas empaquetados 4K, giro {duration:.3f} s y pose final retenida.")
