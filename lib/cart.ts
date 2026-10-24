import type { Article, CartItem } from './types';
import {
  DELIVERY_FEE_ABIDJAN,
  DELIVERY_FEE_INTERIEUR,
  FREE_DELIVERY_THRESHOLD,
} from './config.ts';

// Pure, immutable cart operations. Every function returns a new array.

export const unitPrice = (article: Article): number => article.prix_promo ?? article.prix;

const sameLine = (item: CartItem, article: Article, taille: string, couleur: string) =>
  item.article.id === article.id && item.taille === taille && item.couleur === couleur;

const maxQty = (article: Article) => Math.max(article.quantite_stock, 1);

export function addItem(items: CartItem[], article: Article, taille: string, couleur: string): CartItem[] {
  if (!article.en_stock) return items;
  const exists = items.some((i) => sameLine(i, article, taille, couleur));
  if (!exists) return [...items, { article, taille, couleur, quantite: 1 }];
  return items.map((i) =>
    sameLine(i, article, taille, couleur) ? { ...i, quantite: Math.min(i.quantite + 1, maxQty(article)) } : i
  );
}

export function setQuantity(items: CartItem[], index: number, quantite: number): CartItem[] {
  if (quantite <= 0) return removeItem(items, index);
  return items.map((item, i) =>
    i === index ? { ...item, quantite: Math.min(quantite, maxQty(item.article)) } : item
  );
}

export function removeItem(items: CartItem[], index: number): CartItem[] {
  return items.filter((_, i) => i !== index);
}

export function countItems(items: CartItem[]): number {
  return items.reduce((n, i) => n + i.quantite, 0);
}

export function subtotal(items: CartItem[]): number {
  return items.reduce((sum, i) => sum + unitPrice(i.article) * i.quantite, 0);
}

export function deliveryFee(items: CartItem[], commune: string): number {
  if (items.length === 0) return 0;
  if (subtotal(items) >= FREE_DELIVERY_THRESHOLD) return 0;
  return /int[ée]rieur/i.test(commune) ? DELIVERY_FEE_INTERIEUR : DELIVERY_FEE_ABIDJAN;
}

// Validates data read back from localStorage (untrusted).
export function parseStoredCart(raw: string | null): CartItem[] {
  if (!raw) return [];
  try {
    const data: unknown = JSON.parse(raw);
    if (!Array.isArray(data)) return [];
    return data.filter(
      (i): i is CartItem =>
        !!i &&
        typeof i === 'object' &&
        typeof i.article?.id === 'string' &&
        typeof i.article?.prix === 'number' &&
        typeof i.taille === 'string' &&
        typeof i.couleur === 'string' &&
        Number.isInteger(i.quantite) &&
        i.quantite > 0
    );
  } catch {
    return [];
  }
}
