"""Bake reviewed Higgsfield GLBs into metre-scale authoring assets and native WebGL LODs.

blender -b --python-exit-code 1 --python tools/prepare_mercado_assets.py -- INPUT OUTPUT
INPUT holds taller.glb and marquesina.glb. OUTPUT receives GLBs, metrics and mercado-models.js.
"""
import base64
import hashlib
import io
import json
import math
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector
from PIL import Image

CONFIG = {'taller': (6.50, (.37, .105)), 'marquesina': (2.50, (.55, .16))}
TILE = 640
GUTTER = 8
ROOT = Path(__file__).resolve().parents[1]


def encoded(raw):
    return base64.b64encode(raw).decode('ascii')


def images(raw):
    length = struct.unpack_from('<I', raw, 12)[0]
    doc = json.loads(raw[20:20+length])
    start = 28 + length
    mat = doc['materials'][0]
    pbr = mat['pbrMetallicRoughness']
    names = [mat['normalTexture'], pbr['metallicRoughnessTexture'], pbr['baseColorTexture']]
    for tex in names:
        image = doc['images'][doc['textures'][tex['index']]['source']]
        view = doc['bufferViews'][image['bufferView']]
        i = start + view.get('byteOffset', 0)
        yield Image.open(io.BytesIO(raw[i:i+view['byteLength']])).convert('RGB')


def add_tile(atlas, image, column, row):
    # Repeat edge texels. Mip levels up to three remain within the gutter.
    side = TILE-2*GUTTER
    tile = image.resize((side, side), Image.Resampling.LANCZOS)
    x, y = column*TILE+GUTTER, row*TILE+GUTTER
    atlas.paste(tile, (x, y))
    for dy, src in [(-GUTTER, 0), (side, side-1)]:
        atlas.paste(tile.crop((0, src, side, src+1)).resize((side,GUTTER)),(x,y+dy))
    for dx, src in [(-GUTTER, x), (side, x+side-1)]:
        atlas.paste(atlas.crop((src,y-GUTTER,src+1,y+side+GUTTER)).resize((GUTTER,TILE)),(x+dx,y-GUTTER))


def bake_lod(obj, ratio):
    dec = obj.modifiers.new('Runtime LOD', 'DECIMATE')
    dec.ratio = ratio
    eval_obj = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = eval_obj.to_mesh()
    mesh.calc_loop_triangles()
    coords = mesh.uv_layers.active.data
    matrix = eval_obj.matrix_world
    normal_matrix = matrix.to_3x3().inverted().transposed()
    lookup, points, indices = {}, bytearray(), bytearray()
    for triangle in mesh.loop_triangles:
        for i in triangle.loops:
            p = matrix @ mesh.vertices[mesh.loops[i].vertex_index].co
            n = (normal_matrix @ mesh.corner_normals[i].vector).normalized()
            u,v = coords[i].uv
            item = struct.pack('<3h3bx2H', *(round(1000*a) for a in (p.x,p.z,-p.y)),
                               *(round(127*a) for a in (n.x,n.z,-n.y)),
                               *(round(65535*max(0,min(1,a))) for a in (u,v)))
            if item not in lookup:
                lookup[item] = len(lookup)
                points.extend(item)
            indices.extend(struct.pack('<H',lookup[item]))
    eval_obj.to_mesh_clear()
    obj.modifiers.remove(dec)
    return {'triangles':len(indices)//6, 'points':encoded(points), 'indices':encoded(indices)}


def prepare(src, dest):
    manifest = json.loads((ROOT/'assets/mercado-20261126/generacion.json').read_text())
    hashes = {a['key']:a['sha256'] for a in manifest['assets']}
    dest.mkdir(parents=True, exist_ok=True)
    data, metrics = {}, {}
    atlas = Image.new('RGB',(TILE*2,TILE*3))
    for column,(key,(height,ratios)) in enumerate(CONFIG.items()):
        path = src/(key+'.glb')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=hashes[key]:
            raise ValueError('Unexpected source file: '+key)
        maps = list(images(raw))
        for row,img in enumerate(maps):
            add_tile(atlas,img,column,row)
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.import_scene.gltf(filepath=str(path.resolve()))
        obj, = [o for o in bpy.context.scene.objects if o.type=='MESH']
        points = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        low, high = [Vector([f(p[i] for p in points) for i in range(3)]) for f in (min,max)]
        scale = height/(high.z-low.z)
        center = Vector(((low.x+high.x)/2,(low.y+high.y)/2,low.z))
        # Both original +X facades face the camera in the reviewed Xp image.
        # Blender -Y becomes glTF/game +Z. Bake the matrix for a floor-level pivot.
        matrix = Matrix.Rotation(-math.pi/2,4,'Z') @ Matrix.Scale(scale,4) @ Matrix.Translation(-center) @ obj.matrix_world
        obj.parent = None
        obj.matrix_world = Matrix.Identity(4)
        obj.data.transform(matrix)
        obj.name = {'taller':'Taller del Mercado','marquesina':'Marquesina del Mercado'}[key]
        bpy.context.view_layer.update()
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        bpy.ops.export_scene.gltf(filepath=str((dest/(key+'.glb')).resolve()),export_format='GLB',use_selection=True,
                                  export_animations=False,export_tangents=True,export_image_format='AUTO')
        dims = [round(a*scale,4) for a in (high.y-low.y,high.z-low.z,high.x-low.x)]
        levels = [bake_lod(obj,ratio) for ratio in ratios]
        data[key] = {'size':dims,'levels':levels}
        metrics[key] = {'sizeXYZ':dims,'sourceTriangles':len(obj.data.polygons),'mapSizes':[im.size for im in maps],
                        'nativeTriangles':[l['triangles'] for l in levels],
                        'normalizedSha256':hashlib.sha256((dest/(key+'.glb')).read_bytes()).hexdigest()}
    blob = io.BytesIO()
    atlas.save(blob,'WEBP',quality=94,method=6)
    data['atlas'] = 'data:image/webp;base64,' + encoded(blob.getvalue())
    (dest/'mercado-models.js').write_text('/* Generated by tools/prepare_mercado_assets.py */\nDC.MercadoModels='+json.dumps(data,separators=(',',':'))+';\n')
    (dest/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')


prepare(*(Path(p) for p in sys.argv[sys.argv.index('--')+1:]))
