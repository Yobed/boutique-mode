import bpy
import os

glb_path = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\public\models\sac-elsi.glb"
out_img = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_elsi_authentic.png"

# Reset scene
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.resolution_x = 800
scene.render.resolution_y = 800
scene.render.film_transparent = False

# World background white
world = bpy.data.worlds.new("World_White")
scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs["Color"].default_value = (0.95, 0.95, 0.95, 1.0)
    bg_node.inputs["Strength"].default_value = 1.0

# Import GLB
bpy.ops.import_scene.gltf(filepath=glb_path)

# Find imported objects
objs = [o for o in scene.objects if o.type == "MESH"]
print(f"Imported {len(objs)} mesh objects from {glb_path}")

# Center and compute bbox
import mathutils
min_c = mathutils.Vector((float("inf"), float("inf"), float("inf")))
max_c = mathutils.Vector((float("-inf"), float("-inf"), float("-inf")))

for obj in objs:
    for v in obj.bound_box:
        w_v = obj.matrix_world @ mathutils.Vector(v)
        min_c.x = min(min_c.x, w_v.x)
        min_c.y = min(min_c.y, w_v.y)
        min_c.z = min(min_c.z, w_v.z)
        max_c.x = max(max_c.x, w_v.x)
        max_c.y = max(max_c.y, w_v.y)
        max_c.z = max(max_c.z, w_v.z)

center = (min_c + max_c) / 2.0
dims = max_c - min_c
max_dim = max(dims.x, dims.y, dims.z)

# Setup camera
cam_data = bpy.data.cameras.new("Cam_Front")
cam_data.lens = 55
cam_obj = bpy.data.objects.new("Cam_Front", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

cam_dist = max_dim * 2.5
cam_obj.location = (center.x, center.y - cam_dist, center.z)
cam_obj.rotation_euler = (1.5708, 0, 0) # look along +Y

# Key light
light_data = bpy.data.lights.new("Light_Key", type="AREA")
light_data.energy = 80
light_data.size = max_dim * 1.5
light_obj = bpy.data.objects.new("Light_Key", light_data)
scene.collection.objects.link(light_obj)
light_obj.location = (center.x + max_dim * 1.2, center.y - cam_dist * 0.8, center.z + max_dim * 1.2)

# Fill light
light_data2 = bpy.data.lights.new("Light_Fill", type="AREA")
light_data2.energy = 40
light_data2.size = max_dim * 2.0
light_obj2 = bpy.data.objects.new("Light_Fill", light_data2)
scene.collection.objects.link(light_obj2)
light_obj2.location = (center.x - max_dim * 1.2, center.y - cam_dist * 0.8, center.z + max_dim * 0.5)

scene.render.filepath = out_img
scene.render.image_settings.file_format = "PNG"
bpy.ops.render.render(write_still=True)
print(f"Rendered authentic bag reference: {out_img}")
