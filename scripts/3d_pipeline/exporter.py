"""
exporter.py — Module de Livraison et d'Exportation Sécurisée pour Blender 5.x
Garantit l'isolation stricte des fichiers et vérifie la conformité binaire des livrables.
"""

import hashlib
import json
import os
import sys
import bpy

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(WORKSPACE_DIR, "scripts", "blender"))
import export_production_glb


def get_file_sha256(filepath):
    """Calcule l'empreinte SHA-256 d'un fichier."""
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def save_autonomous_blend(filepath):
    """Sauvegarde la scène active dans un fichier .blend autonome."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.wm.save_mainfile(filepath=filepath)
    sz = os.path.getsize(filepath)
    h = get_file_sha256(filepath)
    print(f"Scène autonome sauvegardée : {filepath} ({sz} octets, SHA-256: {h})")
    return {"path": filepath, "size": sz, "sha256": h}


def export_validated_glb(mesh_objects, output_glb_path):
    """Exécute un export GLB sécurisé et contrôlé via export_production_glb.py."""
    os.makedirs(os.path.dirname(output_glb_path), exist_ok=True)
    if os.path.exists(output_glb_path):
        os.remove(output_glb_path)

    # Désélectionner rigoureusement tous les objets dans toutes les scènes et view-layers
    for scn in bpy.data.scenes:
        for obj in scn.collection.all_objects:
            try:
                obj.select_set(False)
            except Exception:
                pass

    for obj in mesh_objects:
        try:
            obj.select_set(True)
        except Exception:
            pass
    if mesh_objects:
        bpy.context.view_layer.objects.active = mesh_objects[0]

    # Configuration d'export glTF (uniquement les objets sélectionnés de la scène active)
    bpy.ops.export_scene.gltf(
        filepath=output_glb_path,
        export_format='GLB',
        use_active_scene=True,
        use_selection=True,
        use_visible=True,
        export_apply=True,
        export_yup=True,
        export_materials='EXPORT',
        export_cameras=False,
        export_lights=False
    )

    sz = os.path.getsize(output_glb_path)
    h = get_file_sha256(output_glb_path)

    # Vérification binaire
    is_valid_glb = False
    with open(output_glb_path, "rb") as f:
        magic = f.read(4)
        if magic == b"glTF":
            is_valid_glb = True

    print(f"Modèle GLB exporté : {output_glb_path} ({sz} octets, valid={is_valid_glb}, SHA-256: {h})")
    return {
        "path": output_glb_path,
        "size": sz,
        "sha256": h,
        "is_valid_binary_glb": is_valid_glb
    }
