import cv2
import numpy as np
from PIL import Image

ref_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
im = Image.open(ref_p)
w, h = im.size
print(f"Image size: {w}x{h}")

# Let's inspect the key coordinates of the necklace:
# - Clasp at the top
# - Inner loop bottom
# - Outer loop bottom
# - Leftmost extent
# - Rightmost extent

arr = np.array(im.convert("RGB"))
# Color thresholds for clasp (deep red)
clasp_mask = (arr[:, :, 0] > 100) & (arr[:, :, 1] < 40) & (arr[:, :, 2] < 50)
ys, xs = np.where(clasp_mask)
if len(ys) > 0:
    clasp_top = ys.min()
    clasp_bot = ys.max()
    clasp_left = xs.min()
    clasp_right = xs.max()
    print(f"Clasp bbox: top={clasp_top}, bot={clasp_bot}, left={clasp_left}, right={clasp_right}")
    print(f"Clasp size: w={clasp_right-clasp_left}, h={clasp_bot-clasp_top}")

# Overall necklace mask (from our clean mask)
mask_p = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic\03_perfect_necklace_mask.png"
mask = cv2.imread(mask_p, cv2.IMREAD_GRAYSCALE)
ys, xs = np.where(mask > 127)
print(f"Necklace bounds: Y=[{ys.min()}, {ys.max()}], X=[{xs.min()}, {xs.max()}]")
nw = xs.max() - xs.min()
nh = ys.max() - ys.min()
print(f"Necklace span: width={nw} px, height={nh} px (Aspect ratio: {nw/nh:.3f})")

# Sample colors
# Gold beads: high R, G, lower B (golden/brass)
# Coral beads: high R, medium G, low B (orange/coral)
# White pearls: high R, G, B
print("Analysis complete.")
