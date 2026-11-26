"""Compare the pants fold through a complete stride, after importing the portable GLBs.

blender -b -t 2 --python-exit-code 1 -P tools/qa/capture_higgsfield_knee.py -- previous.glb artifacts/knee-before
blender -b -t 2 --python-exit-code 1 -P tools/qa/capture_higgsfield_knee.py -- candidate.glb artifacts/knee-after --before artifacts/knee-before

For the separate running-knee comparison, use --clip Carrera on both captures
and pass new output directories. It captures the lateral fold at phase 3/16.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector
import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from review_higgsfield_motion import aim, load, render


# Measured endpoints of the original denim edge, in Blender metres (Z up).
# Identify the edge in the imported surface by both endpoints, independently of indices.
REST_EDGE = np.array([[-.06417450, .16939774, .48211670], [-.06046238, .15197124, .53408653]])
VIEWS = {
    "posterior": ((-.086, -.02, .53), (0., 1., .10), .37),
    "perfil": ((-.08, -.015, .53), (-1., .04, .075), .83),
}
RUN_VIEW = {
    "perfil": ((-.168, -.254, .552), (-1., .32, .12), .33),
}
STEPS = 16
WIDTH, HEIGHT = 448, 350


def endpoints(obj, graph, ids):
    evaluated = obj.evaluated_get(graph)
    return [evaluated.matrix_world @ evaluated.data.vertices[i].co for i in ids]


def locate_edge(obj, graph):
    mesh = obj.evaluated_get(graph)
    coords = np.array([mesh.matrix_world @ v.co for v in mesh.data.vertices])
    for edge in mesh.data.edges:
        paired = coords[list(edge.vertices)]
        if np.allclose(paired, REST_EDGE, atol=.00001) or np.allclose(paired[::-1], REST_EDGE, atol=.00001):
            return list(edge.vertices)
    raise ValueError("The measured posterior edge was not found in the imported rest topology")


def render_review(path, dest, clip):
    scene, cameras = load(path)
    scene.render.resolution_x, scene.render.resolution_y = WIDTH, HEIGHT
    rig, = [o for o in scene.objects if o.type == "ARMATURE"]
    pants, = [o for o in scene.objects if o.type == "MESH" and o.data.shape_keys]
    graph = bpy.context.evaluated_depsgraph_get()
    camera = cameras["perfil"]
    scene.camera = camera
    rig.data.pose_position = "REST"
    graph.update()
    ids = locate_edge(pants, graph)
    rest = endpoints(pants, graph, ids)
    rig.data.pose_position = "POSE"
    anim = rig.animation_data.nla_tracks[clip].strips[0].action
    rig.animation_data.action = anim
    first, last = anim.frame_range
    duration = (last - first) * scene.render.fps_base / scene.render.fps
    running = clip == "Carrera"
    views = RUN_VIEW if running else VIEWS
    stats = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "clip": clip, "seconds": duration,
             "restLengthMm": (rest[0] - rest[1]).length * 1000, "blender": bpy.app.version_string,
             "cameras": views, "width": WIDTH, "height": HEIGHT, "steps": STEPS, "samples": []}
    for i in ([3] if running else range(STEPS)):
        scene.cycles.samples = 64 if running or i in (6, 14) else 24
        f = first + (last - first) * i / STEPS
        scene.frame_set(math.floor(f), subframe=f - math.floor(f))
        a, b = endpoints(pants, graph, ids)
        sample = {"phase": i / STEPS, "lengthMm": (a - b).length * 1000}
        for name, (focus, direction, scale) in views.items():
            if not running and name == "perfil" and i != 6:
                continue
            camera.location = Vector(focus) + Vector(direction).normalized() * 4
            camera.data.ortho_scale = scale
            aim(camera, focus)
            graph.update()
            projected = [world_to_camera_view(scene, camera, point) for point in (a, b)]
            sample[name] = [[p.x * WIDTH, (1 - p.y) * HEIGHT] for p in projected]
            render(scene, dest / f"{name}-{i:02}.png")
        stats["samples"].append(sample)
    (dest / "medidas.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False) + "\n")


def font(size):
    try:
        return ImageFont.truetype("DejaVuSans.ttf", size)
    except OSError:
        return ImageFont.load_default(size=size)


def pair_running_pose(before, after):
    pad, gap, header, footer = 16, 4, 81, 40
    sheet = Image.new("RGB", (2 * WIDTH + 2 * pad + gap, header + HEIGHT + footer), "#172127")
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), "Rodilla derecha durante la carrera", font=font(27), fill="#f5f2eb")
    draw.text((pad, 51), "Perfil exterior · fase 18,75 % del ciclo", font=font(17), fill="#bbcaca")
    for i, (folder, label) in enumerate(((before, "Antes"), (after, "Después"))):
        x = pad + i * (WIDTH + gap)
        with Image.open(folder / "perfil-03.png") as source:
            sheet.paste(source.convert("RGB"), (x, header))
        draw.text((x, header + HEIGHT + 5), label, font=font(17), fill="#f5f2eb")
    sheet.save(after / "comparacion.jpg", quality=92, optimize=True)


def paired(before, after):
    reports = [json.loads((folder / "medidas.json").read_text()) for folder in (before, after)]
    clips = [report.get("clip", "Marcha") for report in reports]
    if clips[0] != clips[1]:
        raise ValueError(f"Cannot compare different clips: {clips}")
    for key in ("width", "height", "steps", "seconds", "cameras"):
        if reports[0][key] != reports[1][key]:
            raise ValueError("Inconsistent capture parameter: "+key)
    if clips[0] == "Carrera":
        return pair_running_pose(before, after)
    w, h, pad, gap = WIDTH, HEIGHT, 16, 4
    bg, fg, muted = "#172127", "#f5f2eb", "#bbcaca"
    folders = (before, after)
    labels = ("Antes", "Después")
    sheet = Image.new("RGB", (3 * w + 2 * pad + 2 * gap, 2 * h + 189), bg)
    draw = ImageDraw.Draw(sheet)
    draw.text((pad, 10), "Rodilla derecha durante la marcha", font=font(27), fill=fg)
    draw.text((pad, 51), f"Material del GLB en Blender {reports[0]['blender']}   ·   Arista posterior del pantalón en reposo, "
              +f"{reports[0]['restLengthMm']:.1f} mm".replace(".", ","), font=font(17), fill=muted)
    cases = [("posterior", 6, "Vista posterior · fase 37,5 %"),
             ("perfil", 6, "Perfil exterior · fase 37,5 %"),
             ("posterior", 14, "Vista posterior · fase 87,5 %")]
    for j, (view, phase, caption) in enumerate(cases):
        x = pad + j * (w + gap)
        draw.text((x, 84), caption, fill=fg, font=font(18))
        for i, folder in enumerate(folders):
            y = 114 + i * (h + 34)
            with Image.open(folder / f"{view}-{phase:02}.png") as source:
                sheet.paste(source.convert("RGB"), (x, y))
            sample = reports[i]["samples"][phase]
            text = labels[i]
            if j == 0:
                # A thin outline locates the material patch without covering the crease itself.
                center = np.mean(sample[view], axis=0)
                cx, cy = x + center[0], y + center[1]
                draw.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), outline="#ffde8c", width=2)
                text += "   ·   Arista del pantalón, " + f"{sample['lengthMm']:.1f} mm".replace(".", ",")
            draw.text((x, y + h + 4), text, font=font(17), fill=fg)
    sheet.save(after / "comparacion.jpg", quality=92, optimize=True)
    frames = []
    for n in range(STEPS):
        frame = Image.new("RGB", (w * 2 + gap, h + 34), bg)
        d = ImageDraw.Draw(frame)
        for i, folder in enumerate(folders):
            x = i * (w + gap)
            d.text((x + 10, 4), labels[i], font=font(18), fill=fg)
            with Image.open(folder / f"posterior-{n:02}.png") as source:
                frame.paste(source.convert("RGB"), (x, 34))
        frames.append(frame)
    total_ms = round(1000 * reports[0]["seconds"])
    durations = [round(total_ms * (i + 1) / STEPS) - round(total_ms * i / STEPS) for i in range(STEPS)]
    frames[0].save(after / "marcha.webp", save_all=True, append_images=frames[1:], duration=durations,
                   loop=0, quality=85, method=4)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("glb", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--before", type=Path)
    p.add_argument("--clip", choices=("Marcha", "Carrera"), default="Marcha")
    args = p.parse_args(sys.argv[sys.argv.index("--") + 1:])
    args.output.mkdir(parents=True, exist_ok=False)
    render_review(args.glb, args.output, args.clip)
    if args.before:
        paired(args.before, args.output)
