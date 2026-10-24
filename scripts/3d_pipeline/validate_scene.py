"""
validate_scene.py — Validateur 3D Non Destructif pour Blender 5.x / Python API

Ce module inspecte la scène Blender active sans jamais la modifier.
Il produit un rapport technique structuré (dictionnaire Python et JSON)
analysant l'inventaire des objets, l'intégrité géométrique, les transformations,
les matériaux et les couches UV.

Compatibilité : Blender 4.x / 5.x
Auteur : Pipeline Antigravity Image-to-3D
"""

import json
import math
from datetime import datetime, timezone
import bpy
import bmesh


def _inspect_mesh_geometry(mesh_data):
    """
    Analyse géométrique non destructive sur une copie BMesh en mémoire.
    Garantit la libération systématique du BMesh temporaire.
    Ne modifie en aucun cas mesh_data.
    """
    bm = bmesh.new()
    stats = {
        "is_empty": False,
        "vertex_count": 0,
        "edge_count": 0,
        "face_count": 0,
        "quad_count": 0,
        "tri_count": 0,
        "ngon_count": 0,
        "loose_vert_count": 0,
        "degenerate_edge_count": 0,
        "boundary_edge_count": 0,
        "wire_edge_count": 0,
        "non_manifold_edge_count": 0,
    }

    try:
        bm.from_mesh(mesh_data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        stats["vertex_count"] = len(bm.verts)
        stats["edge_count"] = len(bm.edges)
        stats["face_count"] = len(bm.faces)

        if stats["vertex_count"] == 0 or stats["face_count"] == 0:
            stats["is_empty"] = True
            return stats

        # Polygones : quads, tris, ngons
        for f in bm.faces:
            n_verts = len(f.verts)
            if n_verts == 4:
                stats["quad_count"] += 1
            elif n_verts == 3:
                stats["tri_count"] += 1
            else:
                stats["ngon_count"] += 1

        # Sommets orphelins (sans aucune arête connectée)
        stats["loose_vert_count"] = sum(1 for v in bm.verts if not v.link_edges)

        # Arêtes dégénérées (longueur quasi nulle < 1e-6m)
        stats["degenerate_edge_count"] = sum(
            1 for e in bm.edges if e.calc_length() < 1e-6
        )

        # Topologie des arêtes
        for e in bm.edges:
            if e.is_boundary:
                stats["boundary_edge_count"] += 1
            if e.is_wire:
                stats["wire_edge_count"] += 1
            if not e.is_manifold:
                stats["non_manifold_edge_count"] += 1

    finally:
        # Libération obligatoire de la ressource temporaire
        bm.free()

    return stats


def validate_scene(scene=None, print_json=True):
    """
    Point d'entrée principal du validateur de scène.

    Paramètres :
        scene : bpy.types.Scene (optionnel, utilise bpy.context.scene par défaut)
        print_json : bool (si True, affiche le JSON formaté sur stdout)

    Retourne :
        dict : Rapport complet de validation
    """
    if scene is None:
        scene = bpy.context.scene

    timestamp = datetime.now(timezone.utc).isoformat()
    blender_version = bpy.app.version_string

    objects_by_type = {
        "MESH": [],
        "CAMERA": [],
        "LIGHT": [],
        "CURVE": [],
        "OTHER": [],
    }

    for obj in scene.objects:
        t = obj.type
        if t in objects_by_type:
            objects_by_type[t].append(obj)
        else:
            objects_by_type["OTHER"].append(obj)

    issues = []
    inventory = []

    # Analyse détaillée des maillages
    for obj in objects_by_type["MESH"]:
        mesh_data = obj.data

        # Dimensions & Transformations (sans modification)
        dim = (
            round(obj.dimensions.x, 4),
            round(obj.dimensions.y, 4),
            round(obj.dimensions.z, 4),
        )
        loc = (
            round(obj.location.x, 4),
            round(obj.location.y, 4),
            round(obj.location.z, 4),
        )
        rot_deg = (
            round(math.degrees(obj.rotation_euler.x), 2),
            round(math.degrees(obj.rotation_euler.y), 2),
            round(math.degrees(obj.rotation_euler.z), 2),
        )
        scale = (
            round(obj.scale.x, 4),
            round(obj.scale.y, 4),
            round(obj.scale.z, 4),
        )

        # Matériaux
        materials = [
            slot.material.name
            for slot in obj.material_slots
            if slot.material is not None
        ]

        # Couches UV
        uv_layers = [layer.name for layer in mesh_data.uv_layers]

        # Modificateurs
        modifiers = [
            {
                "name": mod.name,
                "type": mod.type,
                "show_viewport": mod.show_viewport,
                "show_render": mod.show_render,
            }
            for mod in obj.modifiers
        ]

        # Analyse BMesh isolée
        geo_stats = _inspect_mesh_geometry(mesh_data)

        # Visibilité
        visibility = {
            "hide_viewport": obj.hide_viewport,
            "hide_render": obj.hide_render,
            "hide_get": obj.hide_get(),
        }

        mesh_entry = {
            "name": obj.name,
            "type": "MESH",
            "counts": {
                "vertices": geo_stats["vertex_count"],
                "edges": geo_stats["edge_count"],
                "faces": geo_stats["face_count"],
                "quads": geo_stats["quad_count"],
                "tris": geo_stats["tri_count"],
                "ngons": geo_stats["ngon_count"],
            },
            "transforms": {
                "dimensions": dim,
                "location": loc,
                "rotation_euler_deg": rot_deg,
                "scale": scale,
            },
            "materials": materials,
            "uv_layers": uv_layers,
            "modifiers": modifiers,
            "visibility": visibility,
        }
        inventory.append(mesh_entry)

        # ---------------------------------------------------------------------
        # Contrôles Géométriques & Détection des Anomalies
        # ---------------------------------------------------------------------

        # 1. Maillage vide
        if geo_stats["is_empty"]:
            issues.append(
                {
                    "severity": "ERROR",
                    "object": obj.name,
                    "code": "EMPTY_MESH",
                    "message": "Le maillage ne contient aucun sommet ou aucune face.",
                    "recommendation": "Supprimer l'objet vide ou assigner des données géométriques valides.",
                }
            )

        # 2. Dimensions nulles ou quasi nulles
        if any(d < 1e-5 for d in (obj.dimensions.x, obj.dimensions.y, obj.dimensions.z)):
            issues.append(
                {
                    "severity": "ERROR",
                    "object": obj.name,
                    "code": "FLAT_OR_ZERO_DIMENSIONS",
                    "message": f"Une ou plusieurs dimensions sont nulles ou quasi nulles : {dim}.",
                    "recommendation": "Vérifier le volume de l'objet pour s'assurer qu'il s'agit bien d'un objet tridimensionnel.",
                }
            )

        # 3. Échelle négative
        if any(s < 0 for s in (obj.scale.x, obj.scale.y, obj.scale.z)):
            issues.append(
                {
                    "severity": "ERROR",
                    "object": obj.name,
                    "code": "NEGATIVE_SCALE",
                    "message": f"L'échelle contient une valeur négative : {scale}. Risque d'inversion des normales.",
                    "recommendation": "Appliquer l'échelle (Ctrl+A > Scale) et recalculer les normales extérieures.",
                }
            )

        # 4. Arêtes non-manifold critiques (filaires ou multi-surfaces)
        if geo_stats["wire_edge_count"] > 0:
            issues.append(
                {
                    "severity": "ERROR",
                    "object": obj.name,
                    "code": "WIRE_EDGES_DETECTED",
                    "message": f"{geo_stats['wire_edge_count']} arêtes filaires (sans faces) détectées.",
                    "recommendation": "Nettoyer les arêtes isolées avec bmesh / Clean Up > Delete Loose.",
                }
            )

        if geo_stats["non_manifold_edge_count"] > geo_stats["boundary_edge_count"]:
            multi_fan = (
                geo_stats["non_manifold_edge_count"] - geo_stats["boundary_edge_count"]
            )
            issues.append(
                {
                    "severity": "ERROR",
                    "object": obj.name,
                    "code": "NON_MANIFOLD_MULTI_FAN",
                    "message": f"{multi_fan} arêtes partagées par plus de 2 faces (non-manifold critique).",
                    "recommendation": "Séparer ou supprimer les faces intérieures en T pour assurer une variété 2D propre.",
                }
            )

        # 5. Avertissements de topologie (WARNING)
        if geo_stats["loose_vert_count"] > 0:
            issues.append(
                {
                    "severity": "WARNING",
                    "object": obj.name,
                    "code": "LOOSE_VERTICES",
                    "message": f"{geo_stats['loose_vert_count']} sommets orphelins détectés.",
                    "recommendation": "Exécuter Clean Up > Delete Loose Vertices.",
                }
            )

        if geo_stats["degenerate_edge_count"] > 0:
            issues.append(
                {
                    "severity": "WARNING",
                    "object": obj.name,
                    "code": "DEGENERATE_EDGES",
                    "message": f"{geo_stats['degenerate_edge_count']} arêtes de longueur quasi nulle (< 1e-6 m).",
                    "recommendation": "Fusionner par distance (Merge By Distance) avec un seuil de 0.0001 m.",
                }
            )

        if geo_stats["boundary_edge_count"] > 0:
            issues.append(
                {
                    "severity": "WARNING",
                    "object": obj.name,
                    "code": "OPEN_BOUNDARY_EDGES",
                    "message": f"{geo_stats['boundary_edge_count']} arêtes de bordure (maillage ouvert non étanche).",
                    "recommendation": "Fermer les trous si un volume solide et étanche (watertight) est requis.",
                }
            )

        # 6. Échelle non normalisée (WARNING)
        if any(abs(s - 1.0) > 1e-4 for s in (obj.scale.x, obj.scale.y, obj.scale.z)):
            issues.append(
                {
                    "severity": "WARNING",
                    "object": obj.name,
                    "code": "UNAPPLIED_SCALE",
                    "message": f"L'échelle n'est pas appliquée à (1.0, 1.0, 1.0) : {scale}.",
                    "recommendation": "Appliquer l'échelle (Ctrl+A > Scale) avant l'export pour garantir des biseaux et textures homogènes.",
                }
            )

        # 7. Absence de matériau (WARNING)
        if len(materials) == 0:
            issues.append(
                {
                    "severity": "WARNING",
                    "object": obj.name,
                    "code": "NO_MATERIAL_ASSIGNED",
                    "message": "Aucun matériau n'est assigné à ce maillage.",
                    "recommendation": "Créer et assigner un matériau Principled BSDF compatible glTF.",
                }
            )

        # 8. Absence de couche UV (WARNING)
        if len(uv_layers) == 0:
            issues.append(
                {
                    "severity": "WARNING",
                    "object": obj.name,
                    "code": "NO_UV_LAYER",
                    "message": "Aucune carte UV n'est présente sur ce maillage.",
                    "recommendation": "Déplier le maillage (UV Unwrap) pour permettre l'application de textures PBR.",
                }
            )

        # 9. Présence de modificateurs non appliqués (INFO)
        if len(modifiers) > 0:
            mod_names = ", ".join(m["name"] for m in modifiers)
            issues.append(
                {
                    "severity": "INFO",
                    "object": obj.name,
                    "code": "MODIFIERS_PRESENT",
                    "message": f"{len(modifiers)} modificateur(s) présent(s) : {mod_names}.",
                    "recommendation": "Vérifier que l'exporteur applique automatiquement les modificateurs ou les figer au besoin.",
                }
            )

    # Récapitulatif des autres types
    for cat in ["CAMERA", "LIGHT", "CURVE", "OTHER"]:
        for obj in objects_by_type[cat]:
            inventory.append(
                {
                    "name": obj.name,
                    "type": cat,
                    "location": (
                        round(obj.location.x, 4),
                        round(obj.location.y, 4),
                        round(obj.location.z, 4),
                    ),
                }
            )

    # Décompte des sévérités
    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    warning_count = sum(1 for i in issues if i["severity"] == "WARNING")
    info_count = sum(1 for i in issues if i["severity"] == "INFO")

    status = "PASS" if error_count == 0 else "FAIL"

    report = {
        "validator_version": "1.0.0",
        "blender_version": blender_version,
        "timestamp": timestamp,
        "scene_name": scene.name,
        "summary": {
            "total_objects": len(scene.objects),
            "mesh_count": len(objects_by_type["MESH"]),
            "camera_count": len(objects_by_type["CAMERA"]),
            "light_count": len(objects_by_type["LIGHT"]),
            "curve_count": len(objects_by_type["CURVE"]),
            "other_count": len(objects_by_type["OTHER"]),
            "error_count": error_count,
            "warning_count": warning_count,
            "info_count": info_count,
            "status": status,
        },
        "inventory": inventory,
        "issues": issues,
        "checks_performed": [
            "scene_inventory_by_type",
            "mesh_empty_detection",
            "mesh_dimensions_zero_or_negative",
            "mesh_negative_scale",
            "mesh_wire_and_non_manifold_edges",
            "mesh_loose_vertices",
            "mesh_degenerate_edges",
            "mesh_open_boundary_edges",
            "mesh_unapplied_scale",
            "mesh_missing_materials",
            "mesh_missing_uv_layers",
            "mesh_modifier_inventory",
        ],
        "checks_not_performed": [
            "texture_bitmap_resolution_on_disk",
            "uv_overlapping_island_intersection",
            "watertightness_self_intersection_boolean",
            "bone_weight_normalization",
        ],
    }

    if print_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return report


if __name__ == "__main__":
    validate_scene(print_json=True)
