import bpy, sys, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
glb_path = os.path.abspath(argv[0])
out_dir = os.path.abspath(argv[1])
os.makedirs(out_dir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_path)

world = bpy.data.worlds.new("StudioWorld")
bpy.context.scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
if bg:
    bg.inputs[0].default_value = (0.95, 0.95, 0.95, 1.0)
    bg.inputs[1].default_value = 1.0

key_data = bpy.data.lights.new(name="Key", type='AREA')
key_data.energy = 50.0
key_data.size = 1.0
key_obj = bpy.data.objects.new(name="Key", object_data=key_data)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (1.5, -2.0, 2.0)

fill_data = bpy.data.lights.new(name="Fill", type='AREA')
fill_data.energy = 25.0
fill_data.size = 1.5
fill_obj = bpy.data.objects.new(name="Fill", object_data=fill_data)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (-2.0, -1.5, 1.0)

cam_data = bpy.data.cameras.new("Cam")
cam_obj = bpy.data.objects.new("Cam", cam_data)
bpy.context.collection.objects.link(cam_obj)
bpy.context.scene.camera = cam_obj
bpy.context.scene.render.resolution_x = 800
bpy.context.scene.render.resolution_y = 800

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
all_verts = []
for m in meshes:
    mw = m.matrix_world
    for v in m.data.vertices:
        all_verts.append(mw @ v.co)

if all_verts:
    min_c = Vector([min(v[i] for v in all_verts) for i in range(3)])
    max_c = Vector([max(v[i] for v in all_verts) for i in range(3)])
    center = (min_c + max_c) / 2.0
    dim = max_c - min_c
    radius = max(dim) * 0.9
else:
    center = Vector((0, 0, 0))
    radius = 1.0

def look_at(cam, target):
    direction = target - cam.location
    rot_quat = direction.to_track_quat('-Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()

# Render 1: Front
cam_obj.location = center + Vector((0, -radius * 2.2, 0))
look_at(cam_obj, center)
bpy.context.scene.render.filepath = os.path.join(out_dir, "render_front.png")
bpy.ops.render.render(write_still=True)

# Render 2: Hero 3/4
cam_obj.location = center + Vector((radius * 1.5, -radius * 1.8, radius * 0.8))
look_at(cam_obj, center)
bpy.context.scene.render.filepath = os.path.join(out_dir, "render_hero.png")
bpy.ops.render.render(write_still=True)

# Render 3: Side
cam_obj.location = center + Vector((radius * 2.2, 0, 0))
look_at(cam_obj, center)
bpy.context.scene.render.filepath = os.path.join(out_dir, "render_side.png")
bpy.ops.render.render(write_still=True)

print("ALL RENDERS COMPLETED SUCCESSFULLY")
