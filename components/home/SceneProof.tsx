'use client';

import { useRef } from 'react';
import { COMMITMENTS } from '@/lib/marketing';
import { gsap, MQ, useGSAP } from '@/lib/gsap';

/**
 * Charte d'excellence & engagements réels ELSI.
 * Élimine tout faux compteur au profit d'engagements de service concrets et vérifiables.
 */
export default function SceneProof() {
  const root = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        gsap.fromTo(
          '[data-commitment]',
          { y: 32, opacity: 0 },
          { y: 0, opacity: 1, duration: 0.9, ease: 'silk', stagger: 0.1, scrollTrigger: { trigger: root.current, start: 'top 82%' } }
        );
        gsap.fromTo(
          '[data-stat-rule]',
          { scaleX: 0 },
          { scaleX: 1, duration: 1.4, ease: 'curtain', scrollTrigger: { trigger: root.current, start: 'top 82%' } }
        );
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <section ref={root} aria-label="Engagements de la maison ELSI" className="relative bg-ink-950 py-16 lg:py-24">
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
        <div className="mb-12 flex flex-col justify-between gap-4 border-b border-ivory/[0.08] pb-6 sm:flex-row sm:items-end">
          <div>
            <p className="text-[11px] uppercase tracking-label text-brass-400">Charte de service</p>
            <h2 className="text-display mt-2 text-[clamp(1.8rem,1.3rem+1.8vw,3.2rem)] leading-tight text-ivory">
              Les engagements <em className="text-brass-300">de la maison</em>
            </h2>
          </div>
          <p className="max-w-md text-xs leading-relaxed text-zinc-400 sm:text-right">
            Confection soignée à Abidjan, livraison express sous housse et sérénité absolue à chaque commande.
          </p>
        </div>

        <span data-stat-rule aria-hidden className="block h-px origin-left bg-gradient-to-r from-brass-500 via-brass-300/40 to-transparent" />

        <div className="grid grid-cols-1 gap-8 pt-10 sm:grid-cols-2 lg:grid-cols-4 lg:gap-10">
          {COMMITMENTS.map((c) => (
            <div key={c.index} data-commitment className="relative flex flex-col justify-between border-l border-brass-400/30 pl-6 transition-colors hover:border-brass-300">
              <div>
                <span className="font-serif italic text-2xl text-brass-400/80">{c.index}</span>
                <h3 className="text-display mt-3 text-xl text-ivory">{c.title}</h3>
                <p className="mt-1 text-xs font-medium uppercase tracking-wider text-brass-300">{c.highlight}</p>
                <p className="mt-3 text-sm leading-relaxed text-zinc-400">{c.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
