'use client';

import { useRef } from 'react';
import Link from 'next/link';
import { ArrowLeft, MessageCircle, Sparkles } from 'lucide-react';
import ProductGallery from '@/components/product/ProductGallery';
import type { Article } from '@/lib/types';

const WHATSAPP_PHONE = '2250574243752';

export default function Showroom3DClient({ article }: { article: Article }) {
  const plateRef = useRef<HTMLDivElement>(null);
  const referenceColor = article.modele_3d?.variantColor ?? article.couleurs[0] ?? 'Unique';
  const price = article.prix_promo ?? article.prix;
  const formattedPrice = new Intl.NumberFormat('fr-FR').format(price);
  const whatsappMessage = encodeURIComponent(
    'Bonjour ELSI, je souhaite des informations sur ' +
      article.nom +
      ' (' +
      referenceColor +
      '), au prix affiché de ' +
      formattedPrice +
      ' FCFA.'
  );
  const whatsappUrl = 'https://wa.me/' + WHATSAPP_PHONE + '?text=' + whatsappMessage;

  return (
    <main className="min-h-screen bg-ink-950 pb-24 pt-6 text-linen-100">
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
        <nav aria-label="Navigation" className="mb-8 border-b border-white/10 pb-4">
          <Link href="/" className="group inline-flex items-center gap-2 text-xs text-zinc-400 transition-colors hover:text-brass-300">
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            Retour à l’accueil
          </Link>
        </nav>

        <div className="grid items-start gap-10 lg:grid-cols-12 lg:gap-14">
          <section aria-label={'Photos et vue 3D de ' + article.nom} className="lg:col-span-7">
            <ProductGallery
              photos={article.photos}
              nom={article.nom}
              plateRef={plateRef}
              modele_3d={article.modele_3d}
              selectedColor={referenceColor}
            />
          </section>

          <section className="space-y-6 lg:sticky lg:top-24 lg:col-span-5">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-brass-400/30 bg-brass-400/10 px-3 py-1 text-xs text-brass-300">
                <Sparkles className="h-3.5 w-3.5" />
                Studio produit
              </div>
              <h1 className="text-display text-3xl leading-tight tracking-tight sm:text-4xl">{article.nom}</h1>
              <p className="mt-4 font-serif text-2xl text-brass-400">{formattedPrice} FCFA</p>
              <p className="mt-4 leading-relaxed text-zinc-300">{article.description}</p>
            </div>

            <dl className="grid gap-3 border-y border-white/10 py-5 text-sm sm:grid-cols-2">
              <div>
                <dt className="text-xs uppercase tracking-wider text-zinc-500">Coloris au catalogue</dt>
                <dd className="mt-1 text-zinc-200">{article.couleurs.join(' · ') || 'Unique'}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wider text-zinc-500">Tailles au catalogue</dt>
                <dd className="mt-1 text-zinc-200">{article.tailles.join(' · ') || 'Unique'}</dd>
              </div>
            </dl>

            <p role="status" className="border-l-2 border-brass-400/60 pl-4 text-sm leading-relaxed text-zinc-400">
              {article.modele_3d
                ? 'Modèle 3D validé pour le coloris ' + article.modele_3d.variantColor + '.'
                : 'La vue 3D reste masquée tant que sa fidélité au produit physique n’a pas été vérifiée. Les photos du catalogue restent visibles.'}
            </p>

            <div className="space-y-3">
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex w-full items-center justify-center gap-3 rounded-full bg-[#25D366] px-6 py-4 text-sm font-semibold text-white transition-colors hover:bg-[#20ba59]"
              >
                <MessageCircle className="h-5 w-5" />
                Demander la disponibilité sur WhatsApp
              </a>
              <Link
                href={'/article/' + article.id}
                className="flex w-full items-center justify-center rounded-full border border-brass-400/40 bg-ink-900 px-6 py-3.5 text-center text-sm font-serif text-brass-300 transition-colors hover:bg-brass-400 hover:text-ink-950"
              >
                Voir la fiche catalogue complète
              </Link>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
