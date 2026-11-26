"""Verify the bilateral index retopology against its authoring scene.

blender -b --python-exit-code 1 -P tests/index_retopology_scene.py -- BEFORE.blend AFTER.blend OUT.json
"""
from collections import Counter
import hashlib
import json
from math import dist
from pathlib import Path
import sys

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from prepare_higgsfield_hand_sections import SECTIONS, components


def face_key(points):
    """Preserve winding, independent of the first corner in a triangle."""
    return min(tuple(points[i:] + points[:i]) for i in range(3))


def uv_area(uv):
    a, b, c = uv
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def outside_hand(face):
    return (max(abs(p[1]) for p in face) < .811 or
            max(p[2] for p in face) < .446 or min(p[2] for p in face) > .477)


def deformation(mesh, obj, coords, faces, side, sign):
    flex = mesh.shape_keys.key_blocks["Prueba.Indice." + side]
    posed = [obj.matrix_world @ v.co for v in flex.data]

    def sections(points):
        return {str(y): [len(ring) for ring in components(points, faces, sign*y)]
                for y in SECTIONS}

    extension, ratios = [], []
    for edge in mesh.edges:
        i, j = edge.vertices
        a, b = coords[i], coords[j]
        if min(sign*a.y, sign*b.y) < .810 or min(a.z, b.z) < .445 or max(a.z, b.z) > .493:
            continue
        length = (a-b).length
        if length > 1e-7:
            new = (posed[i]-posed[j]).length
            extension.append(new-length)
            ratios.append(new/length)
    return sections(coords), sections(posed), {
        "maxExtendedM": max(extension), "maxRatio": max(ratios), "edgesMeasured": len(ratios),
        "maxDisplacementM": max((a-b).length for a, b in zip(coords, posed)),
    }


def analyze(path):
    bpy.ops.wm.open_mainfile(filepath=str(path.resolve()))
    obj, = [o for o in bpy.context.scene.objects if o.type == "MESH" and not o.hide_render]
    mesh = obj.data
    coords = [obj.matrix_world @ v.co for v in mesh.vertices]
    faces = [list(p.vertices) for p in mesh.polygons]
    source_ids = mesh.attributes.get("DC_fuente_cara")
    exterior, uv_by_id = {}, {}
    incidences, windings = Counter(), Counter()
    wall_edges = set()
    areas = []
    wall_faces = inverted_normals = walls_outside = collapsed_wall_uvs = 0
    for poly in mesh.polygons:
        points = [coords[i] for i in poly.vertices]
        assert len(points) == 3, "Mesh contains a non-triangular face"
        a, b, c = points
        areas.append((b-a).cross(c-a).length * .5)
        xyz = [tuple(point) for point in points]
        for a, b in zip(xyz, xyz[1:] + xyz[:1]):
            edge = tuple(sorted((a, b)))
            incidences[edge] += 1
            windings[edge] += 1 if a < b else -1
            if poly.material_index:
                wall_edges.add(edge)
        normals = [tuple(mesh.corner_normals[i].vector) for i in poly.loop_indices]
        if poly.material_index:
            wall_uv = [tuple(mesh.uv_layers.active.data[i].uv) for i in poly.loop_indices]
            collapsed_wall_uvs += abs(uv_area(wall_uv)) < 1e-14
            wall_faces += 1
            walls_outside += outside_hand(xyz)
            inverted_normals += any(poly.normal.dot(normal) <= 0 for normal in normals)
            continue
        uv = [tuple(mesh.uv_layers.active.data[i].uv) for i in poly.loop_indices]
        key = face_key(xyz)
        assert key not in exterior, "Duplicate oriented exterior triangle"
        exterior[key] = dict(zip(xyz, zip(uv, normals)))
        source_face = source_ids.data[poly.index].value if source_ids else poly.index
        uv_by_id[poly.index] = (source_face, uv_area(uv))
    stats = {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "vertices": len(coords), "triangles": len(faces), "wallTriangles": wall_faces,
        "minAreaM2": min(areas), "areasBelow1e-14": sum(a < 1e-14 for a in areas),
        "wallFacesWithCollapsedUvs": collapsed_wall_uvs,
        "wallFacesOutsideHandRegion": walls_outside, "wallFacesWithInvertedCornerNormals": inverted_normals,
        "wallEdgesWithInconsistentWinding": sum(incidences[e] != 2 or windings[e] != 0 for e in wall_edges),
        "packedImageHashes": {im.name: hashlib.sha256(im.packed_file.data).hexdigest()
                              for im in bpy.data.images if im.packed_file},
        "components": {}, "componentsFlex": {}, "elongation": {},
    }
    for side, sign in (("L", 1), ("R", -1)):
        (stats["components"][side], stats["componentsFlex"][side],
         stats["elongation"][side]) = deformation(mesh, obj, coords, faces, side, sign)
    return stats, exterior, uv_by_id, {e for e, n in incidences.items() if n == 1}, {
        e for e, n in incidences.items() if n > 2}


def check_authoring_controls():
    scene = bpy.context.scene
    obj, = [o for o in scene.objects if o.type == "MESH"]
    mesh = obj.data
    assert obj.active_shape_key_index == 0
    assert [k.name for k in mesh.shape_keys.key_blocks] == ["Basis", "Prueba.Indice.L", "Prueba.Indice.R"]
    assert all(k.value == 0 for k in mesh.shape_keys.key_blocks)
    digits = ("Pulgar", "Indice", "Medio", "Anular", "Menique")
    for side in ("L", "R"):
        for name in (*digits, "Mano", "Puente.Am", "Puente.MA", "Indice movil", "Paredes reconstruidas"):
            group = obj.vertex_groups[f"{side}.{name}"]
            assert any(any(g.group == group.index and g.weight > 0 for g in v.groups) for v in mesh.vertices)
        for name in digits:
            marker = scene.objects[f"Punta.{name}.{side}"]
            i = marker['source_vertex']
            assert marker.parent == obj and (marker.location - mesh.vertices[i].co).length < 1e-7
            assert obj.vertex_groups[f"{side}.{name}"].weight(i) == 1.
        assert all(scene.objects[f"{camera}.{side}"].type == 'CAMERA' for camera in ("Palma", "Dorso"))


def main(before, after, output):
    source, old, source_uv, old_open, old_many = analyze(before)
    result, new, result_uv, new_open, new_many = analyze(after)
    kept = old.keys() & new.keys()
    removed, added = old.keys()-kept, new.keys()-kept
    max_uv = max_normal = 0.0
    changed_uv = changed_normal = 0
    for face in kept:
        for point in face:
            uv0, n0 = old[face][point]
            uv1, n1 = new[face][point]
            du, dn = dist(uv0, uv1), dist(n0, n1)
            max_uv, max_normal = max(max_uv, du), max(max_normal, dn)
            changed_uv += du > 1e-6
            changed_normal += dn > 1e-3
    for source_index, _ in result_uv.values():
        assert source_index in source_uv, "Missing source UV face for an exterior face"
    inverted_uv = sum(det*source_uv[source_index][1] < 0 for source_index, det in result_uv.values())
    collapsed_uv = sum(det == 0 and source_uv[source_index][1] != 0 for source_index, det in result_uv.values())
    report = {
        "before": source, "after": result, "blender": bpy.app.version_string,
        "preservedOriginalTriangles": len(kept), "clippedOriginalTriangles": len(removed),
        "unchangedCornersNewUvs": changed_uv, "unchangedMaxUvDelta": max_uv,
        "unchangedCornersNewNormals": changed_normal, "unchangedMaxCornerNormalDelta": max_normal,
        "changedTrianglesOutsideHandRegion": sum(map(outside_hand, removed)) + sum(map(outside_hand, added)),
        "flippedExteriorUvFaces": inverted_uv, "collapsedExteriorUvFaces": collapsed_uv,
        "openEdgesBeforeAfter": [len(old_open), len(new_open)],
        "manyEdgesBeforeAfter": [len(old_many), len(new_many)],
        "newOpenEdges": len(new_open - old_open), "newManyEdges": len(new_many - old_many),
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    for side in ("L", "R"):
        key = "0.83012"
        assert len(source["components"][side][key]) == 1, side+" reference section should have one ring"
        assert len(result["components"][side][key]) == 2, side+" repaired section should have two rings"
        assert source["elongation"][side]["maxExtendedM"] > .040
        assert result["elongation"][side]["maxExtendedM"] < .006
        assert result["elongation"][side]["maxDisplacementM"] > .030, side+" flex probe does not move"
    assert kept and removed and added and result["wallTriangles"] > 0
    assert report["changedTrianglesOutsideHandRegion"] == result["wallFacesOutsideHandRegion"] == 0
    assert changed_uv == changed_normal == 0, "Preserved exterior corner data drifted"
    assert not (new_open - old_open or new_many - old_many), "New open or non-manifold edges"
    assert result["areasBelow1e-14"] == result["wallFacesWithInvertedCornerNormals"] == 0
    assert result["wallEdgesWithInconsistentWinding"] == inverted_uv == collapsed_uv == 0
    assert result["wallFacesWithCollapsedUvs"] == 0
    check_authoring_controls()
    assert len(source["packedImageHashes"]) == 3 and source["packedImageHashes"] == result["packedImageHashes"]
    print("PASS bilateral index sections, flex strain, topology, wall normals, exterior UVs and packed images.")


if __name__ == "__main__":
    main(*map(Path, sys.argv[sys.argv.index("--") + 1:]))
