import os
from PIL import Image, ImageDraw, ImageFont

diag_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
preview_dir = os.path.join(diag_dir, "necklace_360_master")
ref_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
issue_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_viewer_issue.png"

front_p = os.path.join(preview_dir, "necklace_front.png")
hero_p = os.path.join(preview_dir, "necklace_hero_360.png")
side_p = os.path.join(preview_dir, "necklace_side.png")
back_p = os.path.join(preview_dir, "necklace_back.png")

out_board = os.path.join(diag_dir, "necklace_360_masterpiece_showcase.png")

# Board dimensions: 5 columns
# [Photo Référence] [Vue Frontale 0°] [Vue Hero 360° (35°)] [Vue Profil 90°] [Vue Arrière 180° (Fermoir)]
W, H = 2400, 780
board = Image.new("RGB", (W, H), (14, 18, 24))
draw = ImageDraw.Draw(board)

try:
    font_title = ImageFont.truetype("arialbd.ttf", 30)
    font_sub = ImageFont.truetype("arial.ttf", 16)
    font_col = ImageFont.truetype("arialbd.ttf", 18)
    font_body = ImageFont.truetype("arial.ttf", 14)
except:
    font_title = font_sub = font_col = font_body = ImageFont.load_default()

# Header
draw.rectangle([(0, 0), (W, 110)], fill=(22, 28, 38))
draw.text((40, 20), "MODÈLE 3D HAUTE-FIDÉLITÉ POUR LA VUE 360° — COLLIER MULTIRANGS PERLES DE CORAIL (ART-301)", fill=(255, 255, 255), font=font_title)
draw.text((40, 62), "420 perles individuelles PBR (Corail, Or, Ivoire nacré, Perles focales) · Drapé 3D volumique · Fermoir velours · Zéro trou parasite", fill=(160, 185, 215), font=font_sub)

panels = [
    (ref_p, "Photo Source", "Collier 5 rangs perles et fermoir rouge.", 40),
    (front_p, "Vue Face (0°)", "Alignement fidèle aux 5 rangs du catalogue.", 510),
    (hero_p, "Vue 360° Hero (35°)", "Relief 3D, reflets métalliques & perles nacrées.", 980),
    (side_p, "Vue Profil (90°)", "Courbure et drapé volumique en profondeur.", 1450),
    (back_p, "Vue Dos (180°)", "Fermoir velours rouge & continuité des perles.", 1920)
]

pw, ph = 440, 620

for p_path, title, desc, x in panels:
    y = 125
    draw.rectangle([(x, y), (x + pw, y + ph)], fill=(20, 26, 35), outline=(45, 60, 80), width=2)
    draw.text((x + 15, y + 15), title, fill=(255, 215, 0), font=font_col)
    
    if os.path.exists(p_path):
        im = Image.open(p_path).convert("RGBA")
        im.thumbnail((pw - 30, ph - 95), Image.Resampling.LANCZOS)
        ox = x + (pw - im.size[0]) // 2
        oy = y + 50 + (ph - 95 - im.size[1]) // 2
        tile = Image.new("RGB", im.size, (10, 14, 20))
        tile.paste(im, (0, 0), im.split()[3] if im.mode == "RGBA" else None)
        board.paste(tile, (ox, oy))
    
    draw.text((x + 15, y + ph - 30), desc, fill=(180, 195, 215), font=font_body)

board.save(out_board, "PNG", optimize=True)
print("Saved 360 showcase board to:", out_board)

# Copy to brain artifact directory
artifact_p = r"C:\Users\WILFRIED\.gemini\antigravity\brain\a6afba35-f0a6-4827-a7a0-51c2e154eb99\necklace_360_masterpiece_showcase.png"
board.save(artifact_p, "PNG", optimize=True)
print("Mirrored to artifacts:", artifact_p)
