# AUDIT COMPLÉMENTAIRE — COHÉRENCE DES RÉFÉRENCES MISSION 35

**Date :** 24 Octobre 2026  
**Projet audité :** `C:\Users\WILFRIED\OneDrive - Gravel Ivoire\Bureau\boutique-mode`  
**Contexte :** Contrôle d'intégrité et de cohérence entre l'image source 2D, les modèles 3D générés et les planches de rendu  
**Auteur :** Antigravity 3D Pipeline Senior Systems Architect  
**Statut de l'Audit :** **RÉSULTAT DÉMONTRÉ — INCOHÉRENCE DE RÉFÉRENCE PRODUIT IDENTIFIÉE**

---

## 1. Contexte et Motif de l'Audit

Au cours de la Mission 35, un modèle 3D orienté maroquinerie (`sac_demo.glb`, 55.7 Ko) a été produit à partir de `inputs/product_images/sac_demo.jpg`, et comparé au modèle brut de la Mission 34 (`sac_demo.glb`, 42.0 Ko). Un score de fidélité visuelle de **8.6 / 10** avait été attribué sous l'hypothèse que l'image représentait un sac à main en cuir beige avec anse et fermoir laiton.

Le présent audit a pour objectif de vérifier formellement la cohérence de cette chaîne de référence :
- Quelle est la véritable nature de l'objet visible dans `sac_demo.jpg` ?
- Quels sont les identifiants et empreintes cryptographiques SHA-256 réels des fichiers ?
- Quelles images et spécifications ont été effectivement exécutées lors des Missions 34 et 35 ?
- Les métriques rapportées mélangent-elles des données de catégories distinctes (sac, canapé, mobilier, etc.) ?

---

## 2. Action 1 — Identification Visuelle Objective de `sac_demo.jpg`

L'inspection géométrique, colorimétrique et historique du fichier `inputs/product_images/sac_demo.jpg` (16 078 octets, $367 \times 367$ px) établit les faits suivants :

### 2.1 Filiation Cryptographique
Le fichier `sac_demo.jpg` possède l'empreinte SHA-256 :
```
fa5cb935c1a0bc14ba4fd6a3a1c336d0787ff22d008028c0e5374ec854fb26dc
```
Cette empreinte est **rigoureusement identique au bit près** à :
1. `Blend/inputs/reference_images/giro.jpg.jpeg` (introduit en Mission 28 comme image utilisateur inédite).
2. `Blend/inputs/reference_images/mission32/case3_industrial_beacon.jpeg` (réutilisé en Mission 32 sous le nom de "balise industrielle").
3. `Blend/outputs/render_studio/mission28/giro.jpg`.

### 2.2 Analyse Visuelle de l'Objet Réel
Une analyse fine de la silhouette et des niveaux de gris révèle la géométrie effective du produit photographié :
- **Ratio d'aspect :** $H / W = 131\text{ px} / 313\text{ px} = 0.419$ (objet très étiré horizontalement).
- **Structure observée :**
  - Partie supérieure gauche ($Y \in [131:160]$) : Dossier bas ou accoudoir gauche.
  - Partie centrale plane ($Y \in [160:220]$) : Surface d'assise horizontale avec coussins d'ameublement.
  - Partie inférieure droite ($Y \in [220:262]$) : Piétement d'angle et retour bas en méridienne.
- **Nature réelle de l'objet :** L'image représente en réalité un **canapé bas d'angle contemporain / sofa lounge** photographié en légère vue de 3/4 face sur fond blanc neutre.
- **Origine de la confusion :** Lors de l'initialisation du projet `boutique-mode` (commit `aa9c7be` du 24/10/2026 à 10:58), l'image de test `giro.jpg.jpeg` a été copiée et rebaptisée `sac_demo.jpg` pour servir d'échantillon au pipeline de la boutique de mode.

---

## 3. Action 2 — Répertoire des Chemins Exacts, Identifiants et Empreintes SHA-256

| Entité | Chemin Absolu sur Disque | Identifiant Objet | Taille (octets) | Empreinte SHA-256 |
| :--- | :--- | :--- | :---: | :--- |
| **Image Source** | `boutique-mode/inputs/product_images/sac_demo.jpg` | `sac_demo` | 16 078 | `fa5cb935c1a0bc14ba4fd6a3a1c336d0787ff22d008028c0e5374ec854fb26dc` |
| **Modèle GLB M34** | `boutique-mode/public/models/backup_m34/sac_demo.glb` | `sac_demo_spatial_decomposed` | 42 016 | `e4aefd1f9c669422a74bb5bf15396eec062cde26e3a59749ea3c1cb5e4ff06b0` |
| **Modèle GLB M35** | `boutique-mode/public/models/sac_demo.glb` | `sac_demo_spatial_decomposed` | 55 708 | `abd5f1644ff6b2173aa56b4e0b0a16c5ee9ad4f99999c24221918039440b7adc` |
| **Poster M34** | `boutique-mode/public/models/backup_m34/sac_demo-poster.png` | `sac_demo-poster` | 782 304 | `87ce3abde1da220022ffcf5c4601ac96754cc78a9a39439923c875f145506385` |
| **Poster M35** | `boutique-mode/public/models/sac_demo-poster.png` | `sac_demo-poster` | 775 582 | `10a4bf823ebc7b38ffdd02874e505f0822fd69a43ef247d2c9adf3fbf1f26722` |
| **Vase GLB (Contrôle)**| `boutique-mode/public/models/accessoire_vase.glb` | `accessoire_vase_spatial_decomposed` | 71 432 | `03f030bccd1968d3d9d18a530c8480a662779daba04f77e0245504c07e5d94af` |

*(Note historique complémentaire : Le tout premier modèle livré dans le commit `aa9c7be` était `outputs/3d_studio/sac_demo/sac_demo_decomposed.glb` de 88 464 octets, SHA-256 : `ec134dbe43d2caa07046368077d657b22322656816753ae9df437ce1f92006c4`).*

---

## 4. Action 3 — Traçabilité des Exécutions dans les Journaux

### 4.1 Génération Mission 34
- **Commande :** `.\scripts\3d_pipeline\run_fashion_3d.ps1`
- **Fichier image lu :** `inputs/product_images/sac_demo.jpg` (SHA-256 : `fa5cb9...`).
- **Spécification générée :** `config/specs/3d/sac_demo_spec_m34.json`.
- **Moteur d'inférence :** Algorithme générique sans inférence maroquinerie.
- **Résultat :** 3 strates prismatiques issues directement de la découpe horizontale de la silhouette du canapé :
  - `Socle_Inferieur` : $0.023 \times 0.015 \times 0.005\text{ m}$ (aluminium anodisé)
  - `Corps_Principal_Strate_2` : $0.397 \times 0.258 \times 0.192\text{ m}$ (beige)
  - `Chapeau_Superieur` : $0.008 \times 0.010 \times 0.005\text{ m}$ (laque blanche)
- **Fichier GLB produit :** `sac_demo.glb` (42 016 octets, SHA-256 : `e4aefd...`).

### 4.2 Génération Mission 35
- **Commande :** `npm run 3d:model`
- **Fichier image lu :** `inputs/product_images/sac_demo.jpg` (SHA-256 : `fa5cb9...`).
- **Spécification générée :** `config/specs/3d/sac_demo_spec.json`.
- **Moteur d'inférence :** Détection automatique du mot-clé `sac` dans le nom de fichier `sac_demo.jpg`, déclenchant `synthesize_fashion_leather_components()`.
- **Résultat :** Le pipeline a interprété la silhouette du canapé comme un sac à main de maroquinerie sellier :
  - `Corps_Principal_Cuir` : $0.468 \times 0.182 \times 0.136\text{ m}$ (`M_Cuir_Principal`)
  - `Rabat_Superieur_Cuir` : $0.430 \times 0.167 \times 0.056\text{ m}$ (`M_Cuir_Principal`)
  - `Fermoir_Boucle_Laiton` : $0.045 \times 0.008 \times 0.026\text{ m}$ (`brushed_brass_gold`)
  - `Bande_Poignee_Superieure` : $0.311 \times 0.064 \times 0.016\text{ m}$ (`M_Cuir_Principal`)
- **Fichier GLB produit :** `sac_demo.glb` (55 708 octets, SHA-256 : `abd5f1...`).

---

## 5. Action 4 — Authenticité des Rendus et Planche d'Audit Régénérée

Une planche d'audit spécifique a été générée :
- **Fichier :** `outputs/reports/mission35_reference_consistency_board.png`
- **Copie d'artéfact :** `C:\Users\WILFRIED\.gemini\antigravity\brain\a6afba35-f0a6-4827-a7a0-51c2e154eb99\mission35_reference_consistency_board.png`

Elle certifie les points suivants :
1. Les rendus proviennent bien des modèles GLB respectifs générés par Blender 5.2.2.
2. L'image de référence insérée dans la planche est bien `sac_demo.jpg` (SHA-256 : `fa5cb9...`).
3. Elle met en évidence de façon irréfutable le décalage sémantique : la photo montre un canapé bas, tandis que le modèle M35 affiche un sac à main haute maroquinerie.

---

## 6. Action 5 — Diagnostic sur le Mélange des Métriques

L'audit met en évidence une **contamination sémantique induite par le nommage** :
1. **Dimensions métriques injectées :** Les dimensions métriques de M35 ($46.8\text{ cm} \times 18.2\text{ cm} \times 21.6\text{ cm}$) sont des dimensions réalistes pour un grand sac à main ou cabas de voyage. Elles ne correspondent en rien aux dimensions d'un canapé (qui mesure environ $2.00\text{ m} \times 0.90\text{ m} \times 0.85\text{ m}$).
2. **Topologie et composants :** Les composants modélisés (rabat, boucle de fermoir, anse de maintien) sont des attributs purs de maroquinerie, totalement absents de la photo source.
3. **Origine du biais :** L'inférence automatique s'est appuyée sur la présence de la chaîne `"sac"` dans le chemin du fichier (`sac_demo.jpg`) pour forcer une taxonomie maroquinière sur une image de meuble.

---

## 7. Révocation du Score de Fidélité Visuelle

Conformément à la consigne méthodologique stricte :
> **"Ne pas attribuer de score de fidélité avant d'avoir confirmé que la référence et les modèles représentent le même produit."**

### Décision d'Audit :
- Le score de **8.6 / 10** attribué dans le rapport de Mission 35 est **officiellement révoqué**.
- Il est scientifiquement et méthodologiquement invalide de mesurer un score de fidélité entre une **photo de canapé d'angle** et un **modèle 3D de sac à main**, quand bien même le fichier informatique portait le libellé `sac_demo.jpg`.
- Le modèle M35 est techniquement et géométriquement parfait en tant que *sac procédural* (0 défaut BMesh, manifold, PBR Principled BSDF, intégration Next.js fonctionnelle), mais il ne constitue pas une reproduction fidèle de la photo `sac_demo.jpg`.

---

## 8. Recommandations pour la Suite du Projet

1. **Assainissement des données d'entrée (`inputs/product_images/`) :**
   Remplacer `sac_demo.jpg` par une authentique photographie de maroquinerie (ex. une photo réelle du sac Signature ou du sac ELSI de la boutique) avec fond neutre.
2. **Découplage de la détection sémantique :**
   Empêcher que le seul nom de fichier (`sac_*.jpg`) force aveuglément des attributs de sac (anse, rabat, fermoir) si l'image analysée présente un ratio d'aspect ou des caractéristiques incompatibles avec la maroquinerie.
3. **Conservation des actifs actuels :**
   Les modèles et sauvegardes existants (`backup_m34/` et `public/models/`) sont rigoureusement préservés.

---

**Verdict de l'Audit de Cohérence : INCOHÉRENCE DE RÉFÉRENCE PRODUIT DÉMONTRÉE (Photo Canapé vs Modèle Sac — Score de fidélité révoqué)**
