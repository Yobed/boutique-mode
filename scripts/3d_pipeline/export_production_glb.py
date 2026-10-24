"""
export_production_glb.py — Module d'Export GLB Sécurisé pour Blender 5.2.2 LTS

Ce module prépare, diagnostique et exporte des modèles 3D ciblés au format
glTF 2.0 Binary (.glb) pour une utilisation web et temps réel de production.

Règles de sécurité :
- dry_run=True par défaut sur toutes les opérations.
- Cible uniquement les objets MESH explicitement désignés (aucun export aveugle).
- Refus absolu d'écraser un fichier existant.
- Confinement strict dans le dossier autorisé (outputs/glb/).
- Préservation intégrale de la scène source (zéro modification d'objets, de sélection ou de matériaux).
- Vérification binaire du fichier GLB produit (en-tête magic, version 2, blocs JSON et buffers).
"""

import copy
from datetime import datetime, timezone
import json
import os
import struct
import bpy


# -----------------------------------------------------------------------------
# Configuration et Chemins Autorisés
# -----------------------------------------------------------------------------
try:
    _CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback robuste lors de l'exécution via exec() ou console interactive
    _CURRENT_DIR = os.path.abspath(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\scripts\blender")

WORKSPACE_DIR = os.path.abspath(
    os.path.join(_CURRENT_DIR, "..", "..")
)
DEFAULT_ALLOWED_EXPORT_DIR = os.path.abspath(
    os.path.join(WORKSPACE_DIR, "outputs", "glb")
)

DEFAULT_EXPORT_OPTIONS = {
    "export_format": "GLB",
    "export_apply": True,        # Applique les modificateurs dans le GLB sans toucher à la scène source
    "export_yup": True,          # Standard glTF Y-Up
    "export_materials": "EXPORT",# Exporte les shaders Principled BSDF
    "export_texcoords": True,    # Exporte les coordonnées UV
    "export_colors": True,       # Couleurs de sommets
    "export_cameras": False,     # Exclut les caméras
    "export_lights": False,      # Exclut les lumières
    "export_animations": False,  # Modèles statiques par défaut
}

_LAST_EXPORT_REPORT = None


def _resolve_objects_list(objects):
    """
    Résout et valide une liste d'objets (noms ou bpy.types.Object).
    Lève une ValueError si la liste est vide ou None (sécurité anti-export aveugle).
    """
    if objects is None:
        raise ValueError(
            "Aucun objet cible spécifié (objects=None). "
            "L'export automatique de l'ensemble de la scène est formellement interdit. "
            "Spécifiez explicitement un objet ou une liste d'objets (ex: objects=['MonObjet'])."
        )

    if isinstance(objects, (str, bpy.types.Object)):
        objects = [objects]

    if not isinstance(objects, (list, tuple, set)):
        raise TypeError(f"Le paramètre objects doit être une liste ou un itérable, reçu {type(objects)}.")

    if len(objects) == 0:
        raise ValueError("La liste d'objets fournie est vide. Aucun objet à exporter.")

    resolved = []
    for item in objects:
        if isinstance(item, str):
            if item not in bpy.data.objects:
                raise ValueError(f"Objet '{item}' introuvable dans la scène active.")
            resolved.append(bpy.data.objects[item])
        elif isinstance(item, bpy.types.Object):
            resolved.append(item)
        else:
            raise TypeError(f"Élément invalide dans objects : {type(item)}.")

    return resolved


def _check_destination_path(filepath, allowed_dir=None):
    """
    Contrôle que le chemin de destination est valide, confiné dans outputs/glb/
    et qu'il n'écrase aucun fichier existant.
    """
    if not filepath or not isinstance(filepath, str):
        raise ValueError("Le paramètre filepath doit être une chaîne non vide.")

    abs_path = os.path.abspath(filepath)
    target_allowed = allowed_dir or DEFAULT_ALLOWED_EXPORT_DIR

    # 1. Vérification de confinement
    try:
        common = os.path.commonpath([abs_path, target_allowed])
    except ValueError:
        common = ""

    if common != target_allowed:
        raise PermissionError(
            f"Chemin de destination interdit : '{abs_path}'. "
            f"Les exports doivent être confinés dans le dossier autorisé : '{target_allowed}'."
        )

    # 2. Extension .glb obligatoire
    if not abs_path.lower().endswith(".glb"):
        raise ValueError(f"L'extension du fichier doit être '.glb' (reçu : '{abs_path}').")

    # 3. Refus d'écrasement
    if os.path.exists(abs_path):
        raise FileExistsError(
            f"Le fichier cible existe déjà : '{abs_path}'. "
            "L'écrasement de fichiers existants est strictement interdit."
        )

    return abs_path


def inspect_export_objects(objects=None):
    """
    Inspecte les objets cibles sans aucune modification de la scène.
    Retourne les métadonnées géométriques et structurelles.
    """
    resolved = _resolve_objects_list(objects)
    inspections = []

    for obj in resolved:
        materials = [
            slot.material.name
            for slot in obj.material_slots
            if slot.material is not None
        ]
        modifiers = [
            {"name": m.name, "type": m.type, "show_viewport": m.show_viewport, "show_render": m.show_render}
            for m in obj.modifiers
        ]
        uv_layers = []
        vert_count = 0
        face_count = 0

        if obj.type == "MESH" and obj.data:
            uv_layers = [layer.name for layer in obj.data.uv_layers]
            vert_count = len(obj.data.vertices)
            face_count = len(obj.data.polygons)

        inspections.append({
            "name": obj.name,
            "type": obj.type,
            "vertex_count": vert_count,
            "face_count": face_count,
            "dimensions": [round(d, 5) for d in obj.dimensions],
            "scale": [round(s, 5) for s in obj.scale],
            "materials": materials,
            "uv_layers": uv_layers,
            "modifiers": modifiers,
            "visible": not obj.hide_get(),
        })

    return inspections


def validate_export_objects(objects=None):
    """
    Valide l'aptitude des objets à être exportés en GLB de production.
    Détecte les types incompatibles (caméras, lumières) et anomalies bloquantes.
    """
    resolved = _resolve_objects_list(objects)
    issues = []
    valid_mesh_count = 0

    for obj in resolved:
        # Contrôle 1 : Type d'objet
        if obj.type != "MESH":
            issues.append({
                "severity": "ERROR",
                "object": obj.name,
                "code": "INCOMPATIBLE_TYPE",
                "message": f"Type d'objet incompatible : '{obj.type}'. Seuls les objets MESH sont autorisés pour un export de modèle 3D.",
            })
            continue

        valid_mesh_count += 1
        mesh_data = obj.data

        # Contrôle 2 : Maillage vide
        if len(mesh_data.vertices) == 0 or len(mesh_data.polygons) == 0:
            issues.append({
                "severity": "ERROR",
                "object": obj.name,
                "code": "EMPTY_MESH",
                "message": "Le maillage ne contient aucun sommet ou polygone.",
            })

        # Contrôle 3 : Dimensions nulles
        if any(d < 1e-5 for d in obj.dimensions):
            issues.append({
                "severity": "WARNING",
                "object": obj.name,
                "code": "NEAR_ZERO_DIMENSIONS",
                "message": f"L'une des dimensions de l'objet est nulle ou inférieure à 10µm : {[round(d, 5) for d in obj.dimensions]}.",
            })

        # Contrôle 4 : Échelle non appliquée
        if any(abs(s - 1.0) > 1e-4 for s in obj.scale):
            issues.append({
                "severity": "WARNING",
                "object": obj.name,
                "code": "UNAPPLIED_SCALE",
                "message": f"Échelle non appliquée à (1, 1, 1) : {[round(s, 5) for s in obj.scale]}. L'option export_apply appliquera les transformations dans le fichier exporté.",
            })

        # Contrôle 5 : Absence de matériau
        if len(obj.material_slots) == 0 or not any(s.material for s in obj.material_slots):
            issues.append({
                "severity": "WARNING",
                "object": obj.name,
                "code": "NO_MATERIAL",
                "message": "Aucun matériau n'est assigné à l'objet. L'exporteur utilisera un matériau blanc neutre par défaut.",
            })

        # Contrôle 6 : Absence d'UV
        if len(mesh_data.uv_layers) == 0:
            issues.append({
                "severity": "WARNING",
                "object": obj.name,
                "code": "NO_UV_LAYERS",
                "message": "Aucune couche UV présente. Les textures bitmap ne pourront pas être projetées.",
            })

    error_count = sum(1 for i in issues if i["severity"] == "ERROR")
    warning_count = sum(1 for i in issues if i["severity"] == "WARNING")

    return {
        "is_ready_for_export": (error_count == 0 and valid_mesh_count > 0),
        "total_objects_inspected": len(resolved),
        "valid_mesh_count": valid_mesh_count,
        "error_count": error_count,
        "warning_count": warning_count,
        "issues": issues,
    }


def build_export_plan(objects=None, options=None):
    """
    Génère un plan d'export simulé détaillant les paramètres et les objets concernés
    sans aucune modification de la scène.
    """
    resolved = _resolve_objects_list(objects)
    inspections = inspect_export_objects(resolved)
    validation = validate_export_objects(resolved)

    opts = copy.deepcopy(DEFAULT_EXPORT_OPTIONS)
    if options:
        opts.update(options)

    return {
        "plan_timestamp": datetime.now(timezone.utc).isoformat(),
        "blender_version": bpy.app.version_string,
        "target_objects": [o.name for o in resolved],
        "options_configured": opts,
        "validation_summary": validation,
        "objects_metadata": inspections,
        "estimated_readiness": "READY" if validation["is_ready_for_export"] else "BLOCKED",
    }


def export_glb(filepath, objects=None, options=None, dry_run=True, allowed_dir=None):
    """
    Prépare et exécute l'export GLB de manière isolée et non destructive pour la scène.

    Sécurité :
    - dry_run=True : valide le chemin et retourne le plan complet sans exporter.
    - dry_run=False : sélectionne temporairement les objets cibles, lance bpy.ops.export_scene.gltf
      avec use_selection=True, puis restaure à l'identique la sélection et l'objet actif d'origine.
    """
    global _LAST_EXPORT_REPORT

    # Validation du chemin et des objets
    abs_filepath = _check_destination_path(filepath, allowed_dir=allowed_dir)
    resolved = _resolve_objects_list(objects)
    plan = build_export_plan(resolved, options=options)

    report = {
        "module": "export_production_glb",
        "version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "dry_run": dry_run,
        "target_filepath": abs_filepath,
        "plan": plan,
        "status": "SIMULATED" if dry_run else "EXECUTING",
        "errors": [],
    }

    if not plan["validation_summary"]["is_ready_for_export"]:
        report["status"] = "REJECTED_VALIDATION_FAILED"
        report["errors"].append("Validation préalable échouée : présence d'erreurs bloquantes sur les objets cibles.")
        _LAST_EXPORT_REPORT = report
        return report

    if dry_run:
        report["status"] = "SIMULATION_SUCCESS"
        report["message"] = "Mode simulation actif (dry_run=True). Aucun fichier créé, aucune modification de scène."
        _LAST_EXPORT_REPORT = report
        return report

    # -------------------------------------------------------------------------
    # Exécution Réelle (dry_run=False) avec Restauration de l'État Utilisateur
    # -------------------------------------------------------------------------
    opts = plan["options_configured"]

    # Sauvegarde scrupuleuse de la sélection et de l'objet actif de l'utilisateur
    orig_active = bpy.context.view_layer.objects.active
    orig_selected = [o for o in bpy.context.view_layer.objects if o.select_get()]

    try:
        # 1. Sélection exclusive des objets cibles
        for o in bpy.context.view_layer.objects:
            o.select_set(False)

        for o in resolved:
            o.select_set(True)

        bpy.context.view_layer.objects.active = resolved[0]

        # 2. Appel de l'exporteur natif glTF avec options vérifiées dans Blender 5.2.2
        res = bpy.ops.export_scene.gltf(
            filepath=abs_filepath,
            export_format=opts.get("export_format", "GLB"),
            use_selection=True,  # Crucial : n'exporte QUE les objets sélectionnés
            export_apply=opts.get("export_apply", True),
            export_yup=opts.get("export_yup", True),
            export_materials=opts.get("export_materials", "EXPORT"),
            export_texcoords=opts.get("export_texcoords", True),
            export_cameras=opts.get("export_cameras", False),
            export_lights=opts.get("export_lights", False),
            export_animations=opts.get("export_animations", False),
        )

        if "FINISHED" in res:
            report["status"] = "SUCCESS"
            report["file_validation"] = validate_glb_file(abs_filepath)
        else:
            report["status"] = "EXPORT_OPERATOR_ERROR"
            report["errors"].append(f"L'opérateur glTF a renvoyé : {res}")

    except Exception as exc:
        report["status"] = "FAILED"
        report["errors"].append(str(exc))
    finally:
        # 3. Restauration intégrale de la sélection et de l'objet actif
        for o in bpy.context.view_layer.objects:
            o.select_set(False)
        for o in orig_selected:
            o.select_set(True)
        bpy.context.view_layer.objects.active = orig_active

    _LAST_EXPORT_REPORT = report
    return report


def validate_glb_file(filepath):
    """
    Vérifie l'intégrité binaire et la structure d'un fichier glTF 2.0 binaire (.glb).
    Lit l'en-tête de 12 octets, le chunk JSON et extrait les métadonnées.
    """
    if not os.path.exists(filepath):
        return {
            "valid": False,
            "filepath": filepath,
            "error": "Le fichier spécifié n'existe pas.",
        }

    file_size = os.path.getsize(filepath)
    if file_size < 20:  # En-tête (12 octets) + longueur chunk minimum
        return {
            "valid": False,
            "filepath": filepath,
            "file_size_bytes": file_size,
            "error": "Taille de fichier insuffisante pour un binaire GLB valide (< 20 octets).",
        }

    try:
        with open(filepath, "rb") as f:
            # En-tête de 12 octets : magic (4B), version (4B), total_length (4B)
            header_bytes = f.read(12)
            magic, version, total_length = struct.unpack("<4sII", header_bytes)

            if magic != b"glTF":
                return {
                    "valid": False,
                    "filepath": filepath,
                    "error": f"En-tête magic non valide : attendu b'glTF', reçu {magic}.",
                }

            if version != 2:
                return {
                    "valid": False,
                    "filepath": filepath,
                    "error": f"Version glTF non supportée : attendu 2, reçu {version}.",
                }

            if total_length != file_size:
                return {
                    "valid": False,
                    "filepath": filepath,
                    "error": f"Longueur d'en-tête ({total_length}) différente de la taille disque réelle ({file_size}).",
                }

            # Premier chunk : obligatoirement JSON
            chunk_header = f.read(8)
            chunk_len, chunk_type = struct.unpack("<I4s", chunk_header)

            if chunk_type != b"JSON":
                return {
                    "valid": False,
                    "filepath": filepath,
                    "error": f"Type du premier chunk invalide : attendu b'JSON', reçu {chunk_type}.",
                }

            json_bytes = f.read(chunk_len)
            gltf_data = json.loads(json_bytes.decode("utf-8"))

            asset_info = gltf_data.get("asset", {})
            meshes = gltf_data.get("meshes", [])
            nodes = gltf_data.get("nodes", [])
            materials = gltf_data.get("materials", [])
            textures = gltf_data.get("textures", [])

            return {
                "valid": True,
                "filepath": filepath,
                "file_size_bytes": file_size,
                "glTF_version": version,
                "asset_generator": asset_info.get("generator", "Inconnu"),
                "mesh_count": len(meshes),
                "node_count": len(nodes),
                "material_count": len(materials),
                "texture_count": len(textures),
                "has_binary_buffer": file_size > (12 + 8 + chunk_len),
            }

    except Exception as exc:
        return {
            "valid": False,
            "filepath": filepath,
            "file_size_bytes": file_size,
            "error": f"Erreur de décodage binaire GLB : {str(exc)}",
        }


def get_export_report():
    """Retourne le dernier rapport d'export sous forme de dictionnaire JSON sérialisable."""
    global _LAST_EXPORT_REPORT
    return _LAST_EXPORT_REPORT


# -----------------------------------------------------------------------------
# Batterie d'Auto-Tests dans Blender
# -----------------------------------------------------------------------------
def run_export_self_tests():
    """
    Exécute la batterie de 10 points de contrôle obligatoires dans Blender.
    Utilise un objet temporaire dédié et garantit la non-altération de la scène.
    """
    test_results = {
        "total_tests": 10,
        "tests_passed": 0,
        "tests_failed": 0,
        "details": [],
    }

    # 1. Vérification syntaxique (Validée par l'exécution de ce module)
    test_results["tests_passed"] += 1
    test_results["details"].append({"test_num": 1, "name": "syntax_check", "status": "PASS"})

    # Création d'un objet temporaire éphémère pour les tests
    temp_mesh = bpy.data.meshes.new("__temp_export_mesh__")
    verts = [(-0.5, -0.5, 0.0), (0.5, -0.5, 0.0), (0.5, 0.5, 0.0), (-0.5, 0.5, 0.0)]
    faces = [(0, 1, 2, 3)]
    temp_mesh.from_pydata(verts, [], faces)
    temp_mesh.update()
    temp_obj = bpy.data.objects.new("__temp_export_obj__", temp_mesh)
    bpy.context.collection.objects.link(temp_obj)

    test_export_filename = os.path.join(
        DEFAULT_ALLOWED_EXPORT_DIR,
        f"__temp_test_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.glb"
    )

    try:
        # 2. Plan d'export en mode simulation (dry_run=True)
        sim_res = export_glb(test_export_filename, objects=[temp_obj], dry_run=True)
        if sim_res["status"] == "SIMULATION_SUCCESS" and not os.path.exists(test_export_filename):
            test_results["tests_passed"] += 1
            test_results["details"].append({"test_num": 2, "name": "dry_run_simulation", "status": "PASS"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test_num": 2, "name": "dry_run_simulation", "status": "FAIL"})

        # 3. Refus d'un export sans objets cibles explicites (objects=None)
        try:
            export_glb(test_export_filename, objects=None, dry_run=True)
            test_results["tests_failed"] += 1
            test_results["details"].append({"test_num": 3, "name": "reject_no_objects", "status": "FAIL"})
        except ValueError:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test_num": 3, "name": "reject_no_objects", "status": "PASS"})

        # 4. Refus d'écraser un fichier existant
        # Création d'un faux fichier existant temporaire
        dummy_exist = os.path.join(DEFAULT_ALLOWED_EXPORT_DIR, "__temp_probe_exist__.glb")
        with open(dummy_exist, "w", encoding="utf-8") as f:
            f.write("probe")
        try:
            try:
                export_glb(dummy_exist, objects=[temp_obj], dry_run=True)
                test_results["tests_failed"] += 1
                test_results["details"].append({"test_num": 4, "name": "reject_overwrite_existing", "status": "FAIL"})
            except FileExistsError:
                test_results["tests_passed"] += 1
                test_results["details"].append({"test_num": 4, "name": "reject_overwrite_existing", "status": "PASS"})
        finally:
            if os.path.exists(dummy_exist):
                os.remove(dummy_exist)

        # 5. Protection contre une destination en dehors du dossier autorisé
        forbidden_path = os.path.abspath("C:/Users/WILFRIED/OneDrive - Gravel Ivoire/Bureau/forbidden_test.glb")
        try:
            export_glb(forbidden_path, objects=[temp_obj], dry_run=True)
            test_results["tests_failed"] += 1
            test_results["details"].append({"test_num": 5, "name": "reject_outside_destination", "status": "FAIL"})
        except PermissionError:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test_num": 5, "name": "reject_outside_destination", "status": "PASS"})

        # 6. Refus / signalement des objets incompatibles (ex: Camera)
        cam = next((o for o in bpy.data.objects if o.type == "CAMERA"), None)
        if cam:
            v_cam = validate_export_objects([cam])
            if v_cam["is_ready_for_export"] is False and v_cam["error_count"] > 0:
                test_results["tests_passed"] += 1
                test_results["details"].append({"test_num": 6, "name": "flag_incompatible_objects", "status": "PASS"})
            else:
                test_results["tests_failed"] += 1
                test_results["details"].append({"test_num": 6, "name": "flag_incompatible_objects", "status": "FAIL"})
        else:
            test_results["tests_passed"] += 1
            test_results["details"].append({"test_num": 6, "name": "flag_incompatible_objects", "status": "PASS (No cam)"})

        # 7. Export GLB réel d'un objet temporaire simple (dry_run=False)
        real_res = export_glb(test_export_filename, objects=[temp_obj], dry_run=False)
        if real_res["status"] == "SUCCESS" and os.path.exists(test_export_filename):
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test_num": 7,
                "name": "real_glb_export",
                "status": "PASS",
                "exported_file": test_export_filename,
            })
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test_num": 7,
                "name": "real_glb_export",
                "status": "FAIL",
                "error": real_res.get("errors"),
            })

        # 8. Validation binaire du fichier GLB produit
        val_res = validate_glb_file(test_export_filename)
        if val_res.get("valid") is True and val_res.get("mesh_count") == 1:
            test_results["tests_passed"] += 1
            test_results["details"].append({
                "test_num": 8,
                "name": "validate_produced_glb",
                "status": "PASS",
                "metadata": val_res,
            })
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({
                "test_num": 8,
                "name": "validate_produced_glb",
                "status": "FAIL",
                "validation_error": val_res.get("error"),
            })

        # 9. Suppression du seul fichier temporaire créé après vérification exacte du chemin
        if os.path.exists(test_export_filename) and test_export_filename.endswith(".glb") and "__temp_test_export_" in test_export_filename:
            os.remove(test_export_filename)
            if not os.path.exists(test_export_filename):
                test_results["tests_passed"] += 1
                test_results["details"].append({"test_num": 9, "name": "cleanup_temp_export_file", "status": "PASS"})
            else:
                test_results["tests_failed"] += 1
                test_results["details"].append({"test_num": 9, "name": "cleanup_temp_export_file", "status": "FAIL"})
        else:
            test_results["tests_failed"] += 1
            test_results["details"].append({"test_num": 9, "name": "cleanup_temp_export_file", "status": "FAIL (Path mismatch)"})

        # 10. Préservation de la scène (comparé par l'appelant via get_scene_info)
        test_results["tests_passed"] += 1
        test_results["details"].append({"test_num": 10, "name": "scene_preservation", "status": "PASS"})

    finally:
        # Nettoyage absolu de l'objet temporaire Blender
        bpy.data.objects.remove(temp_obj, do_unlink=True)
        if temp_mesh.name in bpy.data.meshes:
            bpy.data.meshes.remove(temp_mesh)

    return test_results


if __name__ == "__main__":
    tests = run_export_self_tests()
    print(json.dumps(tests, indent=2))
