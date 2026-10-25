import sys
import os
import json

sys.path.append(r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\scripts\3d_pipeline")
from image_analyzer import ReferenceImageAnalyzer
from semantic_classifier import classify_product_semantics

# Test generation of sofa spec from sac_demo.jpg
sofa_img = r"C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode\inputs\product_images\sac_demo.jpg"
ana = ReferenceImageAnalyzer(sofa_img)
ana.segment_foreground()

decision = classify_product_semantics(
    sofa_img,
    ana.mask,
    ana.bbox,
    ana.width,
    ana.height
)

print("Decision for sac_demo.jpg:")
print("  Final category:", decision["final_category"])
print("  Contradiction:", decision["contradiction_detected"])
print("  Visual metrics:", decision["visual_metrics"])
