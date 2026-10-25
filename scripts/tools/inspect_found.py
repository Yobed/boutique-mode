import os
from PIL import Image

paths = [
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blender\fauteuil_lounge.png",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Ressource Humaine\public\images\biometric_terminal_hero.png",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement\Contemporary Office Desk L-Shape Executive Desk with 2 Storage Drawers - Right Hand Return 71_L x 63_W x 30_H Table Only Office Desks.jpeg",
]

for p in paths:
    if os.path.exists(p):
        im = Image.open(p)
        print(f"{os.path.basename(p)} | {im.size} | {im.mode}")
