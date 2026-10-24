'use client';

import Link from 'next/link';
import { AnimatePresence, motion } from 'motion/react';
import { X } from 'lucide-react';
import { useStore } from '@/lib/store-context';
import type { Flight } from '@/lib/store-context';
import { subtotal } from '@/lib/cart.ts';
import { formatFCFA } from '@/lib/config';

const CURTAIN = [0.77, 0, 0.175, 1] as const;
const SILK = [0.16, 1, 0.3, 1] as const;

/**
 * Add-to-cart, in three beats:
 * 1. an exposure flash stays on the card (same light language as the hero),
 * 2. the piece folds into a round fabric swatch and arcs toward the bag,
 * 3. the bag receives it (one brass ring, CSS `.icon-cart`), then the toast offers checkout.
 */
function FlyingPiece({ flight, onLand }: { flight: Flight; onLand: () => void }) {
  const { cartIconRef } = useStore();
  const target = cartIconRef.current?.getBoundingClientRect();
  const { left, top, width, height } = flight.from;
  const dx = target ? target.left + target.width / 2 - (left + width / 2) : 0;
  const dy = target ? target.top + target.height / 2 - (top + height / 2) : 0;
  const endScale = Math.max(28 / Math.min(width, height), 0.05);
  const frame = { left, top, width, height };

  return (
    <>
      <motion.img
        src={flight.src}
        alt=""
        aria-hidden
        className="pointer-events-none fixed z-[89] object-cover"
        style={frame}
        initial={{ opacity: 0.85, filter: 'brightness(1.9)' }}
        animate={{ opacity: 0, filter: 'brightness(1)' }}
        transition={{ duration: 0.7, ease: SILK }}
      />
      <motion.img
        src={flight.src}
        alt=""
        aria-hidden
        className="pointer-events-none fixed z-[90] object-cover shadow-lift"
        style={{ ...frame, transformOrigin: 'center' }}
        initial={{ x: 0, y: 0, scale: 1, rotate: 0, clipPath: 'inset(0% 0% 0% 0% round 0px)' }}
        animate={{
          x: [0, 0, dx * 0.35, dx],
          y: [0, -14, dy * 0.35 - 90, dy],
          scale: [1, 0.92, 0.42, endScale],
          rotate: [0, 0, -7, 0],
          clipPath: [
            'inset(0% 0% 0% 0% round 0px)',
            'inset(6% 10% 6% 10% round 2px)',
            'inset(24% 18% 24% 18% round 40px)',
            'inset(30% 30% 30% 30% round 999px)',
          ],
        }}
        transition={{ duration: 0.92, ease: CURTAIN, times: [0, 0.16, 0.55, 1] }}
        onAnimationComplete={onLand}
      />
    </>
  );
}

export default function CartFeedback() {
  const { flights, landFlight, lastAdded, dismissLastAdded, items, openCart } = useStore();

  return (
    <>
      {flights.map((f) => (
        <FlyingPiece key={f.id} flight={f} onLand={() => landFlight(f.id)} />
      ))}

      <div
        aria-live="polite"
        role="status"
        className="pointer-events-none fixed inset-x-0 top-[calc(var(--header-h)+8px)] z-[60] flex justify-end px-[var(--gutter)]"
      >
        <AnimatePresence>
          {lastAdded && (
            <motion.div
              key={lastAdded.id}
              initial={{ opacity: 0, y: -10, clipPath: 'inset(0% 0% 100% 0%)' }}
              animate={{ opacity: 1, y: 0, clipPath: 'inset(0% 0% 0% 0%)' }}
              exit={{ opacity: 0, y: -6, transition: { duration: 0.18, ease: [0.4, 0, 1, 1] } }}
              transition={{ duration: 0.36, ease: SILK, delay: 0.7 }}
              className="pointer-events-auto flex w-full max-w-[440px] gap-4 border border-ivory/10 bg-ink-900 p-3 shadow-lift"
            >
              {lastAdded.photo && (
                // eslint-disable-next-line @next/next/no-img-element -- already decoded: same URL the card just showed
                <img src={lastAdded.photo} alt="" className="h-20 w-16 shrink-0 bg-stone object-contain p-1 mix-blend-multiply" />
              )}
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <p className="min-w-0 text-sm leading-snug">
                    <span className="block truncate text-ivory">{lastAdded.nom}</span>
                    <span className="text-zinc-400">Taille {lastAdded.taille} · dans votre panier</span>
                  </p>
                  <button type="button" onClick={dismissLastAdded} aria-label="Fermer la notification" className="-m-2 grid h-11 w-11 shrink-0 place-items-center text-zinc-500 hover:text-ivory">
                    <X className="h-4 w-4" />
                  </button>
                </div>
                <div className="mt-2 flex items-center gap-4">
                  <Link href="/commande" onClick={dismissLastAdded} className="tabular whitespace-nowrap bg-ivory px-4 py-2.5 text-[11px] font-medium uppercase tracking-label text-ink-950 hover:bg-brass-300">
                    Commander · {formatFCFA(subtotal(items))}
                  </Link>
                  <button type="button" onClick={openCart} className="link-draw whitespace-nowrap py-2 text-xs text-zinc-300">
                    Voir le panier
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </>
  );
}
