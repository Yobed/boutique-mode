import os
import sys
import numpy as np
from PIL import Image

PIPELINE_DIR = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline"
sys.path.insert(0, PIPELINE_DIR)

from neural_reconstruct import _matte

ref_path = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
out_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
os.makedirs(out_dir, exist_ok=True)

im = Image.open(ref_path).convert("RGB")
try:
    alpha = _matte(im)
    Image.fromarray(alpha).save(os.path.join(out_dir, "u2net_alpha.png"))
    # Save cutout
    rgba = np.dstack([np.array(im), alpha])
    Image.fromarray(rgba, "RGBA").save(os.path.join(out_dir, "u2net_cutout.png"))
    print("U2-Net matte successful!")
    print(f"Alpha min={alpha.min()}, max={alpha.max()}, mean={alpha.mean():.1f}")
    
    # Check binary mask at 127
    bin_mask = alpha > 127
    Image.fromarray((bin_mask * 255).astype(np.uint8)).save(os.path.join(out_dir, "u2net_bin_mask_127.png"))
    print(f"Binary mask > 127 foreground fraction: {bin_mask.mean():.3f}")
    
    # Check if there are internal holes inside the strands
    from scipy import ndimage
    filled = ndimage.binary_fill_holes(bin_mask)
    holes = filled & (~bin_mask)
    Image.fromarray((holes * 255).astype(np.uint8)).save(os.path.join(out_dir, "u2net_holes.png"))
    print(f"Holes pixel count: {holes.sum()}")
    
except Exception as e:
    print(f"Error running _matte: {e}")
