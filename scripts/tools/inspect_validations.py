import json
import glob
import os

base_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\test_mission36_pipeline"

for val_file in glob.glob(os.path.join(base_dir, "**", "*_validation.json"), recursive=True):
    with open(val_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    print(f"\n=== {os.path.basename(val_file)} ===")
    print("Verdict:", data.get("verdict"))
    print("Issues:", data.get("issues"))
