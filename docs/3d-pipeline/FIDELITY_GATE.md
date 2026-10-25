# Mise en ligne d’un modèle 3D fidèle

`status: "ok"` indique uniquement que le fichier a passé les contrôles techniques de génération. Il ne prouve pas que le modèle représente l’article réellement vendu.

Un modèle n’est transmis à la boutique que si le manifeste `config/models3d.json` contient une revue distincte avec toutes les conditions suivantes :

- le modèle a été construit à partir de prises de vues physiques de l’article (`monocular_estimate: false`) ;
- les captures couvrent les vues `front`, `back`, `left`, `right`, `top` et `bottom` du même article et du même coloris ;
- `fidelity_review.source_type` vaut `physical_product_captures` et `fidelity_review.status` vaut `approved` ;
- `fidelity_review.variant_color` correspond exactement à un coloris de l’article ;
- la revue indique `reviewed_at` et `reviewed_by` ;
- `recolor` reste à `false` : une autre teinte ne se déduit pas d’une recoloration du matériau.

Après avoir enregistré cette revue, `python scripts/3d_pipeline/image_to_3d.py --publish <id>` vérifie les preuves et le coloris du catalogue, copie le modèle dans `public/models` et ajoute `published_at`. `--approve <id>` ne fait qu’accepter un contrôle technique manuel : il ne publie pas le fichier et ne valide jamais la fidélité.

Pour les articles dont un détail intérieur ou une finition fait partie de la fiche, ajouter aussi des captures de ces détails et les examiner. Une planche synthétique, une image de banque, une seule photo ou un poster ne constitue pas une preuve physique.

Exemple du bloc de revue après contrôle humain :

```json
"fidelity_review": {
  "status": "approved",
  "source_type": "physical_product_captures",
  "captured_views": ["front", "back", "left", "right", "top", "bottom"],
  "variant_color": "Cognac",
  "reviewed_at": "2026-10-25T14:00:00+00:00",
  "reviewed_by": "nom-du-controleur",
  "note": "Silhouette, volumes, attaches et teinte vérifiés sur l’article physique."
}
```

Les modèles actuellement présents dans le manifeste restent en attente de ces preuves. Tant que la revue est absente ou incomplète, la fiche produit utilise ses photos et masque la vue 3D. Les anciens fichiers GLB encore présents dans `public/models` ne sont pas attachés aux fiches.
