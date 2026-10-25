import os
from collections import Counter

bureau = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau"
exclude_dirs = {"node_modules", ".git", ".next", "dist", "build", ".venv", "site_out", "reports", "render_studio", "outputs"}

counts = Counter()
for root, dirs, files in os.walk(bureau):
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            rel = os.path.relpath(root, bureau)
            top_dir = rel.split(os.sep)[0]
            counts[top_dir] += 1

for k, v in counts.most_common():
    print(f"{k}: {v} images")
