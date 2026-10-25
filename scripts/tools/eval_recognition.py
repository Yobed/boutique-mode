"""
eval_recognition.py — Mesure séparée de la reconnaissance et de l'abstention.

Jeu : inputs/product_images/mission37_unseen (libellé = préfixe du nom de fichier,
doublons exacts écartés par SHA-256).

ATTENTION : ces 11 images ont déjà servi à régler les règles de silhouette. Les
chiffres sont indicatifs, pas une mesure de généralisation.
"""

import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(ROOT, "scripts", "3d_pipeline"))

from image_analyzer import ReferenceImageAnalyzer  # noqa: E402
from semantic_classifier import classify_product_semantics  # noqa: E402

DATASET = os.path.join(ROOT, "inputs", "product_images", "mission37_unseen")
GROUND_TRUTH = {
    "armchair_lounge": "armchair", "bag_kelly": "handbag", "carafe_scandinavian": "vase",
    "hammer_mechanic": "hammer", "iron_steam": "iron", "lamp_desk": "lamp",
    "mug_ceramic": "mug", "shoe_merrell": "shoe", "speaker_table": "speaker",
    "stool_tripod": "stool", "thermos_vacuum": "bottle",
}


def list_unique_images():
    seen, items = set(), []
    for name in sorted(os.listdir(DATASET)):
        path = os.path.join(DATASET, name)
        with open(path, "rb") as f:
            digest = hashlib.sha256(f.read()).hexdigest()
        stem = os.path.splitext(name)[0]
        if digest in seen or stem not in GROUND_TRUTH:
            continue
        seen.add(digest)
        items.append((path, GROUND_TRUTH[stem]))
    return items


def main():
    rows = []
    for path, truth in list_unique_images():
        ana = ReferenceImageAnalyzer(path)
        ana.segment_foreground()
        rep = classify_product_semantics(
            path, ana.mask, ana.bbox, ana.width, ana.height, use_recognizer=True)
        rows.append((truth, rep))

    print(f"{'vérité':<10} {'reconnu':<16} {'conf':>5} {'marge':>5}  {'silhouette':<32}")
    for truth, rep in rows:
        r = rep["recognition"]
        shown = r["label"] or f"(abst:{r['best_guess']})"
        print(f"{truth:<10} {shown:<16} {r['confidence']:>5} {r['margin']:>5}  {rep['final_category']:<32}")

    n = len(rows)
    recognized = [(t, r["recognition"]) for t, r in rows if not r["recognition"]["abstained"]]
    correct = sum(1 for t, r in recognized if r["label"] == t)
    wasted = sum(1 for t, r in rows if r["recognition"]["abstained"] and r["recognition"]["best_guess"] == t)
    sil_specific = sum(1 for _, r in rows if r["final_category"] != "generic_spatial_decomposed")

    print(f"\nImages uniques            : {n}")
    print(f"Reconnues (non-abstention): {len(recognized)}/{n}")
    print(f"  dont correctes          : {correct}  (précision {correct / max(1, len(recognized)):.0%})")
    print(f"  dont fausses            : {len(recognized) - correct}")
    print(f"Abstentions               : {n - len(recognized)}  (dont {wasted} où le meilleur candidat était juste)")
    print(f"Rappel global             : {correct}/{n}")
    print(f"Silhouette seule          : {sil_specific}/{n} classées hors générique")


if __name__ == "__main__":
    main()
