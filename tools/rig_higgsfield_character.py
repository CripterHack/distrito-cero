"""Fit the #71 character to the game's articulated body and bake two portable cycles.

blender -b -t 2 --python-exit-code 1 -P tools/rig_higgsfield_character.py -- INPUT.glb NEW_DIRECTORY
"""

from pathlib import Path
import hashlib
import json
import struct
import subprocess
import sys

import numpy as np
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parent))
from bake_human_uv import decode, read_accessor

SOURCE_SHA = "9b74d3e839623de66f5ccffb822cd74dad85f4afa0dd6d18a333c911095c06e7"
AXES = np.array([[0, 0, -1], [0, 1, 0], [1, 0, 0]], dtype=float)
MIRROR = np.diag([-1.0, 1.0, 1.0])
# Midlines of the cropped sleeve, wrist, knee and ankle cross-sections in
# metres. The source stands with its right foot set back and toes turned out.
BODY = {
    "pelvis": (0.006, 0.932, -0.023),
    "spine": (0.003, 1.132, -0.028),
    "chest": (0.001, 1.369, -0.027),
    "neck": (0, 1.538, -0.011),
    "head": (0, 1.624, 0.015),
}
LIMBS = {
    "L": [
        (0.076, 1.424, -0.040),
        (0.216, 1.454, -0.051),
        (0.479, 1.385, -0.042),
        (0.707, 1.378, 0.014),
        (0.111, 0.927, -0.018),
        (0.138, 0.501, 0.040),
        (0.145, 0.101, 0.009),
    ],
    "R": [
        (-0.076, 1.424, -0.040),
        (-0.214, 1.443, -0.041),
        (-0.478, 1.383, -0.030),
        (-0.706, 1.375, 0.021),
        (-0.105, 0.928, -0.030),
        (-0.078, 0.500, -0.068),
        (-0.081, 0.104, -0.137),
    ],
}
LIMB_NAMES = ["clavicle", "upperArm", "forearm", "hand", "thigh", "shin", "foot"]
# Digit knuckle mass centres and measured tips from the #71 surface landmarks,
# expressed in glTF authoring metres after aligning +Z forward.
DIGITS = {
    "index": ((0.813, 0.471, 0.038), (0.900, 0.470, 0.073)),
    "middle": ((0.811, 0.449, 0.035), (0.910, 0.443, 0.075)),
    "ring": ((0.810, 0.428, 0.036), (0.895, 0.425, 0.068)),
    "little": ((0.811, 0.408, 0.038), (0.863, 0.403, 0.065)),
    "thumb": ((0.754, 0.493, 0.047), (0.803, 0.531, 0.096)),
}


def smooth(low, high, x):
    t = np.clip((x - low) / (high - low), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def unit(v):
    return v / np.linalg.norm(v)


def alignment(source, target, src_side=(0, 0, 1), dst_side=(0, 0, 1)):
    def frame(axis, side):
        first = unit(axis)
        second = unit(np.asarray(side) - np.dot(side, first) * first)
        return np.column_stack((first, second, np.cross(first, second)))

    return frame(target, dst_side) @ frame(source, src_side).T


def skeleton(ground):
    bind = {k: np.asarray(p) for k, p in BODY.items()}
    rays = {}
    for side, points in LIMBS.items():
        sign = 1 if side == "L" else -1
        for name, p in zip(LIMB_NAMES, points):
            bind[name + side] = np.array(p)
        for name, (base, tip) in DIGITS.items():
            base, tip = np.array(base), np.array(tip)
            base[0] *= sign
            tip[0] *= sign
            base[1] += ground
            tip[1] += ground
            if side == "R" and name in ("middle", "ring"):
                tip[1] -= 0.004
            rays[name + side] = (base, tip)
            for j, t in enumerate((0.0, 0.42, 0.74)):
                bind[f"{name}{j}{side}"] = (1 - t) * base + t * tip
    return bind, rays


def skin_weights(points, bones, rays):
    x, y, z = points.T
    radial = np.abs(x)
    indices = {b[0]: i for i, b in enumerate(bones)}
    weight = np.zeros((len(x), len(bones)))

    def add(name, value):
        weight[:, indices[name]] = value

    # The legs are distinct below the crotch at y=0.81. Blend to the pelvis
    # across the joined denim above it instead of assigning by sign alone.
    leg = 1 - smooth(0.789, 1.005, y)
    halfwidth = 0.001 + 0.076 * smooth(0.785, 0.940, y)
    left = smooth(0.014 - halfwidth, 0.014 + halfwidth, x)
    foot = 1 - smooth(0.082, 0.171, y)
    front_thigh = smooth(0.29, 0.71, y)
    # The two overlapping envelopes spread deep running flexion over the denim
    # on either side of the crease. End the transition before the cuff and inseam.
    back_thigh = 0.5 * (smooth(0.095, 0.5054, y) + smooth(0.4446, 0.855, y))
    back_thigh *= smooth(0.17, 0.29, y)
    back_thigh += (1 - back_thigh) * smooth(0.71, 0.79, y)
    for side, fraction in [("L", left), ("R", 1 - left)]:
        knee_z = LIMBS[side][5][2]
        front = smooth(knee_z - 0.060, knee_z + 0.110, z)
        thigh = back_thigh + (front_thigh - back_thigh) * front
        add("foot" + side, leg * fraction * foot)
        add("shin" + side, leg * fraction * (1 - foot) * (1 - thigh))
        add("thigh" + side, leg * fraction * thigh)

    # Tailor the shoulder weights to the sloping lower edge of each sleeve.
    # The torso just below the armpits stays with the rib cage.
    # On the shoulder cap, spread the weight change over the collar and sleeve.
    crown = smooth(1.34, 1.49, y)
    arm = smooth(0.10 - 0.02 * crown, 0.205 + 0.055 * crown, radial) * smooth(1.255, 1.44, y)
    arm = np.maximum(arm, smooth(0.17, 0.31, radial) * smooth(1.255, 1.30, y))
    arm *= 1 - smooth(1.55, 1.61, y)
    torso = (1 - leg) * (1 - arm)
    spine = smooth(0.995, 1.20, y)
    chest = smooth(1.18, 1.35, y)
    neck = smooth(1.472, 1.575, y) * (1 - smooth(0.077, 0.158, radial))
    head = smooth(1.544, 1.630, y)
    # The top of the hair follows the skull even where it is wider than the neck.
    neck = np.maximum(neck, smooth(1.587, 1.624, y))
    add("pelvis", torso * (1 - spine))
    add("spine", torso * spine * (1 - chest))
    add("chest", torso * spine * chest * (1 - neck))
    add("neck", torso * neck * (1 - head))
    add("head", torso * neck * head)

    upper = smooth(0.132 + 0.018 * crown, 0.301 + 0.039 * crown, radial)
    forearm = smooth(0.409, 0.550, radial)
    hand = smooth(0.665, 0.748, radial)
    for side, sign in [("L", 1), ("R", -1)]:
        part = arm * (x * sign > 0)
        add("clavicle" + side, part * (1 - upper))
        add("upperArm" + side, part * upper * (1 - forearm))
        add("forearm" + side, part * forearm * (1 - hand))
        palm = part * hand
        # Each ray is inside a measured digit. Soft assignment across the
        # remaining shared webs avoids discontinuous weights on a single face.
        distances, fractions = [], []
        for name in DIGITS:
            start, tip = rays[name + side]
            axis = tip - start
            t = (points - start) @ axis / np.dot(axis, axis)
            nearest = start + np.clip(t, 0, 1)[:, None] * axis
            distances.append(np.sum((points - nearest) ** 2, axis=1))
            fractions.append(t)
        distances = np.array(distances)
        proximity = np.exp(-(distances - distances.min(axis=0)) / (2 * 0.008**2))
        proximity /= proximity.sum(axis=0)
        transferred = np.zeros(len(points))
        for i, name in enumerate(DIGITS):
            t = fractions[i]
            amount = palm * proximity[i] * smooth(-0.23, 0.15, t)
            pip = smooth(0.23, 0.60, t)
            dip = smooth(0.59, 0.88, t)
            add(name + "0" + side, amount * (1 - pip))
            add(name + "1" + side, amount * pip * (1 - dip))
            add(name + "2" + side, amount * dip)
            transferred += amount
        add("hand" + side, np.maximum(0, palm - transferred))

    four = np.argsort(-weight, axis=1, kind="stable")[:, :4]
    largest = np.take_along_axis(weight, four, axis=1)
    if np.min(largest.sum(axis=1)) < 0.7:
        raise ValueError("Anatomical envelopes left an unassigned region")
    scaled = largest / largest.sum(axis=1)[:, None] * 255
    quantized = np.floor(scaled).astype(int)
    remainder_order = np.argsort(-(scaled - quantized), axis=1, kind="stable")
    remainder = 255 - quantized.sum(axis=1)
    for j in range(4):
        rows = np.flatnonzero(remainder > j)
        quantized[rows, remainder_order[rows, j]] += 1
    four[quantized == 0] = 0
    return four.astype("u1"), quantized.astype("u1")


def add_accessor(doc, binary, array, kind, component=5126, target=None, normalized=False, bounds=False):
    data = np.asarray(array, dtype="<f4" if component == 5126 else "u1")
    binary.extend(b"\0" * ((-len(binary)) % 4))
    view = {"buffer": 0, "byteOffset": len(binary), "byteLength": data.nbytes}
    if target:
        view["target"] = target
    index = len(doc["bufferViews"])
    doc["bufferViews"].append(view)
    binary.extend(data.tobytes())
    acc = {"bufferView": index, "componentType": component, "count": len(data), "type": kind}
    if normalized:
        acc["normalized"] = True
    if bounds:
        acc["min"] = np.atleast_1d(data.min(axis=0)).tolist()
        acc["max"] = np.atleast_1d(data.max(axis=0)).tolist()
    doc["accessors"].append(acc)
    return len(doc["accessors"]) - 1


def bake_mesh_axes(doc, binary, scale):
    primitives = doc["meshes"][0]["primitives"]
    source_positions = [read_accessor(doc, binary, p["attributes"]["POSITION"]) for p in primitives]
    ground = -min(p[:, 1].min() for p in source_positions) * scale
    transformed = []
    for p in primitives:
        for block in [p["attributes"], *p["targets"]]:
            for name in ("POSITION", "NORMAL", "TANGENT"):
                if name not in block:
                    continue
                index = block[name]
                a = doc["accessors"][index]
                if "sparse" in a:
                    sparse = a["sparse"]
                    v = doc["bufferViews"][sparse["values"]["bufferView"]]
                    values = (
                        np.frombuffer(binary, "<f4", sparse["count"] * 3, v["byteOffset"])
                        .reshape(-1, 3)
                        .copy()
                    )
                else:
                    v = doc["bufferViews"][a["bufferView"]]
                    values = read_accessor(doc, binary, index)
                values[:, :3] = values[:, :3] @ AXES.T
                if name == "POSITION":
                    values *= scale
                    if block is p["attributes"]:
                        values[:, 1] += ground
                        transformed.append(values.copy())
                if "byteStride" in v or a.get("byteOffset", 0) != 0 or v["byteLength"] != values.nbytes:
                    raise ValueError("Unexpected interleaved layout for frozen character")
                start = v.get("byteOffset", 0)
                binary[start : start + values.nbytes] = values.tobytes()
                if "min" in a:
                    lo, hi = values.min(axis=0), values.max(axis=0)
                    if "sparse" in a:
                        lo, hi = np.minimum(lo, 0), np.maximum(hi, 0)
                    a["min"], a["max"] = lo.tolist(), hi.tolist()
    return transformed, float(ground)


def arm_alignment(bind, native_rest):
    align = {}
    for side in ("L", "R"):
        for bone, child in [("upperArm", "forearm"), ("forearm", "hand")]:
            axis = bind[child + side] - bind[bone + side]
            target = native_rest[child + side] - native_rest[bone + side]
            align[bone + side] = alignment(axis, target)
        arm = "hand" + side
        axis = bind["middle0" + side] - bind[arm]
        finger_axis = bind["index0" + side] - bind["little0" + side]
        align[arm] = alignment(
            axis,
            native_rest["middle0" + side] - native_rest[arm],
            finger_axis,
            native_rest["index0" + side] - native_rest["little0" + side],
        )
    return align


def retarget_frame(frame, bones, bind, arm_align, sole):
    world = {}
    for i, (name, _, _) in enumerate(bones):
        palette = np.asarray(frame["matrices"][16 * i : 16 * i + 16]).reshape(4, 4).T
        world[name] = MIRROR @ palette[:3, :3] @ MIRROR
    for name, correction in arm_align.items():
        world[name] = world[name] @ correction
    # Locomotion holds a relaxed open hand. The separated index morphs can
    # still be dialled independently of the skin. Remaining long fingers share webs.
    for side in ("L", "R"):
        for name in DIGITS:
            for j in range(3):
                world[f"{name}{j}{side}"] = world["hand" + side]

    root = bind["pelvis"].copy()
    root[1] += frame["rootY"]
    hips, targets = {}, {}
    for side, yaw in [("L", -0.304), ("R", 0.397)]:
        thigh, shin, foot = [k + side for k in ("thigh", "shin", "foot")]
        f = frame["feet"][side]
        pitch = f["pitch"]
        world[foot] = (
            Rotation.from_rotvec([pitch, 0, 0]).as_matrix() @ Rotation.from_rotvec([0, yaw, 0]).as_matrix()
        )
        heel_toe_height = 0.015 + 0.070 * np.cos(pitch) + np.sin(pitch) * (0.205 if pitch >= 0 else -0.075)
        lift = max(0, f["y"] - heel_toe_height)
        ankle_y = lift - ((sole[side] - bind[foot]) @ world[foot][1]).min()
        targets[side] = np.array([bind[thigh][0], ankle_y, bind["pelvis"][2] + f["z"]])
        hips[side] = world["pelvis"] @ (bind[thigh] - bind["pelvis"])
        reach = np.linalg.norm(bind[shin] - bind[thigh]) + np.linalg.norm(bind[foot] - bind[shin]) - 0.002
        delta = root + hips[side] - targets[side]
        permitted = np.sqrt(max(0.001, reach**2 - delta[0] ** 2 - delta[2] ** 2))
        root[1] = min(root[1], targets[side][1] + permitted - hips[side][1])
    for side in ("L", "R"):
        thigh, shin, foot = [k + side for k in ("thigh", "shin", "foot")]
        hip = root + hips[side]
        thigh_axis, shin_axis = bind[shin] - bind[thigh], bind[foot] - bind[shin]
        a, b = np.linalg.norm(thigh_axis), np.linalg.norm(shin_axis)
        v = targets[side] - hip
        distance = np.linalg.norm(v)
        direction = v / distance
        pole = np.array([0.0, 0.0, 1.0])
        forward = unit(pole - np.dot(direction, pole) * direction)
        along = (a * a + distance * distance - b * b) / (2 * distance)
        knee = hip + direction * along + forward * np.sqrt(max(0, a * a - along * along))
        lateral = [1, 0, 0]
        world[thigh] = alignment(thigh_axis, knee - hip, lateral, lateral)
        world[shin] = alignment(shin_axis, targets[side] - knee, lateral, lateral)
    rotations = []
    for name, parent, _ in bones:
        local = world[parent].T @ world[name] if parent else world[name]
        rotations.append(Rotation.from_matrix(local).as_quat())
    return root, rotations


def create(source, destination):
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA:
        raise ValueError("Expected the reviewed character-index-retopo.glb from PR #71")
    if destination.exists():
        raise FileExistsError("Choose a new output directory")
    doc, packed = decode(raw)
    binary = bytearray(packed[: doc["buffers"][0]["byteLength"]])
    scale = doc["nodes"][0].pop("scale")[0]
    points, ground = bake_mesh_axes(doc, binary, scale)
    bind, rays = skeleton(ground)
    sampler = Path(__file__).with_name("sample_higgsfield_locomotion.cjs")
    native = json.loads(subprocess.check_output(["node", str(sampler)]))
    bones = native["bones"]
    ids = {b[0]: i + 1 for i, b in enumerate(bones)}
    for name, parent, _ in bones:
        p = bind[name] - bind[parent] if parent else bind[name]
        doc["nodes"].append({"name": name, "translation": p.tolist()})
    for name, parent, _ in bones:
        if parent:
            doc["nodes"][ids[parent]].setdefault("children", []).append(ids[name])
    root_id = ids["pelvis"]
    doc["scenes"][0]["nodes"].append(root_id)
    doc["nodes"][0]["skin"] = 0
    inv = np.tile(np.eye(4), (len(bones), 1, 1))
    inv[:, :3, 3] = -np.stack([bind[name] for name, _, _ in bones])
    doc["skins"] = [
        {
            "name": "Distrito Cero · Higgsfield",
            "joints": list(range(1, len(bones) + 1)),
            "skeleton": root_id,
            "inverseBindMatrices": add_accessor(doc, binary, inv.transpose(0, 2, 1).reshape(-1, 16), "MAT4"),
        }
    ]

    for primitive, pos in zip(doc["meshes"][0]["primitives"], points):
        joints, weights = skin_weights(pos, bones, rays)
        primitive["attributes"]["JOINTS_0"] = add_accessor(doc, binary, joints, "VEC4", 5121, 34962)
        primitive["attributes"]["WEIGHTS_0"] = add_accessor(
            doc, binary, weights, "VEC4", 5121, 34962, normalized=True
        )
    neutral = {name: MIRROR @ p for name, _, p in bones}
    arm = arm_alignment(bind, neutral)
    sole = {
        side: points[0][((points[0][:, 0] - 0.014) * s > 0) & (points[0][:, 1] < 0.079)]
        for s, side in [(1, "L"), (-1, "R")]
    }
    doc["animations"] = []
    for clip in native["clips"]:
        frames = clip["frames"]
        times = add_accessor(doc, binary, [f["t"] for f in frames], "SCALAR", bounds=True)
        animation = {"name": clip["name"], "channels": [], "samplers": []}

        def channel(name, path, data):
            target = add_accessor(doc, binary, data, "VEC4" if path == "rotation" else "VEC3")
            animation["channels"].append(
                {"target": {"node": ids[name], "path": path}, "sampler": len(animation["samplers"])}
            )
            animation["samplers"].append({"input": times, "output": target, "interpolation": "LINEAR"})

        poses = [retarget_frame(frame, bones, bind, arm, sole) for frame in frames]
        channel("pelvis", "translation", [p[0] for p in poses])
        for i, (name, _, _) in enumerate(bones):
            qs = np.array([p[1][i] for p in poses])
            for j in range(1, len(qs)):
                if np.dot(qs[j - 1], qs[j]) < 0:
                    qs[j] *= -1
            if np.max(np.abs(qs[:, :3])) > 1e-6:
                channel(name, "rotation", qs)
        doc["animations"].append(animation)

    doc["buffers"][0]["byteLength"] = len(binary)
    encoded = json.dumps(doc, separators=(",", ":"), ensure_ascii=False).encode()
    encoded += b" " * ((-len(encoded)) % 4)
    binary.extend(b"\0" * ((-len(binary)) % 4))
    output = (
        struct.pack("<4sII", b"glTF", 2, 28 + len(encoded) + len(binary))
        + struct.pack("<I4s", len(encoded), b"JSON")
        + encoded
        + struct.pack("<I4s", len(binary), b"BIN\0")
        + binary
    )
    destination.mkdir(parents=True, exist_ok=False)
    filename = "character-walk.glb"
    (destination / filename).write_bytes(output)
    manifest = {
        "schema": 1,
        "file": filename,
        "bytes": len(output),
        "sha256": hashlib.sha256(output).hexdigest(),
        "sourceSha256": SOURCE_SHA,
        "nativeJoints": len(bones),
        "clips": {c["name"]: c["frames"][-1]["t"] for c in native["clips"]},
    }
    (destination / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    create(*map(Path, sys.argv[sys.argv.index("--") + 1 :]))
