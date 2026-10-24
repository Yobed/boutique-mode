# DESIGN.md — ELSI

## 1. Direction artistique
**La galerie.** Chaque article est présenté comme une œuvre : un packshot (l’objet seul, fond blanc) posé sur une plaque gris pierre, sur une page blanche. Pas de mannequin, pas de mise en scène : on vend l’article. Références étudiées : Polène (blanc, plaques pierre, objet seul), Jacquemus (blanc, noir, la photo porte tout).

- **Mode** : Persuade (accueil), Operate (catalogue, panier, commande).
- **Refus** : fond noir, doré, dégradés violets, texte en dégradé, cartes dans des cartes, compteurs d’urgence factices, photos de mannequins pour présenter un article.

## 2. Couleurs (OKLCH, `app/globals.css`)
Stratégie : **blanc + pierre + un accent** (indigo baoulé), deux rôles sémantiques (rouge cola = stock limité et promo, vert = WhatsApp et réassurance).

| Rôle | Token | Hex |
|---|---|---|
| Page | `--paper` (classes `bg-paper`, ancien `ink-950`) | `#FFFFFF` |
| Panneaux (tiroir, menus) | `--panel` (`bg-panel`, ancien `ink-900`) | `#F7F5F2` |
| Plaques photo | `--stone` / `--stone-deep` (`bg-stone`) | `#ECE9E4` / `#DDD8D0` |
| Texte | `--ink` (`text-ink`, ancien `ivory`) | `#141414` |
| Texte secondaire | `--mute-200…600` (`text-mute-*`, ancien `zinc-*`) | `#5D5B56` = 6,6:1 sur blanc |
| Accent | `--indigo-200…700` (`indigo-*`, anciens `brass-*`, `gold-*`) | `#22305E` |
| Stock limité / promo | `--cola-300…500` (`cola-*`, anciens `ember-*`, `amber-*`, `red-*`) | `#A8322A` |
| WhatsApp / réassurance | `--green-200…950` (`green-*`, ancien `emerald-*`) | `#0E5C46` |

Les anciens noms Tailwind sont conservés comme alias inversés dans `tailwind.config.ts` (un fond sombre + texte clair devient un fond clair + texte sombre). Le nouveau code utilise les noms de rôle.

## 3. Typographie
- **Titres** : *Zodiak* (Indian Type Foundry), romain + italique. L’italique indigo marque le mot important d’un titre.
- **Texte & UI** : *Switzer* (Indian Type Foundry) 400/500/600.
- Chargées par l’API CSS officielle de Fontshare dans `app/layout.tsx` (licence ITF Free Font License, usage commercial web autorisé). Variables `--font-display` / `--font-text`.
- Libellés : capitales 11 px, interlettrage `0.14em` (`tracking-label`). Prix en `tabular-nums`.

## 4. Photos produits
- **Packshot obligatoire** : l’article seul sur fond blanc, entier, non recadré (`object-contain`).
- La photo est fusionnée avec la plaque (`mix-blend-multiply`) : son fond blanc devient pierre. Tout calque animé (masque, parallaxe) entre la plaque et l’image doit hériter de la couleur (`[background-color:inherit]`), sinon le fondu ne se fait pas.
- Fond gris clair au lieu de blanc : ajouter le paramètre d’exposition Unsplash (`P(id, 10)` dans `lib/mock-data.ts`). Pour vos propres photos, exportez sur fond blanc pur.

## 5. Espace, grille, formes
- Gouttière `--gutter` : `clamp(1rem, 0.6rem + 2vw, 2.5rem)` ; respiration de section `--section` : `clamp(5rem, 3rem + 8vw, 11rem)`.
- Grille 12 colonnes, largeur max 1440 px ; grille produits 2 colonnes (mobile) / 4 (bureau).
- Rayons : 0 partout (plaques, boutons) ; `999px` seulement pour les pastilles (compteur, flèches rondes, bouton Sophia).

## 6. États
| État | Traitement |
|---|---|
| Survol | plaque pierre → pierre foncée, objet zoomé 1,06, soulignement dessiné (`link-draw`), bouton : rideau encre qui monte |
| Focus | contour indigo 2 px, décalage 3 px |
| Actif | `scale(0.98)` |
| Épuisé | badge « Épuisé », image désaturée |

## 7. Mouvement
Voir `MOTION.md`. Défilement natif (pas d’inertie, aucune section qui bloque le défilement) ; le mouvement vient de la parallaxe des plaques, des dévoilements et du titre lettre par lettre.
