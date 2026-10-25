"""
neural_reconstruct.py — Reconstruction 3D neuronale image -> GLB (TripoSR) + fidélité à la photo.

Remplace les gabarits procéduraux par catégorie : le modèle infère une forme et une
couleur pour n'importe quel produit. Une seule photo ne révèle pas l'arrière : la
sortie reste une estimation. La fidélité est mesurée par l'IoU entre la silhouette
de la photo et celle du maillage, vue de face.

Prérequis : poids installés par `python scripts/3d_pipeline/setup_neural.py` (voir
docs/3d-pipeline/NEURAL_IMAGE_TO_3D.md). Le moteur TripoSR est embarqué dans vendor/TripoSR.
"""

import json
import os
import sys
import time

import numpy as np
from PIL import Image

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
TRIPOSR_DIR = os.path.join(PIPELINE_DIR, "vendor", "TripoSR")
# Poids hors du dépôt (1,9 Go, ne pas synchroniser sur OneDrive) : config.yaml, model.ckpt, u2net.onnx
MODELS_DIR = os.environ.get("ELSI_3D_MODELS") or os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "elsi-3d-models")
TRIPOSR_WEIGHTS = MODELS_DIR
U2NET_PATH = os.path.join(TRIPOSR_WEIGHTS, "u2net.onnx")
CAMERA_DISTANCE = 1.9  # caméra de rendu par défaut de TripoSR (tsr/system.py::render)
CAMERA_FOVY = 40.0
PROJECTION_SIZE = 512
DEPTH_EPSILON = 0.02
MIN_FACING_COS = 0.2
DEFAULT_TEXTURE_SIZE = 2048
DEFAULT_TARGET_FACES = 60_000   # maillage web ; --quality high : 150 000
MIN_COMPONENT_FRACTION = 0.01
SEPARATE_OBJECT_FRACTION = 0.20
FOREGROUND_RATIO = 0.85
GRID = 256
POINT_SAMPLES = 400_000

for p in (TRIPOSR_DIR, PIPELINE_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import finish_mesh  # noqa: E402
from revolve_solid import build_revolve_mesh, looks_like_revolution  # noqa: E402

_model = {}


def _get_model():
    if "tsr" not in _model:
        import torch
        from tsr.system import TSR

        model = TSR.from_pretrained(
            TRIPOSR_WEIGHTS, config_name="config.yaml", weight_name="model.ckpt")
        model.renderer.set_chunk_size(8192)
        model.to("cpu")
        _model["tsr"] = model
        _model["torch"] = torch
    return _model["tsr"], _model["torch"]


def _matte(rgb_image):
    """Alpha 0-255 par U²-Net (ONNX) : fonctionne sur fonds photographiés, dégradés et reflets."""
    import onnxruntime as ort

    if "u2net" not in _model:
        _model["u2net"] = ort.InferenceSession(U2NET_PATH, providers=["CPUExecutionProvider"])
    sess = _model["u2net"]
    small = np.asarray(rgb_image.resize((320, 320), Image.LANCZOS), dtype=np.float32)
    small = small / max(float(small.max()), 1e-6)
    small = (small - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
    x = small.transpose(2, 0, 1)[None].astype(np.float32)
    pred = sess.run(None, {sess.get_inputs()[0].name: x})[0][0, 0]
    pred = (pred - pred.min()) / max(float(pred.max() - pred.min()), 1e-6)
    alpha = Image.fromarray((pred * 255).astype(np.uint8)).resize(rgb_image.size, Image.LANCZOS)
    return np.array(alpha)


def _prepare_input(image_path, work_dir):
    """Détoure (U²-Net), recadre, fond gris 0.5."""
    from tsr.utils import resize_foreground

    rgb_image = Image.open(image_path).convert("RGB")
    alpha = _matte(rgb_image)
    mask = alpha > 127
    if not mask.any():
        raise ValueError("Aucun objet détecté par le détourage : photo inexploitable.")
    from scipy import ndimage

    sizes = np.bincount(ndimage.label(mask)[0].ravel())[1:]
    stats = {
        "coverage": float(mask.mean()),
        # objets séparés de taille comparable (ex. deux chaussures) : une seule photo ne les modélise pas bien
        "objects": int((sizes >= SEPARATE_OBJECT_FRACTION * sizes.max()).sum()),
    }
    rgba = np.dstack([np.array(rgb_image), alpha])
    rgba_img = resize_foreground(Image.fromarray(rgba, "RGBA"), FOREGROUND_RATIO)
    rgba_img.save(os.path.join(work_dir, "cutout.png"))  # produit détouré, fond transparent (poster)
    arr = np.array(rgba_img).astype(np.float32) / 255.0
    arr = arr[:, :, :3] * arr[:, :, 3:4] + (1 - arr[:, :, 3:4]) * 0.5
    image = Image.fromarray((arr * 255).astype(np.uint8))
    image.save(os.path.join(work_dir, "input.png"))
    return image, np.array(rgba_img)[..., 3] > 127, stats


def _reprojected_silhouette(mesh):
    """Silhouette du maillage vue depuis la caméra de conditionnement de TripoSR (perspective)."""
    from scipy import ndimage

    pts = mesh.sample(POINT_SAMPLES)  # repère glTF : x droite, y haut, +z vers la caméra
    depth = CAMERA_DISTANCE - pts[:, 2]
    t = np.tan(np.radians(CAMERA_FOVY) / 2.0)
    u = pts[:, 0] / (depth * t)
    v = pts[:, 1] / (depth * t)
    cols = np.clip(((u + 1) / 2 * (GRID - 1)).round().astype(int), 0, GRID - 1)
    rows = np.clip(((1 - v) / 2 * (GRID - 1)).round().astype(int), 0, GRID - 1)
    grid = np.zeros((GRID, GRID), dtype=bool)
    grid[rows, cols] = True
    return ndimage.binary_fill_holes(ndimage.binary_closing(grid, iterations=2))


def silhouette_iou(input_alpha, mesh):
    """IoU entre l'image détourée reçue par le modèle et la reprojection du maillage."""
    a = np.array(Image.fromarray((input_alpha * 255).astype(np.uint8)).resize((GRID, GRID), Image.NEAREST)) > 127
    b = _reprojected_silhouette(mesh)
    return float((a & b).sum() / max(1, (a | b).sum()))


def _drop_tiny_components(tri):
    """Supprime les fragments flottants (bruit de l'iso-surface) sous MIN_COMPONENT_FRACTION des faces."""
    import trimesh

    parts = tri.split(only_watertight=False)
    keep = [p for p in parts if len(p.faces) >= MIN_COMPONENT_FRACTION * len(tri.faces)]
    if len(keep) == len(parts):
        return tri
    return trimesh.util.concatenate(keep)


def _project_photo_colors(tri, image, alpha_sq):
    """Remplace la couleur des sommets visibles depuis la caméra par les pixels de la photo.

    Les sommets cachés (dos, dessous) gardent la couleur estimée par le modèle ; les faces
    vues de biais sont fondues vers cette estimation pour éviter l'étirement.
    """
    from scipy import ndimage

    size = PROJECTION_SIZE
    rgb = np.asarray(image.resize((size, size), Image.LANCZOS)).astype(np.float32)
    alpha = np.array(Image.fromarray((alpha_sq * 255).astype(np.uint8)).resize((size, size), Image.NEAREST)) > 127
    alpha = ndimage.binary_erosion(alpha, iterations=3)  # évite les pixels de bord mélangés au fond gris

    v = np.asarray(tri.vertices)
    to_cam = np.array([0.0, 0.0, CAMERA_DISTANCE]) - v
    cos = (np.asarray(tri.vertex_normals) * to_cam).sum(1) / np.linalg.norm(to_cam, axis=1)
    depth = CAMERA_DISTANCE - v[:, 2]
    t = np.tan(np.radians(CAMERA_FOVY) / 2.0)
    ix = np.clip(((v[:, 0] / (depth * t) + 1) / 2 * (size - 1)).round().astype(int), 0, size - 1)
    iy = np.clip(((1 - v[:, 1] / (depth * t)) / 2 * (size - 1)).round().astype(int), 0, size - 1)

    flat = iy * size + ix
    zbuf = np.full(size * size, np.inf)
    np.minimum.at(zbuf, flat, depth)
    visible = (depth <= zbuf[flat] + DEPTH_EPSILON) & alpha[iy, ix] & (cos > MIN_FACING_COS)
    weight = np.clip((cos - MIN_FACING_COS) / 0.5, 0.0, 1.0) * visible

    model_rgb = np.asarray(tri.visual.vertex_colors)[:, :3].astype(np.float32)
    blended = weight[:, None] * rgb[iy, ix] + (1.0 - weight[:, None]) * model_rgb
    tri.visual.vertex_colors = np.column_stack(
        [blended.round().astype(np.uint8), np.full(len(v), 255, np.uint8)])
    return float(visible.mean())


def _triposr_mesh(image, mc_resolution):
    model, torch = _get_model()
    with torch.no_grad():
        codes = model([image], device="cpu")
        tri = model.extract_mesh(codes, True, resolution=mc_resolution)[0]
    # TripoSR : Z haut, caméra sur +X, droite = +Y  ->  glTF : Y haut, +Z vers la caméra, droite = +X
    tri.vertices = tri.vertices[:, [1, 2, 0]]
    return tri


def _finish_or_fallback(tri, image, mask, texture_size, target_faces, smooth_iterations):
    """Lissage + décimation + texture cuite ; en cas d'échec, couleurs par sommet (signalé dans le rapport)."""
    try:
        textured, info = finish_mesh.finish(
            tri, image, mask, texture_size, target_faces, smooth_iterations, CAMERA_DISTANCE, CAMERA_FOVY)
        info["texture"] = "baked"
        return textured, info
    except Exception as exc:
        visible = _project_photo_colors(tri, image, mask)
        return tri, {"watertight": bool(tri.is_watertight), "faces": int(len(tri.faces)),
                     "photo_visible_fraction": round(visible, 3),
                     "texture": f"vertex-colors (repli : {type(exc).__name__}: {exc})"[:160]}


def reconstruct(image_path, out_dir, mc_resolution=256, backend="auto",
                texture_size=DEFAULT_TEXTURE_SIZE, target_faces=DEFAULT_TARGET_FACES):
    """backend : 'auto' (révolution si la silhouette l'est, sinon TripoSR), 'triposr' ou 'revolve'."""
    import trimesh

    if backend not in ("auto", "triposr", "revolve"):
        raise ValueError(f"backend inconnu : {backend}")
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    image, mask, matte = _prepare_input(image_path, out_dir)

    if backend == "auto":
        backend = "revolve" if looks_like_revolution(mask)[0] else "triposr"

    if backend == "revolve":  # déjà lisse et léger : seule la texture est cuite
        tri = build_revolve_mesh(mask, np.asarray(image), CAMERA_DISTANCE, CAMERA_FOVY)
        final, info = _finish_or_fallback(tri, image, mask, texture_size, None, 0)
    else:
        tri = _triposr_mesh(image, mc_resolution)
        if tri.volume < 0:
            tri.invert()
        tri = _drop_tiny_components(tri)
        trimesh.repair.fill_holes(tri)
        final, info = _finish_or_fallback(tri, image, mask, texture_size, target_faces, finish_mesh.SMOOTH_ITERATIONS)

    glb_path = os.path.join(out_dir, "mesh.glb")
    with open(glb_path, "wb") as f:
        f.write(trimesh.exchange.gltf.export_glb(trimesh.Scene(final), include_normals=True))
    report = {
        "image": image_path,
        "glb": glb_path,
        "seconds": round(time.time() - t0, 1),
        "vertices": int(len(final.vertices)),
        "faces": info["faces"],
        "watertight": info["watertight"],
        "silhouette_iou_front": round(silhouette_iou(mask, final), 3),
        "texture": info["texture"],
        "photo_visible_fraction": info["photo_visible_fraction"],
        "glb_megabytes": round(os.path.getsize(glb_path) / 1e6, 2),
        "matte_coverage": round(matte["coverage"], 3),
        "matte_objects": matte["objects"],
        "backend": backend,
        "monocular_estimate": True,
    }
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python neural_reconstruct.py <image> <out_dir>")
    print(json.dumps(reconstruct(sys.argv[1], sys.argv[2]), indent=2))
