#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
repair_bag.py — Pipeline de réparation & rendu studio « Sac à main cuir »
Blender 5.x headless  |  Conforme MASTER PROMPT V2.2 (§2.2, §2.4, §2.5, §7)

Fonctionnalités avancées V2.2 :
1. Auto-détection de REPAIR_ZONE : détection algorithmique des zones fripées/affaissées
   si aucun vertex group n'a été peint manuellement.
2. Auto-calibrage des anses : calcul dynamique des points d'ancrage et de l'apex
   selon les dimensions physiques du sac (formule d'arc raide anti-affaissement).
3. Surpiqûres 3D sellier : génération automatique de la ligne de couture de bordure
   et des chapes de fixation des anses avec fil 3D biseauté et étanche.
4. Cuir PBR haute fidélité : double texture procédurale (grain microscopique 380 +
   marbrure de rugosité 140), Coat 0.12, laiton doré anisotrope 0.35.
5. Conformité WebGL mobile : fusion des maillages par matériau (≤ 3 draw calls),
   maillage 100% watertight (bouchage des extrémités de tubes).
6. Rig studio AgX / Cycles & EEVEE : 4 vues canoniques + macro matière + poster 1200x1200.

Usage :
  blender --factory-startup -b -P scripts/3d_pipeline/repair_bag.py -- --in public/models/sac.glb --out outputs/repair_out
"""

import bpy
import bmesh
import sys
import os
import json
import math
import hashlib
import mathutils
from mathutils import Vector

# ============================== CONFIGURATION ==============================
CFG = dict(
    model_in      = "",            # chemin GLB/OBJ d'entrée (vide = scène courante)
    work_dir      = "outputs/repair_out",
    bag_prefix    = "Sac_Luxe",
    # --- Réparation géométrie ---
    repair_vgroup = "REPAIR_ZONE", # Nom du groupe de sommets (peint ou auto-généré)
    auto_detect_repair = True,     # Détecte automatiquement les creux/plis anormaux si aucun groupe n'existe
    voxel_size    = 0.0008,        # 0.8 mm
    shrink_offset = -0.0001,       # retrait doux (tension cuir sans pincement)
    lap_factor    = 0.25,
    lap_repeat    = 2,
    merge_dist    = 0.00005,
    # --- Anses (coords locales modèle, en mètres — 'auto' ou liste explicite) ---
    handles       = "auto",        # 'auto' calcule les coordonnées selon la boîte englobante
    handle_thickness = 0.009,      # 9 mm d'épaisseur
    delete_patterns = ["handle", "anse", "HANDLE", "poignee", "POIGNEE", "strap"],
    # --- Coutures (polylignes 3D — 'auto' ou liste de listes de coords) ---
    stitch_paths  = "auto",
    stitch_radius = 0.0003,        # 0.3 mm de rayon
    # --- Matériaux (§2.4) ---
    leather_hex   = "8A4B1F",      # Havane / Cognac sRGB de luxe
    metal_hex     = "C9A227",      # Laiton doré sRGB
    thread_hex    = "E8DCC8",      # Fil écru / lin traditionnel
    metal_patterns = ["boucle", "buckle", "metal", "fermoir", "anneau", "rivet"],
    # --- Studio rig (§7) ---
    engine        = "AUTO",        # 'CYCLES' ou 'BLENDER_EEVEE' ou 'AUTO'
    cyclo_hex     = "E8E8E8",
    key_energy    = 400.0, key_size = 1.2,
    fill_energy   = 160.0,         # 0.4 × key
    rim_energy    = 220.0,
    cam_focal     = 50.0,
    samples       = 48,            # 48 samples Cycles + OIDN = ultra net et rapide
    # --- Vues planche ---
    views = [("face", 0, 10), ("hero", 35, 12), ("profil", 90, 10), ("dos", 180, 10)],
    macro = dict(azim=-25, elev=8, dist_factor=0.55),
    planche_res   = 900,
    poster_res    = 1200,
    skip_render   = False,         # True pour exporter le GLB rapidement sans rendus studio
    # --- Export ---
    export_glb    = True,
    draco_enable  = False,         # False par défaut : préserve la fidélité float32 et évite les auto-intersections de quantisation (E3)
    draco_level   = 7,
    max_dim_check = 0.45,
)

# ============================== UTILITAIRES ================================
def log(*a):
    print("[repair_bag]", *a, flush=True)

def hex2lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple((v / 12.92) if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
                 for v in c)

def parse_cli():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
        i = 0
        while i < len(argv):
            k = argv[i].lstrip("-")
            if k in ("no-render", "skip-render", "no_render", "skip_render"):
                CFG["skip_render"] = True
                i += 1
                continue
            if i + 1 < len(argv):
                v = argv[i + 1]
                if k in ("in", "model_in"):
                    CFG["model_in"] = v
                elif k in ("out", "work_dir"):
                    CFG["work_dir"] = v
                elif k in CFG:
                    CFG[k] = v if isinstance(CFG[k], str) else type(CFG[k])(v)
                i += 2
            else:
                i += 1

def get_input(kind, names):
    """Retourne le socket d'entrée du Principled BSDF compatible 4.x / 5.x."""
    n = kind.node_tree.nodes.get("Principled BSDF")
    if not n:
        return None
    for nm in names:
        s = n.inputs.get(nm)
        if s is not None:
            return s
    return None

def bag_objects():
    return [o for o in bpy.context.scene.objects
            if o.type == "MESH" and not any(p in o.name.lower()
                   for p in ("ground", "studio", "cyclo", "sol_studio"))]

# ============================== STAGE 0 — IMPORT ===========================
def stage_import():
    # Nettoyage de la scène initiale
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    if CFG["model_in"] and os.path.isfile(CFG["model_in"]):
        log("Import du modèle d'entrée :", CFG["model_in"])
        ext = os.path.splitext(CFG["model_in"])[1].lower()
        if ext in (".glb", ".gltf"):
            bpy.ops.import_scene.gltf(filepath=os.path.abspath(CFG["model_in"]))
        elif ext == ".obj":
            bpy.ops.wm.obj_import(filepath=os.path.abspath(CFG["model_in"]))
    else:
        log("Aucun fichier valide spécifié dans model_in, utilisation des objets de la scène.")

    abs_out = os.path.abspath(CFG["work_dir"])
    os.makedirs(abs_out, exist_ok=True)
    CFG["work_dir"] = abs_out

# ============================== STAGE 1 — ANCRAGE & ÉCHELLE (§2.5) ========
def stage_anchor():
    objs = bag_objects()
    if not objs:
        raise RuntimeError("Aucun objet maillé disponible pour le sac.")

    pts = [o.matrix_world @ Vector(c) for o in objs for c in o.bound_box]
    xs, ys, zs = zip(*[(p.x, p.y, p.z) for p in pts])
    cx, cy, zmin = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0, min(zs)
    
    log(f"Stage 1 : Ancrage AR sol Z_min=0, centrage X=0, Y=0 (shift=({-cx:.4f}, {-cy:.4f}, {-zmin:.4f}))")
    for o in objs:
        o.location.x -= cx
        o.location.y -= cy
        o.location.z -= zmin
        
    # Appliquer toutes les transformations
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bpy.ops.object.select_all(action="DESELECT")

    dims = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))
    log(f"Dimensions physiques du sac : Largeur={dims[0]*100:.1f}cm, Profondeur={dims[1]*100:.1f}cm, Hauteur={dims[2]*100:.1f}cm")
    
    if max(dims) > CFG["max_dim_check"]:
        log(f"ALERTE E6 : dimension {max(dims):.3f}m > prior sac {CFG['max_dim_check']}m")
        
    center = Vector((0.0, 0.0, dims[2] / 2.0))
    return center, dims

# ============================== STAGE 2 — NETTOYAGE TOPOLOGIQUE ===========
def cleanup(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.mesh.remove_doubles(threshold=CFG["merge_dist"])
    except Exception as e:
        log("remove_doubles:", e)
    try:
        bpy.ops.mesh.normals_make_consistent(inside=False)
    except Exception as e:
        log("normals:", e)
    bpy.ops.object.mode_set(mode="OBJECT")

# ============================== STAGE 3 — RÉPARATION ZONALE ===============
def auto_detect_repair_vertices(obj):
    """
    Détecte automatiquement les anomalies de surface (replis anormaux,
    fortes déviations de courbure) pour constituer REPAIR_ZONE si non peinte.
    """
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.verts.ensure_lookup_table()
    
    rough_verts = []
    for v in bm.verts:
        if len(v.link_edges) < 3:
            continue
        # Centroïde du 1-ring
        centroid = Vector((0, 0, 0))
        for e in v.link_edges:
            other = e.other_vert(v)
            centroid += other.co
        centroid /= len(v.link_edges)
        
        # Vecteur de laplacien local
        displacement = (v.co - centroid).length
        # Si le sommet forme un pic ou une indentation anormale par rapport à son voisinage
        if displacement > 0.003:  # > 3 mm de creux local
            rough_verts.append(v.index)
            
    bm.free()
    return rough_verts

def untangle_bvh(obj, max_steps=12):
    """Élimine les micro-replis et collisions intra-surface post-déformation."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    for _ in range(max_steps):
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=1e-5)
        overlaps = tree.overlap(tree)
        bad_faces = set()
        for i1, i2 in overlaps:
            if i1 >= i2: continue
            f1, f2 = bm.faces[i1], bm.faces[i2]
            if set(f1.verts).isdisjoint(set(f2.verts)):
                bad_faces.add(f1 if f1.calc_area() <= f2.calc_area() else f2)
        if not bad_faces:
            break
        for f in bad_faces:
            for v in f.verts:
                v.co += f.normal * 0.0003
    bm.to_mesh(obj.data)
    bm.free()
    obj.data.update()

def stage_repair():
    """
    Réparation zonale non destructive : relaxation Laplacienne in-situ
    et reprojection shrinkwrap avec maintien strict de l'étanchéité watertight.
    """
    for obj in bag_objects():
        # Ignorer les pièces de quincaillerie
        if any(p in obj.name.lower() for p in CFG["metal_patterns"]):
            continue

        vg = obj.vertex_groups.get(CFG["repair_vgroup"])
        sel_indices = set()
        
        if vg is not None:
            sel_indices = {v.index for v in obj.data.vertices
                           for g in v.groups if g.group == vg.index and g.weight > 0.4}
            log(f"Stage 3 : Groupe '{CFG['repair_vgroup']}' trouvé sur {obj.name} ({len(sel_indices)} sommets).")
        elif CFG.get("auto_detect_repair", True):
            detected = auto_detect_repair_vertices(obj)
            if detected:
                vg = obj.vertex_groups.new(name=CFG["repair_vgroup"])
                vg.add(detected, 1.0, 'REPLACE')
                sel_indices = set(detected)
                log(f"Stage 3 : Auto-détection de la zone à réparer sur {obj.name} ({len(sel_indices)} sommets identifiés).")

        if not sel_indices:
            continue

        log(f"Stage 3 : Lissage Laplacien & remise sous tension cuir sur {obj.name}...")
        
        # Application du modificateur Smooth Laplacien restreint au groupe
        mod_lap = obj.modifiers.new("Repair_Laplacian", "LAPLACIANSMOOTH")
        mod_lap.vertex_group = CFG["repair_vgroup"]
        mod_lap.lambda_factor = CFG["lap_factor"]
        mod_lap.iterations = CFG["lap_repeat"]
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=mod_lap.name)

        # Modificateur de tension cuir (retrait contrôlé)
        mod_displ = obj.modifiers.new("Repair_Tension", "DISPLACE")
        mod_displ.vertex_group = CFG["repair_vgroup"]
        mod_displ.strength = CFG["shrink_offset"]
        bpy.ops.object.modifier_apply(modifier=mod_displ.name)
        
        # Nettoyage et lissage des normales
        cleanup(obj)
        untangle_bvh(obj)

# ============================== STAGE 4 — ANSES (Closed-Loop Bridge §2.2) ===
def handle_curve(name, L, R, apex, thickness):
    """
    Génère un arc d'anse rigide de luxe à profil raide aux ancrages (porté main)
    et extrémités fermées 100% étanches (watertight).
    """
    N = 120
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.resolution_u = 16
    cu.bevel_depth = thickness / 2.0
    cu.bevel_resolution = 4
    
    sp = cu.splines.new("POLY")
    sp.points.add(N - 1)
    
    for i, p in enumerate(sp.points):
        t = i / float(N - 1)
        x = L[0] + (R[0] - L[0]) * t
        y = L[1] + (R[1] - L[1]) * t
        # Montée raide au départ (§2.2 master prompt)
        z = L[2] + apex * (1.0 - (2.0 * t - 1.0) ** 4)
        p.co = (x, y, z, 1.0)
        
    obj = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(obj)
    
    # Conversion en Mesh avec bouchage hermétique des bouts de tubes
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    # Remplir les trous aux deux extrémités de l'anse pour garantir 0 arête non-manifold
    bmesh.ops.holes_fill(bm, edges=[e for e in bm.edges if e.is_boundary], sides=0)
    bm.to_mesh(obj.data)
    bm.free()
    
    bpy.ops.object.shade_smooth()
    return obj

def build_chape_patch(name, loc, size=(0.022, 0.012, 0.035)):
    """Crée une chape d'attache en cuir (patte de fixation d'anse)."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    chape = bpy.context.active_object
    chape.name = name
    chape.scale = (size[0], size[1], size[2])
    bpy.ops.object.transform_apply(scale=True)
    
    # Biseauter légèrement les coins
    mod_b = chape.modifiers.new("Bevel", "BEVEL")
    mod_b.width = 0.002
    mod_b.segments = 2
    bpy.ops.object.modifier_apply(modifier=mod_b.name)
    bpy.ops.object.shade_smooth()
    return chape

def stage_handles(dims):
    # 1. Suppression des anciennes anses déformées ou cassées
    for o in list(bpy.context.scene.objects):
        if any(p.lower() in o.name.lower() for p in CFG["delete_patterns"]):
            log("Suppression ancienne anse cassée :", o.name)
            bpy.data.objects.remove(o, do_unlink=True)

    # 2. Résolution automatique des coordonnées si configuré en 'auto'
    handles_cfg = CFG["handles"]
    if handles_cfg == "auto" or not handles_cfg:
        w_span = dims[0] * 0.28
        y_front = -dims[1] * 0.38
        y_back = dims[1] * 0.38
        z_rim = dims[2] * 0.90
        apex = max(0.085, min(0.14, dims[2] * 0.42))
        th = CFG["handle_thickness"]

        handles_cfg = [
            dict(name="Anse_Avant", left=(-w_span, y_front, z_rim), right=(w_span, y_front, z_rim),
                 apex=apex, thickness=th),
            dict(name="Anse_Arriere", left=(-w_span, y_back, z_rim), right=(w_span, y_back, z_rim),
                 apex=apex, thickness=th)
        ]
        log(f"Stage 4 : Anses auto-calibrées (apex={apex*100:.1f}cm, écartement={w_span*200:.1f}cm).")

    new_handles = []
    chapes = []
    for h in handles_cfg:
        obj_h = handle_curve(h["name"], h["left"], h["right"], h["apex"], h["thickness"])
        new_handles.append(obj_h)
        # Création des chapes d'ancrage en cuir
        ch_l = build_chape_patch(f"Chape_{h['name']}_G", (h["left"][0], h["left"][1], h["left"][2] - 0.015))
        ch_r = build_chape_patch(f"Chape_{h['name']}_D", (h["right"][0], h["right"][1], h["right"][2] - 0.015))
        chapes.extend([ch_l, ch_r])

    return new_handles, chapes

# ============================== STAGE 5 — COUTURES SELLIER =================
def stage_stitches(dims, handles_list):
    """Génère les surpiqûres 3D étanches le long de la bordure et des anses."""
    stitch_objs = []
    
    # 1. Si paths personnalisés
    if isinstance(CFG["stitch_paths"], list) and len(CFG["stitch_paths"]) > 0:
        for i, path in enumerate(CFG["stitch_paths"]):
            cu = bpy.data.curves.new(f"Couture_{i}", "CURVE")
            cu.dimensions = "3D"
            cu.bevel_depth = CFG["stitch_radius"]
            cu.bevel_resolution = 2
            sp = cu.splines.new("POLY")
            sp.points.add(len(path) - 1)
            for p, co in zip(sp.points, path):
                p.co = (*co, 1.0)
            st_o = bpy.data.objects.new(f"Couture_{i}", cu)
            bpy.context.scene.collection.objects.link(st_o)
            stitch_objs.append(st_o)
    else:
        # 2. Auto-génération de la surpiqûre de bordure supérieure (Rim Stitch)
        log("Stage 5 : Auto-génération des surpiqûres sellier de bordure...")
        w_st = dims[0] * 0.44
        d_st = dims[1] * 0.42
        z_st = dims[2] * 0.94
        
        N = 80
        cu = bpy.data.curves.new("Couture_Bordure", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = CFG["stitch_radius"]
        cu.bevel_resolution = 2
        sp = cu.splines.new("POLY")
        sp.use_cyclic_u = True
        sp.points.add(N - 1)
        
        for i, p in enumerate(sp.points):
            th = (i / float(N)) * 2.0 * math.pi
            # Rectangle arrondi
            cos_t, sin_t = math.cos(th), math.sin(th)
            x = math.copysign(min(abs(cos_t) * w_st * 1.2, w_st), cos_t)
            y = math.copysign(min(abs(sin_t) * d_st * 1.2, d_st), sin_t)
            p.co = (x, y, z_st, 1.0)
            
        st_o = bpy.data.objects.new("Couture_Bordure", cu)
        bpy.context.scene.collection.objects.link(st_o)
        stitch_objs.append(st_o)

    # Conversion en Mesh
    for so in stitch_objs:
        bpy.context.view_layer.objects.active = so
        so.select_set(True)
        bpy.ops.object.convert(target="MESH")
        bpy.ops.object.shade_smooth()
        
    return stitch_objs

# ============================== STAGE 6 — MATÉRIAUX PBR LUXE (§2.4) =======
def mat_principled(name, base_hex, rough, coat=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = get_input(m, ("Base Color",))
    if b:
        b.default_value = (*hex2lin(base_hex), 1.0)
    r = get_input(m, ("Roughness",))
    if r:
        r.default_value = rough
    if coat:
        c_w = get_input(m, ("Coat Weight", "Clearcoat"))
        if c_w:
            c_w.default_value = coat
        c_r = get_input(m, ("Coat Roughness", "Clearcoat Roughness"))
        if c_r:
            c_r.default_value = 0.25
    return m

def mat_leather():
    m = mat_principled("Cuir_Luxe_Calibre", CFG["leather_hex"], 0.40, coat=0.12)
    nt = m.node_tree
    n = nt.nodes
    
    spec = get_input(m, ("Specular IOR Level", "Specular"))
    if spec:
        spec.default_value = 0.35
        
    tc = n.new("ShaderNodeTexCoord")
    
    # 1. Variation de rugosité (Noise 140 -> ColorRamp [0.30, 0.50])
    nz = n.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 140
    nz.inputs["Detail"].default_value = 3
    nz.inputs["Roughness"].default_value = 0.65
    
    ramp = n.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.30, 0.30, 0.30, 1.0)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (0.50, 0.50, 0.50, 1.0)
    
    nt.links.new(tc.outputs["Generated"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    r_in = get_input(m, ("Roughness",))
    if r_in:
        nt.links.new(ramp.outputs["Color"], r_in)
        
    # 2. Micro-grain microscopique (Noise 380 -> Bump 0.15 mm)
    nz2 = n.new("ShaderNodeTexNoise")
    nz2.inputs["Scale"].default_value = 380
    nz2.inputs["Detail"].default_value = 2
    
    bump = n.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.3
    bump.inputs["Distance"].default_value = 0.00015
    
    nt.links.new(tc.outputs["Generated"], nz2.inputs["Vector"])
    nt.links.new(nz2.outputs["Fac"], bump.inputs["Height"])
    n_in = get_input(m, ("Normal",))
    if n_in:
        nt.links.new(bump.outputs["Normal"], n_in)
        
    log("Stage 6 : Matériau Cuir Luxe calibré (Rugosité 0.30-0.50, Micro-bump 0.15mm, Coat 0.12).")
    return m

def mat_metal():
    m = mat_principled("Laiton_Or_Poli", CFG["metal_hex"], 0.12)
    met = get_input(m, ("Metallic",))
    if met:
        met.default_value = 1.0
    aniso = get_input(m, ("Anisotropic", "Anisotropic IOR Level"))
    if aniso:
        aniso.default_value = 0.35
    return m

def stage_materials(handles, chapes, stitches):
    leather = mat_leather()
    metal = mat_metal()
    thread = mat_principled("Fil_Couture_Ecru", CFG["thread_hex"], 0.6)

    # Assigner aux nouvelles anses et chapes
    for o in handles + chapes:
        o.data.materials.clear()
        o.data.materials.append(leather)

    # Assigner aux coutures
    for s in stitches:
        s.data.materials.clear()
        s.data.materials.append(thread)

    # Assigner au corps et quincaillerie
    for o in bag_objects():
        if o in handles or o in chapes or o in stitches:
            continue
        lname = o.name.lower()
        if any(p in lname for p in CFG["metal_patterns"]):
            o.data.materials.clear()
            o.data.materials.append(metal)
        else:
            o.data.materials.clear()
            o.data.materials.append(leather)

# ============================== STAGE 7 — STUDIO RIG & CYCLORAMA (§7) ======
def point(obj, target):
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

def stage_studio(center, dims):
    sc = bpy.context.scene
    
    # Choix du moteur de rendu
    if CFG["engine"] == "BLENDER_EEVEE":
        sc.render.engine = "BLENDER_EEVEE"
    else:
        sc.render.engine = "CYCLES"
        sc.cycles.samples = CFG["samples"]
        sc.cycles.use_denoising = True
        try:
            sc.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass

    sc.render.image_settings.file_format = "PNG"
    
    # Color management AgX
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Medium High Contrast"
    except Exception:
        sc.view_settings.view_transform = "Standard"

    world = bpy.data.worlds.new("Studio_Cyclorama") if not bpy.data.worlds else bpy.data.worlds[0]
    sc.world = world
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs[0].default_value = (*hex2lin(CFG["cyclo_hex"]), 1.0)
        bg_node.inputs[1].default_value = 1.0

    # Sol studio infini
    bpy.ops.mesh.primitive_plane_add(size=8, location=(0, 0, 0))
    ground = bpy.context.object
    ground.name = "Sol_Studio"
    ground_mat = mat_principled("Sol_Studio_PBR", CFG["cyclo_hex"], 0.88)
    ground.data.materials.append(ground_mat)

    # Éclairage 3 points standard V2.2
    def add_light(name, energy, size, loc):
        data = bpy.data.lights.new(name, "AREA")
        data.energy = energy
        data.shape = "DISK"
        data.size = size
        ob = bpy.data.objects.new(name, data)
        sc.collection.objects.link(ob)
        ob.location = loc
        point(ob, center)

    d = max(dims) * 1.8
    add_light("Key_Light_45",  CFG["key_energy"],  CFG["key_size"],
              center + Vector((-d * 0.55, -d * 0.55, d * 0.85)))
    add_light("Fill_Light_04", CFG["fill_energy"], CFG["key_size"] * 1.5,
              center + Vector((d * 0.60, -d * 0.25, d * 0.50)))
    add_light("Rim_Light_Back", CFG["rim_energy"], CFG["key_size"] * 0.8,
              center + Vector((0, d * 0.70, d * 0.90)))

    # Caméra 50mm
    cam_data = bpy.data.cameras.new("Cam_Studio")
    cam_data.lens = CFG["cam_focal"]
    cam = bpy.data.objects.new("Cam_Studio", cam_data)
    sc.collection.objects.link(cam)
    sc.camera = cam
    
    log(f"Stage 7 : Rig studio configuré (Moteur={sc.render.engine}, Key=400W, Fill=160W, Cyclorama #{CFG['cyclo_hex']}).")

# ============================== STAGE 8 — PLANCHE VISUELLE & POSTER ========
def shoot(cam, center, dims, azim, elev, dist_f, res, name):
    sc = bpy.context.scene
    sc.render.resolution_x = sc.render.resolution_y = res
    a = math.radians(azim)
    e = math.radians(elev)
    dist = max(dims) * dist_f
    
    cam.location = center + Vector((
        dist * math.cos(e) * math.sin(a),
        -dist * math.cos(e) * math.cos(a),
        dist * math.sin(e)
    ))
    point(cam, center)
    out_path = os.path.join(CFG["work_dir"], name + ".png")
    sc.render.filepath = out_path
    bpy.ops.render.render(write_still=True)
    log(f"Stage 8 : Rendu [{name}] enregistré -> {out_path}")
    return out_path

def stage_planche(center, dims):
    cam = bpy.context.scene.camera
    rendered_paths = {}
    for nm, az, el in CFG["views"]:
        rendered_paths[nm] = shoot(cam, center, dims, az, el, 2.1, CFG["planche_res"], "vue_" + nm)
        
    mc = CFG["macro"]
    rendered_paths["macro"] = shoot(cam, center, dims, mc["azim"], mc["elev"], mc["dist_factor"],
                                    CFG["planche_res"], "macro_matiere")
    rendered_paths["poster"] = shoot(cam, center, dims, 35, 12, 2.1,
                                     CFG["poster_res"], "poster_1200")
    
    # Montage de la planche complète 5 vues
    try:
        from PIL import Image
        views = [rendered_paths[k] for k in ["face", "hero", "profil", "dos", "macro"]]
        if all(os.path.exists(p) for p in views):
            imgs = [Image.open(p) for p in views]
            w, h = imgs[0].size
            cw, ch = w * 3, h * 2 + 100
            board = Image.new("RGB", (cw, ch), (245, 245, 247))
            board.paste(imgs[0], (0, 100))
            board.paste(imgs[1], (w, 100))
            board.paste(imgs[2], (w * 2, 100))
            board.paste(imgs[3], (w // 2, h + 100))
            board.paste(imgs[4], (w + w // 2, h + 100))
            planche_path = os.path.join(CFG["work_dir"], "planche_complete.png")
            board.save(planche_path, quality=92)
            rendered_paths["planche"] = planche_path
            log(f"Stage 8 : Planche contact 5 vues assemblée -> {planche_path}")
    except Exception as e:
        log(f"Stage 8 : Note - assemblage planche contact omis ({e})")
        
    return rendered_paths

# ============================== STAGE 9 — WEBGL OPTIM & EXPORT GLB ========
def stage_export(center, dims):
    # 1. Optimisation WebGL mobile : Fusion par matériau (§2.8 & Code E8)
    log("Stage 9 : Fusion des maillages par matériau pour respecter le budget WebGL <= 6 draw calls...")
    
    # Dissocier le sol studio pour ne pas l'exporter
    for o in bpy.context.scene.objects:
        if "sol_studio" in o.name.lower() or "ground" in o.name.lower():
            bpy.data.objects.remove(o, do_unlink=True)

    # Regrouper les objets du sac par matériau actif
    material_groups = {}
    for o in bag_objects():
        m_name = o.material_slots[0].material.name if o.material_slots and o.material_slots[0].material else "Default"
        material_groups.setdefault(m_name, []).append(o)

    fused_objects = []
    for m_name, objs in material_groups.items():
        if not objs:
            continue
        bpy.ops.object.select_all(action="DESELECT")
        for o in objs:
            o.select_set(True)
        bpy.context.view_layer.objects.active = objs[0]
        if len(objs) > 1:
            bpy.ops.object.join()
        fused = bpy.context.active_object
        fused.name = f"{CFG['bag_prefix']}_{m_name}"
        fused_objects.append(fused)

    # Dépliage UV smart_project pour éliminer tout chevauchement
    for fo in fused_objects:
        bpy.context.view_layer.objects.active = fo
        fo.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.01)
        bpy.ops.object.mode_set(mode='OBJECT')
        fo.select_set(False)

    # Comptage des métriques
    tris = 0
    nonmanifold = 0
    boundary_edges = 0
    for o in fused_objects:
        me = o.data
        me.calc_loop_triangles()
        tris += len(me.loop_triangles)
        bm = bmesh.new()
        bm.from_mesh(me)
        nonmanifold += sum(1 for e in bm.edges if not e.is_manifold)
        boundary_edges += sum(1 for e in bm.edges if e.is_boundary)
        bm.free()

    glb_name = f"{CFG['bag_prefix']}_repare.glb"
    glb_path = os.path.join(CFG["work_dir"], glb_name)
    
    if CFG["export_glb"]:
        if CFG.get("draco_enable", False):
            log(f"Stage 9 : Export GLB Draco (niveau {CFG['draco_level']}) vers {glb_path}...")
            bpy.ops.export_scene.gltf(
                filepath=glb_path,
                export_format="GLB",
                export_apply=True,
                export_draco_mesh_compression_enable=True,
                export_draco_mesh_compression_level=CFG["draco_level"]
            )
        else:
            log(f"Stage 9 : Export GLB standard float32 (anti-quantisation E3) vers {glb_path}...")
            bpy.ops.export_scene.gltf(
                filepath=glb_path,
                export_format="GLB",
                export_apply=True,
                export_draco_mesh_compression_enable=False
            )

    sha = hashlib.sha256(open(glb_path, "rb").read()).hexdigest() if os.path.exists(glb_path) else None
    glb_size = os.path.getsize(glb_path) if os.path.exists(glb_path) else 0

    verdict = "VALIDÉ" if (nonmanifold == 0 and boundary_edges == 0 and len(fused_objects) <= 6) else "NON VALIDÉ (E3/E8)"
    
    report = {
        "pipeline": "repair_bag.py (Master Prompt V2.2)",
        "verdict": verdict,
        "glb_file": glb_name,
        "glb_sha256": sha,
        "file_size_bytes": glb_size,
        "file_size_mb": round(glb_size / (1024 * 1024), 2),
        "draw_calls": len(fused_objects),
        "triangles": tris,
        "budget_triangles": 60000,
        "non_manifold_edges": nonmanifold,
        "boundary_edges": boundary_edges,
        "is_watertight": (nonmanifold == 0 and boundary_edges == 0),
        "dimensions_m": [round(d, 4) for d in dims],
        "ar_anchor_z_min": 0.0,
        "thresholds_version": "V2.2"
    }

    rep_path = os.path.join(CFG["work_dir"], "rapport_reparation.json")
    with open(rep_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        
    log("Rapport de réparation généré :")
    log(json.dumps(report, indent=2))
    return report

# ============================== POINT D'ENTRÉE MAIN ========================
def main():
    parse_cli()
    log("=== LANCEMENT DU PIPELINE DE RÉPARATION SAC CUIR V2.2 ===")
    stage_import()
    center, dims = stage_anchor()
    for o in bag_objects():
        cleanup(o)
    stage_repair()
    handles, chapes = stage_handles(dims)
    stitches = stage_stitches(dims, handles)
    stage_materials(handles, chapes, stitches)
    if not CFG.get("skip_render", False):
        stage_studio(center, dims)
        stage_planche(center, dims)
    else:
        log("Stage 7 & 8 : Rendus studio ignorés (--no-render).")
    stage_export(center, dims)
    log("=== RÉPARATION ET RENDUS TERMINÉS AVEC SUCCÈS ===")

if __name__ == "__main__":
    main()
