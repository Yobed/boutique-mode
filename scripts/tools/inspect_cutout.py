import os
import numpy as np
from PIL import Image

d = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\3d_neural\art-301"
cutout_p = os.path.join(d, "cutout.png")
input_p = os.path.join(d, "input.png")
source_p = os.path.join(d, "source.jpg")

im_cut = Image.open(cutout_p)
print(f"Cutout: {im_cut.size}, mode: {im_cut.mode}")
arr_cut = np.array(im_cut)
alpha = arr_cut[:, :, 3]

print(f"Alpha > 0: {(alpha > 0).mean():.3f}")
print(f"Alpha > 127: {(alpha > 127).mean():.3f}")
print(f"Alpha == 255: {(alpha == 255).mean():.3f}")

# Check alpha distribution in the center opening (where the neck hole should be)
h, w = alpha.shape
cx, cy = w // 2, h // 2
center_alpha = alpha[int(cy*0.6):int(cy*1.2), int(cx*0.7):int(cx*1.3)]
print(f"Center opening alpha mean: {center_alpha.mean():.1f}, min: {center_alpha.min()}, max: {center_alpha.max()}")
print(f"Center opening pixels > 127: {(center_alpha > 127).sum()} / {center_alpha.size}")

# Check connected components and holes
from scipy import ndimage
bin_mask = alpha > 127
lbl, num_features = ndimage.label(bin_mask)
print(f"Number of connected components: {num_features}")

# Fill holes
filled = ndimage.binary_fill_holes(bin_mask)
holes = filled & (~bin_mask)
lbl_holes, num_holes = ndimage.label(holes)
print(f"Number of internal holes: {num_holes}, total hole pixels: {holes.sum()}")

# Analyze hole sizes
hole_sizes = ndimage.sum(holes, lbl_holes, range(1, num_holes + 1))
print(f"Hole sizes (top 10): {sorted(hole_sizes, reverse=True)[:10]}")

# Save visual representation of the cutout on dark and light backgrounds
tile_dark = Image.new("RGB", im_cut.size, (15, 15, 15))
tile_dark.paste(im_cut, (0, 0), im_cut.split()[3])
tile_dark.save(os.path.join(d, "cutout_on_black.png"))

tile_holes = Image.new("RGB", im_cut.size, (0, 0, 0))
# Paint object white, holes red
obj_arr = np.zeros((h, w, 3), dtype=np.uint8)
obj_arr[bin_mask] = [200, 200, 200]
obj_arr[holes] = [255, 30, 30]
Image.fromarray(obj_arr).save(os.path.join(d, "mask_and_holes_visual.png"))
print("Saved visualization images to:", d)
