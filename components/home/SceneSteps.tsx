'use client';

import { useRef } from 'react';
import Link from 'next/link';
import { gsap, MQ, useGSAP } from '@/lib/gsap';
import Magnetic from '@/components/fx/Magnetic';

const STEPS = [
  ['Choisissez avec précision', 'En ligne ou directement sur WhatsApp avec Sophia, qui vérifie vos mensurations et vous conseille la coupe idéale.'],
  ['Recevez sous 24 h à Abidjan', 'Votre pièce arrive repassée sous housse protectrice. Vous réglez à la remise en main propre (espèces, Wave, Orange Money ou MTN MoMo).'],
  ['Essayez chez vous, échange 48 h', 'Prenez le temps d’essayer en toute intimité. Si la taille doit être ajustée, nous organisons l’échange à votre porte sous 48 h sans tracas.'],
] as const;

/**
 * Risk reversal, told as three steps. A brass thread draws down as you scroll and
 * each numeral fills with light when the thread reaches it.
 */
export default function SceneSteps() {
  const root = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        gsap.fromTo(
          '[data-steps-thread]',
          { scaleY: 0 },
          { scaleY: 1, ease: 'none', scrollTrigger: { trigger: '[data-steps-list]', start: 'top 70%', end: 'bottom 60%', scrub: true } }
        );
        gsap.utils.toArray<HTMLElement>('[data-step]').forEach((step) => {
          gsap
            .timeline({ scrollTrigger: { trigger: step, start: 'top 68%', toggleActions: 'play none none reverse' } })
            .fromTo(step, { '--fill': '0%' }, { '--fill': '100%', duration: 0.9, ease: 'velvet' })
            .fromTo(step.querySelectorAll('[data-step-text] > *'), { y: 30, opacity: 0 }, { y: 0, opacity: 1, duration: 0.8, ease: 'silk', stagger: 0.08 }, 0.1);
        });
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <section ref={root} aria-labelledby="steps-titre" className="relative bg-ink-950 py-[var(--section)]">
      <div className="mx-auto grid max-w-[1440px] gap-16 px-[var(--gutter)] lg:grid-cols-12 lg:gap-8">
        <div className="lg:sticky lg:top-[calc(var(--header-h)+8vh)] lg:col-span-5 lg:self-start">
          <p className="text-[11px] uppercase tracking-label text-brass-300">L'esprit serein</p>
          <h2 id="steps-titre" className="text-display mt-5 text-[clamp(2.6rem,1.6rem+3.4vw,5.4rem)] leading-[0.95]">
            L’élégance sans compromis, livrée chez vous.
          </h2>
          <p className="mt-8 max-w-[40ch] text-[17px] leading-relaxed text-zinc-300">
            Commander une création d’exception ne doit comporter aucun doute. Pièce prête à porter, paiement sécurisé à la réception et échange de taille garanti sous 48 h.
          </p>
          <Magnetic className="mt-10">
            <Link href="/catalogue" className="btn-primary">
              Je choisis ma tenue
            </Link>
          </Magnetic>
        </div>

        <ol data-steps-list className="relative lg:col-span-6 lg:col-start-7">
          <span aria-hidden className="absolute bottom-0 left-[1.6rem] top-0 w-px bg-ivory/10 lg:left-[2.6rem]" />
          <span data-steps-thread aria-hidden className="absolute bottom-0 left-[1.6rem] top-0 w-px origin-top bg-brass-400 lg:left-[2.6rem]" />
          {STEPS.map(([t, d], i) => (
            <li key={t} data-step className="step relative grid grid-cols-[3.2rem_1fr] gap-6 pb-20 last:pb-0 lg:grid-cols-[5.2rem_1fr] lg:gap-10 lg:pb-32">
              <span aria-hidden className="text-display relative z-10 self-start bg-ink-950 py-2 text-center text-[clamp(2.6rem,1.8rem+2.4vw,4.6rem)] leading-none">
                <span className="step-num italic">{i + 1}</span>
              </span>
              <div data-step-text className="pt-2">
                <h3 className="text-display text-[clamp(1.8rem,1.3rem+1.6vw,3rem)] leading-tight">{t}</h3>
                <p className="mt-4 max-w-[40ch] leading-relaxed text-zinc-400">{d}</p>
              </div>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
