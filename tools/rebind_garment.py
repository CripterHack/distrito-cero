#!/usr/bin/env python3
"""SPEC-003: topology-aware sleeve ownership, offline and deterministic.
Preserves geometry/UVs/normals and bone IDs. Only joint and weight bytes change.
No dependency beyond Python's standard library. See docs/project/GARMENT-BINDING.md.
"""
from collections import deque
from pathlib import Path
import argparse, base64, hashlib, json, math, struct, zlib
ROOT = Path(__file__).resolve().parents[1]
ROW = struct.Struct('<3h3h2H4B4B')
ARM = ('upperArm', 'forearm', 'hand', 'clavicle')
TAG = ' Topology-aware garment ownership (DC-006): detached sleeves and trunk no longer cross-bind.'

def arm(name):
    return any(name.startswith(prefix) for prefix in ARM)

def unpack(part):
    rows = list(ROW.iter_unpack(base64.b64decode(part['data'])))
    if len(rows) != part['vertices']:
        raise ValueError('Invalid canonical vertex count')
    return rows

def ownership(rows, bones):
    # Weld for adjacency only. Original render corners and UV seams remain intact.
    lookup, points, originals, triangles = {}, [], [], []
    for row in rows:
        key = row[:3]
        if key not in lookup:
            lookup[key] = len(points)
            points.append(tuple(v / 10000 for v in key))
            originals.append(sum(w / 255 for j, w in zip(row[8:12], row[12:16]) if arm(bones[j])))
        triangles.append(lookup[key])
    graph = [set() for _ in points]
    for i in range(0, len(triangles), 3):
        a, b, c = triangles[i:i+3]
        for j, k in ((a,b),(b,c),(c,a)):
            if j != k: graph[j].add(k); graph[k].add(j)
    # At this canonical height the trunk and sleeves have three disconnected surfaces.
    # Use real mesh connectivity, not a transverse blend that spans empty armpit air.
    below = {i for i,p in enumerate(points) if p[1] < 1.26}
    components = {}
    while below:
        seed = min(below); below.remove(seed); todo = deque([seed]); members = []
        while todo:
            i = todo.popleft(); members.append(i)
            for j in sorted(graph[i]):
                if j in below: below.remove(j); todo.append(j)
        if len(members) > 30:
            xs = [points[i][0] for i in members]
            role = 'L' if max(xs) < -.19 else 'R' if min(xs) > .19 else 'trunk'
            if role in components: raise ValueError('Ambiguous garment component: '+role)
            components[role] = members
    if set(components) != {'L','R','trunk'}:
        raise ValueError('Canonical garment topology changed; review binding seeds')
    fixed = {}
    for role, members in components.items():
        for i in members:
            if points[i][1] < 1.24: fixed[i] = 0. if role == 'trunk' else 1.
    for i,(x,y,z) in enumerate(points):
        if abs(x) < .13: fixed[i] = 0.
        elif y >= 1.445: fixed[i] = originals[i]  # preserve existing collar/cap anchor
        elif abs(x) > .245: fixed[i] = 1.
    values = originals.copy()
    for i,v in fixed.items(): values[i] = v
    free = [i for i in range(len(points)) if i not in fixed]
    neighbours = [sorted(ns) for ns in graph]
    # Positive uniform graph Laplacian: no negative/cotangent weights at tiny faces.
    # Stable vertex and neighbour order keeps authoring reproducible.
    for iteration in range(4000):
        error = 0.
        for i in free:
            ns = neighbours[i]
            if not ns: continue
            new = sum(values[j] for j in ns) / len(ns)
            error = max(error, abs(new-values[i])); values[i] = new
        if error < 1e-10: break
    else: raise ValueError('Garment ownership did not converge')
    return {key: values[i] for key,i in lookup.items()}, iteration+1

def encode_weights(row, target, bones):
    weights = {j:w/255 for j,w in zip(row[8:12],row[12:16]) if w}
    groups = [{j:w for j,w in weights.items() if arm(bones[j])==kind} for kind in [False,True]]
    # Existing longitudinal influences stay intact. Fill only an empty class when
    # a connected shoulder transition actually needs it.
    if not groups[0]: groups[0] = {bones.index('chest' if row[1]>=12600 else 'spine'):1.}
    if not groups[1]: groups[1] = {bones.index('upperArm'+('L' if row[0]<0 else 'R')):1.}
    result = {}
    for group,amount in zip(groups,[1-target,target]):
        total = sum(group.values())
        for j,w in group.items():
            if amount*w/total > 1e-12: result[j] = amount*w/total
    # Existing format supports four influences. Selection and residual allocation
    # are explicit and stable, and always sum to exactly 255.
    entries = sorted(result.items(), key=lambda v:(-v[1],v[0]))[:4]
    total = sum(w for j,w in entries)
    scaled = [w/total*255 for j,w in entries]; counts = [int(math.floor(v)) for v in scaled]
    for i in sorted(range(len(entries)),key=lambda i:(-(scaled[i]-counts[i]),entries[i][0]))[:255-sum(counts)]: counts[i]+=1
    ordered = sorted([(entries[i][0],w) for i,w in enumerate(counts) if w],key=lambda v:(-v[1],v[0]))
    joints = [j for j,w in ordered]; weights = [w for j,w in ordered]
    return tuple(row[:8])+tuple(joints+[0]*(4-len(joints)))+tuple(weights+[0]*(4-len(weights)))

def rebind(source, binding_source=None):
    text = source.decode('utf-8'); data = json.loads(text.split('DC.HeroAsset=',1)[1].strip().rstrip(';'))
    if len(data['bones']) != 49 or data['stride'] != 24: raise ValueError('Unsupported rig/vertex contract')
    seeds = binding_source or json.loads((ROOT/'assets/garment-binding-source.json').read_text())
    if seeds.get('schema') != 1 or set(seeds['parts']) != {'jacket','pants'}:
        raise ValueError('Invalid authoring seed contract')
    for part in data['parts']:
        if part['name'] not in seeds['parts']: continue
        seed = seeds['parts'][part['name']]; raw = bytearray(base64.b64decode(part['data']))
        if len(raw) != seed['vertices']*24 or part['vertices'] != seed['vertices']:
            raise ValueError('Canonical garment vertex count changed')
        attributes = b''.join(raw[i:i+16] for i in range(0,len(raw),24))
        if hashlib.sha256(attributes).hexdigest() != seed['attributesSha256']:
            raise ValueError('Canonical garment geometry/UV/normal changed; review binding seeds')
        decoder = zlib.decompressobj()
        weights = decoder.decompress(base64.b64decode(seed['weightsZlibBase64'],validate=True),seed['vertices']*8+1)
        if len(weights) != seed['vertices']*8 or not decoder.eof or decoder.unused_data:
            raise ValueError('Invalid packed authoring weights')
        for i in range(part['vertices']): raw[i*24+16:i*24+24] = weights[i*8:i*8+8]
        part['data'] = base64.b64encode(raw).decode()
    jacket = next(p for p in data['parts'] if p['name']=='jacket')
    rows = unpack(jacket); targets, iterations = ownership(rows,data['bones']); changed = {}
    for part in data['parts']:
        if part['name'] not in ('jacket','pants'): continue
        packed = []
        for row in unpack(part):
            x,y,z = (v/10000 for v in row[:3]); new = row
            if part['name']=='jacket': new = encode_weights(row,targets[row[:3]],data['bones'])
            elif .865 < y < .935 and abs(x) > .195 and any(arm(data['bones'][j]) and w for j,w in zip(row[8:12],row[12:16])):
                # Ribbed cuffs can share the pants material but belong to the sleeve.
                new = encode_weights(row,1.,data['bones'])
            changed[part['name']] = changed.get(part['name'],0)+(new[8:]!=row[8:])
            packed.append(ROW.pack(*new))
        part['data'] = base64.b64encode(b''.join(packed)).decode()
    data['provenance'] = data.get('provenance','').replace(TAG,'')+TAG
    header = text.split('DC.HeroAsset=',1)[0]
    result = (header+'DC.HeroAsset='+json.dumps(data,separators=(',',':'))+';\n').encode()
    return result, {'iterations':iterations,'changedCorners':changed,'topology':'unchanged','rigBones':49}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--source',type=Path,default=ROOT/'src/hero-asset.js');a=p.parse_args()
    original=a.source.read_bytes();result,report=rebind(original)
    report['inputSha256']=hashlib.sha256(original).hexdigest();report['outputSha256']=hashlib.sha256(result).hexdigest()
    print(json.dumps(report,indent=2))
    if a.check:
        if result != original: raise SystemExit('Canonical garment must be regenerated')
    else: a.source.write_bytes(result)
if __name__=='__main__': main()
