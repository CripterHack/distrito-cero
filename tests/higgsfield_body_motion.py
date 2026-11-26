"""Verify the authored walk after export and a fresh import into Blender.

blender -b -t 2 --python-exit-code 1 -P tests/higgsfield_body_motion.py -- ORIGINAL.glb WALK.glb REPORT.json
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys

import bpy
import numpy as np
from scipy.spatial import cKDTree
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from bake_human_uv import decode


class Container:
    def __init__(self, path):
        raw = path.read_bytes()
        self.sha = hashlib.sha256(raw).hexdigest()
        self.doc, self.buffer = decode(raw)

    def view(self, index):
        v = self.doc["bufferViews"][index]
        start = v.get("byteOffset", 0)
        return memoryview(self.buffer)[start:start + v["byteLength"]]

    def values(self, index):
        a = self.doc["accessors"][index]
        widths = {"SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4, "MAT4": 16}
        types = {5121: "<u1", 5123: "<u2", 5125: "<u4", 5126: "<f4"}
        width, dtype = widths[a["type"]], np.dtype(types[a["componentType"]])
        if "bufferView" in a:
            v = self.doc["bufferViews"][a["bufferView"]]
            values = np.ndarray((a["count"], width), dtype=dtype, buffer=self.view(a["bufferView"]),
                                offset=a.get("byteOffset", 0),
                                strides=(v.get("byteStride", width*dtype.itemsize), dtype.itemsize)).copy()
        else:
            values = np.zeros((a["count"], width), dtype=dtype)
        if "sparse" in a:
            s = a["sparse"]
            i, v = s["indices"], s["values"]
            ids = np.frombuffer(self.view(i["bufferView"]), dtype=types[i["componentType"]],
                                offset=i.get("byteOffset", 0), count=s["count"])
            assert np.all(ids[1:] > ids[:-1])
            values[ids] = np.frombuffer(self.view(v["bufferView"]), dtype=dtype,
                                        offset=v.get("byteOffset", 0), count=len(ids)*width).reshape(-1, width)
        if a.get("normalized"):
            values = values.astype(np.float64) / np.iinfo(dtype).max
        assert np.isfinite(values).all()
        return values


def native_hierarchy():
    script = """
const fs = require('node:fs'), vm = require('node:vm');
for (const file of ['core', 'character-motion', 'skin-rig']) {
  vm.runInThisContext(fs.readFileSync('src/' + file + '.js', 'utf8'));
}
console.log(JSON.stringify(DC.SkinRig.bones.map(([name, parent]) => [name, parent])));
"""
    return dict(json.loads(subprocess.check_output(["node", "-e", script], cwd=ROOT)))


def game_axes(v):
    return v[:, [2, 1, 0]] * [-1., 1., 1.]


def compare_art(source, candidate):
    original, new = source.doc["meshes"][0], candidate.doc["meshes"][0]
    assert len(source.doc["meshes"]) == len(candidate.doc["meshes"]) == 1
    assert original["extras"]["targetNames"] == new["extras"]["targetNames"] == ["Prueba.Indice.L", "Prueba.Indice.R"]
    assert new["weights"] == original["weights"] == [0, 0]
    for key in ("materials", "textures", "samplers"):
        assert source.doc.get(key) == candidate.doc.get(key), f"{key} changed"
    images = {}
    for old, current in zip(source.doc["images"], candidate.doc["images"], strict=True):
        assert old["name"] == current["name"] and old["mimeType"] == current["mimeType"]
        old_bytes = source.view(old["bufferView"])
        assert old_bytes == candidate.view(current["bufferView"])
        images[old["name"]] = hashlib.sha256(old_bytes).hexdigest()
    assert len(images) == 3
    scale = source.doc["nodes"][0]["scale"]
    assert scale[0] == scale[1] == scale[2]
    ground = min(source.values(p["attributes"]["POSITION"])[:, 1].min() * scale[1]
                 for p in original["primitives"])
    points, triangles = [], 0
    for old, current in zip(original["primitives"], new["primitives"], strict=True):
        assert old["material"] == current["material"]
        indices = source.values(old["indices"])
        assert np.array_equal(indices, candidate.values(current["indices"]))
        triangles += indices.size // 3
        attributes = current["attributes"]
        assert set(attributes) == set(old["attributes"]) | {"JOINTS_0", "WEIGHTS_0"}
        for name, accessor in old["attributes"].items():
            expected = source.values(accessor)
            if name == "POSITION":
                expected = game_axes(expected) * scale[0] - [0., ground, 0.]
                points.append(expected)
            elif name == "NORMAL":
                expected = game_axes(expected)
            elif name == "TANGENT":
                expected = np.column_stack((game_axes(expected[:, :3]), expected[:, 3]))
            np.testing.assert_allclose(candidate.values(attributes[name]), expected, atol=2e-6, rtol=0,
                                       err_msg=f"Unexpected change in {name}")
        for old_target, new_target in zip(old["targets"], current["targets"], strict=True):
            assert set(new_target) == set(old_target)
            for semantic in old_target:
                expected = game_axes(source.values(old_target[semantic]))
                if semantic == "POSITION":
                    expected *= scale[0]
                np.testing.assert_allclose(candidate.values(new_target[semantic]), expected, atol=2e-6, rtol=0)
    return triangles, images, np.concatenate(points)


def verify_skin(walk, hierarchy):
    nodes = walk.doc["nodes"]
    skin, = walk.doc["skins"]
    mesh_id, = [i for i, n in enumerate(nodes) if "mesh" in n]
    assert nodes[mesh_id]["skin"] == 0
    joints = skin["joints"]
    names = [nodes[i]["name"] for i in joints]
    assert len(names) == len(set(names)) == len(hierarchy) == 49 and set(names) == set(hierarchy)
    parents = {child: i for i, node in enumerate(nodes) for child in node.get("children", [])}
    for joint, name in zip(joints, names):
        parent = parents.get(joint)
        assert (nodes[parent]["name"] if parent in joints else None) == hierarchy[name], name
    inverse = walk.values(skin["inverseBindMatrices"]).reshape(-1, 4, 4)
    assert len(inverse) == len(names) and (np.abs(np.linalg.det(inverse)) > .001).all()
    weighted = set()
    totals = []
    for primitive in walk.doc["meshes"][0]["primitives"]:
        attrs = primitive["attributes"]
        indices, weights = walk.values(attrs["JOINTS_0"]), walk.values(attrs["WEIGHTS_0"])
        n = walk.doc["accessors"][attrs["POSITION"]]["count"]
        assert indices.shape == weights.shape == (n, 4) and indices.dtype.kind == "u"
        assert indices.max() < len(joints) and weights.min() >= 0 and weights.max() <= 1
        np.testing.assert_allclose(weights.sum(axis=1), 1, atol=2e-5, rtol=0)
        for slot in range(4):
            weighted.update(indices[weights[:, slot] > 0, slot].tolist())
        totals.append(np.count_nonzero(weights > 0, axis=1))
    weighted = sorted(names[i] for i in weighted)
    required = {"pelvis", "head"} | {section+side for side in ["L", "R"] for section in
                                      ["upperArm", "forearm", "hand", "thigh", "shin", "foot"]}
    assert required <= set(weighted), f"Missing weights for {required - set(weighted)}"
    return {"joints": len(joints), "weightedJoints": weighted,
            "vertexCountsByInfluences": np.bincount(np.concatenate(totals), minlength=5)[1:].tolist()}


def animation_span(walk, animation):
    assert animation["channels"]
    seen, spans = set(), []
    for channel in animation["channels"]:
        target = channel["target"]
        key = (target["node"], target["path"])
        assert key not in seen and target["path"] in ("rotation", "translation", "scale")
        seen.add(key)
        sampler = animation["samplers"][channel["sampler"]]
        times = walk.values(sampler["input"]).ravel()
        values = walk.values(sampler["output"])
        assert np.all(np.diff(times) > 0) and np.all(np.isfinite(values))
        if target["path"] == "rotation":
            np.testing.assert_allclose(np.linalg.norm(values, axis=1), 1, atol=.0005, rtol=0)
        spans.append((float(times[0]), float(times[-1])))
    first, last = min(s[0] for s in spans), max(s[1] for s in spans)
    assert np.isclose(first, 0) and last > first
    return animation["name"], last - first


def positions(obj):
    mesh = obj.data
    local = np.empty(len(mesh.vertices)*3, dtype=np.float32)
    mesh.vertices.foreach_get("co", local)
    transform = np.array(obj.matrix_world)
    world = local.reshape(-1, 3) @ transform[:3, :3].T + transform[:3, 3]
    # The glTF importer rotates Y-up, +Z forward to Blender Z-up, -Y forward.
    return world[:, [0, 2, 1]] * [1., 1., -1.]


def inspect_playback(path, name, duration, expected_points):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    scene = bpy.context.scene
    rig, = [o for o in scene.objects if o.type == "ARMATURE"]
    mesh, = [o for o in scene.objects if o.type == "MESH" and o.data.shape_keys]
    assert any(m.type == "ARMATURE" and m.object == rig for m in mesh.modifiers)
    assert len(rig.data.bones) == 49 and mesh.data.shape_keys
    packed_maps = [image for image in bpy.data.images if image.packed_file]
    assert len(packed_maps) == 3 and all(tuple(image.size) == (4096, 4096) for image in packed_maps)
    assert all(k.value == 0 for k in list(mesh.data.shape_keys.key_blocks)[1:])
    graph = bpy.context.evaluated_depsgraph_get()
    rig.data.pose_position = "REST"
    graph.update()
    base = positions(mesh.evaluated_get(graph))
    np.testing.assert_allclose([base.min(0), base.max(0)], [expected_points.min(0), expected_points.max(0)],
                               atol=.0001, rtol=0, err_msg="Bind pose differs after fresh import")
    # Trace independent skin regions selected by rest geometry, including the shoes and distal hands.
    zones = {}
    for label, sign in (("L", 1), ("R", -1)):
        zones["shoe"+label] = (base[:, 1] < .14) & (base[:, 0]*sign > .03)
        zones["hand"+label] = base[:, 0]*sign > .74
    assert all(mask.sum() > 50 for mask in zones.values())
    edges = np.array([tuple(e.vertices) for e in mesh.data.edges])
    rest_lengths = np.linalg.norm(base[edges[:, 0]] - base[edges[:, 1]], axis=1)
    valid = rest_lengths > .001
    radial = np.abs(base[:, 0])
    sleeve = (radial > .07) & (radial < .37) & (base[:, 1] > 1.23) & (base[:, 1] < 1.69)
    shoulder_edges = sleeve[edges].any(axis=1)
    # Inspect the back of both trouser knees in bind coordinates, including
    # seams. Trace physical edges over 8 mm to keep tiny UV slivers out of the metric.
    mid = base[edges].mean(axis=1)
    back_knees = {side: (np.abs(mid[:, 1] - .5) < .12) & (mid[:, 0]*sign > .015)
                  & (mid[:, 2] < knee_z - .015) & (rest_lengths >= .008)
                  for side, sign, knee_z in (("R", -1, -.068), ("L", 1, .040))}
    assert all(mask.sum() > 100 for mask in back_knees.values())
    knee_samples = {side: [] for side in back_knees}
    # The documented seam is identified in bind space; vertex order can
    # change during import. Its midpoint and length are in metres.
    landmark = [-.06231844, .50810161, -.16068449]
    crease = np.flatnonzero((np.linalg.norm(mid - landmark, axis=1) < .0001)
                            & (np.abs(rest_lengths - .05493929) < .0001))
    assert len(crease) > 0, "Reference trouser edge missing"
    crease_lengths = []
    _, keep, group = np.unique(np.round(base, 7), axis=0, return_index=True, return_inverse=True)
    first_at_position = keep[group]
    duplicated = first_at_position != np.arange(len(base))
    seam_errors = []
    rig.data.pose_position = "POSE"
    graph.update()
    fps = scene.render.fps/scene.render.fps_base
    assert rig.animation_data and rig.animation_data.action, "A fresh import must play the walk on the rig"
    track = rig.animation_data.nla_tracks[name]
    assert len(track.strips) == 1
    rig.animation_data.action = track.strips[0].action
    first = rig.animation_data.action.frame_range[0]
    records, frames, strain = [], [], []
    peak_edge = None
    peak_shoulder_change = 0.
    for i in range(33):
        f = float(first + fps*duration*i/32)
        frame = math.floor(f)
        scene.frame_set(frame, subframe=f-frame)
        pts = positions(mesh.evaluated_get(graph))
        assert np.isfinite(pts).all()
        if np.any(duplicated):
            gaps = np.linalg.norm(pts[duplicated] - pts[first_at_position[duplicated]], axis=1)
            seam_errors.append(float(gaps.max()))
        lengths = np.linalg.norm(pts[edges[:, 0]] - pts[edges[:, 1]], axis=1)
        crease_lengths.append(float(lengths[crease].min()))
        ratios = lengths[valid] / rest_lengths[valid]
        for side, mask in back_knees.items():
            ids = np.flatnonzero(mask)
            local_ratios = lengths[ids] / rest_lengths[ids]
            k = ids[np.argmin(local_ratios)]
            knee_samples[side].append({"phase": i/32, "minimumRatio": float(local_ratios.min()),
                                        "p01Ratio": float(np.percentile(local_ratios, 1)),
                                        "restM": float(rest_lengths[k]), "posedM": float(lengths[k]),
                                        "maximumRatio": float(local_ratios.max())})
        changes = np.abs(lengths - rest_lengths)
        peak_shoulder_change = max(peak_shoulder_change, float(changes[shoulder_edges].max()))
        worst = int(np.argmax(changes))
        if peak_edge is None or changes[worst] > peak_edge["lengthChangeM"]:
            peak_edge = {"phase": i/32, "lengthChangeM": float(changes[worst]),
                         "restLengthM": float(rest_lengths[worst]), "posedLengthM": float(lengths[worst]),
                         "restMidpointM": base[edges[worst]].mean(axis=0).tolist()}
        strain.append((float(np.percentile(ratios, 1)), float(np.percentile(ratios, 99))))
        record = {key: pts[mask].mean(axis=0).tolist() for key, mask in zones.items()}
        record.update({"phase": i/32, "minimumSoleHeightM":{k:float(pts[v, 1].min())
                       for k, v in zones.items() if k.startswith("shoe")}})
        records.append(record)
        frames.append(pts)
    # Track differences so a translation of the whole actor cannot masquerade as a step.
    foot_differences = np.array([s["shoeL"][2] - s["shoeR"][2] for s in records])
    hand_differences = np.array([s["handL"][2] - s["handR"][2] for s in records])
    max_travel = max(float(np.linalg.norm(frame - frames[0], axis=1).max()) for frame in frames)
    gait = {}
    if name in ("Marcha", "Carrera"):
        assert foot_differences.min() < -.035 and foot_differences.max() > .035, "Shoes never exchange lead"
        assert np.ptp(hand_differences) > .05, "Arm swing missing from the skinned hands"
        correlation = float(np.corrcoef(foot_differences[:-1], hand_differences[:-1])[0, 1])
        assert correlation < -.5, "Arms should advance opposite the legs"
        gait["handToShoeLeadCorrelation"] = correlation
        for side in ("L", "R"):
            heights = [s["minimumSoleHeightM"]["shoe"+side] for s in records]
            assert -.005 < min(heights) < .005 and max(heights) > .025, "Missing stance or swing"
        if name == "Carrera":
            assert duration < .65, "A frightened pedestrian must turn over faster than a walker"
            assert max(min(r["minimumSoleHeightM"].values()) for r in records) > .020, "Missing running flight phase"
    else:
        assert max_travel > .0005, "Rest clip plays a static mesh"

    closure = float(np.linalg.norm(frames[0] - frames[-1], axis=1).max())
    assert closure < .002, f"Visible position jump at loop wrap: {closure:.4f} m"
    max_seam = max(seam_errors, default=0.)
    assert max_seam < .0001, f"Bind-coincident vertices split by {max_seam:.5f} m"
    assert min(s[0] for s in strain) > .45 and max(s[1] for s in strain) < 1.8, "Widespread mesh collapse/stretch"
    shoulder_limit = .030 if name == "Reposo" else .035
    assert peak_shoulder_change < shoulder_limit, f"Sleeve deforms by {peak_shoulder_change:.4f} m near shoulder"
    for side, samples in knee_samples.items():
        worst = min(samples, key=lambda s: s["minimumRatio"])
        assert worst["minimumRatio"] > .50, f"Posterior knee {side} collapses at {name}: {worst}"
    if name == "Marcha":
        assert min(crease_lengths) / rest_lengths[crease[0]] > .65, "Right trouser crease still pinches"
    # Exercise both independently after posing; the opposite hand and sleeves must stay still.
    morph_motion = {}
    for side in ("L", "R"):
        key = mesh.data.shape_keys.key_blocks["Prueba.Indice." + side]
        key.value = 1
        graph.update()
        movement = np.linalg.norm(positions(mesh.evaluated_get(graph)) - frames[-1], axis=1)
        moved = movement > .00001
        assert moved.sum() > 5 and np.all(zones["hand"+side][moved]), "A finger control moved the wrong anatomy"
        morph_motion[side] = {"movedVertices": int(moved.sum()), "peakTravelM": float(movement.max())}
        key.value = 0
        graph.update()
    return {"seconds": duration, "playbackFrames": len(frames), "maxVertexTravelFromStartM": max_travel,
            "maxLoopClosureErrorM": closure,
            "shoeLeadRangeM": [float(foot_differences.min()), float(foot_differences.max())],
            "handLeadRangeM": [float(hand_differences.min()), float(hand_differences.max())],
            "maxEdgeLengthChangeM": peak_edge["lengthChangeM"], "peakEdge": peak_edge,
            "maxShoulderEdgeLengthChangeM": peak_shoulder_change, "posteriorKnees": knee_samples,
            "rightCrease": {"restLengthM": float(rest_lengths[crease[0]]), "posedLengthsM": crease_lengths},
            "posedIndexFlex": morph_motion, **gait,
            "coincidentRestVertexPairs": int(np.count_nonzero(duplicated)),
            "maxSeparationOfCoincidentVerticesM": max_seam,
            "lowestFrameEdgeRatioPercentile1": min(r[0] for r in strain),
            "highestFrameEdgeRatioPercentile99": max(r[1] for r in strain),
            "samples": records}


def inspect_turn(path, duration):
    """Measure the deforming sole surface and the join to Reposo in glTF metres."""
    assert abs(duration - 1.4) < 1e-6
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
    scene = bpy.context.scene
    rig, = [o for o in scene.objects if o.type == "ARMATURE"]
    mesh, = [o for o in scene.objects if o.type == "MESH" and o.data.shape_keys]
    graph = bpy.context.evaluated_depsgraph_get()
    rig.data.pose_position = "REST"
    graph.update()
    base = positions(mesh.evaluated_get(graph))
    soles = {side: (sign * base[:, 0] > .03) & (base[:, 1] < .075)
             for side, sign in (("L", 1), ("R", -1))}
    assert all(mask.sum() > 100 for mask in soles.values())
    mesh.data.calc_loop_triangles()
    triangles = np.array([tuple(face.vertices) for face in mesh.data.loop_triangles])
    mid = base[triangles].mean(axis=1)
    shoes = {}
    for side, sign in (("L", 1), ("R", -1)):
        selection = triangles[(mid[:, 1] < .14) & (mid[:, 0] * sign > .015)]
        assert len(selection) > 400, f"Missing boot surface {side}"
        vertices, faces = np.unique(selection, return_inverse=True)
        shoes[side] = vertices, faces.reshape(-1, 3).tolist()
    rig.data.pose_position = "POSE"

    def sample(action, phase):
        start, end = action.frame_range
        frame = start + phase * (end - start)
        scene.frame_set(math.floor(frame), subframe=frame - math.floor(frame))
        return positions(mesh.evaluated_get(graph))

    def select(name):
        # Blender retains unkeyed transforms when an action is replaced by hand.
        rig.animation_data.action = None
        for bone in rig.pose.bones:
            bone.matrix_basis = Matrix.Identity(4)
        action = rig.animation_data.nla_tracks[name].strips[0].action
        rig.animation_data.action = action
        return action

    def pelvis_position():
        head = rig.matrix_world @ rig.pose.bones["pelvis"].head
        return np.array([head.x, head.z, -head.y])

    neutral = sample(select("Reposo"), 0)
    idle_hip = pelvis_position()
    turn = select("Giro")
    endpoint_errors = []
    for phase in (0, 1):
        actual = sample(turn, phase)
        expected = neutral if phase == 0 else neutral * [-1, 1, -1]
        endpoint_errors.append(float(np.linalg.norm(actual - expected, axis=1).max()))
    assert max(endpoint_errors) < .0001, f"Turn does not join the idle mesh: {endpoint_errors}"

    steps, separation = [], float("inf")
    for i, swing in enumerate(("R", "L", "R", "L", "R")):
        support = "L" if swing == "R" else "R"
        planted = sample(turn, i / 5)[soles[support]]
        slide, support_height, lift = 0., 0., 0.
        for phase in np.linspace(i / 5, (i + 1) / 5, 31):
            points = sample(turn, phase)
            moving, fixed = points[soles[swing]], points[soles[support]]
            lateral = (fixed - planted)[:, [0, 2]]
            slide = max(slide, float(np.linalg.norm(lateral, axis=1).max()))
            support_height = max(support_height, abs(float(fixed[:, 1].min())))
            lift = max(lift, float(moving[:, 1].min()))
            # Sample the complete low shoe surfaces independent of their current heading.
            distance = cKDTree(fixed).query(moving)[0].min()
            separation = min(separation, float(distance))
            left, right = (BVHTree.FromPolygons(points[vertices].tolist(), faces, all_triangles=True)
                           for vertices, faces in shoes.values())
            assert not left.overlap(right), f"Left and right shoes intersect at phase {phase}"
        apex = (i + .5) / 5
        sample(turn, apex)
        angle = np.pi * apex**2 * (3 - 2 * apex)
        body_x = np.array([np.cos(angle), 0., -np.sin(angle)])
        lean = float(pelvis_position() @ body_x - idle_hip[0])
        assert lean * (1 if support == "L" else -1) > .025, "Weight shifted away from the support boot"
        steps.append({"swing": swing, "lateralPelvisShiftM": lean, "support": support, "maxSupportSlideM": slide,
                      "maxAbsoluteSupportHeightM": support_height, "swingClearanceM": lift})
    assert all(s["maxSupportSlideM"] < .003 and s["maxAbsoluteSupportHeightM"] < .003
               and s["swingClearanceM"] > .025 for s in steps), steps
    assert separation > .012, f"Sole surfaces are too close during the turn: {separation}"
    return {"seconds": duration, "endpointErrorsM": endpoint_errors, "steps": steps,
            "minSoleVertexSeparationM": separation, "samplesPerStep": 31,
            "shoeTriangles": {side: len(faces) for side, (_, faces) in shoes.items()}}


def verify(source_path, walk_path, report_path):
    original, walk = Container(source_path), Container(walk_path)
    assert len(walk.doc.get("skins", [])) == 1, "Expected a skinned game skeleton"
    assert sorted(a["name"] for a in walk.doc.get("animations", [])) == ["Carrera", "Giro", "Marcha", "Reposo"]
    skin = verify_skin(walk, native_hierarchy())
    tris, maps, coords = compare_art(original, walk)
    spans = dict(animation_span(walk, clip) for clip in walk.doc["animations"])
    result = {"sourceSha256": original.sha, "candidateSha256": walk.sha, "triangles": tris,
              "mapsSha256": maps, **skin, "blender": bpy.app.version_string,
              "clips": {name: inspect_playback(walk_path, name, duration, coords)
                        for name, duration in spans.items() if name != "Giro"},
              "turn": inspect_turn(walk_path, spans["Giro"])}
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print("Giro", json.dumps(result["turn"]))
    for name, motion in result["clips"].items():
        print(name, tris, "triangles;", skin["joints"], "joints;", motion["playbackFrames"], "posed frames;",
              "shoe lead (m)", motion["shoeLeadRangeM"], "loop error (m)", motion["maxLoopClosureErrorM"])


if __name__ == "__main__":
    verify(*map(Path, sys.argv[sys.argv.index("--") + 1:]))
