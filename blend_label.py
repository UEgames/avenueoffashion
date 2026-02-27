"""
blend_label.py — Blender headless script: V1 "Label" (panel pasted on front face)
Keeps balloon's original 3 solid-color materials; adds livernois.png as a flat
rectangular panel on the front-facing midsection (like a Subway banner).

Usage:
  "C:/Program Files/Blender Foundation/Blender 3.5/blender.exe" --background --python blend_label.py
"""

import bpy
import bmesh
import os

PROJECT_ROOT  = r"C:\Users\jwolf\Documents\uegames\8thwallprojects\prizeballoon"
BALLOON_GLB   = os.path.join(PROJECT_ROOT, "src", "assets", "references", "balloon.glb")
LIVERNOIS_PNG = os.path.join(PROJECT_ROOT, "src", "assets", "livernois.png")
OUTPUT_GLB    = os.path.join(PROJECT_ROOT, "src", "assets", "models", "balloon-label.glb")

# ── 1. Clear scene ────────────────────────────────────────────────────────────
bpy.ops.wm.read_factory_settings(use_empty=True)

# ── 2. Import references/balloon.glb (3 original solid-color materials) ───────
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

# ── 4. Apply transforms (bakes GLTF Y→Z correction; long axis → Blender Z) ───
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

# ── 5. Compute full bounding box ──────────────────────────────────────────────
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.verts.ensure_lookup_table()
bm.faces.ensure_lookup_table()

z_coords = [v.co.z for v in bm.verts]
z_min = min(z_coords)
z_max = max(z_coords)
z_range = z_max - z_min
print(f"Z range: {z_min:.3f} → {z_max:.3f}  (range {z_range:.3f})")

# ── 6. Identify panel faces ───────────────────────────────────────────────────
# Panel = front-hemisphere midsection:
#   a. normal.y < -0.3  (faces ≥30% toward Blender −Y = GLTF +Z = camera-facing)
#   b. face centre Z within [28%, 72%] of total height
z_panel_min = z_min + 0.28 * z_range
z_panel_max = z_min + 0.72 * z_range
print(f"Panel Z band: {z_panel_min:.3f} → {z_panel_max:.3f}")

panel_faces = []
for face in bm.faces:
    n = face.normal
    cz = face.calc_center_median().z
    if n.y < -0.3 and z_panel_min <= cz <= z_panel_max:
        panel_faces.append(face)

print(f"panel_faces found: {len(panel_faces)}")
if not panel_faces:
    raise RuntimeError("No panel faces found — check normal threshold or Z band")

# ── 7. Compute panel bounding box from panel-face vertices ────────────────────
px_coords = []
pz_coords = []
for face in panel_faces:
    for v in face.verts:
        px_coords.append(v.co.x)
        pz_coords.append(v.co.z)

px_min, px_max = min(px_coords), max(px_coords)
pz_min, pz_max = min(pz_coords), max(pz_coords)
print(f"Panel X: {px_min:.3f} → {px_max:.3f}")
print(f"Panel Z: {pz_min:.3f} → {pz_max:.3f}")

# ── 8. Remap UV for panel faces (planar from −Y) ──────────────────────────────
# Ensure a UV layer exists (keep existing ones for non-panel face compatibility)
uv_lay = bm.loops.layers.uv.active
if uv_lay is None:
    bpy.ops.object.mode_set(mode='OBJECT')
    obj.data.uv_layers.new(name="LabelUV")
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    uv_lay = bm.loops.layers.uv.active
    # Re-identify panel faces after bmesh rebuild
    panel_faces = []
    for face in bm.faces:
        n = face.normal
        cz = face.calc_center_median().z
        if n.y < -0.3 and z_panel_min <= cz <= z_panel_max:
            panel_faces.append(face)

px_range = px_max - px_min
pz_range_val = pz_max - pz_min

for face in panel_faces:
    for loop in face.loops:
        co = loop.vert.co
        u = (co.x - px_min) / px_range
        v = (co.z - pz_min) / pz_range_val
        loop[uv_lay].uv = (u, v)

bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
print("UV remapped for panel faces")

# ── 9. Create livernois panel material (slot index 3) ─────────────────────────
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

# Append as slot 3 (original slots 0/1/2 stay intact)
obj.data.materials.append(mat)
panel_mat_index = len(obj.data.materials) - 1
print(f"LabelMaterial added at slot index {panel_mat_index}")

# ── 10. Assign panel material index to panel faces ────────────────────────────
bpy.ops.object.mode_set(mode='EDIT')
bm = bmesh.from_edit_mesh(obj.data)
bm.faces.ensure_lookup_table()

# Re-identify panel faces in the fresh bmesh
for face in bm.faces:
    n = face.normal
    cz = face.calc_center_median().z
    if n.y < -0.3 and z_panel_min <= cz <= z_panel_max:
        face.material_index = panel_mat_index

bmesh.update_edit_mesh(obj.data)
bpy.ops.object.mode_set(mode='OBJECT')
print(f"Panel faces assigned to material slot {panel_mat_index}")

# ── 11. Export balloon-label.glb ──────────────────────────────────────────────
bpy.ops.export_scene.gltf(
    filepath=OUTPUT_GLB,
    export_format='GLB',
    export_texcoords=True,
    export_materials='EXPORT',
    export_apply=True,
    use_selection=False,
)
print(f"\n✓  Exported: {OUTPUT_GLB}")
