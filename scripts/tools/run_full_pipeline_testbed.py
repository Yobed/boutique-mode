import os
import subprocess
import json
import time

blender_exe = r"C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\blender.exe"
blender_py = r"C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\5.2\python\bin\python.exe"

script_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline"
analyzer_script = os.path.join(script_dir, "component_analyzer.py")
orchestrator_script = os.path.join(script_dir, "orchestrator.py")

test_cases = [
    {
        "id": "case1_couch_misleading_sac",
        "file": "sac_demo.jpg",
        "name": "Canapé contemporain (Nom trompeur: sac_demo.jpg)",
        "ground_truth": "Mobilier lounge horizontal",
        "filename_hint": "fashion_handbag"
    },
    {
        "id": "case2_vase_concordant",
        "file": "accessoire_vase.png",
        "name": "Vase en céramique (Nom concordant: accessoire_vase.png)",
        "ground_truth": "Solide de révolution axisymétrique",
        "filename_hint": "tableware_lathe"
    },
    {
        "id": "case3_bag_misleading_sofa",
        "file": "sofa_demo.png",
        "name": "Sac de luxe (Nom trompeur: sofa_demo.png)",
        "ground_truth": "Sac à main maroquinerie",
        "filename_hint": "horizontal_lounge_furniture"
    },
    {
        "id": "case4_vase_misleading_sac",
        "file": "sac_porcelaine.png",
        "name": "Vase en céramique (Nom trompeur: sac_porcelaine.png)",
        "ground_truth": "Solide de révolution axisymétrique",
        "filename_hint": "fashion_handbag"
    },
    {
        "id": "case5_lamp_concordant",
        "file": "lampe_table.png",
        "name": "Lampe de table minimaliste (Nom concordant: lampe_table.png)",
        "ground_truth": "Luminaire sur pied élancé",
        "filename_hint": "slender_pedestal_lamp"
    },
    {
        "id": "case6_electronics_neutral",
        "file": "produit_neutre_001.png",
        "name": "Boîtier électronique SSD (Nom neutre: produit_neutre_001.png)",
        "ground_truth": "Boîtier électronique prismatique",
        "filename_hint": "None (Neutre)"
    },
    {
        "id": "case7_bag_concordant",
        "file": "sac_cuir_luxe.png",
        "name": "Sac à main de luxe (Nom concordant: sac_cuir_luxe.png)",
        "ground_truth": "Sac à main maroquinerie",
        "filename_hint": "fashion_handbag"
    }
]

base_input_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images"
base_output_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\outputs\test_mission36_pipeline"
specs_dir = os.path.join(base_output_dir, "specs")
os.makedirs(specs_dir, exist_ok=True)

print("================================================================================")
print("  EXÉCUTION COMPLÈTE DU BANC D'ESSAI MULTI-CATÉGORIES (MISSION 36)")
print("================================================================================")

summary_results = []

for case in test_cases:
    cid = case["id"]
    fname = case["file"]
    img_path = os.path.join(base_input_dir, fname)
    spec_path = os.path.join(specs_dir, f"{cid}_spec.json")
    case_out_dir = os.path.join(base_output_dir, cid)
    os.makedirs(case_out_dir, exist_ok=True)
    
    print(f"\n>>> Traitement : {case['name']}")
    print(f"    Image: {img_path}")
    
    # 1. Analyse et classification sémantique
    cmd_ana = [blender_py, analyzer_script, "--image", img_path, "--output", spec_path]
    t0 = time.time()
    res_ana = subprocess.run(cmd_ana, capture_output=True, text=True)
    t_ana = time.time() - t0
    
    if res_ana.returncode != 0:
        print(f"    [ERREUR ANALYSE] {res_ana.stderr}")
        continue
        
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)
        
    sc = spec.get("semantic_classification", {})
    cat = spec.get("category")
    contra = sc.get("contradiction_detected", False)
    comp_names = [c["name"] for c in spec.get("components", [])]
    
    print(f"    Catégorie certifiée : {cat} (conf={sc.get('final_confidence', 0):.2f})")
    print(f"    Contradiction       : {contra}")
    print(f"    Composants générés  : {comp_names}")
    
    # 2. Modélisation 3D, Shaders et Rendu Studio
    cmd_blend = [
        blender_exe, "--factory-startup", "-b", "-P", orchestrator_script,
        "--", "--spec", spec_path, "--output-dir", case_out_dir
    ]
    t0 = time.time()
    res_blend = subprocess.run(cmd_blend, capture_output=True, text=True)
    t_blend = time.time() - t0
    
    if res_blend.returncode != 0:
        print(f"    [ERREUR BLENDER] {res_blend.stderr}")
        continue
        
    # Vérification des livrables
    glb_files = [f for f in os.listdir(case_out_dir) if f.endswith(".glb")]
    glb_path = os.path.join(case_out_dir, glb_files[0]) if glb_files else None
    glb_size = os.path.getsize(glb_path) if glb_path else 0
    
    previews_dir = os.path.join(case_out_dir, "previews")
    hero_previews = [f for f in os.listdir(previews_dir) if "hero" in f and f.endswith(".png")] if os.path.exists(previews_dir) else []
    hero_path = os.path.join(previews_dir, hero_previews[0]) if hero_previews else None
    
    summary_json_path = os.path.join(case_out_dir, f"{spec['object_id']}_summary.json")
    val_verdict = "UNKNOWN"
    if os.path.exists(summary_json_path):
        with open(summary_json_path, "r", encoding="utf-8") as f:
            sum_data = json.load(f)
            val_verdict = sum_data.get("validation_verdict", "UNKNOWN")
            
    print(f"    Validation Géom : {val_verdict}")
    print(f"    GLB livré       : {os.path.basename(glb_path) if glb_path else 'AUCUN'} ({glb_size} octets)")
    print(f"    Hero Preview    : {os.path.basename(hero_path) if hero_path else 'AUCUN'}")
    
    summary_results.append({
        "case": case,
        "spec": spec,
        "category": cat,
        "contradiction": contra,
        "contradiction_details": sc.get("contradiction_details"),
        "components": comp_names,
        "val_verdict": val_verdict,
        "glb_path": glb_path,
        "glb_size": glb_size,
        "hero_path": hero_path,
        "render_time_s": round(t_ana + t_blend, 1)
    })

results_manifest_path = os.path.join(base_output_dir, "pipeline_testbed_results.json")
with open(results_manifest_path, "w", encoding="utf-8") as f:
    json.dump(summary_results, f, indent=2)

print("\n================================================================================")
print(f"BANC D'ESSAI TERMINÉ : {len(summary_results)}/{len(test_cases)} CAS TRAITÉS AVEC SUCCÈS")
print(f"Manifeste sauvegardé : {results_manifest_path}")
print("================================================================================")
