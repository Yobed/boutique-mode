"""
revolve_solid.py — Solide de révolution depuis une silhouette détourée (vases, carafes, pots).

TripoSR reconstruit ces objets en lame plate quand la photo est peu texturée. Un solide
axisymétrique est entièrement déterminé par son profil : on le lit sur la silhouette, on le
fait tourner autour de l'axe vertical, et on colore chaque sommet avec le pixel de la photo
situé à la même abscisse (le dos reprend les couleurs de la face par symétrie).

Le maillage est produit dans le repère de la caméra de TripoSR (voir neural_reconstruct.py) pour
que la mesure de fidélité et le repère glTF soient identiques pour les deux moteurs.
"""

import numpy as np

SECTIONS = 96
PROFILE_ROWS = 160
SMOOTH_WINDOW = 5
MIN_RADIUS_PX = 1.0
CLASSIFIER_SIZE = 256


def looks_like_revolution(mask):
    """Vrai si la silhouette est celle d'un solide de révolution (règle de semantic_classifier)."""
    from PIL import Image
    from semantic_classifier import extract_visual_metrics

    small = np.array(Image.fromarray((mask * 255).astype(np.uint8)).resize(
        (CLASSIFIER_SIZE, CLASSIFIER_SIZE), Image.NEAREST)) > 127
    ys, xs = np.where(small)
    if len(xs) == 0:
        return False, {}
    bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
    metrics = extract_visual_metrics(small.tolist(), bbox, CLASSIFIER_SIZE, CLASSIFIER_SIZE)
    return bool(metrics["is_revolution_candidate"]), metrics


def _profile(mask):
    """Rayon (px) et abscisse d'axe par ligne, du haut vers le bas, lissés."""
    ys, xs = np.where(mask)
    top, bottom = ys.min(), ys.max()
    rows = np.linspace(top, bottom, PROFILE_ROWS).round().astype(int)
    left = np.array([np.where(mask[y])[0].min() if mask[y].any() else np.nan for y in rows], dtype=float)
    right = np.array([np.where(mask[y])[0].max() if mask[y].any() else np.nan for y in rows], dtype=float)
    valid = ~np.isnan(left)
    idx = np.arange(len(rows))
    left = np.interp(idx, idx[valid], left[valid])
    right = np.interp(idx, idx[valid], right[valid])

    kernel = np.ones(SMOOTH_WINDOW) / SMOOTH_WINDOW
    pad = SMOOTH_WINDOW // 2
    smooth = lambda a: np.convolve(np.pad(a, pad, mode="edge"), kernel, mode="valid")  # noqa: E731
    left, right = smooth(left), smooth(right)
    axis = float(np.median((left + right) / 2.0))
    radius = np.maximum((right - left) / 2.0, MIN_RADIUS_PX)
    return rows, left, right, radius, axis


def build_revolve_mesh(mask, rgb, camera_distance, fovy_deg):
    """Maillage fermé coloré, dans le repère glTF de la caméra de TripoSR (y haut, +z vers la caméra)."""
    import trimesh

    size = mask.shape[0]
    rows, left, right, radius_px, axis_px = _profile(mask)
    half_extent = camera_distance * np.tan(np.radians(fovy_deg) / 2.0)  # demi-largeur de l'image à l'axe
    to_m = lambda px: (px / (size - 1) * 2.0 - 1.0) * half_extent  # noqa: E731

    n_rows = len(rows)
    theta = np.linspace(0.0, 2.0 * np.pi, SECTIONS, endpoint=False)
    cos_t, sin_t = np.cos(theta), np.sin(theta)

    # Vue en perspective : le bord de silhouette d'un cercle de rayon r est le point de tangence, situé
    # à z_t = r²/D vers la caméra. On retrouve r depuis la demi-largeur observée w (r = w / sqrt(1 + w²/D²))
    # et on remet hauteur et axe à l'échelle (D - z_t)/D pour que la reprojection retombe sur la photo.
    w = radius_px / (size - 1) * 2.0 * half_extent
    r_world = w / np.sqrt(1.0 + (w / camera_distance) ** 2)
    shrink = 1.0 - (r_world ** 2 / camera_distance) / camera_distance

    y = (-to_m(rows.astype(float)) * shrink)[:, None] * np.ones(SECTIONS)
    r = r_world[:, None]
    x = (to_m(axis_px) * shrink)[:, None] + r * cos_t[None, :]
    z = r * sin_t[None, :]
    ring_vertices = np.stack([x, y, z], axis=-1).reshape(-1, 3)

    # Couleur : abscisse orthographique de la face avant ; le dos est le miroir (cos identique).
    cols = np.clip((axis_px + radius_px[:, None] * cos_t[None, :]).round().astype(int), 0, size - 1)
    cols = np.clip(cols, (left + 2)[:, None].astype(int), (right - 2)[:, None].astype(int))
    colors = rgb[rows[:, None], cols].reshape(-1, 3)

    top_center = np.array([x[0].mean(), y[0, 0], 0.0])
    bottom_center = np.array([x[-1].mean(), y[-1, 0], 0.0])
    vertices = np.vstack([ring_vertices, top_center, bottom_center])
    colors = np.vstack([colors, rgb[rows[0], int(axis_px)], rgb[rows[-1], int(axis_px)]])
    top_idx, bottom_idx = len(ring_vertices), len(ring_vertices) + 1

    j = np.arange(SECTIONS)
    faces = []
    for i in range(n_rows - 1):
        a, b = i * SECTIONS + j, i * SECTIONS + (j + 1) % SECTIONS
        c, d = (i + 1) * SECTIONS + j, (i + 1) * SECTIONS + (j + 1) % SECTIONS
        faces.append(np.stack([a, b, c], axis=1))
        faces.append(np.stack([b, d, c], axis=1))
    faces.append(np.stack([np.full(SECTIONS, top_idx), (j + 1) % SECTIONS, j], axis=1))
    last = (n_rows - 1) * SECTIONS
    faces.append(np.stack([np.full(SECTIONS, bottom_idx), last + j, last + (j + 1) % SECTIONS], axis=1))

    mesh = trimesh.Trimesh(vertices=vertices, faces=np.vstack(faces), process=False)
    mesh.visual.vertex_colors = np.column_stack([colors.astype(np.uint8), np.full(len(colors), 255, np.uint8)])
    if mesh.volume < 0:
        mesh.invert()
    return mesh
