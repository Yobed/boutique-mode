// Single source of truth for brand facts used across the storefront.
export const BRAND = {
  name: 'ELSI',
  tagline: 'Vêtements & accessoires — Abidjan',
  city: 'Abidjan',
} as const;

// Shop WhatsApp: 05 74 24 37 52 (Côte d’Ivoire). Overridable per environment.
export const WHATSAPP_NUMBER = (process.env.NEXT_PUBLIC_WHATSAPP_PHONE || '2250574243752').replace(/\D/g, '');
// "2250574243752" -> "+225 05 74 24 37 52"
export const WHATSAPP_DISPLAY = `+${WHATSAPP_NUMBER.slice(0, 3)} ${WHATSAPP_NUMBER.slice(3).replace(/(\d{2})(?=\d)/g, '$1 ')}`;

// Business rule: orders at or above this amount ship free.
// ponytail: one flat threshold; per-commune rules if the logistics partner needs them.
export const FREE_DELIVERY_THRESHOLD = 100_000;
export const DELIVERY_FEE_ABIDJAN = 1_500;
export const DELIVERY_FEE_INTERIEUR = 2_500;

// Stock at or below this count shows the "Stock limité" badge (real stock, never a fake counter).
export const LOW_STOCK_THRESHOLD = 8;

export const COMMUNES = [
  'Cocody',
  'Plateau',
  'Marcory',
  'Treichville',
  'Yopougon',
  'Koumassi',
  'Port-Bouët',
  'Bingerville',
  'Autre commune d’Abidjan',
  'Intérieur du pays',
] as const;

export function waLink(text?: string): string {
  const base = `https://wa.me/${WHATSAPP_NUMBER}`;
  return text ? `${base}?text=${encodeURIComponent(text)}` : base;
}

export function formatFCFA(amount: number): string {
  return `${amount.toLocaleString('fr-FR')} FCFA`;
}
