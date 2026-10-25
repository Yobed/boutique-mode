import os
from PIL import Image, ImageDraw, ImageFont

diag_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
user_viewer_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_viewer_issue.png"
user_ref_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
clean_mask_p = os.path.join(diag_dir, "03_perfect_necklace_mask.png")
clean_comp_p = os.path.join(diag_dir, "05_collier_sur_fond_sombre.png")

out_board = os.path.join(diag_dir, "diagnostic_board_trous_detourage.png")

# Montage 4 panneaux :
# [1. Photo Source Référence] [2. Défaut 3D Constaté (Trous + Double-Coque)]
# [3. Masque Corrigé (Trou du cou vs 32 micro-trous bouchés)] [4. Détourage Propre Validé sur Fond Sombre]

W, H = 1800, 1000
board = Image.new("RGB", (W, H), (20, 24, 30))
draw = ImageDraw.Draw(board)

try:
    font_title = ImageFont.truetype("arialbd.ttf", 32)
    font_sub = ImageFont.truetype("arial.ttf", 18)
    font_label = ImageFont.truetype("arialbd.ttf", 20)
    font_desc = ImageFont.truetype("arial.ttf", 15)
except:
    font_title = font_sub = font_label = font_desc = ImageFont.load_default()

# Header
draw.rectangle([(0, 0), (W, 100)], fill=(30, 36, 46))
draw.text((40, 20), "DIAGNOSTIC TECHNIQUE : PROBLÈME DES TROUS & DU DÉTOURAGE (COLLIER ART-301)", fill=(255, 255, 255), font=font_title)
draw.text((40, 62), "Analyse des causes racines : Perles blanches érodées, micro-perforations du masque alpha et double-coque TripoSR", fill=(170, 190, 215), font=font_sub)

panels = [
    (user_ref_p, "1. Photo d'origine (Collier perles)", "Objet continu : perles corail, blanches & or sur fond clair.", (40, 130)),
    (user_viewer_p, "2. Anomalie constatée (Viewer 3D)", "Détourage bruité -> Maillage troué + double-coque creuse.", (480, 130)),
    (clean_mask_p, "3. Masque morphologique séparé", "Préservation du trou du cou (352k px) & fermeture des 32 micro-trous.", (920, 130)),
    (clean_comp_p, "4. Détourage continu nettoyé", "Contours nets, perles blanches restaurées, zéro trou parasite.", (1360, 130))
]

pw, ph = 400, 520

for p_path, label, desc, (x, y) in panels:
    draw.rectangle([(x, y), (x + pw, y + ph)], fill=(28, 34, 44), outline=(60, 75, 95), width=2)
    draw.text((x + 10, y + 10), label, fill=(255, 215, 0), font=font_label)
    
    # Image
    if os.path.exists(p_path):
        im = Image.open(p_path).convert("RGBA")
        im.thumbnail((pw - 20, ph - 90), Image.Resampling.LANCZOS)
        ox = x + (pw - im.size[0]) // 2
        oy = y + 45 + (ph - 90 - im.size[1]) // 2
        tile = Image.new("RGB", im.size, (15, 18, 24))
        tile.paste(im, (0, 0), im.split()[3] if im.mode == "RGBA" else None)
        board.paste(tile, (ox, oy))
    
    # Description
    draw.text((x + 10, y + ph - 35), desc, fill=(180, 195, 215), font=font_desc)

# Footer explanatory panel
draw.rectangle([(40, 680), (W - 40, H - 30)], fill=(25, 32, 42), outline=(70, 90, 120), width=1)
draw.text((60, 695), "SYNTHÈSE DES 3 CAUSES RACINES & PLAN DE RÉSORPTION :", fill=(255, 200, 80), font=font_label)

causes = [
    "1. Confusion Fond / Perles claires : Le fond ivoire (RGB 236,233,228) est trop proche des perles blanches -> U²-Net découpe l'intérieur des perles en créant des trous.",
    "2. Effondrement topologique TripoSR sur les tores : TripoSR ne sait pas refermer un anneau fin -> Il produit deux parois disjointes en 'sandwich' avec des déchirements.",
    "3. Solution technique : Remplacement par un détourage Delta-E Lab avec fermeture morphologique des 32 micro-trous + extrusion volumique pleine (Solidify étanche)."
]

for idx, c in enumerate(causes):
    draw.text((60, 735 + idx * 30), c, fill=(210, 225, 240), font=font_desc)

board.save(out_board, "PNG", optimize=True)
print("Diagnostic board saved to:", out_board)

# Mirror to brain artifacts directory
artifact_board = r"C:\Users\WILFRIED\.gemini\antigravity\brain\a6afba35-f0a6-4827-a7a0-51c2e154eb99\diagnostic_board_trous_detourage.png"
board.save(artifact_board, "PNG", optimize=True)
print("Mirrored to artifacts:", artifact_board)
