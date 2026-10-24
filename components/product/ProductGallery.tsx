'use client';

import { useCallback, useEffect, useRef, useState } from 'react';
import type { PointerEvent as RPointerEvent, RefObject } from 'react';
import Image from 'next/image';
import { AnimatePresence, motion, useReducedMotion, useScroll, useTransform } from 'motion/react';
import { ChevronLeft, ChevronRight, X, Camera, Sparkles } from 'lucide-react';
import Product3DViewer from '@/components/3d/Product3DViewer';

interface Props {
  photos: string[];
  nom: string;
  /** Points at the photo currently in view, so add-to-cart can fly it. */
  plateRef: RefObject<HTMLDivElement | null>;
  modele_3d?: {
    src: string;
    poster?: string;
    cameraOrbit?: string;
  };
  selectedColor?: string;
}

const SILK = [0.16, 1, 0.3, 1] as const;

/** Moves the zoom origin with the pointer via CSS vars: no React re-render per frame. */
function trackOrigin(e: RPointerEvent<HTMLElement>) {
  const el = e.currentTarget;
  const r = el.getBoundingClientRect();
  el.style.setProperty('--zx', `${((e.clientX - r.left) / r.width) * 100}%`);
  el.style.setProperty('--zy', `${((e.clientY - r.top) / r.height) * 100}%`);
}

interface FigureProps {
  src: string;
  index: number;
  nom: string;
  hidden: boolean;
  onOpen: () => void;
  register: (el: HTMLDivElement | null) => void;
}

/** One plate: unveils as it enters, drifts slightly inside its frame while the page scrolls. */
function Figure({ src, index, nom, hidden, onOpen, register }: FigureProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  const reduce = useReducedMotion();
  const { scrollYProgress } = useScroll({ target: ref, offset: ['start end', 'end start'] });
  const drift = useTransform(scrollYProgress, [0, 1], reduce ? ['0%', '0%'] : ['-5%', '5%']);

  return (
    <motion.div
      ref={(el) => {
        ref.current = el;
        register(el);
      }}
      data-slide={index}
      className="relative aspect-[4/5] w-full shrink-0 snap-center overflow-hidden bg-stone lg:aspect-[3/4]"
      initial={index === 0 ? false : { clipPath: 'inset(10% 0% 10% 0%)', opacity: 0.4 }}
      whileInView={{ clipPath: 'inset(0% 0% 0% 0%)', opacity: 1 }}
      viewport={{ once: true, amount: 0.25 }}
      transition={{ duration: 1.1, ease: [0.77, 0, 0.175, 1] }}
    >
      {!hidden && (
        <motion.button
          type="button"
          layoutId={`photo-${src}`}
          onClick={onOpen}
          aria-label={`Voir la photo ${index + 1} de ${nom} en plein écran`}
          data-cursor="Zoom"
          // Zoom lens (mouse only): the photo scales ×2.4 from under the pointer; click still opens full screen.
          onPointerEnter={(e) => {
            if (!reduce && e.pointerType === 'mouse') e.currentTarget.dataset.zoom = 'true';
          }}
          onPointerMove={trackOrigin}
          onPointerLeave={(e) => {
            e.currentTarget.dataset.zoom = 'false';
          }}
          className="zoom-lens absolute inset-0 block cursor-zoom-in overflow-hidden [background-color:inherit]"
          transition={{ duration: 0.55, ease: SILK }}
        >
          <motion.span className="absolute inset-x-0 -inset-y-[6%] block [background-color:inherit]" style={{ y: drift }}>
            <Image
              src={src}
              alt={`${nom}, vue ${index + 1}`}
              fill
              priority={index === 0}
              sizes="(min-width: 1024px) 54vw, 100vw"
              className="object-contain p-[8%] mix-blend-multiply"
            />
          </motion.span>
        </motion.button>
      )}
    </motion.div>
  );
}

interface LightboxProps {
  photos: string[];
  nom: string;
  index: number;
  go: (delta: number) => void;
  onClose: () => void;
}

/** Full-screen viewer: morphs from the plate, swipe to browse, drag down to dismiss, tap to zoom. */
function Lightbox({ photos, nom, index, go, onClose }: LightboxProps) {
  const closeRef = useRef<HTMLButtonElement>(null);
  const [zoomed, setZoomed] = useState(false);
  const src = photos[index];

  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const { overflow } = document.body.style;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = overflow;
      previous?.focus();
    };
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
      if (e.key === 'ArrowRight') go(1);
      if (e.key === 'ArrowLeft') go(-1);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [go, onClose]);

  useEffect(() => setZoomed(false), [index]);

  return (
    <div role="dialog" aria-modal="true" aria-label={`${nom}, photo ${index + 1} sur ${photos.length}`} className="fixed inset-0 z-[80]">
      <motion.div className="absolute inset-0 bg-ink-950" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0, transition: { duration: 0.25 } }} />

      <motion.div
        layoutId={`photo-${src}`}
        transition={{ duration: 0.55, ease: SILK }}
        className={`absolute inset-0 overflow-hidden ${zoomed ? 'cursor-zoom-out' : 'cursor-zoom-in'}`}
        drag={zoomed ? false : true}
        dragSnapToOrigin
        dragElastic={0.35}
        onDragEnd={(_, info) => {
          if (Math.abs(info.offset.y) > 120 && Math.abs(info.offset.y) > Math.abs(info.offset.x)) onClose();
          else if (info.offset.x < -80) go(1);
          else if (info.offset.x > 80) go(-1);
        }}
        onPointerMove={trackOrigin}
        onTap={() => setZoomed((z) => !z)}
      >
        <div
          className="absolute inset-0 transition-transform duration-500 ease-silk"
          style={{ transform: zoomed ? 'scale(2.4)' : 'none', transformOrigin: 'var(--zx, 50%) var(--zy, 50%)' }}
        >
          <Image src={src} alt={`${nom}, vue ${index + 1}`} fill sizes="100vw" className="pointer-events-none object-contain" />
        </div>
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1, transition: { delay: 0.3 } }} exit={{ opacity: 0, transition: { duration: 0.1 } }}>
        <button ref={closeRef} type="button" onClick={onClose} aria-label="Fermer" className="absolute right-3 top-3 z-10 grid h-12 w-12 place-items-center bg-ink-950/70 text-ivory">
          <X className="h-6 w-6" />
        </button>
        {photos.length > 1 && (
          <>
            <button type="button" onClick={() => go(-1)} aria-label="Photo précédente" className="absolute left-3 top-1/2 z-10 hidden h-12 w-12 -translate-y-1/2 place-items-center bg-ink-950/70 text-ivory sm:grid">
              <ChevronLeft className="h-6 w-6" />
            </button>
            <button type="button" onClick={() => go(1)} aria-label="Photo suivante" className="absolute right-3 top-1/2 z-10 hidden h-12 w-12 -translate-y-1/2 place-items-center bg-ink-950/70 text-ivory sm:grid">
              <ChevronRight className="h-6 w-6" />
            </button>
          </>
        )}
        <p className="tabular absolute bottom-5 left-1/2 z-10 -translate-x-1/2 bg-ink-950/70 px-3 py-1.5 text-xs tracking-label text-zinc-200">
          {index + 1} / {photos.length} ·{' '}
          <span className="[@media(pointer:fine)]:hidden">{zoomed ? 'touchez pour dézoomer' : 'touchez pour zoomer, glissez vers le bas pour fermer'}</span>
          <span className="hidden [@media(pointer:fine)]:inline">{zoomed ? 'cliquez pour dézoomer' : 'cliquez pour zoomer, Échap pour fermer'}</span>
        </p>
      </motion.div>
    </div>
  );
}

export default function ProductGallery({ photos, nom, plateRef, modele_3d, selectedColor }: Props) {
  const [viewMode, setViewMode] = useState<'photos' | '3d'>('3d');
  const [active, setActive] = useState(0);
  const [open, setOpen] = useState<number | null>(null);
  const slides = useRef<(HTMLDivElement | null)[]>([]);
  const viewerPlateRef = useRef<HTMLDivElement>(null);
  const many = photos.length > 1;

  // The plate in view is the one that flies to the cart.
  useEffect(() => {
    if (viewMode === '3d' && modele_3d) {
      plateRef.current = viewerPlateRef.current;
    } else {
      plateRef.current = slides.current[active] ?? slides.current[0] ?? null;
    }
  }, [active, plateRef, viewMode, modele_3d]);

  // Track the slide in view (mobile carousel and desktop stack alike).
  useEffect(() => {
    if (viewMode !== 'photos') return;
    const io = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting).sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];
        if (visible) setActive(Number((visible.target as HTMLElement).dataset.slide));
      },
      { threshold: [0.55] }
    );
    slides.current.forEach((el) => el && io.observe(el));
    return () => io.disconnect();
  }, [photos.length, viewMode]);

  const go = useCallback((delta: number) => setOpen((i) => (i === null ? i : (i + delta + photos.length) % photos.length)), [photos.length]);
  const close = useCallback(() => setOpen(null), []);

  return (
    <div className="relative -mx-[var(--gutter)] lg:mx-0">
      {modele_3d && (
        <div className="mb-4 flex items-center justify-center gap-2 px-[var(--gutter)] lg:px-0">
          <div className="inline-flex rounded-full bg-ink-950/80 p-1 border border-ivory/10 backdrop-blur-md shadow-lg">
            <button
              type="button"
              onClick={() => setViewMode('3d')}
              className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium tracking-wide transition-all ${
                viewMode === '3d'
                  ? 'bg-brass-400 text-ink-950 font-semibold shadow'
                  : 'text-zinc-400 hover:text-ivory'
              }`}
            >
              <Sparkles className="w-3.5 h-3.5" />
              Vue 3D 360°
            </button>
            <button
              type="button"
              onClick={() => setViewMode('photos')}
              className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-xs font-medium tracking-wide transition-all ${
                viewMode === 'photos'
                  ? 'bg-brass-400 text-ink-950 font-semibold shadow'
                  : 'text-zinc-400 hover:text-ivory'
              }`}
            >
              <Camera className="w-3.5 h-3.5" />
              Photos HD ({photos.length})
            </button>
          </div>
        </div>
      )}

      {modele_3d && viewMode === '3d' ? (
        <div ref={viewerPlateRef} className="px-[var(--gutter)] lg:px-0">
          <Product3DViewer
            modelSrc={modele_3d.src}
            posterSrc={modele_3d.poster}
            cameraOrbit={modele_3d.cameraOrbit}
            selectedColor={selectedColor}
            alt={`Modèle 3D de ${nom}`}
            className="w-full aspect-[4/5] lg:aspect-[3/4] shadow-2xl"
          />
        </div>
      ) : (
        <>
          <div className="flex snap-x snap-mandatory overflow-x-auto [scrollbar-width:none] lg:flex-col lg:gap-3 lg:overflow-visible" aria-label={`Photos de ${nom}`}>
            {photos.map((src, i) => (
              <Figure
                key={src}
                src={src}
                index={i}
                nom={nom}
                hidden={open === i}
                onOpen={() => setOpen(i)}
                register={(el) => {
                  slides.current[i] = el;
                }}
              />
            ))}
          </div>

          {many && (
            <div className="pointer-events-none absolute inset-x-[var(--gutter)] bottom-4 flex gap-1.5 lg:hidden" aria-hidden>
              {photos.map((src, i) => (
                <span key={src} className="h-[2px] flex-1 overflow-hidden bg-ivory/25">
                  <motion.span className="block h-full origin-left bg-ivory" animate={{ scaleX: i <= active ? 1 : 0 }} transition={{ duration: 0.4, ease: SILK }} />
                </span>
              ))}
            </div>
          )}

          <AnimatePresence>{open !== null && <Lightbox photos={photos} nom={nom} index={open} go={go} onClose={close} />}</AnimatePresence>
        </>
      )}
    </div>
  );
}
