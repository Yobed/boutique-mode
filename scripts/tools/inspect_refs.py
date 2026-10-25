import sys
sys.path.append(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline")
from image_analyzer import ReferenceImageAnalyzer

for p in [
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\videoframe_6041.png",
    r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\Blend\inputs\reference_images\image de reference.jpg"
]:
    ana = ReferenceImageAnalyzer(p)
    ana.segment_foreground()
    min_x, min_y, max_x, max_y = ana.bbox
    bw = max_x - min_x + 1
    bh = max_y - min_y + 1
    print(f"File: {p}")
    print(f"  BBox: {bw}x{bh}, AR: {bh/bw:.3f}, Sym: {ana.symmetry_score:.3f}")
