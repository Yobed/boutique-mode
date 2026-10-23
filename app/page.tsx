'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import ProductCard from '@/components/ProductCard';
import CartDrawer from '@/components/CartDrawer';
import StylistChatWidget from '@/components/StylistChatWidget';
import Footer from '@/components/Footer';
import { Article, CartItem } from '@/lib/types';
import { getArticles } from '@/lib/supabase';
import { Sparkles, ArrowRight, Flame, Award, TrendingUp } from 'lucide-react';

export default function HomePage() {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [stylistOpen, setStylistOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<'tous' | 'femme' | 'homme' | 'promo'>('tous');

  useEffect(() => {
    async function loadData() {
      try {
        const data = await getArticles();
        setArticles(data);
      } catch (err) {
        console.error('Erreur chargement articles:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();

    // Charger le panier depuis localStorage si disponible
    try {
      const savedCart = localStorage.getItem('boutique_cart');
      if (savedCart) setCartItems(JSON.parse(savedCart));
    } catch {}
  }, []);

  const saveCart = (items: CartItem[]) => {
    setCartItems(items);
    try {
      localStorage.setItem('boutique_cart', JSON.stringify(items));
    } catch {}
  };

  const handleAddToCart = (article: Article, taille: string, couleur: string) => {
    const existingIdx = cartItems.findIndex(
      (item) => item.article.id === article.id && item.taille === taille && item.couleur === couleur
    );

    let updated: CartItem[];
    if (existingIdx > -1) {
      updated = [...cartItems];
      updated[existingIdx].quantite += 1;
    } else {
      updated = [...cartItems, { article, taille, couleur, quantite: 1 }];
    }

    saveCart(updated);
    setCartOpen(true);
  };

  const handleUpdateQuantity = (index: number, newQty: number) => {
    if (newQty <= 0) {
      handleRemoveItem(index);
      return;
    }
    const updated = [...cartItems];
    updated[index].quantite = newQty;
    saveCart(updated);
  };

  const handleRemoveItem = (index: number) => {
    const updated = cartItems.filter((_, i) => i !== index);
    saveCart(updated);
  };

  const handleClearCart = () => {
    saveCart([]);
  };

  // Filtrage selon onglet actif
  const filteredArticles = articles.filter((a) => {
    if (activeTab === 'femme') return a.genre === 'femme';
    if (activeTab === 'homme') return a.genre === 'homme';
    if (activeTab === 'promo') return !!a.prix_promo;
    return true;
  });

  return (
    <>
      <Navbar
        cartItems={cartItems}
        onOpenCart={() => setCartOpen(true)}
        onOpenStylist={() => setStylistOpen(true)}
      />

      <main className="flex-1">
        {/* Hero Section */}
        <Hero onOpenStylist={() => setStylistOpen(true)} />

        {/* Categories Showcase Bar */}
        <section className="bg-dark-900 border-y border-white/10 py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
              <Link
                href="/catalogue?categorie=robes"
                className="p-4 rounded-xl bg-white/5 hover:bg-gold-500/10 border border-white/5 hover:border-gold-500/30 transition-all duration-200 ease-premium motion-hover-lift motion-press group"
              >
                <span className="block font-serif font-bold text-base text-white group-hover:text-gold-400">
                  Robes de Soirée
                </span>
                <span className="text-xs text-zinc-400">Élégance & Galas</span>
              </Link>
              <Link
                href="/catalogue?categorie=costumes"
                className="p-4 rounded-xl bg-white/5 hover:bg-gold-500/10 border border-white/5 hover:border-gold-500/30 transition-all duration-200 ease-premium motion-hover-lift motion-press group"
              >
                <span className="block font-serif font-bold text-base text-white group-hover:text-gold-400">
                  Costumes Homme
                </span>
                <span className="text-xs text-zinc-400">Coupes Sur Mesure</span>
              </Link>
              <Link
                href="/catalogue?categorie=chemises"
                className="p-4 rounded-xl bg-white/5 hover:bg-gold-500/10 border border-white/5 hover:border-gold-500/30 transition-all duration-200 ease-premium motion-hover-lift motion-press group"
              >
                <span className="block font-serif font-bold text-base text-white group-hover:text-gold-400">
                  Lin Pur & Wax
                </span>
                <span className="text-xs text-zinc-400">Chic Afro-Contemporain</span>
              </Link>
              <Link
                href="/catalogue?categorie=chaussures"
                className="p-4 rounded-xl bg-white/5 hover:bg-gold-500/10 border border-white/5 hover:border-gold-500/30 transition-all duration-200 ease-premium motion-hover-lift motion-press group"
              >
                <span className="block font-serif font-bold text-base text-white group-hover:text-gold-400">
                  Chaussures & Sacs
                </span>
                <span className="text-xs text-zinc-400">Cuir Véritable</span>
              </Link>
            </div>
          </div>
        </section>

        {/* Featured Products Grid */}
        <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10">
            <div>
              <div className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-gold-400 mb-2">
                <Flame className="w-4 h-4 text-amber-400" />
                <span>Nos Meilleures Ventes</span>
              </div>
              <h2 className="font-serif text-3xl sm:text-4xl font-bold text-white">
                Sélection Exclusive
              </h2>
            </div>

            {/* Filter Tabs */}
            <div className="flex flex-wrap gap-2 bg-dark-900 p-1.5 rounded-2xl border border-white/10">
              <button
                type="button"
                onClick={() => setActiveTab('tous')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-150 ease-premium motion-press ${
                  activeTab === 'tous'
                    ? 'bg-gold-500 text-dark-950 shadow-md'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Tous
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('femme')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-150 ease-premium motion-press ${
                  activeTab === 'femme'
                    ? 'bg-gold-500 text-dark-950 shadow-md'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Femme
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('homme')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-150 ease-premium motion-press ${
                  activeTab === 'homme'
                    ? 'bg-gold-500 text-dark-950 shadow-md'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                Homme
              </button>
              <button
                type="button"
                onClick={() => setActiveTab('promo')}
                className={`px-4 py-2 rounded-xl text-xs font-bold transition-all duration-150 ease-premium motion-press ${
                  activeTab === 'promo'
                    ? 'bg-red-600 text-white shadow-md'
                    : 'text-zinc-400 hover:text-white'
                }`}
              >
                En Promo 🔥
              </button>
            </div>
          </div>

          {/* Grid */}
          {loading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-6">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="animate-pulse bg-dark-900 border border-white/5 rounded-2xl h-80" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5 sm:gap-6">
              {filteredArticles.map((article) => (
                <ProductCard
                  key={article.id}
                  article={article}
                  onAddToCart={handleAddToCart}
                />
              ))}
            </div>
          )}

          {/* View All CTA */}
          <div className="mt-14 text-center">
            <Link
              href="/catalogue"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white/10 hover:bg-gold-500 hover:text-dark-950 border border-white/20 text-white font-bold text-sm tracking-wide transition-all duration-200 ease-premium motion-press shadow-xl"
            >
              <span>Voir Tous les 50+ Vêtements</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </section>

        {/* Atelier Stylist Feature Banner */}
        <section className="bg-gradient-to-r from-dark-900 via-atelier-deep/30 to-dark-900 border-y border-white/10 py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
              <div className="space-y-4">
                <div className="inline-flex items-center gap-2 px-3.5 py-1 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-300 text-xs font-bold uppercase tracking-wider">
                  <Sparkles className="w-3.5 h-3.5 text-gold-400" />
                  Service Privé d'Atelier
                </div>
                <h3 className="font-serif text-3xl sm:text-4xl font-normal text-white">
                  Besoin d'un Conseil Coupe ou Style ? <br />
                  <span className="text-gold-400 italic">Échangez avec Sophia</span>
                </h3>
                <p className="text-zinc-300 text-sm leading-relaxed">
                  Notre première d'atelier analyse vos mensurations, l'occasion prévue (mariage, cocktail, d'affaires) et vos préférences de tissus pour vous recommander la tenue parfaite disponible immédiatement.
                </p>
                <div className="pt-2 flex flex-wrap gap-4">
                  <button
                    onClick={() => setStylistOpen(true)}
                    className="px-6 py-3.5 rounded-full bg-gold-500 hover:bg-gold-400 text-dark-950 font-bold text-xs uppercase tracking-wider shadow-lg shadow-gold-500/20 transition-all duration-200 ease-premium motion-press"
                  >
                    Consulter la Styliste Privée
                  </button>
                  <a
                    href="https://wa.me/2250778311541?text=Bonjour%20Sophia,%20je%20souhaite%20un%20conseil%20style"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-6 py-3.5 rounded-full bg-emerald-600/20 hover:bg-emerald-600 border border-emerald-500/40 text-emerald-300 hover:text-white font-bold text-xs uppercase tracking-wider transition-all duration-200 ease-premium motion-press"
                  >
                    Discuter sur WhatsApp
                  </a>
                </div>
              </div>

              <div className="p-6 rounded-3xl bg-dark-950/80 border border-white/10 space-y-4 shadow-2xl">
                <div className="flex items-center gap-3 pb-3 border-b border-white/10">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                  <span className="text-xs text-zinc-400 font-mono pl-2">Discussion en direct avec Sophia</span>
                </div>
                <div className="space-y-3 text-xs">
                  <div className="bg-white/5 p-3 rounded-2xl text-zinc-300 self-start max-w-[85%]">
                    💬 <em>"Je cherche une robe pour un mariage samedi à Cocody, taille M, chic mais pas trop voyante."</em>
                  </div>
                  <div className="bg-gold-500/10 border border-gold-500/30 p-3 rounded-2xl text-gold-200 self-end max-w-[90%]">
                    ✨ <strong>Sophia :</strong> <em>"Magnifique ! Je vous recommande notre Robe Soirée Émeraude Satinée en taille M (32 000 FCFA). Son tomber fluide est divin avec des escarpins nude."</em>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* L'Atelier & Le Savoir-Faire Ébène & Or */}
        <section className="py-20 bg-dark-950 border-b border-white/10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center max-w-2xl mx-auto space-y-3 mb-14">
              <span className="text-xs uppercase tracking-widest text-gold-400 font-semibold">
                L'Engagement Maison Élégance
              </span>
              <h2 className="font-serif text-3xl sm:text-4xl font-normal text-white">
                L'Art du Vêtement Parfait à Abidjan
              </h2>
              <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
                Chaque pièce est sélectionnée, repassée à la vapeur en atelier et livrée sous housse zippée avec cintre en bois protecteur.
              </p>
            </div>

            {/* 3 Pillars Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="p-8 rounded-3xl bg-dark-900 border border-white/5 space-y-3 motion-hover-lift">
                <span className="font-serif text-3xl font-light text-gold-400">01</span>
                <h3 className="font-serif text-lg font-bold text-white">Fibres Nobles & Teintures Fixées</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Lin européen thermorégulateur idéal pour le climat tropical abidjanais, crêpe de soie lourd et cotons peignés résistants aux lavages répétés.
                </p>
              </div>

              <div className="p-8 rounded-3xl bg-dark-900 border border-white/5 space-y-3 motion-hover-lift">
                <span className="font-serif text-3xl font-light text-gold-400">02</span>
                <h3 className="font-serif text-lg font-bold text-white">Essayage Libre à la Livraison</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Notre coursier express patiente pendant que vous essayez vos vêtements. Si la coupe ne vous convient pas, aucun engagement, vous ne payez rien.
                </p>
              </div>

              <div className="p-8 rounded-3xl bg-dark-900 border border-white/5 space-y-3 motion-hover-lift">
                <span className="font-serif text-3xl font-light text-gold-400">03</span>
                <h3 className="font-serif text-lg font-bold text-white">Retouches & Ajustements Gratuits</h3>
                <p className="text-xs text-zinc-400 leading-relaxed">
                  Un bas de pantalon à raccourcir ou une taille à cintrer ? Notre maître tailleur prend en charge les ajustements sans frais supplémentaires sous 48h.
                </p>
              </div>
            </div>

            {/* Verified Testimonials */}
            <div className="mt-16 pt-12 border-t border-white/10">
              <h3 className="font-serif text-xl font-normal text-center text-white mb-8">
                Paroles de Nos Clients à Abidjan
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                  <p className="text-xs text-zinc-300 italic leading-relaxed">
                    « J'avais un gala au Sofitel Ivoire samedi soir et pas de tenue. Commande passée vendredi 14h, reçue à 17h à Cocody Danga. La robe émeraude a fait l'unanimité ! »
                  </p>
                  <div className="flex items-center gap-2 pt-2 border-t border-white/5 text-[11px]">
                    <span className="font-bold text-gold-300">Amina K.</span>
                    <span className="text-zinc-500">• Cocody Deux Plateaux</span>
                  </div>
                </div>

                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                  <p className="text-xs text-zinc-300 italic leading-relaxed">
                    « Le costume en lin beige est une merveille. Tissu très respirant en salle de conférence. Le coursier a attendu que j'essaie la veste avant que je valide le paiement Wave. »
                  </p>
                  <div className="flex items-center gap-2 pt-2 border-t border-white/5 text-[11px]">
                    <span className="font-bold text-gold-300">Jean-Marc B.</span>
                    <span className="text-zinc-500">• Plateau & Zone 4</span>
                  </div>
                </div>

                <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 space-y-3">
                  <p className="text-xs text-zinc-300 italic leading-relaxed">
                    « La styliste Sophia sur le site m'a directement orienté vers la taille L selon mon tour de poitrine. Recommandation parfaite, aucune retouche nécessaire. »
                  </p>
                  <div className="flex items-center gap-2 pt-2 border-t border-white/5 text-[11px]">
                    <span className="font-bold text-gold-300">Fatou D.</span>
                    <span className="text-zinc-500">• Marcory Residentiel</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Cart Drawer */}
      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        cartItems={cartItems}
        onUpdateQuantity={handleUpdateQuantity}
        onRemoveItem={handleRemoveItem}
        onClearCart={handleClearCart}
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
