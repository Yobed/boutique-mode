import os
from PIL import Image

def analyze_img(p):
    im = Image.open(p)
    colors = im.getcolors(maxcolors=1000000)
    print(f"File: {os.path.basename(p)}, Size: {im.size}, Mode: {im.mode}")
    # print thumbnail ascii or bounding box of non-white
    bbox = im.getbbox()
    print(f"  bbox: {bbox}")

analyze_img(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\image de reference.jpg")
analyze_img(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\videoframe_6041.png")
analyze_img(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\giro.jpg.jpeg")
