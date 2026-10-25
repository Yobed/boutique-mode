# Image → 3D neuronal : transformer les photos du site en modèles 3D

Ce pipeline génère un modèle GLB à partir d'**une photo produit** (celles du catalogue, ou n'importe quelle image),
le publie dans `public/models/` et l'attache à l'article : la fiche produit affiche alors l'onglet « Vue 3D 360° ».
Il complète le pipeline Blender procédural ([guide](IMAGE_TO_3D_FASHION_GUIDE.md)), limité à quelques gabarits,
par un moteur qui sait reconstruire **n'importe quel objet** (sac, chaussure, bijou, lunettes, flacon…).

> **Limite à connaître.** Une seule photo ne montre ni l'arrière, ni l'épaisseur, ni l'intérieur de l'objet :
> le modèle les **estime**. Vu de face (comme la photo) le résultat colle ; sous d'autres angles c'est une
> approximation plausible, pas une copie. Pour une fidélité totale il faut plusieurs vues ou un scan.

## Utilisation

| Commande | Effet |
| :-- | :-- |
| `npm run 3d:setup` | Une fois : installe les paquets Python et télécharge ~1,9 Go de poids (hors dépôt). |
| `npm run 3d:catalog` | Modélise tous les sacs, chaussures et accessoires du catalogue pas encore publiés. |
| `npm run 3d:product -- --article art-103` | Un article du catalogue (première photo). |
| `npm run 3d:product -- --image chemin/ou/URL.jpg --id mon-sac` | Une photo quelconque. |
| `npm run 3d:product -- --list` | État du manifeste (ok / review, IoU, faces). |
| `npm run 3d:product -- --approve art-103` | Publie un modèle resté « review » après contrôle visuel. |
| `npm run 3d:test` | Tests unitaires du pipeline. |

Options : `--categories sacs,chaussures`, `--limit N`, `--force` (regénère), `--quality web|high` (60 000 ou
150 000 faces ; texture 2048 px dans les deux cas), `--backend auto|triposr|revolve`. Durée : ~2,5 min par photo sur CPU.

Après génération : `npm run build` — les modèles `ok` sont fusionnés aux articles par `lib/supabase.ts`
(`getArticles` / `getArticleById`), donc la boutique reste statique (Netlify).

## Planche multi-vues : le mode fidèle

Avec **plusieurs vues du même objet** la forme n'est plus devinée mais reconstruite.

```
npm run 3d:product -- --sheet inputs/multiview/ma_planche.png --id mon-sac
```

La planche attendue (voir `inputs/multiview/targus_backpack_sheet.png`) : **4 + 4 + 5 panneaux** sur fond clair, objets
sombres ou colorés, étiquettes libres. Rangée 1 : face, dos, côté gauche, côté droit. Rangée 2 : dessus, dessous,
perspective avant, perspective arrière. Rangée 3 : détails (ignorés). Convention : « côté gauche » = caméra à gauche de
la face (la face avant est à droite de l'image), « dessus » = dos de l'objet en haut de l'image. Les vues doivent être
cadrées pareil (même objet, même échelle approximative, quasi orthographiques).

Principe (`multiview.py`) : découpe des panneaux → détourage → **enveloppe visuelle** (un point de l'espace est gardé
s'il tombe dans la silhouette de chaque vue ; silhouettes lissées en champ continu pour éviter les marches d'escalier)
→ surface lissée, décimée, dépliée → texture cuite depuis les vraies photos (chaque zone prend la vue qui la regarde le
mieux). L'orientation du dessous est retrouvée par recherche. Contrôle qualité : IoU de chaque vue ≥ 0,75.

Ce que ça apporte : relief réel (poche avant, sangles décollées du dos, poignée, patins), côtés et dessous **photographiés**
au lieu d'inventés. Limites : l'enveloppe ne creuse pas ce qui est invisible en silhouette (intérieur d'une poche, relief
d'une fermeture vue de face) ; ces détails sont rendus par la texture, pas par la géométrie.

Les produits sombres reçoivent automatiquement un fond de visualiseur clair (`background` du manifeste).

### Planches de mise en page libre : fichier de disposition

Les planches « marketing » (fond clair, objets clairs, vues sur une seule rangée, paires de chaussures…) ne suivent pas la
grille 4 + 4 + 5. Placez à côté de la planche un fichier `<planche>.layout.json` (lu automatiquement, ou `--layout`) :

```json
{ "boxes": { "front": [8,80,266,382], "back": [...], "left": [...], "right": [...], "top": [...], "bottom": [...] },
  "ignore": ["top"] }
```
- `boxes` : rectangle de chaque vue en pixels de la planche. `ignore` : vues peu fiables, retirées de la reconstruction
  (ex. dessus en perspective d'un sac ouvert : son contour creuse l'enveloppe).
- Alternative `{"mode": "single", "panel": [x0,y0,x1,y1], "upscale": 3}` : un seul panneau devient la photo d'une
  reconstruction à une photo (TripoSR). À préférer quand les vues sont des paires ou des perspectives incohérentes
  (escarpins : l'enveloppe donnait un talon en bloc, TripoSR sur le profil donne une aiguille fine).
- Exemples : `inputs/multiview/*.layout.json`.

`--override` : le modèle généré remplace celui déjà défini sur l'article dans `lib/mock-data.ts` (clé `override` du
manifeste ; sans elle, le modèle défini sur l'article reste prioritaire). Les planches sont aussi ajoutées comme photo
supplémentaire de galerie (`public/images/planches/<article>-planche.jpg`, `photos` de l'article).

Les vues d'une planche générée par IA ne sont pas géométriquement cohérentes (perspective, échelles) : si l'IoU d'une vue
tombe sous 0,75, le modèle reste en « review ».

## Flux (une seule photo)

```
photo (catalogue / URL)
  → détourage U²-Net (ONNX)                      outputs/3d_neural/<id>/cutout.png
  → moteur : révolution si la silhouette l'est, sinon TripoSR
  → nettoyage (fragments flottants, trous) puis FINITION : lissage de Taubin, décimation à ~60 000 faces,
    dépliage UV (xatlas), texture 2048 px cuite depuis la photo (faces cachées remplies par la moyenne
    des couleurs voisines bien vues), matériau PBR mat, normales lisses
  → contrôle qualité  ── ok ──► public/models/<id>.glb + <id>-poster.png + config/models3d.json (status ok)
                      └─ review ► reste dans outputs/3d_neural/<id>, raisons dans le manifeste
```

**Moteurs.** `triposr` : réseau image→triplan (TripoSR, MIT), CPU ~60-120 s par image. `revolve` : vases, carafes, pots
(silhouette axisymétrique détectée par `semantic_classifier`), profil lu sur la silhouette puis tourné autour de
l'axe vertical — TripoSR rend ces objets en lame plate quand ils sont peu texturés.

**Contrôle qualité** (`image_to_3d.quality_reasons`) — un modèle n'est publié que si : maillage étanche ;
IoU de silhouette ≥ 0,50 (reprojection du maillage depuis la caméra de TripoSR vs image détourée) ; détourage plausible
(2-92 % de l'image) ; ≤ 250 000 faces. L'IoU mesure la cohérence avec la photo fournie, **pas** la justesse des faces cachées.

**Couleurs.** Le modèle porte les couleurs de la photo : le visualiseur ne le recolore pas (`recolor: false`,
sélecteur de teintes masqué). Les teintes Noir/Bordeaux/Cognac ne concernent que le sac `sac-elsi.glb` d'origine.

## Quels articles ?

Par défaut : `sacs`, `chaussures`, `accessoires`. Les vêtements portés sur mannequin se détourent mal (le
mannequin est découpé avec) : à éviter sauf photo packshot sur fond uni (`--categories robes` pour forcer).
Bonnes photos : objet entier, fond simple, éclairage doux, vue de face ou trois-quarts, pas de main ni de mannequin.

## Fichiers

| Fichier | Rôle |
| :-- | :-- |
| `scripts/3d_pipeline/image_to_3d.py` | Orchestrateur CLI, contrôle qualité, publication, manifeste. |
| `scripts/3d_pipeline/neural_reconstruct.py` | Détourage, TripoSR, nettoyage, projection des couleurs, IoU. |
| `scripts/3d_pipeline/multiview.py` | Planche multi-vues : découpe, enveloppe visuelle, texture multi-vues. |
| `scripts/3d_pipeline/finish_mesh.py` | Finition : lissage, décimation, dépliage UV, cuisson de la texture. |
| `scripts/3d_pipeline/revolve_solid.py` | Solide de révolution depuis une silhouette. |
| `scripts/3d_pipeline/catalog.py` | Lecture du catalogue (Supabase si configuré, sinon `lib/mock-data.ts`). |
| `scripts/3d_pipeline/setup_neural.py` | Téléchargement des poids avec reprise et vérification de taille. |
| `scripts/3d_pipeline/run_neural.ps1` | Lanceur : trouve un Python équipé, force le mode hors ligne. |
| `scripts/3d_pipeline/vendor/TripoSR/` | Moteur TripoSR embarqué et patché (voir `PATCHES.md`). |
| `scripts/3d_pipeline/tests/` | Tests unitaires (aucun poids ni réseau requis). |
| `scripts/tools/eval_fidelity.py`, `eval_recognition.py` | Bancs d'essai (jeu de 11 objets). |
| `config/models3d.json` | Manifeste id d'article → modèle, statut, métriques. |
| `lib/models3d.ts` | Fusion du manifeste dans les articles (testée par `npm test`). |

Les poids vivent dans `%LOCALAPPDATA%\elsi-3d-models` (variable `ELSI_3D_MODELS` pour changer) : ne pas les mettre dans
OneDrive. Espace requis : ~2,5 Go libres au premier lancement.

## Dépannage

- **Téléchargement Hugging Face bloqué à 0 octet** : le client « xet » se fige sur certaines machines Windows.
  `setup_neural.py` télécharge par HTTP direct avec reprise ; relancez-le simplement.
- **`MemoryError` / plantage pendant le chargement** : la mémoire virtuelle de Windows est saturée (navigateurs,
  serveurs MCP en double). Fermez des applications ; le lot réessaie chaque image une fois. Les poids sont chargés
  en `mmap` pour limiter le pic (~2,5 Go).
- **Disque presque plein** : le fichier d'échange Windows grossit sous pression mémoire ; gardez ≥ 3 Go libres.
- **`Aucun Python avec les paquets requis`** : `npm run 3d:setup`, ou `ELSI_PYTHON=<chemin python>`.
- **Modèle en `review`** : regardez `outputs/3d_neural/<id>/input.png` (ce que le modèle a reçu) et `mesh.glb`
  (par exemple dans le visualiseur du site), puis `--approve <id>` ; sinon changez de photo ou de `--backend`.
- **Le site n'affiche rien** : `npm run build` après génération ; l'article doit avoir `status: ok` dans le manifeste
  et ne pas définir déjà un `modele_3d` (celui de l'article est prioritaire).

## Licences

TripoSR (Stability AI / Tripo, MIT), U²-Net (Apache-2.0), DINO ViT-B/16 (config embarquée, Apache-2.0). Voir
`scripts/3d_pipeline/vendor/TripoSR/LICENSE`. Vérifiez les droits d'usage des photos sources (Unsplash : licence Unsplash).
