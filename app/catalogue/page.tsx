'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import ProductCard from '@/components/ProductCard';
import FilterSidebar from '@/components/FilterSidebar';
import CartDrawer from '@/components/CartDrawer';
import StylistChatWidget from '@/components/StylistChatWidget';
import Footer from '@/components/Footer';
import { Article, CartItem, CategorieVêtement, GenreVêtement } from '@/lib/types';
import { getArticles } from '@/lib/supabase';
import { Search, SlidersHorizontal, ArrowUpDown } from 'lucide-react';

function CatalogueContent() {
  const searchParams = useSearchParams();
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [stylistOpen, setStylistOpen] = useState(false);
  const [mobileFilterOpen, setMobileFilterOpen] = useState(false);

  // Filtres
  const [searchQuery, setSearchQuery] = useState('');
  const [categorie, setCategorie] = useState<CategorieVêtement>(
    (searchParams.get('categorie') as CategorieVêtement) || 'tous'
  );
  const [genre, setGenre] = useState<GenreVêtement>(
    (searchParams.get('genre') as GenreVêtement) || 'tous'
  );
  const [taille, setTaille] = useState('');
  const [maxPrice, setMaxPrice] = useState(100000);
  const [onlyPromo, setOnlyPromo] = useState(searchParams.get('promo') === 'true');
  const [sortBy, setSortBy] = useState<'populaire' | 'prix-asc' | 'prix-desc'>('populaire');

  useEffect(() => {
    async function load() {
      try {
        const data = await getArticles();
        setArticles(data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    load();

    try {
      const saved = localStorage.getItem('boutique_cart');
      if (saved) setCartItems(JSON.parse(saved));
    } catch {}
  }, []);

  const saveCart = (items: CartItem[]) => {
    setCartItems(items);
    try {
      localStorage.setItem('boutique_cart', JSON.stringify(items));
    } catch {}
  };

  const handleAddToCart = (article: Article, t: string, c: string) => {
    const existing = cartItems.findIndex(
      (item) => item.article.id === article.id && item.taille === t && item.couleur === c
    );
    let updated: CartItem[];
    if (existing > -1) {
      updated = [...cartItems];
      updated[existing].quantite += 1;
    } else {
      updated = [...cartItems, { article, taille: t, couleur: c, quantite: 1 }];
    }
    saveCart(updated);
    setCartOpen(true);
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setCategorie('tous');
    setGenre('tous');
    setTaille('');
    setMaxPrice(100000);
    setOnlyPromo(false);
  };

  // Filtrage
  const filtered = articles
    .filter((item) => {
      // Recherche
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const mName = item.nom.toLowerCase().includes(q);
        const mDesc = item.description.toLowerCase().includes(q);
        const mCat = item.categorie.toLowerCase().includes(q);
        if (!mName && !mDesc && !mCat) return false;
      }
      // Catégorie
      if (categorie !== 'tous' && item.categorie !== categorie) return false;
      // Genre
      if (genre !== 'tous' && item.genre !== genre && item.genre !== 'mixte') return false;
      // Taille
      if (taille && !item.tailles.includes(taille)) return false;
      // Budget
      if (maxPrice < 100000 && (item.prix_promo || item.prix) > maxPrice) return false;
      // Promo
      if (onlyPromo && !item.prix_promo) return false;

      return true;
    })
    .sort((a, b) => {
      const pA = a.prix_promo || a.prix;
      const pB = b.prix_promo || b.prix;
      if (sortBy === 'prix-asc') return pA - pB;
      if (sortBy === 'prix-desc') return pB - pA;
      return 0; // populaire
    });

  return (
    <>
      <Navbar
        cartItems={cartItems}
        onOpenCart={() => setCartOpen(true)}
        onOpenStylist={() => setStylistOpen(true)}
      />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
        {/* Top Header & Search Bar */}
        <div className="mb-8 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-white">
                Catalogue Prêt-à-Porter
              </h1>
              <p className="text-zinc-400 text-xs mt-1">
                {filtered.length} article{filtered.length > 1 ? 's' : ''} disponible{filtered.length > 1 ? 's' : ''} immédiatement à Abidjan
              </p>
            </div>

            {/* Sort & Mobile Filter Toggle */}
            <div className="flex items-center gap-3">
              <button
                onClick={() => setMobileFilterOpen(!mobileFilterOpen)}
                className="lg:hidden flex items-center gap-2 px-4 py-2.5 rounded-xl bg-dark-900 border border-white/10 text-white text-xs font-semibold"
              >
                <SlidersHorizontal className="w-4 h-4 text-gold-400" />
                <span>Filtres</span>
              </button>

              <div className="flex items-center gap-2 bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-xs">
                <ArrowUpDown className="w-3.5 h-3.5 text-zinc-400" />
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as any)}
                  className="bg-transparent text-white focus:outline-none cursor-pointer"
                >
                  <option value="populaire" className="bg-dark-900">Les plus populaires</option>
                  <option value="prix-asc" className="bg-dark-900">Prix croissant</option>
                  <option value="prix-desc" className="bg-dark-900">Prix décroissant</option>
                </select>
              </div>
            </div>
          </div>

          {/* Search Box */}
          <div className="relative">
            <Search className="w-5 h-5 text-zinc-400 absolute left-4 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Rechercher une robe, un costume, du lin, du wax, une chemise..."
              className="w-full bg-dark-900 border border-white/10 rounded-2xl pl-12 pr-4 py-3.5 text-sm text-white placeholder-zinc-500 focus:outline-none focus:border-gold-500 shadow-md"
            />
          </div>
        </div>

        {/* Content Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar Desktop */}
          <div className="hidden lg:block lg:col-span-1">
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
              onReset={handleResetFilters}
            />
          </div>

          {/* Mobile Filter Modal */}
          {mobileFilterOpen && (
            <div className="lg:hidden fixed inset-0 z-50 bg-black/80 backdrop-blur-sm p-4 overflow-y-auto">
              <div className="max-w-md mx-auto">
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
                  onReset={handleResetFilters}
                />
                <button
                  onClick={() => setMobileFilterOpen(false)}
                  className="w-full mt-4 py-3 bg-gold-500 text-dark-950 font-bold rounded-xl text-sm"
                >
                  Appliquer les filtres
                </button>
              </div>
            </div>
          )}

          {/* Product Grid */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-5">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="animate-pulse bg-dark-900 border border-white/5 rounded-2xl h-80" />
                ))}
              </div>
            ) : filtered.length === 0 ? (
              <div className="py-20 text-center space-y-3 bg-dark-900 border border-white/5 rounded-3xl p-8">
                <p className="text-zinc-400 text-sm">
                  Aucun vêtement ne correspond à vos critères de recherche.
                </p>
                <button
                  onClick={handleResetFilters}
                  className="px-5 py-2.5 rounded-full bg-gold-500 text-dark-950 font-bold text-xs uppercase tracking-wider"
                >
                  Réinitialiser les filtres
                </button>
              </div>
            ) : (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-5">
                {filtered.map((article) => (
                  <ProductCard
                    key={article.id}
                    article={article}
                    onAddToCart={handleAddToCart}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Cart Drawer */}
      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        cartItems={cartItems}
        onUpdateQuantity={(idx, q) => {
          const upd = [...cartItems];
          if (q <= 0) upd.splice(idx, 1);
          else upd[idx].quantite = q;
          saveCart(upd);
        }}
        onRemoveItem={(idx) => {
          const upd = cartItems.filter((_, i) => i !== idx);
          saveCart(upd);
        }}
        onClearCart={() => saveCart([])}
      />

      {/* Stylist Chat Widget */}
      <StylistChatWidget
        isOpen={stylistOpen}
        onToggle={() => setStylistOpen(!stylistOpen)}
        onAddToCart={handleAddToCart}
      />

      <Footer />
    </>
  );
}

export default function CataloguePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-dark-950 flex items-center justify-center text-zinc-400">Chargement du catalogue...</div>}>
      <CatalogueContent />
    </Suspense>
  );
}
