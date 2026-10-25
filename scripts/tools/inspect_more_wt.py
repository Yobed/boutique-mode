import os
from PIL import Image

wt = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement"
for name in ["GEL.jpg", "Filtre.jpg", "PEC500.jpg", "Model ag.jpg", "1dc9a883-7ed7-40be-91fb-de5a035d9ce2.jpeg"]:
    p = os.path.join(wt, name)
    if os.path.exists(p):
        im = Image.open(p)
        print(f"{name}: {im.size} {im.mode} ({os.path.getsize(p)} bytes)")
