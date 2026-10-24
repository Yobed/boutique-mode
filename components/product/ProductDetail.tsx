'use client';

import { useEffect, useRef, useState } from 'react';
import Link from 'next/link';
import { AnimatePresence, motion } from 'motion/react';
import type { Article } from '@/lib/types';
import { formatFCFA, waLink } from '@/lib/config';
import { deliveryLabel } from '@/lib/marketing';
import { unitPrice } from '@/lib/cart.ts';
import { useStore } from '@/lib/store-context';
import ProductGallery from '@/components/product/ProductGallery';
import VariantSelector from '@/components/product/VariantSelector';
import AddToCartButton from '@/components/product/AddToCartButton';
import FavoriteButton from '@/components/product/FavoriteButton';
import Badges from '@/components/product/Badges';
import ProductCard from '@/components/ProductCard';
import SizeGuideModal from '@/components/SizeGuideModal';

const PROMISES = [
  ['Livrée sous housse en 24 h', 'Repassée avec soin dans notre atelier d’Abidjan, prête à être portée dès réception.'],
  ['Paiement à la réception', 'Espèces, Wave, Orange Money ou MTN MoMo lors de la remise en main propre.'],
  ['Échange garanti sous 48 h', 'Essayez tranquillement chez vous. Si la taille ne convient pas, nous l’échangeons à domicile sans frais.'],
] as const;

export default function ProductDetail({ article, related }: { article: Article; related: Article[] }) {
  const { setStylistOpen } = useStore();
  const [taille, setTaille] = useState(article.tailles[0] ?? 'Unique');
  const [couleur, setCouleur] = useState(article.couleurs[0] ?? 'Unique');
  const [guideOpen, setGuideOpen] = useState(false);
  const [showSticky, setShowSticky] = useState(false);
  const plateRef = useRef<HTMLDivElement>(null);
  const buyRef = useRef<HTMLDivElement>(null);
  const soldOut = !article.en_stock || article.quantite_stock <= 0;
  const saving = article.prix_promo ? article.prix - article.prix_promo : 0;
  // Computed on the client: server and visitor may sit in different time zones.
  const [delivery, setDelivery] = useState('');
  useEffect(() => setDelivery(deliveryLabel()), []);

  // Mobile buy bar appears only once the main button has scrolled away.
  useEffect(() => {
    const el = buyRef.current;
    if (!el) return;
    const io = new IntersectionObserver(([entry]) => setShowSticky(!entry.isIntersecting && entry.boundingClientRect.top < 0), { threshold: 0 });
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const waText = `Bonjour ELSI, je souhaite commander « ${article.nom} » — taille ${taille}, coloris ${couleur} (${formatFCFA(unitPrice(article))}). Est-ce disponible pour une livraison ?`;

  return (
    <>
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)] pb-24 pt-6 md:pt-10">
        <nav aria-label="Fil d’Ariane" className="mb-6 text-xs text-zinc-500">
          <ol className="flex flex-wrap gap-2">
            <li>
              <Link href="/" className="hover:text-ivory">Accueil</Link>
            </li>
            <li aria-hidden>/</li>
            <li>
              <Link href={`/catalogue?categorie=${article.categorie}`} className="capitalize hover:text-ivory">
                {article.categorie}
              </Link>
            </li>
            <li aria-hidden>/</li>
            <li aria-current="page" className="text-zinc-300">
              {article.nom}
            </li>
          </ol>
        </nav>

        <div className="grid gap-10 lg:grid-cols-[minmax(0,1.25fr)_minmax(0,1fr)] lg:gap-16">
          <ProductGallery
            photos={article.photos}
            nom={article.nom}
            plateRef={plateRef}
            modele_3d={article.modele_3d}
            selectedColor={couleur}
          />

          <div className="lg:sticky lg:top-[calc(var(--header-h)+24px)] lg:self-start lg:pt-4">
            <div className="flex items-start justify-between gap-4">
              <h1 className="text-display text-[clamp(2.2rem,1.4rem+2.6vw,3.6rem)] leading-[1.02]">{article.nom}</h1>
              <FavoriteButton id={article.id} nom={article.nom} className="-mr-3 shrink-0" />
            </div>
            <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-2">
              <p className="tabular flex items-baseline gap-3 text-xl">
                <span>{formatFCFA(unitPrice(article))}</span>
                {article.prix_promo && <s className="text-sm text-zinc-500">{formatFCFA(article.prix)}</s>}
              </p>
              <Badges article={article} className="!flex-row" />
            </div>
            {saving > 0 && <p className="tabular mt-2 text-sm text-ember-300">Vous économisez {formatFCFA(saving)}</p>}
            <p className="mt-6 max-w-[58ch] leading-relaxed text-zinc-300">{article.description}</p>

            <div className="mt-10 space-y-7 border-t border-ivory/[0.08] pt-8">
              {article.tailles.length > 1 && (
              <div>
                <div className="mb-3 flex items-baseline justify-between">
                  <p className="text-[11px] uppercase tracking-label text-zinc-400">
                    Taille · <span className="text-ivory">{taille}</span>
                  </p>
                  <button type="button" onClick={() => setGuideOpen(true)} className="link-draw py-1 text-xs text-brass-300">
                    Guide des tailles
                  </button>
                </div>
                <VariantSelector label="Taille" options={article.tailles} value={taille} onChange={setTaille} groupId={`pdp-taille-${article.id}`} />
              </div>
              )}

              {article.couleurs.length > 1 && (
                <div>
                  <p className="mb-3 text-[11px] uppercase tracking-label text-zinc-400">
                    Coloris · <span className="text-ivory">{couleur}</span>
                  </p>
                  <VariantSelector label="Coloris" options={article.couleurs} value={couleur} onChange={setCouleur} groupId={`pdp-couleur-${article.id}`} />
                </div>
              )}

              <div ref={buyRef} className="space-y-3">
                {!soldOut && (
                  <ul className="space-y-1.5 text-sm">
                    <li className="flex items-center gap-2.5 text-zinc-300">
                      <span aria-hidden className="h-2 w-2 rounded-full bg-emerald-400" />
                      <span>Confectionné & disponible à l'atelier d'Abidjan</span>
                    </li>
                    {delivery && (
                      <li className="flex items-center gap-2.5 text-zinc-300">
                        <span aria-hidden className="h-2 w-2 rounded-full bg-brass-400" />
                        <span>
                          Livraison à Abidjan dès demain, <span className="text-ivory">{delivery}</span>
                        </span>
                      </li>
                    )}
                  </ul>
                )}
                <AddToCartButton article={article} taille={taille} couleur={couleur} sourceRef={plateRef} variant="full" />
                <a
                  href={waLink(waText)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-14 w-full items-center justify-center border border-emerald-500/50 text-[13px] uppercase tracking-label text-emerald-200 transition-colors hover:border-emerald-300 hover:bg-emerald-950/60"
                >
                  Commander sur WhatsApp
                </a>
                {!soldOut && (
                  <p className="text-xs leading-relaxed text-zinc-400">
                    <span className="text-emerald-300">Paiement sécurisé à la réception :</span> vous réglez à la remise de votre commande (espèces, Wave, Orange Money ou MTN MoMo). Échange de taille garanti sous 48 h.
                  </p>
                )}
              </div>
            </div>

            <dl className="mt-10 divide-y divide-ivory/[0.08] border-y border-ivory/[0.08]">
              {PROMISES.map(([t, d]) => (
                <div key={t} className="grid gap-1 py-4 sm:grid-cols-[180px_1fr] sm:gap-6">
                  <dt className="text-sm text-ivory">{t}</dt>
                  <dd className="text-sm leading-relaxed text-zinc-400">{d}</dd>
                </div>
              ))}
            </dl>

            <details className="group border-b border-ivory/[0.08] py-4">
              <summary className="flex cursor-pointer list-none items-center justify-between text-sm text-ivory">
                Matières & entretien
                <span aria-hidden className="text-brass-300 transition-transform duration-ui group-open:rotate-45">
                  +
                </span>
              </summary>
              <p className="mt-3 max-w-[60ch] text-sm leading-relaxed text-zinc-400">
                Fibres nobles selon le modèle : coton peigné, lin, crêpe ou soie. Lavage délicat à 30 °C ou à la main, repassage vapeur sur l’envers. Livré repassé, sous housse et sur cintre en bois.
              </p>
            </details>

            <button type="button" onClick={() => setStylistOpen(true)} className="link-draw mt-6 py-1 text-left text-sm text-brass-300">
              Une hésitation sur la taille ? Demandez à Sophia, notre styliste
            </button>
          </div>
        </div>

        {related.length > 0 && (
          <section aria-labelledby="pieces-liees" className="mt-28">
            <h2 id="pieces-liees" className="text-display mb-10 text-4xl md:text-5xl">
              À porter avec
            </h2>
            <div className="grid grid-cols-2 gap-x-4 gap-y-12 md:grid-cols-4">
              {related.map((a) => (
                <ProductCard key={a.id} article={a} groupKey="related" />
              ))}
            </div>
          </section>
        )}
      </div>

      <AnimatePresence>
        {showSticky && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%', transition: { duration: 0.2, ease: [0.4, 0, 1, 1] } }}
            transition={{ duration: 0.36, ease: [0.16, 1, 0.3, 1] }}
            className="fixed inset-x-0 bottom-0 z-40 flex items-center gap-3 border-t border-ivory/10 bg-ink-950 px-4 py-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] lg:hidden"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm">{article.nom}</p>
              <p className="tabular text-xs text-zinc-400">
                {formatFCFA(unitPrice(article))} · taille {taille}
              </p>
            </div>
            <div className="w-36 shrink-0">
              <AddToCartButton article={article} taille={taille} couleur={couleur} sourceRef={plateRef} />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <SizeGuideModal isOpen={guideOpen} onClose={() => setGuideOpen(false)} onOpenStylist={() => setStylistOpen(true)} />
    </>
  );
}
