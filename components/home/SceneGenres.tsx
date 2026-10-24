'use client';

import { useRef } from 'react';
import Image from 'next/image';
import Link from 'next/link';
import { gsap, MQ, useGSAP } from '@/lib/gsap';

const P = (id: string, exp = 0) => `https://images.unsplash.com/photo-${id}?w=1000&auto=format&q=80${exp ? `&exp=${exp}` : ''}`;

const DOORS = [
  { href: '/catalogue?categorie=sacs', title: 'Sacs', kicker: 'Cabas, messagers, sacs du soir', img: P('1640901555383-7335ec5a6476', 10), alt: 'Sac trapèze en cuir façon croco jaune' },
  { href: '/catalogue?categorie=chaussures', title: 'Chaussures', kicker: 'Escarpins, sandales, richelieus', img: P('1789110519500-00ec76088f81'), alt: 'Paire de sandales argent à talon aiguille' },
  { href: '/catalogue?categorie=accessoires', title: 'Bijoux', kicker: 'Colliers, bagues, lunettes', img: P('1719861837626-c97f80462525', 10), alt: 'Collier multirangs de perles corail' },
] as const;

/**
 * Choice architecture: three doors instead of a catalogue of thirty articles.
 * Each door is a stone plate with one packshot; its name in italic overlaps the plate's lower edge.
 * Desktop: the hovered door opens wider while the others fade to grey (see `.door` in globals.css).
 */
export default function SceneGenres() {
  const root = useRef<HTMLElement>(null);

  useGSAP(
    () => {
      const mm = gsap.matchMedia();
      mm.add(`${MQ.desktop}, ${MQ.mobile}`, () => {
        const st = { trigger: root.current, start: 'top 75%' };
        gsap.fromTo('[data-door-frame]', { clipPath: 'inset(100% 0% 0% 0%)' }, { clipPath: 'inset(0% 0% 0% 0%)', duration: 1.5, ease: 'expo.out', stagger: 0.12, scrollTrigger: st });
        gsap.fromTo('[data-door]', { rotationY: -35, z: -250, transformPerspective: 1100, transformOrigin: '0% 50%' }, { rotationY: 0, z: 0, duration: 1.8, ease: 'expo.out', stagger: 0.12, scrollTrigger: st });
        // Scrubbed zoom: each object grows from 85 % to 125 % as it crosses the screen, and drifts against the scroll.
        gsap.utils.toArray<HTMLElement>('[data-door-img]').forEach((img) => {
          gsap.fromTo(img, { scale: 0.85, yPercent: 14 }, { scale: 1.25, yPercent: -14, ease: 'none', scrollTrigger: { trigger: img, start: 'top bottom', end: 'bottom top', scrub: 0.6 } });
        });
        gsap.fromTo('[data-door-title]', { yPercent: 60, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: 1.3, ease: 'expo.out', stagger: 0.12, delay: 0.3, scrollTrigger: st });
      });
      return () => mm.revert();
    },
    { scope: root }
  );

  return (
    <section ref={root} aria-labelledby="genres-titre" className="bg-paper pb-[var(--section)]">
      <h2 id="genres-titre" className="sr-only">
        Choisir un rayon
      </h2>
      <div className="doors mx-auto flex max-w-[1440px] flex-col gap-14 px-[var(--gutter)] lg:h-[74svh] lg:flex-row lg:gap-4">
        {DOORS.map((d) => (
          <Link key={d.href} href={d.href} data-door data-cursor="Entrer" className="door group flex min-w-0 flex-col overflow-hidden">
            <div data-door-frame className="relative h-[46svh] overflow-hidden bg-stone transition-colors duration-500 group-hover:bg-stone-deep lg:h-auto lg:flex-1">
              <div data-door-img className="absolute inset-0 [background-color:inherit]">
                <Image src={d.img} alt={d.alt} fill sizes="(min-width: 1024px) 40vw, 100vw" className="object-contain p-[12%] mix-blend-multiply group-hover:scale-[1.06]" />
              </div>
            </div>
            <div className="relative z-10 -mt-[0.35em] flex items-end justify-between gap-4 px-1 text-[clamp(1.75rem,0.9rem+1.6vw,2.75rem)]">
              <span data-door-title className="text-display block italic leading-[0.9] truncate transition-colors duration-500 group-hover:text-indigo">
                {d.title}
              </span>
              <span
                aria-hidden
                className="mb-[0.12em] grid h-9 w-9 shrink-0 place-items-center rounded-full border border-ink/25 text-sm text-ink transition-[background-color,color,transform,border-color] duration-500 ease-silk group-hover:-rotate-45 group-hover:border-indigo group-hover:bg-indigo group-hover:text-paper"
              >
                →
              </span>
            </div>
            <span className="mt-2.5 px-1 text-xs sm:text-sm text-mute-400 truncate">{d.kicker}</span>
          </Link>
        ))}
      </div>
    </section>
  );
}
