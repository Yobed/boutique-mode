"""
eval_fidelity.py — Reconstruction neuronale de chaque image du jeu + mesure de fidélité.

Pour chaque image : GLB (TripoSR), IoU de reprojection depuis la caméra de
conditionnement, étanchéité, durée, et planche de contrôle (photo | 0° | 45° | 90°).

ATTENTION : une seule photo ne montre pas l'arrière. L'IoU mesure la cohérence avec
la vue fournie, pas la justesse des faces cachées. La planche reste à juger à l'oeil.
Usage : python eval_fidelity.py [dossier_sortie]
"""

import gc
import json
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "scripts", "3d_pipeline"))

import neural_reconstruct as nr  # noqa: E402
from eval_recognition import list_unique_images  # noqa: E402

VIEW = 420
DEFAULT_OUT = r"C:\ai_models\out\fidelity"
SAMPLES = 300_000


def _view(points, colors, yaw):
    c, s = np.cos(yaw), np.sin(yaw)
    p = points @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T
    order = np.argsort(p[:, 2])
    p, col = p[order], colors[order]
    scale = (VIEW / 2 - 8) / np.abs(p[:, :2]).max()
    img = np.full((VIEW, VIEW, 3), 245, np.uint8)
    x = np.clip((p[:, 0] * scale + VIEW / 2).astype(int), 0, VIEW - 1)
    y = np.clip((VIEW / 2 - p[:, 1] * scale).astype(int), 0, VIEW - 1)
    img[y, x] = col
    return Image.fromarray(img)


def contact_sheet(src, out_dir):
    import trimesh

    mesh = trimesh.load(os.path.join(out_dir, "mesh.glb"), force="mesh")
    pts, face_idx = mesh.sample(SAMPLES, return_index=True)
    colors = np.asarray(mesh.visual.vertex_colors)[mesh.faces[face_idx][:, 0]][:, :3]
    photo = Image.open(src).convert("RGB")
    photo.thumbnail((VIEW, VIEW))
    sheet = Image.new("RGB", (VIEW * 4, VIEW), (245, 245, 245))
    sheet.paste(photo, (0, 0))
    for i, yaw in enumerate([0.0, np.pi / 4, np.pi / 2]):
        sheet.paste(_view(pts, colors, yaw), (VIEW * (i + 1), 0))
    sheet.save(os.path.join(out_dir, "contact.png"))


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_OUT
    rows = []
    for path, truth in list_unique_images():
        out_dir = os.path.join(root, truth)
        report = None
        for attempt in (1, 2):  # la mémoire système est parfois saturée : une seconde chance
            try:
                report = nr.reconstruct(path, out_dir)
                contact_sheet(path, out_dir)
                break
            except Exception as exc:  # une image en échec ne doit pas arrêter le lot
                report = {"error": f"{type(exc).__name__}: {exc}"[:300], "attempts": attempt}
                gc.collect()
        report["label"] = truth
        rows.append(report)
        print(json.dumps({k: report.get(k) for k in ("label", "silhouette_iou_front", "watertight", "seconds", "error")}), flush=True)

    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "summary.json"), "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)

    ok = [r for r in rows if "error" not in r]
    print(f"\nReconstruits : {len(ok)}/{len(rows)}")
    if ok:
        ious = [r["silhouette_iou_front"] for r in ok]
        print(f"IoU reprojection : moyenne {np.mean(ious):.3f}, min {min(ious):.3f}, max {max(ious):.3f}")
        print(f"Étanches : {sum(r['watertight'] for r in ok)}/{len(ok)}")


if __name__ == "__main__":
    main()
