import os
from PIL import Image

paths = [
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\image de reference.jpg",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\videoframe_6041.png",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\giro.jpg.jpeg",
]

for p in paths:
    if os.path.exists(p):
        im = Image.open(p)
        print(f"{os.path.basename(p)}: size={im.size}, mode={im.mode}")
