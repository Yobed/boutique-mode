import os
import re

pipeline_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline"
keywords = ["fname", "basename", "category", "hint", "sac", "bag", "vase", "lamp", "ssd", "sofa", "couch", "cuir", "maroquinerie"]

print(f"=== AUDIT SÉMANTIQUE DANS {pipeline_dir} ===")

for root, dirs, files in os.walk(pipeline_dir):
    if "backups" in root:
        continue
    for f in sorted(files):
        if not (f.endswith(".py") or f.endswith(".ps1")):
            continue
        filepath = os.path.join(root, f)
        with open(filepath, "r", encoding="utf-8", errors="ignore") as file_obj:
            lines = file_obj.readlines()
        
        matches = []
        for i, line in enumerate(lines):
            l_lower = line.lower()
            for kw in keywords:
                if kw in l_lower:
                    matches.append((i + 1, kw, line.strip()))
                    break
        
        print(f"\nFichier: {f} ({len(matches)} occurrences)")
        for line_no, kw, content in matches[:20]: # show first 20
            print(f"  L{line_no:4d} [{kw}]: {content[:100]}")
        if len(matches) > 20:
            print(f"  ... et {len(matches) - 20} autres occurrences.")
