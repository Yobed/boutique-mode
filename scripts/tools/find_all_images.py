import os

bureau = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau"
exclude_dirs = {"node_modules", ".git", ".next", "dist", "build", ".venv", "site_out", "reports", "render_studio"}

found = []
for root, dirs, files in os.walk(bureau):
    dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith(".")]
    for f in files:
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
            p = os.path.join(root, f)
            sz = os.path.getsize(p)
            found.append((p, sz))

print(f"Total images found: {len(found)}")
for p, sz in found[:40]:
    rel = os.path.relpath(p, bureau)
    print(f"  {rel} ({sz} bytes)")
if len(found) > 40:
    print(f"  ... and {len(found)-40} more")
