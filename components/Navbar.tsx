'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ShoppingBag, Sparkles, MessageCircle, Menu, X } from 'lucide-react';
import { CartItem } from '@/lib/types';

interface NavbarProps {
  cartItems: CartItem[];
  onOpenCart: () => void;
  onOpenStylist: () => void;
}

export default function Navbar({ cartItems, onOpenCart, onOpenStylist }: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const totalCount = cartItems.reduce((acc, item) => acc + item.quantite, 0);

  return (
    <header className="sticky top-0 z-40 bg-dark-950/90 backdrop-blur-md border-b border-white/10 text-white">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-gold-600 via-gold-400 to-gold-600 text-dark-950 text-xs font-bold py-1.5 text-center px-4 tracking-wide uppercase">
        ✨ Livraison express en 24h à Abidjan & Intérieur — Paiement à la livraison ou Wave / Mobile Money
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-10 h-10 rounded-full bg-gold-500 flex items-center justify-center text-dark-950 font-serif font-black text-xl shadow-lg shadow-gold-500/20 group-hover:scale-105 transition-transform">
            M
          </div>
          <div>
            <span className="font-serif text-xl sm:text-2xl font-normal tracking-wider text-white">
              MAISON <span className="text-gold-400 italic">ÉLÉGANCE</span>
            </span>
            <span className="block text-[10px] text-zinc-400 tracking-widest uppercase font-medium">
              Prêt-à-Porter & Atelier Abidjan
            </span>
          </div>
        </Link>

        {/* Desktop Nav Links */}
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-300">
          <Link href="/" className="hover:text-gold-400 transition-colors">
            Accueil
          </Link>
          <Link href="/catalogue" className="hover:text-gold-400 transition-colors">
            Catalogue
          </Link>
          <Link href="/catalogue?genre=femme" className="hover:text-gold-400 transition-colors">
            Femme
          </Link>
          <Link href="/catalogue?genre=homme" className="hover:text-gold-400 transition-colors">
            Homme
          </Link>
          <Link href="/catalogue?promo=true" className="text-amber-400 font-semibold hover:text-amber-300 transition-colors">
            Promotions
          </Link>
          <Link href="/suivi" className="hover:text-gold-400 transition-colors text-xs uppercase tracking-wider text-zinc-400">
            Suivi Commande
          </Link>
        </nav>

        {/* Action Buttons */}
        <div className="flex items-center gap-3">
          {/* Styliste Atelier Button */}
          <button
            onClick={onOpenStylist}
            className="flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-200 text-xs sm:text-sm font-semibold hover:border-gold-400 hover:text-white transition-all duration-150 ease-premium motion-press shadow-sm shadow-emerald-900/30"
            title="Consulter Sophia, notre styliste d'atelier"
          >
            <Sparkles className="w-3.5 h-3.5 text-gold-400 animate-pulse-subtle" />
            <span className="hidden sm:inline">Styliste Privée</span>
          </button>

          {/* WhatsApp Direct */}
          <a
            href="https://wa.me/2250778311541?text=Bonjour%20Boutique%20en%20Ligne,%20je%20souhaite%20des%20renseignements%20sur%20vos%20v%C3%AAtements"
            target="_blank"
            rel="noopener noreferrer"
            className="p-2.5 rounded-full bg-emerald-950/80 border border-emerald-500/30 text-emerald-400 hover:bg-emerald-900/80 transition-all duration-150 ease-premium motion-press"
            title="Nous écrire sur WhatsApp"
          >
            <MessageCircle className="w-5 h-5" />
          </a>

          {/* Cart Button */}
          <button
            onClick={onOpenCart}
            className="relative p-2.5 rounded-full bg-white/5 border border-white/10 hover:border-gold-500/50 hover:bg-white/10 text-white transition-all duration-150 ease-premium motion-press"
            title="Voir mon panier"
          >
            <ShoppingBag className="w-5 h-5 text-gold-400" />
            {totalCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-gold-500 text-dark-950 text-[11px] font-black w-5 h-5 rounded-full flex items-center justify-center shadow-md animate-scale-in">
                {totalCount}
              </span>
            )}
          </button>

          {/* Mobile Menu Toggle */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 text-zinc-300 hover:text-white"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden bg-dark-900 border-b border-white/10 px-6 py-4 space-y-3">
          <Link
            href="/"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-zinc-200 font-medium py-1 hover:text-gold-400"
          >
            Accueil
          </Link>
          <Link
            href="/catalogue"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-zinc-200 font-medium py-1 hover:text-gold-400"
          >
            Catalogue Complet
          </Link>
          <Link
            href="/catalogue?genre=femme"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-zinc-200 font-medium py-1 hover:text-gold-400"
          >
            Collection Femme
          </Link>
          <Link
            href="/catalogue?genre=homme"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-zinc-200 font-medium py-1 hover:text-gold-400"
          >
            Collection Homme
          </Link>
          <Link
            href="/catalogue?promo=true"
            onClick={() => setMobileMenuOpen(false)}
            className="block text-amber-400 font-semibold py-1"
          >
            Promotions & Ventes Flash
          </Link>
        </div>
      )}
    </header>
  );
}
