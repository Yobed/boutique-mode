'use client';

import { useRef } from 'react';
import Image from 'next/image';
import { gsap, MQ, useGSAP } from '@/lib/gsap';
import Words from '@/components/home/Words';

const ATELIER = 'https://images.unsplash.com/photo-1768212566108-4ce4f329e4d2?w=1400&auto=format&fit=crop&q=80';
const WAX = 'https://images.unsplash.com/photo-1784123476742-de48239d2fb0?w=800&auto=format&fit=crop&q=80';

/** Scene 2 — the house: an editorial sentence that lights up word by word, two images on two depths. */
export default function SceneUnivers() {
  const root = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        gsap.fromTo(
          '[data-word]',
          { opacity: 0.42 }, // floor keeps unrevealed words ≥ 3:1 (WCAG AA, large text)
          { opacity: 1, stagger: 0.06, ease: 'none', scrollTrigger: { trigger: '[data-statement]', start: 'top 78%', end: 'bottom 45%', scrub: true } }
        );
        const st = { trigger: root.current, start: 'top bottom', end: 'bottom top', scrub: true };
        gsap.fromTo('[data-depth="far"]', { yPercent: -14, scale: 1.2 }, { yPercent: 14, scale: 1, ease: 'none', scrollTrigger: st });
        gsap.fromTo('[data-depth="near"]', { yPercent: 70, rotation: -8, rotationY: 25, transformPerspective: 900 }, { yPercent: -70, rotation: 5, rotationY: -10, ease: 'none', scrollTrigger: { ...st } });
        gsap.fromTo(
          '[data-frame]',
          { clipPath: 'inset(28% 8% 28% 8%)' },
          { clipPath: 'inset(0% 0% 0% 0%)', ease: 'curtain', scrollTrigger: { trigger: '[data-frame]', start: 'top 90%', end: 'top 35%', scrub: 0.6 } }
        );
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <section ref={root} aria-labelledby="univers-titre" className="relative overflow-hidden bg-ink-950 py-[var(--section)]">
      <div className="mx-auto grid max-w-[1440px] gap-16 px-[var(--gutter)] lg:grid-cols-12 lg:gap-8">
        <div className="lg:col-span-7 lg:pt-[8vh]">
          <h2 id="univers-titre" data-statement className="text-display text-[clamp(2rem,1.2rem+2.9vw,4.4rem)] leading-[1.08]">
            <Words text="Une pièce ne quitte notre atelier d’Abidjan qu’après avoir été choisie, ajustée et repassée à la vapeur. Puis elle voyage sous housse, jusqu’à vous." />
          </h2>
          <p className="mt-10 max-w-[46ch] text-[17px] leading-relaxed text-zinc-300 lg:ml-[16%]">
            ELSI réunit couturières, tailleurs et stylistes autour d’une exigence absolue : vous offrir des créations aux coupes parfaites, confectionnées avec soin et prêtes à être portées. Vous essayez chez vous, et nous garantissons l’échange de taille sous 48 h à votre porte.
          </p>
        </div>

        <div className="relative lg:col-span-5">
          <div data-frame className="relative aspect-[3/4] overflow-hidden bg-ink-900">
            <div data-depth="far" className="absolute inset-x-0 -inset-y-[22%]">
              <Image src={ATELIER} alt="Tissus wax aux motifs vifs exposés au marché d’Abidjan" fill sizes="(min-width: 1024px) 40vw, 100vw" className="object-cover" />
            </div>
          </div>
          <div data-depth="near" className="absolute -bottom-10 -left-4 w-[44%] shadow-lift sm:-left-10 lg:-left-[22%]">
            <div className="relative aspect-square overflow-hidden">
              <Image src={WAX} alt="Détail d’un wax aux motifs d’oiseaux et de papillons" fill sizes="(min-width: 1024px) 18vw, 44vw" className="object-cover" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
