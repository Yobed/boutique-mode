"""
setup_neural.py — Installe les poids du moteur image-vers-3D (hors du dépôt, ~1,9 Go).

  python scripts/3d_pipeline/setup_neural.py            télécharge ce qui manque, vérifie les tailles
  python scripts/3d_pipeline/setup_neural.py --check    vérifie seulement (code retour 1 si incomplet)
  python scripts/3d_pipeline/setup_neural.py --install-deps   installe aussi les paquets Python

Les poids vont dans %LOCALAPPDATA%\\elsi-3d-models (ou $ELSI_3D_MODELS). Téléchargement par urllib avec
reprise : le client Hugging Face « xet » reste bloqué à 0 octet sur certaines machines Windows.
"""

import argparse
import os
import shutil
import subprocess
import sys
import urllib.request

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.environ.get("ELSI_3D_MODELS") or os.path.join(
    os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "elsi-3d-models")

HF = "https://huggingface.co/stabilityai/TripoSR/resolve/main"
# nom -> (URL, taille attendue en octets)
FILES = {
    "config.yaml": (f"{HF}/config.yaml", 987),
    "model.ckpt": (f"{HF}/model.ckpt", 1_677_246_742),
    "u2net.onnx": ("https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2net.onnx", 175_997_641),
    # super-résolution des vues sources (planches : panneaux de ~175 px) avant cuisson de la texture
    "RealESRGAN_x4plus.pth": (
        "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth", 67_040_989),
}
CHUNK = 1024 * 1024
MIN_FREE_MARGIN = 500 * 1024 * 1024


def missing_files():
    return [n for n, (_, size) in FILES.items()
            if not os.path.exists(os.path.join(MODELS_DIR, n)) or os.path.getsize(os.path.join(MODELS_DIR, n)) != size]


def download(name, url, expected):
    target = os.path.join(MODELS_DIR, name)
    part = target + ".part"
    done = os.path.getsize(part) if os.path.exists(part) else 0
    request = urllib.request.Request(url, headers={"User-Agent": "elsi-3d-setup/1.0"})
    if done:
        request.add_header("Range", f"bytes={done}-")
    with urllib.request.urlopen(request, timeout=60) as response:
        resumed = response.status == 206
        with open(part, "ab" if resumed else "wb") as f:
            written = done if resumed else 0
            while chunk := response.read(CHUNK):
                f.write(chunk)
                written += len(chunk)
                print(f"\r  {name}: {written / 1e6:8.1f} / {expected / 1e6:.1f} Mo", end="", flush=True)
    print()
    if os.path.getsize(part) != expected:
        raise IOError(f"{name}: taille {os.path.getsize(part)} != attendue {expected} (relancez pour reprendre)")
    os.replace(part, target)


def check_python_packages():
    missing = []
    for module in ("torch", "transformers", "omegaconf", "einops", "trimesh", "skimage", "scipy", "PIL", "onnxruntime",
                   "fast_simplification", "xatlas", "spandrel"):
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    return missing


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--install-deps", action="store_true")
    args = parser.parse_args()

    if args.install_deps:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--no-cache-dir", "-r",
                               os.path.join(PIPELINE_DIR, "requirements-neural.txt")])

    todo = missing_files()
    if todo and not args.check:
        os.makedirs(MODELS_DIR, exist_ok=True)
        need = sum(FILES[n][1] for n in todo)
        free = shutil.disk_usage(MODELS_DIR).free
        if free < need + MIN_FREE_MARGIN:
            sys.exit(f"Espace disque insuffisant : {free / 1e9:.2f} Go libres, {(need + MIN_FREE_MARGIN) / 1e9:.2f} Go requis.")
        for name in todo:
            download(name, *FILES[name])
        todo = missing_files()

    packages = check_python_packages()
    print(f"Poids dans {MODELS_DIR} : {'complets' if not todo else 'MANQUANTS ' + ', '.join(todo)}")
    print(f"Paquets Python : {'complets' if not packages else 'MANQUANTS ' + ', '.join(packages)}"
          + ("  (relancez avec --install-deps)" if packages else ""))
    sys.exit(0 if not todo and not packages else 1)


if __name__ == "__main__":
    main()
