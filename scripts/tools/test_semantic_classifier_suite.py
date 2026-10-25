import os
import sys

sys.path.append(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline")
from image_analyzer import ReferenceImageAnalyzer
from semantic_classifier import classify_product_semantics

test_suite = [
    {
        "id": "T1_MISLEADING_SOFA_AS_SAC",
        "description": "Canapé contemporain avec nom trompeur 'sac_demo.jpg'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_demo.jpg",
        "category_hint": None,
        "expected_final": "horizontal_lounge_furniture",
        "expected_contradiction": True
    },
    {
        "id": "T2_MISLEADING_BAG_AS_SOFA",
        "description": "Sac de luxe avec nom trompeur 'sofa_demo.png'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sofa_demo.png",
        "category_hint": None,
        # Silhouette ambiguë : la catégorie générique est le résultat attendu.
        "expected_final": "generic_spatial_decomposed",
        "expected_contradiction": False
    },
    {
        "id": "T3_CONCORDANT_VASE",
        "description": "Vase en céramique avec nom concordant 'accessoire_vase.png'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\accessoire_vase.png",
        "category_hint": None,
        "expected_final": "tableware_lathe",
        "expected_contradiction": False
    },
    {
        "id": "T4_MISLEADING_VASE_AS_SAC",
        "description": "Vase en céramique avec nom trompeur 'sac_porcelaine.png'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_porcelaine.png",
        "category_hint": None,
        "expected_final": "tableware_lathe",
        "expected_contradiction": True
    },
    {
        "id": "T5_CONCORDANT_LAMP",
        "description": "Lampe de table avec nom concordant 'lampe_table.png'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\lampe_table.png",
        "category_hint": None,
        "expected_final": "slender_pedestal_lamp",
        "expected_contradiction": False
    },
    {
        "id": "T6_NEUTRAL_ELECTRONICS",
        "description": "SSD externe avec nom neutre 'produit_neutre_001.png'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\produit_neutre_001.png",
        "category_hint": None,
        "expected_final": "prismatic_enclosure_electronics",
        "expected_contradiction": False
    },
    {
        "id": "T7_CONCORDANT_BAG",
        "description": "Sac authentique avec nom concordant 'sac_cuir_luxe.png'",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_cuir_luxe.png",
        "category_hint": None,
        # Le masque de cette image est identique à sofa_demo.png ; sans
        # modèle sémantique, les deux doivent produire le même repli neutre.
        "expected_final": "generic_spatial_decomposed",
        "expected_contradiction": False
    },
    {
        "id": "T8_USER_FORCE_CONTRADICTORY",
        "description": "Canapé forcé manuellement avec --category sac --force",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_demo.jpg",
        "category_hint": "sac",
        "force_override": True,
        "expected_final": "fashion_handbag",
        "expected_contradiction": True
    }
]

# Régressions image-first sur les 11 images inédites de la Mission 37.
# Les catégories absentes des archétypes pris en charge doivent rester
# génériques, au lieu d'être transformées en sac ou en lampe par une seule
# cavité ou un simple rapport de forme.
mission37_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\mission37_test_cases"
test_suite.extend([
    {"id": "M37_CASE01_KELLY_BAG", "description": "Sac avec nom de fichier trompeur", "path": os.path.join(mission37_dir, "case01_sofa_trompeur.jpg"), "expected_final": "fashion_handbag", "expected_contradiction": True},
    {"id": "M37_CASE02_SHOE_ABSTAIN", "description": "Chaussure hors archétypes", "path": os.path.join(mission37_dir, "case02_produit_neutre_chaussure.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE03_LOUNGE_ABSTAIN", "description": "Fauteuil hors archétypes", "path": os.path.join(mission37_dir, "case03_sac_trompeur_fauteuil.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE04_BOTTLE_ABSTAIN", "description": "Bouteille sans confusion avec lampe", "path": os.path.join(mission37_dir, "case04_bouteille_isotherme.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE05_VASE", "description": "Vase axisymétrique", "path": os.path.join(mission37_dir, "case05_vase_carafe_verre.png"), "expected_final": "tableware_lathe", "expected_contradiction": False},
    {"id": "M37_CASE06_LAMP", "description": "Lampe ajourée", "path": os.path.join(mission37_dir, "case06_sofa_trompeur_lampe.jpg"), "expected_final": "slender_pedestal_lamp", "expected_contradiction": True},
    {"id": "M37_CASE07_SPEAKER_ABSTAIN", "description": "Enceinte hors archétypes", "path": os.path.join(mission37_dir, "case07_enceinte_acoustique.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE08_MUG_ABSTAIN", "description": "Tasse à anse sans confusion avec sac", "path": os.path.join(mission37_dir, "case08_tasse_mug_anse.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE09_HAMMER_ABSTAIN", "description": "Marteau sans confusion avec lampe", "path": os.path.join(mission37_dir, "case09_marteau_asymetrique.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE10_IRON_ABSTAIN", "description": "Fer à vapeur hors archétypes", "path": os.path.join(mission37_dir, "case10_fer_vapeur_multimat.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
    {"id": "M37_CASE11_STOOL_ABSTAIN", "description": "Tabouret tripode sans confusion avec sac", "path": os.path.join(mission37_dir, "case11_tabouret_tripode.png"), "expected_final": "generic_spatial_decomposed", "expected_contradiction": False},
])

print("================================================================================")
print("  EXÉCUTION DU BANC DE TEST ANTI-CONTAMINATION SÉMANTIQUE (MISSION 36)")
print("================================================================================")

results = []
all_passed = True

for case in test_suite:
    p = case["path"]
    analyzer = ReferenceImageAnalyzer(p)
    analyzer.segment_foreground()
    
    rep = classify_product_semantics(
        image_path=p,
        mask=analyzer.mask,
        bbox=analyzer.bbox,
        width=analyzer.width,
        height=analyzer.height,
        category_hint=case.get("category_hint"),
        force_override=case.get("force_override", False)
    )
    
    passed_cat = (rep["final_category"] == case["expected_final"])
    passed_contra = (rep["contradiction_detected"] == case["expected_contradiction"])
    case_success = passed_cat and passed_contra
    
    if not case_success:
        all_passed = False
        
    print(f"\n--- [{case['id']}] {case['description']} ---")
    print(f"  Fichier          : {os.path.basename(p)}")
    print(f"  Indice fichier   : {rep['extracted_filename_hint']}")
    print(f"  Indice utilisateur : {rep['user_metadata_hint']}")
    print(f"  Catégorie visuelle : {rep['visual_category']} (conf: {rep['visual_confidence']})")
    print(f"  Contradiction    : {rep['contradiction_detected']} (Attendu: {case['expected_contradiction']})")
    if rep["contradiction_details"]:
        print(f"  Détail rejet     : {rep['contradiction_details'][:120]}...")
    print(f"  Catégorie finale : {rep['final_category']} (Attendu: {case['expected_final']}) -> {'SUCCÈS' if case_success else 'ÉCHEC'}")
    
    results.append({
        "case": case,
        "report": rep,
        "success": case_success
    })

print("\n================================================================================")
print(f"RÉSULTAT GLOBAL DU BANC D'ESSAI : {'TOUS LES TESTS ONT RÉUSSI' if all_passed else 'DES ÉCHECS ONT ÉTÉ DÉTECTÉS'}")
print("================================================================================")
