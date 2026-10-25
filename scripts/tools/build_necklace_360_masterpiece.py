import bpy
import os
import math
import numpy as np

out_glb = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\public\models\art-301.glb"
preview_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic\necklace_360_master"
os.makedirs(preview_dir, exist_ok=True)
poster_out = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\public\models\art-301-poster.png"

# Reset Blender
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# 1. PBR Materials
# Material 1: Coral Glass (Corail rouge/orange)
mat_coral = bpy.data.materials.new("M_Corail_Verre")
mat_coral.use_nodes = True
nodes = mat_coral.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
bsdf_c = nodes.new('ShaderNodeBsdfPrincipled')
bsdf_c.inputs['Base Color'].default_value = (0.85, 0.28, 0.14, 1.0) # Rich coral red
bsdf_c.inputs['Roughness'].default_value = 0.22
bsdf_c.inputs['IOR'].default_value = 1.52
mat_coral.node_tree.links.new(bsdf_c.outputs['BSDF'], out_n.inputs['Surface'])

# Material 2: Gold Filigree / Brass (Or poli)
mat_gold = bpy.data.materials.new("M_Or_Poli")
mat_gold.use_nodes = True
nodes = mat_gold.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
bsdf_g = nodes.new('ShaderNodeBsdfPrincipled')
bsdf_g.inputs['Base Color'].default_value = (0.95, 0.78, 0.28, 1.0) # Luxury warm gold
bsdf_g.inputs['Metallic'].default_value = 1.0
bsdf_g.inputs['Roughness'].default_value = 0.20
mat_gold.node_tree.links.new(bsdf_g.outputs['BSDF'], out_n.inputs['Surface'])

# Material 3: White Pearl (Perle d'ivoire nacrée)
mat_pearl = bpy.data.materials.new("M_Perle_Nacree")
mat_pearl.use_nodes = True
nodes = mat_pearl.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
bsdf_p = nodes.new('ShaderNodeBsdfPrincipled')
bsdf_p.inputs['Base Color'].default_value = (0.94, 0.92, 0.88, 1.0) # Ivory pearl
bsdf_p.inputs['Roughness'].default_value = 0.15
mat_pearl.node_tree.links.new(bsdf_p.outputs['BSDF'], out_n.inputs['Surface'])

# Material 4: Maroon Patterned Focal Beads
mat_focal = bpy.data.materials.new("M_Perle_Focale_Bordeaux")
mat_focal.use_nodes = True
nodes = mat_focal.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
bsdf_f = nodes.new('ShaderNodeBsdfPrincipled')
bsdf_f.inputs['Base Color'].default_value = (0.48, 0.08, 0.10, 1.0) # Deep burgundy
bsdf_f.inputs['Metallic'].default_value = 0.35
bsdf_f.inputs['Roughness'].default_value = 0.30
mat_focal.node_tree.links.new(bsdf_f.outputs['BSDF'], out_n.inputs['Surface'])

# Material 5: Velvet Clasp (Velours rouge fermoir)
mat_velvet = bpy.data.materials.new("M_Velours_Fermoir")
mat_velvet.use_nodes = True
nodes = mat_velvet.node_tree.nodes
nodes.clear()
out_n = nodes.new('ShaderNodeOutputMaterial')
bsdf_v = nodes.new('ShaderNodeBsdfPrincipled')
bsdf_v.inputs['Base Color'].default_value = (0.50, 0.04, 0.07, 1.0) # Royal crimson velvet
bsdf_v.inputs['Roughness'].default_value = 0.75
mat_velvet.node_tree.links.new(bsdf_v.outputs['BSDF'], out_n.inputs['Surface'])

# 2. Geometry: Clasp (Manchon supérieur en velours)
bpy.ops.mesh.primitive_cylinder_add(
    radius=0.016,
    depth=0.09,
    vertices=24,
    location=(0.0, 0.18, 0.02)
)
clasp_obj = bpy.context.active_object
clasp_obj.name = "Fermoir_Velours"
clasp_obj.rotation_euler = (0, math.radians(90), 0)
clasp_obj.data.materials.append(mat_velvet)

# Golden end-caps for clasp
for side in [-1, 1]:
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.017,
        depth=0.008,
        vertices=20,
        location=(side * 0.045, 0.18, 0.02)
    )
    cap = bpy.context.active_object
    cap.rotation_euler = (0, math.radians(90), 0)
    cap.data.materials.append(mat_gold)

# 3. Generating the 5 Strands of Beads
# Parametric 3D curve for a necklace drape:
# x(t) = a * sin(t)
# y(t) = b * cos(t) with sag
# z(t) = c * (1 - cos(t)) forward drape

num_strands = 5
strands_beads_objs = []

# Base dimensions of necklace (width ~ 28cm to 34cm, height ~ 36cm to 46cm)
strand_params = [
    # (a_width, b_height, sag_depth, num_beads)
    (0.125, 0.165, 0.035, 68),  # Strand 1 (innermost)
    (0.138, 0.185, 0.042, 76),  # Strand 2
    (0.150, 0.208, 0.050, 84),  # Strand 3
    (0.162, 0.230, 0.058, 92),  # Strand 4
    (0.174, 0.252, 0.065, 100), # Strand 5 (outermost)
]

for s_idx, (a_w, b_h, sag_z, n_beads) in enumerate(strand_params):
    # Parameter t goes from ~ math.pi * 0.15 to math.pi * 0.85 for lower hanging arc
    # And connects up to the clasp at (-0.035, 0.18) and (+0.035, 0.18)
    
    t_vals = np.linspace(-math.pi * 0.88, math.pi * 0.88, n_beads)
    
    for i, t in enumerate(t_vals):
        # Arc equations:
        # Normalized parameter u from -1 (left clasp) to 0 (bottom) to +1 (right clasp)
        u = t / (math.pi * 0.88)
        
        # Elliptical width with natural pinch at neck
        x = a_w * math.sin(t * 0.95)
        # Vertical drop: high at ends (near clasp y=0.18), drops to y = 0.18 - b_h * 1.5 at bottom
        drop_factor = (1.0 - math.cos(t * 0.95)) / 2.0
        y = 0.175 - drop_factor * (b_h * 1.85)
        
        # 3D Depth Drape (hangs forward in chest cavity, curves back at neck)
        z = 0.02 + drop_factor * sag_z
        
        # Bead radius varies: normal beads ~ 3.5mm, focal beads ~ 5.5mm
        # Determine bead type based on pattern along strand
        is_focal = False
        is_gold = False
        is_pearl = False
        
        # Focal beads near the bottom arc (abs(u) < 0.5) spaced out
        if abs(u) < 0.6 and (i % 8 == 0):
            is_focal = True
            radius = 0.0062
            chosen_mat = mat_focal
        elif i % 5 == 0:
            is_gold = True
            radius = 0.0048
            chosen_mat = mat_gold
        elif i % 3 == 0:
            is_pearl = True
            radius = 0.0042
            chosen_mat = mat_pearl
        else:
            radius = 0.0038
            chosen_mat = mat_coral
        
        # Create bead mesh (icosphere with subdivision 2 = 80 faces, smooth and round)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2,
            radius=radius,
            location=(x, y, z)
        )
        bead = bpy.context.active_object
        bead.name = f"Bead_{s_idx}_{i}"
        bead.data.materials.append(chosen_mat)
        for poly in bead.data.polygons:
            poly.use_smooth = True
        strands_beads_objs.append(bead)

print(f"Total beads created: {len(strands_beads_objs)}")

# Select all bead objects and join by material to keep draw calls low
mat_groups = {}
for b in strands_beads_objs:
    m = b.data.materials[0].name
    if m not in mat_groups:
        mat_groups[m] = []
    mat_groups[m].append(b)

joined_parts = []
for m_name, b_list in mat_groups.items():
    bpy.ops.object.select_all(action='DESELECT')
    for b in b_list:
        b.select_set(True)
    bpy.context.view_layer.objects.active = b_list[0]
    bpy.ops.object.join()
    joined_obj = bpy.context.active_object
    joined_obj.name = f"Group_{m_name}"
    joined_parts.append(joined_obj)
    print(f"Joined {len(b_list)} beads into {joined_obj.name}")

# Select all objects and center geometry at origin
bpy.ops.object.select_all(action='SELECT')
# Export clean master GLB
bpy.ops.export_scene.gltf(
    filepath=out_glb,
    export_format='GLB',
    use_selection=True,
    export_apply=True,
    export_yup=True
)

glb_size = os.path.getsize(out_glb)
print(f"Masterpiece 360 GLB exported successfully : {out_glb} ({glb_size:,} octets)")

# 4. Multi-Angle Studio Render for 360 Validation
# Setup lighting
world = bpy.data.worlds.new("Studio360World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.04, 0.05, 0.07, 1.0)
bg.inputs['Strength'].default_value = 1.0

# 3-Point Studio Lights
# Key Light
key_light = bpy.data.lights.new("KeyLight", 'AREA')
key_light.energy = 60.0
key_light.size = 0.6
key_obj = bpy.data.objects.new("KeyLight", key_light)
scene.collection.objects.link(key_obj)
key_obj.location = (0.4, -0.6, 0.5)

# Fill Light
fill_light = bpy.data.lights.new("FillLight", 'AREA')
fill_light.energy = 25.0
fill_light.size = 0.8
fill_obj = bpy.data.objects.new("FillLight", fill_light)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-0.5, -0.5, 0.3)

# Rim Light (for bead highlights)
rim_light = bpy.data.lights.new("RimLight", 'SPOT')
rim_light.energy = 50.0
rim_light.spot_size = math.radians(60)
rim_obj = bpy.data.objects.new("RimLight", rim_light)
scene.collection.objects.link(rim_obj)
rim_obj.location = (0.0, 0.5, 0.4)
rim_obj.rotation_euler = (math.radians(-45), 0, 0)

# Camera
cam_data = bpy.data.cameras.new("Cam360")
cam_obj = bpy.data.objects.new("Cam360", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
scene.render.resolution_x = 900
scene.render.resolution_y = 900

angles = [
    ("front", (0.0, -0.75, 0.0), (math.radians(90), 0, 0)),
    ("hero_360", (0.42, -0.62, 0.28), (math.radians(70), 0, math.radians(34))),
    ("side", (0.75, 0.0, 0.0), (math.radians(90), 0, math.radians(90))),
    ("back", (0.0, 0.75, 0.0), (math.radians(90), 0, math.radians(180))),
]

for name, loc, rot in angles:
    cam_obj.location = loc
    cam_obj.rotation_euler = rot
    p_path = os.path.join(preview_dir, f"necklace_{name}.png")
    scene.render.filepath = p_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered view: {name} -> {p_path}")
    if name == "hero_360":
        # Copy to poster
        import shutil
        shutil.copy2(p_path, poster_out)
        print(f"Updated poster at: {poster_out}")

print("Masterpiece 360 build & render process complete.")
