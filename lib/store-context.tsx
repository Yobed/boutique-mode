'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';
import type { ReactNode, RefObject } from 'react';
import { useReducedMotion } from 'motion/react';
import type { Article, CartItem } from './types';
import { addItem, countItems, parseStoredCart, removeItem, setQuantity } from './cart.ts';

const CART_KEY = 'boutique_cart';
const FAV_KEY = 'elsi_favoris';

export interface Flight {
  id: number;
  src: string;
  from: { left: number; top: number; width: number; height: number };
}

export interface LastAdded {
  id: number;
  nom: string;
  taille: string;
  photo?: string;
}

interface StoreValue {
  items: CartItem[];
  count: number;
  hydrated: boolean;
  add: (article: Article, taille: string, couleur: string, source?: HTMLElement | null) => void;
  setQty: (index: number, quantite: number) => void;
  remove: (index: number) => void;
  clear: () => void;
  cartOpen: boolean;
  openCart: () => void;
  closeCart: () => void;
  stylistOpen: boolean;
  setStylistOpen: (open: boolean) => void;
  favorites: string[];
  toggleFavorite: (id: string) => void;
  cartIconRef: RefObject<HTMLButtonElement | null>;
  flights: Flight[];
  landFlight: (id: number) => void;
  bump: number;
  lastAdded: LastAdded | null;
  dismissLastAdded: () => void;
}

const StoreContext = createContext<StoreValue | null>(null);

function readFavorites(): string[] {
  try {
    const data: unknown = JSON.parse(localStorage.getItem(FAV_KEY) ?? '[]');
    return Array.isArray(data) ? data.filter((x): x is string => typeof x === 'string') : [];
  } catch {
    return [];
  }
}

function write(key: string, value: unknown) {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch {
    // Private mode / quota: the session still works in memory.
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [favorites, setFavorites] = useState<string[]>([]);
  const [hydrated, setHydrated] = useState(false);
  const [cartOpen, setCartOpen] = useState(false);
  const [stylistOpen, setStylistOpen] = useState(false);
  const [flights, setFlights] = useState<Flight[]>([]);
  const [bump, setBump] = useState(0);
  const [lastAdded, setLastAdded] = useState<LastAdded | null>(null);
  const cartIconRef = useRef<HTMLButtonElement | null>(null);
  const reduceMotion = useReducedMotion();

  useEffect(() => {
    let stored: string | null = null;
    try {
      stored = localStorage.getItem(CART_KEY);
    } catch {
      stored = null;
    }
    setItems(parseStoredCart(stored));
    setFavorites(readFavorites());
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (hydrated) write(CART_KEY, items);
  }, [items, hydrated]);

  useEffect(() => {
    if (hydrated) write(FAV_KEY, favorites);
  }, [favorites, hydrated]);

  useEffect(() => {
    if (!lastAdded) return;
    const t = window.setTimeout(() => setLastAdded(null), 4200);
    return () => window.clearTimeout(t);
  }, [lastAdded]);

  const add = useCallback<StoreValue['add']>(
    (article, taille, couleur, source) => {
      if (!article.en_stock) return;
      setItems((prev) => addItem(prev, article, taille, couleur));
      setLastAdded({ id: Date.now(), nom: article.nom, taille, photo: article.photos[0] });

      const icon = cartIconRef.current;
      const img = source instanceof HTMLImageElement ? source : source?.querySelector('img');
      if (reduceMotion || !icon || !source || !img?.currentSrc) {
        setBump((b) => b + 1);
        return;
      }
      const r = source.getBoundingClientRect();
      setFlights((f) => [
        ...f,
        { id: Date.now() + Math.random(), src: img.currentSrc, from: { left: r.left, top: r.top, width: r.width, height: r.height } },
      ]);
    },
    [reduceMotion]
  );

  const landFlight = useCallback((id: number) => {
    setFlights((f) => f.filter((x) => x.id !== id));
    setBump((b) => b + 1);
  }, []);

  const toggleFavorite = useCallback((id: string) => {
    setFavorites((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]));
  }, []);

  const value = useMemo<StoreValue>(
    () => ({
      items,
      count: countItems(items),
      hydrated,
      add,
      setQty: (i, q) => setItems((prev) => setQuantity(prev, i, q)),
      remove: (i) => setItems((prev) => removeItem(prev, i)),
      clear: () => setItems([]),
      cartOpen,
      openCart: () => {
        setLastAdded(null);
        setCartOpen(true);
      },
      closeCart: () => setCartOpen(false),
      stylistOpen,
      setStylistOpen,
      favorites,
      toggleFavorite,
      cartIconRef,
      flights,
      landFlight,
      bump,
      lastAdded,
      dismissLastAdded: () => setLastAdded(null),
    }),
    [items, hydrated, add, cartOpen, stylistOpen, favorites, toggleFavorite, flights, landFlight, bump, lastAdded]
  );

  return <StoreContext.Provider value={value}>{children}</StoreContext.Provider>;
}

export function useStore(): StoreValue {
  const ctx = useContext(StoreContext);
  if (!ctx) throw new Error('useStore must be used inside <StoreProvider>');
  return ctx;
}
