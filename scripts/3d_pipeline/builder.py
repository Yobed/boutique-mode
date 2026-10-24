"""
builder.py — Moteur Géométrique Procédural pour Blender 5.x
Génère des maillages 3D étanches (manifold), propres et prêts pour la production.
"""

import math
import bpy
import bmesh
import mathutils

from materials import get_or_create_material


def finalize_mesh_object(obj, material_name=None, bevel_width=None, bevel_segments=2, use_weighted_normal=True):
    """Finalise l'objet maillage : UVs, shading, biseaux et normales pondérées."""
    mesh = obj.data

    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")

    if bevel_width and bevel_width > 0:
        bev = obj.modifiers.get("Bevel")
        if not bev:
            bev = obj.modifiers.new(name="Bevel", type='BEVEL')
        bev.width = bevel_width
        bev.segments = bevel_segments
        bev.limit_method = 'ANGLE'
        bev.angle_limit = math.radians(35.0)

    if use_weighted_normal:
        wn = obj.modifiers.get("WeightedNormal")
        if not wn:
            wn = obj.modifiers.new(name="WeightedNormal", type='WEIGHTED_NORMAL')
        wn.keep_sharp = True

    if material_name:
        mat = bpy.data.materials.get(material_name)
        if not mat:
            mat = get_or_create_material(material_name)
        if not obj.data.materials:
            obj.data.materials.append(mat)
        else:
            obj.data.materials[0] = mat

    return obj


def build_rounded_box(scene, name, dims, corner_radius=0.015, taper_ratio=1.0, bevel_width=0.002, material_name=None, location=(0, 0, 0), rotation=(0, 0, 0)):
    """
    Construit un parallélépipède à coins verticaux arrondis, dépouille et chanfrein sommital.
    """
    dx, dy, dz = dims
    bm = bmesh.new()

    hx, hy = dx / 2.0, dy / 2.0
    r = min(corner_radius, hx * 0.9, hy * 0.9)
    cx, cy = hx - r, hy - r
    n_seg = 6

    profile_base = []
    for i in range(n_seg + 1):
        th = (math.pi / 2.0) * (i / n_seg)
        profile_base.append((cx + r * math.cos(th), cy + r * math.sin(th)))
    for i in range(n_seg + 1):
        th = (math.pi / 2.0) + (math.pi / 2.0) * (i / n_seg)
        profile_base.append((-cx + r * math.cos(th), cy + r * math.sin(th)))
    for i in range(n_seg + 1):
        th = math.pi + (math.pi / 2.0) * (i / n_seg)
        profile_base.append((-cx + r * math.cos(th), -cy + r * math.sin(th)))
    for i in range(n_seg + 1):
        th = (3.0 * math.pi / 2.0) + (math.pi / 2.0) * (i / n_seg)
        profile_base.append((cx + r * math.cos(th), -cy + r * math.sin(th)))

    unique_profile = []
    for pt in profile_base:
        if not unique_profile or math.hypot(pt[0] - unique_profile[-1][0], pt[1] - unique_profile[-1][1]) > 1e-5:
            unique_profile.append(pt)

    bottom_verts = [bm.verts.new((x, y, 0.0)) for x, y in unique_profile]
    t = taper_ratio
    top_verts = [bm.verts.new((x * t, y * t, dz)) for x, y in unique_profile]

    bm.verts.ensure_lookup_table()
    n_pts = len(unique_profile)

    for i in range(n_pts):
        next_i = (i + 1) % n_pts
        bm.faces.new((bottom_verts[i], bottom_verts[next_i], top_verts[next_i], top_verts[i]))

    bm.faces.new(reversed(bottom_verts))
    bm.faces.new(top_verts)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    scene.collection.objects.link(obj)

    return finalize_mesh_object(obj, material_name=material_name, bevel_width=bevel_width, use_weighted_normal=True)


def build_lathe(scene, name, profile_points, n_segments=36, is_hollow=False, wall_thickness=0.004, bevel_width=None, material_name=None, location=(0, 0, 0)):
    """
    Construit un solide de révolution autour de l'axe Z à partir d'un profil (r, z).
    Garantit une géométrie 100% étanche (2-manifold) et sans arêtes libres.
    """
    bm = bmesh.new()

    full_profile = []
    if is_hollow:
        ext_profile = list(profile_points)
        z_bot = ext_profile[0][1]
        z_top = ext_profile[-1][1]
        w = wall_thickness

        full_profile.append((0.0, z_bot))
        full_profile.extend(ext_profile)
        for r, z in reversed(ext_profile):
            r_in = max(0.002, r - w)
            z_in = z_top if z == z_top else max(z_bot + w, z)
            full_profile.append((r_in, z_in))
        full_profile.append((0.0, z_bot + w))
    else:
        full_profile = list(profile_points)

    rings = []
    for r, z in full_profile:
        ring = []
        if r <= 1e-5:
            v = bm.verts.new((0.0, 0.0, z))
            ring.append(v)
        else:
            for s in range(n_segments):
                angle = 2.0 * math.pi * (s / n_segments)
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                v = bm.verts.new((x, y, z))
                ring.append(v)
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    for idx in range(len(rings) - 1):
        r1 = rings[idx]
        r2 = rings[idx + 1]

        if len(r1) == 1 and len(r2) > 1:
            c = r1[0]
            for s in range(n_segments):
                ns = (s + 1) % n_segments
                bm.faces.new((c, r2[s], r2[ns]))
        elif len(r1) > 1 and len(r2) == 1:
            c = r2[0]
            for s in range(n_segments):
                ns = (s + 1) % n_segments
                bm.faces.new((r1[s], c, r1[ns]))
        elif len(r1) == len(r2) and len(r1) == n_segments:
            for s in range(n_segments):
                ns = (s + 1) % n_segments
                bm.faces.new((r1[s], r1[ns], r2[ns], r2[s]))

    if not is_hollow:
        if len(rings[0]) == n_segments:
            bm.faces.new(reversed(rings[0]))
        if len(rings[-1]) == n_segments:
            bm.faces.new(rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    scene.collection.objects.link(obj)

    return finalize_mesh_object(obj, material_name=material_name, bevel_width=bevel_width, use_weighted_normal=True)


def build_curved_sweep(scene, name, path_points, radius=0.005, n_segments=16, material_name=None, location=(0, 0, 0)):
    """
    Construit un tube extrudé le long d'une trajectoire 3D sans singularité de tangente.
    """
    bm = bmesh.new()
    rings = []
    n_pts = len(path_points)

    for i in range(n_pts):
        p_curr = mathutils.Vector(path_points[i])
        if i == 0:
            tangent = (mathutils.Vector(path_points[1]) - p_curr).normalized()
        elif i == n_pts - 1:
            tangent = (p_curr - mathutils.Vector(path_points[i - 1])).normalized()
        else:
            tangent = (mathutils.Vector(path_points[i + 1]) - mathutils.Vector(path_points[i - 1])).normalized()

        if tangent.length < 1e-4:
            tangent = mathutils.Vector((0, 0, 1))

        up = mathutils.Vector((0, 0, 1))
        if abs(tangent.dot(up)) > 0.9:
            up = mathutils.Vector((1, 0, 0))
        normal = tangent.cross(up).normalized()
        binormal = tangent.cross(normal).normalized()

        ring = []
        for s in range(n_segments):
            th = 2.0 * math.pi * (s / n_segments)
            offset = normal * (radius * math.cos(th)) + binormal * (radius * math.sin(th))
            v = bm.verts.new(p_curr + offset)
            ring.append(v)
        rings.append(ring)

    bm.verts.ensure_lookup_table()

    for idx in range(len(rings) - 1):
        r1, r2 = rings[idx], rings[idx + 1]
        for s in range(n_segments):
            ns = (s + 1) % n_segments
            bm.faces.new((r1[s], r1[ns], r2[ns], r2[s]))

    bm.faces.new(reversed(rings[0]))
    bm.faces.new(rings[-1])

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    scene.collection.objects.link(obj)

    return finalize_mesh_object(obj, material_name=material_name, bevel_width=None, use_weighted_normal=True)


def build_cylinder(scene, name, radius_top, radius_bottom, height, n_segments=24, bevel_width=None, material_name=None, location=(0, 0, 0), rotation=(0, 0, 0)):
    """
    Construit un cylindre ou cône tronqué orienté.
    """
    bm = bmesh.new()

    bot_verts = []
    top_verts = []
    for s in range(n_segments):
        th = 2.0 * math.pi * (s / n_segments)
        xb = radius_bottom * math.cos(th)
        yb = radius_bottom * math.sin(th)
        bot_verts.append(bm.verts.new((xb, yb, 0.0)))

        xt = radius_top * math.cos(th)
        yt = radius_top * math.sin(th)
        top_verts.append(bm.verts.new((xt, yt, height)))

    bm.verts.ensure_lookup_table()

    for s in range(n_segments):
        ns = (s + 1) % n_segments
        bm.faces.new((bot_verts[s], bot_verts[ns], top_verts[ns], top_verts[s]))

    bm.faces.new(reversed(bot_verts))
    bm.faces.new(top_verts)

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    scene.collection.objects.link(obj)

    return finalize_mesh_object(obj, material_name=material_name, bevel_width=bevel_width, use_weighted_normal=True)


def build_ring_collar(scene, name, r_ext, r_int, height, n_segments=32, bevel_width=0.0004, material_name=None, location=(0, 0, 0), rotation=(0, 0, 0)):
    """
    Construit une collerette/cerclage annulaire creux.
    """
    bm = bmesh.new()

    outer_bot, outer_top = [], []
    inner_bot, inner_top = [], []

    for s in range(n_segments):
        th = 2.0 * math.pi * (s / n_segments)
        ct, st = math.cos(th), math.sin(th)
        outer_bot.append(bm.verts.new((r_ext * ct, r_ext * st, 0.0)))
        outer_top.append(bm.verts.new((r_ext * ct, r_ext * st, height)))
        inner_bot.append(bm.verts.new((r_int * ct, r_int * st, 0.0)))
        inner_top.append(bm.verts.new((r_int * ct, r_int * st, height)))

    bm.verts.ensure_lookup_table()

    for s in range(n_segments):
        ns = (s + 1) % n_segments
        bm.faces.new((outer_bot[s], outer_bot[ns], outer_top[ns], outer_top[s]))
        bm.faces.new((inner_bot[ns], inner_bot[s], inner_top[s], inner_top[ns]))
        bm.faces.new((outer_top[s], outer_top[ns], inner_top[ns], inner_top[s]))
        bm.faces.new((outer_bot[ns], outer_bot[s], inner_bot[s], inner_bot[ns]))

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()

    for p in mesh.polygons:
        p.use_smooth = True

    obj = bpy.data.objects.new(name, mesh)
    obj.location = location
    obj.rotation_euler = rotation
    scene.collection.objects.link(obj)

    return finalize_mesh_object(obj, material_name=material_name, bevel_width=bevel_width, use_weighted_normal=True)
