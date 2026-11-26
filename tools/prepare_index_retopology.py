"""Reconstruct both index/middle web spaces on the documented Higgsfield character.

blender -b -t 4 --python-exit-code 1 -P tools/prepare_index_retopology.py -- INPUT_REVIEW_DIRECTORY NEW_DIRECTORY
"""

from pathlib import Path
import collections
import json
import math
import sys

import bmesh
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import tessellate_polygon

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prepare_higgsfield_hand_scene as hand


def cut_channel(scene, obj, inv, tmp, wallmat, sign):
    rows = [
        0.812,
        0.814,
        0.817,
        0.821,
        0.825,
        0.830,
        0.836,
        0.842,
        0.848,
        0.854,
        0.860,
        0.866,
        0.872,
        0.878,
        0.884,
        0.890,
        0.896,
        0.906,
        0.918,
    ]
    offsets = [
        -0.20,
        -0.021,
        -0.014,
        -0.009,
        -0.004,
        0,
        0.004,
        0.009,
        0.014,
        0.021,
        0.20,
    ]
    coords = []
    faces = []
    for layer in (-1, 1):
        for y in rows:
            cx = 0.039 + 0.46 * (y - 0.82)
            center = hand.groove(y)[2]
            taper = min(1, max(0.08, (y - 0.812) / 0.015))
            for dx in offsets:
                half = taper * (0.00145 + 0.0028 * min(1, (dx / 0.015) ** 2))
                coords.append(
                    tuple(inv @ Vector((cx + dx, sign * y, center + layer * half)))
                )
    R = len(rows)
    C = len(offsets)

    def pt(b, r, c):
        return (b * R + r) * C + c

    for a in range(2):
        for r in range(R - 1):
            for c in range(C - 1):
                q = [pt(a, r, c), pt(a, r, c + 1), pt(a, r + 1, c + 1), pt(a, r + 1, c)]
                faces.append(q)
    for c in range(C - 1):
        for r in [0, R - 1]:
            faces.append([pt(0, r, c), pt(1, r, c), pt(1, r, c + 1), pt(0, r, c + 1)])
    for r in range(R - 1):
        for c in [0, C - 1]:
            faces.append([pt(0, r, c), pt(1, r, c), pt(1, r + 1, c), pt(0, r + 1, c)])
    cutter = bpy.data.meshes.new("Slit cutter")
    cutter.from_pydata(coords, [], faces)
    cutter.update()
    # Enforce outward winding regardless of hand side.
    bm = bmesh.new()
    bm.from_mesh(cutter)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bmesh.ops.triangulate(bm, faces=list(bm.faces))
    bm.to_mesh(cutter)
    bm.free()
    cutter.materials.append(wallmat)
    actor = bpy.data.objects.new("Cut", cutter)
    scene.collection.objects.link(actor)
    actor.matrix_world = obj.matrix_world
    mod = tmp.modifiers.new("Interdigital channel", "BOOLEAN")
    mod.object = actor
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.material_mode = "TRANSFER"
    mod.use_hole_tolerant = False
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(actor, do_unlink=True)


def barycentric(a, b, c, p):
    u, v, w = b - a, c - a, p - a
    uu, uv, vv, wu, wv = u.dot(u), u.dot(v), v.dot(v), w.dot(u), w.dot(v)
    denom = uu * vv - uv * uv
    return ((vv * wu - uv * wv) / denom, (uu * wv - uv * wu) / denom)


def concave_triangles(points):
    n = len(points)
    indices = list(range(n))
    # Classify nearly collinear runs at submicron tolerance in model space.
    # Their points are retained in the refined triangles below.
    while len(indices) > 3:
        best = None
        for k, j in enumerate(indices):
            a, c = points[indices[k - 1]], points[indices[(k + 1) % len(indices)]]
            ac = c - a
            ap = points[j] - a
            if ac.length < 1e-10:
                continue
            distance = ac.cross(ap).length / ac.length
            if distance < 3e-7 and 0 < ap.dot(ac) < ac.length_squared:
                if best is None or distance < best[0]:
                    best = (distance, k)
        if best is None:
            break
        indices.pop(best[1])
    reduced = [points[i] for i in indices]
    result = []
    for t in tessellate_polygon([reduced]):
        original = [indices[k] for k in t]
        perimeter = []
        for a, b in zip(original, original[1:] + original[:1]):
            perimeter.append(points[a])
            if b == indices[(indices.index(a) + 1) % len(indices)]:
                k = (a + 1) % n
                while k != b:
                    perimeter.append(points[k])
                    k = (k + 1) % n
        if len(perimeter) == 3:
            result.append(perimeter)
        else:
            center = sum((points[i] for i in original), Vector()) / 3
            result.extend(
                [
                    [a, b, center]
                    for a, b in zip(perimeter, perimeter[1:] + perimeter[:1])
                ]
            )
    return result


def clipped_shell(scene, obj, mesh, inv, positions, old_polys, uvs, normals):
    source_ids = {}
    for i, p in enumerate(positions):
        source_ids.setdefault(tuple(p), i)
    idxs = [source_ids[tuple(v)] for v in positions]
    faces = [tuple(idxs[j] for j in p) for p in old_polys]
    proxy = bpy.data.meshes.new("Temporary welded input")
    proxy.from_pydata(positions, [], faces)
    proxy.update()
    tmp = bpy.data.objects.new("Temporary boolean", proxy)
    scene.collection.objects.link(tmp)
    tmp.matrix_world = obj.matrix_world
    source_mat = mesh.materials[0]
    wallmat = bpy.data.materials.new("Pared interdigital · piel reconstruida")
    wallmat.use_nodes = True
    proxy.materials.append(source_mat)
    proxy.materials.append(wallmat)
    orig = proxy.attributes.new("source_face", "INT", "FACE")
    for i, d in enumerate(orig.data):
        d.value = i + 1
    # Build both curved channels as one solid tool. Start at a hand-selected
    # commissure and taper the germ of the gap into the distal index/middle groove.
    for sign in (-1, 1):
        cut_channel(scene, obj, inv, tmp, wallmat, sign)
    m = tmp.data
    if not any(p.material_index for p in m.polygons):
        raise RuntimeError("The boolean operation did not create interdigital surfaces")
    # Preserve the original triangle corners wherever the cutter did not intersect.
    # Use material/source-face identity propagated by the exact boolean. A shared
    # boundary position has one Blender vertex; UV and normals remain per corner.
    pointmap = {tuple(p): i for i, p in enumerate(positions)}
    coords = list(positions)

    def index(v):
        k = tuple(v)
        if k not in pointmap:
            pointmap[k] = len(coords)
            coords.append(v.copy())
        return pointmap[k]

    newfaces = []
    faceUV = []
    faceN = []
    faceMat = []
    source_ids = []

    def add(face, uv, n, material, source):
        newfaces.append(face)
        faceUV.extend(uv)
        faceN.extend(n)
        faceMat.append(material)
        source_ids.append(source)

    # Boolean tessellation of clipped triangles can leave large concave polygons;
    # Blender's constrained loop-triangle tessellation is applied before posing.
    m.calc_loop_triangles()
    # Blender's default tessellator can emit subpixel slivers along a clipped
    # triangle's nearly collinear boundary points. A fan to a strictly interior
    # point retains those boundary positions and gives meaningful UV area.
    by_poly = collections.defaultdict(list)
    for tri in m.loop_triangles:
        by_poly[tri.polygon_index].append(
            [m.vertices[i].co.copy() for i in tri.vertices]
        )

    for p in m.polygons:
        source_index = m.attributes["source_face"].data[p.index].value - 1
        triangles = by_poly[p.index]
        if p.material_index == 0 and len(p.vertices) > 3:
            points = [m.vertices[i].co.copy() for i in p.vertices]
            center = sum(points, Vector()) / len(points)
            normal = mesh.polygons[source_index].normal

            def signed(a, b, c):
                return (b - a).cross(c - a).dot(normal)

            ordered = list(zip(points, points[1:] + points[:1]))
            if all(signed(a, b, center) > 0 for a, b in ordered):
                triangles = [[a, b, center] for a, b in ordered]
            else:
                triangles = concave_triangles(points)
        for points in triangles:
            if p.material_index != 0:
                add(
                    [index(v) for v in points],
                    [(v.x, v.y) for v in points],
                    [(0, 0, 0)] * 3,
                    1,
                    -1,
                )
                continue
            orig = old_polys[source_index]
            a, b, c = (positions[i] for i in orig)
            corners = tuple(mesh.polygons[source_index].loop_indices)
            ids = []
            UV = []
            N = []
            for v in points:
                same = next(
                    (j for j, k in enumerate(orig) if tuple(v) == tuple(positions[k])),
                    None,
                )
                if same is not None:
                    ids.append(orig[same])
                    UV.append(uvs[corners[same]])
                    N.append(normals[corners[same]])
                else:
                    beta, gamma = barycentric(a, b, c, v)
                    alpha = 1 - beta - gamma
                    ids.append(index(v))
                    UV.append(
                        uvs[corners[0]] * alpha
                        + uvs[corners[1]] * beta
                        + uvs[corners[2]] * gamma
                    )
                    N.append(
                        (
                            normals[corners[0]] * alpha
                            + normals[corners[1]] * beta
                            + normals[corners[2]] * gamma
                        ).normalized()
                    )
            add(ids, UV, N, 0, source_index)
    used = sorted({i for face in newfaces for i in face})
    renumber = {old: new for new, old in enumerate(used)}
    coords = [coords[i] for i in used]
    newfaces = [tuple(renumber[i] for i in f) for f in newfaces]
    new = bpy.data.meshes.new("Paredes índice–medio")
    new.from_pydata(coords, [], newfaces)
    new.update()
    new.materials.append(source_mat)
    new.materials.append(wallmat)
    newUV = new.uv_layers.new(name=mesh.uv_layers.active.name)
    for d, uv in zip(newUV.data, faceUV):
        d.uv = uv
    attr = new.attributes.new("DC_fuente_cara", "INT", "FACE")
    for i, p in enumerate(new.polygons):
        p.material_index = faceMat[i]
        p.use_smooth = True
        attr.data[i].value = source_ids[i]
    return tmp, new, coords, faceN, wallmat


def wall_charts(obj, new, coords, faceN):
    newUV = new.uv_layers.active
    # Give each wall its own chart. The longitudinal strips use XY. The end cap uses XZ.
    wall_normals = {}
    fan = collections.defaultdict(lambda: Vector((0, 0, 0)))
    for poly in new.polygons:
        if not poly.material_index:
            continue
        ids = list(poly.vertices)
        points = [obj.matrix_world @ coords[i] for i in ids]
        side = 1 if points[0].y > 0 else -1
        center = sum(points, Vector()) / 3
        rootcap = max(abs(q.y - side * 0.812) for q in points) < 1e-6
        index_wall = center.z > hand.groove(abs(center.y))[2]
        tile = (1 if side == 1 else 0) * 3 + (2 if rootcap else int(index_wall))
        ux = (tile % 3) / 3
        vy = (tile // 3) / 2
        for vi, li, q in zip(ids, poly.loop_indices, points):
            if rootcap:
                u = 0.5 + (q.x - 0.045) / 0.09
                v = 0.5 + (q.z - 0.464) / 0.016
            else:
                u = (abs(q.y) - 0.808) / 0.109
                v = (q.x - 0.46 * (abs(q.y) - 0.82) - 0.008) / 0.068
            newUV.data[li].uv = (ux + (0.04 + 0.92 * u) / 3, vy + (0.04 + 0.92 * v) / 2)
            fan[vi, tile] += poly.normal
        wall_normals[poly.index] = tile
    for pi, tile in wall_normals.items():
        poly = new.polygons[pi]
        for vi, li in zip(poly.vertices, poly.loop_indices):
            n = fan[vi, tile].normalized()
            faceN[li] = n if n.dot(poly.normal) > 0.5 else poly.normal.copy()
    new.normals_split_custom_set(faceN)


def bake_wall_color(obj, new, mesh, inv, positions, coords, old_polys, uvs, wallmat):
    # Assign adjacent skin colors by projecting opposite wall edges to the nearest
    # outer source surface and sampling its original base-color image in linear RGB.
    tree = BVHTree.FromPolygons(positions, old_polys, all_triangles=True)
    color_img = next(im for im in bpy.data.images if im.name.startswith("Color_"))
    pix = np.zeros(len(color_img.pixels), dtype=np.float32)
    color_img.pixels.foreach_get(pix)
    pix = pix.reshape(color_img.size[1], color_img.size[0], 4)

    def shade(v):
        p = obj.matrix_world @ v
        side = 1 if p.z > hand.groove(abs(p.y))[2] else -1
        # Land a few millimetres within the relevant pad away from the old crease.
        p.z += side * 0.004
        p.x += 0.014
        pt, n, j, dist = tree.find_nearest(inv @ p)
        a, b, c = [positions[i] for i in old_polys[j]]
        be, ga = barycentric(a, b, c, pt)
        ids = tuple(mesh.polygons[j].loop_indices)
        uv = (1 - be - ga) * uvs[ids[0]] + be * uvs[ids[1]] + ga * uvs[ids[2]]
        xx = int(uv.x * color_img.size[0]) % color_img.size[0]
        yy = int(uv.y * color_img.size[1]) % color_img.size[1]
        patch = pix[max(0, yy - 2) : yy + 3, max(0, xx - 2) : xx + 3, :3].mean(
            axis=(0, 1)
        )
        return tuple(patch) + (1.0,)

    colors = new.color_attributes.new(
        name="Color piel lateral", type="FLOAT_COLOR", domain="POINT"
    )
    for i in {v for p in new.polygons if p.material_index == 1 for v in p.vertices}:
        colors.data[i].color = shade(coords[i])
    bs = wallmat.node_tree.nodes.get("Principled BSDF")
    node = wallmat.node_tree.nodes.new("ShaderNodeVertexColor")
    node.layer_name = colors.name
    wallmat.node_tree.links.new(node.outputs[0], bs.inputs["Base Color"])
    bs.inputs["Roughness"].default_value = 0.68
    wallmat.diffuse_color = (0.54, 0.31, 0.22, 1)


def author_side(obj, new, inv, coords, newworld, source_report, markers, side, sign):
    pivot = Vector((*source_report["sides"][side]["indexProbe"]["pivotWorldXY"], 0))
    flex = obj.shape_key_add(name="Prueba.Indice." + side, from_mix=False)
    moved = set()
    for i, p in enumerate(newworld):
        y = p.y * sign
        if y <= 0.819 or p.z < hand.groove(y)[2] or p.z > 0.493:
            continue
        t = min(1, (y - 0.819) / 0.024)
        angle = -sign * math.radians(30) * t * t * (3 - 2 * t)
        dx, dy = p.x - pivot.x, p.y - pivot.y
        q = Vector(
            (
                pivot.x + math.cos(angle) * dx - math.sin(angle) * dy,
                pivot.y + math.sin(angle) * dx + math.cos(angle) * dy,
                p.z,
            )
        )
        flex.data[i].co = inv @ q
        moved.add(i)
    group = obj.vertex_groups.new(name=side + ".Indice movil")
    group.add(sorted(moved), 1, "REPLACE")
    wall_ids = {
        i
        for f in new.polygons
        if f.material_index == 1
        for i in f.vertices
        if sign * newworld[i].y > 0
    }
    group = obj.vertex_groups.new(name=side + ".Paredes reconstruidas")
    group.add(sorted(wall_ids), 1, "REPLACE")
    groups = collections.defaultdict(set)
    for i, p in enumerate(newworld):
        y = sign * p.y
        if y < 0.72:
            continue
        groups["Mano"].add(i)
        if y >= 0.766 and p.z > 0.493:
            groups["Pulgar"].add(i)
        elif y >= hand.STATIONS[0][0]:
            groups[hand.DIGITS[sum(p.z >= z for z in hand.groove(y))]].add(i)
    for face in new.polygons:
        ids = tuple(face.vertices)
        points = [newworld[i] for i in ids]
        if min(sign * p.y for p in points) < 0.813:
            continue
        for j, seam in enumerate(hand.SEAMS[:2]):
            delta = [p.z - hand.groove(sign * p.y)[j] for p in points]
            if min(delta) < 0 < max(delta):
                groups[seam].update(ids)
    for name, ids in groups.items():
        obj.vertex_groups.new(name=f"{side}.{name}").add(sorted(ids), 1, "REPLACE")
    tips = {}
    for digit in ("Pulgar", *hand.DIGITS):
        i = max(groups[digit], key=lambda k: (sign * newworld[k].y, -k))
        marker = bpy.data.objects.new(f"Punta.{digit}.{side}", None)
        markers.objects.link(marker)
        marker.parent = obj
        marker.location = coords[i]
        marker.empty_display_type = "SPHERE"
        marker.empty_display_size = 0.0013
        marker["source_vertex"] = i
        tips[digit] = {"vertex": i, "worldM": list(newworld[i])}
    return {
        "moved": len(moved),
        "wallVertices": len(wall_ids),
        "groups": {k: len(v) for k, v in groups.items()},
        "landmarks": tips,
        "pivotWorldXY": list(pivot)[:2],
    }


def build(source, out):
    base = source / "hand-edit.blend"
    source_report = json.loads((source / "hand-review.json").read_text())
    if (
        source_report["sourceSha256"] != hand.SOURCE_SHA
        or hand.sha(base) != source_report["blendSha256"]
    ):
        raise ValueError(
            "Expected the hand review scene and its matching source manifest"
        )
    out.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.open_mainfile(filepath=str(base.resolve()))
    scene = bpy.context.scene
    (obj,) = [o for o in scene.objects if o.type == "MESH"]
    for key in obj.data.shape_keys.key_blocks:
        key.value = 0
    obj.shape_key_clear()
    obj.vertex_groups.clear()
    for o in list(bpy.data.collections["Puntas de referencia"].objects):
        bpy.data.objects.remove(o, do_unlink=True)
    bpy.data.texts.remove(bpy.data.texts["LEEME · manos"])
    mesh = obj.data
    inv = obj.matrix_world.inverted()
    positions = [v.co.copy() for v in mesh.vertices]
    old_polys = [tuple(p.vertices) for p in mesh.polygons]
    uvs = [d.uv.copy() for d in mesh.uv_layers.active.data]
    normals = [d.vector.copy() for d in mesh.corner_normals]
    tmp, new, coords, custom_normals, wallmat = clipped_shell(
        scene, obj, mesh, inv, positions, old_polys, uvs, normals
    )
    wall_charts(obj, new, coords, custom_normals)
    obj.data = new
    bpy.data.objects.remove(tmp, do_unlink=True)
    bake_wall_color(obj, new, mesh, inv, positions, coords, old_polys, uvs, wallmat)
    # Generate the same flexion witness, now on the locally separated index.
    newworld = [obj.matrix_world @ v.co for v in new.vertices]
    markers = bpy.data.collections["Puntas de referencia"]
    obj.shape_key_add(name="Basis", from_mix=False)
    sides = {
        side: author_side(
            obj, new, inv, coords, newworld, source_report, markers, side, sign
        )
        for side, sign in [("L", 1), ("R", -1)]
    }
    obj.active_shape_key_index = 0
    scene.camera = bpy.data.objects["Palma.R"]
    scene.render.filepath = "//"
    scene.render.image_settings.file_format = "PNG"
    readme = bpy.data.texts.new("LEEME · reparación local")
    readme.write(
        "Cada índice cuenta con paredes interdigitales reconstruidas y clave de flexión local de 30 grados. Seleccione Basis para editar reposo. Los grupos de cada lado localizan las paredes y los vértices móviles. Material lateral de piel por color de vértice, con UV de autoría separada. Pendientes dedos medio/anular y anular/meñique, ajuste de pared y rig completo.\n"
    )
    obj.name = "Personaje · índices reconstruidos"
    obj.vertex_groups.active_index = obj.vertex_groups["R.Paredes reconstruidas"].index
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    blend = out / "hand-index-retopology.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend.resolve()), compress=True)
    report = {
        "blender": bpy.app.version_string,
        "sourceModelSha256": hand.SOURCE_SHA,
        "inputBlendSha256": source_report["blendSha256"],
        "inputReportSha256": hand.sha(source / "hand-review.json"),
        "blendSha256": hand.sha(blend),
        "recipeSha256": hand.sha(Path(__file__)),
        "triangles": len(new.polygons),
        "wallTriangles": sum(p.material_index == 1 for p in new.polygons),
        "sides": sides,
        "views": {},
    }
    for side in ("L", "R"):
        for camera in ["Palma", "Dorso"]:
            scene.camera = bpy.data.objects[camera + "." + side]
            for value, label in [(0, "reposo"), (1, "flexion")]:
                key = obj.data.shape_keys.key_blocks["Prueba.Indice." + side]
                key.value = value
                png = out / (camera + "." + side + "-" + label + ".png")
                scene.render.filepath = str(png.resolve())
                bpy.ops.render.render(write_still=True)
                report["views"][png.name] = hand.sha(png)
            key.value = 0
    (out / "index-retopology.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    )
    if hand.sha(base) != source_report["blendSha256"]:
        raise RuntimeError("The input changed during reconstruction")


if __name__ == "__main__":
    build(*map(Path, sys.argv[sys.argv.index("--") + 1 :]))
