import os
import sys
from PIL import Image

sys.path.append(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline")
from image_analyzer import ReferenceImageAnalyzer

images_to_test = [
    {
        "id": "case_sofa_sac_demo",
        "name": "sac_demo.jpg (Canapé avec nom trompeur 'sac')",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_demo.jpg",
        "filename_hint": "sac",
        "expected_visual": "horizontal_lounge_furniture"
    },
    {
        "id": "case_vase",
        "name": "accessoire_vase.png (Vase authentique)",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\accessoire_vase.png",
        "filename_hint": "vase",
        "expected_visual": "tableware_lathe"
    },
    {
        "id": "case_lamp",
        "name": "case1_table_lamp_minimalist.png (Lampe minimaliste)",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case1_table_lamp_minimalist.png",
        "filename_hint": "lamp",
        "expected_visual": "slender_pedestal_lamp"
    },
    {
        "id": "case_ssd",
        "name": "case2_external_ssd_powerbank.png (SSD boîtier)",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\mission27\case2_external_ssd_powerbank.png",
        "filename_hint": "ssd",
        "expected_visual": "prismatic_enclosure_electronics"
    },
    {
        "id": "case_sac_elsi",
        "name": "sac_elsi_authentic.png (Sac à main de luxe authentique)",
        "path": r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_elsi_authentic.png",
        "filename_hint": "sac",
        "expected_visual": "fashion_handbag"
    }
]

print("=== EXTRACTION DES MÉTRIQUES VISUELLES DU BANC D'ESSAI ===")

for item in images_to_test:
    p = item["path"]
    analyzer = ReferenceImageAnalyzer(p)
    analyzer.segment_foreground()
    analyzer.compute_symmetry()
    
    min_x, min_y, max_x, max_y = analyzer.bbox
    bw = max_x - min_x + 1
    bh = max_y - min_y + 1
    ar = bh / float(bw) # aspect ratio H/W
    sym = analyzer.symmetry_score
    
    fg_area = sum(sum(1 for v in row if v) for row in analyzer.mask)
    fill = fg_area / float(bw * bh)
    
    # Check for slender stem
    mid_widths = []
    for y in range(int(min_y + bh * 0.3), int(min_y + bh * 0.7)):
        xs = [x for x in range(min_x, max_x + 1) if analyzer.mask[y][x]]
        if xs:
            mid_widths.append(max(xs) - min(xs) + 1)
    min_mid_w = min(mid_widths) if mid_widths else bw
    avg_mid_w = sum(mid_widths)/len(mid_widths) if mid_widths else bw
    slender_ratio = avg_mid_w / float(bw)
    
    print(f"\nImage: {item['name']}")
    print(f"  BBox: {bw}x{bh} px | AR (H/W): {ar:.3f} | Symétrie: {sym:.3f} | Fill: {fill:.3f} | MidWidthRatio: {slender_ratio:.3f}")
    im = Image.open(p)
    print(f"  Image Mode: {im.mode}, Size: {im.size}")
    if im.mode == "RGBA":
        alpha = im.split()[-1]
        a_min, a_max = alpha.getextrema()
        print(f"  Alpha Channel range: [{a_min}, {a_max}]")
    center_color = im.getpixel((im.width//2, im.height//2))
    print(f"  Center pixel: {center_color}")
