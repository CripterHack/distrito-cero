"""Render fixed character authoring views with Blender 4.3.2.

blender -b -t 4 --python-exit-code 1 -P tools/prepare_higgsfield_character_views.py -- INPUT.glb NEW_DIRECTORY
"""
import hashlib
import json
from pathlib import Path
import sys

import bpy
from mathutils import Vector


# Coordinates in the Blender scene after glTF import (vertical Z, character facing +X).
VIEWS = {
    "silhouette": ((0, 0, 0), (3.1, -1.65, .68), 2.12),
    "face": ((.035, 0, .73), (2.9, -.85, .12), .46),
    "hand": ((.05, -.805, .466), (2.9, -.25, .12), .27),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def render(source, destination):
    source = source.resolve(strict=True)
    destination.mkdir(parents=True, exist_ok=False)
    initial_hash = digest(source)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source))
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.seed = 73
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = 512
    scene.render.resolution_percentage = 100
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'AgX'
    scene.world = bpy.data.worlds.new("Neutral studio")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.45, .45, .45, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .8
    for location, power, width in [
        ((3, -2, 3.4), 440, 2.5), ((2, 2.5, 1.6), 300, 2.8), ((-1.4, .4, 2.8), 270, 2.2)
    ]:
        bpy.ops.object.light_add(type='AREA', location=location)
        lamp = bpy.context.object
        lamp.data.energy = power
        lamp.data.size = width
        aim(lamp, (0, 0, .25))
    bpy.ops.object.camera_add()
    camera = bpy.context.object
    scene.camera = camera
    camera.data.type = 'ORTHO'
    images = {}
    for name, (target, offset, scale) in VIEWS.items():
        camera.location = Vector(target) + Vector(offset)
        aim(camera, target)
        camera.data.ortho_scale = scale
        output = destination / f'{name}.png'
        scene.render.filepath = str(output.resolve())
        bpy.ops.render.render(write_still=True)
        images[name] = {"file": output.name, "sha256": digest(output)}
    if digest(source) != initial_hash:
        raise ValueError("Input changed during render")
    report = {
        "blender": bpy.app.version_string, "sourceSha256": initial_hash,
        "scriptSha256": digest(Path(__file__)), "source": source.name,
        "renderer": "Cycles CPU", "samples": scene.cycles.samples, "seed": scene.cycles.seed,
        "size": [512, 512], "viewTransform": scene.view_settings.view_transform,
        "cameraTargetOffsetAndOrthoScaleBlender": VIEWS, "images": images,
    }
    (destination / "views.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    input_path, output_dir = sys.argv[sys.argv.index("--") + 1:]
    render(Path(input_path), Path(output_dir))
