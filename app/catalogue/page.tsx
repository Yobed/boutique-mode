'use client';

import { Suspense, useCallback, useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { AnimatePresence, motion } from 'motion/react';
import { SlidersHorizontal, X } from 'lucide-react';
import ProductCard from '@/components/ProductCard';
import FilterSidebar from '@/components/FilterSidebar';
import { ProductGridSkeleton } from '@/components/ui/Skeleton';
import { getArticles } from '@/lib/supabase';
import { useStore } from '@/lib/store-context';
import { unitPrice } from '@/lib/cart.ts';
import type { Article, CategorieVêtement, GenreVêtement } from '@/lib/types';

type Sort = 'selection' | 'prix-asc' | 'prix-desc';
const MAX_PRICE = 100000;

function CatalogueContent() {
  const params = useSearchParams();
  const { favorites } = useStore();
  const [articles, setArticles] = useState<Article[]>([]);
  const [status, setStatus] = useState<'loading' | 'ready' | 'error'>('loading');
  const [filtersOpen, setFiltersOpen] = useState(false);

  const [query, setQuery] = useState(params.get('q') ?? '');
  const [categorie, setCategorie] = useState<CategorieVêtement>((params.get('categorie') as CategorieVêtement) || 'tous');
  const [genre, setGenre] = useState<GenreVêtement>((params.get('genre') as GenreVêtement) || 'tous');
  const [taille, setTaille] = useState('');
  const [maxPrice, setMaxPrice] = useState(MAX_PRICE);
  const [onlyPromo, setOnlyPromo] = useState(params.get('promo') === 'true');
  const [onlyFav, setOnlyFav] = useState(params.get('favoris') === '1');
  const [sort, setSort] = useState<Sort>('selection');

  // Keep state in sync when the header search or a nav link changes the URL.
  useEffect(() => {
    setQuery(params.get('q') ?? '');
    setCategorie((params.get('categorie') as CategorieVêtement) || 'tous');
    setGenre((params.get('genre') as GenreVêtement) || 'tous');
    setOnlyPromo(params.get('promo') === 'true');
    setOnlyFav(params.get('favoris') === '1');
  }, [params]);

  const load = useCallback(() => {
    setStatus('loading');
    getArticles()
      .then((data) => {
        setArticles(data);
        setStatus('ready');
      })
      .catch(() => setStatus('error'));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  const reset = () => {
    setQuery('');
    setCategorie('tous');
    setGenre('tous');
    setTaille('');
    setMaxPrice(MAX_PRICE);
    setOnlyPromo(false);
    setOnlyFav(false);
  };

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const list = articles.filter((a) => {
      if (q && ![a.nom, a.description, a.categorie, ...a.couleurs].some((s) => s.toLowerCase().includes(q))) return false;
      if (categorie !== 'tous' && a.categorie !== categorie) return false;
      if (genre !== 'tous' && a.genre !== genre && a.genre !== 'mixte') return false;
      if (taille && !a.tailles.includes(taille)) return false;
      if (maxPrice < MAX_PRICE && unitPrice(a) > maxPrice) return false;
      if (onlyPromo && !a.prix_promo) return false;
      if (onlyFav && !favorites.includes(a.id)) return false;
      return true;
    });
    if (sort === 'prix-asc') return [...list].sort((a, b) => unitPrice(a) - unitPrice(b));
    if (sort === 'prix-desc') return [...list].sort((a, b) => unitPrice(b) - unitPrice(a));
    return list;
  }, [articles, query, categorie, genre, taille, maxPrice, onlyPromo, onlyFav, favorites, sort]);

  const title = onlyFav ? 'Vos favoris' : genre === 'femme' ? 'Femme' : genre === 'homme' ? 'Homme' : categorie !== 'tous' ? categorie : 'La collection';

  const sidebar = (
    <FilterSidebar
      selectedCategorie={categorie}
      onSelectCategorie={setCategorie}
      selectedGenre={genre}
      onSelectGenre={setGenre}
      selectedTaille={taille}
      onSelectTaille={setTaille}
      maxPrice={maxPrice}
      onMaxPriceChange={setMaxPrice}
      onlyPromo={onlyPromo}
      onTogglePromo={setOnlyPromo}
      onReset={reset}
    />
  );

  return (
    <div className="mx-auto max-w-[1440px] px-[var(--gutter)] pb-24 pt-10 md:pt-16">
      <header className="mb-10 flex flex-col gap-6 border-b border-ivory/[0.08] pb-8 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-display text-[clamp(2.6rem,1.6rem+3vw,5rem)] capitalize leading-none">{title}</h1>
          <p className="tabular mt-3 text-sm text-zinc-400" aria-live="polite">
            {status === 'ready' ? `${filtered.length} pièce${filtered.length > 1 ? 's' : ''}` : ' '}
            {query && status === 'ready' && <> pour « {query} »</>}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <label className="sr-only" htmlFor="tri">
            Trier
          </label>
          <select id="tri" value={sort} onChange={(e) => setSort(e.target.value as Sort)} className="h-11 border border-ivory/15 bg-ink-950 px-3 text-sm text-zinc-200 focus:border-brass-300 focus:outline-none">
            <option value="selection">Notre sélection</option>
            <option value="prix-asc">Prix croissant</option>
            <option value="prix-desc">Prix décroissant</option>
          </select>
          <button type="button" onClick={() => setFiltersOpen(true)} aria-expanded={filtersOpen} className="flex h-11 items-center gap-2 border border-ivory/15 px-4 text-sm text-zinc-200 lg:hidden">
            <SlidersHorizontal className="h-4 w-4" /> Filtres
          </button>
        </div>
      </header>

      <div className="grid gap-10 lg:grid-cols-[240px_1fr]">
        <aside aria-label="Filtres" className="hidden lg:block">
          {sidebar}
        </aside>

        <div>
          {status === 'loading' && <ProductGridSkeleton count={6} />}

          {status === 'error' && (
            <div role="alert" className="py-20 text-center">
              <p className="text-display text-3xl">La vitrine ne répond pas.</p>
              <p className="mt-3 text-sm text-zinc-400">Vérifiez votre connexion puis réessayez.</p>
              <button type="button" onClick={load} className="mt-6 bg-ivory px-7 py-3.5 text-xs font-medium uppercase tracking-label text-ink-950 hover:bg-brass-300">
                Réessayer
              </button>
            </div>
          )}

          {status === 'ready' && filtered.length === 0 && (
            <div className="py-20 text-center">
              <p className="text-display text-3xl">{onlyFav ? 'Aucun favori pour l’instant.' : 'Rien ne correspond.'}</p>
              <p className="mt-3 text-sm text-zinc-400">{onlyFav ? 'Touchez le cœur d’une pièce pour la garder ici.' : 'Élargissez un filtre ou essayez un autre mot.'}</p>
              <button type="button" onClick={reset} className="mt-6 border border-ivory/20 px-7 py-3.5 text-xs uppercase tracking-label text-zinc-200 hover:border-brass-300">
                Tout afficher
              </button>
            </div>
          )}

          {status === 'ready' && filtered.length > 0 && (
            <motion.ul layout className="grid grid-cols-2 gap-x-4 gap-y-12 md:grid-cols-3">
              <AnimatePresence mode="popLayout" initial={false}>
                {filtered.map((a, i) => (
                  <motion.li
                    key={a.id}
                    layout
                    initial={{ opacity: 0, y: 24 }}
                    animate={{ opacity: 1, y: 0, transition: { delay: Math.min(i, 8) * 0.05, duration: 0.5, ease: [0.16, 1, 0.3, 1] } }}
                    exit={{ opacity: 0, scale: 0.96, transition: { duration: 0.2 } }}
                  >
                    <ProductCard article={a} priority={i < 2} sizes="(min-width: 1024px) 26vw, 50vw" />
                  </motion.li>
                ))}
              </AnimatePresence>
            </motion.ul>
          )}
        </div>
      </div>

      <AnimatePresence>
        {filtersOpen && (
          <div className="fixed inset-0 z-[70] lg:hidden" role="dialog" aria-modal="true" aria-label="Filtres">
            <motion.div className="absolute inset-0 bg-ink-950/70" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} onClick={() => setFiltersOpen(false)} />
            <motion.div
              className="absolute inset-x-0 bottom-0 max-h-[85dvh] overflow-y-auto bg-ink-900 px-6 pb-8 pt-4"
              initial={{ y: '100%' }}
              animate={{ y: 0 }}
              exit={{ y: '100%', transition: { duration: 0.22, ease: [0.4, 0, 1, 1] } }}
              transition={{ duration: 0.42, ease: [0.16, 1, 0.3, 1] }}
            >
              <div className="mb-4 flex items-center justify-between">
                <p className="text-display text-2xl">Filtres</p>
                <button type="button" onClick={() => setFiltersOpen(false)} aria-label="Fermer les filtres" className="grid h-11 w-11 place-items-center">
                  <X className="h-5 w-5" />
                </button>
              </div>
              {sidebar}
              <button type="button" onClick={() => setFiltersOpen(false)} className="tabular mt-6 h-14 w-full bg-ivory text-[13px] font-medium uppercase tracking-label text-ink-950">
                Voir {filtered.length} pièce{filtered.length > 1 ? 's' : ''}
              </button>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default function CataloguePage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-[1440px] px-[var(--gutter)] pt-16">
          <ProductGridSkeleton />
        </div>
      }
    >
      <CatalogueContent />
    </Suspense>
  );
}
