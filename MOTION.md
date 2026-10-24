# MOTION.md — ELSI

## Personnalité
**Magique, précis, sensuel, luxueux.** Le mouvement d’ELSI imite une vitrine de Cocody qui s’allume la nuit : un rideau de cabine qui s’ouvre, une lumière de scène qui glisse sur le perlage, une étoffe qui retombe. Jamais de rebond, jamais d’élastique, jamais d’animation pour décorer. Chaque mouvement révèle une pièce, confirme un geste ou guide vers l’achat.

## Durées
| Famille | Durée | Usage |
|---|---|---|
| Feedback | **120–180 ms** (`--dur-feedback` 150 ms) | pression bouton (scale 0.97–0.985), survol icônes, cœur, couleur des liens |
| UI | **220–360 ms** (`--dur-ui` 280 ms) | tiroir panier (420 ms entrée / 260 ms sortie), étapes du checkout (320 ms), sélecteurs, toasts, menus |
| Storytelling | **800–1600 ms** (`--dur-story` 1200 ms) | intro du héro (1,5 s), dévoilements au scroll, vol vers le panier (780 ms) |

Règle d’asymétrie : **les sorties sont ~35 % plus courtes que les entrées** et utilisent `--ease-exit`.

## Courbes (CSS ↔ GSAP ↔ Motion)
| Nom | cubic-bezier | Rôle |
|---|---|---|
| `silk` | `0.16, 1, 0.3, 1` | arrivées (exponentielle sortante) — défaut Motion |
| `curtain` | `0.77, 0, 0.175, 1` | masques, rideaux, vol vers le panier |
| `velvet` | `0.65, 0, 0.35, 1` | échanges d’état symétriques, lumière, reflets |
| `exit` | `0.4, 0, 1, 1` | départs |
| ressort sélecteurs | `stiffness 520, damping 42, mass 0.8` | pastille taille/couleur (layoutId), sans dépassement visible |

Déclarées dans `app/globals.css` (`--ease-*`), `lib/gsap.ts` (`CustomEase`) et `components/Providers.tsx` (`MotionConfig`).

## Stagger
**40–90 ms** : 50 ms pour les grilles produit (plafonné à 8 éléments), 60 ms pour le texte éditorial (mot à mot), 70 ms pour les textes de rangées, 50 ms pour le menu mobile.

## Accessibilité
- `prefers-reduced-motion: reduce` :
  - **GSAP** : aucune scène n’est créée (`gsap.matchMedia` ne cible que `no-preference`) ; les états pré-révélation CSS sont annulés → tout est visible, statique.
  - **Motion** : `MotionConfig reducedMotion="user"` supprime les transformations, garde les fondus.
  - **CSS** : boucles et transitions ramenées à 0,01 ms.
  - Le vol vers le panier est remplacé par le seul rebond du compteur.
- Le contenu est **visible par défaut** : sans JS, la classe `.js` n’est jamais posée et rien n’est masqué.
- Aucune animation ne cache un CTA : titre et boutons du héro sont statiques ; le bouton flottant de Sophia est retiré des fiches produit et du checkout ; la barre d’achat mobile n’apparaît qu’une fois le bouton principal sorti de l’écran.
- Focus géré : tiroir panier (piège de focus, Échap, retour du focus), visionneuse photo, guide des tailles, étapes du checkout (focus sur le titre de chaque étape après l’animation).
- Annonces : toast d’ajout en `aria-live="polite"`, erreurs de formulaire reliées par `aria-describedby`, erreur d’envoi en `role="alert"`.
- Mots révélés au scroll : opacité plancher 0,42 → contraste ≥ 3:1 même avant révélation ; le texte complet est fourni aux lecteurs d’écran.

## Performance
- **On n’anime que** `transform`, `opacity`, `clip-path`, `filter` (flou/luminosité ponctuels). Aucune animation de `width/height/top/left/margin`.
- Barre de progression et jauge « livraison offerte » : `scaleX`, pas `width`.
- Zoom produit : origine pilotée par variables CSS (`--zx/--zy`) → zéro re-render React par frame.
- GSAP : `useGSAP` avec `scope`, `matchMedia().revert()` au démontage, `invalidateOnRefresh` sur les distances mesurées, `scrub` 0,6–0,8 pour lisser.
- Aucun épinglage ni défilement détourné : le défilement reste natif sur tous les écrans, seules les images bougent (parallaxe).
- Objectif 60 fps ; `will-change` limité au calque image du héro.

## Les deux moments signature

### 1. « La vitrine s’allume » — révélation du produit héro (scène 1)
`components/home/SceneHero.tsx` · GSAP ScrollTrigger
1. Toute la scène est la photo de la Robe Ébène Perlée, derrière deux rideaux noirs. Avant même l’hydratation, une fente de lumière est visible (`clip-path: inset(0 48%)`).
2. À l’arrivée (desktop) : les rideaux s’entrouvrent à 20 % (1,6 s, `curtain`), l’image dézoome de 1,22 à 1,12. Le titre romain « Habillés pour les grands soirs. » occupe le rideau gauche, la pièce signature et son prix le rideau droit.
3. Au scroll (section épinglée sur 140 %) : les rideaux s’ouvrent en plein cadre, l’image termine son dézoom, le titre s’élève et s’efface, un voile bas monte pour garder le CTA lisible. Une **bande d’exposition** balaie la robe : c’est la photo elle-même, surexposée, vue à travers une fente aux bords doux qui se déplace (transform uniquement, sans halo coloré).
4. Le bouton « Découvrir la collection » et l’étiquette produit ne bougent jamais et restent cliquables du début à la fin.
5. Mobile : pas d’épinglage ; les rideaux s’ouvrent seuls en 1,6 s, la bande d’exposition passe une fois, le CTA est dans le premier écran.

Objectif UX : montrer une vraie pièce, à son prix, dans la lumière d’un soir abidjanais, avant tout discours.

### 2. Transition cinématique collection → savoir-faire (scènes 3 → 4)
`components/home/SceneCollectionSavoir.tsx` · GSAP ScrollTrigger
1. La collection défile horizontalement (section épinglée) ; chaque pièce hors du premier écran s’ouvre par un masque en entrant.
2. Dernier écran de l’épinglage : la collection **recule** (scale 1 → 0,9), **se floute** (0 → 8 px) et **s’assombrit** (luminosité 0,4), uniquement une fois la lecture terminée.
3. Pendant ce temps, le panneau lin du savoir-faire **glisse par-dessus** : un fil de laiton se tend d’abord (scaleX), puis le panneau s’ouvre comme un rideau (`inset 0 9%` → `0`), et sa photo de coupe de tissu descend en **parallaxe** (yPercent −14 → 0, scale 1,12 → 1).

Objectif UX : faire sentir le passage de la vitrine (le désir) à l’atelier (la confiance) sans rupture, et changer d’ambiance lumineuse : nuit → lin.

### 3. « La nuit tombe » — du savoir-faire à l’appel final (scènes 4 → 5)
`components/home/SceneFinalCta.tsx` · GSAP ScrollTrigger
1. La scène finale commence sous un voile de lin qui prolonge le savoir-faire : le visiteur ne voit pas de coupure.
2. Un fil de laiton se tend à l’horizon (scaleX), puis le lin se referme en deux paupières vers cette ligne (`inset(0)` → `inset(50% 0)`).
3. Derrière, le portrait sort du flou (10 px → 0), de l’ombre (luminosité 0,45 → 1) et du zoom (1,2 → 1), comme un œil qui s’habitue à la nuit ; le titre monte ligne à ligne.
4. Le voile n’existe qu’avec JS et mouvement autorisé (`.js [data-dusk]`), sinon la scène est directement visible.

Objectif UX : refermer la journée d’atelier et revenir à la nuit pour l’appel à l’action final.

## Inventaire des animations
| Animation | Fichier | Objectif UX | Outil / skill |
|---|---|---|---|
| Intro rideaux plein cadre | `home/SceneHero.tsx` | Révéler la pièce signature, créer l’émotion | GSAP (gsap-scrolltrigger) |
| Ouverture au scroll + bande d’exposition | `home/SceneHero.tsx` | Moment signature 1, lumière « matière » | GSAP ScrollTrigger |
| Voile de lin → horizon → portrait qui sort de l’ombre | `home/SceneFinalCta.tsx` | Transition « La nuit tombe » | GSAP ScrollTrigger |
| Phrase éditoriale mot à mot | `home/SceneUnivers.tsx` | Rythmer la lecture du manifeste | GSAP ScrollTrigger |
| Parallaxe deux profondeurs (atelier / wax) | `home/SceneUnivers.tsx` | Matière, profondeur | GSAP ScrollTrigger |
| Galerie horizontale épinglée + masques cartes | `home/SceneCollectionSavoir.tsx` | Présenter la collection comme un défilé | GSAP ScrollTrigger |
| Transition scale + flou + masque + parallaxe | `home/SceneCollectionSavoir.tsx` | Moment signature 2 | GSAP ScrollTrigger |
| Rangées savoir-faire (image masquée, texte en cascade) | `home/SceneCollectionSavoir.tsx` | Preuve, savoir-faire | GSAP ScrollTrigger |
| Portrait final dévoilé | `home/SceneFinalCta.tsx` | Clore sur une image forte, CTA fixe | GSAP ScrollTrigger |
| Galerie : grandes plaques empilées (desktop) / carrousel bord à bord (mobile), dévoilées au scroll, légère dérive intérieure | `product/ProductGallery.tsx` | Immersion dans la matière | Motion (motion-framer) useScroll |
| Barre de progression segmentée (mobile) | `product/ProductGallery.tsx` | Savoir où l’on est dans les photos | Motion |
| Visionneuse : morphing depuis la plaque (layoutId), swipe, glisser vers le bas pour fermer, zoom suivant le pointeur | `product/ProductGallery.tsx` | Voir le tissu de près sans perdre le contexte | Motion layoutId + drag |
| Sélecteurs taille/couleur (pastille qui glisse) | `product/VariantSelector.tsx` | Confirmer le choix, navigation au clavier | Motion layoutId |
| Ajout au panier : flash d’exposition, pièce pliée en échantillon qui suit un arc | `chrome/CartFeedback.tsx` | Ajout « magique », montrer où va la pièce | Motion keyframes |
| Anneau laiton unique sur le panier | `globals.css` `.icon-cart::after` | Accuser réception | CSS |
| Toast avec vignette, sous-total et « Commander » | `chrome/CartFeedback.tsx` | Raccourcir le chemin vers l’achat | Motion AnimatePresence |
| Bouton Ajouter → Ajouté | `product/AddToCartButton.tsx` | Feedback immédiat | Motion AnimatePresence |
| Tiroir panier, lignes qui entrent/sortent, jauge livraison offerte | `CartDrawer.tsx` | Panier vivant, incitation douce | Motion AnimatePresence + layout |
| Checkout : étapes glissées, barre de progression, erreurs | `checkout/CheckoutFlow.tsx`, `Field.tsx` | Avancer sans perdre le fil | Motion |
| Confirmation de commande | `checkout/CheckoutFlow.tsx` | Rassurer, inviter à WhatsApp | Motion |
| Grille catalogue (filtrage avec layout) | `app/catalogue/page.tsx` | Comprendre ce qui change au filtre | Motion layout + popLayout |
| Panneau filtres mobile, menu mobile, recherche | `catalogue`, `Navbar.tsx` | Ouverture/fermeture lisible | Motion (clip-path) |
| Barre d’achat mobile collante | `product/ProductDetail.tsx` | Garder l’achat à portée de pouce | Motion |
| Suivi de commande (étapes en cascade) | `app/suivi/page.tsx` | Lire l’état d’une commande réelle | Motion |
| Skeletons à reflet laiton | `globals.css` `.skeleton` | Attente premium | CSS (css-animation) |
| Cœur favori (pop + remplissage) | `globals.css` `.icon-heart` | Feedback de sauvegarde | CSS |
| Panier qui « reçoit » + compteur | `globals.css` `.icon-cart`, `.cart-count` | Accuser réception du vol | CSS |
| Loupe de recherche qui pivote | `globals.css` `.icon-search` | Affordance | CSS |
| Badge « Nouveau » (un seul reflet) | `globals.css` `.badge-new` | Attirer l’œil une fois | CSS |
| Badge « Plus que N » (statique) | `globals.css` `.badge-low` | Stock réel, énoncé sans effet | CSS |

**Supprimés (décoratifs, sans gain de conversion)** : halo radial du héro, mot-marque géant « ELSI » en filigrane, point qui pulse sur les badges stock et sur le bouton Sophia, titres en italique répétés, zoom loupe au survol de la fiche produit (remplacé par la visionneuse).
| Badge « Livraison offerte » (camion qui avance au survol) | `globals.css` `.badge-ship` | Valeur perçue | CSS |
| Soulignement dessiné des liens | `globals.css` `.link-draw` | Survol raffiné | CSS |

## Couche spectacle (octobre 2026)
Ajoutée pour l’effet « waouh » et la conversion. Le défilement reste natif : pas d’inertie, aucune section épinglée. Tout respecte `prefers-reduced-motion` (rien ne bouge, tout est visible).

| Effet | Fichier | Rôle |
|---|---|---|
| Intro de marque (1re visite de la session) | `components/fx/Preloader.tsx` + CSS `.preloader` | Lettres ELSI qui montent, fil laiton, rideau qui se lève. 100 % CSS, ne peut pas bloquer. |
| Curseur anneau + étiquette | `components/fx/Cursor.tsx` | `data-cursor="Voir"` sur un élément affiche l'étiquette dans un disque ivoire. |
| Boutons magnétiques | `components/fx/Magnetic.tsx` | CTA principaux attirés par le pointeur. |
| Bandeaux infinis | `components/fx/Marquee.tsx` | Promesses de service, avis clients ; pause au survol. |
| Titre lettre par lettre | `SceneHero` (GSAP SplitText, masque par ligne) | Démarre après l'intro (`introDelay()` dans `lib/gsap.ts`). Filet de sécurité CSS à 4 s. |
| Compteurs | `SceneProof` | Comptent une fois à l'entrée. |
| Portes Elle / Lui | `SceneGenres` + CSS `.door` | La porte survolée s'élargit, l'autre s'assombrit. |
| Étapes zéro risque | `SceneSteps` | Fil laiton qui se dessine, chiffres qui se remplissent (`--fill`). |

Leviers de persuasion utilisés (honnêtes) : inversion du risque, preuve sociale, autorité de l'atelier, rareté **réelle** (stock), ancrage (économie affichée), projection (« livrée dès demain, dimanche 25 octobre »), effet de but (barre de livraison offerte). Interdits maintenus : faux compte à rebours, faux « X personnes regardent ». Les avis et chiffres de `lib/marketing.ts` sont des exemples à remplacer.
