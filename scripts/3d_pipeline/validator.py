"""
validator.py — Moteur de Validation Géométrique et Audit Qualité pour Blender 5.x
Intègre les règles de vérification non destructives et produit un diagnostic unifié.
"""

import sys
import os
import mathutils
import bpy
import bmesh

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# validate_scene.py ships beside this validator in scripts/3d_pipeline.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validate_scene


def validate_model_quality(mesh_objects, expected_dims=None, tolerance_pct=5.0):
    """
    Exécute un audit qualité BMesh complet sur une liste d'objets maillés.
    Retourne un dictionnaire structuré et un verdict binaire PASS / FAIL.
    """
    results = {
        "verdict": "PASS",
        "objects_count": len(mesh_objects),
        "total_base_vertices": 0,
        "total_base_faces": 0,
        "total_evaluated_vertices": 0,
        "total_evaluated_triangles": 0,
        "issues": [],
        "objects_audit": {}
    }

    depsgraph = bpy.context.evaluated_depsgraph_get()

    min_co = [float("inf"), float("inf"), float("inf")]
    max_co = [float("-inf"), float("-inf"), float("-inf")]

    for obj in mesh_objects:
        obj_name = obj.name
        mesh = obj.data

        # 1. Vérification BMesh non destructive
        stats = validate_scene._inspect_mesh_geometry(mesh)
        base_v = stats["vertex_count"]
        base_f = stats["face_count"]

        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh()
        eval_v = len(eval_mesh.vertices)
        eval_t = sum(len(p.vertices) - 2 for p in eval_mesh.polygons)

        results["total_base_vertices"] += base_v
        results["total_base_faces"] += base_f
        results["total_evaluated_vertices"] += eval_v
        results["total_evaluated_triangles"] += eval_t

        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ mathutils.Vector(corner)
            for i in range(3):
                min_co[i] = min(min_co[i], world_corner[i])
                max_co[i] = max(max_co[i], world_corner[i])

        # Contrôle des transformations non appliquées
        has_unapplied_scale = any(abs(s - 1.0) > 1e-4 for s in obj.scale)

        # Contrôle des matériaux
        has_material = len(obj.material_slots) > 0 and obj.material_slots[0].material is not None

        # Contrôle des UVs
        has_uv = len(mesh.uv_layers) > 0

        obj_res = {
            "base_verts": base_v,
            "base_faces": base_f,
            "eval_verts": eval_v,
            "eval_triangles": eval_t,
            "non_manifold_edges": stats["non_manifold_edge_count"],
            "degenerate_edges": stats["degenerate_edge_count"],
            "loose_vertices": stats["loose_vert_count"],
            "has_unapplied_scale": has_unapplied_scale,
            "has_material": has_material,
            "has_uv": has_uv
        }
        results["objects_audit"][obj_name] = obj_res

        # Détection d'anomalies critiques
        if stats["non_manifold_edge_count"] > 0:
            results["issues"].append(f"[{obj_name}] {stats['non_manifold_edge_count']} arêtes non-manifold détectées.")
            results["verdict"] = "FAIL"
        if stats["degenerate_edge_count"] > 0:
            results["issues"].append(f"[{obj_name}] {stats['degenerate_edge_count']} arêtes dégénérées.")
            results["verdict"] = "FAIL"
        if has_unapplied_scale:
            results["issues"].append(f"[{obj_name}] Échelle non unitaire : {list(obj.scale)}.")
            results["verdict"] = "FAIL"
        if not has_material:
            results["issues"].append(f"[{obj_name}] Aucun matériau assigné.")
            results["verdict"] = "FAIL"
        if not has_uv:
            results["issues"].append(f"[{obj_name}] Aucune couche UV trouvée.")
            results["verdict"] = "FAIL"

        eval_obj.to_mesh_clear()

    dims = [round(max_co[i] - min_co[i], 6) for i in range(3)]
    results["bounding_box"] = {
        "min": [round(c, 6) for c in min_co],
        "max": [round(c, 6) for c in max_co],
        "dimensions": dims
    }

    # Vérification dimensionnelle si spécifiée
    if expected_dims:
        results["dimension_check"] = {}
        for i, axis in enumerate(["dx", "dy", "dz"]):
            target = expected_dims[i]
            actual = dims[i]
            err_pct = abs(actual - target) / target * 100.0 if target > 0 else 0.0
            match = err_pct <= tolerance_pct
            results["dimension_check"][axis] = {
                "target": target,
                "actual": actual,
                "error_pct": round(err_pct, 2),
                "match": match
            }
            if not match:
                results["issues"].append(f"Écart dimensionnel sur {axis}: {actual:.4f}m vs cible {target:.4f}m ({err_pct:.1f}% > {tolerance_pct}%).")
                results["verdict"] = "FAIL"

    return results

def main(argv=None):
    """Importe un GLB dans Blender, exécute l'audit et retourne un code fiable."""
    import argparse
    import json

    if argv is None:
        raw_argv = sys.argv
        argv = raw_argv[raw_argv.index("--") + 1:] if "--" in raw_argv else raw_argv[1:]

    parser = argparse.ArgumentParser(description="Valide la géométrie et l'export d'un fichier GLB.")
    parser.add_argument("--glb", required=True, help="Chemin du fichier GLB à contrôler")
    parser.add_argument("--spec", required=True, help="Spécification JSON de référence")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.glb):
        parser.error(f"Fichier GLB introuvable: {args.glb}")
    if not os.path.isfile(args.spec):
        parser.error(f"Spécification introuvable: {args.spec}")

    try:
        with open(args.spec, "r", encoding="utf-8") as spec_file:
            spec = json.load(spec_file)

        # Exclude Blender's startup cube and any other pre-existing scene objects.
        for obj in list(bpy.context.scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

        # Blender's glTF importer is an operator registered by the bundled addon.
        if not hasattr(bpy.ops.import_scene, "gltf"):
            bpy.ops.preferences.addon_enable(module="io_scene_gltf2")
        bpy.ops.import_scene.gltf(filepath=os.path.abspath(args.glb))

        mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
        if not mesh_objects:
            raise RuntimeError("Le GLB ne contient aucun objet maillé.")

        expected_dims = spec.get("scale_metric", {}).get("dimensions")
        report = validate_model_quality(mesh_objects, expected_dims=expected_dims)
        report["glb_path"] = os.path.abspath(args.glb)
        report["glb_bytes"] = os.path.getsize(args.glb)
        report["objects"] = [obj.name for obj in mesh_objects]
        print("VALIDATION_RESULT:" + json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report["verdict"] == "PASS" else 2
    except Exception as exc:
        failure = {
            "verdict": "ERROR",
            "glb_path": os.path.abspath(args.glb),
            "error": f"{type(exc).__name__}: {exc}",
        }
        print("VALIDATION_RESULT:" + json.dumps(failure, ensure_ascii=False, sort_keys=True))
        return 3


if __name__ == "__main__":
    sys.exit(main())
