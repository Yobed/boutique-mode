import os

keywords = ["sac", "bag", "purse", "pochette", "tote", "handbag", "shoe", "chaussure", "sneaker", "boot", "escarpin", "basket", "sandale"]
bureau = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau"

exclude = {"node_modules", ".git", ".next", "dist", "build", "site_out", "reports"}
found = []
for root, dirs, files in os.walk(bureau):
    dirs[:] = [d for d in dirs if d not in exclude and not d.startswith(".")]
    for f in files:
        fl = f.lower()
        if any(k in fl for k in keywords):
            p = os.path.join(root, f)
            found.append(p)

print(f"Total matching files: {len(found)}")
for p in found:
    if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        print(f"  IMAGE: {p} ({os.path.getsize(p)} bytes)")
    else:
        # only print non-images if few
        if len(found) < 30:
            print(f"  OTHER: {p}")
