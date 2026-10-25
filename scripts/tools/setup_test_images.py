import shutil
import os

dest_dir = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images"
os.makedirs(dest_dir, exist_ok=True)

test_files = [
    # 1. Canapé avec nom trompeur "sac_demo.jpg" (déjà présent)
    # 2. Sac avec nom trompeur "sofa_demo.png"
    (os.path.join(dest_dir, "sac_elsi_authentic.png"), os.path.join(dest_dir, "sofa_demo.png")),
    # 3. Lampe de table
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case1_table_lamp_minimalist.png", os.path.join(dest_dir, "lampe_table.png")),
    # 4. Électronique avec nom neutre "produit_neutre_001.png"
    (r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case2_external_ssd_powerbank.png", os.path.join(dest_dir, "produit_neutre_001.png")),
    # 5. Sac authentique avec nom concordant "sac_cuir_luxe.png"
    (os.path.join(dest_dir, "sac_elsi_authentic.png"), os.path.join(dest_dir, "sac_cuir_luxe.png")),
    # 6. Vase avec nom trompeur "sac_porcelaine.png"
    (os.path.join(dest_dir, "accessoire_vase.png"), os.path.join(dest_dir, "sac_porcelaine.png"))
]

for src, dst in test_files:
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"Copied {os.path.basename(src)} -> {os.path.basename(dst)} ({os.path.getsize(dst)} bytes)")
    else:
        print(f"Source not found: {src}")
