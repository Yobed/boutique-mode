import os
import urllib.request
import hashlib
import shutil
from PIL import Image

dest_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\mission37_unseen"
os.makedirs(dest_dir, exist_ok=True)

# Previous development hashes that CANNOT be used
m36_hashes = {
    "fa5cb935c1a0bc14ba4fd6a3a1c336d0787ff22d008028c0e5374ec854fb26dc", # sac_demo.jpg (sofa)
    "74a07bdb8615250462a59394ba3c71888250763749f387a5e3ee5ae828cd6d10", # accessoire_vase.png / sac_porcelaine.png
    "7d0ebfae066a3d9050d276bca9e9e1bb3f9ba87d27e997aeb77ecdf002d4fb63", # sofa_demo.png / sac_cuir_luxe.png
    "d7af0f5a2f15f319eda7891685b1fdc7023b044bfb2e310686d668fcb8f82b47", # lampe_table.png
    "d364270eb83502bd8cea4c7a2b5632a821a4a1c8c90e2c943dba8e00fae3ecab", # produit_neutre_001.png
}

def download_file(url, out_path):
    print(f"Downloading {url} -> {out_path} ...")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    with urllib.request.urlopen(req) as resp, open(out_path, 'wb') as fp:
        fp.write(resp.read())

# 1. Download online items
urls = {
    "bag_kelly.jpg": "https://upload.wikimedia.org/wikipedia/commons/1/13/Kelly_Bag.jpg",
    "shoe_merrell.png": "https://upload.wikimedia.org/wikipedia/commons/b/b4/Merrell_Vapor_Glove_3.png",
    "lamp_desk.jpg": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Blaue_Halogen-Schreibtischlampe_rechts_2022.jpg",
}

for fname, url in urls.items():
    p = os.path.join(dest_dir, fname)
    if not os.path.exists(p):
        download_file(url, p)

# 2. Local items from Blend / Bureau
local_sources = {
    "armchair_lounge.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blender\fauteuil_lounge.png",
    "thermos_vacuum.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case2_vacuum_thermos.png",
    "carafe_scandinavian.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case3_scandinavian_carafe.png",
    "speaker_table.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission29\case3_table_speaker.png",
    "mug_ceramic.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case4_ceramic_tea_mug.png",
    "hammer_mechanic.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case3_mechanic_hammer.png",
    "iron_steam.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case6_steam_iron.png",
    "stool_tripod.png": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission33\case5_tripod_stool.png",
}

for fname, src in local_sources.items():
    dest = os.path.join(dest_dir, fname)
    if os.path.exists(src) and not os.path.exists(dest):
        shutil.copy2(src, dest)
        print(f"Copied {fname} from {src}")

print("Dataset raw files populated.")
