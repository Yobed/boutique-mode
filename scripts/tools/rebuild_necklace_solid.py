import bpy
import os
import cv2
import numpy as np

diag_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
mask_p = os.path.join(diag_dir, "03_perfect_necklace_mask.png")
rgba_p = os.path.join(diag_dir, "04_collier_detoure_propre.png")
out_glb = os.path.join(diag_dir, "art-301_solid_clean.glb")

# 1. Vectorize the clean mask to 2D polygons with OpenCV
mask = cv2.imread(mask_p, cv2.IMREAD_GRAYSCALE)
h, w = mask.shape

scale = 800.0 / max(h, w)
mask_small = cv2.resize(mask, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
sh, sw = mask_small.shape

contours, hierarchy = cv2.findContours(mask_small, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_TC89_KCOS)

print(f"Trouvé {len(contours)} contours")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

curve_data = bpy.data.curves.new(name="NecklaceCurve", type='CURVE')
curve_data.dimensions = '2D'
curve_data.fill_mode = 'BOTH'
curve_data.extrude = 0.008
curve_data.bevel_depth = 0.003
curve_data.bevel_resolution = 2

for i, cnt in enumerate(contours):
    area = cv2.contourArea(cnt)
    if area < 500:
        continue
    
    spline = curve_data.splines.new(type='POLY')
    spline.use_cyclic_u = True
    pts = cnt.reshape(-1, 2)
    spline.points.add(len(pts) - 1)
    
    for j, (px, py) in enumerate(pts):
        bx = (px - sw / 2.0) / (sw / 2.0) * 0.18
        by = -(py - sh / 2.0) / (sh / 2.0) * 0.22
        spline.points[j].co = (bx, by, 0.0, 1.0)

curve_obj = bpy.data.objects.new("Necklace", curve_data)
scene.collection.objects.link(curve_obj)
bpy.context.view_layer.objects.active = curve_obj
curve_obj.select_set(True)

bpy.ops.object.convert(target='MESH')
mesh_obj = bpy.context.active_object

remesh = mesh_obj.modifiers.new("VoxelRemesh", 'REMESH')
remesh.mode = 'VOXEL'
remesh.voxel_size = 0.0035
remesh.adaptivity = 0.0
bpy.ops.object.modifier_apply(modifier="VoxelRemesh")

smooth = mesh_obj.modifiers.new("Smooth", 'SMOOTH')
smooth.iterations = 3
smooth.factor = 0.5
bpy.ops.object.modifier_apply(modifier="Smooth")

# Direct UV assignment from planar coordinates
me = mesh_obj.data
if not me.uv_layers:
    uv_layer = me.uv_layers.new(name="UVMap")
else:
    uv_layer = me.uv_layers.active

min_x = min(v.co.x for v in me.vertices)
max_x = max(v.co.x for v in me.vertices)
min_y = min(v.co.y for v in me.vertices)
max_y = max(v.co.y for v in me.vertices)
span_x = max(max_x - min_x, 1e-5)
span_y = max(max_y - min_y, 1e-5)

uv_data = uv_layer.data
for poly in me.polygons:
    for loop_idx in poly.loop_indices:
        vert_idx = me.loops[loop_idx].vertex_index
        v = me.vertices[vert_idx]
        u = (v.co.x - min_x) / span_x
        v_coord = (v.co.y - min_y) / span_y
        uv_data[loop_idx].uv = (u, v_coord)

# PBR Material
mat = bpy.data.materials.new("M_Collier_Perles")
mat.use_nodes = True
nodes = mat.node_tree.nodes
links = mat.node_tree.links
nodes.clear()

output_node = nodes.new('ShaderNodeOutputMaterial')
principled = nodes.new('ShaderNodeBsdfPrincipled')
principled.inputs['Roughness'].default_value = 0.35
principled.inputs['Metallic'].default_value = 0.20

tex_image = nodes.new('ShaderNodeTexImage')
tex_image.image = bpy.data.images.load(rgba_p)

links.new(tex_image.outputs['Color'], principled.inputs['Base Color'])
links.new(principled.outputs['BSDF'], output_node.inputs['Surface'])

mesh_obj.data.materials.append(mat)

for f in me.polygons:
    f.use_smooth = True

# Export clean solid GLB
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True
)

print(f"Modèle solide étanche généré avec succès : {out_glb}")
print(f"Sommets: {len(me.vertices)}, Faces: {len(me.polygons)}")
