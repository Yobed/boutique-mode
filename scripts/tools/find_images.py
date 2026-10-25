import os
import glob

print("Scanning for product images in boutique-mode and Blend...")
for root_dir in [
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend"
]:
    for root, dirs, files in os.walk(root_dir):
        if "node_modules" in root or ".git" in root or ".next" in root:
            continue
        for f in files:
            if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
                full = os.path.join(root, f)
                sz = os.path.getsize(full)
                if sz > 2000:
                    print(f"  {sz:7d} bytes: {full}")
