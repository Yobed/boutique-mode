# 👗 Boutique en Ligne — E-Commerce Mode & Styliste IA (100% Free / 0 FCFA)

Application e-commerce moderne de prêt-à-porter chic & haute couture avec **Agent IA Styliste Vendeur** (Sophia) disponible à la fois sur le site web et sur WhatsApp.

Conçue selon une architecture **100% Cloud Souveraine à 0 FCFA/mois à vie** :
* 🌐 **Site Web & API** : Next.js 15 sur **Netlify Starter** (0 FCFA)
* 🗄️ **Base de Données & Stockage** : PostgreSQL & Storage sur **Supabase** (0 FCFA)
* 🧠 **Intelligence Artificielle Vendeuse** : Llama 3.3 70B sur **Groq Cloud** / Gemini Flash (0 FCFA)
* 📱 **Canal WhatsApp** : Passerelle Baileys sur **Render Cloud** (0 FCFA)

---

## 🌟 Fonctionnalités

1. **Expérience d'Achat Haute Couture (Mobile-First)** :
   * Vitrine chic avec bannières de collection et vêtements vedettes.
   * Filtres instantanés : par taille (XS à XXL, 37 à 45), par couleur, par catégorie (Robes, Costumes, Lin/Wax, etc.) et par budget max.
   * Fiche produit détaillée avec galerie d'images HD, sélecteur de taille et stock disponible en temps réel.
2. **Panier & Express Checkout WhatsApp** :
   * Tiroir panier glissant avec gestion des quantités.
   * Calcul des frais de livraison automatiques (Abidjan 1 500 FCFA, Intérieur 2 500 FCFA).
   * Validation en 1 clic avec message WhatsApp pré-rempli pour confirmation immédiate avec le gérant.
   * Prise en charge du paiement à la livraison, Wave, Orange Money et MTN MoMo.
3. **Sophia — Conseillère & Styliste IA (Web + WhatsApp)** :
   * Conseils personnalisés selon l'occasion (mariage, dîner d'affaires, soirée gala).
   * Interrogation en temps réel du catalogue et des stocks.
   * Présentation des articles recommandés avec photos et bouton d'ajout au panier direct.
4. **Tableau de Bord Gérant (`/admin`)** :
   * Suivi des commandes reçues (N° commande, client, téléphone, adresse, articles, total).
   * Statistiques en direct (Chiffre d'affaires, commandes en attente).
5. **Modèles 3D générés depuis les photos produit** :
   * `npm run 3d:setup` (une fois), puis `npm run 3d:catalog` : chaque photo de sac, chaussure ou accessoire devient un modèle GLB publié dans `public/models/` et affiché dans l'onglet « Vue 3D 360° » de la fiche produit.
   * Contrôle qualité automatique (étanchéité, fidélité à la photo, un seul objet) ; les modèles douteux restent en « review » jusqu'à validation (`--approve`).
   * Mode fidèle : une planche multi-vues (face, dos, côtés, dessus, dessous) donne un modèle reconstruit au lieu de deviné : `npm run 3d:product -- --sheet planche.png --id mon-sac`.
   * Avec une seule photo, l'arrière de l'objet n'est pas visible : le modèle est une estimation. Détails et limites : [`docs/3d-pipeline/NEURAL_IMAGE_TO_3D.md`](docs/3d-pipeline/NEURAL_IMAGE_TO_3D.md).

---

## 🚀 Démarrage Rapide

### 1. Installation des dépendances
```bash
npm install
```

### 2. Lancement en développement local
```bash
npm run dev
```
Ouvrez [http://localhost:3000](http://localhost:3000) dans votre navigateur.
* La boutique démarre immédiatement avec une collection démo de 10 vêtements de luxe même sans base de données connectée.

### 3. Connexion Supabase (Optionnel pour passer en production)
1. Créez un projet gratuit sur [supabase.com](https://supabase.com).
2. Rendez-vous dans le **SQL Editor** et collez le contenu du fichier [`supabase/schema.sql`](supabase/schema.sql).
3. Cliquez sur **Run** : les tables `articles` et `commandes` sont créées et 10 articles sont injectés.
4. Créez un fichier `.env.local` et renseignez :
```env
NEXT_PUBLIC_SUPABASE_URL="https://votre-projet.supabase.co"
NEXT_PUBLIC_SUPABASE_ANON_KEY="votre-cle-anon"
GROQ_API_KEY="gsk_votre_cle_groq_gratuite"
```

---

## 💎 Studio 3D & Modélisation d'Articles Image-vers-3D

Le projet intègre désormais le **pipeline de modélisation 3D procédurale Blender** pour transformer automatiquement des photos d'articles de mode en modèles 3D interactifs (`.glb`) :

### 1. Modéliser un article depuis sa photo (en 1 clic) :
Déposez la photo dans `inputs/product_images/` puis lancez :
```powershell
npm run 3d:model -- -ImagePath "inputs/product_images/mon_sac.jpg" -Id "sac_luxe"
```
Le modèle est automatiquement analysé, modélisé sous Blender 5.2.2 avec shaders PBR physiques (cuir, métal, soie, verre), validé (100% manifold) et copié dans `public/models/sac_luxe.glb`.

### 2. Afficher le modèle 3D dans le site Web (React / Next.js) :
Utilisez le composant interactif `Product3DViewer` :
```tsx
import Product3DViewer from '@/components/3d/Product3DViewer';

<Product3DViewer
  modelSrc="/models/sac_luxe.glb"
  alt="Sac en Cuir Luxe"
  autoRotate={true}
/>
```

Pour tous les détails et personnalisations de matières, consultez le guide complet :
👉 [`docs/3d-pipeline/IMAGE_TO_3D_FASHION_GUIDE.md`](docs/3d-pipeline/IMAGE_TO_3D_FASHION_GUIDE.md)

---

## ☁️ Déploiement Gratuit sur Netlify (0 FCFA/mois)

1. Poussez le projet sur GitHub :
```bash
git add .
git commit -m "feat: boutique en ligne avec agent styliste ia"
git remote add origin https://github.com/VOTRE_USER/boutique-mode.git
git push -u origin master
```
2. Sur [app.netlify.com](https://app.netlify.com) :
   * Cliquez sur **Add new site** ➔ **Import an existing project** ➔ Choisissez votre dépôt GitHub.
   * Netlify détecte automatiquement le fichier `netlify.toml` et configure le build Next.js.
   * Ajoutez vos variables d'environnement dans les paramètres Netlify.
   * Votre boutique est en ligne avec HTTPS et domaine personnalisé gratuit !

---

## 📱 Activation du Styliste IA sur WhatsApp

La route webhook `/api/whatsapp/webhook` est déjà programmée. Il vous suffit de configurer l'URL de votre site Netlify dans votre passerelle Render WhatsApp :
```
https://votre-boutique.netlify.app/api/whatsapp/webhook
```
Dès qu'un client écrira un message sur WhatsApp, Sophia répondra en moins de 2 secondes avec les photos et les prix des vêtements adaptés !
