"""Compare bilateral finger sections of the manifested source and intermediate GLBs.
blender -b -P tools/prepare_higgsfield_hand_sections.py -- SOURCE.glb INTERMEDIATE.glb NEW_DIRECTORY
"""
from collections import defaultdict
import json
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
from prepare_higgsfield_hand_scene import SOURCE_SHA, sha, studio

PORTABLE_SHA = "1cc77f0ea4e930a178a7c627f7fb2c4eba8f27b481bb94ced444e65208788bb8"
# Keep sections between source vertices so each intersected edge has two
# unambiguous sides. Quantization joins seam copies of the same intersection.
SECTIONS = (.77812, .83012, .85012, .87512, .89312)
QUANTIZATION_M = 1e-8


def components(points, triangles, y):
    neighbours = defaultdict(set)
    for face in triangles:
        vertices = [points[i] for i in face]
        if not min(p.y for p in vertices) < y < max(p.y for p in vertices):
            continue
        intersections = []
        for a, b in zip(vertices, vertices[1:] + vertices[:1]):
            if (a.y < y) == (b.y < y):
                continue
            t = (y-a.y)/(b.y-a.y)
            x = a.x + t*(b.x-a.x)
            z = a.z + t*(b.z-a.z)
            intersections.append((round(x/QUANTIZATION_M),round(z/QUANTIZATION_M)))
        a, b = intersections
        if a != b:
            neighbours[a].add(b)
            neighbours[b].add(a)
    if not neighbours or any(len(n) != 2 for n in neighbours.values()):
        raise ValueError(f"Open or ambiguous reference section at {y}")
    seen = set()
    rings = []
    for p in neighbours:
        if p in seen:
            continue
        todo = [p]
        loop = set()
        while todo:
            v = todo.pop()
            if v not in loop:
                loop.add(v)
                todo.extend(neighbours[v]-loop)
        seen.update(loop)
        rings.append(sorted(loop))
    return sorted(rings)


def main(source, intermediate, out):
    if sha(source) != PORTABLE_SHA or sha(intermediate) != SOURCE_SHA:
        raise ValueError("Expected the documented source and intermediate GLBs")
    out.mkdir(parents=True,exist_ok=False)
    records = {}
    contours = {}
    for label,path in (("source",source),("intermediate",intermediate)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
        obj, = [o for o in bpy.context.scene.objects if o.type == 'MESH']
        coords = [obj.matrix_world @ v.co for v in obj.data.vertices]
        triangles = [p.vertices[:] for p in obj.data.polygons]
        rings = {f"{side}.{y}": components(coords,triangles,y*s)
                 for side,s in (("L",1),("R",-1)) for y in SECTIONS}
        contours[label] = rings
        records[label] = {"sha256":sha(path),"sections":{
            key: [{"samples":len(loop), "zRangeM":[min(p[1] for p in loop)*QUANTIZATION_M,
                                                   max(p[1] for p in loop)*QUANTIZATION_M]}
                  for loop in loops] for key,loops in rings.items()}}
        if label == "source":
            views = {}
            for camera in studio(bpy.context.scene):
                bpy.context.scene.camera = camera
                image = out/(camera.name+"-fuente.png")
                bpy.context.scene.render.filepath = str(image.resolve())
                bpy.ops.render.render(write_still=True)
                views[image.name]=sha(image)
            records[label]["views"]=views
    counts = {key: len(loops) for key,loops in contours["intermediate"].items()}
    if any(counts[key]!=len(loops) for key,loops in contours["source"].items()):
        raise ValueError("Reduction changed the number of loops in a sampled section")
    if any(counts[f"{side}.0.83012"] != 1 for side in ("L","R")):
        raise ValueError("Expected the four long fingers to share this section")
    records["matchingSampleCoordinates"] = {key: value==contours["source"][key]
                                             for key,value in contours["intermediate"].items()}
    records.update(quantizationM=QUANTIZATION_M, stationsM=SECTIONS,
                   blender=bpy.app.version_string, sectionToolSha256=sha(Path(__file__)),
                   sceneToolSha256=sha(Path(__file__).with_name("prepare_higgsfield_hand_scene.py")))
    (out/"sections.json").write_text(json.dumps(records,indent=2)+"\n")


if __name__ == "__main__":
    main(*map(Path,sys.argv[sys.argv.index("--")+1:]))
