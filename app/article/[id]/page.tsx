'use client';

import React, { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import Navbar from '@/components/Navbar';
import CartDrawer from '@/components/CartDrawer';
import StylistChatWidget from '@/components/StylistChatWidget';
import SizeGuideModal from '@/components/SizeGuideModal';
import Footer from '@/components/Footer';
import { Article, CartItem } from '@/lib/types';
import { getArticleById, getArticles } from '@/lib/supabase';
import { ShoppingBag, MessageCircle, ArrowLeft, Check, ShieldCheck, Truck, Sparkles, Ruler, RefreshCw, Scissors } from 'lucide-react';

export default function ArticleDetailPage() {
  const params = useParams();
  const id = params?.id as string;

  const [article, setArticle] = useState<Article | null>(null);
  const [related, setRelated] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedPhoto, setSelectedPhoto] = useState<string>('');
  const [selectedTaille, setSelectedTaille] = useState<string>('');
  const [selectedCouleur, setSelectedCouleur] = useState<string>('');
  const [added, setAdded] = useState(false);

  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [stylistOpen, setStylistOpen] = useState(false);
  const [sizeGuideOpen, setSizeGuideOpen] = useState(false);

  useEffect(() => {
    async function load() {
      if (!id) return;
      try {
        const item = await getArticleById(id);
        if (item) {
          setArticle(item);
          setSelectedPhoto(item.photos[0] || '');
          setSelectedTaille(item.tailles[0] || 'Standard');
          setSelectedCouleur(item.couleurs[0] || 'Standard');
        }

        const all = await getArticles();
        setRelated(all.filter((a) => a.id !== id).slice(0, 4));
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
  }, [id]);

  const saveCart = (items: CartItem[]) => {
    setCartItems(items);
    try {
      localStorage.setItem('boutique_cart', JSON.stringify(items));
    } catch {}
  };

  const handleAddToCart = () => {
    if (!article) return;
    const existing = cartItems.findIndex(
      (item) => item.article.id === article.id && item.taille === selectedTaille && item.couleur === selectedCouleur
    );

    let updated: CartItem[];
    if (existing > -1) {
      updated = [...cartItems];
      updated[existing].quantite += 1;
    } else {
      updated = [...cartItems, { article, taille: selectedTaille, couleur: selectedCouleur, quantite: 1 }];
    }

    saveCart(updated);
    setAdded(true);
    setCartOpen(true);
    setTimeout(() => setAdded(false), 2000);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center text-zinc-400">
        Chargement de l'article...
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen bg-dark-950 flex flex-col items-center justify-center text-center p-6 space-y-4">
        <h1 className="font-serif text-2xl font-bold text-white">Vêtement introuvable</h1>
        <p className="text-zinc-400 text-sm">Cet article n'existe plus ou est en cours de réapprovisionnement.</p>
        <Link href="/catalogue" className="px-6 py-2.5 rounded-full bg-gold-500 text-dark-950 font-bold text-xs">
          Retour au catalogue
        </Link>
      </div>
    );
  }

  const whatsappMsg = encodeURIComponent(
    `Bonjour Maison Élégance ! Je souhaite commander cet article :\n\n` +
    `👗 Produit : *${article.nom}*\n` +
    `📏 Taille : *${selectedTaille}*\n` +
    `🎨 Couleur : *${selectedCouleur}*\n` +
    `💰 Prix : *${(article.prix_promo || article.prix).toLocaleString('fr-FR')} FCFA*\n` +
    `📸 Photo : ${selectedPhoto}\n\n` +
    `Quelle est la disponibilité pour une livraison à Abidjan ?`
  );

  return (
    <>
      <Navbar
        cartItems={cartItems}
        onOpenCart={() => setCartOpen(true)}
        onOpenStylist={() => setStylistOpen(true)}
      />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 w-full">
        {/* Back link */}
        <Link
          href="/catalogue"
          className="inline-flex items-center gap-2 text-xs font-semibold text-zinc-400 hover:text-gold-400 transition-colors mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Retour au catalogue</span>
        </Link>

        {/* Product Details Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-10">
          {/* Images Gallery */}
          <div className="space-y-4">
            <div className="aspect-[3/4] w-full rounded-3xl overflow-hidden bg-dark-900 border border-white/10 shadow-2xl">
              <img
                src={selectedPhoto}
                alt={article.nom}
                className="w-full h-full object-cover object-center"
              />
            </div>

            {article.photos.length > 1 && (
              <div className="flex gap-3 overflow-x-auto pb-2">
                {article.photos.map((p, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setSelectedPhoto(p)}
                    className={`w-20 h-24 rounded-xl overflow-hidden border-2 transition-all duration-150 ease-premium motion-press flex-shrink-0 ${
                      selectedPhoto === p ? 'border-gold-400 scale-105' : 'border-white/10 opacity-70 hover:opacity-100'
                    }`}
                  >
                    <img src={p} alt="" className="w-full h-full object-cover" />
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Product Info */}
          <div className="space-y-6 flex flex-col justify-between">
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-xs text-zinc-400">
                <span className="capitalize font-semibold text-gold-400">{article.categorie}</span>
                <span>•</span>
                <span className="capitalize">{article.genre}</span>
                <span>•</span>
                <span className="text-emerald-400 font-medium">En stock ({article.quantite_stock} disponibles)</span>
              </div>

              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-white leading-tight">
                {article.nom}
              </h1>

              {/* Price */}
              <div className="flex items-baseline gap-3 pt-1">
                <span className="text-gold-400 font-bold text-3xl">
                  {(article.prix_promo || article.prix).toLocaleString('fr-FR')} FCFA
                </span>
                {article.prix_promo && (
                  <span className="text-zinc-500 text-base line-through">
                    {article.prix.toLocaleString('fr-FR')} FCFA
                  </span>
                )}
              </div>

              {/* Description */}
              <div className="pt-2 border-t border-white/10 text-sm text-zinc-300 leading-relaxed space-y-2">
                <p>{article.description}</p>
              </div>

              {/* Size Selector with Guide Button */}
              <div className="pt-4 space-y-2.5">
                <div className="flex justify-between items-center text-xs">
                  <span className="font-bold text-white uppercase tracking-wider">
                    Choisir votre Taille :
                  </span>
                  <div className="flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => setSizeGuideOpen(true)}
                      className="text-gold-400 hover:text-gold-300 flex items-center gap-1 font-semibold underline underline-offset-4 transition-colors"
                    >
                      <Ruler className="w-3.5 h-3.5" />
                      <span>Guide des Tailles</span>
                    </button>
                    <span className="text-zinc-600">•</span>
                    <button
                      type="button"
                      onClick={() => setStylistOpen(true)}
                      className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-semibold transition-colors"
                    >
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Avis Styliste</span>
                    </button>
                  </div>
                </div>
                <div className="flex flex-wrap gap-2">
                  {article.tailles.map((t) => (
                    <button
                      key={t}
                      type="button"
                      onClick={() => setSelectedTaille(t)}
                      className={`px-4 py-2 text-sm font-bold rounded-xl border transition-all duration-150 ease-premium motion-press ${
                        selectedTaille === t
                          ? 'border-gold-400 bg-gold-400/20 text-gold-300 shadow-md'
                          : 'border-white/10 bg-dark-900 text-zinc-300 hover:border-white/30'
                      }`}
                    >
                      {t}
                    </button>
                  ))}
                </div>
              </div>

              {/* Color Selector */}
              {article.couleurs.length > 0 && (
                <div className="pt-2 space-y-2">
                  <span className="text-xs font-bold text-white uppercase tracking-wider block">
                    Couleur : <span className="text-gold-400 font-normal">{selectedCouleur}</span>
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {article.couleurs.map((c) => (
                      <button
                        key={c}
                        type="button"
                        onClick={() => setSelectedCouleur(c)}
                        className={`px-3 py-1.5 text-xs font-semibold rounded-lg border transition-all duration-150 ease-premium motion-press ${
                          selectedCouleur === c
                            ? 'border-gold-400 bg-gold-400/20 text-gold-300'
                            : 'border-white/10 bg-dark-900 text-zinc-400 hover:border-white/20'
                        }`}
                      >
                        {c}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="pt-6 border-t border-white/10 space-y-3">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={handleAddToCart}
                  className={`w-full py-4 px-6 rounded-2xl font-bold text-sm flex items-center justify-center gap-2 transition-all duration-150 ease-premium motion-press shadow-xl ${
                    added
                      ? 'bg-emerald-600 text-white'
                      : 'bg-gold-500 hover:bg-gold-400 text-dark-950 shadow-gold-500/20'
                  }`}
                >
                  {added ? (
                    <>
                      <Check className="w-5 h-5" />
                      <span>Ajouté au panier !</span>
                    </>
                  ) : (
                    <>
                      <ShoppingBag className="w-5 h-5" />
                      <span>Ajouter au Panier</span>
                    </>
                  )}
                </button>

                <a
                  href={`https://wa.me/2250778311541?text=${whatsappMsg}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-full py-4 px-6 rounded-2xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-xl shadow-emerald-600/20 transition-all duration-150 ease-premium motion-press"
                >
                  <MessageCircle className="w-5 h-5" />
                  <span>Commander sur WhatsApp</span>
                </a>
              </div>

              {/* Guarantees Box */}
              <div className="p-4 rounded-2xl bg-dark-900 border border-white/10 grid grid-cols-2 gap-3 text-xs text-zinc-400">
                <div className="flex items-center gap-2">
                  <Truck className="w-4 h-4 text-gold-400 flex-shrink-0" />
                  <span>Livraison 24h à Abidjan</span>
                </div>
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-gold-400 flex-shrink-0" />
                  <span>Paiement à la réception</span>
                </div>
                <div className="flex items-center gap-2">
                  <RefreshCw className="w-4 h-4 text-gold-400 flex-shrink-0" />
                  <span>Échange gratuit 48h</span>
                </div>
                <div className="flex items-center gap-2">
                  <Scissors className="w-4 h-4 text-gold-400 flex-shrink-0" />
                  <span>Retouches atelier offertes</span>
                </div>
              </div>

              {/* Fabric & Care Accordion */}
              <div className="p-4 rounded-2xl bg-dark-950 border border-white/5 space-y-2 text-xs">
                <h4 className="font-serif font-bold text-gold-300 uppercase tracking-wider">
                  Matières & Entretien d'Atelier
                </h4>
                <p className="text-zinc-400 leading-relaxed">
                  Confectionné à partir de fibres nobles (coton peigné, lin pur ou soies italiennes selon le modèle). Lavage délicat à la main ou en machine à 30°C avec couleurs similaires. Repassage doux à la vapeur sur l'envers.
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Mobile Sticky Buy Bar (Fixed on Small Screens) */}
      <div className="sm:hidden fixed bottom-0 inset-x-0 z-30 p-3 bg-dark-950/95 border-t border-white/10 backdrop-blur-xl flex items-center justify-between gap-3 shadow-2xl">
        <div>
          <span className="text-[10px] text-zinc-400 block">Taille : {selectedTaille}</span>
          <span className="font-bold text-gold-400 text-sm">
            {(article.prix_promo || article.prix).toLocaleString('fr-FR')} FCFA
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleAddToCart}
            className="p-3 rounded-xl bg-white/10 text-white font-bold text-xs duration-150 ease-premium motion-press"
            title="Ajouter au panier"
          >
            <ShoppingBag className="w-4 h-4" />
          </button>

          <a
            href={`https://wa.me/2250778311541?text=${whatsappMsg}`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-4 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs flex items-center gap-1.5 duration-150 ease-premium motion-press whitespace-nowrap shadow-lg shadow-emerald-900/30"
          >
            <MessageCircle className="w-4 h-4" />
            <span>Commander WhatsApp</span>
          </a>
        </div>
      </div>

      {/* Size Guide Modal */}
      <SizeGuideModal
        isOpen={sizeGuideOpen}
        onClose={() => setSizeGuideOpen(false)}
        onOpenStylist={() => setStylistOpen(true)}
      />

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
        onAddToCart={(art, t, c) => {
          handleAddToCart();
        }}
      />

      <Footer />
    </>
  );
}
