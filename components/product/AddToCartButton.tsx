'use client';

import { useEffect, useState } from 'react';
import type { RefObject } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Check } from 'lucide-react';
import type { Article } from '@/lib/types';
import { useStore } from '@/lib/store-context';
import { formatFCFA, waLink } from '@/lib/config';
import { unitPrice } from '@/lib/cart.ts';

interface Props {
  article: Article;
  taille: string;
  couleur: string;
  /** Element whose image flies to the cart. */
  sourceRef?: RefObject<HTMLElement | null>;
  variant?: 'compact' | 'full';
}

const swap = {
  initial: { y: '110%', opacity: 0 },
  animate: { y: 0, opacity: 1 },
  exit: { y: '-110%', opacity: 0 },
  transition: { duration: 0.26, ease: [0.16, 1, 0.3, 1] },
} as const;

export default function AddToCartButton({ article, taille, couleur, sourceRef, variant = 'compact' }: Props) {
  const { add } = useStore();
  const [added, setAdded] = useState(false);
  const soldOut = !article.en_stock || article.quantite_stock <= 0;

  useEffect(() => {
    if (!added) return;
    const t = window.setTimeout(() => setAdded(false), 1800);
    return () => window.clearTimeout(t);
  }, [added]);

  const height = variant === 'full' ? 'h-14 text-[13px]' : 'h-11 text-[12px]';

  if (soldOut) {
    return (
      <a
        href={waLink(`Bonjour ELSI, je souhaite être prévenu(e) du retour de « ${article.nom} » en taille ${taille}.`)}
        target="_blank"
        rel="noopener noreferrer"
        className={`${height.replace('h-', 'min-h-')} flex w-full items-center justify-center border border-ivory/20 px-3 py-2 text-center uppercase leading-tight tracking-label text-zinc-300 transition-colors hover:border-emerald-400 hover:text-emerald-200`}
      >
        {variant === 'full' ? 'Épuisé · être prévenu(e) du retour' : 'Me prévenir'}
        <span className="sr-only">, {article.nom} est épuisé, message WhatsApp</span>
      </a>
    );
  }

  const label = variant === 'full' ? `Ajouter au panier · ${formatFCFA(unitPrice(article))}` : 'Ajouter';

  return (
    <button
      type="button"
      onClick={() => {
        add(article, taille, couleur, sourceRef?.current);
        setAdded(true);
      }}
      // Accessible name starts with the visible text (WCAG 2.5.3, voice control).
      aria-label={added ? `Ajouté, ${article.nom}, taille ${taille}` : `${label}, ${article.nom}, taille ${taille}`}
      className={`${height} relative flex w-full items-center justify-center overflow-hidden px-4 font-medium uppercase tracking-label transition-colors duration-feedback active:scale-[0.985] ${
        added ? 'bg-emerald-600 text-ivory' : 'bg-ivory text-ink-950 hover:bg-brass-300'
      }`}
    >
      <AnimatePresence mode="popLayout" initial={false}>
        {added ? (
          <motion.span key="ok" {...swap} className="flex items-center gap-2">
            <Check className="h-4 w-4" strokeWidth={2.2} /> Ajouté
          </motion.span>
        ) : (
          <motion.span key="add" {...swap} className="tabular">
            {label}
          </motion.span>
        )}
      </AnimatePresence>
    </button>
  );
}
