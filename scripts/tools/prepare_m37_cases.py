import os
import hashlib
import shutil
from PIL import Image

unseen_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\mission37_unseen"
test_cases_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\mission37_test_cases"
os.makedirs(test_cases_dir, exist_ok=True)

test_definitions = [
    {
        "case_id": "case01",
        "src_file": "bag_kelly.jpg",
        "test_filename": "case01_sofa_trompeur.jpg",
        "category_expected": "fashion_leather_goods",
        "ground_truth_desc": "Sac à main cuir avec anse/poignée supérieure (nom trompeur: sofa)",
        "features": ["sac à main", "objet avec anse/poignée", "fermoir métallique", "asymétrie 3D"]
    },
    {
        "case_id": "case02",
        "src_file": "shoe_merrell.png",
        "test_filename": "case02_produit_neutre_chaussure.png",
        "category_expected": "footwear_or_organic",
        "ground_truth_desc": "Chaussure de sport / sneaker (forme profil allongée, asymétrie semelle/tige)",
        "features": ["chaussure", "objet asymétrique", "multi-matériaux (mesh/semelle gomme)"]
    },
    {
        "case_id": "case03",
        "src_file": "armchair_lounge.png",
        "test_filename": "case03_sac_trompeur_fauteuil.png",
        "category_expected": "horizontal_lounge_furniture",
        "ground_truth_desc": "Fauteuil lounge contemporain rembourré (nom trompeur: sac)",
        "features": ["canapé ou fauteuil", "assise rembourrée", "dossier incurvé"]
    },
    {
        "case_id": "case04",
        "src_file": "thermos_vacuum.png",
        "test_filename": "case04_bouteille_isotherme.png",
        "category_expected": "cylindrical_container_bottle",
        "ground_truth_desc": "Bouteille thermos isotherme sous vide en acier inoxydable",
        "features": ["bouteille", "corps de révolution cylindrique", "bouchon à vis"]
    },
    {
        "case_id": "case05",
        "src_file": "carafe_scandinavian.png",
        "test_filename": "case05_vase_carafe_verre.png",
        "category_expected": "scandinavian_tableware_lathe",
        "ground_truth_desc": "Vase / carafe scandinave en verre à col rétréci",
        "features": ["vase", "objet de révolution", "col étroit", "base élargie"]
    },
    {
        "case_id": "case06",
        "src_file": "lamp_desk.jpg",
        "test_filename": "case06_sofa_trompeur_lampe.jpg",
        "category_expected": "minimalist_lighting",
        "ground_truth_desc": "Lampe de bureau sur tige et socle (nom trompeur: sofa)",
        "features": ["lampe", "socle circulaire", "tige mince", "tête orientable"]
    },
    {
        "case_id": "case07",
        "src_file": "speaker_table.png",
        "test_filename": "case07_enceinte_acoustique.png",
        "category_expected": "cylindrical_electronics",
        "ground_truth_desc": "Enceinte acoustique de table cylindrique / appareil électronique",
        "features": ["appareil électronique", "cylindre compact", "grille acoustique"]
    },
    {
        "case_id": "case08",
        "src_file": "mug_ceramic.png",
        "test_filename": "case08_tasse_mug_anse.png",
        "category_expected": "tableware_with_handle",
        "ground_truth_desc": "Tasse mug en céramique émaillée avec anse latérale",
        "features": ["objet avec anse ou poignée", "corps cylindrique", "anse latérale cintrée"]
    },
    {
        "case_id": "case09",
        "src_file": "hammer_mechanic.png",
        "test_filename": "case09_marteau_asymetrique.png",
        "category_expected": "asymmetric_tool_handled",
        "ground_truth_desc": "Marteau de mécanicien avec tête acier asymétrique et manche en bois",
        "features": ["objet asymétrique", "manche", "tête métallique", "bi-matériau bois/acier"]
    },
    {
        "case_id": "case10",
        "src_file": "iron_steam.png",
        "test_filename": "case10_fer_vapeur_multimat.png",
        "category_expected": "complex_multimaterial_appliance",
        "ground_truth_desc": "Fer à repasser à vapeur multi-matériaux (semelle inox, réservoir, poignée)",
        "features": ["objet comportant plusieurs matériaux", "poignée fermée", "semelle métallique", "corps asymétrique"]
    },
    {
        "case_id": "case11",
        "src_file": "stool_tripod.png",
        "test_filename": "case11_tabouret_tripode.png",
        "category_expected": "furniture_tripod_seating",
        "ground_truth_desc": "Tabouret tripode scandinave en bois massif (3 pieds inclinés et assise)",
        "features": ["assise / tabouret", "3 pieds cylindriques", "disque d'assise massif"]
    }
]

# Development hashes from M36
m36_hashes = {
    "fa5cb935c1a0bc14ba4fd6a3a1c336d0787ff22d008028c0e5374ec854fb26dc", # sac_demo.jpg (sofa)
    "74a07bdb8615250462a59394ba3c71888250763749f387a5e3ee5ae828cd6d10", # accessoire_vase.png / sac_porcelaine.png
    "7d0ebfae066a3d9050d276bca9e9e1bb3f9ba87d27e997aeb77ecdf002d4fb63", # sofa_demo.png / sac_cuir_luxe.png
    "d7af0f5a2f15f319eda7891685b1fdc7023b044bfb2e310686d668fcb8f82b47", # lampe_table.png
    "d364270eb83502bd8cea4c7a2b5632a821a4a1c8c90e2c943dba8e00fae3ecab", # produit_neutre_001.png
}

seen_shas = set()
print("=== MISSION 37 TESTBED VERIFICATION ===")
for item in test_definitions:
    src_p = os.path.join(unseen_dir, item["src_file"])
    dest_p = os.path.join(test_cases_dir, item["test_filename"])
    shutil.copy2(src_p, dest_p)
    with open(dest_p, "rb") as fp:
        data = fp.read()
        h = hashlib.sha256(data).hexdigest()
    item["sha256"] = h
    item["size_bytes"] = len(data)
    item["path"] = dest_p
    im = Image.open(dest_p)
    item["dimensions"] = f"{im.size[0]}x{im.size[1]}"
    item["mode"] = im.mode
    
    assert h not in m36_hashes, f"FATAL: {item['test_filename']} matches M36 development hash!"
    assert h not in seen_shas, f"FATAL: Duplicate SHA within M37 dataset!"
    seen_shas.add(h)
    
    print(f"[{item['case_id']}] {item['test_filename']:<36} | {item['dimensions']:<9} {item['mode']:<4} | {len(data):>7} B | SHA256: {h[:16]}... | M36: NON (INEDIT)")

print(f"\nAll {len(test_definitions)} cases verified 100% UNSEEN and DISTINCT.")
