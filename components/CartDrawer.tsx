'use client';

import { useEffect, useRef } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { AnimatePresence, motion } from 'motion/react';
import { Minus, Plus, X } from 'lucide-react';
import { useStore } from '@/lib/store-context';
import { subtotal, unitPrice } from '@/lib/cart.ts';
import { FREE_DELIVERY_THRESHOLD, formatFCFA } from '@/lib/config';

const SILK = [0.16, 1, 0.3, 1] as const;

export default function CartDrawer() {
  const { items, count, cartOpen, closeCart, setQty, remove } = useStore();
  const panelRef = useRef<HTMLDivElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);
  const total = subtotal(items);
  const remaining = Math.max(FREE_DELIVERY_THRESHOLD - total, 0);
  const progress = Math.min(total / FREE_DELIVERY_THRESHOLD, 1);

  useEffect(() => {
    if (!cartOpen) return;
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const { overflow } = document.body.style;
    document.body.style.overflow = 'hidden';

    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeCart();
      if (e.key !== 'Tab' || !panelRef.current) return;
      const focusable = panelRef.current.querySelectorAll<HTMLElement>('a[href], button:not([disabled]), input');
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last?.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = overflow;
      window.removeEventListener('keydown', onKey);
      previous?.focus();
    };
  }, [cartOpen, closeCart]);

  return (
    <AnimatePresence>
      {cartOpen && (
        <div className="fixed inset-0 z-[70]">
          <motion.div
            className="absolute inset-0 bg-ink-950/70"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            onClick={closeCart}
            aria-hidden
          />
          <motion.div
            ref={panelRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="panier-titre"
            className="absolute inset-y-0 right-0 flex w-full max-w-[440px] flex-col bg-ink-900 shadow-drawer"
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%', transition: { duration: 0.26, ease: [0.4, 0, 1, 1] } }}
            transition={{ duration: 0.42, ease: SILK }}
          >
            <header className="flex items-center justify-between border-b border-ivory/[0.07] px-6 py-5">
              <h2 id="panier-titre" className="text-display text-2xl">
                Votre panier <span className="tabular font-sans text-sm text-zinc-500">({count})</span>
              </h2>
              <button ref={closeRef} type="button" onClick={closeCart} aria-label="Fermer le panier" className="-mr-2 grid h-11 w-11 place-items-center text-zinc-400 hover:text-ivory">
                <X className="h-5 w-5" />
              </button>
            </header>

            {items.length === 0 ? (
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.15, duration: 0.4, ease: SILK }}
                className="flex flex-1 flex-col items-center justify-center gap-5 px-8 text-center"
              >
                <p className="text-display text-3xl text-zinc-200">Rien encore.</p>
                <p className="max-w-[26ch] text-sm text-zinc-400">Les pièces que vous ajoutez se rangent ici, le temps de vous décider.</p>
                <Link href="/catalogue" onClick={closeCart} className="mt-2 bg-brass-400 px-7 py-3.5 text-xs font-medium uppercase tracking-label text-ink-950 transition-colors hover:bg-brass-300">
                  Voir la collection
                </Link>
              </motion.div>
            ) : (
              <>
                <div className="border-b border-ivory/[0.07] px-6 py-4">
                  <p className="text-xs text-zinc-300" aria-live="polite">
                    {remaining > 0 ? (
                      <>Encore <span className="tabular text-brass-300">{formatFCFA(remaining)}</span> pour la livraison offerte</>
                    ) : (
                      <span className="text-emerald-300">Livraison offerte sur cette commande</span>
                    )}
                  </p>
                  <div className="mt-2.5 h-px bg-ivory/10" aria-hidden>
                    <motion.div className="h-px origin-left bg-brass-400" initial={false} animate={{ scaleX: progress }} transition={{ duration: 0.6, ease: SILK }} />
                  </div>
                </div>

                <ul className="flex-1 overflow-y-auto px-6">
                  <AnimatePresence initial={false}>
                    {items.map((item, idx) => (
                      <motion.li
                        key={`${item.article.id}-${item.taille}-${item.couleur}`}
                        layout
                        initial={{ opacity: 0, x: 24 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 40, transition: { duration: 0.22, ease: [0.4, 0, 1, 1] } }}
                        transition={{ duration: 0.36, ease: SILK }}
                        className="flex gap-4 border-b border-ivory/[0.06] py-5"
                      >
                        <div className="relative h-28 w-[84px] shrink-0 overflow-hidden bg-ink-800">
                          {item.article.photos[0] && <Image src={item.article.photos[0]} alt="" fill sizes="84px" className="object-contain p-1.5 mix-blend-multiply" />}
                        </div>
                        <div className="flex min-w-0 flex-1 flex-col">
                          <Link href={`/article/${item.article.id}`} onClick={closeCart} className="text-display text-[17px] leading-snug hover:text-brass-200">
                            {item.article.nom}
                          </Link>
                          <p className="mt-1 text-xs text-zinc-400">
                            {item.taille} · {item.couleur}
                          </p>
                          <div className="mt-auto flex items-center justify-between pt-3">
                            <div className="flex items-center border border-ivory/15">
                              <button type="button" onClick={() => setQty(idx, item.quantite - 1)} aria-label={`Retirer un exemplaire de ${item.article.nom}`} className="grid h-9 w-9 place-items-center text-zinc-300 hover:text-ivory">
                                <Minus className="h-3.5 w-3.5" />
                              </button>
                              <span className="tabular w-7 text-center text-sm" aria-label={`Quantité ${item.quantite}`}>
                                {item.quantite}
                              </span>
                              <button
                                type="button"
                                onClick={() => setQty(idx, item.quantite + 1)}
                                disabled={item.quantite >= item.article.quantite_stock}
                                aria-label={`Ajouter un exemplaire de ${item.article.nom}`}
                                className="grid h-9 w-9 place-items-center text-zinc-300 hover:text-ivory disabled:cursor-not-allowed disabled:opacity-30"
                              >
                                <Plus className="h-3.5 w-3.5" />
                              </button>
                            </div>
                            <p className="tabular text-sm text-ivory">{formatFCFA(unitPrice(item.article) * item.quantite)}</p>
                          </div>
                          <button type="button" onClick={() => remove(idx)} className="mt-1 self-start py-2.5 text-[11px] uppercase tracking-label text-zinc-500 hover:text-ember-300">
                            Retirer
                          </button>
                        </div>
                      </motion.li>
                    ))}
                  </AnimatePresence>
                </ul>

                <footer className="space-y-4 border-t border-ivory/[0.07] bg-ink-950/60 px-6 py-5">
                  <div className="flex items-baseline justify-between">
                    <span className="text-sm text-zinc-300">Sous-total</span>
                    <motion.span key={total} initial={{ opacity: 0.4, y: -4 }} animate={{ opacity: 1, y: 0 }} className="tabular text-display text-2xl">
                      {formatFCFA(total)}
                    </motion.span>
                  </div>
                  <p className="text-xs leading-relaxed text-zinc-400">
                    <span className="text-emerald-300">Rien à payer maintenant.</span> Vous essayez à la livraison et ne réglez que ce que vous gardez. Frais de livraison selon votre commune à l’étape suivante.
                  </p>
                  <Link
                    href="/commande"
                    onClick={closeCart}
                    className="block bg-brass-400 py-4 text-center text-[13px] font-medium uppercase tracking-label text-ink-950 transition-colors duration-feedback hover:bg-brass-300 active:scale-[0.99]"
                  >
                    Passer commande
                  </Link>
                  <button type="button" onClick={closeCart} className="w-full py-1 text-xs uppercase tracking-label text-zinc-400 hover:text-ivory">
                    Continuer mes achats
                  </button>
                </footer>
              </>
            )}
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
