export type CategorieVêtement =
  | 'tous'
  | 'robes'
  | 'chemises'
  | 'pantalons'
  | 'costumes'
  | 'chaussures'
  | 'accessoires'
  | 't-shirts';

export type GenreVêtement = 'tous' | 'femme' | 'homme' | 'enfant' | 'mixte';

export interface Article {
  id: string;
  nom: string;
  description: string;
  prix: number; // en FCFA (ex: 25000)
  prix_promo?: number;
  categorie: CategorieVêtement;
  genre: GenreVêtement;
  tailles: string[]; // ex: ['S', 'M', 'L', 'XL'] ou ['38', '39', '40', '41']
  couleurs: string[]; // ex: ['Noir', 'Blanc', 'Bordeaux']
  photos: string[];
  en_stock: boolean;
  quantite_stock: number;
  vedette?: boolean;
  nouveaute?: boolean;
  created_at?: string;
}

export interface CartItem {
  article: Article;
  taille: string;
  couleur: string;
  quantite: number;
}

export type StatutCommande =
  | 'en_attente'
  | 'confirmee'
  | 'en_livraison'
  | 'livree'
  | 'annulee';

export interface Commande {
  id?: string;
  numero_commande: string;
  client_nom: string;
  client_telephone: string;
  client_adresse: string;
  commune_livraison: string;
  articles_commande: CartItem[];
  montant_total: number;
  frais_livraison: number;
  statut: StatutCommande;
  canal_origine: 'web' | 'whatsapp';
  mode_paiement?: 'livraison' | 'wave' | 'orange_money' | 'mtn_momo';
  created_at?: string;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  articles?: Article[];
  suggestedActions?: string[];
  orderDraft?: Partial<Commande>;
  timestamp: number;
}
