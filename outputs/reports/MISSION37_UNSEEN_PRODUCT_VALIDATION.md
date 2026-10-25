# Mission 37 — validation sur des produits inédits

Date d’audit : 24 octobre 2026  
Statut : **NON VALIDÉ**

## Résumé

Une campagne antérieure est présente dans `outputs/test_mission37_campaign` avec 11 cas, des GLB, des spécifications JSON, des journaux et des rendus. Cet audit a contrôlé ces éléments sans relancer ni modifier le pipeline. Les données attestent de 11 images distinctes et d’un gel des principaux modules, mais pas d’une validation indépendante satisfaisante : seulement 2 catégories sont exactes sur 11, des composants sont manifestement mal attribués, et la validation technique des GLB n’a pas pu s’exécuter.

Les résultats de la campagne ne démontrent pas non plus que la classification se fonde sur l’image seule : les noms des fichiers de test décrivent explicitement les objets, alors que la mission demandait des noms neutres ou trompeurs. L’existence d’images préalablement utilisées dans les répertoires Mission 36 est documentée, mais l’absence de recouvrement exact ou perceptuel avec ces images n’est pas démontrée. Les 11 empreintes de ce jeu sont distinctes entre elles.

## Méthode et éléments vérifiés

- Résumé de campagne : `outputs/test_mission37_campaign/campaign_summary.json`.
- Entrées : `inputs/product_images/mission37_test_cases/`.
- Sorties : dossiers `case01` à `case11`, contenant spécifications, GLB, aperçus et journaux.
- Gel : `scripts/3d_pipeline/backups/mission37_freeze/code_freeze_manifest.json` et les neuf fichiers `.frozen` associés.
- Les SHA-256 des neuf modules actifs listés dans le manifeste concordent avec les empreintes déclarées.
- Les 11 SHA-256 d’images du résumé concordent avec les fichiers présents; ils sont tous distincts.
- Aucun nouvel essai de génération n’a été exécuté durant cet audit. Les modifications du pipeline ne font pas partie de la campagne.

## Résultats individuels

| Cas | Image | Vérité terrain | Prédiction | Catégorie exacte | Contradiction signalée | GLB exporté | Validation | s | Observation sur les composants |
|---|---|---|---|---:|---:|---:|---|---:|---|
| 01 | `case01_sofa_trompeur.jpg` | Sac à main | `fashion_leather_goods` | Oui | Oui | Oui | Non exécutée | 40,81 | Sac, rabat, fermoir et anse cohérents |
| 02 | `case02_produit_neutre_chaussure.png` | Chaussure | `multi_component_spatial_decomposed` | Non | Non | Oui | Non exécutée | 52,70 | 10 éléments génériques, dont deux anses courbes |
| 03 | `case03_sac_trompeur_fauteuil.png` | Fauteuil | `multi_component_spatial_decomposed` | Non | Oui | Oui | Non exécutée | 40,96 | 25 éléments génériques et deux anses; fauteuil non représenté de façon fiable |
| 04 | `case04_bouteille_isotherme.png` | Bouteille thermos | `minimalist_lighting` | Non | Oui | Oui | Non exécutée | 35,21 | Base, tige, abat-jour et finial de lampe |
| 05 | `case05_vase_carafe_verre.png` | Vase/carafe | `scandinavian_tableware_lathe` | Oui* | Non | Oui | Non exécutée | 35,30 | Un corps de vase; matériaux et fidélité non évalués |
| 06 | `case06_sofa_trompeur_lampe.jpg` | Lampe | `fashion_leather_goods` | Non | Oui | Oui | Non exécutée | 72,23 | Corps en cuir, rabat et anse de sac |
| 07 | `case07_enceinte_acoustique.png` | Enceinte | `multi_component_spatial_decomposed` | Non | Non | Oui | Non exécutée | 35,87 | Couches cylindriques génériques; électronique non établie |
| 08 | `case08_tasse_mug_anse.png` | Mug à anse | `fashion_leather_goods` | Non | Non | Oui | Non exécutée | 36,81 | Corps en cuir, rabat et anse de sac |
| 09 | `case09_marteau_asymetrique.png` | Marteau | `minimalist_lighting` | Non | Non | Oui | Non exécutée | 36,45 | Base, tige, abat-jour et finial de lampe |
| 10 | `case10_fer_vapeur_multimat.png` | Fer à repasser | `multi_component_spatial_decomposed` | Non | Non | Oui | Non exécutée | 34,51 | Un seul socle; poignée et matériaux multiples absents |
| 11 | `case11_tabouret_tripode.png` | Tabouret tripode | `fashion_leather_goods` | Non | Non | Oui | Non exécutée | 34,31 | Corps en cuir, rabat et anse; tabouret non représenté |

\* Le cas 05 correspond à la catégorie déclarée, mais la vérité terrain regroupe vase et carafe et ne permet pas d’évaluer finement la distinction.

## Métriques agrégées

| Mesure | Résultat observé | Limite |
|---|---:|---|
| Exactitude de catégorie | 2/11 (18,2 %) | Catégories GT parfois larges ou distinctes du vocabulaire de sortie |
| Noms trompeurs | 3/11 | Les noms trompeurs étaient effectivement présents dans les noms de fichiers |
| Signal de contradiction sur les trois noms trompeurs | 3/3 | Ce signal n’a pas empêché les erreurs image/nom : cas 03, 04 et 06 restent mal classés; seule la vérité terrain du cas 01 est exacte |
| SHA-256 d’images distincts | 11/11 | Confirme l’unicité binaire au sein du jeu, pas l’absence de quasi-doublons ni d’usage lors du développement |
| GLB exporté | 11/11 | Le journal du cas 01 confirme un export GLB réussi et un fichier non vide; aucun contrôle indépendant de tous les GLB n’a été effectué |
| Validation technique via `validator.py` | 0/11 confirmées | Le validateur s’arrête sur `ModuleNotFoundError: No module named 'mathutils'`; les statuts `WARNING_OR_FAIL` ne démontrent pas que les fichiers GLB soient invalides |
| Temps total / moyen | 455,16 s / 41,38 s par cas | D’après le résumé enregistré; pas de nouvelle mesure pendant cet audit |
| Fidélité silhouette, composants visibles, matériaux | Non évaluée formellement | La planche comparative existe, mais aucune notation fiable photo-versus-GLB n’est enregistrée dans les données auditées |
| Intervention humaine | 0 signalée dans le résumé | Ce champ est une déclaration du pipeline, non une observation indépendante |

Les règles métier ne sont pas toutes mesurables : le nom des fichiers révèle souvent l’objet, les catégories source et cible ne sont pas alignées dans tous les cas, et aucune justification textuelle normalisée de la classification n’est conservée dans le résumé. Par conséquent, le 2/11 est l’exactitude stricte selon les catégories déclarées, pas une mesure exhaustive de la qualité visuelle.

## Échec de validation GLB

Le journal du cas 01 montre que l’export Blender a terminé avec `valid=True` et un GLB de 57 576 octets. Le processus de validation lancé ensuite avec le Python embarqué Blender a échoué à l’import de `mathutils`. Le même statut global `WARNING_OR_FAIL` apparaît pour les 11 cas. Cela signifie que la vérification du maillage et de l’export par le validateur du projet est indisponible dans cette campagne; aucune conclusion de manifold, de structure interne ou de fidélité ne peut en être tirée.

## Non-régression web

Les tests Next.js, le typecheck, le build de production, l’intégrité des modèles existants et le fonctionnement du visualiseur n’ont pas été exécutés dans cet audit. Ils sont **non vérifiés**, et non réputés réussis. Aucun fichier produit du pipeline ni code applicatif n’a été modifié pendant l’audit.

## Correctifs post-campagne — révision image-first

Après l’audit historique, une révision séparée a corrigé les défauts techniques et les faux positifs mis en évidence. Elle ne modifie pas rétroactivement les résultats ni les GLB de la campagne d’origine.

- Le classificateur ne laisse plus le nom du fichier choisir ou renforcer une catégorie. Les noms servent à signaler une contradiction quand la silhouette fournit déjà une classe exploitable.
- Une cavité seule ne suffit plus à classer un objet comme sac. Un faisceau d’indices (ouverture importante, corps rempli, silhouette asymétrique et partie basse suffisamment large) est requis pour le sac Kelly. Une bouteille ou un marteau ne sont plus assimilés à une lampe sur le seul rapport de forme ou une tige étroite. Les objets hors des archétypes pris en charge restent génériques.
- Un solide de révolution est départagé vers tableware avant une lampe lorsque les scores se recouvrent.
- Le validateur Blender possède maintenant un point d’entrée CLI, vide la scène avant import et émet un résultat JSON exploitable. L’audit topologique fusionne les sommets dupliqués uniquement dans sa copie temporaire afin que les coutures glTF ne soient pas comptées comme des arêtes ouvertes.
- La profondeur déclarée du sac inclut désormais le fermoir saillant.
- Le banc de classification comprend les 11 images de Mission 37 en plus des 8 cas historiques. Résultat courant : **19/19 assertions image-first réussies**. Sur les 11 images inédites, 3 reçoivent un archétype spécifique (sac, vase/carafe, lampe) et 8 restent génériques faute de classe dédiée ; cela ne vaut pas 11 reconstructions sémantiquement exactes. Les deux noms trompeurs qui produisent une classe spécifique sont signalés.
- Les cas historiques `sofa_demo.png` et `sac_cuir_luxe.png` ont le même SHA-256 (`9a24daeb29bc4f546d0d5e745dec2529a8501c7ced94c04f1a55e14c49835a8a`). Ils ne peuvent donc pas justifier deux catégories visuelles distinctes ; le banc attend maintenant le repli générique pour cette paire.
- Le test syntaxique Python, la suite 19 cas, trois régressions image-first et le contrôle d’enveloppe de spécification sont réussis. Le validateur GLB a réussi sur 10 des 11 anciens exports ; le cas 01 échoue seulement à la comparaison de dimensions de son ancienne spécification. Une nouvelle génération du cas 01 dans `outputs/mission37_fix_verify_20261024/case01` passe les contrôles de géométrie et de dimensions.
- Non-régression web après correctifs : **11/11 tests**, typecheck réussi et build Next.js réussi avec 41 pages générées. Le build affiche un avertissement `metadataBase` absent pour la résolution des URL Open Graph/Twitter ; aucun échec bloquant. Le visualiseur 3D n’a pas été contrôlé manuellement.

Empreintes SHA-256 des fichiers de la révision post-campagne :

| Fichier | SHA-256 |
|---|---|
| `scripts/3d_pipeline/semantic_classifier.py` | `fd248f6e0af5b04cec3c5302f8ced99ba506523d4c6706a7d3f81d268c302f7a` |
| `scripts/3d_pipeline/validator.py` | `63315c0db0f0d6a6edf31fa58a9c58560d11aeb2f9a3ba7839cf4b5968470a40` |
| `scripts/3d_pipeline/validate_scene.py` | `e5be32d803bfdb18aaf175183767eb2593ed6ee0b45bcea61a9c6a4364e5b285` |
| `scripts/3d_pipeline/component_analyzer.py` | `dacac4fcedb29f3ccf8b0534a0e697fa896fcc6a975f881f6d160583b45f852e` |
| `scripts/tools/test_semantic_classifier_suite.py` | `14ff1772e0ad76b2950466d91b120f6838acbf78bc99654d7778cb87f3ea40c3` |

Ces corrections sont postérieures à la campagne gelée. Les 8 cas génériques restent des abstentions, et non des reconnaissances de chaussure, fauteuil, bouteille, enceinte, mug, marteau, fer ou tabouret. Blender n’était pas joignable pendant le dernier contrôle, et les tests Next.js, le typecheck, le build et l’évaluation visuelle comparée restent non vérifiés. Le verdict de la campagne indépendante demeure donc **NON VALIDÉ**.

## Verdict et limites

**NON VALIDÉ.** Les résultats montrent des erreurs de classification répétées et la réutilisation d’archétypes de composants inadaptés (notamment sac et lampe). La campagne ne satisfait pas le contrôle des noms neutres, ne prouve pas l’inédit vis-à-vis des données de développement, ne fournit pas d’évaluation de fidélité visuelle reproductible et n’a pas obtenu de validation technique du maillage. L’export d’un GLB ne doit pas être assimilé à une reconstruction fidèle ni à une validation de qualité.

La campagne enregistrée reste utile comme diagnostic historique; ses résultats ne doivent pas être présentés comme une validation indépendante réussie. Toute nouvelle mesure devrait utiliser un jeu dont les images et les noms sont gelés avant le test, établir les catégories de référence indépendamment, corriger l’environnement du validateur avant la campagne, et préserver les sorties courantes.
