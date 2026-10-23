'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowRight, Sparkles, ShieldCheck, Truck, RefreshCw } from 'lucide-react';

interface HeroProps {
  onOpenStylist: () => void;
}

export default function Hero({ onOpenStylist }: HeroProps) {
  return (
    <div className="relative overflow-hidden bg-dark-950 text-white min-h-[580px] flex items-center">
      {/* Background with Ambient Glow */}
      <div className="absolute inset-0 z-0">
        <img
          src="https://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=1600&auto=format&fit=crop&q=80"
          alt="Mode & Prêt-à-porter de luxe"
          className="w-full h-full object-cover object-center opacity-30 mix-blend-luminosity scale-105"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-dark-950 via-dark-950/80 to-transparent" />
        <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent" />
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="max-w-2xl space-y-6">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-xs font-semibold uppercase tracking-widest backdrop-blur-sm animate-fade-up">
            <span className="w-2 h-2 rounded-full bg-gold-400 animate-ping" />
            Nouvelle Collection 2026
          </div>

          {/* Heading */}
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-normal tracking-tight leading-[1.1] text-white animate-fade-up stagger-1">
            L'Élégance Pure, <br />
            <span className="text-gold-400 italic">
              Faite Pour Vous.
            </span>
          </h1>

          {/* Description */}
          <p className="text-zinc-300 text-base sm:text-lg leading-relaxed font-normal animate-fade-up stagger-2 max-w-xl">
            Atelier de prêt-à-porter d'exception à Abidjan. Robes de gala sculpturales, costumes sur mesure, lin italien et créations wax contemporaines.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-2 animate-fade-up stagger-3">
            <Link
              href="/catalogue"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-gold-500 hover:bg-gold-400 text-dark-950 font-bold text-sm tracking-wide shadow-xl shadow-gold-500/20 transition-all duration-200 ease-premium motion-press hover:scale-105"
            >
              <span>Découvrir la Collection</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <button
              onClick={onOpenStylist}
              className="inline-flex items-center gap-2.5 px-7 py-4 rounded-full bg-dark-900/80 hover:bg-dark-800 border border-gold-500/30 hover:border-gold-500/60 text-white font-semibold text-sm backdrop-blur-md transition-all duration-200 ease-premium motion-press"
            >
              <Sparkles className="w-4 h-4 text-gold-400" />
              <span>Styliste Privée Atelier</span>
            </button>
          </div>

          {/* Guarantees Badges */}
          <div className="pt-8 grid grid-cols-3 gap-4 border-t border-white/10 text-xs text-zinc-400 animate-fade-up stagger-4">
            <div className="flex items-center gap-2">
              <Truck className="w-5 h-5 text-gold-400 flex-shrink-0" />
              <span>Livraison 24h à Abidjan</span>
            </div>
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-5 h-5 text-gold-400 flex-shrink-0" />
              <span>Paiement à la réception</span>
            </div>
            <div className="flex items-center gap-2">
              <RefreshCw className="w-5 h-5 text-gold-400 flex-shrink-0" />
              <span>Échange taille facile</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
