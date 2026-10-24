'use client';

import { useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { useStore } from '@/lib/store-context';
import { waLink } from '@/lib/config';
import { gsap, MQ, useGSAP } from '@/lib/gsap';
import Magnetic from '@/components/fx/Magnetic';

const PIECE = 'https://images.unsplash.com/photo-1761646238176-b480909e6ba6?w=1200&auto=format&q=80&exp=10';

/**
 * Scene 5 — the close. A pale « Abidjan » slides behind; the last piece hangs on its plate and
 * drifts inside its frame; the two lines of the promise rise out of their masks.
 */
export default function SceneFinalCta() {
  const root = useRef<HTMLElement>(null);
  const { setStylistOpen } = useStore();

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        const range = { trigger: root.current, start: 'top bottom', end: 'bottom top', scrub: true };
        gsap.fromTo('[data-final-word]', { xPercent: 15 }, { xPercent: -32, ease: 'none', scrollTrigger: range });
        gsap.fromTo('[data-final-plate]', { yPercent: 22, rotationY: 32, rotationX: 8, transformPerspective: 1100 }, { yPercent: -18, rotationY: -12, rotationX: -4, ease: 'none', scrollTrigger: { ...range, scrub: 0.6 } });
        gsap.fromTo('[data-final-img]', { yPercent: -10, scale: 0.8 }, { yPercent: 10, scale: 1.25, ease: 'none', scrollTrigger: range });
        gsap.fromTo('[data-final-frame]', { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.6, ease: 'expo.out', scrollTrigger: { trigger: root.current, start: 'top 70%' } });
        gsap.fromTo('[data-final-line]', { yPercent: 110 }, { yPercent: 0, duration: 1.2, stagger: 0.1, ease: 'expo.out', scrollTrigger: { trigger: root.current, start: 'top 60%' } });
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <section ref={root} aria-labelledby="final-titre" className="relative overflow-hidden bg-paper py-[var(--section)]">
      <p
        data-final-word
        aria-hidden
        className="text-display pointer-events-none absolute left-0 top-[8%] select-none whitespace-nowrap text-[30vw] italic leading-[0.8] text-stone"
      >
        Abidjan
      </p>

      <div className="relative mx-auto grid max-w-[1440px] items-center gap-14 px-[var(--gutter)] lg:grid-cols-12 lg:gap-8">
        <div data-final-plate className="plate lg:col-span-4 lg:col-start-2">
          <div data-final-frame className="relative aspect-[4/5] overflow-hidden [background-color:inherit]">
            <div data-final-img className="absolute inset-0 [background-color:inherit]">
              <Image src={PIECE} alt="Sac bourse plissé ivoire à anse arrondie" fill sizes="(min-width: 1024px) 34vw, 100vw" className="object-contain p-[10%] mix-blend-multiply" />
            </div>
          </div>
          <p className="plate-caption">N°07 — Sac Bourse Plissé Ivoire, 45 000 FCFA</p>
        </div>

        <div className="lg:col-span-6 lg:col-start-7">
          <h2 id="final-titre" className="text-display text-[clamp(3rem,1.4rem+5vw,7.2rem)] leading-[0.92]">
            <span className="block overflow-hidden pb-[0.1em]">
              <span data-final-line className="block">
                Ce soir,
              </span>
            </span>
            <span className="block overflow-hidden pb-[0.1em]">
              <span data-final-line className="block italic text-indigo">
                on vous habille.
              </span>
            </span>
          </h2>
          <p className="mt-8 max-w-[40ch] text-[17px] leading-relaxed text-mute-300">
            Livrée en 24 h à Abidjan sous housse, paiement à la réception et échange de taille garanti sous 48 h.
          </p>
          <div className="mt-10 flex flex-wrap items-center gap-x-7 gap-y-4">
            <Magnetic>
              <Link href="/catalogue" className="btn-primary">
                Choisir ma tenue
              </Link>
            </Magnetic>
            <button type="button" onClick={() => setStylistOpen(true)} className="link-draw py-2 text-sm text-ink">
              Demander conseil à Sophia
            </button>
            <a href={waLink('Bonjour ELSI, je cherche une tenue pour une soirée.')} target="_blank" rel="noopener noreferrer" className="link-draw py-2 text-sm text-green">
              Écrire sur WhatsApp
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
