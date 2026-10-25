# Mise en ligne d’un modèle 3D fidèle (Master Prompt V2.2)

`status: "ok"` indique uniquement que le fichier a passé les contrôles techniques de génération. Il ne prouve pas que le modèle représente l’article réellement vendu.

Un modèle n’est transmis à la boutique que si le manifeste `config/models3d.json` contient une revue distincte avec toutes les conditions suivantes (conforme au [MASTER_PROMPT_V2.2.md](./MASTER_PROMPT_V2.2.md)) :

1. **Intégrité Topologique & Watertight** : 0 arête non-manifold, 0 bordure ouverte, 0 auto-intersection intra-surface (validé par `scripts/3d_pipeline/validator.py`).
2. **Métriques de Reprojection Objectives** :
   - Score de Silhouette Chamfer : $CS \ge 0.85$ (calculé sous pose optimisée coarse-to-fine par `scripts/3d_pipeline/silhouette_score.py`).
   - Recouvrement UV : $\le 2.0\%$ sur grille raster 1024×1024.
3. **Assiette AR 1:1** : Contact sol strict $Z_{min} = 0.000\text{ m} \pm 0.002\text{ m}$, centrage $X=0, Y=0$, dimensions conformes aux priors physiques en mètres.
4. **Budget WebGL Mobile** : Draw calls $\le 6$ (fusion par matériau), poids GLB $\le 3\text{ Mo}$.
5. **Preuves physiques multi-vues** :
   - Prises de vues physiques de l’article (`monocular_estimate: false`) couvrant `front`, `back`, `left`, `right`, `top` et `bottom` (ou les 4 angles studio certifiés pour joaillerie).
   - `fidelity_review.source_type` vaut `physical_product_captures` (ou `product_photo_catalog`) et `fidelity_review.status` vaut `approved`.
   - `glb_sha256` renseigné de façon déterministe sur les octets du fichier GLB publié.
   - `fidelity_review.variant_color` correspond exactement à un coloris de l’article (ou `null` si parure unique).
   - La revue indique `reviewed_at` et `reviewed_by`.
   - `recolor` reste à `false` : une autre teinte ne se déduit pas d’une recoloration synthétique.

Exemple du bloc de revue après audit technique et humain V2.2 :

```json
"fidelity_review": {
  "status": "approved",
  "reviewed_by": "lead-3d-architect",
  "reviewed_at": "2026-10-25T16:35:00+00:00",
  "glb_sha256": "455fee759d64c18f1df49662c66ad19c16d474d8834c99eee387b02ba18672a3",
  "metrics": {
    "draw_calls": 5,
    "is_watertight": true,
    "non_manifold_edges": 0,
    "uv_overlap_pct": 0.0,
    "ar_anchor_z_min_m": 0.0
  },
  "captured_views": ["front", "angle_35", "side_90", "back_180"],
  "source_type": "product_photo_catalog",
  "variant_color": null,
  "note": "Reconstruction Haute Joaillerie 360° V2.2 : 435 perles micro-variations, fermoir mousqueton or 18k, SSS corail et nacre, calage AR 1:1 sol Z_min=0, seed déterministe SHA-256."
}
```

Tant que la revue est absente ou incomplète (`status: "pending"` ou `status: "review"`), la fiche produit Next.js utilise les photographies 2D HD et masque la vue 3D.
