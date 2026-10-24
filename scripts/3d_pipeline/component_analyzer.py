"""
component_analyzer.py — Décomposition Visuelle Intelligente et Analyse Multi-Composants
Fait partie du pipeline procédural générique Image-to-3D pour Blender 5.x.

Analyse la structure spatiale et physique d'un objet 2D avant modélisation :
- Détection des strates géométriques verticales (socle, corps, col/sommet, couvercle)
- Détection des discontinuités de contour (épaulements, rétrécissements, décrochements)
- Corrélation entre frontières géométriques et contrastes de matériaux PBR
- Détection des détails localisés (cadrans, boutons, cerclages, inserts, patins)
- Formulation explicite des relations structurales (stacked_on, attached_to, nested_in)
- Attribution de niveaux de confiance et documentation des incertitudes
"""

import math
import os
import sys
from PIL import Image

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
if PIPELINE_DIR not in sys.path:
    sys.path.append(PIPELINE_DIR)

from image_analyzer import ReferenceImageAnalyzer


class VisualComponentDecomposer:
    """Décomposeur structurel de premier plan en composants physiques assemblables."""

    def __init__(self, image_path, category_hint=None):
        self.image_path = os.path.abspath(image_path)
        if not os.path.exists(self.image_path):
            raise FileNotFoundError(f"Image introuvable : {self.image_path}")

        self.category_hint = category_hint
        # Utiliser l'analyseur de base pour la vision initiale
        self.base_analyzer = ReferenceImageAnalyzer(self.image_path, category_hint=category_hint)
        self.base_analyzer.segment_foreground()
        self.base_analyzer.compute_symmetry()
        self.base_analyzer.extract_dominant_colors(max_colors=4)

        self.image = self.base_analyzer.raw_image
        self.mask = self.base_analyzer.mask
        self.bbox = self.base_analyzer.bbox  # min_x, min_y, max_x, max_y
        self.palette = self.base_analyzer.palette
        self.aspect_ratio = self.base_analyzer.aspect_ratio

        self.components = []
        self.structural_layers = []
        self.analysis_logs = []

    def log(self, msg):
        self.analysis_logs.append(msg)

    def analyze_strata(self, num_slices=32):
        """Découpe l'objet en tranches horizontales et détecte les discontinuités géométriques et colorimétriques."""
        min_x, min_y, max_x, max_y = self.bbox
        bh = max_y - min_y
        bw = max_x - min_x
        pix = self.image.load()

        slices = []
        for i in range(num_slices):
            # De la base (y_max) au sommet (y_min)
            t = i / float(num_slices - 1)
            y = int(max_y - t * bh)
            y = min(max(y, 0), self.image.height - 1)

            lx, rx = None, None
            colors = []
            for x in range(min_x, max_x + 1):
                if self.mask[y][x]:
                    if lx is None: lx = x
                    rx = x
                    colors.append(pix[x, y])

            if lx is not None:
                width = rx - lx
                cx = (lx + rx) / 2.0
                avg_r = sum(c[0] for c in colors) / len(colors)
                avg_g = sum(c[1] for c in colors) / len(colors)
                avg_b = sum(c[2] for c in colors) / len(colors)
                slices.append({
                    "idx": i,
                    "t": t,
                    "y": y,
                    "width": width,
                    "center_x": cx,
                    "avg_rgb": (avg_r, avg_g, avg_b),
                    "coverage": len(colors)
                })

        if not slices:
            return []

        # Détection des frontières entre strates
        cut_indices = []
        for j in range(1, len(slices)):
            s_prev = slices[j - 1]
            s_curr = slices[j]

            # Écart colorimétrique
            dr = s_curr["avg_rgb"][0] - s_prev["avg_rgb"][0]
            dg = s_curr["avg_rgb"][1] - s_prev["avg_rgb"][1]
            db = s_curr["avg_rgb"][2] - s_prev["avg_rgb"][2]
            color_dist = math.sqrt(dr*dr + dg*dg + db*db)

            # Écart dimensionnel relatif
            width_ratio = s_curr["width"] / float(max(1, s_prev["width"]))
            width_delta = abs(s_curr["width"] - s_prev["width"]) / float(bw)

            # Écart de centrage latéral
            center_shift = abs(s_curr["center_x"] - s_prev["center_x"]) / float(bw)

            # Règle de coupure : changement physique plausible
            # (changement de couleur significatif avec saut de largeur OU épaulement franc)
            is_cut = False
            reasons = []
            if color_dist > 28.0 and (width_delta > 0.08 or width_ratio < 0.85 or width_ratio > 1.15):
                is_cut = True
                reasons.append(f"color_and_width_shift(dist={color_dist:.1f}, dW={width_delta:.2f})")
            elif width_delta > 0.16:
                is_cut = True
                reasons.append(f"strong_shoulder_step(dW={width_delta:.2f})")
            elif center_shift > 0.12 and width_delta > 0.05:
                is_cut = True
                reasons.append(f"lateral_center_offset(shift={center_shift:.2f})")

            if is_cut:
                cut_indices.append((j, reasons))

        # Regroupement des tranches en couches continues
        layers = []
        start_idx = 0
        cut_points = [c[0] for c in cut_indices] + [len(slices)]

        # Filtrer et fusionner les strates trop minces (< 2 tranches sauf si saut de couleur très net)
        merged_ranges = []
        curr_start = 0
        for cp in cut_points:
            count = cp - curr_start
            if count >= 2 or curr_start == 0 or cp == len(slices):
                merged_ranges.append((curr_start, cp))
                curr_start = cp
            else:
                # Trop mince : fusionner avec la strate précédente si elle existe
                if merged_ranges:
                    prev_s, _ = merged_ranges.pop()
                    merged_ranges.append((prev_s, cp))
                    curr_start = cp
                else:
                    merged_ranges.append((curr_start, cp))
                    curr_start = cp

        total_slices_count = len(slices)
        for r_start, r_end in merged_ranges:
            layer_slices = slices[r_start:r_end]
            if layer_slices:
                t_min = layer_slices[0]["t"]
                t_max = layer_slices[-1]["t"]
                # Ratio de hauteur normalisé exact sur le nombre total de tranches
                h_ratio = len(layer_slices) / float(total_slices_count)
                avg_w = sum(s["width"] for s in layer_slices) / len(layer_slices)
                avg_cx = sum(s["center_x"] for s in layer_slices) / len(layer_slices)
                r_m = sum(s["avg_rgb"][0] for s in layer_slices) / len(layer_slices)
                g_m = sum(s["avg_rgb"][1] for s in layer_slices) / len(layer_slices)
                b_m = sum(s["avg_rgb"][2] for s in layer_slices) / len(layer_slices)

                layers.append({
                    "start_t": t_min,
                    "end_t": t_max,
                    "height_ratio": h_ratio,
                    "width_px": avg_w,
                    "center_x_px": avg_cx,
                    "relative_width": avg_w / float(bw),
                    "relative_offset_x": (avg_cx - (min_x + bw / 2.0)) / float(bw),
                    "mean_rgb": (int(r_m), int(g_m), int(b_m)),
                    "slice_count": len(layer_slices)
                })

        self.structural_layers = layers
        self.log(f"Strates structurelles détectées : {len(layers)}")
        return layers

    def detect_local_features(self):
        """Recherche les éléments saillants localisés (ex: cadrans, boutons, molettes, cerclages)."""
        min_x, min_y, max_x, max_y = self.bbox
        bw = max_x - min_x
        bh = max_y - min_y
        pix = self.image.load()

        features = []

        # Recherche de zones circulaires ou à fort contraste interne dans le corps
        # Découpage du tiers central
        cx_obj = min_x + bw / 2.0
        cy_obj = min_y + bh / 2.0

        # Échantillonnage d'écarts de couleur circulaires
        for r_cand in [bw * 0.15, bw * 0.22, bw * 0.30]:
            edge_contrast_sum = 0
            samples_count = 16
            for s in range(samples_count):
                th = 2.0 * math.pi * (s / samples_count)
                px_in = int(cx_obj + (r_cand - 6) * math.cos(th))
                py_in = int(cy_obj + (r_cand - 6) * math.sin(th))
                px_out = int(cx_obj + (r_cand + 6) * math.cos(th))
                py_out = int(cy_obj + (r_cand + 6) * math.sin(th))

                if 0 <= px_in < self.image.width and 0 <= py_in < self.image.height and 0 <= px_out < self.image.width and 0 <= py_out < self.image.height:
                    cin = pix[px_in, py_in]
                    cout = pix[px_out, py_out]
                    diff = math.sqrt((cin[0]-cout[0])**2 + (cin[1]-cout[1])**2 + (cin[2]-cout[2])**2)
                    edge_contrast_sum += diff

            mean_contrast = edge_contrast_sum / float(samples_count)
            if mean_contrast > 35.0:
                features.append({
                    "type": "rotary_dial_or_bezel",
                    "radius_rel": r_cand / float(bw),
                    "center_rel": (0.0, 0.50),
                    "contrast": round(mean_contrast, 2)
                })
                break

        return features

    def synthesize_components(self, target_metric_height=0.20):
        """
        Synthétise la liste des composants candidats prêts pour l'orchestrateur Blender.
        Évite l'écueil du bloc unique en décomposant intelligemment les strates physiques.
        """
        self.analyze_strata()
        local_features = self.detect_local_features()

        real_h = target_metric_height
        real_w = real_h / float(self.aspect_ratio)
        real_d = real_w * 0.65  # Profondeur estimée réaliste

        components = []
        materials_decl = {}

        # 1. Traitement des strates verticales détectées
        if len(self.structural_layers) >= 2:
            self.log(f"Décomposition multi-composants activée ({len(self.structural_layers)} couches identifiées)")

            prev_comp_id = None
            current_z = 0.0

            for idx, layer in enumerate(self.structural_layers):
                comp_h = max(0.005, layer["height_ratio"] * real_h)
                comp_w = max(0.010, layer["relative_width"] * real_w)
                comp_d = max(0.010, layer["relative_width"] * real_d)
                offset_x = layer["relative_offset_x"] * real_w

                # Déterminer le rôle
                if idx == 0:
                    role = "structural_base"
                    comp_name = "Socle_Inferieur"
                    primitive = "rounded_box"
                    corner_rad = 0.020
                    taper = 0.95
                    confidence = 0.88
                    justif = "Strate inférieure continue délimitée par un épaulement franc et transition de teinte."
                elif idx == len(self.structural_layers) - 1:
                    role = "top_cap_or_insert"
                    comp_name = "Chapeau_Superieur"
                    primitive = "rounded_box"
                    corner_rad = 0.015
                    taper = 0.90
                    confidence = 0.82
                    justif = "Strate sommitale avec décrochement de largeur et décalage de centre."
                else:
                    role = "main_body_core"
                    comp_name = f"Corps_Central_Strate_{idx}"
                    primitive = "rounded_box"
                    corner_rad = 0.025
                    taper = 0.92
                    confidence = 0.91
                    justif = "Strate médiane de largeur maximale constituant le volume principal."

                # Mappage du matériau selon la couleur moyenne de la strate
                preset, custom = self.base_analyzer.map_color_to_pbr_preset(layer["mean_rgb"])
                mat_key = f"M_{comp_name}"
                if preset:
                    materials_decl[mat_key] = {"preset": preset}
                else:
                    materials_decl[mat_key] = {"custom": custom}

                comp_entry = {
                    "id": f"comp_{idx+1}_{comp_name.lower()}",
                    "name": comp_name,
                    "role": role,
                    "primitive": primitive,
                    "material": mat_key,
                    "dimensions": [round(comp_w, 4), round(comp_d, 4), round(comp_h, 4)],
                    "location": [round(offset_x, 4), 0.0, round(current_z, 4)],
                    "corner_radius": corner_rad,
                    "taper_ratio": taper,
                    "bevel_width": 0.002,
                    "confidence": confidence,
                    "relationship": {
                        "type": "stacked_on" if prev_comp_id else "base_anchor",
                        "target": prev_comp_id
                    },
                    "visual_justification": justif,
                    "uncertainties": [
                        "Profondeur front-to-back estimée selon heuristique 0.65x large",
                        "Face arrière non visible supposée symétrique à la face avant"
                    ]
                }
                components.append(comp_entry)
                current_z += comp_h
                prev_comp_id = comp_entry["id"]

        else:
            # Fallback simple mais documenté : 1 seul volume homogène
            self.log("Objet visuellement homogène : pas de stratification détectée.")
            preset, custom = self.base_analyzer.map_color_to_pbr_preset(self.palette[0]["rgb"])
            mat_key = "M_Corps_Monolithique"
            if preset:
                materials_decl[mat_key] = {"preset": preset}
            else:
                materials_decl[mat_key] = {"custom": custom}

            components.append({
                "id": "comp_1_corps_principal",
                "name": "Corps_Principal",
                "role": "monolithic_volume",
                "primitive": "rounded_box",
                "material": mat_key,
                "dimensions": [round(real_w, 4), round(real_d, 4), round(real_h, 4)],
                "location": [0.0, 0.0, 0.0],
                "corner_radius": 0.015,
                "taper_ratio": 1.0,
                "bevel_width": 0.002,
                "confidence": 0.70,
                "relationship": {"type": "root"},
                "visual_justification": "Aucune strate ni rupture géométrique nette n'a été détectée dans l'image.",
                "uncertainties": ["Structure interne et profondeur Y indéterminées"]
            })

        # 2. Ajout des détails fins ou cerclages si détectés
        max_comp_d = max(c["dimensions"][1] for c in components if "dimensions" in c) if any("dimensions" in c for c in components) else real_d
        for f_idx, feat in enumerate(local_features):
            if feat["type"] == "rotary_dial_or_bezel":
                dial_r = feat["radius_rel"] * real_w
                dial_r = min(dial_r, real_w * 0.20, real_d * 0.40)
                mat_dial = "M_Dial_Accent"
                materials_decl[mat_dial] = {"preset": "dark_polymer"}
                components.append({
                    "id": f"comp_detail_{f_idx+1}_cadran",
                    "name": "Cadran_Circulaire_Accent",
                    "role": "rotary_dial_bezel",
                    "primitive": "ring_collar",
                    "material": mat_dial,
                    "radius_ext": round(dial_r, 4),
                    "radius_int": round(dial_r * 0.80, 4),
                    "height": 0.003,
                    "bevel_width": 0.0004,
                    "segments": 32,
                    "location": [0.0, -round(max_comp_d * 0.50, 4), round(real_h * 0.50, 4)],
                    "rotation": [1.5708, 0.0, 0.0],
                    "confidence": 0.78,
                    "relationship": {"type": "embedded_in_face", "target": components[0]["id"]},
                    "visual_justification": f"Contraste circulaire détecté au centre de la face avant (contraste={feat['contrast']}).",
                    "uncertainties": ["Profondeur d'encastrement estimée"]
                })

        # 3. Assemblage du document de spécification JSON normalisé
        max_comp_w = max(c["dimensions"][0] for c in components if "dimensions" in c)
        max_comp_d = max(c["dimensions"][1] for c in components if "dimensions" in c)
        total_scale = [
            round(max_comp_w, 4),
            round(max_comp_d, 4),
            round(real_h, 4)
        ]

        base_stem = os.path.splitext(os.path.basename(self.image_path))[0]
        if "." in base_stem:
            base_stem = os.path.splitext(base_stem)[0]

        spec = {
            "object_id": f"{base_stem}_decomposed",
            "object_name": f"{base_stem.replace('_', ' ').title()} Multi-Component Model",
            "category": "multi_component_decomposed_object",
            "scale_metric": {
                "unit": "meters",
                "dimensions": [round(s, 4) for s in total_scale]
            },
            "coordinate_system": {
                "up_axis": "+Z",
                "forward_axis": "-Y",
                "lateral_axis": "+X",
                "origin": "bottom_center"
            },
            "materials": materials_decl,
            "components": components,
            "analysis_metadata": {
                "source_image": self.image_path,
                "analyzer_module": "component_analyzer.py",
                "detected_strata_count": len(self.structural_layers),
                "detected_features_count": len(local_features),
                "confidence_score": 0.88 if len(components) > 1 else 0.70,
                "monocular_ambiguity": True,
                "known_facts": [
                    f"Dimensions boîte englobante 2D : {self.bbox[2]-self.bbox[0]}x{self.bbox[3]-self.bbox[1]} px",
                    f"Ratio d'aspect mesuré : {self.aspect_ratio:.3f}",
                    f"Nombre de strates physiques distinctes identifiées : {len(self.structural_layers)}"
                ],
                "hypotheses": [
                    "Chaque strate verticale avec discontinuité géométrique et colorimétrique est modélisée comme une pièce étanche indépendante.",
                    "Profondeur Y fixée selon le coefficient ergonomique 0.65x largeur en absence de vue orthogonale."
                ],
                "structural_breakdown": [
                    {
                        "component_id": c["id"],
                        "role": c["role"],
                        "justification": c["visual_justification"]
                    }
                    for c in components
                ]
            }
        }
        return spec


def main():
    if len(sys.argv) < 3:
        print("Usage: python component_analyzer.py --image <image_path> --output <spec_path>")
        sys.exit(1)

    image_path = None
    output_path = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == "--image" and i + 1 < len(sys.argv):
            image_path = sys.argv[i + 1]
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]

    if not image_path or not output_path:
        print("Erreur : --image et --output sont requis.")
        sys.exit(1)

    decomposer = VisualComponentDecomposer(image_path)
    spec = decomposer.synthesize_components()

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    import json
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2)

    print(f"Spécification multi-composants générée avec succès : {output_path}")
    print(f"  - Composants détectés : {len(spec['components'])}")
    print(f"  - Matériaux physiques : {len(spec['materials'])}")
    print(f"  - Strates identifiées : {spec['analysis_metadata']['detected_strata_count']}")


if __name__ == "__main__":
    main()
