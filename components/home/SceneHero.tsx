'use client';

import { useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import type { Article } from '@/lib/types';
import { formatFCFA } from '@/lib/config';
import { unitPrice } from '@/lib/cart.ts';
import { PROOF, SHOW_CUSTOMER_PROOF } from '@/lib/marketing';
import { useStore } from '@/lib/store-context';
import { gsap, introDelay, MQ, SplitText, useGSAP } from '@/lib/gsap';
import Magnetic from '@/components/fx/Magnetic';
import { Sparkles } from 'lucide-react';

interface PlateProps {
  article: Article;
  n: number;
  depth: number;
  className: string;
  sizes: string;
  priority?: boolean;
  /** The lead piece: tips back and zooms on scroll. */
  main?: boolean;
}

/** A photograph mounted on its stone plate, numbered like a gallery label. */
function Plate({ article, n, depth, className, sizes, priority = false, main = false }: PlateProps) {
  return (
    <Link href={`/article/${article.id}`} data-depth={depth} data-main={main || undefined} data-cursor="Voir" className={`plate group absolute block ${className}`}>
      <div data-plate-reveal className="relative aspect-[3/4] overflow-hidden [background-color:inherit]">
        <div data-plate-img className="absolute inset-0 [background-color:inherit]">
          <Image
            src={article.photos[0]}
            alt={article.nom}
            fill
            priority={priority}
            sizes={sizes}
            className="object-contain p-[7%] mix-blend-multiply"
          />
        </div>
      </div>
      <p className="plate-caption flex justify-between gap-3">
        <span className="truncate">
          N°{String(n).padStart(2, '0')} — {article.nom}
        </span>
      </p>
    </Link>
  );
}

/**
 * Scene 1 — « La galerie ».
 * Three pieces hang on stone plates at three depths in front of one pale italic word.
 * After the brand intro the plates unveil from the bottom, the headline rises letter by letter,
 * then the promise and the CTAs settle. Scrolling slides the word and drifts the plates at
 * different speeds; on desktop the plates also lean toward the pointer.
 */
export default function SceneHero({ article, side }: { article: Article; side: Article[] }) {
  const root = useRef<HTMLElement>(null);
  const { setStylistOpen } = useStore();

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      const d = introDelay();

      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        // Entrance: each plate unfolds in 3D from its lower edge, from deep in the room, while the
        // object inside zooms from 160 % down to its place.
        gsap.set('[data-depth]', { transformPerspective: 1200, transformOrigin: '50% 100%' });
        gsap.fromTo(
          '[data-depth]',
          { rotationX: -80, z: -400, autoAlpha: 0 },
          { rotationX: 0, z: 0, autoAlpha: 1, duration: 2, ease: 'expo.out', stagger: 0.16, delay: d + 0.05 }
        );
        gsap.fromTo('[data-plate-reveal]', { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.4, ease: 'expo.out', stagger: 0.16, delay: d + 0.15 });
        gsap.fromTo('[data-plate-img]', { scale: 1.6 }, { scale: 1, duration: 2.4, ease: 'expo.out', stagger: 0.16, delay: d + 0.15 });
        gsap.fromTo('[data-hero-word]', { yPercent: 30, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 2, ease: 'expo.out', delay: d });
        const split = SplitText.create('[data-hero-title]', { type: 'words,lines,chars', mask: 'lines' });
        gsap.set('[data-hero-title]', { autoAlpha: 1 });
        gsap.fromTo(split.chars, { yPercent: 115, rotationX: -60 }, { yPercent: 0, rotationX: 0, duration: 1.3, ease: 'expo.out', stagger: 0.018, delay: d + 0.4 });
        gsap.fromTo('[data-hero-reveal]', { y: 30, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: 1, ease: 'expo.out', stagger: 0.08, delay: d + 0.8 });

        // Scroll: strong depth. The word races sideways, each plate travels at its own speed,
        // the main plate tips back in 3D while its object zooms toward you.
        const range = { trigger: root.current, start: 'top top', end: 'bottom top', scrub: 0.6 };
        gsap.fromTo('[data-hero-word]', { xPercent: 0 }, { xPercent: -42, ease: 'none', immediateRender: false, scrollTrigger: range });
        gsap.utils.toArray<HTMLElement>('[data-depth]').forEach((el) => {
          gsap.to(el, { yPercent: Number(el.dataset.depth), ease: 'none', scrollTrigger: range });
        });
        gsap.fromTo('[data-main]', { rotationX: 0, scale: 1 }, { rotationX: 22, scale: 1.08, ease: 'none', immediateRender: false, scrollTrigger: range });
        gsap.fromTo('[data-plate-img] img', { scale: 1 }, { scale: 1.35, ease: 'none', immediateRender: false, scrollTrigger: range });
      });

      // Desktop: the plates turn in 3D toward the pointer, nearer plates further, like objects in a room.
      mm.add(MQ.desktop, () => {
        // The copy drifts up and fades as the gallery takes over (desktop only: on phones it sits below the stage).
        gsap.to('[data-hero-copy]', { yPercent: -25, autoAlpha: 0.2, ease: 'none', scrollTrigger: { trigger: root.current, start: 'top top', end: 'bottom top', scrub: 0.6 } });
        if (!window.matchMedia('(pointer: fine)').matches) return;
        const movers = gsap.utils.toArray<HTMLElement>('[data-depth]').map((el) => ({
          x: gsap.quickTo(el, 'x', { duration: 1.2, ease: 'power3' }),
          ry: gsap.quickTo(el, 'rotationY', { duration: 1.2, ease: 'power3' }),
          k: Math.abs(Number(el.dataset.depth)) / 30 + 0.5,
        }));
        const move = (e: PointerEvent) => {
          const dx = e.clientX / window.innerWidth - 0.5;
          movers.forEach((m) => {
            m.x(dx * -60 * m.k);
            m.ry(dx * 22 * m.k);
          });
        };
        window.addEventListener('pointermove', move, { passive: true });
        return () => window.removeEventListener('pointermove', move);
      });

      return () => mm.revert();
    },
    { scope: root }
  );

  // ponytail: the backdrop word is the last word of the piece's name ("Sac Cabas Cuir Cognac" → "Cognac").
  const word = article.nom.split(' ').at(-1) ?? 'Abidjan';
  const [left, right] = side;

  return (
    <section ref={root} aria-labelledby="hero-titre" className="relative overflow-hidden bg-paper lg:h-[calc(100svh-var(--header-h))] lg:min-h-[640px]">
      {/* Stage: word + plates. On phones it is a 74svh block above the copy. */}
      <div className="relative h-[74svh] min-h-[460px] lg:absolute lg:inset-0 lg:h-auto">
        <p
          data-hero-word
          aria-hidden
          className="text-display pointer-events-none absolute left-[-1vw] top-[18%] select-none whitespace-nowrap text-[46vw] italic leading-[0.8] text-stone lg:top-[4%] lg:text-[31vw]"
        >
          {word}
        </p>

        <Plate article={article} n={1} depth={-28} main priority sizes="(min-width: 1024px) 28vw, 60vw" className="z-[2] left-[20%] top-[8%] w-[60vw] lg:left-[44%] lg:top-[7%] lg:w-[min(27vw,420px)]" />
        {right && (
          <Plate article={right} n={2} depth={-85} sizes="(min-width: 1024px) 12vw, 30vw" className="right-[3%] top-[4%] w-[27vw] lg:right-[5%] lg:top-[8%] lg:w-[min(11.5vw,190px)]" />
        )}
        {left && (
          <Plate article={left} n={3} depth={60} sizes="(min-width: 1024px) 12vw, 30vw" className="bottom-[2%] left-[3%] w-[30vw] lg:bottom-[9%] lg:left-auto lg:right-[13%] lg:w-[min(12vw,200px)]" />
        )}
      </div>

      {/* Copy */}
      <div data-hero-copy className="relative z-10 px-[var(--gutter)] pb-14 pt-8 lg:absolute lg:bottom-[9%] lg:left-0 lg:w-[40vw] lg:max-w-[600px] lg:p-0 lg:pl-[var(--gutter)]">
        <h1 id="hero-titre" data-hero-title className="text-display text-[clamp(2.6rem,1.1rem+3.6vw,5.4rem)] leading-[1]">
          Portée un soir, <em className="text-indigo">racontée longtemps.</em>
        </h1>
        <p data-hero-reveal className="mt-6 max-w-[44ch] text-[16px] leading-relaxed text-mute-300 lg:mt-8">
          Prêt-à-porter & accessoires d'exception à Abidjan, livrés sous housse en 24 h. Essayez chez vous en toute sérénité,{' '}
          <strong className="font-medium text-ink">échange de taille garanti sous 48 h.</strong>
        </p>
        <div data-hero-reveal className="mt-8 flex flex-wrap items-center gap-x-7 gap-y-3">
          <Magnetic>
            <Link href="/catalogue" className="btn-primary">
              Découvrir la collection
            </Link>
          </Magnetic>
          <Link
            href="/3d"
            className="inline-flex items-center gap-2 rounded-full border border-brass-500/40 bg-ink-950/90 px-4 py-2.5 text-xs font-serif font-medium text-brass-300 shadow-lg backdrop-blur-md transition-all hover:bg-brass-400 hover:text-ink-950 hover:scale-105 active:scale-95"
          >
            <Sparkles className="h-3.5 w-3.5 text-brass-400" />
            <span>Vue 3D 360° du Sac</span>
          </Link>
          <button type="button" onClick={() => setStylistOpen(true)} className="link-draw py-2 text-sm text-ink">
            Être conseillé·e par Sophia
          </button>
        </div>
        <p data-hero-reveal className="mt-7 flex flex-wrap items-center gap-x-3 gap-y-1 text-[13px] text-mute-400">
          {SHOW_CUSTOMER_PROOF && (
            <>
              <span aria-hidden className="tracking-[0.18em] text-indigo">
                ★★★★★
              </span>
              <span>
                <strong className="tabular font-medium text-ink">{PROOF.rating.toLocaleString('fr-FR')}/5</strong> · {PROOF.clients.toLocaleString('fr-FR')}+ clientes à Abidjan
              </span>
              <span aria-hidden className="text-stone-deep">
                |
              </span>
            </>
          )}
          <Link href={`/article/${article.id}`} className="link-draw text-ink">
            {article.nom.split(' ').slice(0, 3).join(' ')}, {formatFCFA(unitPrice(article))}
          </Link>
        </p>
      </div>
    </section>
  );
}
