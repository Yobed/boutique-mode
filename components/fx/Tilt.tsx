'use client';

import { useEffect, useRef } from 'react';
import type { ReactNode } from 'react';
import { gsap } from '@/lib/gsap';

/**
 * 3D tilt: the wrapped plate leans toward the pointer in perspective, a soft light glare
 * follows the pointer, and the plate lifts with a shadow. Children can read --px / --py
 * (pointer position, -0.5…0.5) to move against the tilt for an inner parallax.
 * Fine pointers only; reduced motion leaves the plate still.
 */
export default function Tilt({ children, max = 9, className = '' }: { children: ReactNode; max?: number; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el || !window.matchMedia('(pointer: fine) and (prefers-reduced-motion: no-preference)').matches) return;
    gsap.set(el, { transformPerspective: 900 });
    const rx = gsap.quickTo(el, 'rotationX', { duration: 0.7, ease: 'power3' });
    const ry = gsap.quickTo(el, 'rotationY', { duration: 0.7, ease: 'power3' });
    const lift = gsap.quickTo(el, 'z', { duration: 0.7, ease: 'power3' });

    const move = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      const px = (e.clientX - r.left) / r.width - 0.5;
      const py = (e.clientY - r.top) / r.height - 0.5;
      ry(px * max * 2);
      rx(-py * max * 2);
      el.style.setProperty('--px', px.toFixed(3));
      el.style.setProperty('--py', py.toFixed(3));
      el.style.setProperty('--gx', `${((px + 0.5) * 100).toFixed(1)}%`);
      el.style.setProperty('--gy', `${((py + 0.5) * 100).toFixed(1)}%`);
    };
    const enter = () => {
      el.dataset.active = 'true';
      lift(30);
    };
    const leave = () => {
      el.dataset.active = 'false';
      rx(0);
      ry(0);
      lift(0);
      el.style.setProperty('--px', '0');
      el.style.setProperty('--py', '0');
    };
    el.addEventListener('pointerenter', enter);
    el.addEventListener('pointermove', move);
    el.addEventListener('pointerleave', leave);
    return () => {
      el.removeEventListener('pointerenter', enter);
      el.removeEventListener('pointermove', move);
      el.removeEventListener('pointerleave', leave);
    };
  }, [max]);

  return (
    <div ref={ref} className={`tilt relative ${className}`}>
      {children}
      <span aria-hidden className="tilt-glare" />
    </div>
  );
}
