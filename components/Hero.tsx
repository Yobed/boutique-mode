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
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-gold-500/10 border border-gold-500/30 text-gold-400 text-xs font-semibold uppercase tracking-widest backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-gold-400 animate-ping" />
            Nouvelle Collection 2026
          </div>

          {/* Heading */}
          <h1 className="font-serif text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight leading-[1.1] text-white">
            L'Élégance Pure, <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-gold-400 via-brand-300 to-amber-200">
              Faite Pour Vous.
            </span>
          </h1>

          {/* Description */}
          <p className="text-zinc-300 text-base sm:text-lg leading-relaxed font-normal">
            Découvrez notre sélection exclusive de prêt-à-porter chic : robes de soirée somptueuses, costumes tailleur raffinés, tenues d'affaires et créations contemporaines.
          </p>

          {/* CTAs */}
          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              href="/catalogue"
              className="inline-flex items-center gap-2 px-7 py-3.5 rounded-full bg-gradient-to-r from-gold-500 to-gold-400 hover:from-gold-400 hover:to-gold-300 text-dark-950 font-bold text-sm tracking-wide shadow-xl shadow-gold-500/20 transition-all hover:scale-105"
            >
              <span>Découvrir les Vêtements</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <button
              onClick={onOpenStylist}
              className="inline-flex items-center gap-2 px-6 py-3.5 rounded-full bg-white/10 hover:bg-white/15 border border-white/20 text-white font-semibold text-sm backdrop-blur-md transition-all hover:border-gold-500/50"
            >
              <Sparkles className="w-4 h-4 text-purple-400" />
              <span>Conseillère IA Vendeuse</span>
            </button>
          </div>

          {/* Guarantees Badges */}
          <div className="pt-8 grid grid-cols-3 gap-4 border-t border-white/10 text-xs text-zinc-400">
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
