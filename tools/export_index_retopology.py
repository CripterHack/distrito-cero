"""Export the fitted character at rest with its two index flexes and original PBR maps.

blender -b --python-exit-code 1 -P tools/export_index_retopology.py -- SCENE.blend OUT/character-index-retopo.glb
node tools/qa/validate_glb.cjs OUT VALIDATOR_MODULE_DIRECTORY
"""
import hashlib
import json
import sys
from pathlib import Path

import bpy


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class glTF2ExportUserExtension:
    """Let the Blender exporter serialize color buffers only for materials that use them."""

    def gather_mesh_hook(self, mesh, *_):
        for primitive in mesh.primitives:
            if primitive.material.pbr_metallic_roughness.base_color_texture is not None:
                primitive.attributes.pop("COLOR_0", None)


def export(source, output):
    manifest_path = output.with_name("source-manifest.json")
    if output.suffix.lower() != ".glb" or output.exists() or manifest_path.exists():
        raise ValueError("Expected a new .glb file and a free companion source-manifest.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.open_mainfile(filepath=str(source.resolve()))
    obj, = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    keys = obj.data.shape_keys.key_blocks
    if [key.name for key in keys] != ["Basis", "Prueba.Indice.L", "Prueba.Indice.R"]:
        raise ValueError("Expected an editable character with both index flexes")
    for key in list(keys)[1:]:
        key.value = 0
    obj.show_only_shape_key = False
    obj.active_shape_key_index = 0
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Blender 4.3 gathers a mesh-wide color attribute even in MATERIAL mode.
    # Register the documented glTF gather hook for this background export only.
    addon = bpy.context.preferences.addons.new()
    addon.module = __name__
    try:
        result = bpy.ops.export_scene.gltf(
            filepath=str(output.resolve()), export_format="GLB", use_selection=True,
            export_yup=True, export_normals=True, export_tangents=True,
            export_morph=True, export_morph_normal=True, export_materials="EXPORT",
            export_vertex_color="MATERIAL", export_all_vertex_colors=False,
            export_animations=False, export_cameras=False, export_lights=False,
        )
    finally:
        bpy.context.preferences.addons.remove(addon)
    if "FINISHED" not in result:
        raise RuntimeError("Blender GLB export did not complete")
    manifest = {"schema": 1, "file": output.name, "sha256": digest(output),
                "bytes": output.stat().st_size, "sourceBlendSha256": digest(source),
                "blender": bpy.app.version_string}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    export(*map(Path, sys.argv[sys.argv.index("--") + 1:]))
