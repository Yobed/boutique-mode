"""
finish_mesh.py — Finition d'un maillage reconstruit : surface lisse, maillage léger, texture nette.

Pourquoi : la sortie brute de TripoSR est granuleuse (bruit du champ de densité) et ses couleurs, portées
par les sommets, sont floues. Ici :
  1. lissage de Taubin (adoucit la surface sans la faire rétrécir) ;
  2. décimation quadrique vers un nombre de faces adapté au web ;
  3. dépliage UV (xatlas) ;
  4. cuisson d'une texture : pixels de la photo sur tout ce que la caméra voit ; faces cachées remplies par la
     moyenne des couleurs visibles voisines (cohérent, sans les teintes pastel parasites du réseau) ;
  5. matériau PBR mat, normales lisses reprises du maillage avant dépliage.

Repère : celui de neural_reconstruct (glTF, caméra sur +Z à CAMERA_DISTANCE, champ vertical CAMERA_FOVY).
"""

import io

import numpy as np
from PIL import Image

SMOOTH_ITERATIONS = 20
DECIMATION_LEVELS = (2, 0)  # du plus efficace au plus prudent
DECIMATION_TOLERANCE = 1.1
MAX_DECIMATION_PASSES = 10
DECIMATION_STEP = 2.0   # réduction maximale par passe
TAUBIN_LAMBDA, TAUBIN_NU = 0.5, 0.53
MIN_FACING_COS = 0.5      # en dessous, la photo est trop étirée : on remplit depuis les zones bien vues
FACING_RAMP = 0.3         # fondu photo -> remplissage entre MIN_FACING_COS et MIN_FACING_COS + FACING_RAMP
DEPTH_EPSILON = 0.02
ZBUF_SIZE = 1024
ALPHA_ERODE_PX = 6
FILL_NEIGHBOURS = 64      # moyenne large : le dos reprend la teinte de la matière, pas un détail local
FILL_SAMPLE_LIMIT = 40_000
FILL_EPSILON = 0.3
QUERY_CHUNK = 50_000
BARYCENTRIC_TOLERANCE = 0.02
JPEG_QUALITY = 90
ROUGHNESS = 0.6
MAP_SIZE = 1024                 # cartes de relief et de métal/rugosité
GRAIN_SIGMA = 3.0               # px : sépare le grain fin de l'ombrage cuit dans la photo
NORMAL_STRENGTH = 0.6
GOLD_HUE = (0.09, 0.17)         # teinte jaune-or (0-1) ; un cuir camel ou beige reste en dessous
GOLD_MIN_SATURATION, GOLD_MIN_VALUE = 0.4, 0.55
MAX_METAL_FRACTION = 0.08       # au-delà, la matière « dorée » est le produit lui-même, pas la quincaillerie
BASE_ROUGHNESS, METAL_ROUGHNESS = 0.55, 0.28


def smooth(tri, iterations=SMOOTH_ITERATIONS):
    import trimesh

    out = tri.copy()
    if iterations > 0:
        trimesh.smoothing.filter_taubin(out, lamb=TAUBIN_LAMBDA, nu=TAUBIN_NU, iterations=iterations)
    return out


def repair_nonmanifold(mesh, attempts=3):
    """Retire les (rares) faces autour des arêtes non-manifold créées par la décimation, puis rebouche les trous."""
    import trimesh

    for _ in range(attempts):
        edges = mesh.edges_sorted  # 3 arêtes par face, dans l'ordre des faces
        _, inverse, counts = np.unique(edges, axis=0, return_inverse=True, return_counts=True)
        bad_edges = counts[inverse.reshape(-1)] > 2
        if not bad_edges.any():
            break
        keep = np.ones(len(mesh.faces), bool)
        keep[np.unique(np.nonzero(bad_edges)[0] // 3)] = False
        mesh = trimesh.Trimesh(vertices=mesh.vertices, faces=mesh.faces[keep], process=True)
        trimesh.repair.fill_holes(mesh)
    return mesh


def decimate(tri, target_faces):
    """Réduction quadrique ; conserve la forme et la topologie fermée dans la quasi-totalité des cas."""
    import fast_simplification
    import trimesh

    current = tri
    for _ in range(MAX_DECIMATION_PASSES):
        if not target_faces or len(current.faces) <= target_faces * DECIMATION_TOLERANCE:
            break
        # Le défaut de la bibliothèque (agg=7) crée des arêtes non-manifold, donc un maillage non étanche.
        # On essaie des niveaux plus doux ; chaque passe réduit moins, d'où l'itération.
        accepted = None
        # paliers : un grand saut (ex. 360 000 -> 60 000 faces) casse l'étanchéité, une réduction par deux la préserve
        step_target = max(int(target_faces), int(len(current.faces) / DECIMATION_STEP))
        for aggressiveness in DECIMATION_LEVELS:
            vertices, faces = fast_simplification.simplify(
                np.asarray(current.vertices), np.asarray(current.faces),
                target_count=step_target, agg=aggressiveness)
            candidate = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
            if not candidate.is_watertight and current.is_watertight:
                candidate = repair_nonmanifold(candidate)
            if candidate.is_watertight or not current.is_watertight:
                accepted = candidate
                break
        if accepted is None or len(accepted.faces) >= len(current.faces):
            break  # plus de réduction possible sans perdre l'étanchéité
        current = accepted
    return current


def unwrap(tri):
    """Dépliage UV : retourne (sommets, faces, uvs, normales lisses) avec sommets dédoublés aux coutures."""
    import xatlas

    vmapping, indices, uvs = xatlas.parametrize(
        np.asarray(tri.vertices, dtype=np.float32), np.asarray(tri.faces, dtype=np.uint32))
    return (np.asarray(tri.vertices)[vmapping], indices.astype(np.int64), uvs,
            np.asarray(tri.vertex_normals)[vmapping])


def rasterize_uv(faces, uvs, vertices, normals, size):
    """Position et normale 3D de chaque texel couvert par le dépliage."""
    px = np.column_stack([uvs[:, 0] * (size - 1), (1.0 - uvs[:, 1]) * (size - 1)])
    positions = np.zeros((size, size, 3), np.float32)
    out_normals = np.zeros((size, size, 3), np.float32)
    covered = np.zeros((size, size), bool)

    for face in faces:
        a, b, c = px[face]
        denom = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(denom) < 1e-12:
            continue
        lo = np.maximum(np.floor(px[face].min(0)).astype(int) - 1, 0)
        hi = np.minimum(np.ceil(px[face].max(0)).astype(int) + 1, size - 1)
        xs, ys = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1))
        dx, dy = xs - a[0], ys - a[1]
        w1 = (dx * (c[1] - a[1]) - (c[0] - a[0]) * dy) / denom
        w2 = ((b[0] - a[0]) * dy - dx * (b[1] - a[1])) / denom
        w0 = 1.0 - w1 - w2
        inside = (w0 >= -BARYCENTRIC_TOLERANCE) & (w1 >= -BARYCENTRIC_TOLERANCE) & (w2 >= -BARYCENTRIC_TOLERANCE)
        if not inside.any():
            continue
        xi, yi = xs[inside], ys[inside]
        weights = np.stack([w0[inside], w1[inside], w2[inside]], axis=1)
        positions[yi, xi] = weights @ vertices[face]
        out_normals[yi, xi] = weights @ normals[face]
        covered[yi, xi] = True
    return positions, out_normals, covered


def _project(pos, camera_distance, fovy_deg, size):
    depth = camera_distance - pos[:, 2]
    t = np.tan(np.radians(fovy_deg) / 2.0)
    col = (pos[:, 0] / (depth * t) + 1.0) / 2.0 * (size - 1)
    row = (1.0 - pos[:, 1] / (depth * t)) / 2.0 * (size - 1)
    return depth, col, row


def _sample_rgb(photo, rows, cols):
    from scipy import ndimage

    coords = np.stack([rows, cols])
    return np.stack([ndimage.map_coordinates(photo[..., ch], coords, order=1, mode="nearest")
                     for ch in range(3)], axis=1)


def _fill_hidden(pos, colors, weight):
    """Faces non visibles : moyenne pondérée des couleurs visibles voisines (dans l'espace 3D)."""
    from scipy import spatial

    visible = np.nonzero(weight > 0.5)[0]
    need = np.nonzero(weight < 0.999)[0]
    if len(need) == 0:
        return colors
    if len(visible) < FILL_NEIGHBOURS:
        out = colors.copy()
        out[need] = colors[weight > 0].mean(0) if (weight > 0).any() else 128.0
        return out
    rng = np.random.default_rng(0)
    sample = visible if len(visible) <= FILL_SAMPLE_LIMIT else rng.choice(visible, FILL_SAMPLE_LIMIT, replace=False)
    tree = spatial.cKDTree(pos[sample])
    fill = np.zeros((len(pos), 3), np.float32)
    for start in range(0, len(need), QUERY_CHUNK):
        chunk = need[start:start + QUERY_CHUNK]
        # recherche approchée : pour le dos d'un objet plat tous les points visibles sont presque
        # équidistants et la recherche exacte devient quadratique (plusieurs minutes)
        dist, idx = tree.query(pos[chunk], k=FILL_NEIGHBOURS, eps=FILL_EPSILON, workers=-1)
        inv = 1.0 / (dist + 0.05)  # amortissement : les plus proches voisins ne dominent pas
        fill[chunk] = (colors[sample][idx] * inv[..., None]).sum(1) / inv.sum(1)[:, None]
    blended = weight[:, None] * colors + (1.0 - weight[:, None]) * fill
    return np.where((weight < 0.999)[:, None], blended, colors)


def bake_texture(vertices, faces, uvs, normals, image, alpha_sq, size, camera_distance, fovy_deg):
    """Texture (PIL RGB) : photo sur les parties vues par la caméra, couleurs voisines ailleurs."""
    from scipy import ndimage

    positions, tex_normals, covered = rasterize_uv(faces, uvs, vertices, normals, size)
    ys, xs = np.nonzero(covered)
    pos = positions[ys, xs]
    nrm = tex_normals[ys, xs]
    nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-9)

    photo = np.asarray(image, dtype=np.float32)
    s0 = photo.shape[0]
    alpha = np.array(Image.fromarray((alpha_sq * 255).astype(np.uint8)).resize((s0, s0), Image.NEAREST)) > 127
    alpha = ndimage.binary_erosion(alpha, iterations=ALPHA_ERODE_PX)

    to_cam = np.array([0.0, 0.0, camera_distance]) - pos
    cos = (nrm * to_cam).sum(1) / np.linalg.norm(to_cam, axis=1)
    depth, cols, rows = _project(pos, camera_distance, fovy_deg, s0)

    zi = np.clip((cols / (s0 - 1) * (ZBUF_SIZE - 1)).round().astype(int), 0, ZBUF_SIZE - 1)
    zj = np.clip((rows / (s0 - 1) * (ZBUF_SIZE - 1)).round().astype(int), 0, ZBUF_SIZE - 1)
    flat = zj * ZBUF_SIZE + zi
    zbuf = np.full(ZBUF_SIZE * ZBUF_SIZE, np.inf)
    np.minimum.at(zbuf, flat, depth)
    ci = np.clip(cols.round().astype(int), 0, s0 - 1)
    ri = np.clip(rows.round().astype(int), 0, s0 - 1)
    visible = (depth <= zbuf[flat] + DEPTH_EPSILON) & alpha[ri, ci] & (cos > MIN_FACING_COS)
    weight = (np.clip((cos - MIN_FACING_COS) / FACING_RAMP, 0.0, 1.0) * visible).astype(np.float32)

    colors = _sample_rgb(photo, np.clip(rows, 0, s0 - 1), np.clip(cols, 0, s0 - 1)).astype(np.float32)
    final = _fill_hidden(pos, colors, weight)

    texture = np.zeros((size, size, 3), np.uint8)
    texture[ys, xs] = np.clip(final, 0, 255).round().astype(np.uint8)
    nearest = ndimage.distance_transform_edt(~covered, return_distances=False, return_indices=True)
    texture = texture[nearest[0], nearest[1]]  # marge : évite les liserés aux bords des îlots UV
    return Image.fromarray(texture), float(visible.mean())


def _as_jpeg(img):
    buffer = io.BytesIO()
    img.save(buffer, "JPEG", quality=JPEG_QUALITY, optimize=True)
    buffer.seek(0)
    out = Image.open(buffer)
    out.load()
    return out  # format JPEG conservé : trimesh l'écrit tel quel dans le GLB (3-4 fois plus léger que PNG)


def material_maps(texture):
    """Cartes PBR dérivées de la texture : relief fin (grain, tissage) et métal/rugosité (ferrures dorées).

    Le relief vient des détails de la texture débarrassés de l'ombrage cuit ; les ferrures dorées sont repérées par
    la teinte. Si le « doré » couvre trop de surface, c'est la matière principale (sac jaune) : pas de métal."""
    from scipy import ndimage

    rgb = np.asarray(texture.resize((MAP_SIZE, MAP_SIZE), Image.LANCZOS), np.float32) / 255.0
    lum = rgb @ np.array([0.299, 0.587, 0.114], np.float32)
    detail = lum - ndimage.gaussian_filter(lum, GRAIN_SIGMA)
    detail = detail / (detail.std() + 1e-6)
    gy, gx = np.gradient(ndimage.gaussian_filter(detail, 0.7))
    normal = np.dstack([-gx * NORMAL_STRENGTH, gy * NORMAL_STRENGTH, np.ones_like(lum)])
    normal /= np.linalg.norm(normal, axis=2, keepdims=True)

    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    top, bottom = rgb.max(2), rgb.min(2)
    delta = np.maximum(top - bottom, 1e-6)
    hue = np.where(top == r, ((g - b) / delta) % 6, np.where(top == g, (b - r) / delta + 2, (r - g) / delta + 4)) / 6.0
    saturation = (top - bottom) / np.maximum(top, 1e-6)
    metal = ((hue >= GOLD_HUE[0]) & (hue <= GOLD_HUE[1]) & (saturation >= GOLD_MIN_SATURATION)
             & (top >= GOLD_MIN_VALUE)).astype(np.float32)
    if metal.mean() > MAX_METAL_FRACTION:
        metal[:] = 0.0
    metal = ndimage.gaussian_filter(metal, 1.0)
    roughness = (BASE_ROUGHNESS - 0.04 * np.clip(detail, -2, 2)) * (1 - metal) + METAL_ROUGHNESS * metal

    to_image = lambda a: Image.fromarray((np.clip(a, 0, 1) * 255).round().astype(np.uint8))  # noqa: E731
    return to_image(normal * 0.5 + 0.5), to_image(np.dstack([np.zeros_like(lum), roughness, metal]))


def make_material(texture):
    """Matériau PBR : couleur de base (texture cuite), relief fin, métal/rugosité."""
    import trimesh

    normal, metallic_roughness = material_maps(texture)
    return trimesh.visual.material.PBRMaterial(
        baseColorTexture=_as_jpeg(texture), normalTexture=_as_jpeg(normal),
        metallicRoughnessTexture=_as_jpeg(metallic_roughness), metallicFactor=1.0, roughnessFactor=1.0)


def finish(tri, image, alpha_sq, texture_size, target_faces, smooth_iterations,
           camera_distance, fovy_deg):
    """Retourne (maillage texturé, infos). `tri` : maillage fermé en repère glTF caméra."""
    import trimesh

    work = decimate(smooth(tri, smooth_iterations), target_faces)
    watertight = bool(work.is_watertight)
    vertices, faces, uvs, normals = unwrap(work)
    texture, visible_fraction = bake_texture(
        vertices, faces, uvs, normals, image, alpha_sq, texture_size, camera_distance, fovy_deg)

    material = make_material(texture)
    out = trimesh.Trimesh(
        vertices=vertices, faces=faces, process=False,
        visual=trimesh.visual.TextureVisuals(uv=uvs, material=material))
    out.vertex_normals = normals
    return out, {"watertight": watertight, "texture_size": texture_size,
                 "photo_visible_fraction": round(visible_fraction, 3), "faces": int(len(faces))}
