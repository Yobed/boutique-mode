import bpy
import os

glb_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\3d_neural\art-301\mesh.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb_p)

obs = [o for o in bpy.context.scene.objects if o.type == 'MESH']
print(f"Imported {len(obs)} mesh objects")
for ob in obs:
    me = ob.data
    print(f"Object: {ob.name}, Verts: {len(me.vertices)}, Edges: {len(me.edges)}, Polys: {len(me.polygons)}")
    dim = ob.dimensions
    print(f"Dimensions: X={dim.x:.4f}, Y={dim.y:.4f}, Z={dim.z:.4f}")
    # Check bounding box
    bbox = [ob.matrix_world @ bpy.mathutils.Vector(b) for b in ob.bound_box]
    xs = [b.x for b in bbox]
    ys = [b.y for b in bbox]
    zs = [b.z for b in bbox]
    print(f"Bounds X: [{min(xs):.3f}, {max(xs):.3f}], Y: [{min(ys):.3f}, {max(ys):.3f}], Z: [{min(zs):.3f}, {max(zs):.3f}]")
