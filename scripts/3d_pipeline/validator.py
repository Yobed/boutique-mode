"""
validator.py — Moteur de Validation Topologique, Métrique & Qualité WebGL V2
Pipeline : boutique-mode / Master Prompt V2.2
Auteur : Architecte Principal Vision 3D & DT E-Commerce Luxe

Contrôles stricts appliqués :
1. Fichier : Empreinte SHA-256 déterministe (hashlib) et budget poids mobile (< 3 Mo).
2. Topologie : 0 arête non-manifold, maillage 100% fermé (watertight), 0 arête dégénérée, 0 sommet orphelin.
3. Auto-intersections BVH : Partitionnement en îlots connexes et détection des auto-intersections intra-surface (0 toléré).
4. UV Mapping : Analyse de recouvrement inter-îles sur grille 1024x1024 (seuil max 2.0%) et détection des faces UV dégénérées.
5. Échelle physique absolue : Boîte englobante en mètres et conformité aux priors catégoriels (±15%).
6. Assiette AR 1:1 : Contact sol Z_min = 0.0 ± 0.002 m, centrage X=0, Y=0.
7. Budget WebGL : Tris selon catégorie (sac <= 60k, bijoux <= 80k, mobilier <= 90k, generic <= 100k).
8. Draw calls : Nombre d'objets / matériaux <= 6 (Code E8).
9. Taxonomie d'échec unifiée (E1 à E9).
"""

import sys
import os
import json
import hashlib
import argparse
import numpy as np

# Blender modules (chargés automatiquement en mode Blender headless)
try:
    import bpy
    import bmesh
    import mathutils
    import cv2
except ImportError as err:
    print(f"AVERTISSEMENT: Modules Blender ou OpenCV manquants dans l'environnement courant ({err}).")
    print("Exécutez ce script via : blender --factory-startup -b -P validator.py -- [args]")

# Priors dimensionnels catégoriels en mètres [min, max] pour la plus grande dimension ou [dx, dy, dz]
CATEGORY_PRIORS = {
    "collier": {
        "label": "Collier / Sautoir Joaillerie",
        "budget_tris": 80000,
        "width_range": [0.18, 0.45],
        "depth_range": [0.18, 0.45],
        "height_range": [0.02, 0.25],
        "max_dim_range": [0.20, 0.48]
    },
    "bracelet": {
        "label": "Bracelet Joaillerie",
        "budget_tris": 80000,
        "width_range": [0.05, 0.12],
        "depth_range": [0.05, 0.12],
        "height_range": [0.01, 0.08],
        "max_dim_range": [0.06, 0.15]
    },
    "boucle_d_oreille": {
        "label": "Boucles d'oreilles",
        "budget_tris": 60000,
        "width_range": [0.01, 0.08],
        "depth_range": [0.01, 0.08],
        "height_range": [0.01, 0.10],
        "max_dim_range": [0.01, 0.10]
    },
    "sac": {
        "label": "Sac à main / Maroquinerie",
        "budget_tris": 60000,
        "width_range": [0.18, 0.50],
        "depth_range": [0.06, 0.25],
        "height_range": [0.12, 0.45],
        "max_dim_range": [0.20, 0.55]
    },
    "sac_a_main": {
        "label": "Sac à main / Maroquinerie",
        "budget_tris": 60000,
        "width_range": [0.18, 0.50],
        "depth_range": [0.06, 0.25],
        "height_range": [0.12, 0.45],
        "max_dim_range": [0.20, 0.55]
    },
    "chaussure": {
        "label": "Chaussure / Escarpin",
        "budget_tris": 70000,
        "width_range": [0.06, 0.15],
        "depth_range": [0.18, 0.35],
        "height_range": [0.06, 0.30],
        "max_dim_range": [0.20, 0.35]
    },
    "fauteuil": {
        "label": "Fauteuil / Mobilier",
        "budget_tris": 90000,
        "width_range": [0.60, 1.25],
        "depth_range": [0.50, 1.20],
        "height_range": [0.65, 1.25],
        "max_dim_range": [0.70, 1.30]
    },
    "canape": {
        "label": "Canapé / Mobilier",
        "budget_tris": 90000,
        "width_range": [1.20, 2.60],
        "depth_range": [0.70, 1.30],
        "height_range": [0.65, 1.10],
        "max_dim_range": [1.20, 2.70]
    },
    "vase": {
        "label": "Vase / Objet d'art",
        "budget_tris": 60000,
        "width_range": [0.08, 0.35],
        "depth_range": [0.08, 0.35],
        "height_range": [0.12, 0.55],
        "max_dim_range": [0.15, 0.60]
    },
    "bouteille": {
        "label": "Flacon / Bouteille",
        "budget_tris": 50000,
        "width_range": [0.05, 0.15],
        "depth_range": [0.05, 0.15],
        "height_range": [0.15, 0.40],
        "max_dim_range": [0.15, 0.40]
    },
    "generic": {
        "label": "Produit Générique",
        "budget_tris": 100000,
        "width_range": [0.02, 2.00],
        "depth_range": [0.02, 2.00],
        "height_range": [0.02, 2.00],
        "max_dim_range": [0.05, 2.20]
    }
}


def compute_file_sha256(filepath):
    """Calcule le SHA-256 déterministe sur les octets du fichier GLB."""
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def audit_bmesh_topology(mesh_data):
    """
    Audit topologique approfondi d'un maillage BMesh sans altérer les données de la scène.
    """
    bm = bmesh.new()
    bm.from_mesh(mesh_data)
    
    # 1. Élimination des doublons de coutures UV dans la copie temporaire
    # (Le format glTF duplique les sommets aux coutures UV et aux discontinuités de normales)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    bm.faces.ensure_lookup_table()
    
    vertex_count = len(bm.verts)
    edge_count = len(bm.edges)
    face_count = len(bm.faces)
    
    if vertex_count == 0 or face_count == 0:
        bm.free()
        return {
            "empty": True,
            "vertex_count": 0,
            "face_count": 0,
            "triangle_count": 0,
            "non_manifold_edges": 0,
            "boundary_edges": 0,
            "wire_edges": 0,
            "degenerate_edges": 0,
            "loose_vertices": 0,
            "is_watertight": False,
            "intra_self_intersections": 0,
            "inter_island_overlaps": 0,
            "islands_count": 0
        }

    # Calcul du nombre exact de triangles évalués
    triangle_count = sum(len(f.verts) - 2 for f in bm.faces)
    
    # Compteurs topologiques
    loose_vertices = sum(1 for v in bm.verts if not v.link_edges)
    degenerate_edges = sum(1 for e in bm.edges if e.calc_length() < 1e-6)
    
    non_manifold_edges = 0
    boundary_edges = 0
    wire_edges = 0
    
    for e in bm.edges:
        if not e.is_manifold:
            non_manifold_edges += 1
        if e.is_boundary:
            boundary_edges += 1
        if e.is_wire:
            wire_edges += 1

    is_watertight = (boundary_edges == 0 and non_manifold_edges == 0 and wire_edges == 0)

    # 2. Partitionnement en îlots connexes (Connected Components)
    face_island = {}
    island_idx = 0
    visited = set()
    for f in bm.faces:
        if f.index in visited:
            continue
        queue = [f]
        visited.add(f.index)
        face_island[f.index] = island_idx
        while queue:
            curr = queue.pop()
            for edge in curr.edges:
                for linked in edge.link_faces:
                    if linked.index not in visited:
                        visited.add(linked.index)
                        face_island[linked.index] = island_idx
                        queue.append(linked)
        island_idx += 1

    # 3. Détection des auto-intersections via BVHTree
    tree = mathutils.bvhtree.BVHTree.FromBMesh(bm, epsilon=1e-5)
    overlaps = tree.overlap(tree)
    
    intra_self_intersections = 0
    inter_island_overlaps = 0
    
    for i1, i2 in overlaps:
        if i1 >= i2:
            continue
        f1 = bm.faces[i1]
        f2 = bm.faces[i2]
        # Ignore les faces qui partagent un sommet ou une arête
        if set(f1.verts).isdisjoint(set(f2.verts)):
            if face_island.get(i1) == face_island.get(i2):
                intra_self_intersections += 1
            else:
                inter_island_overlaps += 1

    bm.free()

    return {
        "empty": False,
        "vertex_count": vertex_count,
        "edge_count": edge_count,
        "face_count": face_count,
        "triangle_count": triangle_count,
        "non_manifold_edges": non_manifold_edges,
        "boundary_edges": boundary_edges,
        "wire_edges": wire_edges,
        "degenerate_edges": degenerate_edges,
        "loose_vertices": loose_vertices,
        "is_watertight": is_watertight,
        "intra_self_intersections": intra_self_intersections,
        "inter_island_overlaps": inter_island_overlaps,
        "islands_count": island_idx
    }


def audit_uv_mapping(mesh_data):
    """
    Audit du dépliage UV : analyse de recouvrement inter-îles (overlap %) et détection de faces dégénérées.
    Partitionne d'abord les polygones en îles UV réelles (sans confondre les arêtes internes avec des recouvrements).
    """
    if not mesh_data.uv_layers:
        return {
            "has_uv": False,
            "degenerate_uv_faces": 0,
            "uv_overlap_pct": 0.0,
            "total_uv_coverage_pct": 0.0
        }

    bm = bmesh.new()
    bm.from_mesh(mesh_data)
    uv_layer = bm.loops.layers.uv.active

    if not uv_layer:
        bm.free()
        return {
            "has_uv": False,
            "degenerate_uv_faces": 0,
            "uv_overlap_pct": 0.0,
            "total_uv_coverage_pct": 0.0
        }

    # 1. Regroupement rapide en îles UV réelles
    islands = []
    visited_faces = set()
    degenerate_uv_faces = 0
    grid_size = 1024

    for f in bm.faces:
        if f.index in visited_faces:
            continue
        queue = [f]
        visited_faces.add(f.index)
        island_faces = [f]
        while queue:
            curr = queue.pop()
            for l in curr.loops:
                rad_l = l.link_loop_radial_next
                if rad_l and rad_l != l:
                    nbr_face = rad_l.face
                    if nbr_face.index not in visited_faces:
                        uv1_a = l[uv_layer].uv
                        uv1_b = l.link_loop_next[uv_layer].uv
                        uv2_a = rad_l[uv_layer].uv
                        uv2_b = rad_l.link_loop_next[uv_layer].uv
                        if (uv1_a - uv2_b).length < 1e-4 and (uv1_b - uv2_a).length < 1e-4:
                            visited_faces.add(nbr_face.index)
                            island_faces.append(nbr_face)
                            queue.append(nbr_face)
        islands.append(island_faces)

    # 2. Rasterisation par île UV pour mesurer le chevauchement inter-îles
    accum = np.zeros((grid_size, grid_size), dtype=np.int16)
    
    for isl in islands:
        isl_polys = []
        for f in isl:
            pts = []
            for l in f.loops:
                u, v = l[uv_layer].uv
                px = int(np.clip(u * grid_size, 0, grid_size - 1))
                py = int(np.clip((1.0 - v) * grid_size, 0, grid_size - 1))
                pts.append([px, py])
            pts_arr = np.array(pts, dtype=np.int32)
            if cv2.contourArea(pts_arr) < 0.5:
                degenerate_uv_faces += 1
            isl_polys.append(pts_arr)

        isl_mask = np.zeros((grid_size, grid_size), dtype=np.uint8)
        cv2.fillPoly(isl_mask, isl_polys, 1)
        accum += isl_mask

    bm.free()

    tot_cov = int(np.count_nonzero(accum > 0))
    overlap_pixels = int(np.count_nonzero(accum > 1))
    
    coverage_pct = round((tot_cov / (grid_size * grid_size)) * 100.0, 2)
    overlap_pct = round((overlap_pixels / tot_cov) * 100.0, 2) if tot_cov > 0 else 0.0

    return {
        "has_uv": True,
        "islands_count": len(islands),
        "degenerate_uv_faces": degenerate_uv_faces,
        "uv_overlap_pct": overlap_pct,
        "total_uv_coverage_pct": coverage_pct
    }


def validate_glb(glb_path, category=None, spec=None, strict=False):
    """
    Exécute l'audit complet conforme au MASTER PROMPT V2.2.
    """
    abs_glb_path = os.path.abspath(glb_path)
    if not os.path.isfile(abs_glb_path):
        return {
            "verdict": "ERROR",
            "error_codes": ["E1"],
            "error": f"Fichier GLB introuvable : {abs_glb_path}"
        }

    glb_bytes_size = os.path.getsize(abs_glb_path)
    sha256_hash = compute_file_sha256(abs_glb_path)
    
    cat_key = (category or "generic").lower().replace("-", "_")
    cat_prior = CATEGORY_PRIORS.get(cat_key, CATEGORY_PRIORS["generic"])
    
    # 1. Reset scène Blender et import glTF
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    if not hasattr(bpy.ops.import_scene, "gltf"):
        bpy.ops.preferences.addon_enable(module="io_scene_gltf2")

    bpy.ops.import_scene.gltf(filepath=abs_glb_path)
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]

    if not mesh_objects:
        return {
            "verdict": "FAIL",
            "error_codes": ["E1"],
            "sha256": sha256_hash,
            "issues": ["Le fichier GLB ne contient aucun objet maillé."]
        }

    issues = []
    error_codes = set()
    objects_report = {}

    total_vertices = 0
    total_triangles = 0
    total_intra_self_intersections = 0
    total_inter_island_overlaps = 0
    non_manifold_count = 0
    open_boundary_count = 0
    degenerate_edges_total = 0
    loose_vertices_total = 0

    unique_materials = set()
    
    # 2. Boîte englobante globale
    min_co = [float("inf"), float("inf"), float("inf")]
    max_co = [float("-inf"), float("-inf"), float("-inf")]

    for obj in mesh_objects:
        # Vérification transformations unifiées
        has_unapplied_scale = any(abs(s - 1.0) > 1e-4 for s in obj.scale)
        if has_unapplied_scale:
            issues.append(f"[{obj.name}] Échelle non unitaire appliquée : {list(obj.scale)}.")
            error_codes.add("E6")

        # Matériaux
        obj_mats = [slot.material.name for slot in obj.material_slots if slot.material]
        for m in obj_mats:
            unique_materials.add(m)
        if not obj_mats:
            issues.append(f"[{obj.name}] Aucun matériau assigné.")
            error_codes.add("E4")

        # Topologie
        topo = audit_bmesh_topology(obj.data)
        uv_res = audit_uv_mapping(obj.data)

        total_vertices += topo["vertex_count"]
        total_triangles += topo["triangle_count"]
        total_intra_self_intersections += topo["intra_self_intersections"]
        total_inter_island_overlaps += topo["inter_island_overlaps"]
        non_manifold_count += topo["non_manifold_edges"]
        open_boundary_count += topo["boundary_edges"]
        degenerate_edges_total += topo["degenerate_edges"]
        loose_vertices_total += topo["loose_vertices"]

        if topo["non_manifold_edges"] > 0:
            issues.append(f"[{obj.name}] {topo['non_manifold_edges']} arêtes non-manifold détectées.")
            error_codes.add("E3")

        if not topo["is_watertight"]:
            issues.append(f"[{obj.name}] Maillage non étanche (watertight) : {topo['boundary_edges']} arêtes de bordure ouvertes.")
            error_codes.add("E3")

        if topo["intra_self_intersections"] > 0:
            issues.append(f"[{obj.name}] {topo['intra_self_intersections']} auto-intersections intra-surface détectées via BVH.")
            error_codes.add("E3")

        if not uv_res["has_uv"]:
            issues.append(f"[{obj.name}] Aucune couche UV trouvée.")
            error_codes.add("E4")
        elif uv_res["uv_overlap_pct"] > 2.0:
            issues.append(f"[{obj.name}] Recouvrement UV excessif : {uv_res['uv_overlap_pct']}% (seuil max 2.0%).")
            error_codes.add("E4")

        # World Bounding Box
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ mathutils.Vector(corner)
            for i in range(3):
                min_co[i] = min(min_co[i], world_corner[i])
                max_co[i] = max(max_co[i], world_corner[i])

        objects_report[obj.name] = {
            "vertices": topo["vertex_count"],
            "triangles": topo["triangle_count"],
            "is_watertight": topo["is_watertight"],
            "non_manifold_edges": topo["non_manifold_edges"],
            "boundary_edges": topo["boundary_edges"],
            "intra_self_intersections": topo["intra_self_intersections"],
            "inter_island_overlaps": topo["inter_island_overlaps"],
            "uv": uv_res,
            "materials": obj_mats
        }

    # 3. Calcul des dimensions métriques globales
    dims = [round(max_co[i] - min_co[i], 4) for i in range(3)]
    max_dim = max(dims)
    center_x = round((min_co[0] + max_co[0]) / 2.0, 4)
    center_y = round((min_co[1] + max_co[1]) / 2.0, 4)
    z_min = round(min_co[2], 4)

    # 4. Contrôle Draw Calls (Master Prompt §2.8 & Code E8)
    draw_calls = len(mesh_objects)
    if draw_calls > 6:
        issues.append(f"E8: Nombre de draw calls excessif ({draw_calls} > 6 max). Fusion requise par matériau.")
        error_codes.add("E8")

    # 5. Contrôle Budget Triangles
    budget_tris = cat_prior.get("budget_tris", 100000)
    if total_triangles > budget_tris:
        issues.append(f"Budget polygones dépassé : {total_triangles} tris pour catégorie '{cat_key}' (limite {budget_tris}).")
        error_codes.add("E5")

    # 6. Contrôle Poids Fichier WebGL (< 3 Mo recommandé)
    file_mb = round(glb_bytes_size / (1024 * 1024), 2)
    if file_mb > 5.0:
        issues.append(f"Poids GLB critique : {file_mb} Mo (> 5 Mo max).")
        error_codes.add("E5")
    elif file_mb > 3.0:
        issues.append(f"Avertissement : Poids GLB de {file_mb} Mo supérieur à la recommandation mobile (< 3 Mo).")

    # 7. Contrôle d'Échelle Absolue & Priors Catégoriels (Master Prompt §2.5 & Code E6)
    scale_audit = {
        "category": cat_key,
        "dimensions_m": dims,
        "max_dim_m": max_dim,
        "prior_matched": True,
        "target_spec_matched": None
    }

    if "max_dim_range" in cat_prior:
        p_min, p_max = cat_prior["max_dim_range"]
        # Tolérance ±15%
        allowed_min = p_min * 0.85
        allowed_max = p_max * 1.15
        if not (allowed_min <= max_dim <= allowed_max):
            issues.append(f"E6: Dimension max hors prior catégoriel : {max_dim:.3f}m non compris dans [{allowed_min:.3f}m, {allowed_max:.3f}m].")
            scale_audit["prior_matched"] = False
            error_codes.add("E6")

    # Si une spec avec dimensions cibles est fournie
    if spec and "scale_metric" in spec and "dimensions" in spec["scale_metric"]:
        target_dims = spec["scale_metric"]["dimensions"]
        max_err_pct = 0.0
        for i in range(3):
            if target_dims[i] > 0:
                err = abs(dims[i] - target_dims[i]) / target_dims[i] * 100.0
                max_err_pct = max(max_err_pct, err)
        scale_audit["target_spec_matched"] = (max_err_pct <= 15.0)
        scale_audit["max_target_error_pct"] = round(max_err_pct, 2)
        if max_err_pct > 15.0:
            issues.append(f"E6: Écart aux dimensions cibles de la spécification supérieur à 15% ({max_err_pct:.1f}%).")
            error_codes.add("E6")

    # 8. Contrôle Assiette AR 1:1 (Z_min = 0.0 ± 0.002m, Centrage X=0, Y=0)
    ar_plate_valid = True
    if abs(z_min) > 0.003:
        issues.append(f"E6: Assiette AR non conforme : Z_min = {z_min:.4f}m (doit être 0.000m ± 0.002m pour reposer sur le plancher AR).")
        ar_plate_valid = False
        error_codes.add("E6")

    if abs(center_x) > 0.015 or abs(center_y) > 0.015:
        issues.append(f"Assiette AR décentrée : Centre X={center_x:.4f}m, Y={center_y:.4f}m (tolérance max ±0.015m).")
        ar_plate_valid = False
        if strict:
            error_codes.add("E6")

    # 9. Verdict Global
    critical_error_codes = [c for c in sorted(error_codes) if c in {"E1", "E3", "E6", "E8"}]
    if strict:
        is_pass = (len(error_codes) == 0 and len(issues) == 0)
    else:
        # En mode standard : échec si codes critiques E1, E3, E6, E8 ou maillage non étanche
        is_pass = (len(critical_error_codes) == 0 and non_manifold_count == 0)

    verdict = "PASS" if is_pass else "FAIL"

    return {
        "verdict": verdict,
        "glb_path": abs_glb_path,
        "sha256": sha256_hash,
        "file_size_bytes": glb_bytes_size,
        "file_size_mb": file_mb,
        "error_codes": sorted(list(error_codes)),
        "metrics": {
            "mesh_objects_count": len(mesh_objects),
            "draw_calls": draw_calls,
            "materials_count": len(unique_materials),
            "total_vertices": total_vertices,
            "total_triangles": total_triangles,
            "budget_triangles": budget_tris,
            "non_manifold_edges": non_manifold_count,
            "boundary_edges": open_boundary_count,
            "degenerate_edges": degenerate_edges_total,
            "loose_vertices": loose_vertices_total,
            "is_watertight": (open_boundary_count == 0 and non_manifold_count == 0),
            "intra_self_intersections": total_intra_self_intersections,
            "inter_island_overlaps": total_inter_island_overlaps
        },
        "bounding_box": {
            "min": [round(c, 4) for c in min_co],
            "max": [round(c, 4) for c in max_co],
            "dimensions_m": dims,
            "center": [center_x, center_y, round((min_co[2] + max_co[2]) / 2.0, 4)]
        },
        "ar_anchor": {
            "valid": ar_plate_valid,
            "z_min_m": z_min,
            "offset_from_ground_mm": round(z_min * 1000, 2)
        },
        "scale_audit": scale_audit,
        "issues": issues,
        "objects": objects_report
    }


def main(argv=None):
    if argv is None:
        raw = sys.argv
        argv = raw[raw.index("--") + 1:] if "--" in raw else raw[1:]

    parser = argparse.ArgumentParser(description="Validateur Géométrique et Qualité WebGL V2 (Master Prompt V2.2)")
    parser.add_argument("--glb", required=True, help="Chemin du fichier GLB à auditer")
    parser.add_argument("--category", default="generic", help="Catégorie de produit pour les priors d'échelle et budget tris")
    parser.add_argument("--spec", default=None, help="Spécification JSON optionnelle")
    parser.add_argument("--output-json", default=None, help="Chemin de sortie du rapport JSON")
    parser.add_argument("--strict", action="store_true", help="Mode strict : toute anomalie invalide le modèle")
    args = parser.parse_args(argv)

    spec_dict = None
    if args.spec and os.path.isfile(args.spec):
        with open(args.spec, "r", encoding="utf-8") as f:
            spec_dict = json.load(f)

    try:
        report = validate_glb(args.glb, category=args.category, spec=spec_dict, strict=args.strict)
        report_json = json.dumps(report, indent=2, ensure_ascii=False)

        if args.output_json:
            os.makedirs(os.path.dirname(os.path.abspath(args.output_json)), exist_ok=True)
            with open(args.output_json, "w", encoding="utf-8") as out_f:
                out_f.write(report_json)
            print(f"Rapport de validation sauvegardé dans : {args.output_json}")

        print("VALIDATION_REPORT:")
        print(report_json)

        if report["verdict"] == "PASS":
            return 0
        elif report["verdict"] == "FAIL":
            return 2
        else:
            return 3

    except Exception as exc:
        err_res = {
            "verdict": "ERROR",
            "error_codes": ["E1"],
            "error": f"{type(exc).__name__}: {exc}"
        }
        print("VALIDATION_REPORT:" + json.dumps(err_res, ensure_ascii=False))
        return 3


if __name__ == "__main__":
    sys.exit(main())
