"""Build an editable Blender scene aligning native cabin landmarks to the review sedan."""
from pathlib import Path
import hashlib
import json
import math
import sys

import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SEDAN_SHA = '1b3d9ef2f0824f18a9ef0146031deee55cde568b722456bda246ff81ade74a89'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def blender_point(point):
    x, y, z = point
    return Vector((x, -z, y))


def game_point(point):
    return [point.x, point.z, -point.y]


def make_curve(collection, name, paths, color, radius):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.bevel_depth = radius
    curve.bevel_resolution = 1
    for line in paths:
        poly = curve.splines.new('POLY')
        poly.points.add(len(line)-1)
        for point, xyz in zip(poly.points, line):
            point.co = (*blender_point(xyz), 1)
    obj = bpy.data.objects.new(name, curve)
    collection.objects.link(obj)
    obj.show_in_front = True
    obj.color = color
    return obj


def marker(collection, name, point, color):
    obj = bpy.data.objects.new(name, None)
    collection.objects.link(obj)
    obj.location = blender_point(point)
    obj.empty_display_type = 'SPHERE'
    obj.empty_display_size = .023
    obj.show_in_front = True
    obj.color = color


def main(source, cabin_file, output):
    if sha(source) != SEDAN_SHA:
        raise ValueError("Expected articulated sedan from PR 66")
    d = json.loads(cabin_file.read_text())
    if d['schema'] != 1 or len(d['skeleton']) != 49:
        raise ValueError('Expected 49 native joint samples')
    output.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(source.resolve()))
    car = bpy.data.objects['sedan_body']
    mesh = car.data
    mesh.calc_loop_triangles()
    world = [car.matrix_world @ v.co for v in mesh.vertices]
    triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
    tree = BVHTree.FromPolygons(world, triangles, all_triangles=True)

    def collection(name):
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        return c
    guides = collection('01 · Referencias del juego')
    section = collection('02 · Corte longitudinal del exterior')
    driver = collection('03 · Pose sentada del conductor')
    orange = (1, .43, .09, 1)
    teal = (.1, .86, .72, 1)
    points = {bone['name']: bone['point'] for bone in d['skeleton']}
    segments = [[points[b['parent']], b['point']] for b in d['skeleton'] if b['parent']]
    make_curve(driver, 'Pose nativa · 49 articulaciones', segments, teal, .005)
    for key in ('approach','openingHand','seatOrigin','wheelCenter','cushionCenter',
                'backrestCenter','hinge','closedHandle'):
        marker(guides, key, d[key], orange)
    make_curve(guides, 'Entrada · trayectoria del origen del actor', [d['entry']], orange, .007)
    # Draw the native steering ring in its own tilted plane.
    cx, cy, cz = d['wheelCenter']
    rad, tilt = d['wheelRadius'], d['wheelTilt']
    ring = [[cx+rad*math.cos(a), cy+rad*math.sin(a)*math.cos(tilt),
             cz+rad*math.sin(a)*math.sin(tilt)] for a in (i*math.tau/64 for i in range(65))]
    make_curve(guides, 'Volante nativo', [ring], orange, .006)
    for k, pt in d['grips'].items():
        marker(guides, 'Muñeca '+k, pt, teal)

    # Intersect the *actual exterior* with the longitudinal plane through the
    # driver. Keep the disconnected segments, including any gaps in the shell.
    plane = d['seatOrigin'][0]
    cuts = []
    for triangle in triangles:
        verts = [world[i] for i in triangle]
        hits = []
        for a, b in zip(verts, verts[1:]+verts[:1]):
            if (a.x < plane) != (b.x < plane):
                hits.append(a.lerp(b, (plane-a.x)/(b.x-a.x)))
        if len(hits)==2 and (hits[0]-hits[1]).length>1e-7:
            cuts.append([game_point(hit) for hit in hits])
    if not cuts:
        raise RuntimeError('Empty driver-side body section')
    make_curve(section, 'Exterior · plano X del conductor', cuts, (1,.82,.23,1), .0025)
    probes = {}
    for label in ('openingHand','closedHandle','hinge'):
        _, y, z = d[label]
        location, _, index, _ = tree.ray_cast(blender_point([-3,y,z]),Vector((1,0,0)))
        if location is None:
            raise RuntimeError('No body hit for '+label)
        hit = game_point(location)
        probes[label] = dict(firstOuterHit=hit, triangle=index, deltaXToReferenceM=d[label][0]-hit[0])
    head = points['head']
    roof, _, index, _ = tree.ray_cast(blender_point([head[0],3,head[2]]), Vector((0,0,-1)))
    if roof is None:
        raise RuntimeError('No outer roof above head joint')
    feet = {}
    for name in ('footL','footR'):
        foot = points[name]
        location, _, face_index, _ = tree.ray_cast(blender_point([foot[0],-1,foot[2]]), Vector((0,0,1)))
        if location is None:
            raise RuntimeError('No lower body shell at '+name)
        feet[name] = {'joint':foot,'lowestBodySurface':game_point(location),
                      'bodyHeightMinusAnkleJointM':location.z-foot[1],'triangle':face_index}
    body_section = {'modelSha256':SEDAN_SHA,'cabinSha256':sha(cabin_file),'blender':bpy.app.version_string,
                    'longitudinalPlaneX':plane,'exteriorSection':cuts,'probes':probes,
                    'headJoint':head,'outerRoofAtHead':game_point(roof),
                    'outerRoofAboveHeadJointM':roof.z-head[1],'lowerShellAtAnkles':feet}
    (output/'section.json').write_text(json.dumps(body_section,separators=(',',':'))+'\n')
    # A user opening the file can select each guide, toggle the three collections,
    # and orbit the original textured asset using material preview.
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.shading.color_type = 'OBJECT'
                region = space.region_3d
                region.view_rotation = Vector((1,-.42,-.16)).to_track_quat('-Z','Y')
                region.view_distance = 5.8
                region.view_location = (0,0,.76)
                region.view_perspective = 'ORTHO'
    bpy.ops.object.select_all(action='DESELECT')
    bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str((output/'sedan-cabin.blend').resolve()), compress=True)


if __name__=='__main__':
    main(*map(Path,sys.argv[sys.argv.index('--')+1:]))
