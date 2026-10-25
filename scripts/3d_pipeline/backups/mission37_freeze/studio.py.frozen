"""
studio.py — Staging Studio Photoréaliste et Cadrage Adaptatif pour Blender 5.x
Adapte automatiquement l'éclairage, le cyclorama 360° et le recul caméra à la taille du modèle.
"""

import math
import os
import bpy
import bmesh
import mathutils


def calculate_bounding_sphere(mesh_objects):
    """Calcule le centre et le rayon englobant d'une collection d'objets maillés."""
    min_co = [float("inf"), float("inf"), float("inf")]
    max_co = [float("-inf"), float("-inf"), float("-inf")]

    for obj in mesh_objects:
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ mathutils.Vector(corner)
            for i in range(3):
                min_co[i] = min(min_co[i], world_corner[i])
                max_co[i] = max(max_co[i], world_corner[i])

    center = mathutils.Vector([(min_co[i] + max_co[i]) / 2.0 for i in range(3)])
    radius = max((mathutils.Vector(max_co) - center).length, 0.05)
    dims = [max_co[i] - min_co[i] for i in range(3)]
    return center, radius, dims


def setup_adaptive_cyclorama(scene, center, radius):
    """Crée ou adapte le cyclorama 360° radial à l'échelle de l'objet."""
    # Nettoyer les anciens décors
    for o in list(scene.collection.objects):
        if any(tag in o.name for tag in ["Studio_360", "Studio_Floor", "Studio_Cyclorama"]):
            bpy.data.objects.remove(o, do_unlink=True)

    mesh = bpy.data.meshes.new("Studio_Adaptive_Cyclorama_Mesh")
    bm = bmesh.new()

    n_segments = 64
    r_floor = max(radius * 7.0, 1.5)
    r_curve = max(radius * 3.5, 0.8)
    wall_height = max(radius * 6.0, 1.8)
    curve_steps = 12

    profile = [(0.0, 0.0), (r_floor, 0.0)]
    for i in range(1, curve_steps + 1):
        th = (math.pi / 2.0) * (i / curve_steps)
        r = r_floor + r_curve * (1.0 - math.cos(th))
        z = r_curve * math.sin(th)
        profile.append((r, z))
    profile.append((r_floor + r_curve, wall_height))

    rings = []
    for r, z in profile:
        ring = []
        if r <= 1e-5:
            v_center = bm.verts.new((0.0, 0.0, 0.0))
            ring.append(v_center)
        else:
            for seg in range(n_segments):
                angle = 2.0 * math.pi * (seg / n_segments)
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                v = bm.verts.new((x, y, z))
                ring.append(v)
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    # Raccordement centre
    for seg in range(n_segments):
        next_seg = (seg + 1) % n_segments
        bm.faces.new((rings[0][0], rings[1][seg], rings[1][next_seg]))

    # Anneaux
    for r_idx in range(1, len(rings) - 1):
        r1, r2 = rings[r_idx], rings[r_idx + 1]
        for seg in range(n_segments):
            next_seg = (seg + 1) % n_segments
            bm.faces.new((r1[seg], r1[next_seg], r2[next_seg], r2[seg]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    cyc_obj = bpy.data.objects.new("Studio_360_Cove", mesh)
    scene.collection.objects.link(cyc_obj)

    # Matériau blanc studio neutre
    mat_cyc = bpy.data.materials.get("M_Studio_Neutral_Cyclorama")
    if not mat_cyc:
        mat_cyc = bpy.data.materials.new("M_Studio_Neutral_Cyclorama")
        mat_cyc.use_nodes = True
        bsdf = next((n for n in mat_cyc.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.97, 0.97, 0.97, 1.0)
            bsdf.inputs["Roughness"].default_value = 0.85
    cyc_obj.data.materials.append(mat_cyc)
    return cyc_obj


def setup_studio_staging(scene, mesh_objects):
    """Configure l'ensemble du studio (éclairage 4-points, caméra 85mm et cyclorama)."""
    center, radius, dims = calculate_bounding_sphere(mesh_objects)
    print(f"Studio adaptatif : Centre={center}, Rayon={radius:.4f}m, Dims={dims}")

    # 1. Cyclorama adaptatif
    setup_adaptive_cyclorama(scene, center, radius)

    # 2. Nettoyage des anciennes lumières
    for o in list(scene.collection.objects):
        if o.type == 'LIGHT':
            bpy.data.objects.remove(o, do_unlink=True)

    # Facteur d'échelle d'énergie et de distance
    scale_fac = max(radius / 0.18, 0.3)
    base_dist = radius * 3.5

    # Key Softbox (Zénithale douce)
    k_data = bpy.data.lights.new(name="Studio_KeySoftbox", type="AREA")
    k_data.energy = 110.0 * scale_fac
    k_data.size = max(radius * 4.0, 0.8)
    k_data.color = (1.0, 0.995, 0.985)
    k_obj = bpy.data.objects.new("Studio_KeySoftbox", k_data)
    k_obj.location = (center.x + base_dist * 0.4, center.y + base_dist * 0.5, center.z + base_dist * 1.2)
    k_obj.rotation_euler = (math.radians(-38.0), math.radians(18.0), math.radians(-25.0))
    scene.collection.objects.link(k_obj)

    # Flank Softbox (Panneau latéral)
    f_data = bpy.data.lights.new(name="Studio_FlankSoftbox", type="AREA")
    f_data.energy = 75.0 * scale_fac
    f_data.size = max(radius * 4.5, 0.9)
    f_data.color = (0.985, 0.99, 1.0)
    f_obj = bpy.data.objects.new("Studio_FlankSoftbox", f_data)
    f_obj.location = (center.x + base_dist * 1.1, center.y - base_dist * 0.1, center.z + base_dist * 0.5)
    f_obj.rotation_euler = (math.radians(10.0), math.radians(65.0), math.radians(5.0))
    scene.collection.objects.link(f_obj)

    # Front Fill Softbox
    ff_data = bpy.data.lights.new(name="Studio_FrontFillSoftbox", type="AREA")
    ff_data.energy = 50.0 * scale_fac
    ff_data.size = max(radius * 3.0, 0.6)
    ff_data.color = (1.0, 1.0, 1.0)
    ff_obj = bpy.data.objects.new("Studio_FrontFillSoftbox", ff_data)
    ff_obj.location = (center.x - base_dist * 0.2, center.y + base_dist * 1.1, center.z + base_dist * 0.4)
    ff_obj.rotation_euler = (math.radians(-42.0), math.radians(-10.0), math.radians(170.0))
    scene.collection.objects.link(ff_obj)

    # Rim Softbox (Kicker)
    r_data = bpy.data.lights.new(name="Studio_RimSoftbox", type="AREA")
    r_data.energy = 35.0 * scale_fac
    r_data.size = max(radius * 2.5, 0.5)
    r_data.color = (1.0, 1.0, 1.0)
    r_obj = bpy.data.objects.new("Studio_RimSoftbox", r_data)
    r_obj.location = (center.x - base_dist * 0.8, center.y - base_dist * 0.9, center.z + base_dist * 0.7)
    r_obj.rotation_euler = (math.radians(35.0), math.radians(-35.0), math.radians(-55.0))
    scene.collection.objects.link(r_obj)

    # Ambiance World
    if not scene.world:
        scene.world = bpy.data.worlds.new("Studio_World")
    scene.world.use_nodes = True
    bg = next((n for n in scene.world.node_tree.nodes if n.type == 'BACKGROUND'), None)
    if bg:
        bg.inputs["Color"].default_value = (0.95, 0.95, 0.95, 1.0)
        bg.inputs["Strength"].default_value = 0.65

    # 3. Moteur et AgX
    scene.render.engine = 'BLENDER_EEVEE'
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100

    if hasattr(scene.view_settings, "view_transform"):
        supported = [item.identifier for item in scene.view_settings.bl_rna.properties['view_transform'].enum_items]
        if 'AgX' in supported:
            scene.view_settings.view_transform = 'AgX'
            scene.view_settings.look = 'AgX - Medium High Contrast'

    # 4. Cible et Caméra
    target = next((o for o in scene.collection.objects if "LookTarget" in o.name), None)
    if not target:
        target = bpy.data.objects.new("Studio_LookTarget", None)
        scene.collection.objects.link(target)
    target.location = center

    cam = scene.camera
    if not cam:
        cam_data = bpy.data.cameras.new("Studio_Camera")
        cam = bpy.data.objects.new("Studio_Camera", cam_data)
        scene.collection.objects.link(cam)
        scene.camera = cam

    cam.data.lens = 85.0
    cam.data.sensor_width = 36.0

    for c in list(cam.constraints):
        cam.constraints.remove(c)
    track = cam.constraints.new(type="TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    # Calcul distance focale adaptative pour optique 85mm (FOV horizontal ~23.9°)
    fov_rad = 2.0 * math.atan(18.0 / 85.0)
    cam_dist = max((radius * 1.35) / math.tan(fov_rad / 2.0), 0.3)

    return {
        "center": center,
        "radius": radius,
        "dims": dims,
        "camera": cam,
        "target": target,
        "cam_dist": cam_dist
    }


def render_standard_views(scene, studio_info, output_dir, prefix="render"):
    """Exécute les rendus des 4 vues canoniques du produit."""
    os.makedirs(output_dir, exist_ok=True)
    center = studio_info["center"]
    cam = studio_info["camera"]
    dist = studio_info["cam_dist"]

    views = [
        (f"{prefix}_hero.png", (center.x + dist * 0.707, center.y + dist * 0.707, center.z + dist * 0.35)),
        (f"{prefix}_front.png", (center.x, center.y + dist, center.z + dist * 0.15)),
        (f"{prefix}_side.png", (center.x + dist, center.y, center.z + dist * 0.15)),
        (f"{prefix}_top.png", (center.x + 0.001, center.y + 0.001, center.z + dist))
    ]

    rendered_files = []
    for fname, cam_pos in views:
        cam.location = cam_pos
        out_path = os.path.abspath(os.path.join(output_dir, fname))
        scene.render.filepath = out_path
        print(f"Rendering view {fname} at {cam_pos}...")
        bpy.ops.render.render(write_still=True)
        sz = os.path.getsize(out_path)
        rendered_files.append((fname, out_path, sz))
        print(f"  -> Generated {fname} ({sz} bytes)")

    return rendered_files
