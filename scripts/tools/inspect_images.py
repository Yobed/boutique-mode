import os
import hashlib
from PIL import Image

ref_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images"
print("Scanning:", ref_dir)
for root, dirs, files in os.walk(ref_dir):
    for f in sorted(files):
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
            p = os.path.join(root, f)
            with open(p, 'rb') as fp:
                data = fp.read()
                h = hashlib.sha256(data).hexdigest()
            try:
                im = Image.open(p)
                info = f"{im.size[0]}x{im.size[1]} {im.mode}"
            except Exception as e:
                info = str(e)
            rel = os.path.relpath(p, ref_dir)
            print(f"{rel} | {len(data)} bytes | {info} | SHA256: {h}")
