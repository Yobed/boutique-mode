import os
import sys
import time
import json
import hashlib
import subprocess
import shutil
from PIL import Image

BLENDER_EXE = r"C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\blender.exe"
BLENDER_PY  = r"C:\Users\WILFRIED\Downloads\Blender-5.2.2-Portable\blender-5.2.2-windows-x64\5.2\python\bin\python.exe"

PROJECT_ROOT = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode"
TEST_CASES_DIR = os.path.join(PROJECT_ROOT, "inputs", "product_images", "mission37_test_cases")
CAMPAIGN_OUT_DIR = os.path.join(PROJECT_ROOT, "outputs", "test_mission37_campaign")
os.makedirs(CAMPAIGN_OUT_DIR, exist_ok=True)

COMPONENT_ANALYZER = os.path.join(PROJECT_ROOT, "scripts", "3d_pipeline", "component_analyzer.py")
ORCHESTRATOR = os.path.join(PROJECT_ROOT, "scripts", "3d_pipeline", "orchestrator.py")
VALIDATOR = os.path.join(PROJECT_ROOT, "scripts", "3d_pipeline", "validator.py")

test_cases = [
    {
        "case_id": "case01",
        "file": "case01_sofa_trompeur.jpg",
        "ground_truth_category": "fashion_leather_goods",
        "ground_truth_name": "Sac à main Kelly (cuir, anse supérieure)",
        "expected_features": ["sac", "cuir", "anse/poignée", "fermoir"],
        "has_misleading_name": True,
        "filename_keyword": "sofa"
    },
    {
        "case_id": "case02",
        "file": "case02_produit_neutre_chaussure.png",
        "ground_truth_category": "footwear_athletic",
        "ground_truth_name": "Chaussure de sport / sneaker Merrell",
        "expected_features": ["chaussure", "semelle", "asymétrie profil"],
        "has_misleading_name": False,
        "filename_keyword": "produit_neutre"
    },
    {
        "case_id": "case03",
        "file": "case03_sac_trompeur_fauteuil.png",
        "ground_truth_category": "horizontal_lounge_furniture",
        "ground_truth_name": "Fauteuil lounge contemporain",
        "expected_features": ["fauteuil/canapé", "assise rembourrée", "dossier"],
        "has_misleading_name": True,
        "filename_keyword": "sac"
    },
    {
        "case_id": "case04",
        "file": "case04_bouteille_isotherme.png",
        "ground_truth_category": "scandinavian_tableware_lathe",
        "ground_truth_name": "Bouteille thermos isotherme sous vide",
        "expected_features": ["bouteille", "corps révolution", "bouchon"],
        "has_misleading_name": False,
        "filename_keyword": "bouteille"
    },
    {
        "case_id": "case05",
        "file": "case05_vase_carafe_verre.png",
        "ground_truth_category": "scandinavian_tableware_lathe",
        "ground_truth_name": "Vase / carafe scandinave en verre",
        "expected_features": ["vase", "révolution", "col rétréci"],
        "has_misleading_name": False,
        "filename_keyword": "vase"
    },
    {
        "case_id": "case06",
        "file": "case06_sofa_trompeur_lampe.jpg",
        "ground_truth_category": "minimalist_lighting",
        "ground_truth_name": "Lampe de bureau halogène sur tige",
        "expected_features": ["lampe", "socle", "tige mince", "diffuseur"],
        "has_misleading_name": True,
        "filename_keyword": "sofa"
    },
    {
        "case_id": "case07",
        "file": "case07_enceinte_acoustique.png",
        "ground_truth_category": "cylindrical_electronics",
        "ground_truth_name": "Enceinte acoustique cylindrique de table",
        "expected_features": ["appareil électronique", "cylindre compact"],
        "has_misleading_name": False,
        "filename_keyword": "enceinte"
    },
    {
        "case_id": "case08",
        "file": "case08_tasse_mug_anse.png",
        "ground_truth_category": "tableware_with_handle",
        "ground_truth_name": "Tasse mug en céramique émaillée à anse",
        "expected_features": ["mug/tasse", "anse/poignée", "corps céramique"],
        "has_misleading_name": False,
        "filename_keyword": "mug"
    },
    {
        "case_id": "case09",
        "file": "case09_marteau_asymetrique.png",
        "ground_truth_category": "asymmetric_tool_handled",
        "ground_truth_name": "Marteau mécanicien à manche (objet asymétrique)",
        "expected_features": ["outil asymétrique", "manche", "tête métallique"],
        "has_misleading_name": False,
        "filename_keyword": "marteau"
    },
    {
        "case_id": "case10",
        "file": "case10_fer_vapeur_multimat.png",
        "ground_truth_category": "complex_multimaterial_appliance",
        "ground_truth_name": "Fer à repasser à vapeur multi-matériaux",
        "expected_features": ["multi-matériaux", "poignée fermée", "semelle inox"],
        "has_misleading_name": False,
        "filename_keyword": "fer"
    },
    {
        "case_id": "case11",
        "file": "case11_tabouret_tripode.png",
        "ground_truth_category": "furniture_tripod_seating",
        "ground_truth_name": "Tabouret tripode scandinave en bois massif",
        "expected_features": ["tabouret/assise", "3 pieds", "disque assise"],
        "has_misleading_name": False,
        "filename_keyword": "tabouret"
    }
]

campaign_results = []

print("=================================================================", flush=True)
print("  MISSION 37 : CAMPAGNE D'ÉVALUATION SUR 11 PRODUITS INÉDITS", flush=True)
print("=================================================================", flush=True)
start_campaign_time = time.time()

for idx, tc in enumerate(test_cases, 1):
    case_id = tc["case_id"]
    fname = tc["file"]
    img_path = os.path.join(TEST_CASES_DIR, fname)
    case_out_dir = os.path.join(CAMPAIGN_OUT_DIR, case_id)
    os.makedirs(case_out_dir, exist_ok=True)
    
    spec_path = os.path.join(case_out_dir, f"{case_id}_spec.json")
    log_path = os.path.join(case_out_dir, "execution.log")
    
    with open(img_path, "rb") as fp:
        img_bytes = fp.read()
        sha256 = hashlib.sha256(img_bytes).hexdigest()
    
    im = Image.open(img_path)
    img_dims = f"{im.size[0]}x{im.size[1]}"
    img_mode = im.mode
    
    print(f"\n--- [{idx}/{len(test_cases)}] {case_id}: {fname} ---", flush=True)
    print(f"  Ground Truth : {tc['ground_truth_name']}", flush=True)
    print(f"  Taille Image : {img_dims} ({img_mode}) | {len(img_bytes)} octets | SHA256: {sha256[:16]}...", flush=True)
    
    t0 = time.time()
    
    # 1. Step 1: Component analysis & semantic classification
    cmd_analyzer = [
        BLENDER_PY, COMPONENT_ANALYZER,
        "--image", img_path,
        "--output", spec_path
    ]
    
    with open(log_path, "w", encoding="utf-8") as log_fp:
        log_fp.write(f"=== STEP 1: COMPONENT ANALYZER ===\nCommand: {' '.join(cmd_analyzer)}\n\n")
        res_an = subprocess.run(cmd_analyzer, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log_fp.write(res_an.stdout)
        log_fp.write(f"\nExit code: {res_an.returncode}\n\n")
    
    analyzer_ok = (res_an.returncode == 0) and os.path.exists(spec_path)
    
    predicted_category = None
    category_confidence = 0.0
    contradiction_detected = False
    rejection_reason = None
    components_count = 0
    components_names = []
    object_id = case_id
    
    if analyzer_ok:
        try:
            with open(spec_path, "r", encoding="utf-8") as sfp:
                spec_data = json.load(sfp)
            object_id = spec_data.get("object_id", case_id)
            predicted_category = spec_data.get("category")
            components = spec_data.get("components", [])
            components_count = len(components)
            components_names = [c.get("name") for c in components]
            
            sc = spec_data.get("semantic_classification", {})
            category_confidence = sc.get("final_confidence", 0.0)
            contradiction_detected = sc.get("contradiction_detected", False)
            rejection_reason = sc.get("rejection_reason")
        except Exception as e:
            analyzer_ok = False
            with open(log_path, "a", encoding="utf-8") as log_fp:
                log_fp.write(f"Spec parsing error: {e}\n")
    
    print(f"  Classification : {predicted_category} (conf: {category_confidence:.2f})", flush=True)
    print(f"  Contradiction  : {'OUI (Nom rejeté)' if contradiction_detected else 'NON'}", flush=True)
    if rejection_reason:
        print(f"  Justification  : {rejection_reason}", flush=True)
    print(f"  Composants ({components_count}): {', '.join(components_names)}", flush=True)
    
    # 2. Step 2: 3D Generation & Studio Rendering via Blender Headless with --factory-startup
    cmd_orchestrator = [
        BLENDER_EXE, "--factory-startup", "-b",
        "-P", ORCHESTRATOR,
        "--",
        "--spec", spec_path,
        "--output-dir", case_out_dir
    ]
    
    with open(log_path, "a", encoding="utf-8") as log_fp:
        log_fp.write(f"=== STEP 2: 3D ORCHESTRATOR & STUDIO RENDERING ===\nCommand: {' '.join(cmd_orchestrator)}\n\n")
        res_orch = subprocess.run(cmd_orchestrator, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        log_fp.write(res_orch.stdout)
        log_fp.write(f"\nExit code: {res_orch.returncode}\n\n")
    
    # Locate generated GLB
    expected_glb = os.path.join(case_out_dir, f"{object_id}.glb")
    if not os.path.exists(expected_glb):
        for f in os.listdir(case_out_dir):
            if f.endswith(".glb"):
                expected_glb = os.path.join(case_out_dir, f)
                break
    
    glb_ok = os.path.exists(expected_glb) and os.path.getsize(expected_glb) > 0
    glb_size = os.path.getsize(expected_glb) if glb_ok else 0
    
    # 3. Step 3: GLB Technical Validation via validator.py
    validation_status = "FAILED"
    validation_issues = []
    
    if glb_ok:
        cmd_validator = [
            BLENDER_PY, VALIDATOR,
            "--glb", expected_glb,
            "--spec", spec_path
        ]
        with open(log_path, "a", encoding="utf-8") as log_fp:
            log_fp.write(f"=== STEP 3: GLB VALIDATOR ===\nCommand: {' '.join(cmd_validator)}\n\n")
            res_val = subprocess.run(cmd_validator, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            log_fp.write(res_val.stdout)
            log_fp.write(f"\nExit code: {res_val.returncode}\n\n")
        
        if "VALIDATION RÉUSSIE" in res_val.stdout or res_val.returncode == 0:
            validation_status = "PASS"
        else:
            validation_status = "WARNING_OR_FAIL"
            for line in res_val.stdout.splitlines():
                if "Avertissement" in line or "Erreur" in line or "Écart" in line:
                    validation_issues.append(line.strip())
    
    elapsed = time.time() - t0
    print(f"  GLB généré     : {glb_size:,} octets ({validation_status}) en {elapsed:.1f}s", flush=True)
    
    # Standardize preview filenames to case_id_front.png etc.
    previews_dir = os.path.join(case_out_dir, "previews")
    renders = {}
    if os.path.exists(previews_dir):
        for rf in os.listdir(previews_dir):
            if rf.endswith(".png"):
                renders[rf] = os.path.join(previews_dir, rf)
                for angle in ["front", "hero", "side", "top"]:
                    if angle in rf and not rf.startswith(f"{case_id}_"):
                        alias_path = os.path.join(previews_dir, f"{case_id}_{angle}.png")
                        if not os.path.exists(alias_path):
                            shutil.copy2(os.path.join(previews_dir, rf), alias_path)
    
    print(f"  Rendus studio  : {len(renders)} vues générées ({', '.join(renders.keys())})", flush=True)
    
    result_entry = {
        "case_id": case_id,
        "filename": fname,
        "sha256": sha256,
        "image_size_bytes": len(img_bytes),
        "image_dimensions": img_dims,
        "image_mode": img_mode,
        "ground_truth_name": tc["ground_truth_name"],
        "ground_truth_category": tc["ground_truth_category"],
        "has_misleading_name": tc["has_misleading_name"],
        "filename_keyword": tc["filename_keyword"],
        "predicted_category": predicted_category,
        "category_confidence": category_confidence,
        "contradiction_detected": contradiction_detected,
        "rejection_reason": rejection_reason,
        "components_count": components_count,
        "components_names": components_names,
        "glb_path": expected_glb,
        "glb_size_bytes": glb_size,
        "glb_created": glb_ok,
        "validation_status": validation_status,
        "validation_issues": validation_issues,
        "elapsed_seconds": round(elapsed, 2),
        "renders": list(renders.keys()),
        "previews_dir": previews_dir,
        "log_path": log_path,
        "human_intervention_needed": False
    }
    campaign_results.append(result_entry)

total_elapsed = time.time() - start_campaign_time
print(f"\n=================================================================", flush=True)
print(f"  CAMPAGNE TERMINÉE en {total_elapsed:.1f}s", flush=True)
print(f"=================================================================", flush=True)

summary_path = os.path.join(CAMPAIGN_OUT_DIR, "campaign_summary.json")
with open(summary_path, "w", encoding="utf-8") as fp:
    json.dump({
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "total_cases": len(campaign_results),
        "total_elapsed_seconds": round(total_elapsed, 2),
        "results": campaign_results
    }, fp, indent=2)

print(f"Résumé sauvegardé dans : {summary_path}", flush=True)
