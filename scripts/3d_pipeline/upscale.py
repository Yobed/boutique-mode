"""
upscale.py — Super-résolution des vues sources (Real-ESRGAN x4, via spandrel).

Les panneaux d'une planche font ~175 px de large : projetés sur le modèle, la texture est floue au zoom.
Real-ESRGAN reconstruit des détails plausibles (grain, coutures, bords nets) avant la cuisson de la texture.
Les détails ajoutés sont inventés par le réseau : ils servent la crédibilité visuelle, pas la fidélité métrologique.
"""

import os

import numpy as np
from PIL import Image

MODELS_DIR = os.environ.get("ELSI_3D_MODELS") or os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "elsi-3d-models")
WEIGHTS = os.path.join(MODELS_DIR, "RealESRGAN_x4plus.pth")
TARGET_LONG_SIDE = 1200   # on ne dépasse pas cette taille (mémoire, poids de la texture)
SKIP_ABOVE = 700          # une vue déjà grande n'a pas besoin de super-résolution
TILE = 160
OVERLAP = 16
SCALE = 4

_cache = {}


def _model():
    if "m" not in _cache:
        import torch
        from spandrel import ModelLoader

        descriptor = ModelLoader().load_from_file(WEIGHTS)
        descriptor.model.eval()
        torch.set_grad_enabled(False)
        _cache["m"] = descriptor.model
    return _cache["m"]


def _run_tiled(rgb):
    """Inférence par tuiles avec recouvrement (la mémoire reste bornée quelle que soit la taille)."""
    import torch

    model = _model()
    h, w, _ = rgb.shape
    pad = OVERLAP
    padded = np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)), mode="reflect")
    out = np.zeros((h * SCALE, w * SCALE, 3), np.float32)
    for y in range(0, h, TILE):
        for x in range(0, w, TILE):
            th, tw = min(TILE, h - y), min(TILE, w - x)
            tile = padded[y:y + th + 2 * pad, x:x + tw + 2 * pad]
            tensor = torch.from_numpy(tile).permute(2, 0, 1)[None].float() / 255.0
            result = model(tensor)[0].permute(1, 2, 0).clamp(0, 1).numpy() * 255.0
            crop = result[pad * SCALE:(pad + th) * SCALE, pad * SCALE:(pad + tw) * SCALE]
            out[y * SCALE:(y + th) * SCALE, x * SCALE:(x + tw) * SCALE] = crop
    return out


def upscale_rgb(rgb):
    """rgb uint8 (h, w, 3) -> uint8 plus grand (x4 puis réduit à TARGET_LONG_SIDE). Inchangé si déjà grand ou poids absents."""
    if max(rgb.shape[:2]) >= SKIP_ABOVE or not os.path.exists(WEIGHTS):
        return rgb
    big = _run_tiled(rgb)
    scale = min(1.0, TARGET_LONG_SIDE / max(big.shape[:2]))
    image = Image.fromarray(np.clip(big, 0, 255).astype(np.uint8))
    if scale < 1.0:
        image = image.resize((round(image.width * scale), round(image.height * scale)), Image.LANCZOS)
    return np.asarray(image)
