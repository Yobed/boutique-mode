import os

candidates = []
for p in [r"C:\Users\WILFRIED\Downloads", r"C:\Users\WILFRIED\Desktop", r"C:\Users\WILFRIED\Pictures"]:
    if os.path.exists(p):
        for root, dirs, files in os.walk(p):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("node_modules", "AppData")]
            for f in files:
                if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    candidates.append(os.path.join(root, f))

print(f"Total images found in Downloads/Desktop/Pictures: {len(candidates)}")
for c in candidates:
    fl = os.path.basename(c).lower()
    if any(k in fl for k in ["shoe", "chaussure", "sac", "bag", "boot", "sneaker", "vase", "lamp", "bottle", "bouteille", "fauteuil", "sofa", "chair", "table"]):
        print("  MATCH:", c)
