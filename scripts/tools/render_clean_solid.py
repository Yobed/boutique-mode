import bpy
import os
import math

glb_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic\art-301_solid_clean.glb"
out_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic\previews"
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Import GLB
bpy.ops.import_scene.gltf(filepath=glb_p)

# Setup studio lighting
world = bpy.data.worlds.new("StudioWorld")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes['Background']
bg.inputs['Color'].default_value = (0.05, 0.06, 0.08, 1.0) # Dark luxury studio
bg.inputs['Strength'].default_value = 1.0

# Key light
light_data = bpy.data.lights.new(name="KeyLight", type='AREA')
light_data.energy = 80.0
light_data.size = 0.8
light_obj = bpy.data.objects.new(name="KeyLight", object_data=light_data)
scene.collection.objects.link(light_obj)
light_obj.location = (0.5, -0.6, 0.7)
light_obj.rotation_euler = (math.radians(45), 0, math.radians(40))

# Fill light
fill_data = bpy.data.lights.new(name="FillLight", type='AREA')
fill_data.energy = 30.0
fill_data.size = 1.0
fill_obj = bpy.data.objects.new(name="FillLight", object_data=fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-0.6, -0.4, 0.4)

# Camera
cam_data = bpy.data.cameras.new("StudioCamera")
cam_obj = bpy.data.objects.new("StudioCamera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
scene.render.resolution_x = 800
scene.render.resolution_y = 800

# Render angles
angles = [
    ("front", (0.0, -0.85, 0.0), (math.radians(90), 0, 0)),
    ("hero", (0.45, -0.7, 0.35), (math.radians(65), 0, math.radians(35))),
    ("side", (0.85, 0.0, 0.0), (math.radians(90), 0, math.radians(90))),
]

for name, loc, rot in angles:
    cam_obj.location = loc
    cam_obj.rotation_euler = rot
    scene.render.filepath = os.path.join(out_dir, f"solid_{name}.png")
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {name}")

print("All studio views rendered successfully.")
