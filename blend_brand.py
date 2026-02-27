"""
blend_brand.py — Blender headless script
- Imports balloon.glb
- UV unwraps all meshes (sphere project on largest, smart project on rest)
- Applies livernois.png as the diffuse texture on all meshes
- Exports branded balloon back to balloon.glb (texture embedded)
"""

import bpy
import os

PROJECT_DIR = r'C:\Users\jwolf\Documents\uegames\8thwallprojects\prizeballoon'
GLB_IN      = os.path.join(PROJECT_DIR, 'src', 'assets', 'models', 'balloon.glb')
TEXTURE     = os.path.join(PROJECT_DIR, 'src', 'assets', 'livernois.png')
GLB_OUT     = os.path.join(PROJECT_DIR, 'src', 'assets', 'models', 'balloon.glb')

# ── 1. Clean slate ────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── 2. Import GLB ─────────────────────────────────────────────────────────────
bpy.ops.import_scene.gltf(filepath=GLB_IN)

meshes = [o for o in bpy.data.objects if o.type == 'MESH']
if not meshes:
    raise RuntimeError("No mesh objects found in GLB")

print(f"Found {len(meshes)} mesh(es):")
for m in meshes:
    print(f"  {m.name}  verts={len(m.data.vertices)}")

# Largest mesh by vertex count is assumed to be the balloon envelope
largest = max(meshes, key=lambda o: len(o.data.vertices))
print(f"Treating '{largest.name}' as the balloon envelope")

# ── 3. Load brand texture ─────────────────────────────────────────────────────
img = bpy.data.images.load(TEXTURE)
img.colorspace_settings.name = 'sRGB'

# ── 4. Build a single Principled material with the brand image ────────────────
def make_material(name='BrandBalloon'):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out  = nodes.new('ShaderNodeOutputMaterial'); out.location  = (400, 0)
    bsdf = nodes.new('ShaderNodeBsdfPrincipled'); bsdf.location = (0, 0)
    tex  = nodes.new('ShaderNodeTexImage');       tex.location  = (-400, 0)
    tex.image = img

    links.new(tex.outputs['Color'],  bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'],  out.inputs['Surface'])

    # Slightly reduce metallic/specular so the brand reads clearly
    bsdf.inputs['Metallic'].default_value   = 0.0
    bsdf.inputs['Roughness'].default_value  = 0.8

    return mat

brand_mat = make_material()

# ── 5. UV unwrap + assign material ───────────────────────────────────────────
def uv_unwrap(obj, method='smart'):
    """Enter edit mode, unwrap, return to object mode."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Ensure there is a UV map
    if not obj.data.uv_layers:
        bpy.ops.mesh.uv_texture_add()

    if method == 'sphere':
        # Spherical projection — ideal for the round balloon envelope
        bpy.ops.uv.sphere_project(
            direction='ALIGN_TO_OBJECT',
            align='POLAR_ZX',
            correct_aspect=True,
            clip_to_bounds=False,
            scale_to_bounds=True,
        )
    else:
        # Smart UV Project — good for irregular shapes (basket, ropes, etc.)
        bpy.ops.uv.smart_project(
            angle_limit=1.15,
            island_margin=0.02,
            area_weight=0.0,
            correct_aspect=True,
            scale_to_bounds=False,
        )

    bpy.ops.object.mode_set(mode='OBJECT')

for obj in meshes:
    method = 'sphere' if obj is largest else 'smart'
    print(f"UV unwrapping '{obj.name}' with method='{method}'")
    uv_unwrap(obj, method)

    # Replace all existing materials with the brand material
    obj.data.materials.clear()
    obj.data.materials.append(brand_mat)

# ── 6. Export branded GLB (texture embedded) ──────────────────────────────────
print(f"Exporting to {GLB_OUT} …")
bpy.ops.export_scene.gltf(
    filepath=GLB_OUT,
    export_format='GLB',
    export_image_format='AUTO',  # embed texture in the GLB
    export_materials='EXPORT',
    use_selection=False,
    export_yup=True,
)

print("Done — branded balloon exported successfully.")
