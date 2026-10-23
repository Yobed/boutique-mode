'use client';

import React, { useState } from 'react';
import { Article } from '@/lib/types';
import { ShoppingBag, MessageCircle, Check, Eye } from 'lucide-react';
import Link from 'next/link';

interface ProductCardProps {
  article: Article;
  onAddToCart: (article: Article, taille: string, couleur: string) => void;
}

export default function ProductCard({ article, onAddToCart }: ProductCardProps) {
  const [selectedTaille, setSelectedTaille] = useState<string>(article.tailles[0] || 'Standard');
  const [selectedCouleur, setSelectedCouleur] = useState<string>(article.couleurs[0] || 'Couleur unique');
  const [added, setAdded] = useState(false);

  const handleAdd = () => {
    onAddToCart(article, selectedTaille, selectedCouleur);
    setAdded(true);
    setTimeout(() => setAdded(false), 2000);
  };

  const whatsappText = encodeURIComponent(
    `Bonjour Maison Élégance ! Je souhaite commander cet article :\n\n` +
    `👗 Produit : *${article.nom}*\n` +
    `📏 Taille : *${selectedTaille}*\n` +
    `🎨 Couleur : *${selectedCouleur}*\n` +
    `💰 Prix : *${(article.prix_promo || article.prix).toLocaleString('fr-FR')} FCFA*\n` +
    `📸 Photo : ${article.photos[0] || ''}\n\n` +
    `Est-il disponible pour livraison ?`
  );

  return (
    <div className="group relative bg-dark-900 border border-white/10 rounded-2xl overflow-hidden motion-hover-lift hover:border-gold-500/50 flex flex-col justify-between">
      {/* Image Container */}
      <div className="relative aspect-[3/4] w-full overflow-hidden bg-zinc-900">
        <img
          src={article.photos[0]}
          alt={article.nom}
          className="w-full h-full object-cover object-center motion-img-zoom"
          loading="lazy"
        />

        {/* Badges */}
        <div className="absolute top-3 left-3 flex flex-col gap-1.5 z-10">
          {article.prix_promo && (
            <span className="bg-red-600 text-white text-[11px] font-black px-2.5 py-1 rounded-md shadow-md uppercase tracking-wider">
              Promo -{Math.round(((article.prix - article.prix_promo) / article.prix) * 100)}%
            </span>
          )}
          {article.nouveaute && !article.prix_promo && (
            <span className="bg-gold-500 text-dark-950 text-[11px] font-black px-2.5 py-1 rounded-md shadow-md uppercase tracking-wider">
              Nouveau
            </span>
          )}
          {article.vedette && (
            <span className="bg-purple-600/90 text-white text-[10px] font-bold px-2 py-0.5 rounded shadow uppercase tracking-wider">
              Coup de Cœur
            </span>
          )}
        </div>

        {/* Quick View Link */}
        <Link
          href={`/article/${article.id}`}
          className="absolute top-3 right-3 p-2 rounded-full bg-dark-950/70 text-zinc-300 hover:text-white hover:bg-dark-950 transition-all duration-200 ease-premium motion-press opacity-0 group-hover:opacity-100"
          title="Voir la fiche détaillée"
        >
          <Eye className="w-4 h-4" />
        </Link>
      </div>

      {/* Content */}
      <div className="p-4 sm:p-5 flex-1 flex flex-col justify-between">
        <div>
          <div className="flex items-center justify-between text-xs text-zinc-400 mb-1">
            <span className="capitalize">{article.categorie}</span>
            <span className="capitalize text-zinc-500 font-medium">{article.genre}</span>
          </div>

          <Link href={`/article/${article.id}`} className="group-hover:text-gold-400 transition-colors">
            <h3 className="font-serif font-bold text-white text-base leading-snug line-clamp-1">
              {article.nom}
            </h3>
          </Link>

          <p className="text-zinc-400 text-xs mt-1.5 line-clamp-2 leading-relaxed">
            {article.description}
          </p>

          {/* Price */}
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-gold-400 font-bold text-lg">
              {(article.prix_promo || article.prix).toLocaleString('fr-FR')} FCFA
            </span>
            {article.prix_promo && (
              <span className="text-zinc-500 text-xs line-through">
                {article.prix.toLocaleString('fr-FR')} FCFA
              </span>
            )}
          </div>

          {/* Size Selector */}
          <div className="mt-3">
            <span className="text-[11px] text-zinc-400 block mb-1">Taille :</span>
            <div className="flex flex-wrap gap-1.5">
              {article.tailles.map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setSelectedTaille(t)}
                  className={`px-2.5 py-1 text-xs font-semibold rounded-lg border transition-all duration-150 ease-premium motion-press ${
                    selectedTaille === t
                      ? 'border-gold-400 bg-gold-400/10 text-gold-300 shadow-sm'
                      : 'border-white/10 bg-white/5 text-zinc-400 hover:border-white/20'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-4 pt-3 border-t border-white/5 grid grid-cols-2 gap-2">
          {/* Add to Cart */}
          <button
            onClick={handleAdd}
            className={`flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl text-xs font-bold transition-all duration-150 ease-premium motion-press ${
              added
                ? 'bg-emerald-600 text-white'
                : 'bg-white/10 hover:bg-gold-500 hover:text-dark-950 text-white border border-white/10'
            }`}
          >
            {added ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Ajouté</span>
              </>
            ) : (
              <>
                <ShoppingBag className="w-3.5 h-3.5 text-gold-400 group-hover:text-dark-950" />
                <span>Panier</span>
              </>
            )}
          </button>

          {/* WhatsApp 1-Click Order */}
          <a
            href={`https://wa.me/2250778311541?text=${whatsappText}`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-center gap-1.5 py-2.5 px-3 rounded-xl bg-emerald-600/20 hover:bg-emerald-600 border border-emerald-500/40 text-emerald-300 hover:text-white text-xs font-bold transition-all duration-150 ease-premium motion-press"
            title="Commander directement sur WhatsApp"
          >
            <MessageCircle className="w-3.5 h-3.5" />
            <span>WhatsApp</span>
          </a>
        </div>
      </div>
    </div>
  );
}
