import os
import numpy as np
from PIL import Image

ref_path = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\collier_art301_ref.png"
out_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\detourage_diagnostic"
os.makedirs(out_dir, exist_ok=True)

im = Image.open(ref_path).convert("RGB")
print(f"Loaded ref image: {im.size}, mode: {im.mode}")

# Let's check background color
arr = np.array(im)
# Corners background sample
corners = np.concatenate([
    arr[:30, :30].reshape(-1, 3),
    arr[:30, -30:].reshape(-1, 3),
    arr[-30:, :30].reshape(-1, 3),
    arr[-30:, -30:].reshape(-1, 3)
], axis=0)
bg_mean = corners.mean(axis=0)
bg_std = corners.std(axis=0)
print(f"Background mean RGB: {bg_mean}, std: {bg_std}")

# Let's inspect the center (the hole inside the necklace loop)
cx, cy = im.size[0] // 2, im.size[1] // 2
center_sample = arr[cy-50:cy+50, cx-50:cx+50].reshape(-1, 3)
center_mean = center_sample.mean(axis=0)
center_std = center_sample.std(axis=0)
print(f"Center opening mean RGB: {center_mean}, std: {center_std}")

# Color distance from background
diff = np.linalg.norm(arr.astype(float) - bg_mean, axis=-1)
print(f"Diff stats: min={diff.min():.1f}, max={diff.max():.1f}, median={np.median(diff):.1f}")

# Threshold test
for thresh in [15, 25, 35, 45, 60]:
    mask = diff > thresh
    Image.fromarray((mask * 255).astype(np.uint8)).save(os.path.join(out_dir, f"naive_thresh_{thresh}.png"))
    print(f"Threshold {thresh}: foreground fraction = {mask.mean():.3f}")

print("Diagnostic script completed.")
