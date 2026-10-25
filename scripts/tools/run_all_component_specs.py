import os
import subprocess
import sys
import json

blender_py = r"C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\5.2\python\bin\python.exe"
analyzer_script = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline\component_analyzer.py"
test_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images"
out_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\test_mission36_specs"
os.makedirs(out_dir, exist_ok=True)

test_cases = [
    ("sac_demo.jpg", None, False, "horizontal_lounge_furniture", True),
    ("sofa_demo.png", None, False, "fashion_leather_goods", True),
    ("accessoire_vase.png", None, False, "scandinavian_tableware_lathe", False),
    ("sac_porcelaine.png", None, False, "scandinavian_tableware_lathe", True),
    ("lampe_table.png", None, False, "minimalist_lighting", False),
    ("produit_neutre_001.png", None, False, "industrial_rugged_electronics", False),
    ("sac_cuir_luxe.png", None, False, "fashion_leather_goods", False),
    ("sac_demo.jpg", "sac", True, "fashion_leather_goods", True) # Forced by user
]

print("=== GÉNÉRATION DES SPÉCIFICATIONS SPATIALES DU BANC DE TEST MISSION 36 ===")

results = []
all_ok = True

for fname, cat_arg, force_flag, expected_cat, expect_contra in test_cases:
    img_path = os.path.join(test_dir, fname)
    prefix = f"forced_{fname}" if force_flag else fname.replace(".", "_")
    spec_path = os.path.join(out_dir, f"{prefix}_spec.json")
    
    cmd = [blender_py, analyzer_script, "--image", img_path, "--output", spec_path]
    if cat_arg:
        cmd.extend(["--category", cat_arg])
    if force_flag:
        cmd.append("--force-category")
        
    proc = subprocess.run(cmd, capture_output=True, text=True)
    
    if proc.returncode != 0:
        print(f"[ERREUR EXÉCUTION] {fname}: {proc.stderr}")
        all_ok = False
        continue
        
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
        
    sc = spec.get("semantic_classification", {})
    actual_cat = spec.get("category")
    actual_contra = sc.get("contradiction_detected", False)
    comp_names = [c["name"] for c in spec.get("components", [])]
    
    cat_match = (actual_cat == expected_cat)
    contra_match = (actual_contra == expect_contra)
    case_ok = cat_match and contra_match
    if not case_ok:
        all_ok = False
        
    print(f"\n[{fname}] (arg_cat={cat_arg}, force={force_flag})")
    print(f"  Catégorie obtenue : {actual_cat} (Attendu: {expected_cat}) -> {'OK' if cat_match else 'FAIL'}")
    print(f"  Contradiction     : {actual_contra} (Attendu: {expect_contra}) -> {'OK' if contra_match else 'FAIL'}")
    print(f"  Composants ({len(comp_names)}): {comp_names}")
    
    results.append({
        "file": fname,
        "arg_cat": cat_arg,
        "force": force_flag,
        "expected_cat": expected_cat,
        "actual_cat": actual_cat,
        "expect_contra": expect_contra,
        "actual_contra": actual_contra,
        "components": comp_names,
        "spec_path": spec_path,
        "ok": case_ok
    })

print("\n=======================================================")
print(f"RÉSULTAT DES SPÉCIFICATIONS : {'100% SUCCÈS' if all_ok else 'DES CAS ONT ÉCHOUÉ'}")
print("=======================================================")
