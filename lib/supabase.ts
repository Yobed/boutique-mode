import { createClient } from '@supabase/supabase-js';
import { Article, Commande } from './types';
import { ARTICLES_DEMO } from './mock-data';

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || '';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || '';

export const supabase = (supabaseUrl && supabaseAnonKey)
  ? createClient(supabaseUrl, supabaseAnonKey)
  : null;

export async function getArticles(): Promise<Article[]> {
  if (!supabase) {
    return ARTICLES_DEMO;
  }

  try {
    const { data, error } = await supabase
      .from('articles')
      .select('*')
      .order('created_at', { ascending: false });

    if (error || !data || data.length === 0) {
      return ARTICLES_DEMO;
    }

    return data as Article[];
  } catch (err) {
    console.warn('Fallback to demo articles:', err);
    return ARTICLES_DEMO;
  }
}

export async function getArticleById(id: string): Promise<Article | null> {
  if (!supabase) {
    return ARTICLES_DEMO.find((a) => a.id === id) || null;
  }

  try {
    const { data, error } = await supabase
      .from('articles')
      .select('*')
      .eq('id', id)
      .single();

    if (error || !data) {
      return ARTICLES_DEMO.find((a) => a.id === id) || null;
    }

    return data as Article;
  } catch {
    return ARTICLES_DEMO.find((a) => a.id === id) || null;
  }
}

export async function searchArticles(query: string, categorie?: string, genre?: string, maxPrice?: number): Promise<Article[]> {
  const all = await getArticles();
  const q = (query || '').toLowerCase().trim();

  return all.filter((item) => {
    // Filtre texte
    if (q) {
      const matchName = item.nom.toLowerCase().includes(q);
      const matchDesc = item.description.toLowerCase().includes(q);
      const matchCat = item.categorie.toLowerCase().includes(q);
      const matchTaille = item.tailles.some((t) => t.toLowerCase() === q);
      const matchCouleur = item.couleurs.some((c) => c.toLowerCase().includes(q));
      if (!matchName && !matchDesc && !matchCat && !matchTaille && !matchCouleur) return false;
    }

    // Filtre catégorie
    if (categorie && categorie !== 'tous' && item.categorie !== categorie) {
      return false;
    }

    // Filtre genre
    if (genre && genre !== 'tous' && item.genre !== genre && item.genre !== 'mixte') {
      return false;
    }

    // Filtre prix max
    if (maxPrice && maxPrice > 0 && item.prix > maxPrice) {
      return false;
    }

    return true;
  });
}

export type StatutLookup =
  | { kind: 'found'; statut: Commande['statut']; created_at?: string }
  | { kind: 'not_found' }
  | { kind: 'unavailable' };

/** Looks up an order by its public number. `unavailable` in demo mode or on network error. */
export async function getCommandeStatut(numero: string): Promise<StatutLookup> {
  const clean = numero.trim().toUpperCase().slice(0, 32);
  if (!supabase || !clean) return { kind: 'unavailable' };
  try {
    const { data, error } = await supabase
      .from('commandes')
      .select('statut, created_at')
      .eq('numero_commande', clean)
      .maybeSingle();
    if (error) return { kind: 'unavailable' };
    return data ? { kind: 'found', statut: data.statut, created_at: data.created_at } : { kind: 'not_found' };
  } catch {
    return { kind: 'unavailable' };
  }
}

export async function createCommande(cmd: Commande): Promise<{ success: boolean; id?: string; error?: string }> {
  if (!supabase) {
    // Demo mode (no Supabase env): accept the order without persisting customer data anywhere.
    return { success: true, id: `demo-${cmd.numero_commande}` };
  }

  try {
    const { data, error } = await supabase
      .from('commandes')
      .insert([cmd])
      .select('id')
      .single();

    if (error) {
      console.error('Erreur Supabase createCommande:', error);
      return { success: false, error: error.message };
    }

    return { success: true, id: data?.id };
  } catch (err: any) {
    return { success: false, error: err.message };
  }
}
