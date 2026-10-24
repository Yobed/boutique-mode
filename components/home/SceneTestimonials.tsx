import Marquee from '@/components/fx/Marquee';
import { PROOF, TESTIMONIALS } from '@/lib/marketing';
import type { Testimonial } from '@/lib/marketing';

function Stars({ className = '' }: { className?: string }) {
  return (
    <span aria-hidden className={`tracking-[0.2em] text-indigo ${className}`}>
      ★★★★★
    </span>
  );
}

function Card({ t }: { t: Testimonial }) {
  return (
    <figure className="mx-2.5 flex w-[min(82vw,400px)] shrink-0 flex-col justify-between bg-paper p-7 lg:p-8">
      <div>
        <Stars />
        <blockquote className="text-display mt-4 text-[19px] leading-snug text-linen-ink">« {t.quote} »</blockquote>
      </div>
      <figcaption className="mt-6 flex items-baseline justify-between gap-4 border-t border-linen-ink/10 pt-4 text-sm">
        <span className="text-linen-ink">
          {t.name} <span className="text-linen-muted">· {t.commune}</span>
        </span>
        <span className="truncate text-xs text-linen-muted">{t.piece}</span>
      </figcaption>
    </figure>
  );
}

/** Social proof on linen: two ribbons of customer quotes drifting in opposite directions. */
export default function SceneTestimonials() {
  const half = Math.ceil(TESTIMONIALS.length / 2);
  // Each ribbon repeats its cards so one loop is wider than the widest screen (no gap at the seam).
  const rowA = [...TESTIMONIALS.slice(0, half), ...TESTIMONIALS.slice(0, half)];
  const rowB = [...TESTIMONIALS.slice(half), ...TESTIMONIALS.slice(half)];
  return (
    <section aria-labelledby="avis-titre" className="surface-linen overflow-hidden bg-linen py-[var(--section)] text-linen-ink">
      <div className="mx-auto mb-14 flex max-w-[1440px] flex-col justify-between gap-6 px-[var(--gutter)] lg:flex-row lg:items-end">
        <h2 id="avis-titre" className="text-display max-w-[14ch] text-[clamp(2.6rem,1.6rem+3.4vw,5.4rem)] leading-[0.95]">
          Elles en parlent mieux que nous.
        </h2>
        <p className="flex items-center gap-3 text-sm text-linen-muted">
          <Stars className="text-base" />
          <span>
            <strong className="tabular font-medium text-linen-ink">{PROOF.rating.toLocaleString('fr-FR')}/5</strong> sur {PROOF.reviews} avis
          </span>
        </p>
      </div>
      <div className="space-y-5">
        <Marquee speed={60}>
          {rowA.map((t, i) => (
            <Card key={`${t.name}-${i}`} t={t} />
          ))}
        </Marquee>
        <Marquee speed={70} reverse>
          {rowB.map((t, i) => (
            <Card key={`${t.name}-${i}`} t={t} />
          ))}
        </Marquee>
      </div>
    </section>
  );
}
