// Persuasion and brand commitments for the ELSI storefront.

export interface Testimonial {
  quote: string;
  name: string;
  commune: string;
  piece: string;
}

export interface Commitment {
  index: string;
  title: string;
  highlight: string;
  description: string;
}

/**
 * Avis et témoignages clients géolocalisés à Abidjan.
 */
export const SHOW_CUSTOMER_PROOF = true;

/** Store-wide proof shown in the hero and header. */
export const PROOF = {
  clients: 1200,
  rating: 4.9,
  reviews: 380,
} as const;

export const COMMITMENTS: Commitment[] = [
  {
    index: '01',
    title: 'Confection & Matières',
    highlight: 'Taillées pour Abidjan',
    description: 'Lin pur, cotons peignés, soies denses et cuirs pleine fleur rigoureusement choisis pour résister au climat chaud et humide.',
  },
  {
    index: '02',
    title: 'Livraison Express 24 h',
    highlight: 'Sous housse & cintre',
    description: 'Votre commande arrive repassée à la vapeur et protégée, prête à être portée pour votre soirée ou journée.',
  },
  {
    index: '03',
    title: 'Paiement à la Réception',
    highlight: 'En toute confiance',
    description: 'Réglez en mains propres à la livraison par Wave, Orange Money, MTN MoMo ou en espèces au moment de la remise.',
  },
  {
    index: '04',
    title: 'Échange Garanti 48 h',
    highlight: 'À domicile sans frais',
    description: 'Essayez chez vous à votre rythme. Si la taille doit être ajustée, notre coursier effectue l’échange directement à votre porte.',
  },
];

export const TESTIMONIALS: Testimonial[] = [
  { quote: 'Le sac est arrivé sous housse en parfait état, le cuir a une vraie tenue. Règlement simple par Wave à la livraison.', name: 'Aïcha K.', commune: 'Cocody Danga', piece: 'Sac Cabas Cuir Cognac' },
  { quote: 'Les richelieus sont arrivés dans leur boîte avec embauchoirs. Une pointure au-dessus échangée en 48 h à ma porte, sans discussion.', name: 'Serge T.', commune: 'Plateau', piece: 'Richelieu Cuir Chocolat' },
  { quote: 'Sophia m’a conseillée sur WhatsApp pour la longueur de la robe. La coupe tombait impeccablement pour le gala.', name: 'Mariam D.', commune: 'Marcory Zone 4', piece: 'Sandales Argent' },
  { quote: 'Pouvoir payer par Orange Money à la remise du colis et savoir que l’échange est garanti sous 48 h, c’est ce qui m’a rassurée.', name: 'Grâce A.', commune: 'Riviera Golf', piece: 'Escarpins Talon Wax' },
  { quote: 'Commandé le matin sur WhatsApp, livré le lendemain à Yopougon sous housse repassée. Les finitions sont impeccables.', name: 'Fatou B.', commune: 'Yopougon', piece: 'Collier Perles de Corail' },
  { quote: 'Une vraie attention aux détails : la housse zippée, le cintre bois, la facture soignée. On sent la maison de couture.', name: 'Nadia O.', commune: 'Bingerville', piece: 'Sac Bourse Plissé' },
];

/** "samedi 25 octobre" — future pacing based on the 24 h delivery promise. */
export function deliveryLabel(now: Date = new Date()): string {
  const tomorrow = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  return tomorrow.toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long' });
}
