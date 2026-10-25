import os

wt = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Wilfried Telechargement"
for root, dirs, files in os.walk(wt):
    for f in sorted(files):
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            p = os.path.join(root, f)
            print(f"{os.path.relpath(p, wt)} ({os.path.getsize(p)} bytes)")
