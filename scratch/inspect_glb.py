import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath='public/models/art-301.glb')
meshes = [o for o in bpy.data.objects if o.type == 'MESH']
total_verts = sum(len(o.data.vertices) for o in meshes)
total_polys = sum(len(o.data.polygons) for o in meshes)
print(f'=== INSPECT ART-301 ===')
print(f'TOTAL_OBJECTS={len(meshes)}')
print(f'TOTAL_VERTICES={total_verts}')
print(f'TOTAL_POLYGONS={total_polys}')
for o in meshes:
    print(f'  Object: {o.name}, polys: {len(o.data.polygons)}, mats: {[m.name for m in o.data.materials]}')
