import os, sys
sys.path.append(r'scripts/3d_pipeline')
from image_analyzer import ReferenceImageAnalyzer
from component_analyzer import ComponentAnalyzer

test_imgs = [
    'inputs/product_images/mission37_test_cases/case02_produit_neutre_chaussure.png',
    'inputs/product_images/mission37_test_cases/case03_sac_trompeur_fauteuil.png',
    'inputs/product_images/mission37_test_cases/case08_tasse_mug_anse.png',
    'inputs/product_images/mission37_test_cases/case10_fer_vapeur_multimat.png'
]

for p in test_imgs:
    analyzer = ReferenceImageAnalyzer(p)
    analyzer.segment_foreground()
    comp = ComponentAnalyzer(analyzer)
    apps = comp.detect_appendages(0.2, 0.2)
    names = [a['name'] for a in apps]
    print(os.path.basename(p), '->', len(apps), 'appendages:', names)
