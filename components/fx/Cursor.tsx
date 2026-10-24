'use client';

import { useEffect, useRef, useState } from 'react';
import { gsap } from '@/lib/gsap';

/**
 * A brass ring that trails the pointer (fine pointers only, native cursor kept).
 * Over links it tightens; over any element with `data-cursor="Label"` it opens into a disc that reads the label.
 */
export default function Cursor() {
  const ring = useRef<HTMLDivElement>(null);
  const [label, setLabel] = useState('');
  const [enabled, setEnabled] = useState(false);

  useEffect(() => {
    setEnabled(window.matchMedia('(pointer: fine) and (prefers-reduced-motion: no-preference)').matches);
  }, []);

  useEffect(() => {
    const el = ring.current;
    if (!enabled || !el) return;
    const x = gsap.quickTo(el, 'x', { duration: 0.45, ease: 'power3' });
    const y = gsap.quickTo(el, 'y', { duration: 0.45, ease: 'power3' });
    let current = '';
    let seen = false;

    const move = (e: PointerEvent) => {
      if (!seen) {
        seen = true;
        gsap.set(el, { x: e.clientX, y: e.clientY });
        gsap.to(el, { autoAlpha: 1, duration: 0.3 });
      }
      x(e.clientX);
      y(e.clientY);
      const target = (e.target as HTMLElement | null)?.closest<HTMLElement>('[data-cursor], a, button');
      const next = target?.dataset.cursor ?? (target ? '·' : '');
      if (next === current) return;
      current = next;
      setLabel(next);
    };
    const hide = () => gsap.to(el, { autoAlpha: 0, duration: 0.2 });
    const show = () => gsap.to(el, { autoAlpha: 1, duration: 0.2 });
    const root = document.documentElement;

    window.addEventListener('pointermove', move, { passive: true });
    root.addEventListener('pointerleave', hide);
    root.addEventListener('pointerenter', show);
    return () => {
      window.removeEventListener('pointermove', move);
      root.removeEventListener('pointerleave', hide);
      root.removeEventListener('pointerenter', show);
    };
  }, [enabled]);

  if (!enabled) return null;
  const mode = label === '' ? 'idle' : label === '·' ? 'link' : 'label';

  return (
    <div ref={ring} aria-hidden className="cursor-ring" data-mode={mode}>
      <span>{mode === 'label' ? label : ''}</span>
    </div>
  );
}
