"""Create an editable Blender review scene for the Mercado resident's actions.

blender -b -t 2 --python-exit-code 1 -P tools/review_higgsfield_motion.py -- [ORIGINAL.glb] CANDIDATE.glb NEW_DIR [--frames] [--turn-preview]
"""

import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def load(path, reference=False):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    (character,) = [o for o in scene.objects if o.type == "MESH" and o.data.shape_keys]
    if reference:
        transform = Matrix.Rotation(-math.pi / 2, 4, "Z") @ character.matrix_world
        ground = min((transform @ v.co).z for v in character.data.vertices)
        character.matrix_world = Matrix.Translation((0, 0, -ground)) @ transform

    scene.render.engine = "CYCLES"
    scene.cycles.device = "CPU"
    scene.cycles.samples = 32 if reference else 10
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.cycles.seed = 173
    scene.render.resolution_x = 464
    scene.render.resolution_y = 576
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("Estudio")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs[0].default_value = (0.43, 0.49, 0.56, 1)
    background.inputs[1].default_value = 0.40
    for name, position, energy, size, color in [
        ("Principal", (2, -3.8, 4.3), 480, 3.0, (1, 0.91, 0.83)),
        ("Relleno", (-3, -2.2, 2.4), 210, 2.7, (0.80, 0.89, 1)),
        ("Contraluz", (-1.5, 2.7, 3.9), 580, 1.8, (1, 0.94, 0.84)),
    ]:
        bpy.ops.object.light_add(type="AREA", location=position)
        light = bpy.context.object
        light.name = name
        light.data.energy, light.data.size, light.data.color = energy, size, color
        aim(light, (0, 0, 1))

    bpy.ops.mesh.primitive_plane_add(size=200, location=(0, 0, -0.002))
    plane = bpy.context.object
    plane.name = "Ciclorama"
    mat = bpy.data.materials.new("Ciclorama")
    mat.diffuse_color = (0.18, 0.22, 0.25, 1)
    plane.data.materials.append(mat)

    cameras = {}
    for name, degrees in (("oblicua", 30), ("perfil", 84)):
        angle = math.radians(degrees)
        bpy.ops.object.camera_add(location=(4 * math.sin(angle), -4 * math.cos(angle), 1.25))
        camera = bpy.context.object
        camera.name = "Estudio · " + name
        camera.data.type = "ORTHO"
        camera.data.ortho_scale = 2.18
        aim(camera, (0, 0, 0.93))
        cameras[name] = camera
    scene.camera = cameras["oblicua"]
    return scene, cameras


def render(scene, destination):
    scene.render.filepath = str(destination.resolve())
    bpy.ops.render.render(write_still=True)


def reset_pose(rig):
    rig.animation_data.action = None
    for bone in rig.pose.bones:
        bone.matrix_basis = Matrix.Identity(4)


def save_frames(scene, cameras, rig, out):
    durations = {}
    tracks = rig.animation_data.nla_tracks
    for track in tracks:
        track.mute = True
    for view, camera in cameras.items():
        scene.camera = camera
        counts = {"Marcha": 12, "Reposo": 8, "Carrera": 12} if view == "oblicua" else {"Marcha": 4, "Carrera": 4}
        if "Giro" in tracks:
            counts["Giro"] = 5
        for name, count in counts.items():
            action = tracks[name].strips[0].action
            reset_pose(rig)
            rig.animation_data.action = action
            first, last = action.frame_range
            durations[name] = (last - first) * scene.render.fps_base / scene.render.fps
            for i in range(count):
                intervals = count - 1 if name == "Giro" else count
                frame = first + (last - first) * i / intervals
                whole = math.floor(frame)
                scene.frame_set(whole, subframe=frame - whole)
                render(scene, out / f"{name}-{view}-{i:02}.png")
    (out / "duraciones.json").write_text(json.dumps(durations, indent=2) + "\n")


def save_scene(scene, cameras, rig, out):
    reset_pose(rig)
    strips = {}
    for track in rig.animation_data.nla_tracks:
        track.mute = False
        (strip,) = list(track.strips)
        strip.extrapolation = "NOTHING"
        strips[track.name] = strip
    walk = strips["Marcha"]
    walk.frame_start_ui = 1
    walk.repeat = 4
    idle = strips["Reposo"]
    idle.frame_start_ui = math.ceil(walk.frame_end)
    run = strips["Carrera"]
    run.frame_start_ui = math.ceil(idle.frame_end)
    run.repeat = 4
    turn = strips.get("Giro")
    if turn:
        turn.frame_start_ui = math.ceil(run.frame_end)
        turn.extrapolation = "HOLD_FORWARD"
    for strip in strips.values():
        full_length = (strip.action_frame_end - strip.action_frame_start) * strip.repeat
        if abs(strip.frame_end - strip.frame_start - full_length) > 0.001:
            raise ValueError(f"Timeline trimmed the {strip.name} action")
    scene.frame_start = int(walk.frame_start)
    scene.frame_end = math.ceil(run.frame_end) - 1
    scene.timeline_markers.new("Marcha · cuatro ciclos", frame=scene.frame_start)
    scene.timeline_markers.new("Reposo · respiración", frame=int(idle.frame_start))
    scene.timeline_markers.new("Carrera · cuatro ciclos", frame=int(run.frame_start))
    if turn:
        finish = math.ceil(turn.frame_end)
        scene.timeline_markers.new("Giro · media vuelta", frame=int(turn.frame_start))
        scene.timeline_markers.new("Fin del giro · de espaldas", frame=finish)
        scene.frame_end = finish + round(.5 * scene.render.fps / scene.render.fps_base)
    scene.frame_set(scene.frame_start)
    scene.camera = cameras["oblicua"]
    scene.cycles.samples = 32
    scene.render.filepath = "//"
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    rig.data.display_type = "STICK"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == "VIEW_3D":
                view = area.spaces.active
                view.region_3d.view_perspective = "ORTHO"
                view.region_3d.view_distance = 3.15
                view.region_3d.view_location = (0, 0, 0.93)
                view.region_3d.view_rotation = scene.camera.rotation_euler.to_quaternion()
                view.overlay.show_extras = False
                view.overlay.show_overlays = False
                view.shading.color_type = "TEXTURE"
                view.clip_start = 0.01
    info = bpy.data.texts.new("LEEME · movimiento")
    info.write(
        "Pulse Espacio para reproducir. Los marcadores llevan a los cuatro ciclos de marcha, "
        "al reposo y a los cuatro ciclos de carrera. "
        + ("En la cuarta tira da media vuelta una vez y mantiene el último apoyo medio segundo. " if turn else "")
        + "Las tiras de cada acción son editables en el editor NLA. "
        "Encienda Superposiciones para ver los 49 huesos. Para editar la malla en T, "
        "seleccione el esqueleto y active la posición de reposo en Propiedades de datos. "
        "Las claves Prueba.Indice.L/R de la malla se prueban de manera independiente.\n"
    )
    for obj in scene.objects:
        if obj.type in {"CAMERA", "LIGHT"} or obj.name == "Ciclorama":
            obj.hide_select = True
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str((out / "character-motion.blend").resolve()), compress=True)


def render_turn_preview(scene, rig, out):
    turn = rig.animation_data.nla_tracks["Giro"].strips[0]
    scene.frame_start = int(turn.frame_start)
    scene.render.image_settings.file_format = "FFMPEG"
    scene.render.ffmpeg.format = "MPEG4"
    scene.render.ffmpeg.codec = "H264"
    scene.render.ffmpeg.constant_rate_factor = "HIGH"
    scene.render.filepath = str((out / "giro-oblicua.mp4").resolve())
    bpy.ops.render.render(animation=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, nargs="?", help="source GLB used for the reference image with --frames")
    parser.add_argument("candidate", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--frames", action="store_true")
    parser.add_argument("--turn-preview", action="store_true", help="render the one-shot Giro strip to giro-oblicua.mp4")
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])
    if args.frames and args.original is None:
        parser.error("--frames requiere el GLB original para la imagen de referencia")
    args.output.mkdir(parents=True, exist_ok=False)
    if args.frames:
        reference, _ = load(args.original, reference=True)
        render(reference, args.output / "referencia.png")
    scene, cameras = load(args.candidate)
    (rig,) = [obj for obj in scene.objects if obj.type == "ARMATURE"]
    if args.turn_preview and "Giro" not in rig.animation_data.nla_tracks:
        parser.error("--turn-preview requiere un GLB con la acción Giro")
    if args.frames:
        save_frames(scene, cameras, rig, args.output)
    save_scene(scene, cameras, rig, args.output)
    if args.turn_preview:
        render_turn_preview(scene, rig, args.output)


if __name__ == "__main__":
    main()
