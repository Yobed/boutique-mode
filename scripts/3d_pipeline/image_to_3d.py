"""
image_to_3d.py — Transforme les photos produit de la boutique en modèles 3D (GLB) pour le site.

Usage (via scripts/3d_pipeline/run_neural.ps1 ou npm run 3d:*) :
  --image <chemin|URL> --id <id>     une photo vers un modèle
  --article <id>                     la première photo de l'article du catalogue
  --catalog [--categories a,b]       tous les articles du catalogue (sacs, chaussures, accessoires par défaut)
  --approve <id>                     publie un modèle resté « review » après contrôle visuel
  --list                             état du manifeste

Un modèle n'est publié (public/models + config/models3d.json, status "ok") que s'il passe le contrôle
qualité ; sinon il reste dans outputs/3d_neural/<id> avec status "review" et ses raisons.
Une seule photo ne montre pas l'arrière de l'objet : toute sortie est une estimation monoculaire.
"""

import argparse
import datetime
import json
import os
import re
import shutil
import sys
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PIPELINE_DIR)

from catalog import ROOT, read_catalog  # noqa: E402

PUBLIC_MODELS = os.path.join(ROOT, "public", "models")
WORK_ROOT = os.path.join(ROOT, "outputs", "3d_neural")
MANIFEST_PATH = os.path.join(ROOT, "config", "models3d.json")

DEFAULT_CATEGORIES = ("sacs", "chaussures", "accessoires")  # objets : les vêtements portés se détourent mal
MC_RESOLUTION = 192             # grille d'extraction du réseau ; le maillage est ensuite lissé puis décimé à 60 000 faces
QUALITY_FACES = {"web": 60_000, "high": 150_000}  # faces du GLB final (texture 2048 px dans les deux cas)
MIN_IOU = 0.50
DARK_LUMINANCE = 70             # luminance moyenne (0-255) sous laquelle le fond du visualiseur passe en clair
LIGHT_BACKGROUND = "#d9dce1"
MIN_VIEW_IOU = 0.75            # planche multi-vues : silhouette de chaque vue vs enveloppe reconstruite
MIN_MATTE_COVERAGE, MAX_MATTE_COVERAGE = 0.02, 0.92
MAX_WEB_FACES = 250_000
POSTER_SIZE = 768
MAX_DOWNLOAD_BYTES = 25 * 1024 * 1024
DEFAULT_ORBIT = "0deg 75deg 105%"
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def safe_id(raw):
    candidate = re.sub(r"[^a-z0-9_-]+", "-", raw.strip().lower()).strip("-")
    if not ID_PATTERN.match(candidate):
        raise ValueError(f"Identifiant invalide : {raw!r}")
    return candidate


def load_manifest():
    if not os.path.exists(MANIFEST_PATH):
        return {}
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(manifest):
    os.makedirs(os.path.dirname(MANIFEST_PATH), exist_ok=True)
    tmp = MANIFEST_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    os.replace(tmp, MANIFEST_PATH)  # écriture atomique : jamais de manifeste à moitié écrit


def fetch_source(photo, work_dir):
    """Retourne le chemin local de la photo (téléchargée si URL http/https, ou relative à public/)."""
    os.makedirs(work_dir, exist_ok=True)
    if photo.startswith(("http://", "https://")):
        request = urllib.request.Request(photo, headers={"User-Agent": "elsi-3d-pipeline/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            data = response.read(MAX_DOWNLOAD_BYTES + 1)
        if len(data) > MAX_DOWNLOAD_BYTES:
            raise ValueError("Photo trop volumineuse (> 25 Mo).")
        target = os.path.join(work_dir, "source" + (os.path.splitext(urllib.parse.urlparse(photo).path)[1] or ".jpg"))
        with open(target, "wb") as f:
            f.write(data)
        return target
    path = os.path.join(ROOT, "public", photo.lstrip("/")) if photo.startswith("/") else photo
    if not os.path.exists(path):
        raise FileNotFoundError(f"Photo introuvable : {photo}")
    return path


def quality_reasons(report):
    reasons = []
    if not report["watertight"]:
        reasons.append("maillage non étanche")
    if report["silhouette_iou_front"] < MIN_IOU:
        reasons.append(f"IoU de silhouette {report['silhouette_iou_front']} < {MIN_IOU}")
    if not MIN_MATTE_COVERAGE <= report["matte_coverage"] <= MAX_MATTE_COVERAGE:
        reasons.append(f"détourage suspect (couverture {report['matte_coverage']})")
    if report["faces"] > MAX_WEB_FACES:
        reasons.append(f"{report['faces']} faces > {MAX_WEB_FACES} (trop lourd pour le web)")
    if report.get("matte_objects", 1) > 1:
        reasons.append(f"{report['matte_objects']} objets séparés sur la photo : recadrer sur un seul produit")
    view_ious = report.get("view_ious")
    if view_ious and min(view_ious.values()) < MIN_VIEW_IOU:
        worst = min(view_ious, key=view_ious.get)
        reasons.append(f"vues incohérentes : « {worst} » IoU {view_ious[worst]} < {MIN_VIEW_IOU}")
    return reasons


def make_poster(cutout_path, target):
    with Image.open(cutout_path) as img:
        img = img.convert("RGBA")
        img.thumbnail((POSTER_SIZE, POSTER_SIZE), Image.LANCZOS)
        img.save(target, optimize=True)


def deploy(model_id, work_dir):
    os.makedirs(PUBLIC_MODELS, exist_ok=True)
    shutil.copyfile(os.path.join(work_dir, "mesh.glb"), os.path.join(PUBLIC_MODELS, f"{model_id}.glb"))
    make_poster(os.path.join(work_dir, "cutout.png"), os.path.join(PUBLIC_MODELS, f"{model_id}-poster.png"))


def unpublish(model_id):
    for name in (f"{model_id}.glb", f"{model_id}-poster.png"):
        path = os.path.join(PUBLIC_MODELS, name)
        if os.path.exists(path):
            os.remove(path)


def pick_background(work_dir):
    """Fond clair pour un produit sombre (un sac noir est invisible sur le fond quasi noir du visualiseur)."""
    with Image.open(os.path.join(work_dir, "cutout.png")) as img:
        rgba = np.asarray(img.convert("RGBA"), dtype=np.float32)
    inside = rgba[..., 3] > 127
    if not inside.any():
        return None
    luminance = (0.299 * rgba[..., 0] + 0.587 * rgba[..., 1] + 0.114 * rgba[..., 2])[inside].mean()
    return LIGHT_BACKGROUND if luminance < DARK_LUMINANCE else None


def manifest_entry(model_id, report, reasons, source, background=None):
    entry = _manifest_entry(model_id, report, reasons, source)
    if background:
        entry["background"] = background
    return entry


def _manifest_entry(model_id, report, reasons, source):
    return {
        "src": f"/models/{model_id}.glb",
        "poster": f"/models/{model_id}-poster.png",
        "cameraOrbit": DEFAULT_ORBIT,
        "recolor": False,  # le modèle porte déjà les couleurs de la photo
        "status": "review" if reasons else "ok",
        "reasons": reasons,
        "backend": report["backend"],
        "source_image": source,
        "silhouette_iou": report["silhouette_iou_front"],
        "faces": report["faces"],
        "monocular_estimate": report.get("monocular_estimate", True),  # False : plusieurs vues
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
    }


def process_image(photo, model_id, backend="auto", quality="web", source_label=None):
    """Photo (chemin ou URL) -> modèle ; publie si le contrôle qualité passe. Retourne l'entrée du manifeste."""
    import neural_reconstruct as nr

    model_id = safe_id(model_id)
    work_dir = os.path.join(WORK_ROOT, model_id)
    source = fetch_source(photo, work_dir)
    report = nr.reconstruct(source, work_dir, mc_resolution=MC_RESOLUTION, backend=backend,
                            target_faces=QUALITY_FACES[quality])
    reasons = quality_reasons(report)
    entry = manifest_entry(model_id, report, reasons, source_label or photo, pick_background(work_dir))
    if reasons:
        unpublish(model_id)  # un modèle repassé en « review » ne doit pas rester en ligne
    else:
        deploy(model_id, work_dir)
    manifest = load_manifest()
    manifest[model_id] = entry
    save_manifest(manifest)
    return entry


def _load_sheet_layout(sheet, layout_path):
    """Disposition explicite (--layout, ou <planche>.layout.json à côté de la planche) ; {} = détection automatique."""
    layout_path = layout_path or os.path.splitext(sheet)[0] + ".layout.json"
    if not os.path.exists(layout_path):
        return None, {}
    with open(layout_path, encoding="utf-8") as f:
        return layout_path, json.load(f)


def _crop_panel(sheet, layout, work_dir):
    """Mode « single » : un seul panneau de la planche, agrandi, sert de photo unique (TripoSR)."""
    x0, y0, x1, y1 = layout["panel"]
    scale = int(layout.get("upscale", 1))
    with Image.open(sheet) as img:
        crop = img.convert("RGB").crop((x0, y0, x1, y1))
        crop = crop.resize((crop.width * scale, crop.height * scale), Image.LANCZOS)
    path = os.path.join(work_dir, "panel.png")
    crop.save(path)
    return path


def process_sheet(sheet, model_id, quality="web", layout_path=None):
    """Planche multi-vues (face, dos, côtés, dessus, dessous...) -> modèle fidèle ; même publication que process_image.

    Disposition JSON : {"boxes": {vue: [x0,y0,x1,y1]}, "ignore": [vues]} (enveloppe visuelle) ou
    {"mode": "single", "panel": [x0,y0,x1,y1], "upscale": n} (un panneau -> reconstruction à une photo)."""
    import multiview

    model_id = safe_id(model_id)
    work_dir = os.path.join(WORK_ROOT, model_id)
    os.makedirs(work_dir, exist_ok=True)
    source = os.path.relpath(sheet, ROOT) if os.path.isabs(sheet) else sheet
    layout_path, layout = _load_sheet_layout(sheet, layout_path)
    if layout.get("mode") == "single":
        return process_image(_crop_panel(sheet, layout, work_dir), model_id, "triposr", quality, source_label=source)
    boxes = multiview.load_layout(layout_path) if layout_path else None
    report = multiview.reconstruct_sheet(sheet, work_dir, target_faces=QUALITY_FACES[quality], boxes=boxes)
    reasons = quality_reasons(report)
    entry = manifest_entry(model_id, report, reasons, source, pick_background(work_dir))
    if reasons:
        unpublish(model_id)
    else:
        deploy(model_id, work_dir)
    manifest = load_manifest()
    manifest[model_id] = entry
    save_manifest(manifest)
    return entry


def set_flag(model_id, key, value):
    """Ajoute un drapeau à une entrée du manifeste (ex. override : prioritaire sur le modèle défini dans les données)."""
    model_id = safe_id(model_id)
    manifest = load_manifest()
    manifest[model_id][key] = value
    save_manifest(manifest)
    return manifest[model_id]


def approve(model_id):
    model_id = safe_id(model_id)
    manifest = load_manifest()
    if model_id not in manifest:
        raise KeyError(f"{model_id} absent du manifeste")
    deploy(model_id, os.path.join(WORK_ROOT, model_id))
    manifest[model_id]["status"] = "ok"
    manifest[model_id]["reasons"] = []
    save_manifest(manifest)


def select_articles(articles, categories, only_id=None, force=False, limit=None):
    manifest = load_manifest()
    chosen = []
    for article in articles:
        if only_id and article["id"] != only_id:
            continue
        if not only_id and article["categorie"] not in categories:
            continue
        if not article["photos"]:
            continue
        if not (only_id or force) and article.get("has_model"):
            continue
        if not (only_id or force) and manifest.get(safe_id(article["id"]), {}).get("status") == "ok":
            continue
        chosen.append(article)
    return chosen[:limit] if limit else chosen


def run_batch(articles, backend, quality):
    failures = 0
    for index, article in enumerate(articles, 1):
        label = f"[{index}/{len(articles)}] {article['id']} ({article['categorie']})"
        try:
            entry = process_image(article["photos"][0], article["id"], backend, quality)
            print(f"{label} -> {entry['status']} IoU={entry['silhouette_iou']} faces={entry['faces']} {entry['reasons']}", flush=True)
        except Exception as exc:  # un article en échec ne doit pas arrêter le lot
            failures += 1
            print(f"{label} -> ERREUR {type(exc).__name__}: {exc}", flush=True)
    return failures


def parse_args(argv):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--image")
    parser.add_argument("--sheet", help="planche multi-vues (4 + 4 + 5 panneaux : face, dos, côtés, dessus, dessous...)")
    parser.add_argument("--layout", help="disposition JSON de la planche (défaut : <planche>.layout.json si présent)")
    parser.add_argument("--override", action="store_true",
                        help="le modèle remplace celui déjà défini sur l'article dans les données du site")
    parser.add_argument("--id")
    parser.add_argument("--article")
    parser.add_argument("--catalog", action="store_true")
    parser.add_argument("--categories", default=",".join(DEFAULT_CATEGORIES))
    parser.add_argument("--force", action="store_true", help="regénère même les modèles déjà publiés")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--backend", choices=("auto", "triposr", "revolve"), default="auto")
    parser.add_argument("--quality", choices=("web", "high"), default="web")
    parser.add_argument("--approve")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="exécute les tests unitaires du pipeline")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.self_test:
        import unittest
        suite = unittest.defaultTestLoader.discover(os.path.join(PIPELINE_DIR, "tests"))
        return 0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1
    if args.list:
        for model_id, e in sorted(load_manifest().items()):
            print(f"{model_id:24} {e['status']:7} {e['backend']:8} IoU={e['silhouette_iou']} faces={e['faces']} {e['reasons']}")
        return 0
    if args.approve:
        approve(args.approve)
        print(f"{args.approve} publié.")
        return 0
    if args.sheet:
        if not args.id:
            sys.exit("--sheet exige --id")
        entry = process_sheet(args.sheet, args.id, args.quality, args.layout)
        if args.override:
            entry = set_flag(args.id, "override", True)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        return 0 if entry["status"] == "ok" else 2
    if args.image:
        if not args.id:
            sys.exit("--image exige --id")
        entry = process_image(args.image, args.id, args.backend, args.quality)
        print(json.dumps(entry, indent=2, ensure_ascii=False))
        return 0 if entry["status"] == "ok" else 2
    if args.article or args.catalog:
        articles, source = read_catalog()
        categories = {c.strip() for c in args.categories.split(",") if c.strip()}
        todo = select_articles(articles, categories, args.article, args.force, args.limit)
        print(f"Catalogue ({source}) : {len(articles)} articles, {len(todo)} à modéliser.")
        return 1 if run_batch(todo, args.backend, args.quality) else 0
    sys.exit("Rien à faire : voir --help")


if __name__ == "__main__":
    sys.exit(main())
