import os
import hashlib
import json
import shutil

pipeline_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline"
backup_dir = os.path.join(pipeline_dir, "backups", "mission37_freeze")
os.makedirs(backup_dir, exist_ok=True)

modules = [
    "semantic_classifier.py",
    "component_analyzer.py",
    "image_analyzer.py",
    "builder.py",
    "materials.py",
    "orchestrator.py",
    "studio.py",
    "validator.py",
    "run_fashion_3d.ps1",
]

manifest = {}
print("=== MISSION 37 - CODE FREEZE MANIFEST ===")
for mod in modules:
    p = os.path.join(pipeline_dir, mod)
    if os.path.exists(p):
        with open(p, "rb") as fp:
            data = fp.read()
            h = hashlib.sha256(data).hexdigest()
        manifest[mod] = {
            "size": len(data),
            "sha256": h,
            "path": p
        }
        # backup copy
        shutil.copy2(p, os.path.join(backup_dir, mod + ".frozen"))
        print(f"FROZEN: {mod:<24} | {len(data):>7} B | SHA256: {h}")
    else:
        print(f"MISSING: {mod}")

# Also freeze reference models in public/models
models_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\public\models"
models_backup = os.path.join(backup_dir, "public_models")
os.makedirs(models_backup, exist_ok=True)
for mf in ["sac_demo.glb", "sac_demo-poster.png", "accessoire_vase.glb", "accessoire_vase-poster.png"]:
    mp = os.path.join(models_dir, mf)
    if os.path.exists(mp):
        with open(mp, "rb") as fp:
            h = hashlib.sha256(fp.read()).hexdigest()
        shutil.copy2(mp, os.path.join(models_backup, mf))
        print(f"SAVED MODEL: {mf:<26} | SHA256: {h}")

out_manifest_path = os.path.join(backup_dir, "code_freeze_manifest.json")
with open(out_manifest_path, "w", encoding="utf-8") as fp:
    json.dump(manifest, fp, indent=2)

print("\nManifest saved to:", out_manifest_path)
