"""Build an editable bilateral hand review scene from the intermediate character GLB.
blender -b -t 4 --python-exit-code 1 -P tools/prepare_higgsfield_hand_scene.py -- INPUT.glb NEW_DIRECTORY
"""
import collections
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

SOURCE_SHA = "075460e2524f882d3dc852c0aca900d18b9d09489991306e7a8d34b94b6d3057"
# (Distance from midline, little/ring, ring/middle, middle/index), in Blender world metres.
# Each row follows grooves observed in cross-sections of the authored pose. After the
# shorter fingers end, the last groove is extended as a selection boundary.
STATIONS = (
    (.805, .4165, .4390, .4635),
    (.820, .4165, .4385, .4615),
    (.840, .4152, .4374, .4596),
    (.860, .4135, .4360, .4595),
    (.880, .4120, .4342, .4572),
    (.900, .4110, .4320, .4575),
)
DIGITS = ("Menique", "Anular", "Medio", "Indice")
SEAMS = ("Puente.Am", "Puente.MA", "Puente.IM")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def groove(y):
    for a, b in zip(STATIONS, STATIONS[1:]):
        if y <= b[0]:
            t = max(0, (y-a[0])/(b[0]-a[0]))
            return [value + t*(other-value) for value, other in zip(a[1:], b[1:])]
    return STATIONS[-1][1:]


def new_side(obj, positions, side, sign, landmarks):
    sets = collections.defaultdict(set)
    for i, p in enumerate(positions):
        y = sign*p.y
        if y < .72:
            continue
        sets["Mano"].add(i)
        if y >= .766 and p.z > .493:
            sets["Pulgar"].add(i)
        elif y >= STATIONS[0][0]:
            sets[DIGITS[sum(p.z >= h for h in groove(y))]].add(i)

    # A face with corners on both sides of one measured groove is a useful
    # patch to inspect. Adjacent faces are included by Blender group selection.
    crossing_faces = {s: [] for s in SEAMS}
    for face in obj.data.polygons:
        ids = tuple(face.vertices)
        points = [positions[i] for i in ids]
        if min(p.y*sign for p in points) < .813:
            continue
        for j, seam in enumerate(SEAMS):
            delta = [p.z-groove(p.y*sign)[j] for p in points]
            if min(delta) < 0 < max(delta):
                crossing_faces[seam].append(face.index)
                sets[seam].update(ids)
    for name, ids in sets.items():
        obj.vertex_groups.new(name=f"{side}.{name}").add(sorted(ids), 1., 'REPLACE')
    tips = {}
    for finger in ("Pulgar", *DIGITS):
        i = max(sets[finger], key=lambda k: (positions[k].y*sign, -k))
        marker = bpy.data.objects.new(f"Punta.{finger}.{side}", None)
        landmarks.objects.link(marker)
        marker.parent = obj
        marker.location = obj.data.vertices[i].co
        marker.empty_display_type = 'SPHERE'
        marker.empty_display_size = .0013
        marker["source_vertex"] = i
        tips[finger] = {"vertex": i, "worldM": list(positions[i])}

    # Controlled diagnostic: bend the isolated index zone toward the palm.
    # Smoothing starts at the knuckle. Vertices across the neighbouring crease
    # stay fixed, making stretched bridge faces visible to the artist.
    index_ids = sets["Indice"]
    knuckle_band = [positions[i] for i in index_ids if sign*positions[i].y < .827]
    if not knuckle_band:
        raise ValueError("Cannot locate the reference index base")
    pivot = Vector((sum(p.x for p in knuckle_band)/len(knuckle_band), .819*sign, 0))
    flex = obj.shape_key_add(name="Prueba.Indice."+side, from_mix=False)
    inverse = obj.matrix_world.inverted()
    moved = {}
    for i in index_ids:
        p = positions[i]
        t = min(1., max(0., (sign*p.y-.819)/.024))
        angle = -sign*math.radians(30)*t*t*(3-2*t)
        if angle == 0:
            continue
        dx, dy = p.x-pivot.x, p.y-pivot.y
        q = Vector((pivot.x+math.cos(angle)*dx-math.sin(angle)*dy,
                    pivot.y+math.sin(angle)*dx+math.cos(angle)*dy, p.z))
        flex.data[i].co = inverse @ q
        moved[i] = q
    deltas = []
    for edge in obj.data.edges:
        a, b = edge.vertices
        if (a in moved) == (b in moved) or not ({a,b} <= sets["Puente.IM"]):
            continue
        old_length = (positions[a]-positions[b]).length
        new_length = (moved.get(a,positions[a])-moved.get(b,positions[b])).length
        deltas.append((new_length-old_length, edge.index, old_length))
    if not deltas or set(sets) != {"Mano","Pulgar",*DIGITS,*SEAMS}:
        raise ValueError("Incomplete bilateral review regions")
    maximum, edge, rest_length = max(deltas)
    return {"groups": {k: len(v) for k,v in sets.items()}, "landmarks": tips,
            "crossingFaceIndices": crossing_faces, "indexProbe": {"degrees":30,
            "pivotWorldXY":list(pivot)[:2], "movedVertices":len(moved),
            "bridgeEdgesMeasured":len(deltas),"worstEdge":edge,
            "worstEdgeRestM":rest_length, "maximumBridgeEdgeElongationM":maximum}}


def aim(obj, target):
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()


def studio(scene):
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 10
    scene.cycles.seed = 73
    scene.cycles.use_adaptive_sampling = False
    scene.cycles.use_denoising = False
    scene.render.film_transparent = True
    scene.render.resolution_x = scene.render.resolution_y = 480
    scene.render.resolution_percentage = 100
    scene.world = bpy.data.worlds.new("Estudio de manos")
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.55,.55,.55,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .7
    cameras = []
    for x in (-1, 1):
        bpy.ops.object.light_add(type='AREA',location=(x*2,-1,3))
        lamp = bpy.context.object
        lamp.data.energy = 360
        lamp.data.size = 2.5
        aim(lamp, (0,0,.45))
    for side, sign in (("R",-1), ("L",1)):
        focus = Vector((.045, sign*.812,.467))
        for angle, dx in (("Palma",2.6),("Dorso",-2.6)):
            bpy.ops.object.camera_add(location=focus+Vector((dx,sign*.24,.16)))
            camera = bpy.context.object
            camera.name = angle+"."+side
            aim(camera,focus)
            camera.data.type = 'ORTHO'
            camera.data.ortho_scale = .225
            cameras.append(camera)
    return cameras


def build(source, destination):
    if sha(source) != SOURCE_SHA:
        raise ValueError("Expected the intermediate character identified by the authoring manifest")
    destination.mkdir(parents=True,exist_ok=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    obj, = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    obj.name = "Personaje · edición de manos"
    positions = [obj.matrix_world @ v.co for v in obj.data.vertices]
    markers = bpy.data.collections.new("Puntas de referencia")
    bpy.context.scene.collection.children.link(markers)
    obj.shape_key_add(name="Basis", from_mix=False)
    sides = {side:new_side(obj,positions,side,sign,markers) for side,sign in (("L",1),("R",-1))}
    scene = bpy.context.scene
    cameras = studio(scene)
    scene.camera = cameras[0]
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    obj.vertex_groups.active_index = obj.vertex_groups["R.Puente.IM"].index
    obj.active_shape_key_index = 0
    # Open with a usable hand framing and the editable mesh selected.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                view = area.spaces.active
                view.region_3d.view_perspective = 'ORTHO'
                view.region_3d.view_distance = .35
                view.region_3d.view_location = (.045,-.812,.467)
                view.region_3d.view_rotation = cameras[0].rotation_euler.to_quaternion()
                view.overlay.show_extras = False
                view.clip_start = .001
                view.shading.color_type = 'TEXTURE'
    text = bpy.data.texts.new("LEEME · manos")
    text.write("Seleccione un grupo Puente en Propiedades de datos. En modo Edición use Seleccionar para destacar la región. L y R son los lados del personaje.\n"
               "Prueba.Indice.L/R (valor 0 a 1) flexiona el índice de forma controlada para inspeccionar las caras estiradas del puente índice-medio. Ponga ambas claves a 0 y seleccione Basis antes de editar el reposo.\n"
               "Las cuatro cámaras muestran dorso y palma. Los marcadores de punta señalan vértices de superficie para referencia. El siguiente trabajo es construir paredes y bucles de deformación a cada lado del surco.\n")
    scene_path = destination/'hand-edit.blend'
    bpy.ops.wm.save_as_mainfile(filepath=str(scene_path.resolve()),compress=True)
    inputs = {"sourceSha256":SOURCE_SHA,"recipeSha256":sha(Path(__file__)),"blender":bpy.app.version_string,
              "blendSha256":sha(scene_path),"restTriangles":len(obj.data.polygons),"sides":sides,"views":{}}
    for camera in cameras:
        scene.camera = camera
        side = camera.name[-1]
        for label, value in (("reposo",0),("flexion",1)):
            obj.data.shape_keys.key_blocks["Prueba.Indice."+side].value = value
            png = destination/(camera.name+"-"+label+".png")
            scene.render.filepath = str(png.resolve())
            bpy.ops.render.render(write_still=True)
            inputs["views"][png.name] = sha(png)
        obj.data.shape_keys.key_blocks["Prueba.Indice."+side].value = 0
    (destination/'hand-review.json').write_text(json.dumps(inputs,indent=2,ensure_ascii=False)+"\n")


if __name__ == '__main__':
    input_file, new_dir = map(Path, sys.argv[sys.argv.index("--")+1:])
    build(input_file,new_dir)
