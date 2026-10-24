import type { CSSProperties, ReactNode } from 'react';

/** Endless CSS ribbon. Content is rendered twice; the copy is hidden from screen readers. Pauses on hover. */
export default function Marquee({
  children,
  reverse = false,
  speed = 40,
  className = '',
}: {
  children: ReactNode;
  reverse?: boolean;
  /** Seconds per loop. */
  speed?: number;
  className?: string;
}) {
  return (
    <div className={`marquee ${className}`} style={{ '--marquee-dur': `${speed}s` } as CSSProperties}>
      <div className={`marquee-track ${reverse ? 'marquee-reverse' : ''}`}>
        <div className="marquee-group">{children}</div>
        <div className="marquee-group" aria-hidden>
          {children}
        </div>
      </div>
    </div>
  );
}
