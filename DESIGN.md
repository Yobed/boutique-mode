# DESIGN.md — Charte Graphique & Système de Design Maison Élégance

## 1. Direction Artistique & Atmosphère
- **Style** : Haute Couture Contemporaine Afro-Européenne.
- **Référence** : Maison de luxe parisienne & abidjanaise (lignes épurées, contrastes profonds, or brossé satiné, atmosphère de salon privé).

## 2. Palette de Couleurs (Harmonie Obsidienne & Or Champagne)
- **Fond Principal** : `var(--bg-obsidian)` (`#0c0c0e`, noir chaud teinté d'ambre, OKLCH ~ `14% 0.008 45`).
- **Surfaces Élégantes** : `var(--bg-surface)` (`#16161a`, noir charbon feutré).
- **Cartes & Tiroirs** : `var(--bg-card)` (`#1a1a20` avec bordure fine `#ffffff12`).
- **Or Champagne (Accent Primaire)** :
  - `gold-400`: `#e5c158` (reflets clairs)
  - `gold-500`: `#d4af37` (or impérial satiné)
  - `gold-600`: `#a88424` (or patiné)
- **Vert Émeraude Atelier (Accent Réassurance & WhatsApp)** :
  - `emerald-600`: `#12382c` (vert soie profonde)
  - `emerald-500`: `#1a5d46` (vert bouteille couture)
  - `emerald-400`: `#2ecc71` (vert actif WhatsApp)
- **Textes** :
  - Titres : Blanc ivoire pur (`#faf8f5`).
  - Corps de texte : Lin doux (`#d4d0c8`).
  - Métadonnées & Discrets : Ébène clair (`#918d84`).

## 3. Typographie
- **Affichage & Titres (Couture Display)** : `Italiana`, `Playfair/Bodoni`, serif éditorial à fort contraste de graisse et d'élégance.
- **Corps de texte & UI** : `Plus Jakarta Sans`, sans-serif géométrique humaniste aux proportions équilibrées.
- **Règles Typographiques** :
  - Pas de texte en dégradé multicolore (`bg-clip-text` banni).
  - Titres : Combinaison de normal bold et d'italique raffiné pour créer du rythme éditorial.
  - Interlettrage (`letter-spacing`) généreux sur les badges de collection (`0.12em`).

## 4. Règles de Mouvement & Animations (LottieFiles + CSS Animation)
- **Archetype** : *Premium / Luxury*.
- **Signature Easing** : `cubic-bezier(0.4, 0, 0.2, 1)` (0% rebond, 0% overshoot, décélération noble).
- **Durées** :
  - Micro-pression : 80ms (`motion-press`).
  - Survol carte : 150ms (`motion-hover-lift`).
  - Zoom image : 450ms (`motion-img-zoom`, max 1.04x).
  - Glissement tiroirs : 400ms (`drawer-in`).
- **Interdictions** : Pas d'animations `animate-bounce` enfantines ou tape-à-l'œil.

## 5. Composants Clés
- **Product Card** : Image plein cadre 3:4, zoom doux au survol, badge d'atelier discret, sélection immédiate de taille avec retour tactile.
- **Concierge Privé Styliste (Sophia)** : Interface émeraude atelier et or satiné, suggestions de vêtements avec affichage instantané des prix et tailles en stock.
- **Guide des Tailles** : Tableau comparatif interactif (mensurations poitrine, taille, hanches en cm).
- **Suivi de Commande** : Stepper interactif de livraison en temps réel à Abidjan.
