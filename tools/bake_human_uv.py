#!/usr/bin/env python3
"""Blender-only authoring bake of the portable face into non-collapsed UVs.

Usage: blender -b --python-exit-code 1 --python tools/bake_human_uv.py -- INPUT_GLB NEW_OUTPUT_DIR [--cervical-color CANONICAL_HERO_JS]
Consumes an explicit-tangent GLB. Never writes runtime assets or the input file.
The output recipe is applied by the separate GLB patcher, preserving the rig.
"""
import base64
import hashlib
import json
import math
from pathlib import Path
import struct
import sys

import bpy
import numpy as np


def sha(data):
    return hashlib.sha256(data).hexdigest()


def decode(raw):
    if len(raw) < 28 or struct.unpack_from('<3I', raw) != (0x46546C67, 2, len(raw)):
        raise ValueError('Invalid GLB header')
    jl, jt = struct.unpack_from('<2I', raw, 12)
    end = 20 + jl
    if jt != 0x4E4F534A or jl % 4 or end + 8 > len(raw):
        raise ValueError('Invalid GLB JSON chunk')
    bl, bt = struct.unpack_from('<2I', raw, end)
    if bt != 0x004E4942 or end + 8 + bl != len(raw):
        raise ValueError('Invalid GLB BIN chunk')
    doc = json.loads(raw[20:end])
    if len(doc['buffers']) != 1 or doc['buffers'][0].get('uri'):
        raise ValueError('Self-contained single-buffer GLB required')
    return doc, raw[end + 8:]


def read_accessor(doc, binary, index, allow_normalized=False):
    a = doc['accessors'][index]
    types = {5121: '<u1', 5123: '<u2', 5125: '<u4', 5126: '<f4'}
    widths = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
    if a.get('sparse') or a.get('extensions') or (a.get('normalized') and not (allow_normalized and a['componentType'] == 5121)):
        raise ValueError('Unsupported bake accessor')
    dtype, width = np.dtype(types[a['componentType']]), widths[a['type']]
    view = doc['bufferViews'][a['bufferView']]
    if view['buffer'] != 0 or view.get('extensions'):
        raise ValueError('Unsupported bake buffer view')
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = view.get('byteStride', width * dtype.itemsize)
    count = a['count']
    end = start + (count - 1) * stride + width * dtype.itemsize
    if count < 1 or stride < width * dtype.itemsize or start < 0 or end > len(binary) or end > view.get('byteOffset', 0) + view['byteLength']:
        raise ValueError('Invalid bake accessor range')
    out = np.ndarray((count, width), dtype=dtype, buffer=binary, offset=start,
                     strides=(stride, dtype.itemsize)).copy()
    if not np.isfinite(out).all():
        raise ValueError('Nonfinite bake input')
    if a.get('normalized'):
        out = out.astype(np.float64) / 255
    return out


def converted(v):
    """glTF Y-up to Blender Z-up, a determinant-positive rotation."""
    return np.column_stack((v[:, 0], -v[:, 2], v[:, 1]))


def cervical_color_coverage(pixels):
    """Record the positive source bound and explicit coverage-mask policy.

    ``pixels`` are the original PNG's encoded RGBA samples loaded Non-Color,
    before filtering, tinting or sRGB decoding. Linear interpolation, positive
    pigment multipliers and the clamped convex blend cannot introduce black.
    Thus an all-zero texel in the emission bake is cleared, unbaked background.
    Nonzero fringe texels may still be partially covered, so downstream padding
    must use the separately baked white-emission mask, not this color bound.
    """
    rgb = np.asarray(pixels, dtype=np.float64).reshape(-1, 4)[:, :3]
    if not len(rgb) or not np.isfinite(rgb).all() or np.any(rgb <= 0) or np.any(rgb > 1):
        raise ValueError('Cervical coverage requires strictly positive source RGB')
    minimum = np.rint(rgb.min(axis=0) * 255).astype(np.int64)
    if np.any(minimum <= 0):
        raise ValueError('Cervical coverage requires strictly positive source RGB at PNG byte precision')
    return {'sourceBaseColorMinEncoded': minimum.tolist(),
            'colorCoveragePolicy': 'coverage-mask-full-white-is-valid-source'}


def coverage_png_pixels(pixels):
    """Encode RGB8 coverage without promoting a partial sample to full white."""
    rgba = np.asarray(pixels, dtype=np.float64).reshape(-1, 4)
    rgb = rgba[:, :3]
    if not np.isfinite(rgb).all() or not np.all(rgb == rgb[:, :1]) or np.any(rgb < 0) or np.any(rgb > 1):
        raise ValueError('Coverage bake must contain finite grayscale values in [0, 1]')
    result = np.ones(rgba.shape, dtype=np.float32)
    # Floor in float64: float32 multiplication can round nextafter(1, 0)
    # up to 255. Only a baked float value of exactly one may encode as 255.
    result[:, :3] = np.floor(rgb * 255) / 255
    return result.reshape(-1)


def canonical_surface(hero_path, source, raw, doc, binary, attrs, order, position, uv):
    """Bind the uncompressed mask positions to this exact portable corner order."""
    manifest_path = source.parent / 'source-manifest.json'
    manifest_bytes = manifest_path.read_bytes(); manifest = json.loads(manifest_bytes)
    hero_bytes = hero_path.read_bytes()
    fit_path = hero_path.parent / 'character-fit.js'; fit_bytes = fit_path.read_bytes()
    fit_sha = sha(fit_bytes)
    if manifest.get('sha256') != sha(raw) or manifest.get('sources', {}).get('src/hero-asset.js') != sha(hero_bytes):
        raise ValueError('Canonical hero / portable source provenance mismatch')
    # The explicit neutral formula below is version-bound, not a generic morph.
    if fit_sha != 'efdf174324622f53f2be64763bb47c1e6401e9ea637d72cd403dd93caa2223e7' or manifest['sources'].get('src/character-fit.js') != fit_sha:
        raise ValueError('Unsupported CharacterFit source revision')
    if manifest.get('profile') != 'neutral, neckLength=0, classic groom, detailed mesh':
        raise ValueError('Cervical mask requires the neutral portable profile')
    hero = json.loads(hero_bytes.decode().split('DC.HeroAsset=', 1)[1].strip().rstrip(';'))
    face = next(part for part in hero['parts'] if part['name'] == 'face')
    dtype = np.dtype([('p', '<i2', 3), ('n', '<i2', 3), ('uv', '<u2', 2), ('j', 'u1', 4), ('w', 'u1', 4)])
    rows = np.frombuffer(base64.b64decode(face['data'], validate=True), dtype=dtype)
    if len(rows) != len(order) or len(rows) != face['vertices'] or len(hero['bones']) != 49:
        raise ValueError('Canonical face corner / rig contract mismatch')
    rest = rows['p'].astype(np.float64) / 10000
    expected = rest.copy(); y = rest[:, 1]; t = np.clip(y - 1.447, 0, .103)
    weight = np.where(t < .008, t * t / (2 * .008 * .095),
                      np.where(t > .095, 1 - (.103 - t) ** 2 / (2 * .008 * .095), (t - .004) / .095))
    expected[:, 1] -= .045 * weight
    expected = np.floor(expected * 10000 + .5) / 10000
    expected_uv = rows['uv'].astype(np.float64) / 65535; expected_uv[:, 1] = 1 - expected_uv[:, 1]
    joints = read_accessor(doc, binary, attrs['JOINTS_0'])[order]
    weights = read_accessor(doc, binary, attrs['WEIGHTS_0'], allow_normalized=True)[order]
    normals = read_accessor(doc, binary, attrs['NORMAL'])[order]
    if not np.allclose(position[order], expected, rtol=0, atol=1.3e-7) or not np.allclose(uv[order], expected_uv, rtol=0, atol=6e-8):
        raise ValueError('Canonical face position/UV corner order mismatch')
    if not np.allclose(weights, rows['w'] / 255, rtol=0, atol=6e-8) or np.any(joints[weights != 0] != rows['j'][weights != 0]):
        raise ValueError('Canonical face skinning corner order mismatch')
    slope = np.where((y <= 1.447) | (y >= 1.550), 0,
                     np.where(t < .008, t / (.008 * .095), np.where(t > .095, (.103 - t) / (.008 * .095), 1 / .095)))
    expected_normal = rows['n'].astype(np.float64); expected_normal[:, 1] /= np.maximum(.1, 1 - .045 * slope)
    expected_normal /= np.linalg.norm(expected_normal, axis=1)[:, None]
    expected_normal = np.floor(expected_normal * 32767 + .5)
    expected_normal /= np.linalg.norm(expected_normal, axis=1)[:, None]
    if not np.allclose(normals, expected_normal, rtol=0, atol=1e-4):
        raise ValueError('Canonical face fitted normal corner order mismatch')
    provenance = {'heroAssetSha256': sha(hero_bytes), 'faceCornerCount': len(rows),
                  'cornerOrder': 'native-face-triangle-corners', 'sourceManifestSha256': sha(manifest_bytes),
                  'characterFitSha256': fit_sha, 'neutralNeckDropMetres': .045,
                  'colorPolicy': 'Linear blend of original face texture and filtered cervical pigment using canonical rest-position mask',
                  'pigment': {'sourceMip': 3, 'uClamp': [.23, .77], 'nativeV': .095, 'encodedMultiplier': [.975, .982, .990]},
                  'mask': {'faceHeight': [1.537, 1.605], 'jawFront': [.035, .092], 'jawHeight': [1.530, 1.549]}}
    return rest, provenance, [(hero_path, hero_bytes), (fit_path, fit_bytes), (manifest_path, manifest_bytes)]


def main():
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) not in (2, 4) or (len(args) == 4 and args[2] != '--cervical-color'):
        raise ValueError(__doc__)
    source, out = Path(args[0]).resolve(), Path(args[1]).resolve()
    root = Path(__file__).resolve().parents[1]
    if out.is_relative_to(root) and not out.is_relative_to(root / 'artifacts'):
        raise ValueError('Bake outputs inside the repository must use artifacts/')
    raw = source.read_bytes()
    doc, binary = decode(raw)
    candidates = [(mi, pi, p) for mi, mesh in enumerate(doc['meshes'])
                  for pi, p in enumerate(mesh['primitives'])
                  if doc['materials'][p['material']].get('normalTexture')]
    if len(candidates) != 1:
        raise ValueError('Expected exactly one normal-mapped face primitive')
    mi, pi, primitive = candidates[0]
    attrs = primitive['attributes']
    if primitive.get('mode', 4) != 4 or primitive.get('targets') or primitive.get('extensions') or 'TANGENT' not in attrs:
        raise ValueError('An explicit-tangent, non-morph triangle primitive is required')
    p, n, t, uv = [read_accessor(doc, binary, attrs[k]) for k in ['POSITION', 'NORMAL', 'TANGENT', 'TEXCOORD_0']]
    if [a.shape[1] for a in [p, n, t, uv]] != [3, 3, 4, 2] or len({len(a) for a in [p, n, t, uv]}) != 1:
        raise ValueError('Mismatched face attributes')
    order = read_accessor(doc, binary, primitive['indices']).reshape(-1).astype(np.int64)
    if len(order) % 3 or order.min() < 0 or order.max() >= len(p):
        raise ValueError('Invalid face indices')
    material = doc['materials'][primitive['material']]
    if material.get('extensions'):
        raise ValueError('Unsupported source material extension')
    texinfos = {'baseColor': material['pbrMetallicRoughness']['baseColorTexture'],
                'orm': material['pbrMetallicRoughness']['metallicRoughnessTexture'],
                'normal': material['normalTexture']}
    if any(info.get('texCoord', 0) != 0 or info.get('extensions') for info in texinfos.values()):
        raise ValueError('Unsupported source texture coordinates')
    rest = provenance = None; dependencies = []
    if len(args) == 4:
        rest, provenance, dependencies = canonical_surface(Path(args[3]).resolve(), source, raw, doc, binary, attrs, order, p, uv)
    out.mkdir(parents=True, exist_ok=False)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mesh = bpy.data.meshes.new('Face original corner contract')
    mesh.from_pydata(converted(p).tolist(), [], order.reshape(-1, 3).tolist())
    mesh.update()
    if len(mesh.loops) != len(order):
        raise ValueError('Blender changed face corner count')
    for poly in mesh.polygons:
        poly.use_smooth = True
    mesh.normals_split_custom_set(converted(n)[order].tolist())
    obj = bpy.data.objects.new('Face UV authoring', mesh)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    old = mesh.uv_layers.new(name='OldUV')
    old_values = uv[order].copy(); old_values[:, 1] = 1 - old_values[:, 1]
    old.data.foreach_set('uv', old_values.reshape(-1))
    new = mesh.uv_layers.new(name='RebakedUV')
    mesh.uv_layers.active = new
    new.active_render = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=.018,
                             area_weight=.5, correct_aspect=True, scale_to_bounds=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    values = np.empty(len(order) * 2, dtype=np.float32)
    mesh.uv_layers['RebakedUV'].data.foreach_get('uv', values)
    values = values.reshape(-1, 2); values[:, 1] = 1 - values[:, 1]
    tri = values.reshape(-1, 3, 2)
    det = (tri[:, 1, 0] - tri[:, 0, 0]) * (tri[:, 2, 1] - tri[:, 0, 1]) - (tri[:, 2, 0] - tri[:, 0, 0]) * (tri[:, 1, 1] - tri[:, 0, 1])
    if not np.isfinite(values).all() or np.any(det == 0):
        raise ValueError('Smart Project left collapsed UVs')
    for name, data, kind in [('SourceNormal', converted(n)[order], 'FLOAT_VECTOR'),
                             ('SourceTangent', converted(t[:, :3])[order], 'FLOAT_VECTOR'),
                             ('SourceW', t[order, 3], 'FLOAT')]:
        attr = mesh.attributes.new(name, kind, 'CORNER')
        attr.data.foreach_set('vector' if kind == 'FLOAT_VECTOR' else 'value', np.asarray(data).reshape(-1))
    if rest is not None:
        mesh.attributes.new('CanonicalSurface', 'FLOAT_VECTOR', 'CORNER').data.foreach_set('vector', rest.reshape(-1))
    mat = bpy.data.materials.new('Explicit portable tangent baseline'); mat.use_nodes = True
    obj.data.materials.append(mat)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    def node(kind): return nodes.new(kind)
    def mathnode(op, a, b=None):
        x = node('ShaderNodeVectorMath'); x.operation = op
        links.new(a, x.inputs[0])
        if b is not None: links.new(b, x.inputs[1])
        return x.outputs[0]
    def attr(name):
        x = node('ShaderNodeAttribute'); x.attribute_name = name
        return x
    N = mathnode('NORMALIZE', attr('SourceNormal').outputs['Vector'])
    T = mathnode('NORMALIZE', attr('SourceTangent').outputs['Vector'])
    B = mathnode('CROSS_PRODUCT', N, T)
    w = node('ShaderNodeCombineXYZ')
    for socket in w.inputs: links.new(attr('SourceW').outputs['Fac'], socket)
    B = mathnode('MULTIPLY', B, w.outputs[0])
    olduv = node('ShaderNodeUVMap'); olduv.uv_map = 'OldUV'
    images = {}
    for role, info in texinfos.items():
        texture = doc['textures'][info['index']]
        sampler = doc['samplers'][texture['sampler']]
        if sampler.get('wrapS', 10497) != 10497 or sampler.get('wrapT', 10497) != 33071 or sampler.get('magFilter', 9729) != 9729:
            raise ValueError('Bake supports source linear sampling with repeat U / clamp V only')
        imageinfo = doc['images'][texture['source']]
        if 'bufferView' not in imageinfo or imageinfo.get('mimeType') != 'image/png':
            raise ValueError('Expected embedded PNG source maps')
        v = doc['bufferViews'][imageinfo['bufferView']]
        imagefile = out / ('source-' + role + '.png')
        imagefile.write_bytes(binary[v.get('byteOffset', 0):v.get('byteOffset', 0) + v['byteLength']])
        image = bpy.data.images.load(str(imagefile)); image.colorspace_settings.name = 'sRGB' if role == 'baseColor' else 'Non-Color'
        image.pack()
        tex = node('ShaderNodeTexImage'); tex.image = image; tex.extension = 'REPEAT'
        # Blender has one wrap mode for both axes. Repeat U but clamp V to the
        # texel-centre interval so the repeat sampler cannot blend opposite rows.
        coord = node('ShaderNodeSeparateXYZ'); links.new(olduv.outputs['UV'], coord.inputs[0])
        lo = node('ShaderNodeMath'); lo.operation = 'MAXIMUM'; links.new(coord.outputs['Y'], lo.inputs[0]); lo.inputs[1].default_value = .5 / image.size[1]
        hi = node('ShaderNodeMath'); hi.operation = 'MINIMUM'; links.new(lo.outputs[0], hi.inputs[0]); hi.inputs[1].default_value = 1 - .5 / image.size[1]
        joined = node('ShaderNodeCombineXYZ'); links.new(coord.outputs['X'], joined.inputs['X']); links.new(hi.outputs[0], joined.inputs['Y'])
        links.new(joined.outputs[0], tex.inputs['Vector']); images[role] = tex
    sampled = node('ShaderNodeVectorMath'); sampled.operation = 'MULTIPLY_ADD'
    links.new(images['normal'].outputs['Color'], sampled.inputs[0]); sampled.inputs[1].default_value = (2, 2, 2); sampled.inputs[2].default_value = (-1, -1, -1)
    scaled = node('ShaderNodeVectorMath'); scaled.operation = 'MULTIPLY'
    links.new(sampled.outputs[0], scaled.inputs[0]); strength = texinfos['normal'].get('scale', 1)
    scaled.inputs[1].default_value = (strength, strength, 1)
    split = node('ShaderNodeSeparateXYZ'); links.new(scaled.outputs[0], split.inputs[0])
    terms = []
    for vec, channel in zip([T, B, N], ['X', 'Y', 'Z']):
        scale = node('ShaderNodeVectorMath'); scale.operation = 'SCALE'
        links.new(vec, scale.inputs[0]); links.new(split.outputs[channel], scale.inputs[3]); terms.append(scale.outputs[0])
    world = node('ShaderNodeVectorTransform'); world.vector_type = 'NORMAL'; world.convert_from = 'OBJECT'; world.convert_to = 'WORLD'
    links.new(mathnode('NORMALIZE', mathnode('ADD', mathnode('ADD', terms[0], terms[1]), terms[2])), world.inputs[0])
    bsdf = node('ShaderNodeBsdfPrincipled'); links.new(world.outputs[0], bsdf.inputs['Normal'])
    links.new(images['baseColor'].outputs['Color'], bsdf.inputs['Base Color'])
    baked_color = images['baseColor'].outputs['Color']
    if rest is not None:
        # Native mip generation averages stored (encoded) texels before decoding.
        # Filter by eight in each dimension, then decode the adjusted pigment.
        source_color = bpy.data.images.load(str(out / 'source-baseColor.png'), check_existing=False)
        source_color.colorspace_settings.name = 'Non-Color'
        width, height = source_color.size
        if width % 8 or height % 8:
            raise ValueError('Cervical pigment requires dimensions divisible by eight')
        pixels = np.empty(width * height * 4, dtype=np.float32); source_color.pixels.foreach_get(pixels)
        provenance.update(cervical_color_coverage(pixels))
        encoded = pixels.reshape(height // 8, 8, width // 8, 8, 4).mean(axis=(1, 3))
        encoded[:, :, :3] *= np.array([.975, .982, .990])
        linear = encoded.copy(); rgb = encoded[:, :, :3]
        linear[:, :, :3] = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
        pigment = bpy.data.images.new('Filtered linear cervical pigment', width // 8, height // 8, alpha=True, float_buffer=True)
        pigment.colorspace_settings.name = 'Non-Color'; pigment.pixels.foreach_set(linear.reshape(-1)); pigment.pack()
        texture = node('ShaderNodeTexImage'); texture.image = pigment; texture.extension = 'EXTEND'
        coord = node('ShaderNodeSeparateXYZ'); links.new(olduv.outputs['UV'], coord.inputs[0])
        low = node('ShaderNodeMath'); low.operation = 'MAXIMUM'; low.inputs[1].default_value = .23; links.new(coord.outputs['X'], low.inputs[0])
        high = node('ShaderNodeMath'); high.operation = 'MINIMUM'; high.inputs[1].default_value = .77; links.new(low.outputs[0], high.inputs[0])
        joined = node('ShaderNodeCombineXYZ'); links.new(high.outputs[0], joined.inputs['X']); joined.inputs['Y'].default_value = .095
        links.new(joined.outputs[0], texture.inputs['Vector'])
        surface = node('ShaderNodeSeparateXYZ'); links.new(attr('CanonicalSurface').outputs['Vector'], surface.inputs[0])
        def smooth(socket, low_value, high_value):
            mapped = node('ShaderNodeMapRange'); mapped.interpolation_type = 'SMOOTHSTEP'; mapped.clamp = True
            links.new(socket, mapped.inputs['Value']); mapped.inputs['From Min'].default_value = low_value; mapped.inputs['From Max'].default_value = high_value
            return mapped.outputs[0]
        front = smooth(surface.outputs['Z'], .035, .092); height_mask = smooth(surface.outputs['Y'], 1.530, 1.549)
        jaw = node('ShaderNodeMath'); jaw.operation = 'MULTIPLY'; links.new(front, jaw.inputs[0]); links.new(height_mask, jaw.inputs[1])
        blend = node('ShaderNodeMath'); blend.operation = 'MAXIMUM'; links.new(jaw.outputs[0], blend.inputs[0]); links.new(smooth(surface.outputs['Y'], 1.537, 1.605), blend.inputs[1])
        mixed = node('ShaderNodeMixRGB'); mixed.blend_type = 'MIX'; links.new(blend.outputs[0], mixed.inputs[0]); links.new(texture.outputs['Color'], mixed.inputs[1]); links.new(baked_color, mixed.inputs[2])
        baked_color = mixed.outputs[0]
    output = node('ShaderNodeOutputMaterial'); links.new(bsdf.outputs[0], output.inputs['Surface'])
    emission = node('ShaderNodeEmission')
    target = node('ShaderNodeTexImage'); target.label = 'Bake destination only'
    scene = bpy.context.scene; scene.render.engine = 'CYCLES'; scene.cycles.device = 'CPU'; scene.cycles.samples = 16; scene.cycles.use_denoising = False
    scene.render.bake.margin = 16; scene.render.bake.use_clear = True; scene.render.bake.use_selected_to_active = False
    scene.render.bake.normal_space = 'TANGENT'
    filenames = {'baseColor': 'base-color.png', 'orm': 'orm.png', 'normal': 'normal.png'}
    if provenance is not None:
        filenames['coverage'] = 'coverage.png'
    for role in filenames:
        image = bpy.data.images.new('Rebaked ' + role, 2048, 2048, alpha=False, float_buffer=True)
        image.colorspace_settings.name = 'sRGB' if role == 'baseColor' else 'Non-Color'
        target.image = image; nodes.active = target
        for x in nodes: x.select = x == target
        if role == 'normal':
            links.new(bsdf.outputs[0], output.inputs['Surface'])
            bpy.ops.object.bake(type='NORMAL')
            pixels = np.empty(2048 * 2048 * 4, dtype=np.float32); image.pixels.foreach_get(pixels)
            pixels.reshape(-1, 4)[:, 1] = 1 - pixels.reshape(-1, 4)[:, 1]
            image.pixels.foreach_set(pixels)
        else:
            if role == 'coverage':
                # Use the identical Cycles bake footprint, including partial
                # edge coverage and margin. Only encoded RGB255 is a complete
                # sample; padding can replace every other mask value without
                # classifying skin colors or erasing legitimate dark detail.
                for link in list(emission.inputs['Color'].links):
                    links.remove(link)
                emission.inputs['Color'].default_value = (1, 1, 1, 1)
            else:
                links.new(baked_color if role == 'baseColor' else images[role].outputs['Color'], emission.inputs['Color'])
            links.new(emission.outputs[0], output.inputs['Surface'])
            bpy.ops.object.bake(type='EMIT')
            if role == 'coverage':
                pixels = np.empty(2048 * 2048 * 4, dtype=np.float32); image.pixels.foreach_get(pixels)
                byte_image = bpy.data.images.new('Encoded coverage RGB8', 2048, 2048, alpha=False, float_buffer=False)
                byte_image.colorspace_settings.name = 'Non-Color'
                byte_image.pixels.foreach_set(coverage_png_pixels(pixels))
                target.image = byte_image; bpy.data.images.remove(image); image = byte_image
        image.filepath_raw = str(out / filenames[role]); image.file_format = 'PNG'; image.save()
    links.new(bsdf.outputs[0], output.inputs['Surface'])
    if source.read_bytes() != raw:
        raise ValueError('Source changed during bake')
    if any(path.read_bytes() != data for path, data in dependencies):
        raise ValueError('Canonical source changed during bake')
    recipe = {'schema': 1, 'sourceSha256': sha(raw), 'mesh': mi, 'primitive': pi,
              'cornerUvs': values.tolist(), 'images': filenames, 'normalScale': 1,
              'toolchain': {'blender': bpy.app.version_string, 'scriptSha256': sha(Path(__file__).read_bytes()),
                            'engine': 'Cycles CPU', 'samples': 16, 'resolution': 2048, 'marginPixels': 16,
                            'uvAlgorithm': 'Smart Project 66 degrees, area weight .5, island margin .018',
                            'sourceBasis': 'Explicit GLB tangent, W and normal corner attributes; source normal scale baked once',
                            'sourceSampler': 'Linear repeat U / clamp V; V clamped per-image to half-texel interval before Blender repeat lookup',
                            'normalConvention': 'Blender target UV V inverted to glTF; baked normal green inverted',
                            'sourceFallback': 'Preserves declared portable-tangent fallback; does not recover an undefined original UV basis'}}
    if provenance is not None:
        recipe['toolchain']['coverageEncoding'] = 'Constant-white emission; Non-Color RGB8 floor(255 * coverage), exact 255 only for full coverage; same UV, samples, clear and margin'
        recipe.update(mode='cervical-color', nativeSource=provenance)
    (out / 'recipe.json').write_text(json.dumps(recipe, separators=(',', ':')) + '\n')
    # The .blend is delivered with its PNGs; do not retain workspace paths.
    for image in bpy.data.images:
        if image.filepath:
            image.filepath = bpy.path.relpath(image.filepath, start=str(out))
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'authoring.blend'))
    print(json.dumps({'recipe': str(out / 'recipe.json'), 'triangles': len(order) // 3,
                      'degenerateUvTriangles': int((det == 0).sum()), 'sourceSha256': sha(raw)}))


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print('UV BAKE FAILED:', str(exc), file=sys.stderr)
        raise
