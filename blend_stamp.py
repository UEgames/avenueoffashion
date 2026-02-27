"""
blend_stamp.py — Blender headless script: V2 "Stamp" (planar front-face UV)
Projects livernois.png flat onto the front-facing hemisphere only.

Usage:
  "C:/Program Files/Blender Foundation/Blender 3.5/blender.exe" --background --python blend_stamp.py
"""

import bpy
import bmesh
import os

PROJECT_ROOT  = r"C:\Users\jwolf\Documents\uegames\8thwallprojects\prizeballoon"
BALLOON_GLB   = os.path.join(PROJECT_ROOT, "src", "assets", "models", "balloon.glb")
LIVERNOIS_PNG = os.path.join(PROJECT_ROOT, "src", "assets", "livernois.png")
OUTPUT_GLB    = os.path.join(PROJECT_ROOT, "src", "assets", "models", "balloon-stamp.glb")

# ── 1. Clear scene ────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── 2. Import balloon.glb ─────────────────────────────────────────────────────
bpy.ops.import_scene.gltf(filepath=BALLOON_GLB)
print(f"Objects after import: {[o.name for o in bpy.data.objects]}")

# ── 3. Select the mesh ────────────────────────────────────────────────────────
obj = next((o for o in bpy.data.objects if o.type == 'MESH'), None)
if obj is None:
    raise RuntimeError("No mesh found in imported GLB")
print(f"Using mesh: {obj.name}")

bpy.context.view_layer.objects.active = obj
bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)

# Apply GLTF Y→Z correction rotation so vertex .co is in Z-up Blender space.
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ── 4. Rebuild UV layers ──────────────────────────────────────────────────────
for layer in list(obj.data.uv_layers):
    obj.data.uv_layers.remove(layer)
obj.data.uv_layers.new(name="StampUV")

# ── 5. Compute planar UV (front-face stamp) via bmesh ─────────────────────────
# After Y→Z correction: balloon long axis = Z, "front" = −Y direction in Blender
# (GLTF +Z camera-facing side maps to Blender −Y after the import correction).
# Planar projection along Y ignores Y depth; maps X→U, Z→V.
# Scale 0.5 from centre so the image covers only the front hemisphere, not the
# full silhouette width, reducing wrap-around onto the sides.

bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

uv_lay = bm.loops.layers.uv.get("StampUV") or bm.loops.layers.uv.active

x_coords = [v.co.x for v in bm.verts]
z_coords = [v.co.z for v in bm.verts]
x_min, x_max = min(x_coords), max(x_coords)
z_min, z_max = min(z_coords), max(z_coords)
x_range = x_max - x_min
z_range = z_max - z_min
print(f"X range: {x_min:.3f} → {x_max:.3f}")
print(f"Z range: {z_min:.3f} → {z_max:.3f}")

# Planar projection along -Y (Blender front = GLTF +Z = camera-facing side).
# U spans the full balloon width so the image fills the visible silhouette.
# V is aspect-correct: image (1048×619, aspect ≈1.693) maps at natural ratio,
# centred vertically — like a decal covering the front face (cf. JLL balloon ref).
IMAGE_ASPECT = 1048.0 / 619.0   # ≈ 1.693
v_height = x_range / (z_range * IMAGE_ASPECT)   # fraction of total V height used
v_offset = (1.0 - v_height) / 2.0               # centre the band vertically
print(f"Stamp band: v_height={v_height:.3f}  v_offset={v_offset:.3f}")

for face in bm.faces:
    for loop in face.loops:
        co = loop.vert.co
        u = (co.x - x_min) / x_range        # 0..1 full width
        v_raw = (co.z - z_min) / z_range    # 0..1 full height
        v = v_raw * v_height + v_offset      # aspect-correct centred band
        loop[uv_lay].uv = (u, v)

bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
print("UV computation complete (stamp/planar)")

# ── 6. Create StampMaterial ───────────────────────────────────────────────────
mat = bpy.data.materials.new(name="StampMaterial")
mat.use_nodes = True
tree = mat.node_tree
tree.nodes.clear()

tex = tree.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(LIVERNOIS_PNG)
tex.location = (-300, 0)

bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
bsdf.inputs["Roughness"].default_value = 0.7
bsdf.location = (0, 0)

out = tree.nodes.new("ShaderNodeOutputMaterial")
out.location = (300, 0)

tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

obj.data.materials.clear()
obj.data.materials.append(mat)
print("StampMaterial assigned")

# ── 7. Export balloon-stamp.glb ───────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_texcoords=True,
    export_materials='EXPORT',
    export_apply=True,
    use_selection=False,
)
print(f"\n✓  Exported: {OUTPUT_GLB}")
