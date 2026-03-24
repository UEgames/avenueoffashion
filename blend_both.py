"""
blend_both.py — Blender headless script: livernois.png on front AND back faces.
Keeps balloon's original 3 solid-color materials; assigns the label panel to
both the front-facing and back-facing midsection hemispheres.
Back panel U is mirrored so the image reads correctly from both directions.

Usage:
  "C:/Program Files/Blender Foundation/Blender 3.5/blender.exe" --background --python blend_both.py
"""

import bpy
import bmesh
import os

PROJECT_ROOT  = r"C:\Users\jwolf\Documents\uegames\8thwallprojects\prizeballoon"
BALLOON_GLB   = os.path.join(PROJECT_ROOT, "src", "assets", "references", "balloon.glb")
LIVERNOIS_PNG = os.path.join(PROJECT_ROOT, "src", "assets", "leo.png")
OUTPUT_GLB    = os.path.join(PROJECT_ROOT, "src", "assets", "models", "balloon-both.glb")

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

# ── 4. Compute full bounding box ──────────────────────────────────────────────
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

z_coords = [v.co.z for v in bm.verts]
z_min = min(z_coords)
z_max = max(z_coords)
z_range = z_max - z_min
print(f"Z range: {z_min:.3f} → {z_max:.3f}  (range {z_range:.3f})")

# ── 5. Identify front and back panel faces ────────────────────────────────────
# Front panel: normal.y < -0.3  (Blender −Y = GLTF +Z = camera-facing)
# Back panel:  normal.y >  0.3  (Blender +Y = GLTF −Z = away from camera)
# Height band: 28%–72% of total Z range (midsection)
z_panel_min = z_min + 0.28 * z_range
z_panel_max = z_min + 0.72 * z_range
print(f"Panel Z band: {z_panel_min:.3f} → {z_panel_max:.3f}")

front_faces = []
back_faces  = []
for face in bm.faces:
    n  = face.normal
    cz = face.calc_center_median().z
    if z_panel_min <= cz <= z_panel_max:
        if n.y < -0.3:
            front_faces.append(face)
        elif n.y > 0.3:
            back_faces.append(face)

print(f"Front panel faces: {len(front_faces)}")
print(f"Back  panel faces: {len(back_faces)}")
if not front_faces:
    raise RuntimeError("No front panel faces found — check normal threshold or Z band")

# ── 6. Compute panel bounding box from front-face vertices ───────────────────
px_coords = [v.co.x for face in front_faces for v in face.verts]
pz_coords = [v.co.z for face in front_faces for v in face.verts]
px_min, px_max = min(px_coords), max(px_coords)
pz_min, pz_max = min(pz_coords), max(pz_coords)
px_range    = px_max - px_min
pz_range_val = pz_max - pz_min
print(f"Panel X: {px_min:.3f} → {px_max:.3f}")
print(f"Panel Z: {pz_min:.3f} → {pz_max:.3f}")

# ── 7. Ensure UV layer exists ─────────────────────────────────────────────────
uv_lay = bm.loops.layers.uv.active
if uv_lay is None:
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.uv_layers.new(name="BothUV")
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    uv_lay = bm.loops.layers.uv.active
    # Re-identify faces after bmesh rebuild
    front_faces, back_faces = [], []
    for face in bm.faces:
        n  = face.normal
        cz = face.calc_center_median().z
        if z_panel_min <= cz <= z_panel_max:
            if n.y < -0.3:
                front_faces.append(face)
            elif n.y > 0.3:
                back_faces.append(face)

# ── 8. Assign UVs ─────────────────────────────────────────────────────────────
# Front: u increases left→right as viewed from front (normal orientation)
# Back:  u is mirrored (1 - u) so the image reads correctly from behind
for face in front_faces:
    for loop in face.loops:
        co = loop.vert.co
        u = (co.x - px_min) / px_range
        v = (co.z - pz_min) / pz_range_val
        loop[uv_lay].uv = (u, v)

for face in back_faces:
    for loop in face.loops:
        co = loop.vert.co
        u = 1.0 - (co.x - px_min) / px_range   # mirrored for back
        v = (co.z - pz_min) / pz_range_val
        loop[uv_lay].uv = (u, v)

bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
print("UV remapped for front + back panel faces")

# ── 9. Create label material ──────────────────────────────────────────────────
mat = bpy.data.materials.new(name="LabelMaterial")
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

obj.data.materials.append(mat)
panel_mat_index = len(obj.data.materials) - 1
print(f"LabelMaterial added at slot index {panel_mat_index}")

# ── 10. Assign material to panel faces ────────────────────────────────────────
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.faces.ensure_lookup_table()

for face in bm.faces:
    n  = face.normal
    cz = face.calc_center_median().z
    if z_panel_min <= cz <= z_panel_max:
        if n.y < -0.3 or n.y > 0.3:
            face.material_index = panel_mat_index

bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
print(f"Front + back faces assigned to material slot {panel_mat_index}")

# ── 11. Export balloon-both.glb ───────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_texcoords=True,
    export_materials='EXPORT',
    export_apply=True,
    use_selection=False,
)
print(f"\n✓  Exported: {OUTPUT_GLB}")
