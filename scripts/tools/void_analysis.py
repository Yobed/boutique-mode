import sys
sys.path.append(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline")
from image_analyzer import ReferenceImageAnalyzer

files = [
    ("accessoire_vase.png", r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\accessoire_vase.png"),
    ("sac_cuir_luxe.png", r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_cuir_luxe.png"),
    ("produit_neutre_001.png", r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\produit_neutre_001.png"),
    ("lampe_table.png", r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\lampe_table.png"),
    ("sac_demo.jpg", r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_demo.jpg")
]

for name, p in files:
    ana = ReferenceImageAnalyzer(p)
    ana.segment_foreground()
    min_x, min_y, max_x, max_y = ana.bbox
    bw = max_x - min_x + 1
    bh = max_y - min_y + 1
    
    # Internal void check: rows that have foreground on left AND right, but background in middle
    void_pixels = 0
    void_rows = 0
    for y in range(min_y, max_y + 1):
        xs = [x for x in range(min_x, max_x + 1) if ana.mask[y][x]]
        if xs:
            min_row_x, max_row_x = min(xs), max(xs)
            span = max_row_x - min_row_x + 1
            solid = len(xs)
            void_in_row = span - solid
            if void_in_row > 10: # Significant hollow / through-hole
                void_pixels += void_in_row
                void_rows += 1
                
    # Constant width check (prismatic extrusion)
    # Check rows between 20% and 80% of height
    mid_widths = []
    for y in range(int(min_y + bh * 0.2), int(min_y + bh * 0.8)):
        xs = [x for x in range(min_x, max_x + 1) if ana.mask[y][x]]
        if xs:
            mid_widths.append(max(xs) - min(xs) + 1)
    if mid_widths:
        mean_w = sum(mid_widths) / len(mid_widths)
        std_w = (sum((w - mean_w)**2 for w in mid_widths) / len(mid_widths))**0.5
        cv_w = std_w / mean_w # Coefficient of variation
    else:
        cv_w = 1.0
        
    print(f"[{name}]")
    print(f"  Void rows: {void_rows}/{bh} ({void_rows/bh*100:.1f}%), Void pixels: {void_pixels}")
    print(f"  Mid-body Width CV: {cv_w:.4f} (lower means more constant/straight)")
