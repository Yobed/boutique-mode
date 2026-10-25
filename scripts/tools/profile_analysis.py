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
    
    # Analyze slice widths from bottom to top
    widths = []
    for y in range(max_y, min_y - 1, -max(1, bh // 30)):
        xs = [x for x in range(min_x, max_x + 1) if ana.mask[y][x]]
        w = max(xs) - min(xs) + 1 if xs else 0
        widths.append(w / float(bw))
        
    w_min = min(widths) if widths else 0
    w_max = max(widths) if widths else 0
    # Straight sides: percentage of slices with width > 0.90 of max
    straight_pct = sum(1 for w in widths if w > 0.90) / float(len(widths))
    # Neck constriction in upper half
    upper_widths = widths[len(widths)//2:]
    neck_ratio = min(upper_widths) if upper_widths else 1.0
    
    print(f"\n[{name}] BBox: {bw}x{bh}, AR: {bh/bw:.3f}")
    print(f"  Widths (sampled 10): {[round(w, 2) for w in widths[::3]]}")
    print(f"  Min/Max: {w_min:.2f} / {w_max:.2f} | Straight sides (>90%): {straight_pct*100:.1f}%")
    print(f"  Neck ratio (min upper): {neck_ratio:.2f}")
