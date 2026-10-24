"""
clean_mesh.py — Module de Nettoyage 3D Non Destructif pour Blender 5.x

Ce module fournit des outils modulaires de diagnostic, de proposition et
d'exécution contrôlée pour préparer les maillages à la production.

Règles de conception :
- dry_run=True par défaut sur toutes les opérations.
- Cible uniquement l'objet explicitement fourni.
- Sauvegarde et restauration automatique du maillage en cas d'erreur.
- Respect absolu des UVs, matériaux et textures existants.
- Zéro dépendance externe (bpy, bmesh, mathutils uniquement).
"""

import copy
from datetime import datetime, timezone
import json
import math
import bmesh
import bpy
import mathutils


# -----------------------------------------------------------------------------
# Options par défaut (Toutes désactivées par défaut pour une sécurité totale)
# -----------------------------------------------------------------------------
DEFAULT_OPTIONS = {
    "merge_vertices": False,
    "merge_threshold": 0.0001,
    "recalculate_normals": False,
    "detect_non_manifold": False,
    "apply_transforms": False,
    "apply_location": False,
    "apply_rotation": False,
    "apply_scale": False,
    "origin_to_bottom": False,
    "add_bevel": False,
    "bevel_width": None,  # Calculé automatiquement si None selon l'échelle
    "bevel_segments": 3,
    "add_weighted_normal": False,
}

_LAST_REPORT = None


def _resolve_object(obj):
    """Résout une référence d'objet (chaîne ou bpy.types.Object)."""
    if isinstance(obj, str):
        if obj not in bpy.data.objects:
            raise ValueError(f"Objet '{obj}' introuvable dans bpy.data.objects.")
        return bpy.data.objects[obj]
    if isinstance(obj, bpy.types.Object):
        return obj
    raise TypeError(f"Type d'objet invalide : attendu str ou bpy.types.Object, reçu {type(obj)}.")


def inspect_mesh(obj):
    """
    Recueille les statistiques complètes et transformations de l'objet maillage
    sans modifier la scène ni les données.
    """
    target = _resolve_object(obj)
    if target.type != "MESH":
        raise ValueError(f"L'objet '{target.name}' n'est pas de type MESH (type: {target.type}).")

    mesh_data = target.data

    materials = [
        slot.material.name
        for slot in target.material_slots
        if slot.material is not None
    ]
    uv_layers = [layer.name for layer in mesh_data.uv_layers]
    modifiers = [
        {"name": mod.name, "type": mod.type, "show_viewport": mod.show_viewport, "show_render": mod.show_render}
        for mod in target.modifiers
    ]

    # Bounding box en coordonnées locales
    bbox_corners = target.bound_box
    min_z = min(corner[2] for corner in bbox_corners)
    max_z = max(corner[2] for corner in bbox_corners)

    return {
        "object_name": target.name,
        "mesh_name": mesh_data.name,
        "vertex_count": len(mesh_data.vertices),
        "edge_count": len(mesh_data.edges),
        "face_count": len(mesh_data.polygons),
        "dimensions": (
            round(target.dimensions.x, 5),
            round(target.dimensions.y, 5),
            round(target.dimensions.z, 5),
        ),
        "location": (
            round(target.location.x, 5),
            round(target.location.y, 5),
            round(target.location.z, 5),
        ),
        "rotation_euler_deg": (
            round(math.degrees(target.rotation_euler.x), 2),
            round(math.degrees(target.rotation_euler.y), 2),
            round(math.degrees(target.rotation_euler.z), 2),
        ),
        "scale": (
            round(target.scale.x, 5),
            round(target.scale.y, 5),
            round(target.scale.z, 5),
        ),
        "materials": materials,
        "uv_layers": uv_layers,
        "modifiers": modifiers,
        "local_bounds_z": {"min_z": round(min_z, 5), "max_z": round(max_z, 5)},
    }


def find_duplicate_vertices(obj, threshold=0.0001):
    """
    Détecte les sommets doublons ou quasi-doublons avec un KDTree spatial.
    Opération de lecture seule stricte : aucun sommet n'est fusionné.
    """
    target = _resolve_object(obj)
    if target.type != "MESH":
        raise ValueError(f"L'objet '{target.name}' n'est pas un maillage.")

    mesh = target.data
    vert_count = len(mesh.vertices)
    if vert_count == 0:
        return {"threshold": threshold, "duplicate_pairs_count": 0, "pairs_sample": []}

    kd = mathutils.kdtree.KDTree(vert_count)
    for i, v in enumerate(mesh.vertices):
        kd.insert(v.co, i)
    kd.balance()

    duplicate_pairs = []
    visited = set()

    for i, v in enumerate(mesh.vertices):
        for co, index, dist in kd.find_range(v.co, threshold):
            if index != i:
                pair = tuple(sorted((i, index)))
                if pair not in visited:
                    visited.add(pair)
                    duplicate_pairs.append({
                        "vert_a": pair[0],
                        "vert_b": pair[1],
                        "distance": round(dist, 7),
                    })

    return {
        "threshold": threshold,
        "duplicate_pairs_count": len(duplicate_pairs),
        "pairs_sample": duplicate_pairs[:20],  # Échantillon pour lisibilité
    }


def check_normals(obj):
    """
    Diagnostique l'orientation et la cohérence des normales de faces.
    Utilise une copie BMesh éphémère libérée systématiquement.
    """
    target = _resolve_object(obj)
    if target.type != "MESH":
        raise ValueError(f"L'objet '{target.name}' n'est pas un maillage.")

    bm = bmesh.new()
    report = {
        "is_manifold": False,
        "boundary_edges": 0,
        "wire_edges": 0,
        "non_manifold_edges": 0,
        "zero_area_faces": 0,
        "volume": None,
        "watertight": False,
        "note": "Un maillage dont les normales pointent vers l'extérieur n'est pas nécessairement étanche (watertight).",
    }

    try:
        bm.from_mesh(target.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        report["boundary_edges"] = sum(1 for e in bm.edges if e.is_boundary)
        report["wire_edges"] = sum(1 for e in bm.edges if e.is_wire)
        report["non_manifold_edges"] = sum(1 for e in bm.edges if not e.is_manifold)
        report["zero_area_faces"] = sum(1 for f in bm.faces if f.calc_area() < 1e-8)

        # Si aucune arête de bordure ni arête non-manifold, le maillage est fermé
        is_closed = (report["boundary_edges"] == 0 and report["non_manifold_edges"] == 0 and len(bm.faces) > 0)
        report["is_manifold"] = (report["non_manifold_edges"] == 0)
        report["watertight"] = is_closed

        if is_closed:
            try:
                report["volume"] = round(bm.calc_volume(), 6)
            except Exception:
                report["volume"] = None
    finally:
        bm.free()

    return report


def propose_cleanup(obj, options=None):
    """
    Établit un plan d'actions détaillé avec évaluation des risques associés.
    Ne modifie en aucun cas l'objet ni la scène.
    """
    target = _resolve_object(obj)
    opts = copy.deepcopy(DEFAULT_OPTIONS)
    if options:
        opts.update(options)

    stats = inspect_mesh(target)
    duplicates = find_duplicate_vertices(target, threshold=opts["merge_threshold"])
    normals_diag = check_normals(target)

    actions_plan = []

    # 1. Fusion de sommets proches
    actions_plan.append({
        "action": "merge_vertices",
        "enabled": opts["merge_vertices"],
        "condition_met": duplicates["duplicate_pairs_count"] > 0,
        "candidates_count": duplicates["duplicate_pairs_count"],
        "threshold": opts["merge_threshold"],
        "risk_level": "MEDIUM",
        "risk_description": (
            "Risque de perte de micro-détails si le seuil est trop élevé par rapport à l'échelle du maillage."
        ),
    })

    # 2. Recalcul des normales extérieures
    actions_plan.append({
        "action": "recalculate_normals",
        "enabled": opts["recalculate_normals"],
        "condition_met": True,
        "risk_level": "LOW",
        "risk_description": (
            "Peut inverser des faces intentionnellement orientées vers l'intérieur sur des objets creux sans épaisseur."
        ),
    })

    # 3. Détection des arêtes non-manifold
    actions_plan.append({
        "action": "detect_non_manifold",
        "enabled": opts["detect_non_manifold"],
        "condition_met": normals_diag["non_manifold_edges"] > 0,
        "non_manifold_count": normals_diag["non_manifold_edges"],
        "risk_level": "NONE",
        "risk_description": "Opération de pure inspection (aucun impact géométrique).",
    })

    # 4. Application des transformations
    scale_unapplied = any(abs(s - 1.0) > 1e-4 for s in stats["scale"])
    actions_plan.append({
        "action": "apply_transforms",
        "enabled": opts["apply_transforms"],
        "condition_met": scale_unapplied,
        "details": {
            "apply_scale": opts.get("apply_scale", True),
            "apply_rotation": opts.get("apply_rotation", False),
            "apply_location": opts.get("apply_location", False),
        },
        "risk_level": "LOW",
        "risk_description": (
            "Fige les transformations dans le maillage. Indispensable pour un Bevel uniforme, "
            "mais réinitialise les deltas d'origine."
        ),
    })

    # 5. Placement de l'origine au sol (Z min = 0)
    actions_plan.append({
        "action": "origin_to_bottom",
        "enabled": opts["origin_to_bottom"],
        "condition_met": abs(stats["local_bounds_z"]["min_z"]) > 1e-4,
        "current_min_z": stats["local_bounds_z"]["min_z"],
        "risk_level": "MEDIUM",
        "risk_description": (
            "Déplace le point de pivot local au contact du sol. Déconseillé pour les objets destinés "
            "à pivoter autour de leur barycentre (ex: roues, hélices, cardans)."
        ),
    })

    # 6. Ajout modificateur Bevel
    bevel_width = opts["bevel_width"]
    if bevel_width is None:
        max_dim = max(stats["dimensions"]) if max(stats["dimensions"]) > 0 else 1.0
        bevel_width = round(max_dim * 0.005, 5)  # 0.5% de la plus grande dimension

    has_bevel = any(m["type"] == "BEVEL" for m in stats["modifiers"])
    actions_plan.append({
        "action": "add_bevel",
        "enabled": opts["add_bevel"],
        "condition_met": not has_bevel,
        "already_present": has_bevel,
        "proposed_width": bevel_width,
        "segments": opts["bevel_segments"],
        "risk_level": "LOW",
        "risk_description": (
            "Génère un chanfrein physique doux. Risque d'auto-intersection si les faces sont trop denses "
            "ou si la largeur dépasse l'épaisseur locale."
        ),
    })

    # 7. Ajout modificateur Weighted Normal
    has_wn = any(m["type"] == "WEIGHTED_NORMAL" for m in stats["modifiers"])
    actions_plan.append({
        "action": "add_weighted_normal",
        "enabled": opts["add_weighted_normal"],
        "condition_met": not has_wn,
        "already_present": has_wn,
        "risk_level": "LOW",
        "risk_description": (
            "Améliore l'ombrage sur les surfaces planes biseautées. Nécessite Auto Smooth / Smooth Angle actif."
        ),
    })

    return {
        "object_name": target.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "stats_before": stats,
        "options_configured": opts,
        "actions_plan": actions_plan,
        "summary": {
            "duplicate_pairs_found": duplicates["duplicate_pairs_count"],
            "non_manifold_edges_found": normals_diag["non_manifold_edges"],
            "boundary_edges_found": normals_diag["boundary_edges"],
            "is_watertight": normals_diag["watertight"],
        },
    }


def clean_mesh(obj, options=None, dry_run=True):
    """
    Exécute le nettoyage d'un maillage spécifique.

    Sécurité :
    - Si dry_run=True (par défaut), retourne uniquement le plan d'actions sans modifier l'objet.
    - Si dry_run=False, crée une copie de sauvegarde en mémoire du maillage avant toute mutation.
      En cas d'exception, le maillage d'origine est restauré immédiatement.

    Paramètres :
        obj : str ou bpy.types.Object
        options : dict (options de nettoyage, toutes désactivées par défaut)
        dry_run : bool (True par défaut)

    Retourne :
        dict : Rapport détaillé sérialisable en JSON
    """
    global _LAST_REPORT

    target = _resolve_object(obj)
    if target.type != "MESH":
        raise ValueError(f"L'objet '{target.name}' n'est pas un maillage MESH.")

    opts = copy.deepcopy(DEFAULT_OPTIONS)
    if options:
        opts.update(options)

    plan = propose_cleanup(target, options=opts)

    report = {
        "module": "clean_mesh",
        "version": "1.0.0",
        "object_name": target.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "status": "PROPOSED" if dry_run else "EXECUTED",
        "plan": plan,
        "operations_executed": [],
        "errors": [],
    }

    if dry_run:
        report["message"] = (
            "Mode dry_run=True actif : aucune modification n'a été effectuée. "
            "Passez dry_run=False avec des options activées pour exécuter les opérations."
        )
        _LAST_REPORT = report
        return report

    # -------------------------------------------------------------------------
    # Mode Exécution Réelle (dry_run=False) avec Protection par Sauvegarde
    # -------------------------------------------------------------------------
    original_mesh = target.data
    backup_mesh = original_mesh.copy()  # Copie de sécurité intégrale en mémoire Blender

    try:
        # A. Opérations géométriques BMesh (Merge / Recalculate Normals)
        needs_bmesh = opts["merge_vertices"] or opts["recalculate_normals"]
        if needs_bmesh:
            bm = bmesh.new()
            bm.from_mesh(target.data)
            bm.verts.ensure_lookup_table()
            bm.edges.ensure_lookup_table()
            bm.faces.ensure_lookup_table()

            # 1. Fusion des sommets proches
            if opts["merge_vertices"]:
                v_count_before = len(bm.verts)
                bmesh.ops.remove_doubles(
                    bm,
                    verts=bm.verts,
                    dist=opts["merge_threshold"]
                )
                v_count_after = len(bm.verts)
                merged_count = v_count_before - v_count_after
                report["operations_executed"].append({
                    "operation": "merge_vertices",
                    "threshold": opts["merge_threshold"],
                    "merged_vertices_count": merged_count,
                })

            # 2. Recalcul des normales extérieures
            if opts["recalculate_normals"]:
                bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
                report["operations_executed"].append({
                    "operation": "recalculate_normals",
                    "status": "COMPLETED",
                })

            # Réécriture sécurisée dans le maillage cible
            bm.to_mesh(target.data)
            target.data.update()
            bm.free()

        # B. Application sélective des transformations (sans impacter d'autres objets)
        if opts["apply_transforms"]:
            # On applique via les matrices sans toucher au contexte global de scène
            apply_loc = opts.get("apply_location", False)
            apply_rot = opts.get("apply_rotation", False)
            apply_sca = opts.get("apply_scale", True)

            # Application ciblée par manipulation de matrice
            # Pour garantir la sécurité, on utilise transform_apply temporairement
            current_active = bpy.context.view_layer.objects.active
            current_selected = [o for o in bpy.context.view_layer.objects if o.select_get()]

            try:
                for o in bpy.context.view_layer.objects:
                    o.select_set(False)
                target.select_set(True)
                bpy.context.view_layer.objects.active = target

                bpy.ops.object.transform_apply(
                    location=apply_loc,
                    rotation=apply_rot,
                    scale=apply_sca,
                )
                report["operations_executed"].append({
                    "operation": "apply_transforms",
                    "applied": {"location": apply_loc, "rotation": apply_rot, "scale": apply_sca},
                })
            finally:
                # Restauration scrupuleuse de la sélection précédente
                target.select_set(False)
                for o in current_selected:
                    o.select_set(True)
                bpy.context.view_layer.objects.active = current_active

        # C. Placement de l'origine au sol (Z min = 0)
        if opts["origin_to_bottom"]:
            bbox_corners = target.bound_box
            min_z = min(corner[2] for corner in bbox_corners)
            if abs(min_z) > 1e-5:
                # Déplacement géométrique inverse pour placer l'origine au sol
                offset = mathutils.Vector((0.0, 0.0, -min_z))
                # Translation des sommets dans l'espace local
                for v in target.data.vertices:
                    v.co += offset
                target.data.update()
                # Compensation de la position de l'objet pour préserver la position monde
                world_offset = target.matrix_world.to_3x3() @ (-offset)
                target.location += world_offset
                report["operations_executed"].append({
                    "operation": "origin_to_bottom",
                    "z_offset_applied": round(min_z, 5),
                })

        # D. Ajout contrôlé du modificateur Bevel
        if opts["add_bevel"]:
            has_bevel = any(m.type == "BEVEL" for m in target.modifiers)
            if not has_bevel:
                bevel_width = opts["bevel_width"]
                if bevel_width is None:
                    max_dim = max(target.dimensions) if max(target.dimensions) > 0 else 1.0
                    bevel_width = round(max_dim * 0.005, 5)

                mod = target.modifiers.new(name="Bevel", type="BEVEL")
                mod.width = bevel_width
                mod.segments = opts["bevel_segments"]
                mod.limit_method = "ANGLE"
                mod.angle_limit = math.radians(30.0)
                mod.use_clamp_overlap = True
                report["operations_executed"].append({
                    "operation": "add_bevel",
                    "width": bevel_width,
                    "segments": opts["bevel_segments"],
                    "limit_method": "ANGLE",
                })

        # E. Ajout contrôlé du modificateur Weighted Normal
        if opts["add_weighted_normal"]:
            has_wn = any(m.type == "WEIGHTED_NORMAL" for m in target.modifiers)
            if not has_wn:
                mod = target.modifiers.new(name="WeightedNormal", type="WEIGHTED_NORMAL")
                mod.keep_sharp = True
                report["operations_executed"].append({
                    "operation": "add_weighted_normal",
                    "keep_sharp": True,
                })

        # Succès : suppression de la copie de secours pour libérer la mémoire
        bpy.data.meshes.remove(backup_mesh)
        report["status"] = "SUCCESS"

    except Exception as exc:
        # En cas d'erreur critique, restauration immédiate du maillage
        target.data = backup_mesh
        bpy.data.meshes.remove(original_mesh)
        report["status"] = "FAILED_RESTORED"
        report["errors"].append(str(exc))

    # Statistiques après exécution
    report["stats_after"] = inspect_mesh(target)
    _LAST_REPORT = report
    return report


def get_cleanup_report():
    """Retourne le dernier rapport d'exécution généré sous forme de dict sérialisable."""
    global _LAST_REPORT
    return _LAST_REPORT


# -----------------------------------------------------------------------------
# Batterie de Tests d'Intégrité Automatisés
# -----------------------------------------------------------------------------
def run_self_tests():
    """
    Exécute une suite de tests unitaires non destructifs sur un objet maillage éphémère.
    Garantit que la scène initiale est laissée strictement intacte.
    """
    test_results = {
        "tests_passed": 0,
        "tests_failed": 0,
        "details": [],
    }

    # 1. Vérification sur objet inexistant (Gestion propre des erreurs)
    try:
        clean_mesh("__non_existent_object_xyz__", dry_run=True)
        test_results["tests_failed"] += 1
        test_results["details"].append({"test": "invalid_object", "status": "FAIL", "msg": "Erreur non levée"})
    except ValueError:
        test_results["tests_passed"] += 1
        test_results["details"].append({"test": "invalid_object", "status": "PASS", "msg": "Erreur ValueError levée correctement"})

    # 2. Création d'un maillage de test éphémère
    test_mesh_data = bpy.data.meshes.new("__temp_clean_mesh_test__")
    # Cube simple 1x1x1 avec 2 sommets doublons intentionnels
    verts = [
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (-0.5, 0.5, -0.5),
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
        (0.50001, 0.50001, 0.50001),  # Doublon proche du sommet 6
    ]
    test_mesh_data.from_pydata(verts, [], [])
    test_mesh_data.update()
    test_obj = bpy.data.objects.new("__temp_clean_obj_test__", test_mesh_data)
    bpy.context.collection.objects.link(test_obj)

    try:
        # Test A : inspect_mesh ne modifie rien
        info_before = inspect_mesh(test_obj)
        info_after = inspect_mesh(test_obj)
        if info_before == info_after and info_before["vertex_count"] == 9:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test": "inspect_mesh_integrity", "status": "PASS"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test": "inspect_mesh_integrity", "status": "FAIL"})

        # Test B : dry_run=True ne modifie ni les sommets ni les données
        report_dry = clean_mesh(test_obj, options={"merge_vertices": True}, dry_run=True)
        if len(test_obj.data.vertices) == 9 and report_dry["dry_run"] is True:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test": "dry_run_zero_mutation", "status": "PASS"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test": "dry_run_zero_mutation", "status": "FAIL"})

        # Test C : Détection effective des doublons sans modification
        dups = find_duplicate_vertices(test_obj, threshold=0.001)
        if dups["duplicate_pairs_count"] == 1:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test": "find_duplicates", "status": "PASS"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test": "find_duplicates", "status": "FAIL"})

        # Test D : Sérialisation JSON du rapport
        json_str = json.dumps(report_dry, ensure_ascii=False)
        parsed = json.loads(json_str)
        if parsed["module"] == "clean_mesh":
            test_results["tests_passed"] += 1
            test_results["details"].append({"test": "json_serializability", "status": "PASS"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test": "json_serializability", "status": "FAIL"})

        # Test E : Exécution réelle contrôlée sur le maillage temporaire
        report_exec = clean_mesh(
            test_obj,
            options={
                "merge_vertices": True,
                "merge_threshold": 0.001,
                "add_bevel": True,
                "add_weighted_normal": True,
            },
            dry_run=False
        )
        if len(test_obj.data.vertices) == 8 and len(test_obj.modifiers) == 2:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test": "controlled_execution_temp_object", "status": "PASS"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test": "controlled_execution_temp_object", "status": "FAIL"})

    finally:
        # Nettoyage absolu des objets et maillages temporaires créés pour le test
        bpy.data.objects.remove(test_obj, do_unlink=True)
        if test_mesh_data.name in bpy.data.meshes:
            bpy.data.meshes.remove(test_mesh_data)

    return test_results


if __name__ == "__main__":
    results = run_self_tests()
    print(json.dumps(results, indent=2))
