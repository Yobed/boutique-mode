'use client';

import { useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import type { Article } from '@/lib/types';
import ProductCard from '@/components/ProductCard';
import { gsap, MQ, useGSAP } from '@/lib/gsap';

const U = (id: string, w = 1400) => `https://images.unsplash.com/photo-${id}?w=${w}&auto=format&fit=crop&q=80`;

const ROWS = [
  {
    img: U('1497997092403-f091fcf5b6c4', 1000),
    alt: 'Pied-de-biche d’une machine à coudre sur une étoffe sombre, fil tendu',
    titre: 'La matière d’abord',
    texte: 'Cuirs pleine fleur, lin, cotons peignés : des matières choisies pour la chaleur d’Abidjan, qui tiennent dans le temps.',
  },
  {
    img: U('1768212565424-efa3a3852b81', 1000),
    alt: 'Pile de wax aux motifs vifs, étiquettes encore attachées',
    titre: 'Le wax, au mètre',
    texte: 'Nos pièces en wax sont coupées dans des tissus sélectionnés un à un, puis doublées pour durer.',
  },
];

/**
 * Scene 3 — the pieces, as a gallery grid: no scroll hijacking, the cards rise in a cascade as the
 * grid enters. Scene 4 — savoir-faire on stone, its photograph in parallax, rows unveiling once.
 */
export default function SceneCollectionSavoir({ articles, total }: { articles: Article[]; total: number }) {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        gsap.fromTo(
          '[data-card]',
          { y: 120, rotationX: -55, z: -200, opacity: 0, transformPerspective: 1000, transformOrigin: '50% 100%' },
          { y: 0, rotationX: 0, z: 0, opacity: 1, duration: 1.5, ease: 'expo.out', stagger: { each: 0.09, grid: 'auto' }, scrollTrigger: { trigger: '[data-grid]', start: 'top 85%' } }
        );
        gsap.fromTo('[data-savoir-img]', { yPercent: -12, scale: 1.25 }, { yPercent: 12, scale: 1, ease: 'none', scrollTrigger: { trigger: '[data-savoir]', start: 'top bottom', end: 'bottom top', scrub: true } });
        gsap.utils.toArray<HTMLElement>('[data-row]').forEach((row) => {
          gsap
            .timeline({ scrollTrigger: { trigger: row, start: 'top 80%' } })
            .fromTo(row.querySelector('[data-row-img]'), { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.3, ease: 'expo.out' })
            .fromTo(row.querySelector('[data-row-img] img'), { scale: 1.5 }, { scale: 1, duration: 2, ease: 'expo.out' }, 0)
            .fromTo(row.querySelectorAll('[data-row-text] > *'), { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: 0.9, ease: 'expo.out', stagger: 0.07 }, 0.3);
        });
        gsap.utils.toArray<HTMLElement>('[data-row-img]').forEach((frame) => {
          gsap.fromTo(frame, { yPercent: 12 }, { yPercent: -12, ease: 'none', scrollTrigger: { trigger: frame, start: 'top bottom', end: 'bottom top', scrub: 0.6 } });
        });
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <div ref={root}>
      {/* Scene 3 — the pieces */}
      <section aria-labelledby="collection-titre" className="bg-paper pb-[var(--section)]">
        <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
          <div className="mb-12 flex flex-col justify-between gap-6 lg:mb-16 lg:flex-row lg:items-end">
            <h2 id="collection-titre" className="text-display text-[clamp(2.6rem,1.6rem+3.4vw,5.4rem)] leading-[0.95]">
              Les pièces <em className="text-indigo">du moment</em>
            </h2>
            <Link href="/catalogue" className="link-draw self-start py-1 text-sm lg:self-auto">
              Voir les {total} articles →
            </Link>
          </div>
          <ul data-grid aria-label="Pièces du moment" className="grid grid-cols-2 gap-x-3 gap-y-12 sm:gap-x-5 lg:grid-cols-4">
            {articles.map((a, i) => (
              <li key={a.id} data-card>
                <ProductCard article={a} groupKey="collection" sizes="(min-width: 1024px) 24vw, 48vw" priority={i < 2} />
              </li>
            ))}
          </ul>
        </div>
      </section>

      {/* Scene 4 — savoir-faire, on stone */}
      <section data-savoir aria-labelledby="savoir-titre" className="relative bg-stone pb-[var(--section)]">
        <div className="mx-auto max-w-[1440px] px-[var(--gutter)] pt-[var(--section)]">
          <div className="grid gap-12 lg:grid-cols-12 lg:gap-8">
            <div className="lg:col-span-5 lg:pt-[6vh]">
              <h2 id="savoir-titre" className="text-display text-[clamp(2.6rem,1.6rem+3.4vw,5.4rem)] leading-[0.95]">
                Le geste <em className="text-indigo">avant la pièce.</em>
              </h2>
              <p className="mt-8 max-w-[42ch] text-[17px] leading-relaxed text-mute-400">
                Avant d’arriver chez vous, chaque article passe entre les mains de l’atelier : contrôle des coutures et des finitions, ajustement si besoin, emballage soigné.
              </p>
            </div>
            <div className="relative aspect-[4/3] overflow-hidden bg-stone-deep lg:col-span-7">
              <div data-savoir-img className="absolute inset-x-0 -inset-y-[22%]">
                <Image src={U('1718184021018-d2158af6b321')} alt="Mains d’un tailleur coupant une étoffe sombre aux ciseaux, mètre ruban posé à côté" fill sizes="(min-width: 1024px) 56vw, 100vw" className="object-cover" />
              </div>
            </div>
          </div>

          <div className="mt-[var(--section)] space-y-[clamp(4rem,8vw,9rem)]">
            {ROWS.map((row, i) => (
              <article key={row.titre} data-row className="grid items-center gap-8 lg:grid-cols-12">
                <div data-row-img className={`relative aspect-[4/5] overflow-hidden bg-stone-deep lg:col-span-5 lg:row-start-1 ${i % 2 ? 'lg:col-start-8' : 'lg:col-start-2'}`}>
                  <Image src={row.img} alt={row.alt} fill sizes="(min-width: 1024px) 40vw, 100vw" className="object-cover" />
                </div>
                <div data-row-text className={`lg:col-span-4 lg:row-start-1 ${i % 2 ? 'lg:col-start-2' : 'lg:col-start-8'}`}>
                  <h3 className="text-display text-[clamp(2rem,1.4rem+1.8vw,3.2rem)] leading-tight">{row.titre}</h3>
                  <p className="mt-5 max-w-[38ch] leading-relaxed text-mute-400">{row.texte}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
