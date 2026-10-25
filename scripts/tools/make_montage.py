import os
from PIL import Image

wt = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement"
imgs = [
    "Gemini_Generated_Image_44o3wn44o3wn44o3.png",
    "Gemini_Generated_Image_4c89o04c89o04c89.png",
    "Gemini_Generated_Image_j2cf0uj2cf0uj2cf.png",
    "Gemini_Generated_Image_s3gmc8s3gmc8s3gm.png",
    "Gemini_Generated_Image_t7mud2t7mud2t7mu.png",
    "Gemini_Generated_Image_ub35rzub35rzub35.png",
    "Generated Image GEMINI.jpeg",
    "Contemporary Office Desk L-Shape Executive Desk with 2 Storage Drawers - Right Hand Return 71_L x 63_W x 30_H Table Only Office Desks.jpeg",
    "Filtre.jpg",
    "GEL.jpg",
    "Image_fx (1).png",
    "Image_fx (2).png",
    "Image_fx (3).png",
    "Image_fx (4).png",
    "Image_fx.png",
    "Habillage murale.png",
    "Materiel yomi oussama.jpg",
    "Model ag.jpg",
    "PEC500.jpg"
]

out_sheet = Image.new("RGB", (1200, 1000), (240, 240, 240))
# Let's create a montage and save it
w_tile, h_tile = 240, 200
for i, name in enumerate(imgs[:20]):
    p = os.path.join(wt, name)
    if os.path.exists(p):
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail((w_tile - 10, h_tile - 25))
            x = (i % 5) * w_tile + 5
            y = (i // 5) * h_tile + 5
            out_sheet.paste(im, (x, y))
        except Exception as e:
            pass

out_path = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\reports\montage_candidates.png"
os.makedirs(os.path.dirname(out_path), exist_ok=True)
out_sheet.save(out_path)
print("Montage saved to:", out_path)
