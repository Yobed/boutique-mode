-- ==============================================================================
-- BOUTIQUE EN LIGNE — SCHEMA POSTGRESQL & SEED SUPABASE (100% GRATUIT)
-- ==============================================================================

-- 1. Table des articles / vêtements
CREATE TABLE IF NOT EXISTS articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom TEXT NOT NULL,
    description TEXT,
    prix INTEGER NOT NULL, -- Prix en FCFA (ex: 25000)
    prix_promo INTEGER,
    categorie TEXT NOT NULL, -- 'robes', 'chemises', 'pantalons', 'costumes', 'chaussures', 'accessoires', 't-shirts'
    genre TEXT NOT NULL DEFAULT 'femme', -- 'femme', 'homme', 'enfant', 'mixte'
    tailles TEXT[] NOT NULL DEFAULT '{}', -- ARRAY['S', 'M', 'L', 'XL']
    couleurs TEXT[] NOT NULL DEFAULT '{}', -- ARRAY['Rouge', 'Noir', 'Blanc']
    photos TEXT[] NOT NULL DEFAULT '{}',
    en_stock BOOLEAN DEFAULT true,
    quantite_stock INTEGER DEFAULT 1,
    vedette BOOLEAN DEFAULT false,
    nouveaute BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Table des commandes
CREATE TABLE IF NOT EXISTS commandes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    numero_commande TEXT UNIQUE NOT NULL, -- ex: CMD-849201
    client_nom TEXT NOT NULL,
    client_telephone TEXT NOT NULL,
    client_adresse TEXT,
    commune_livraison TEXT NOT NULL, -- Cocody, Marcory, Plateau, Yopougon...
    articles_commande JSONB NOT NULL, -- [{ article: {...}, taille: 'M', couleur: 'Noir', quantite: 1 }]
    montant_total INTEGER NOT NULL,
    frais_livraison INTEGER DEFAULT 1500,
    statut TEXT NOT NULL DEFAULT 'en_attente', -- 'en_attente', 'confirmee', 'en_livraison', 'livree', 'annulee'
    canal_origine TEXT NOT NULL DEFAULT 'web', -- 'web' ou 'whatsapp'
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Activation de Row Level Security (RLS)
ALTER TABLE articles ENABLE ROW LEVEL SECURITY;
ALTER TABLE commandes ENABLE ROW LEVEL SECURITY;

-- Politiques de sécurité (Lecture publique pour les clients, insertion publique de commande)
CREATE POLICY "Lecture publique des articles" ON articles FOR SELECT USING (true);
CREATE POLICY "Insertion publique des commandes" ON commandes FOR INSERT WITH CHECK (true);
CREATE POLICY "Lecture des commandes autorisée" ON commandes FOR SELECT USING (true);

-- 4. Insertion des 10 premiers articles de mode (Collection de départ)
INSERT INTO articles (nom, description, prix, prix_promo, categorie, genre, tailles, couleurs, photos, en_stock, quantite_stock, vedette, nouveaute)
VALUES
(
    'Robe Soirée Émeraude Satinée',
    'Sublime robe longue fluide en satin soyeux de couleur émeraude. Coupe cintrée flatteuse avec fente discrète sur le côté. Idéale pour galas, dîners chics et mariages.',
    38000, 32000, 'robes', 'femme',
    ARRAY['S', 'M', 'L', 'XL'],
    ARRAY['Vert Émeraude', 'Noir Profond', 'Bordeaux'],
    ARRAY['https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800&auto=format&fit=crop&q=80'],
    true, 12, true, true
),
(
    'Costume Slim Fit Deux Pièces Bleu Nuit',
    'Ensemble veste et pantalon sur mesure en laine froide italienne. Coupe moderne ajustée avec doublure satinée. Finitions tailleur haut de gamme pour l''homme d''affaires moderne.',
    85000, 75000, 'costumes', 'homme',
    ARRAY['M', 'L', 'XL', 'XXL'],
    ARRAY['Bleu Nuit', 'Gris Anthracite', 'Noir'],
    ARRAY['https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800&auto=format&fit=crop&q=80'],
    true, 8, true, true
),
(
    'Ensemble Wax Moderne & Lin Blanc',
    'Création artisanale haut de gamme combinant lin pur respirant et motifs authentiques en Wax doré. Une élégance afro-contemporaine parfaite pour les sorties et cérémonies.',
    42000, NULL, 'chemises', 'homme',
    ARRAY['S', 'M', 'L', 'XL', 'XXL'],
    ARRAY['Blanc & Or', 'Bleu Indigo & Ocre'],
    ARRAY['https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=800&auto=format&fit=crop&q=80'],
    true, 15, true, false
),
(
    'Robe Cocktail Cache-Cœur Fleurie',
    'Robe mi-longue ceinturée avec col cache-cœur et manches papillon. Tissu en mousseline légère au tomber impeccable. Très agréable à porter en journée comme en soirée.',
    26000, NULL, 'robes', 'femme',
    ARRAY['XS', 'S', 'M', 'L'],
    ARRAY['Terracotta', 'Bleu Ciel', 'Noir Floral'],
    ARRAY['https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800&auto=format&fit=crop&q=80'],
    true, 7, false, true
),
(
    'Chemise Homme Coton Égyptien Manches Longues',
    'Chemise business classique en coton égyptien double retors. Col semi-italien renforcé, boutons en nacre gravés et tissu infroissable toute la journée.',
    22000, 18500, 'chemises', 'homme',
    ARRAY['S', 'M', 'L', 'XL'],
    ARRAY['Blanc Pur', 'Bleu Ciel', 'Rose Poudré'],
    ARRAY['https://images.unsplash.com/photo-1603252109303-2751441dd157?w=800&auto=format&fit=crop&q=80'],
    true, 25, false, false
),
(
    'Pantalon Tailleur Taille Haute Cintrée',
    'Pantalon chic à pinces avec taille haute élastiquée à l''arrière pour un confort absolu. Jambe droite élancée, poches italiennes et tissu stretch infroissable.',
    24000, NULL, 'pantalons', 'femme',
    ARRAY['S', 'M', 'L', 'XL'],
    ARRAY['Camel', 'Noir', 'Beige Ivoire'],
    ARRAY['https://images.unsplash.com/photo-1584370848010-d7fe6bc767ec?w=800&auto=format&fit=crop&q=80'],
    true, 14, false, true
),
(
    'Escarpins Cuir Verni Talon Aiguille 8cm',
    'Paire d''escarpins intemporels confectionnés en cuir verni premium. Semelle intérieure rembourrée avec coussinet mémoire de forme pour un confort prolongé.',
    34000, NULL, 'chaussures', 'femme',
    ARRAY['37', '38', '39', '40', '41'],
    ARRAY['Noir Verni', 'Nude Poudré', 'Rouge Passion'],
    ARRAY['https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=800&auto=format&fit=crop&q=80'],
    true, 9, true, false
),
(
    'Mocassins Cuir Suédé Penny Loafers',
    'Mocassins classiques pour homme en veau velours doux. Cousu Blake artisanal et semelle gomme antidérapante. La touche d''élégance décontractée idéale.',
    45000, 39000, 'chaussures', 'homme',
    ARRAY['40', '41', '42', '43', '44', '45'],
    ARRAY['Brun Chocolat', 'Noir', 'Bleu Marine'],
    ARRAY['https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?w=800&auto=format&fit=crop&q=80'],
    true, 11, false, true
),
(
    'Sac à Main Cuir Grainé Fermoir Doré',
    'Sac à main rigide structuré avec poignée supérieure et bandoulière amovible. Trois compartiments doublés dont un zippé pour une organisation optimale.',
    32000, NULL, 'accessoires', 'femme',
    ARRAY['Unique'],
    ARRAY['Noir', 'Bordeaux', 'Cognac'],
    ARRAY['https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=800&auto=format&fit=crop&q=80'],
    true, 18, true, false
),
(
    'Polo Piqué Signature Boutons Nacre',
    'Polo classique en piqué de coton peigné haut de gamme. Col renforcé indéformable et broderie subtile ton sur ton sur la poitrine. Respirant et durable.',
    16000, NULL, 't-shirts', 'homme',
    ARRAY['S', 'M', 'L', 'XL', 'XXL'],
    ARRAY['Blanc', 'Noir', 'Vert Forêt', 'Bordeaux'],
    ARRAY['https://images.unsplash.com/photo-1581655353564-df123a1eb820?w=800&auto=format&fit=crop&q=80'],
    true, 30, false, false
);
