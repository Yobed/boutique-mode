"""
analyzer.py — Analyseur de Référence et Validateur de Schéma de Spécification
Transforme et valide les spécifications JSON d'objets pour le pipeline 3D.
"""

import json
import os

REQUIRED_SPEC_KEYS = ["object_id", "object_name", "category", "scale_metric", "components"]


def validate_and_load_spec(spec_path):
    """Charge et valide la structure déclarative d'une spécification d'objet."""
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"Fichier de spécification introuvable : {spec_path}")

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    for key in REQUIRED_SPEC_KEYS:
        if key not in spec:
            raise ValueError(f"Clé obligatoire manquante dans la spécification : '{key}'")

    if not isinstance(spec["components"], list) or len(spec["components"]) == 0:
        raise ValueError("La liste 'components' doit comporter au moins un élément.")

    # Compléter les valeurs par défaut si absentes
    if "coordinate_system" not in spec:
        spec["coordinate_system"] = {
            "up_axis": "+Z",
            "forward_axis": "-Y",
            "lateral_axis": "+X",
            "origin": "bottom_center"
        }

    return spec
