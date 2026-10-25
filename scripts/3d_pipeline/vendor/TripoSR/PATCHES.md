# TripoSR embarqué — patchs locaux

Source : https://github.com/VAST-AI-Research/TripoSR (MIT, voir `LICENSE`), paquet `tsr/` uniquement.
Poids : `stabilityai/TripoSR` (téléchargés par `scripts/3d_pipeline/setup_neural.py`, jamais dans le dépôt).
À réappliquer si le moteur est mis à jour.

| Fichier | Patch | Raison |
| :-- | :-- | :-- |
| `tsr/models/isosurface.py` | `marching_cubes` via `skimage` ; renvoie les sommets en ordre inversé (axe2, axe1, axe0) | `torchmcubes` exige un compilateur C++ ; l'ordre inversé est celui attendu par le `[2, 1, 0]` qui suit — sans cela le maillage est en **miroir** |
| `tsr/system.py` | `extract_mesh` interroge la grille par blocs de 200 000 points | la grille entière (7 M points × 120 variables) dépasse la mémoire |
| `tsr/system.py` | chargement des poids : device `meta` + `mmap` + `assign=True`, contrôle des tenseurs restés sur `meta` | évite de commettre 2 × 1,7 Go de RAM |
| `tsr/system.py` | `_convert_vit_keys` : renomme `encoder.layer.N.attention.attention.query` → `layers.N.attention.q_proj`, etc., seulement si le modèle instancié n'a pas les noms 4.x | `transformers` ≥ 5 a renommé les couches ViT ; le checkpoint est au format 4.35 |
| `tsr/models/tokenizers/image.py` | config DINO lue depuis `tsr/dino-vitb16-config.json` ; constantes `image_mean/std` forcées sur `cpu` | aucun accès réseau à l'exécution ; ces tampons non persistants restaient sur `meta` |
| `tsr/utils.py` | `import rembg` paresseux dans `remove_background` | `rembg` n'est pas utilisé (détourage U²-Net ONNX dans `neural_reconstruct.py`) |

Repères de repère géométrique : TripoSR sort un maillage Z haut, caméra de conditionnement sur +X, droite = +Y,
distance 1,9, champ vertical 40°. `neural_reconstruct.py` le convertit en glTF (Y haut, +Z vers la caméra, droite = +X).
