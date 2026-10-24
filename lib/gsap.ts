'use client';

import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { CustomEase } from 'gsap/CustomEase';
import { SplitText } from 'gsap/SplitText';
import { useGSAP } from '@gsap/react';

// Registered once on the client. Eases mirror the CSS tokens in globals.css.
if (typeof window !== 'undefined') {
  gsap.registerPlugin(ScrollTrigger, CustomEase, SplitText, useGSAP);
  CustomEase.create('silk', '0.16,1,0.3,1');
  CustomEase.create('curtain', '0.77,0,0.175,1');
  CustomEase.create('velvet', '0.65,0,0.35,1');
}

/** Breakpoint contexts for gsap.matchMedia(). Reduced motion gets no scroll choreography. */
export const MQ = {
  desktop: '(min-width: 1024px) and (prefers-reduced-motion: no-preference)',
  mobile: '(max-width: 1023px) and (prefers-reduced-motion: no-preference)',
} as const;

/** Seconds the CSS brand intro covers the page on a first visit (see Preloader + globals.css). */
export const introDelay = () =>
  typeof document !== 'undefined' && !document.documentElement.classList.contains('no-intro') ? 1.55 : 0;

export { gsap, ScrollTrigger, SplitText, useGSAP };
