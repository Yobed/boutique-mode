'use client';

import { useRef, useState } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { AnimatePresence, motion } from 'motion/react';
import type { Article } from '@/lib/types';
import { formatFCFA } from '@/lib/config';
import { isSheetPhoto } from '@/lib/models3d';
import Badges from '@/components/product/Badges';
import FavoriteButton from '@/components/product/FavoriteButton';
import VariantSelector from '@/components/product/VariantSelector';
import AddToCartButton from '@/components/product/AddToCartButton';
import Tilt from '@/components/fx/Tilt';

interface Props {
  article: Article;
  priority?: boolean;
  /** Distinguishes two cards of the same article on one page (layoutId scope). */
  groupKey?: string;
  sizes?: string;
}

export default function ProductCard({
  article,
  priority = false,
  groupKey = 'grid',
  sizes = '(min-width: 1280px) 25vw, (min-width: 768px) 33vw, 50vw',
}: Props) {
  const [taille, setTaille] = useState(article.tailles[0] ?? 'Unique');
  const [picking, setPicking] = useState(false);
  const couleur = article.couleurs[0] ?? 'Unique';
  const plateRef = useRef<HTMLDivElement>(null);
  const href = `/article/${article.id}`;
  const second = article.photos.slice(1).find((src) => !isSheetPhoto(src)); // pas de planche en survol de vignette
  const multiSize = article.tailles.length > 1;
  const soldOut = !article.en_stock || article.quantite_stock <= 0;

  return (
    <article className="group relative">
      {/* The stone plate: the photograph is mounted, never bled to the edge. */}
      <Tilt>
      <div className="plate transition-colors duration-ui ease-silk group-hover:bg-stone-deep">
      <div ref={plateRef} className="relative aspect-[3/4] overflow-hidden [background-color:inherit]">
        {/* Every layer between the plate and the photo inherits the stone so the packshot's white melts into it. */}
        <Link href={href} aria-label={article.nom} className="tilt-depth absolute inset-0 z-10 block [background-color:inherit]">
          <Image
            src={article.photos[0]}
            alt={article.nom}
            fill
            sizes={sizes}
            priority={priority}
            className={`object-contain p-[9%] mix-blend-multiply transition-[transform,opacity] duration-[900ms] ease-silk group-hover:scale-[1.06] ${second ? 'md:group-hover:opacity-0' : ''} ${soldOut ? 'grayscale-[0.6]' : ''}`}
          />
          {second && (
            <Image
              src={second}
              alt=""
              fill
              sizes={sizes}
              className="hidden object-contain p-[9%] opacity-0 mix-blend-multiply transition-opacity duration-[700ms] ease-silk md:block md:group-hover:opacity-100"
            />
          )}
        </Link>

        <Badges article={article} className="pointer-events-none absolute left-3 top-3" />
        <FavoriteButton id={article.id} nom={article.nom} className="absolute right-1 top-1" />

        {/* Desktop quick-add: rises from the hem of the image on hover / keyboard focus */}
        <div className="absolute inset-x-0 bottom-0 hidden translate-y-full bg-ink-950/90 p-3 opacity-0 transition-[transform,opacity] duration-ui ease-silk group-focus-within:translate-y-0 group-focus-within:opacity-100 group-hover:translate-y-0 group-hover:opacity-100 md:block">
          {multiSize && !soldOut && (
            <div className="mb-2.5">
              <VariantSelector label={`Taille pour ${article.nom}`} options={article.tailles} value={taille} onChange={setTaille} groupId={`${groupKey}-${article.id}-d`} size="sm" />
            </div>
          )}
          <AddToCartButton article={article} taille={taille} couleur={couleur} sourceRef={plateRef} />
        </div>
      </div>
      </div>
      </Tilt>

      <div className="mt-4 flex items-start justify-between gap-3">
        <h3 className="text-display text-[18px] leading-[1.15] md:text-[21px]">
          <Link href={href} className="transition-colors hover:text-indigo">
            {article.nom}
          </Link>
        </h3>
        <p className="tabular shrink-0 pt-0.5 text-right text-sm">
          {article.prix_promo ? (
            <>
              <span className="block text-ivory">{formatFCFA(article.prix_promo)}</span>
              <s className="text-xs text-zinc-500">{formatFCFA(article.prix)}</s>
            </>
          ) : (
            <span className="text-ivory">{formatFCFA(article.prix)}</span>
          )}
        </p>
      </div>
      {article.couleurs.length > 1 && <p className="mt-1 text-xs text-zinc-500">{article.couleurs.length} coloris</p>}

      {/* Mobile: one tap reveals sizes, the second adds. Never hidden behind hover. */}
      <div className="mt-3 md:hidden">
        {multiSize && !picking && !soldOut ? (
          <button
            type="button"
            onClick={() => setPicking(true)}
            aria-expanded={false}
            className="h-11 w-full border border-ivory/20 text-[12px] uppercase tracking-label text-zinc-200 active:bg-ivory/5"
          >
            Choisir ma taille
          </button>
        ) : (
          <AnimatePresence initial={false}>
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
              className="space-y-2"
            >
              {multiSize && !soldOut && (
                <VariantSelector label={`Taille pour ${article.nom}`} options={article.tailles} value={taille} onChange={setTaille} groupId={`${groupKey}-${article.id}-m`} size="sm" />
              )}
              <AddToCartButton article={article} taille={taille} couleur={couleur} sourceRef={plateRef} />
            </motion.div>
          </AnimatePresence>
        )}
      </div>
    </article>
  );
}
