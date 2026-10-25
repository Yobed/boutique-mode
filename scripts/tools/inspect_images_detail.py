import os
from PIL import Image
import numpy as np

def inspect(p):
    im = Image.open(p)
    arr = np.array(im)
    print("="*60)
    print(f"Path: {p}")
    print(f"Size: {im.size}, Mode: {im.mode}, Shape: {arr.shape}")
    # Mean color
    if len(arr.shape) == 3:
        mean_c = arr.mean(axis=(0,1))[:3]
        print(f"Mean RGB: {mean_c}")
    # Check if transparent or white background
    if arr.shape[-1] == 4:
        alpha = arr[:,:,3]
        print(f"Alpha > 0 count: {np.sum(alpha > 10)} / {alpha.size}")
    # Aspect ratio
    w, h = im.size
    print(f"Aspect ratio w/h: {w/h:.3f}")

inspect(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\videoframe_6041.png")
inspect(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\image de reference.jpg")
inspect(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\giro.jpg.jpeg")
