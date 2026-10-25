import os
from PIL import Image, ImageDraw, ImageFont

diag_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
ref_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
issue_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_viewer_issue.png"
mask_p = os.path.join(diag_dir, "03_perfect_necklace_mask.png")
hero_p = os.path.join(diag_dir, "previews", "solid_hero.png")
side_p = os.path.join(diag_dir, "previews", "solid_side.png")

out_board = os.path.join(diag_dir, "comparatif_avant_apres_collier.png")

W, H = 2000, 750
board = Image.new("RGB", (W, H), (18, 22, 28))
draw = ImageDraw.Draw(board)

try:
    font_title = ImageFont.truetype("arialbd.ttf", 28)
    font_sub = ImageFont.truetype("arial.ttf", 16)
    font_col = ImageFont.truetype("arialbd.ttf", 18)
    font_body = ImageFont.truetype("arial.ttf", 14)
except:
    font_title = font_sub = font_col = font_body = ImageFont.load_default()

# Header
draw.rectangle([(0, 0), (W, 110)], fill=(28, 34, 44))
draw.text((40, 20), "RÉSOLUTION DU PROBLÈME DE DÉTOURAGE ET DE MAILLAGE TROUÉ (COLLIER MULTIRANGS)", fill=(255, 255, 255), font=font_title)
draw.text((40, 62), "Comparatif Avant/Après : Diagnostic des trous parasites vs Reconstruction volumique étanche sans double-coque", fill=(160, 180, 205), font=font_sub)

panels = [
    (ref_p, "1. Photo d'origine", "Collier continu avec trou du cou central.", 40),
    (issue_p, "2. Anomalie constatée (Avant)", "Détourage U2Net bruité -> Trous & double paroi creuse.", 520),
    (mask_p, "3. Masque réparé", "Trou central préservé, 32 micro-trous perles rebouchés.", 1000),
    (hero_p, "4. Nouveau modèle 3D (Après)", "Volume plein, étanche, zéro trou parasite, relief réel.", 1480)
]

pw, ph = 460, 580

for p_path, title, desc, x in panels:
    y = 130
    draw.rectangle([(x, y), (x + pw, y + ph)], fill=(24, 30, 38), outline=(50, 65, 85), width=2)
    draw.text((x + 15, y + 15), title, fill=(255, 215, 0), font=font_col)
    
    if os.path.exists(p_path):
        im = Image.open(p_path).convert("RGBA")
        im.thumbnail((pw - 30, ph - 90), Image.Resampling.LANCZOS)
        ox = x + (pw - im.size[0]) // 2
        oy = y + 50 + (ph - 90 - im.size[1]) // 2
        tile = Image.new("RGB", im.size, (12, 15, 20))
        tile.paste(im, (0, 0), im.split()[3] if im.mode == "RGBA" else None)
        board.paste(tile, (ox, oy))
    
    draw.text((x + 15, y + ph - 30), desc, fill=(180, 195, 215), font=font_body)

board.save(out_board, "PNG", optimize=True)
print("Saved comparative board to:", out_board)

# Copy to brain artifact directory
artifact_p = r"C:\Users\WILFRIED\.gemini\antigravity\brain\a6afba35-f0a6-4827-a7a0-51c2e154eb99\comparatif_avant_apres_collier.png"
board.save(artifact_p, "PNG", optimize=True)
print("Mirrored to artifacts:", artifact_p)
