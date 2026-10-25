import os
from PIL import Image

wt = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement"
candidates = [
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
]

for name in candidates:
    p = os.path.join(wt, name)
    if os.path.exists(p):
        try:
            im = Image.open(p)
            print(f"{name} | {im.size} | {im.mode}")
        except Exception as e:
            print(f"{name} | Error: {e}")
