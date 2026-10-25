import os

bureau = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau"
dirs_to_check = ["Blender", "MonVeto", "Profneci", "Ressource Humaine", "Site", "TEST", "PROJET FE"]

for d in dirs_to_check:
    full_d = os.path.join(bureau, d)
    if os.path.exists(full_d):
        imgs = []
        for root, _, files in os.walk(full_d):
            for f in files:
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    imgs.append(os.path.join(root, f))
        print(f"Directory {d}: {len(imgs)} images")
        for img in imgs[:10]:
            print(f"  {os.path.relpath(img, full_d)} ({os.path.getsize(img)} bytes)")
