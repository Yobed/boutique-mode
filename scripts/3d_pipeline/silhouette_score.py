"""
silhouette_score.py — Moteur de Recherche de Pose Coarse-to-Fine & Score de Silhouette Chamfer (CS)
Pipeline : boutique-mode / Master Prompt V2.2
Auteur : Architecte Principal Vision 3D & DT E-Commerce Luxe

Fonctionnement :
1. Extraction robuste de la silhouette 2D de référence (alpha natif ou fond studio CIE L*a*b* + fermeture morphologique).
2. Calcul de la carte de distance euclidienne (Distance Transform) des contours de référence.
3. Recherche grossière (Coarse Search) sur grille SO(3) : azimut 15°, élévation 15°, roulis 10° maximisant l'IoU 2D.
4. Raffinement continu 6-DoF (Fine Optimization via Powell/Nelder-Mead) maximisant IoU 2D + proximité Chamfer.
5. Gel de pose et calcul du Score de Silhouette Chamfer (CS normalisé).
6. Balayage orbital 12 angles (30°) pour consigner la stabilité globale de la silhouette.
7. Génération de la planche visuelle de contrôle (Photo source | Masque | Reprojection 3D | Overlay contours).
"""

import sys
import os
import json
import math
import argparse
import numpy as np
import cv2
from scipy.optimize import minimize

try:
    import bpy
    import bmesh
    import mathutils
except ImportError:
    pass


def extract_reference_mask(image_path, target_size=512):
    """
    Extrait un masque binaire net (0 ou 255) du produit depuis l'image source.
    Gère les PNG avec canal alpha ou les fonds clairs de studio avec estimation automatique.
    """
    img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise FileNotFoundError(f"Impossible de lire l'image : {image_path}")

    # Cas 1 : Canal Alpha présent
    if img.ndim == 3 and img.shape[2] == 4:
        alpha = img[:, :, 3]
        _, mask = cv2.threshold(alpha, 15, 255, cv2.THRESH_BINARY)
    else:
        # Cas 2 : Image RGB avec fond studio uniforme
        if img.ndim == 3:
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
        else:
            rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
            lab = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

        h, w = img.shape[:2]
        # Échantillonnage des 4 coins pour estimer la couleur moyenne du fond studio
        corner_pixels = np.concatenate([
            lab[0:15, 0:15].reshape(-1, 3),
            lab[0:15, w-15:w].reshape(-1, 3),
            lab[h-15:h, 0:15].reshape(-1, 3),
            lab[h-15:h, w-15:w].reshape(-1, 3)
        ], axis=0)
        bg_mean = np.mean(corner_pixels, axis=0)

        # Calcul du Delta E approximatif dans l'espace Lab
        diff = np.linalg.norm(lab.astype(np.float32) - bg_mean, axis=2)
        # Seuil adaptatif : tout pixel avec Delta E > 14 est considéré comme produit
        mask = (diff > 14.0).astype(np.uint8) * 255

        # Nettoyage morphologique des micro-trous et poussières
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    # Cadrage centré sur le produit
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return np.zeros((target_size, target_size), dtype=np.uint8), img

    # Trouver la plus grande composante
    main_contour = max(contours, key=cv2.contourArea)
    x, y, bw, bh = cv2.boundingRect(main_contour)
    cropped_mask = mask[y:y+bh, x:x+bw]

    # Redimensionnement proportionnel vers target_size avec marge de 10%
    pad_canvas = np.zeros((target_size, target_size), dtype=np.uint8)
    inner_dim = int(target_size * 0.82)
    scale = inner_dim / max(bw, bh)
    new_w = max(1, int(bw * scale))
    new_h = max(1, int(bh * scale))

    resized_mask = cv2.resize(cropped_mask, (new_w, new_h), interpolation=cv2.INTER_NEAREST)
    off_x = (target_size - new_w) // 2
    off_y = (target_size - new_h) // 2
    pad_canvas[off_y:off_y+new_h, off_x:off_x+new_w] = resized_mask

    return pad_canvas, img


def load_glb_mesh_data(glb_path):
    """
    Importe le GLB dans Blender et extrait les coordonnées 3D de tous les sommets et faces.
    """
    for obj in list(bpy.context.scene.objects):
        bpy.data.objects.remove(obj, do_unlink=True)

    if not hasattr(bpy.ops.import_scene, "gltf"):
        bpy.ops.preferences.addon_enable(module="io_scene_gltf2")

    bpy.ops.import_scene.gltf(filepath=os.path.abspath(glb_path))
    mesh_objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    if not mesh_objects:
        raise ValueError("Aucun maillage trouvé dans le GLB.")

    all_verts = []
    all_faces = []
    vert_offset = 0

    depsgraph = bpy.context.evaluated_depsgraph_get()

    for obj in mesh_objects:
        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh()
        
        # Coordonnées monde
        mat = obj.matrix_world
        for v in eval_mesh.vertices:
            wco = mat @ v.co
            all_verts.append([wco.x, wco.y, wco.z])

        for poly in eval_mesh.polygons:
            if len(poly.vertices) == 3:
                all_faces.append([poly.vertices[0] + vert_offset,
                                  poly.vertices[1] + vert_offset,
                                  poly.vertices[2] + vert_offset])
            elif len(poly.vertices) == 4:
                # Triangulation de base
                v0, v1, v2, v3 = poly.vertices
                all_faces.append([v0 + vert_offset, v1 + vert_offset, v2 + vert_offset])
                all_faces.append([v0 + vert_offset, v2 + vert_offset, v3 + vert_offset])
            else:
                # Ngon fan
                for i in range(1, len(poly.vertices) - 1):
                    all_faces.append([poly.vertices[0] + vert_offset,
                                      poly.vertices[i] + vert_offset,
                                      poly.vertices[i + 1] + vert_offset])

        vert_offset += len(eval_mesh.vertices)
        eval_obj.to_mesh_clear()

    verts_arr = np.array(all_verts, dtype=np.float32)
    faces_arr = np.array(all_faces, dtype=np.int32)

    # Centrage du modèle à l'origine (0, 0, 0) et normalisation d'échelle
    center = (verts_arr.min(axis=0) + verts_arr.max(axis=0)) / 2.0
    verts_arr -= center
    max_span = np.linalg.norm(verts_arr, axis=1).max()
    if max_span > 1e-6:
        verts_arr /= max_span

    # Création d'un sous-échantillonnage de faces pour le coarse search ultra-rapide
    if len(faces_arr) > 4000:
        stride = max(1, len(faces_arr) // 2500)
        coarse_faces = faces_arr[::stride]
    else:
        coarse_faces = faces_arr

    return verts_arr, faces_arr, coarse_faces


def render_projected_silhouette(verts, faces, yaw, pitch, roll, scale, tx, ty, canvas_size=512):
    """
    Projette géométriquement les sommets 3D sous l'orientation Euler donnée et rasterise le masque 2D.
    yaw : rotation autour de l'axe vertical Z (degrés)
    pitch : inclinaison vers le haut/bas X (degrés)
    roll : roulis dans le plan caméra Y (degrés)
    """
    ry = math.radians(yaw)
    rp = math.radians(pitch)
    rr = math.radians(roll)

    # Matrice de rotation R = Rz(roll) * Rx(pitch) * Ry(yaw)
    cz, sz = math.cos(rr), math.sin(rr)
    cx, sx = math.cos(rp), math.sin(rp)
    cy, sy = math.cos(ry), math.sin(ry)

    # Rotation Z (Yaw vertical)
    Rz = np.array([
        [cy, -sy, 0],
        [sy,  cy, 0],
        [ 0,   0, 1]
    ], dtype=np.float32)

    # Rotation X (Pitch)
    Rx = np.array([
        [1,  0,   0],
        [0, cx, -sx],
        [0, sx,  cx]
    ], dtype=np.float32)

    # Rotation écran (Roll)
    R_roll = np.array([
        [cz, -sz, 0],
        [sz,  cz, 0],
        [ 0,   0, 1]
    ], dtype=np.float32)

    R = R_roll @ (Rx @ Rz)
    rotated_v = verts @ R.T

    # Projection orthogonale centrée sur le plan (X, Y) vers les coordonnées pixels
    half = canvas_size / 2.0
    u = rotated_v[:, 0] * (half * 0.85 * scale) + half + tx
    v = -rotated_v[:, 1] * (half * 0.85 * scale) + half + ty

    u = np.clip(u, 0, canvas_size - 1).astype(np.int32)
    v = np.clip(v, 0, canvas_size - 1).astype(np.int32)

    pts2d = np.stack([u, v], axis=1)
    mask = np.zeros((canvas_size, canvas_size), dtype=np.uint8)

    # Rasterisation ultra-rapide des polygones projetés
    tri_pts = pts2d[faces]
    cv2.fillPoly(mask, tri_pts, 255)
    return mask


def compute_mask_iou(mask_a, mask_b):
    """Calcule l'Intersection-over-Union (IoU) entre deux masques binaires 2D."""
    intersection = np.logical_and(mask_a > 0, mask_b > 0)
    union = np.logical_or(mask_a > 0, mask_b > 0)
    union_sum = np.sum(union)
    if union_sum == 0:
        return 0.0
    return float(np.sum(intersection) / union_sum)


def compute_chamfer_distance(mask_a, mask_b, dist_map_b=None):
    """
    Calcule la distance de Chamfer symétrique entre les contours de deux masques binaires.
    """
    canny_a = cv2.Canny(mask_a, 50, 150)
    canny_b = cv2.Canny(mask_b, 50, 150)

    pts_a = np.argwhere(canny_a > 0)
    pts_b = np.argwhere(canny_b > 0)

    if len(pts_a) == 0 or len(pts_b) == 0:
        return 999.0

    if dist_map_b is None:
        dist_map_b = cv2.distanceTransform(255 - canny_b, cv2.DIST_L2, 5)

    dist_map_a = cv2.distanceTransform(255 - canny_a, cv2.DIST_L2, 5)

    d_a_to_b = np.mean(dist_map_b[pts_a[:, 0], pts_a[:, 1]])
    d_b_to_a = np.mean(dist_map_a[pts_b[:, 0], pts_b[:, 1]])

    return float((d_a_to_b + d_b_to_a) / 2.0)


def coarse_to_fine_pose_search(verts, faces, coarse_faces, ref_mask, canvas_size=512):
    """
    Recherche grossière puis continue de la meilleure pose caméra (6-DoF)
    faisant correspondre la projection 3D au masque source 2D.
    """
    print("[Pose Search] Étape 1/2 : Balayage SO(3) grossier (Coarse Search)...")
    best_iou = -1.0
    best_pose = (0.0, 0.0, 0.0, 1.0, 0.0, 0.0)

    # Grille de recherche SO(3)
    yaw_angles = range(0, 360, 15)
    pitch_angles = range(-15, 60, 15)
    roll_angles = [-10, 0, 10]

    for y in yaw_angles:
        for p in pitch_angles:
            for r in roll_angles:
                m = render_projected_silhouette(verts, coarse_faces, y, p, r, 1.0, 0.0, 0.0, canvas_size)
                iou = compute_mask_iou(m, ref_mask)
                if iou > best_iou:
                    best_iou = iou
                    best_pose = (float(y), float(p), float(r), 1.0, 0.0, 0.0)

    print(f"[Pose Search] Meilleur candidat coarse : yaw={best_pose[0]}°, pitch={best_pose[1]}°, roll={best_pose[2]}° (IoU: {best_iou:.3f})")

    # Étape 2 : Optimisation continue 6-DoF
    print("[Pose Search] Étape 2/2 : Raffinement continu 6-DoF (Fine Optimization)...")

    # Distance map du contour de référence
    ref_canny = cv2.Canny(ref_mask, 50, 150)
    ref_dist_map = cv2.distanceTransform(255 - ref_canny, cv2.DIST_L2, 5)

    def objective_fn(params):
        y, p, r, s, tx, ty = params
        m = render_projected_silhouette(verts, coarse_faces, y, p, r, s, tx, ty, canvas_size)
        iou = compute_mask_iou(m, ref_mask)
        if iou < 0.1:
            return 2.0 - iou
        cd = compute_chamfer_distance(m, ref_mask, ref_dist_map)
        # Score combiné : minimiser (1 - IoU) + perte de chamfer normalisée
        norm_cd = cd / canvas_size
        return (1.0 - iou) + 0.5 * norm_cd

    init_params = np.array([best_pose[0], best_pose[1], best_pose[2], 1.0, 0.0, 0.0], dtype=np.float32)
    bounds = [
        (best_pose[0] - 25, best_pose[0] + 25),
        (best_pose[1] - 20, best_pose[1] + 20),
        (best_pose[2] - 15, best_pose[2] + 15),
        (0.65, 1.35),
        (-40.0, 40.0),
        (-40.0, 40.0)
    ]

    res = minimize(objective_fn, init_params, method='Powell', bounds=bounds,
                   options={'maxiter': 40, 'ftol': 1e-3})

    opt_y, opt_p, opt_r, opt_s, opt_tx, opt_ty = res.x
    refined_pose = {
        "yaw": round(float(opt_y), 2),
        "pitch": round(float(opt_p), 2),
        "roll": round(float(opt_r), 2),
        "scale": round(float(opt_s), 4),
        "tx": round(float(opt_tx), 2),
        "ty": round(float(opt_ty), 2)
    }

    # Rendu final sous la pose gelée
    final_render_mask = render_projected_silhouette(verts, faces, opt_y, opt_p, opt_r, opt_s, opt_tx, opt_ty, canvas_size)
    final_iou = compute_mask_iou(final_render_mask, ref_mask)
    final_cd = compute_chamfer_distance(final_render_mask, ref_mask, ref_dist_map)

    # Calcul du CS normalisé selon Master Prompt V2.2
    # Périmètre/diagonale de référence
    pts_ref = np.argwhere(ref_mask > 0)
    if len(pts_ref) > 0:
        min_y, min_x = pts_ref.min(axis=0)
        max_y, max_x = pts_ref.max(axis=0)
        diag = math.sqrt((max_x - min_x)**2 + (max_y - min_y)**2)
    else:
        diag = float(canvas_size)

    norm_cd = final_cd / max(1.0, diag)
    # Score exponentiel calibré (1.0 = parfait, >= 0.85 = acceptable luxe)
    cs_score = round(float(np.exp(-12.0 * norm_cd)), 4)
    cs_linear = round(float(max(0.0, 1.0 - (norm_cd / 0.08))), 4)

    print(f"[Pose Search] Optimisation terminée : IoU={final_iou:.3f}, CD={final_cd:.2f}px, CS={cs_score:.3f}")

    return {
        "optimal_pose": refined_pose,
        "mask_iou": round(final_iou, 4),
        "chamfer_distance_px": round(final_cd, 2),
        "chamfer_normalized": round(norm_cd, 4),
        "cs_score": cs_score,
        "cs_linear": cs_linear,
        "final_mask": final_render_mask
    }


def compute_orbital_stability(verts, faces, opt_pose, canvas_size=512):
    """
    Effectue un balayage orbital de 12 angles (par pas de 30°)
    pour évaluer la régularité du périmètre et de la surface de silhouette.
    """
    areas = []
    perimeters = []
    base_pitch = opt_pose["pitch"]
    base_scale = opt_pose["scale"]

    for step in range(12):
        angle = step * 30.0
        m = render_projected_silhouette(verts, faces, angle, base_pitch, 0.0, base_scale, 0.0, 0.0, canvas_size)
        area = int(np.count_nonzero(m > 0))
        canny = cv2.Canny(m, 50, 150)
        perim = int(np.count_nonzero(canny > 0))
        areas.append(area)
        perimeters.append(perim)

    area_cv = float(np.std(areas) / np.mean(areas)) if np.mean(areas) > 0 else 0.0
    return {
        "angles_count": 12,
        "areas_per_angle": areas,
        "perimeters_per_angle": perimeters,
        "silhouette_area_variation_cv": round(area_cv, 4)
    }


def create_verification_board(source_img, ref_mask, rendered_mask, output_path):
    """
    Assemble la planche visuelle comparative 4 quadrants :
    [ Photo Source | Masque Détourage | Reprojection 3D | Overlay Diff / Contours ]
    """
    h_target = 512
    w_target = 512

    # 1. Image source redimensionnée
    src_h, src_w = source_img.shape[:2]
    scale_src = h_target / max(src_h, src_w)
    src_resized = cv2.resize(source_img[:, :, :3], (int(src_w * scale_src), int(src_h * scale_src)))
    panel_src = np.full((h_target, w_target, 3), 245, dtype=np.uint8)
    sy_off = (h_target - src_resized.shape[0]) // 2
    sx_off = (w_target - src_resized.shape[1]) // 2
    panel_src[sy_off:sy_off+src_resized.shape[0], sx_off:sx_off+src_resized.shape[1]] = src_resized

    # 2. Masque source
    panel_mask = cv2.cvtColor(ref_mask, cv2.COLOR_GRAY2BGR)

    # 3. Rendu 3D projeté
    panel_render = cv2.cvtColor(rendered_mask, cv2.COLOR_GRAY2BGR)

    # 4. Overlay de comparaison (Vert = intersection, Rouge = référence manquée, Bleu = excès 3D)
    overlay = np.zeros((h_target, w_target, 3), dtype=np.uint8)
    inter = np.logical_and(ref_mask > 0, rendered_mask > 0)
    ref_only = np.logical_and(ref_mask > 0, rendered_mask == 0)
    render_only = np.logical_and(ref_mask == 0, rendered_mask > 0)

    overlay[inter] = [80, 200, 80]     # Vert doux (accord parfait)
    overlay[ref_only] = [50, 50, 220]   # Rouge (manque 3D)
    overlay[render_only] = [220, 120, 50] # Bleu/cyan (excès 3D)

    # Contours nets
    canny_ref = cv2.Canny(ref_mask, 50, 150)
    canny_rend = cv2.Canny(rendered_mask, 50, 150)
    overlay[canny_ref > 0] = [255, 255, 255]
    overlay[canny_rend > 0] = [0, 255, 255]

    # Titres sur les panneaux
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(panel_src, "Photo Source", (15, 30), font, 0.7, (20, 20, 20), 2)
    cv2.putText(panel_mask, "Silhouette Reference (2D)", (15, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(panel_render, "Reprojection GLB (3D)", (15, 30), font, 0.7, (255, 255, 255), 2)
    cv2.putText(overlay, "Overlay Comparatif (Vert=Accord)", (15, 30), font, 0.6, (255, 255, 255), 2)

    top_row = np.hstack([panel_src, panel_mask])
    bot_row = np.hstack([panel_render, overlay])
    board = np.vstack([top_row, bot_row])

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    cv2.imwrite(output_path, board)
    print(f"[Planche] Visualisation enregistrée : {output_path}")


def evaluate_chamfer_silhouette(glb_path, image_path, output_json=None, output_img=None, threshold=0.85):
    """
    Point d'entrée complet d'évaluation de fidélité par Score de Silhouette (CS).
    """
    ref_mask, source_img = extract_reference_mask(image_path, target_size=512)
    verts, faces, coarse_faces = load_glb_mesh_data(glb_path)

    res = coarse_to_fine_pose_search(verts, faces, coarse_faces, ref_mask, canvas_size=512)
    orbital = compute_orbital_stability(verts, coarse_faces, res["optimal_pose"], canvas_size=512)

    cs_val = res["cs_score"]
    passed = (cs_val >= threshold)

    report = {
        "metric": "Chamfer Silhouette Score (CS)",
        "pipeline_version": "Master Prompt V2.2",
        "verdict": "PASS" if passed else "FAIL",
        "threshold_required": threshold,
        "cs_score": cs_val,
        "cs_linear": res["cs_linear"],
        "mask_iou_2d": res["mask_iou"],
        "chamfer_distance_px": res["chamfer_distance_px"],
        "chamfer_normalized": res["chamfer_normalized"],
        "optimal_pose_6dof": res["optimal_pose"],
        "orbital_stability": orbital,
        "source_image": os.path.abspath(image_path),
        "glb_model": os.path.abspath(glb_path)
    }

    if output_img:
        create_verification_board(source_img, ref_mask, res["final_mask"], output_img)
        report["verification_board_path"] = os.path.abspath(output_img)

    if output_json:
        os.makedirs(os.path.dirname(os.path.abspath(output_json)), exist_ok=True)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"[Rapport] Métriques CS sauvegardées : {output_json}")

    return report


def main(argv=None):
    if argv is None:
        raw = sys.argv
        argv = raw[raw.index("--") + 1:] if "--" in raw else raw[1:]

    parser = argparse.ArgumentParser(description="Évaluateur de Silhouette Chamfer (CS) Coarse-to-Fine")
    parser.add_argument("--glb", required=True, help="Chemin du GLB à évaluer")
    parser.add_argument("--image", required=True, help="Chemin de l'image photo source de référence")
    parser.add_argument("--output-json", default=None, help="Chemin du rapport JSON")
    parser.add_argument("--output-img", default=None, help="Chemin de la planche comparative")
    parser.add_argument("--threshold", type=float, default=0.85, help="Seuil d'acceptation commerciale CS (défaut 0.85)")
    args = parser.parse_args(argv)

    report = evaluate_chamfer_silhouette(args.glb, args.image, args.output_json, args.output_img, args.threshold)
    print("CS_EVALUATION_REPORT:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
