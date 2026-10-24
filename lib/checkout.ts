import { COMMUNES } from './config.ts';

export type PaymentMethod = 'livraison' | 'wave' | 'orange_money' | 'mtn_momo';

export interface CheckoutForm {
  nom: string;
  telephone: string;
  commune: string;
  adresse: string;
  instructions: string;
  paiement: PaymentMethod;
}

export type FieldErrors = Partial<Record<keyof CheckoutForm, string>>;

export const PAYMENT_LABELS: Record<PaymentMethod, { titre: string; detail: string }> = {
  livraison: { titre: 'Espèces à la réception', detail: 'Réglez en mains propres au coursier lors de la remise du colis.' },
  wave: { titre: 'Wave à la réception', detail: 'Réglez par Wave directement au coursier ou sur notre compte marchand à la livraison.' },
  orange_money: { titre: 'Orange Money à la réception', detail: 'Réglez par Orange Money au coursier lors de la remise du colis.' },
  mtn_momo: { titre: 'MTN MoMo à la réception', detail: 'Réglez par MTN MoMo au coursier lors de la remise du colis.' },
};

/**
 * Ivorian numbers: 10 digits starting 01, 05, 07 (mobile) or 21/25/27 (fixed),
 * optionally prefixed by +225 / 00225. Returns the 10 national digits or null.
 */
export function normalizePhoneCI(input: string): string | null {
  let digits = input.replace(/\D/g, '');
  if (digits.startsWith('00225')) digits = digits.slice(5);
  else if (digits.startsWith('225') && digits.length === 13) digits = digits.slice(3);
  return /^(01|05|07|21|25|27)\d{8}$/.test(digits) ? digits : null;
}

export function validateContact(f: Pick<CheckoutForm, 'nom' | 'telephone'>): FieldErrors {
  const errors: FieldErrors = {};
  const nom = f.nom.trim();
  if (nom.length < 2) errors.nom = 'Indiquez votre nom pour que le coursier vous trouve.';
  else if (nom.length > 80) errors.nom = 'Le nom est trop long (80 caractères maximum).';
  if (!normalizePhoneCI(f.telephone)) errors.telephone = 'Numéro ivoirien à 10 chiffres attendu, par exemple 07 00 00 00 00.';
  return errors;
}

export function validateDelivery(f: Pick<CheckoutForm, 'commune' | 'adresse'>): FieldErrors {
  const errors: FieldErrors = {};
  if (!(COMMUNES as readonly string[]).includes(f.commune)) errors.commune = 'Choisissez votre commune dans la liste.';
  const adresse = f.adresse.trim();
  if (adresse.length < 3) errors.adresse = 'Un quartier ou un repère aide le coursier, par exemple « Angré 8e tranche ».';
  else if (adresse.length > 160) errors.adresse = 'Adresse trop longue (160 caractères maximum).';
  return errors;
}

export function orderNumber(now: number = Date.now()): string {
  return `ELSI-${now.toString(36).toUpperCase().slice(-6)}`;
}
