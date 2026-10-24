import { BRAND } from '@/lib/config';

/**
 * First-visit brand intro, pure CSS: it plays while the page hydrates and can never get stuck.
 * The inline script in layout.tsx adds `.no-intro` on later page views of the session.
 */
export default function Preloader() {
  return (
    <div aria-hidden className="preloader">
      <div className="preloader-inner">
        <p className="preloader-word text-display">
          {BRAND.name.split('').map((c, i) => (
            <span key={i} style={{ animationDelay: `${120 + i * 90}ms` }}>
              {c}
            </span>
          ))}
        </p>
        <span className="preloader-line" />
        <p className="preloader-sub">Abidjan · Couture du soir</p>
      </div>
    </div>
  );
}
