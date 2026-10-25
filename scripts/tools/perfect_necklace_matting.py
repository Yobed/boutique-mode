import os
import cv2
import numpy as np
from PIL import Image

ref_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
out_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
os.makedirs(out_dir, exist_ok=True)

im = Image.open(ref_p).convert("RGB")
img_np = np.array(im)
h, w, _ = img_np.shape

# 1. Analyse précise du fond par échantillonnage des 4 bords
border_mask = np.zeros((h, w), dtype=bool)
border_mask[:40, :] = True
border_mask[-40:, :] = True
border_mask[:, :40] = True
border_mask[:, -40:] = True

bg_samples = img_np[border_mask]
bg_median = np.median(bg_samples, axis=0)
print(f"Fond médian RGB: {bg_median}")

# Conversion en espace Lab pour une distance perceptuelle réelle Delta E
img_lab = cv2.cvtColor(img_np, cv2.COLOR_RGB2LAB).astype(np.float32)
bg_lab = cv2.cvtColor(np.uint8([[bg_median]]), cv2.COLOR_RGB2LAB)[0, 0].astype(np.float32)

delta_e = np.sqrt(np.sum((img_lab - bg_lab) ** 2, axis=-1))

# Seuil perceptuel
raw_mask = (delta_e > 12.0).astype(np.uint8) * 255

# 2. Traitement morphologique pour éliminer les 'trous' dans les perles
# Les perles blanches ont un faible delta E mais font partie de la texture du collier
kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
closed_mask = cv2.morphologyEx(raw_mask, cv2.MORPH_CLOSE, kernel_close)

# 3. Séparation entre le 'grand trou central' (ouverture du cou légitime) et les 'micro-trous' parasites
# Trouver les contours du fond (inversion du masque)
inv_mask = cv2.bitwise_not(closed_mask)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(inv_mask)

# Le fond extérieur est la composante qui touche les bords de l'image
clean_mask = np.zeros((h, w), dtype=np.uint8)
exterior_label = labels[10, 10]

# Identifier le grand trou central (la plus grande composante intérieure)
interior_components = []
for lbl_idx in range(1, num_labels):
    if lbl_idx == exterior_label:
        continue
    area = stats[lbl_idx, cv2.CC_STAT_AREA]
    interior_components.append((area, lbl_idx))

interior_components.sort(reverse=True)

# La plus grande composante intérieure est le trou du cou légitime
neck_hole_label = interior_components[0][1] if interior_components else None
neck_hole_area = interior_components[0][0] if interior_components else 0

print(f"Composantes intérieures détectées: {len(interior_components)}")
print(f"Trou du cou principal (légitime): surface={neck_hole_area} pixels")

# Reconstruire le masque parfait :
# Tout ce qui n'est PAS le fond extérieur et PAS le trou central légitime est l'objet (y compris les perles blanches !)
clean_fg = np.ones((h, w), dtype=bool)
clean_fg[labels == exterior_label] = False
if neck_hole_label is not None and neck_hole_area > 50000:
    clean_fg[labels == neck_hole_label] = False

clean_mask = (clean_fg.astype(np.uint8)) * 255

# Lissage des bords par filtre bilatéral / anti-aliasing
clean_mask_smooth = cv2.GaussianBlur(clean_mask, (5, 5), 0)

# Sauvegarde des comparaisons
Image.fromarray(raw_mask).save(os.path.join(out_dir, "01_raw_delta_e_mask.png"))
Image.fromarray(closed_mask).save(os.path.join(out_dir, "02_morph_closed_mask.png"))
Image.fromarray(clean_mask).save(os.path.join(out_dir, "03_perfect_necklace_mask.png"))

# Découpage final avec transparence
rgba_clean = np.dstack([img_np, clean_mask_smooth])
Image.fromarray(rgba_clean, "RGBA").save(os.path.join(out_dir, "04_collier_detoure_propre.png"))

# Superposition sur fond sombre pour valider
dark_bg = np.full((h, w, 3), 20, dtype=np.uint8)
alpha_factor = clean_mask_smooth[:, :, None] / 255.0
composite = (img_np * alpha_factor + dark_bg * (1 - alpha_factor)).astype(np.uint8)
Image.fromarray(composite).save(os.path.join(out_dir, "05_collier_sur_fond_sombre.png"))

print("Planche comparative de détourage générée avec succès dans:", out_dir)
