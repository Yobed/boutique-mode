"""
orchestrator.py — Orchestrateur Central du Pipeline Générique Image-vers-3D
Lit une spécification déclarative, assemble le modèle, valide le maillage,
réalise les rendus studio et exporte le livrable en totale isolation.
"""

import argparse
import json
import os
import sys
import bpy

# Ajout du dossier pipeline au sys.path
PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if PIPELINE_DIR not in sys.path:
    sys.path.append(PIPELINE_DIR)

from analyzer import validate_and_load_spec
from materials import get_or_create_material
import builder
import studio
import validator
import exporter


def run_pipeline(spec_path, output_dir, export_glb=True, render_previews=True):
    print(f"=== DÉBUT D'EXÉCUTION DU PIPELINE GÉNÉRIQUE ===")
    print(f"Spécification : {spec_path}")
    print(f"Dossier de sortie : {output_dir}")

    # 1. Validation de la spécification
    spec = validate_and_load_spec(spec_path)
    object_id = spec["object_id"]
    object_name = spec.get("object_name", object_id)
    os.makedirs(output_dir, exist_ok=True)

    # 2. Préparation d'une scène Blender propre et isolée
    scene_name = f"Scene_{object_id}"
    if scene_name in bpy.data.scenes:
        scene = bpy.data.scenes[scene_name]
        for obj in list(scene.collection.objects):
            scene.collection.objects.unlink(obj)
            if obj.users == 0:
                bpy.data.objects.remove(obj)
    else:
        scene = bpy.data.scenes.new(scene_name)
    bpy.context.window.scene = scene

    # 3. Création des matériaux déclarés
    mats_decl = spec.get("materials", {})
    for mat_name, mat_def in mats_decl.items():
        preset = mat_def.get("preset")
        custom = mat_def.get("custom")
        get_or_create_material(mat_name, preset_key=preset, custom_params=custom)
        print(f"Matériau préparé : {mat_name} (preset={preset})")

    # 4. Assemblage géométrique composant par composant
    created_mesh_objects = []

    for comp in spec["components"]:
        c_name = comp["name"]
        c_prim = comp["primitive"]
        c_mat = comp.get("material")
        c_loc = tuple(comp.get("location", (0, 0, 0)))
        c_rot = tuple(comp.get("rotation", (0, 0, 0)))

        obj = None
        if c_prim == "rounded_box":
            dims = tuple(comp["dimensions"])
            cr = comp.get("corner_radius", 0.01)
            taper = comp.get("taper_ratio", 1.0)
            bev = comp.get("bevel_width", 0.002)
            obj = builder.build_rounded_box(scene, c_name, dims, corner_radius=cr, taper_ratio=taper, bevel_width=bev, material_name=c_mat, location=c_loc, rotation=c_rot)

        elif c_prim == "lathe":
            profile = [tuple(p) for p in comp["profile_points"]]
            n_seg = comp.get("segments", 32)
            is_hol = comp.get("is_hollow", False)
            wall_t = comp.get("wall_thickness", 0.004)
            bev = comp.get("bevel_width", None)
            obj = builder.build_lathe(scene, c_name, profile, n_segments=n_seg, is_hollow=is_hol, wall_thickness=wall_t, bevel_width=bev, material_name=c_mat, location=c_loc)

        elif c_prim == "cylinder":
            rt = comp.get("radius_top", 0.02)
            rb = comp.get("radius_bottom", 0.02)
            h = comp.get("height", 0.05)
            n_seg = comp.get("segments", 24)
            bev = comp.get("bevel_width", None)
            obj = builder.build_cylinder(scene, c_name, rt, rb, h, n_segments=n_seg, bevel_width=bev, material_name=c_mat, location=c_loc, rotation=c_rot)

        elif c_prim == "curved_sweep":
            path = [tuple(p) for p in comp["path_points"]]
            rad = comp.get("radius", 0.005)
            n_seg = comp.get("segments", 16)
            obj = builder.build_curved_sweep(scene, c_name, path, radius=rad, n_segments=n_seg, material_name=c_mat, location=c_loc)

        elif c_prim == "ring_collar":
            re = comp["radius_ext"]
            ri = comp["radius_int"]
            h = comp.get("height", 0.005)
            n_seg = comp.get("segments", 32)
            bev = comp.get("bevel_width", 0.0004)
            obj = builder.build_ring_collar(scene, c_name, re, ri, h, n_segments=n_seg, bevel_width=bev, material_name=c_mat, location=c_loc, rotation=c_rot)

        else:
            print(f"ATTENTION : Primitive inconnue '{c_prim}' pour le composant '{c_name}'")

        if obj:
            created_mesh_objects.append(obj)
            print(f"Composant créé : {c_name} (type={c_prim}, verts={len(obj.data.vertices)}, faces={len(obj.data.polygons)})")

    # 5. Validation géométrique rigoureuse
    expected_dims = spec.get("scale_metric", {}).get("dimensions")
    val_report = validator.validate_model_quality(created_mesh_objects, expected_dims=expected_dims)

    report_path = os.path.join(output_dir, f"{object_id}_validation.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(val_report, f, indent=2)

    print(f"Validation Géométrique : {val_report['verdict']} (Issues: {len(val_report['issues'])})")
    for issue in val_report["issues"]:
        print(f"  - {issue}")

    # 6. Éclairage Studio & Rendus de Contrôle
    render_files = []
    if render_previews:
        studio_info = studio.setup_studio_staging(scene, created_mesh_objects)
        previews_dir = os.path.join(output_dir, "previews")
        render_files = studio.render_standard_views(scene, studio_info, previews_dir, prefix=object_id)

    # 7. Sauvegarde du fichier .blend autonome
    blend_path = os.path.join(output_dir, f"{object_id}.blend")
    blend_info = exporter.save_autonomous_blend(blend_path)

    # 8. Exportation GLB sécurisée
    glb_info = None
    if export_glb:
        glb_path = os.path.join(output_dir, f"{object_id}.glb")
        glb_info = exporter.export_validated_glb(created_mesh_objects, glb_path)

    # 9. Rapport final de synthèse
    final_summary = {
        "object_id": object_id,
        "object_name": object_name,
        "category": spec["category"],
        "validation_verdict": val_report["verdict"],
        "base_vertices": val_report["total_base_vertices"],
        "base_faces": val_report["total_base_faces"],
        "evaluated_vertices": val_report["total_evaluated_vertices"],
        "evaluated_triangles": val_report["total_evaluated_triangles"],
        "bounding_box": val_report["bounding_box"],
        "delivered_blend": blend_info,
        "delivered_glb": glb_info,
        "previews": render_files
    }

    summary_path = os.path.join(output_dir, f"{object_id}_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(final_summary, f, indent=2)

    print(f"=== GÉNÉRATION DU MODÈLE '{object_id}' TERMINÉE AVEC SUCCÈS ===")
    return final_summary


if __name__ == "__main__":
    # Traitement des arguments passés après '--' dans Blender
    argv = sys.argv
    if "--" in argv:
        args_list = argv[argv.index("--") + 1:]
    else:
        args_list = []

    parser = argparse.ArgumentParser(description="Orchestrateur Générique 3D")
    parser.add_argument("--spec", required=True, help="Chemin vers le fichier JSON de spécification")
    parser.add_argument("--output-dir", required=True, help="Dossier de sortie du modèle")
    parser.add_argument("--no-glb", action="store_true", help="Désactiver l'exportation GLB")
    parser.add_argument("--no-render", action="store_true", help="Désactiver les rendus studio")

    args = parser.parse_args(args_list)
    run_pipeline(args.spec, args.output_dir, export_glb=not args.no_glb, render_previews=not args.no_render)
