"""
multiview.py — Modèle 3D fidèle depuis une planche multi-vues (face, dos, côtés, dessus, dessous).

Avec plusieurs vues, la forme n'est plus devinée : elle est reconstruite.
  1. découpe de la planche en panneaux (lignes puis colonnes d'objets, étiquettes ignorées) ;
  2. détourage U²-Net de chaque vue ;
  3. enveloppe visuelle (« space carving ») : un voxel est gardé s'il tombe dans la silhouette de chaque vue ;
     l'orientation des vues dessus/dessous/côtés est choisie par recherche (la bonne maximise le volume) ;
  4. surface lissée, décimée, dépliée en UV ;
  5. texture cuite depuis les vraies photos : chaque texel prend la moyenne des vues qui le voient bien.

Limites : une enveloppe visuelle ne reproduit pas les creux invisibles en silhouette (intérieur d'une poche,
relief d'une poignée vue de face) ; ils sont rendus par la texture. Les vues sont supposées quasi orthographiques.

Repère de sortie : glTF, Y haut, face avant vers +Z, droite = +X, hauteur normalisée à 1.
Convention des vues : « gauche » = caméra en -X (la face avant est à droite de l'image), « droite » = caméra en +X,
« dessus » = dos de l'objet en haut de l'image.
"""

import itertools
import os

import numpy as np
from PIL import Image

DEFAULT_LAYOUT = (4, 4, 5)
VIEW_NAMES = ("front", "back", "left", "right", "top", "bottom", "persp_front", "persp_back")
HULL_VIEWS = ("front", "back", "left", "right", "top", "bottom")

DARK_THRESHOLD = 130
ROW_MIN_HEIGHT = 60
ROW_GAP_PX = 6
COLUMN_GAP_PX = 6
CROP_MARGIN_PX = 8
ALPHA_THRESHOLD = 127
MIN_SPECKLE_FRACTION = 0.0005
CARVE_DILATE_FRACTION = 0.004  # faible : les silhouettes sont lues sur l'image agrandie, les anses ne doivent pas se refermer
SOFT_SIGMA_FRACTION = 0.006   # flou des silhouettes (fraction de la taille de l'image)
SEARCH_GRID = 96
ORIENTATION_MARGIN = 1.02   # gain de volume minimal pour contredire la convention d'orientation d'une vue
HULL_GRID = 256
HULL_SMOOTH_SIGMA = 1.5
MARCHING_STEP = 1
HULL_PAD_VOXELS = 3
ZBUF_SIZE = 512
ALPHA_ERODE_PX = 3
BG_MIN_BRIGHTNESS = 200       # le détourage par couleur ne s'applique qu'aux fonds clairs
BG_OBJECT_MIN_DISTANCE = 35   # objet plus proche que cela du fond : on ne touche pas au détourage
BG_KEY_LOW, BG_KEY_LOW_MAX, BG_KEY_RAMP = 12, 60, 18
BG_KEY_LOW_RATIO, BG_KEY_HIGH_RATIO = 0.25, 0.5
BG_PURE_DISTANCE, BG_PURE_FRACTION = 14, 0.6   # un vrai trou est presque entièrement de la couleur du fond
ALPHA_ERODE_FRACTION = 0.015  # le bord de la silhouette mélange objet et fond : on ne lit pas la couleur dessus
FACING_MIN_COS = 0.3
FACING_POWER = 4
CONFIDENT_WEIGHT = (0.8 - FACING_MIN_COS) ** FACING_POWER  # une vue qui regarde le texel à ~37° suffit
DEPTH_EPSILON_FRACTION = 0.02
MIN_COMPONENT_FRACTION = 0.01
SMOOTH_ITERATIONS = 30

# direction de la caméra de chaque vue (de l'objet vers la caméra), repère final
CAMERA_DIRECTION = {
    "front": (0, 0, 1), "back": (0, 0, -1), "left": (-1, 0, 0), "right": (1, 0, 0),
    "top": (0, 1, 0), "bottom": (0, -1, 0),
}


# ----------------------------------------------------------------------------- découpe de la planche
def _segments(active, gap):
    """Intervalles [a, b) de True consécutifs, en fusionnant les trous de moins de `gap`."""
    idx = np.flatnonzero(active)
    if len(idx) == 0:
        return []
    cuts = np.flatnonzero(np.diff(idx) > gap)
    starts = np.r_[idx[0], idx[cuts + 1]]
    ends = np.r_[idx[cuts], idx[-1]] + 1
    return list(zip(starts.tolist(), ends.tolist()))


def find_panels(gray, layout):
    """Boîtes (x0, y0, x1, y1) des objets, par rangée, dans l'ordre de lecture. Les étiquettes (fines) sont ignorées."""
    dark = gray < DARK_THRESHOLD
    rows = [r for r in _segments(dark.sum(axis=1) > 2, ROW_GAP_PX) if r[1] - r[0] >= ROW_MIN_HEIGHT]
    if len(rows) != len(layout):
        raise ValueError(f"{len(rows)} rangées détectées, {len(layout)} attendues (layout {layout})")
    boxes = []
    for (y0, y1), count in zip(rows, layout):
        cols = _segments(dark[y0:y1].sum(axis=0) > 2, COLUMN_GAP_PX)
        cols = [c for c in cols if c[1] - c[0] >= ROW_MIN_HEIGHT // 2]
        if len(cols) != count:
            raise ValueError(f"{len(cols)} panneaux détectés dans la rangée y={y0}-{y1}, {count} attendus")
        boxes.append([(x0, y0, x1, y1) for x0, x1 in cols])
    return boxes


def _clean_alpha(alpha):
    """Binarise, supprime les poussières sans boucher les vrais trous (espace entre sangle et dos)."""
    from scipy import ndimage

    mask = alpha > ALPHA_THRESHOLD
    min_size = max(4, int(MIN_SPECKLE_FRACTION * mask.size))
    labels, n = ndimage.label(mask)
    if n:
        sizes = np.bincount(labels.ravel())
        mask = np.isin(labels, np.flatnonzero(sizes >= min_size)) & (labels > 0)
    holes, hn = ndimage.label(~mask)
    if hn:
        hsizes = np.bincount(holes.ravel())
        small = np.isin(holes, np.flatnonzero(hsizes < min_size)) & (holes > 0)
        mask = mask | small
    return mask


def _background_color(crop):
    """Couleur du fond clair uni (médiane du bord du panneau), ou None si le fond n'est pas clair."""
    rgb = np.asarray(crop, np.float32)
    bg = np.median(np.concatenate([rgb[0], rgb[-1], rgb[:, 0], rgb[:, -1]]), axis=0)
    return None if bg.mean() < BG_MIN_BRIGHTNESS else bg


def _key_alpha(rgb, alpha, bg):
    """alpha (0-1) multiplié par la distance à la couleur de fond : les pixels de fond que le détourage (réseau,
    basse résolution) a gardés — typiquement l'espace entre deux anses — redeviennent transparents. Sans effet si
    l'objet est lui-même proche du fond (produit blanc ou ivoire)."""
    distance = np.linalg.norm(np.asarray(rgb, np.float32) - bg, axis=2)
    inside = alpha > 0.5
    if not inside.any():
        return alpha
    contrast = float(np.median(distance[inside]))
    if contrast < BG_OBJECT_MIN_DISTANCE:
        return alpha
    # seuils proportionnels au contraste de l'objet : l'ombre portée et le dégradé du fond d'un sac noir
    # (distance ~30-50 du fond) sont écartés, sans manger les reflets d'un sac clair
    low = float(np.clip(BG_KEY_LOW_RATIO * contrast, BG_KEY_LOW, BG_KEY_LOW_MAX))
    high = max(low + BG_KEY_RAMP, BG_KEY_HIGH_RATIO * contrast)
    keyed = alpha * np.clip((distance - low) / (high - low), 0.0, 1.0)
    return _restore_false_holes(alpha, keyed, distance)


def _restore_false_holes(before, after, distance):
    """Un trou ouvert par le détourage couleur n'est réel que s'il montre vraiment le fond (couleur unie). Les
    reflets clairs d'une ferrure ou d'une fermeture, proches du blanc, ne doivent pas percer l'objet."""
    from scipy import ndimage

    removed = (before > 0.5) & (after <= 0.5)
    labels, n = ndimage.label(removed)
    if not n:
        return after
    outside_contact = ndimage.binary_dilation(before <= 0.5) & removed
    pure = np.bincount(labels.ravel(), weights=(distance < BG_PURE_DISTANCE).ravel(), minlength=n + 1)
    sizes = np.bincount(labels.ravel(), minlength=n + 1)
    enclosed = np.ones(n + 1, bool)
    enclosed[np.unique(labels[outside_contact])] = False
    fake = enclosed & (pure < BG_PURE_FRACTION * sizes)
    fake[0] = False
    return np.where(fake[labels], before, after)


def _key_out_background(crop, alpha):
    """Version uint8 de `_key_alpha` pour un panneau entier ; inchangé sur fond sombre."""
    bg = _background_color(crop)
    if bg is None:
        return alpha
    return (_key_alpha(crop, alpha.astype(np.float32) / 255.0, bg) * 255).astype(np.uint8)


def load_layout(path):
    """Disposition explicite d'une planche : {'boxes': {vue: [x0, y0, x1, y1]}} (pixels de la planche)."""
    import json

    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    ignored = set(data.get("ignore", []))  # vues peu fiables (ex. dessus d'un sac ouvert, en perspective)
    missing = [n for n in HULL_VIEWS if n not in data.get("boxes", {}) and n not in ignored]
    if missing:
        raise ValueError(f"layout {path} : vues manquantes {missing}")
    if not {"front", "left"} <= set(data["boxes"]) - ignored:
        raise ValueError("layout : les vues « front » et « left » ne peuvent pas être ignorées")
    return {name: tuple(int(v) for v in box) for name, box in data["boxes"].items() if name not in ignored}


def extract_views(sheet_path, layout=DEFAULT_LAYOUT, names=VIEW_NAMES, boxes=None, enhance=True):
    """dict nom -> {'rgb': (h,w,3) uint8, 'mask': (h,w) bool} recadrés exactement sur la silhouette.

    `boxes` (vue -> rectangle) remplace la détection automatique : planches à fond clair, paires à scinder en moitiés."""
    import neural_reconstruct as nr

    sheet = Image.open(sheet_path).convert("RGB")
    if boxes is not None:
        margin, panels = 0, list(boxes.items())  # rectangles fournis : tels quels, sans empiéter sur les voisins
    else:
        gray = np.asarray(sheet.convert("L"))
        margin, panels = CROP_MARGIN_PX, list(zip(names, [b for row in find_panels(gray, layout) for b in row]))
    views = {}
    for name, (x0, y0, x1, y1) in panels:
        box = (max(0, x0 - margin), max(0, y0 - margin), min(sheet.width, x1 + margin), min(sheet.height, y1 + margin))
        crop = sheet.crop(box)
        matte = nr._matte(crop)
        bg = _background_color(crop)
        mask = _clean_alpha(_key_out_background(crop, matte))
        ys, xs = np.nonzero(mask)
        if len(xs) == 0:
            raise ValueError(f"vue « {name} » : aucun objet détecté")
        sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        rgb, alpha = np.asarray(crop)[sl], matte[sl].astype(np.float32) / 255.0
        if enhance:  # super-résolution : texture nette ; le contour est relu sur l'image agrandie (trous nets)
            import upscale
            big = upscale.upscale_rgb(rgb)
            if big.shape != rgb.shape:
                alpha = np.asarray(Image.fromarray(alpha).resize((big.shape[1], big.shape[0]), Image.BICUBIC))
                alpha = np.clip(alpha, 0.0, 1.0)
            rgb = big
        if bg is not None:
            alpha = _key_alpha(rgb, alpha, bg)
        views[name] = {"rgb": rgb, "mask": _clean_alpha(alpha * 255), "alpha": alpha}
    return views


# ----------------------------------------------------------------------------- enveloppe visuelle
def view_uv(name, x, y, z, dims, flip_u=False, flip_v=False):
    """Coordonnées image (u colonne, v ligne, dans [0,1]) du point (x,y,z) pour une vue orthographique."""
    w, h, d = dims
    nx, ny, nz = x / w + 0.5, y / h, z / d + 0.5
    if name == "front":
        u, v = nx, 1 - ny
    elif name == "back":
        u, v = 1 - nx, 1 - ny
    elif name == "left":      # caméra en -x : la face avant est à droite de l'image
        u, v = nz, 1 - ny
    elif name == "right":     # caméra en +x : la face avant est à gauche de l'image
        u, v = 1 - nz, 1 - ny
    elif name == "top":       # caméra en +y, dos de l'objet en haut de l'image
        u, v = nx, nz
    elif name == "bottom":
        u, v = nx, 1 - nz
    else:
        raise KeyError(name)
    return (1 - u if flip_u else u), (1 - v if flip_v else v)


def _lookup(mask, u, v):
    h, w = mask.shape
    col = np.clip((u * (w - 1)).round().astype(int), 0, w - 1)
    row = np.clip((v * (h - 1)).round().astype(int), 0, h - 1)
    return mask[row, col]


def _soft(mask, alpha=None):
    """Silhouette légèrement dilatée puis floutée en champ continu : les bords pixelisés et les petites
    incohérences de perspective entre vues ne créent plus de marches d'escalier dans l'enveloppe.
    `alpha` (0-1, détourage continu) donne des bords sous-pixel ; sinon on part du masque binaire."""
    from scipy import ndimage

    size = max(mask.shape)
    base = alpha if alpha is not None else mask.astype(np.float32)
    grown = ndimage.maximum_filter(base, size=2 * max(1, int(CARVE_DILATE_FRACTION * size)) + 1)
    return ndimage.gaussian_filter(grown.astype(np.float32), SOFT_SIGMA_FRACTION * size)


def _lookup_soft(field, u, v):
    """Lecture bilinéaire d'un champ continu : pas de marches d'escalier à la résolution du panneau."""
    from scipy import ndimage

    h, w = field.shape
    coords = np.stack([np.clip(v * (h - 1), 0, h - 1).ravel(), np.clip(u * (w - 1), 0, w - 1).ravel()])
    return ndimage.map_coordinates(field, coords, order=1, mode="nearest").reshape(np.shape(u))


def estimate_dims(views):
    """(largeur, hauteur=1, profondeur) depuis les proportions des silhouettes (médiane sur les vues)."""
    def aspect(name):
        h, w = views[name]["mask"].shape
        return w / h
    widths = [aspect(n) for n in ("front", "back") if n in views]
    depths = [aspect(n) for n in ("left", "right") if n in views]
    if "top" in views:
        top_ratio = views["top"]["mask"].shape[1] / views["top"]["mask"].shape[0]  # largeur / profondeur
        widths.append(np.median(depths) * top_ratio)
    return float(np.median(widths)), 1.0, float(np.median(depths))


def active(views):
    """Les vues réellement utilisées (certaines peuvent être ignorées par la disposition)."""
    return [n for n in HULL_VIEWS if n in views]


def grid_coords(dims, resolution):
    w, h, d = dims
    voxel = max(w, h, d) / resolution
    nx, ny, nz = (int(np.ceil(s / voxel)) for s in (w, h, d))
    xs = (np.arange(nx) + 0.5) * voxel - w / 2
    ys = (np.arange(ny) + 0.5) * voxel
    zs = (np.arange(nz) + 0.5) * voxel - d / 2
    return xs, ys, zs, voxel


def carve(views, dims, flips, resolution, names=None):
    """Champ continu de l'enveloppe (minimum des silhouettes souples) ; l'objet est le niveau 0,5."""
    names = names or active(views)
    xs, ys, zs, voxel = grid_coords(dims, resolution)
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
    field = np.ones(x.shape, np.float32)
    for name in names:
        u, v = view_uv(name, x, y, z, dims, *flips.get(name, (False, False)))
        np.minimum(field, _lookup_soft(views[name]["soft"], u, v).astype(np.float32), out=field)
    return field, (xs, ys, zs, voxel)


def choose_orientations(views, dims):
    """Pour chaque vue sans orientation certaine, la symétrie qui laisse le plus de volume est la bonne."""
    for v in views.values():
        v.setdefault("soft", _soft(v["mask"], v.get("alpha")))
    flips = {}
    for name in [n for n in ("left", "right", "top", "bottom") if n in views]:
        def volume_of(flip):
            trial = {**flips, name: flip}
            done = [n for n in active(views) if n in trial or n in ("front", "back")]
            return (carve(views, dims, trial, SEARCH_GRID, names=done)[0] > 0.5).sum()

        # La convention fait foi : un objet presque symétrique avant/arrière (sac) donne des volumes quasi égaux
        # pour les deux orientations (écarts < 2 % = bruit) ; on ne retourne la vue que pour un gain net.
        best, best_volume = (False, False), volume_of((False, False))
        reference = best_volume
        for flip in itertools.product((False, True), repeat=2):
            volume = volume_of(flip)
            if volume > max(best_volume, reference * ORIENTATION_MARGIN):
                best, best_volume = flip, volume
        flips[name] = best
    return flips


def reprojection_iou(views, volume_grid, dims, flips):
    """IoU entre la silhouette de l'enveloppe et celle de chaque vue (contrôle de cohérence des vues)."""
    from scipy import ndimage

    keep, (xs, ys, zs, _) = volume_grid
    x, y, z = np.meshgrid(xs, ys, zs, indexing="ij")
    ious = {}
    rows = min(160, max(len(xs), len(ys), len(zs)))  # au plus un voxel par pixel : projection sans trous
    for name in active(views):
        mask = views[name]["mask"]
        h, w = rows, max(8, int(rows * mask.shape[1] / mask.shape[0]))
        uu, vv = np.meshgrid((np.arange(w) + 0.5) / w, (np.arange(h) + 0.5) / h)
        target = _lookup(mask, uu, vv)
        projected = np.zeros((h, w), bool)
        u, v = view_uv(name, x[keep], y[keep], z[keep], dims, *flips.get(name, (False, False)))
        projected[np.clip((v * (h - 1)).round().astype(int), 0, h - 1),
                  np.clip((u * (w - 1)).round().astype(int), 0, w - 1)] = True
        projected = ndimage.binary_closing(projected, iterations=2)
        ious[name] = float((projected & target).sum() / max(1, (projected | target).sum()))
    return ious


# ----------------------------------------------------------------------------- maillage
def hull_mesh(field, grid):
    import trimesh
    from scipy import ndimage
    from skimage import measure

    xs, ys, zs, voxel = grid
    pad = HULL_PAD_VOXELS
    volume = np.pad(field, pad)
    volume = ndimage.gaussian_filter(volume, HULL_SMOOTH_SIGMA)
    # pas de 2 : ~4x moins de faces (le champ est déjà flouté sur 1,5 voxel) ; une décimation lourde ensuite
    # casserait l'étanchéité sur les anses fines
    verts, faces, _, _ = measure.marching_cubes(volume, level=0.5, step_size=MARCHING_STEP)
    origin = np.array([xs[0], ys[0], zs[0]]) - pad * voxel
    mesh = trimesh.Trimesh(vertices=origin + verts * voxel, faces=faces, process=True)
    parts = mesh.split(only_watertight=False)
    keep_parts = [p for p in parts if len(p.faces) >= MIN_COMPONENT_FRACTION * len(mesh.faces)]
    if len(keep_parts) != len(parts):
        mesh = trimesh.util.concatenate(keep_parts)
    if mesh.volume < 0:
        mesh.invert()
    trimesh.repair.fill_holes(mesh)
    return mesh


# ----------------------------------------------------------------------------- texture multi-vues
def bake_views_texture(vertices, faces, uvs, normals, views, dims, flips, size):
    """Texture : moyenne, par texel, des vues qui le voient bien (pondérée par l'orientation)."""
    import finish_mesh as fm
    from scipy import ndimage

    positions, tex_normals, covered = fm.rasterize_uv(faces, uvs, vertices, normals, size)
    ys, xs = np.nonzero(covered)
    pos = positions[ys, xs].astype(np.float64)
    nrm = tex_normals[ys, xs].astype(np.float64)
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)

    total_w = np.zeros(len(pos))
    total_c = np.zeros((len(pos), 3))
    extent = max(dims)
    for name in active(views):
        cam = np.array(CAMERA_DIRECTION[name], float)
        cos = nrm @ cam
        depth = -(pos @ cam)  # plus petit = plus près de la caméra
        u, v = view_uv(name, pos[:, 0], pos[:, 1], pos[:, 2], dims, *flips.get(name, (False, False)))
        zi = np.clip((u * (ZBUF_SIZE - 1)).round().astype(int), 0, ZBUF_SIZE - 1)
        zj = np.clip((v * (ZBUF_SIZE - 1)).round().astype(int), 0, ZBUF_SIZE - 1)
        flat = zj * ZBUF_SIZE + zi
        zbuf = np.full(ZBUF_SIZE * ZBUF_SIZE, np.inf)
        np.minimum.at(zbuf, flat, depth)
        erosion = max(ALPHA_ERODE_PX, int(ALPHA_ERODE_FRACTION * max(views[name]["mask"].shape)))
        eroded = ndimage.binary_erosion(views[name]["mask"], iterations=erosion)
        inside = _lookup(eroded, u, v)
        visible = (depth <= zbuf[flat] + DEPTH_EPSILON_FRACTION * extent) & inside
        # puissance élevée : la vue qui regarde le mieux le texel l'emporte, les vues rasantes (pixels étirés,
        # source des bandes « tartan ») pèsent quasi zéro ; au voisinage de 45° deux vues se partagent la zone
        weight = np.clip(cos - FACING_MIN_COS, 0, None) ** FACING_POWER * visible
        h, w = views[name]["mask"].shape
        photo = views[name]["rgb"].astype(np.float32)
        colors = fm._sample_rgb(photo, np.clip(v * (h - 1), 0, h - 1), np.clip(u * (w - 1), 0, w - 1))
        total_w += weight
        total_c += colors * weight[:, None]

    averaged = total_c / np.maximum(total_w, 1e-6)[:, None]
    confidence = np.clip(total_w / CONFIDENT_WEIGHT, 0, 1).astype(np.float32)
    final = fm._fill_hidden(pos.astype(np.float32), averaged.astype(np.float32), confidence)

    texture = np.zeros((size, size, 3), np.uint8)
    texture[ys, xs] = np.clip(final, 0, 255).round().astype(np.uint8)
    nearest = ndimage.distance_transform_edt(~covered, return_distances=False, return_indices=True)
    texture = texture[nearest[0], nearest[1]]
    return Image.fromarray(texture), float((total_w > 0.05).mean())


# ----------------------------------------------------------------------------- pipeline complet
def reconstruct_sheet(sheet_path, out_dir, layout=DEFAULT_LAYOUT, texture_size=2048, target_faces=60_000,
                      boxes=None):
    """Planche -> GLB texturé + rapport (mêmes clés que neural_reconstruct.reconstruct)."""
    import json
    import time

    import finish_mesh as fm
    import trimesh

    t0 = time.time()
    os.makedirs(out_dir, exist_ok=True)
    views = extract_views(sheet_path, layout, boxes=boxes)
    dims = estimate_dims(views)
    flips = choose_orientations(views, dims)
    field, grid = carve(views, dims, flips, HULL_GRID)
    keep = field > 0.5
    if keep.sum() == 0:
        raise ValueError("enveloppe vide : les silhouettes sont incohérentes")
    ious = reprojection_iou(views, (keep, grid), dims, flips)

    mesh = hull_mesh(field, grid)
    mesh = fm.decimate(fm.smooth(mesh, SMOOTH_ITERATIONS), target_faces)
    watertight = bool(mesh.is_watertight)
    vertices, faces, uvs, normals = fm.unwrap(mesh)
    texture, covered = bake_views_texture(vertices, faces, uvs, normals, views, dims, flips, texture_size)
    material = fm.make_material(texture)
    final = trimesh.Trimesh(vertices=vertices, faces=faces, process=False,
                            visual=trimesh.visual.TextureVisuals(uv=uvs, material=material))
    final.vertex_normals = normals

    glb_path = os.path.join(out_dir, "mesh.glb")
    with open(glb_path, "wb") as f:
        f.write(trimesh.exchange.gltf.export_glb(trimesh.Scene(final), include_normals=True))

    front_rgba = np.dstack([views["front"]["rgb"], (views["front"]["mask"] * 255).astype(np.uint8)])
    Image.fromarray(front_rgba, "RGBA").save(os.path.join(out_dir, "cutout.png"))

    report = {
        "image": sheet_path, "glb": glb_path, "seconds": round(time.time() - t0, 1),
        "vertices": int(len(final.vertices)), "faces": int(len(faces)), "watertight": watertight,
        "silhouette_iou_front": round(float(np.mean(list(ious.values()))), 3),  # moyenne des 6 vues
        "view_ious": {k: round(v, 3) for k, v in ious.items()},
        "orientations": {k: list(v) for k, v in flips.items()},
        "dimensions_w_h_d": [round(s, 3) for s in dims],
        "texture": "baked-multiview", "texture_covered_fraction": round(covered, 3),
        "glb_megabytes": round(os.path.getsize(glb_path) / 1e6, 2),
        "matte_coverage": round(float(views["front"]["mask"].mean()), 3), "matte_objects": 1,
        "backend": "multiview", "monocular_estimate": False,
    }
    with open(os.path.join(out_dir, "report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    return report
