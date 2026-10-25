"""
visual_recognizer.py — Reconnaissance de produit par modèle de vision (CLIP zero-shot)
Projet : boutique-mode / Pipeline Image-to-3D

Complète semantic_classifier.py : la silhouette seule ne distingue pas une tasse
d'un sac ni une lampe d'une bouteille. Ce module reconnaît le produit à partir de
l'apparence (couleur, texture, parties visibles) et s'abstient sous un seuil de
confiance au lieu de forcer un libellé.

Il ne choisit PAS la catégorie de construction 3D : il fournit un libellé reconnu
et indique l'archétype 3D correspondant. Un libellé sans gabarit 3D (archétype None)
reste construit en générique.
"""

import os

MODEL_ID = "openai/clip-vit-base-patch32"
PROMPT = "a product photo of {} on a plain background"
MIN_PROB = 0.45     # ponytail: seuils posés à la main, à calibrer sur un jeu étiqueté indépendant
MIN_MARGIN = 0.15
CROP_MARGIN = 0.05

# libellé -> (description CLIP, archétype 3D existant ou None)
LABELS = {
    "handbag": ("a leather handbag", "fashion_handbag"),
    "sofa": ("a sofa", "horizontal_lounge_furniture"),
    "armchair": ("an armchair", None),
    "vase": ("a ceramic vase or carafe", "tableware_lathe"),
    "lamp": ("a table lamp", "slender_pedestal_lamp"),
    "electronics_box": ("an external SSD or power bank", "prismatic_enclosure_electronics"),
    "shoe": ("a sneaker or shoe", None),
    "mug": ("a mug or cup with a handle", None),
    "stool": ("a stool", None),
    "speaker": ("a loudspeaker", None),
    "iron": ("a steam iron", None),
    "bottle": ("a thermos or water bottle", None),
    "hammer": ("a hammer", None),
}

_model_cache = {}


def _load():
    if not _model_cache:
        from transformers import CLIPModel, CLIPProcessor
        _model_cache["model"] = CLIPModel.from_pretrained(MODEL_ID).eval()
        _model_cache["proc"] = CLIPProcessor.from_pretrained(MODEL_ID)
    return _model_cache["model"], _model_cache["proc"]


def _crop(image, bbox):
    if not bbox:
        return image
    x0, y0, x1, y1 = bbox
    mx = int((x1 - x0) * CROP_MARGIN)
    my = int((y1 - y0) * CROP_MARGIN)
    return image.crop((max(0, x0 - mx), max(0, y0 - my),
                       min(image.width, x1 + mx), min(image.height, y1 + my)))


def recognize_product(image_path, bbox=None):
    """Retourne le libellé reconnu, ou abstained=True si la confiance est insuffisante."""
    import torch
    from PIL import Image

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image introuvable : {image_path}")

    model, proc = _load()
    image = _crop(Image.open(image_path).convert("RGB"), bbox)
    names = list(LABELS)
    inputs = proc(text=[PROMPT.format(LABELS[n][0]) for n in names],
                  images=image, return_tensors="pt", padding=True)
    with torch.no_grad():
        probs = model(**inputs).logits_per_image.softmax(dim=-1)[0].tolist()

    ranked = sorted(zip(names, probs), key=lambda p: p[1], reverse=True)
    (top, p1), (_, p2) = ranked[0], ranked[1]
    abstained = p1 < MIN_PROB or (p1 - p2) < MIN_MARGIN
    return {
        "label": None if abstained else top,
        "best_guess": top,
        "confidence": round(p1, 3),
        "margin": round(p1 - p2, 3),
        "abstained": abstained,
        "archetype": None if abstained else LABELS[top][1],
        "top3": [(n, round(p, 3)) for n, p in ranked[:3]],
    }
