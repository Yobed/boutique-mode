'use client';

import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { AnimatePresence, motion } from 'motion/react';
import { Heart, Menu, Search, ShoppingBag, X } from 'lucide-react';
import { useStore } from '@/lib/store-context';
import { BRAND } from '@/lib/config';

const LINKS = [
  { href: '/catalogue?categorie=sacs', label: 'Sacs' },
  { href: '/catalogue?categorie=chaussures', label: 'Chaussures' },
  { href: '/catalogue?categorie=accessoires', label: 'Bijoux' },
  { href: '/3d', label: 'Studio 3D ✨' },
  { href: '/catalogue', label: 'Tout voir' },
];

const iconBtn =
  'relative grid h-11 w-11 place-items-center text-zinc-300 transition-colors duration-feedback hover:text-ivory';

export default function Navbar() {
  const { count, openCart, cartIconRef, bump, favorites, setStylistOpen, hydrated } = useStore();
  const [menuOpen, setMenuOpen] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const [bumping, setBumping] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    if (bump === 0) return;
    setBumping(true);
    const t = window.setTimeout(() => setBumping(false), 700);
    return () => window.clearTimeout(t);
  }, [bump]);

  useEffect(() => {
    setMenuOpen(false);
    setSearchOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (searchOpen) searchRef.current?.focus();
  }, [searchOpen]);

  useEffect(() => {
    if (!menuOpen && !searchOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key !== 'Escape') return;
      setMenuOpen(false);
      setSearchOpen(false);
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [menuOpen, searchOpen]);

  const submitSearch = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const q = new FormData(e.currentTarget).get('q')?.toString().trim().slice(0, 80) ?? '';
    router.push(q ? `/catalogue?q=${encodeURIComponent(q)}` : '/catalogue');
  };

  return (
    <header className="sticky top-0 z-50 border-b border-ivory/[0.06] bg-ink-950 text-ivory">
      <p className="truncate border-b border-ivory/[0.06] px-4 py-2 text-center text-[11px] uppercase tracking-[0.1em] text-zinc-400 sm:tracking-label">
        Livraison 24 h à Abidjan
        <span className="hidden sm:inline">
          <span aria-hidden className="mx-2 text-brass-600">·</span> Paiement sécurisé à la réception
        </span>
        <span className="hidden md:inline">
          <span aria-hidden className="mx-2 text-brass-600">·</span> Échange garanti sous 48 h
        </span>
      </p>

      <div className="relative mx-auto grid h-16 max-w-[1440px] grid-cols-[1fr_auto_1fr] items-center px-[var(--gutter)] md:h-[76px]">
        <div className="flex items-center gap-1">
          <button
            type="button"
            className={`${iconBtn} -ml-3 md:hidden`}
            aria-label={menuOpen ? 'Fermer le menu' : 'Ouvrir le menu'}
            aria-expanded={menuOpen}
            aria-controls="menu-mobile"
            onClick={() => setMenuOpen((o) => !o)}
          >
            {menuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
          <nav aria-label="Navigation principale" className="hidden md:block">
            <ul className="flex items-center gap-7 text-[13px] tracking-[0.06em] text-zinc-300">
              {LINKS.map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className="link-draw py-1 transition-colors hover:text-ivory">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>

        <Link href="/" aria-label={`${BRAND.name}, accueil`} className="text-display pl-[0.32em] text-[28px] leading-none tracking-[0.32em] md:text-[34px]">
          {BRAND.name}
        </Link>

        <div className="flex items-center justify-end gap-0.5">
          <button type="button" className={`${iconBtn} icon-search hidden sm:grid`} aria-label="Rechercher" aria-expanded={searchOpen} onClick={() => setSearchOpen((o) => !o)}>
            <Search className="h-[19px] w-[19px]" strokeWidth={1.6} />
          </button>
          <button
            type="button"
            onClick={() => setStylistOpen(true)}
            className="link-draw mr-1 hidden px-3 py-2 text-[12px] uppercase tracking-label text-brass-300 transition-colors hover:text-brass-200 lg:block"
          >
            Conseil styliste
          </button>
          <Link href="/catalogue?favoris=1" className={`${iconBtn} hidden sm:grid`} aria-label={`Mes favoris (${favorites.length})`}>
            <Heart className="h-[19px] w-[19px]" strokeWidth={1.6} />
            {hydrated && favorites.length > 0 && <span className="absolute right-1.5 top-2 h-1.5 w-1.5 rounded-full bg-brass-400" aria-hidden />}
          </Link>
          <button
            ref={cartIconRef}
            type="button"
            onClick={openCart}
            data-bump={bumping}
            className={`${iconBtn} icon-cart -mr-3`}
            aria-label={`Ouvrir le panier, ${count} article${count > 1 ? 's' : ''}`}
          >
            <ShoppingBag className="h-[20px] w-[20px]" strokeWidth={1.6} />
            {hydrated && count > 0 && (
              <span key={count} className="cart-count tabular absolute right-0.5 top-1 grid h-[18px] min-w-[18px] place-items-center rounded-full bg-brass-400 px-1 text-[10px] font-semibold text-ink-950">
                {count}
              </span>
            )}
          </button>
        </div>
      </div>

      <AnimatePresence>
        {searchOpen && (
          <motion.form
            role="search"
            onSubmit={submitSearch}
            initial={{ clipPath: 'inset(0 0 100% 0)', opacity: 0 }}
            animate={{ clipPath: 'inset(0 0 0% 0)', opacity: 1 }}
            exit={{ clipPath: 'inset(0 0 100% 0)', opacity: 0, transition: { duration: 0.18 } }}
            className="absolute inset-x-0 top-full border-y border-ivory/[0.06] bg-ink-950"
          >
            <label className="mx-auto flex max-w-3xl items-center gap-4 px-[var(--gutter)] py-5">
              <span className="sr-only">Rechercher une pièce</span>
              <Search className="h-5 w-5 text-brass-400" strokeWidth={1.6} aria-hidden />
              <input
                ref={searchRef}
                name="q"
                type="search"
                maxLength={80}
                placeholder="Robe du soir, lin, costume, taille M…"
                className="text-display w-full bg-transparent text-2xl text-ivory placeholder:text-zinc-500 focus:outline-none md:text-3xl"
              />
            </label>
          </motion.form>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {menuOpen && (
          <motion.nav
            id="menu-mobile"
            aria-label="Menu"
            initial={{ clipPath: 'inset(0 0 100% 0)' }}
            animate={{ clipPath: 'inset(0 0 0% 0)' }}
            exit={{ clipPath: 'inset(0 0 100% 0)', transition: { duration: 0.2, ease: [0.4, 0, 1, 1] } }}
            transition={{ duration: 0.36, ease: [0.77, 0, 0.175, 1] }}
            className="absolute inset-x-0 top-full h-[calc(100dvh-96px)] overflow-y-auto border-t border-ivory/[0.06] bg-ink-950 px-[var(--gutter)] pb-10 pt-6 md:hidden"
          >
            <form role="search" onSubmit={submitSearch} className="mb-8 flex items-center gap-3 border-b border-ivory/15 pb-3">
              <Search className="h-5 w-5 text-brass-400" strokeWidth={1.6} aria-hidden />
              <label className="sr-only" htmlFor="q-mobile">Rechercher</label>
              <input id="q-mobile" name="q" type="search" maxLength={80} placeholder="Rechercher" className="w-full bg-transparent text-lg placeholder:text-zinc-500 focus:outline-none" />
            </form>
            <ul className="space-y-1">
              {[...LINKS, { href: '/catalogue?favoris=1', label: 'Mes favoris' }, { href: '/suivi', label: 'Suivre ma commande' }].map((l, i) => (
                <motion.li
                  key={l.href}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.12 + i * 0.05, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                >
                  <Link href={l.href} className="text-display block py-2.5 text-[32px] leading-tight">
                    {l.label}
                  </Link>
                </motion.li>
              ))}
            </ul>
            <button
              type="button"
              onClick={() => {
                setMenuOpen(false);
                setStylistOpen(true);
              }}
              className="mt-10 w-full border border-brass-500/50 py-4 text-sm uppercase tracking-label text-brass-300"
            >
              Demander conseil à Sophia
            </button>
          </motion.nav>
        )}
      </AnimatePresence>
    </header>
  );
}
