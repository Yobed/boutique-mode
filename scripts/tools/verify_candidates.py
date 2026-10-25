import os, hashlib
from PIL import Image

m36_hashes = {
    "fa5cb935c1a0bc14ba4fd6a3a1c336d0787ff22d008028c0e5374ec854fb26dc", # sac_demo.jpg (sofa)
    "74a07bdb8615250462a59394ba3c71888250763749f387a5e3ee5ae828cd6d10", # accessoire_vase.png / sac_porcelaine.png
    "7d0ebfae066a3d9050d276bca9e9e1bb3f9ba87d27e997aeb77ecdf002d4fb63", # sofa_demo.png / sac_cuir_luxe.png
    "d7af0f5a2f15f319eda7891685b1fdc7023b044bfb2e310686d668fcb8f82b47", # lampe_table.png
    "d364270eb83502bd8cea4c7a2b5632a821a4a1c8c90e2c943dba8e00fae3ecab", # produit_neutre_001.png
}

candidates = [
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case2_vacuum_thermos.png", "bouteille / thermos"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case3_mechanic_hammer.png", "objet asymétrique / marteau"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case4_ceramic_tea_mug.png", "objet avec anse / mug céramique"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case5_tripod_stool.png", "assise / tabouret tripode"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case6_steam_iron.png", "objet multi-matériaux / poignée / fer à repasser"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case3_scandinavian_carafe.png", "bouteille / carafe scandinave"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case4_timer_front.png", "appareil mécanique / minuteur"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission29\case2_nordic_kettle.png", "objet avec anse / bouilloire"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission29\case3_table_speaker.png", "appareil électronique / enceinte"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission32\case2_ceramic_pitcher_handle.png", "vase-pichet avec anse"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blender\fauteuil_lounge.png", "fauteuil / canapé lounge"),
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Ressource Humaine\public\images\biometric_terminal_hero.png", "appareil électronique / terminal"),
]

seen_hashes = set()
for p, desc in candidates:
    if not os.path.exists(p):
        print(f"MISSING: {p}")
        continue
    with open(p, "rb") as fp:
        h = hashlib.sha256(fp.read()).hexdigest()
    im = Image.open(p)
    is_m36 = h in m36_hashes
    is_dup = h in seen_hashes
    seen_hashes.add(h)
    print(f"File: {os.path.basename(p)}")
    print(f"  Desc: {desc}")
    print(f"  Size: {im.size}, Mode: {im.mode}, Bytes: {os.path.getsize(p)}")
    print(f"  SHA256: {h}")
    print(f"  Used in M36: {is_m36} | Duplicate in list: {is_dup}")
    print()
