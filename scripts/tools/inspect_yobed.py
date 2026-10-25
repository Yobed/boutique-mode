import os
from PIL import Image

yobed = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement\YOBED"
for f in os.listdir(yobed):
    p = os.path.join(yobed, f)
    if os.path.isfile(p):
        im = Image.open(p)
        print(f"YOBED {f}: {im.size} {im.mode} ({os.path.getsize(p)} bytes)")
