'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, MessageCircle, ShoppingBag, ShieldCheck, Clock, Truck, Sparkles, Check } from 'lucide-react';
import Product3DViewer from '@/components/3d/Product3DViewer';
import { useStore } from '@/lib/store-context';

const WHATSAPP_PHONE = '2250574243752';

const COLOR_OPTIONS = [
  {
    key: 'Noir',
    label: 'Noir Ébène',
    colorHex: '#18181b',
    desc: 'Cuir grainé d’un noir profond et intemporel, magnifié par les finitions laiton doré.',
  },
  {
    key: 'Bordeaux',
    label: 'Bordeaux Royal',
    colorHex: '#581c24',
    desc: 'Teinte carmin envoûtante, riche en reflets chauds pour vos soirées élégantes.',
  },
  {
    key: 'Cognac',
    label: 'Cognac Cuir',
    colorHex: '#8b4513',
    desc: 'Cuir ambré aux accents naturels de maroquinerie sellier artisanale.',
  },
];

export default function Showroom3DClient() {
  const [selectedColor, setSelectedColor] = useState('Noir');
  const { add } = useStore();

  const activeColorInfo =
    COLOR_OPTIONS.find((c) => c.key === selectedColor) || COLOR_OPTIONS[0];

  const whatsappMessage = encodeURIComponent(
    `Bonjour Sophia, je viens d'explorer le Sac Signature en vue 3D sur le site. Je souhaite le commander en teinte ${activeColorInfo.label} (32 000 FCFA). Est-il disponible pour une livraison à domicile ?`
  );
  const whatsappUrl = `https://wa.me/${WHATSAPP_PHONE}?text=${whatsappMessage}`;

  return (
    <div className="min-h-screen bg-ink-950 text-linen-100 pb-24 pt-6">
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
        {/* Fil d'Ariane & Retour */}
        <nav className="mb-6 flex items-center justify-between gap-4 border-b border-white/10 pb-4 text-xs font-serif text-zinc-400">
          <Link
            href="/"
            className="group flex items-center gap-2 hover:text-brass-300 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 transition-transform group-hover:-translate-x-1" />
            <span>Retour à l'accueil</span>
          </Link>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="tracking-widest uppercase text-[10px] text-brass-300">
              Expérience 3D Interactive
            </span>
          </div>
        </nav>

        {/* Grille principale Showroom 3D */}
        <div className="grid gap-10 lg:grid-cols-12 lg:gap-14 items-start">
          {/* Colonne gauche : Visualiseur 3D interactif (7 colonnes) */}
          <div className="lg:col-span-7 space-y-4">
            <div className="relative">
              <Product3DViewer
                modelSrc="/models/sac-elsi.glb"
                posterSrc="/models/sac-elsi-poster.png"
                alt="Sac à Main Cuir Grainé ELSI en 3D 360°"
                cameraOrbit="0deg 75deg 105%"
                selectedColor={selectedColor}
                onColorChange={(c) => setSelectedColor(c)}
                showColorPicker={true}
                className="w-full aspect-[4/4] sm:aspect-[4/4.2] rounded-3xl"
              />
            </div>

            {/* Conseils d'interaction */}
            <div className="grid grid-cols-3 gap-3 text-center text-xs text-zinc-400 border border-white/5 rounded-2xl p-3 bg-ink-900/40">
              <div>
                <span className="block text-brass-300 font-medium font-serif">Pivoter</span>
                <span>Glissez le doigt ou la souris</span>
              </div>
              <div className="border-x border-white/10 px-2">
                <span className="block text-brass-300 font-medium font-serif">Zoomer</span>
                <span>Pincez ou molette</span>
              </div>
              <div>
                <span className="block text-brass-300 font-medium font-serif">Couleurs</span>
                <span>Pastilles en direct</span>
              </div>
            </div>
          </div>

          {/* Colonne droite : Fiche d'exception & Commandes directes (5 colonnes) */}
          <div className="lg:col-span-5 space-y-7 lg:sticky lg:top-24">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full bg-brass-400/10 border border-brass-400/30 px-3 py-1 text-xs text-brass-300 mb-3">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Pièce Phare · Maroquinerie d'Exception</span>
              </div>
              <h1 className="text-display text-3xl sm:text-4xl text-linen-100 tracking-tight leading-tight">
                Sac à Main Signature Cuir Grainé
              </h1>
              <p className="mt-3 text-2xl font-serif text-brass-400">
                32 000 FCFA
              </p>
              <p className="mt-2 text-xs text-zinc-400">
                TVA comprise · Livraison 24h & Essayage offert à domicile
              </p>
            </div>

            {/* Sélecteur de Couleurs avec descriptif */}
            <div className="space-y-3 rounded-2xl bg-ink-900/60 p-5 border border-white/10">
              <span className="block text-xs font-serif tracking-widest uppercase text-brass-300">
                Teinte de cuir sélectionnée : <strong className="text-linen-100">{activeColorInfo.label}</strong>
              </span>

              <div className="flex items-center gap-3 pt-1">
                {COLOR_OPTIONS.map((c) => {
                  const isSelected = selectedColor === c.key;
                  return (
                    <button
                      key={c.key}
                      type="button"
                      onClick={() => setSelectedColor(c.key)}
                      className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all ${
                        isSelected
                          ? 'bg-brass-400 text-ink-950 shadow-lg scale-105 font-semibold'
                          : 'bg-ink-950 text-zinc-300 border border-white/10 hover:border-brass-400/50'
                      }`}
                    >
                      <span
                        className="w-3.5 h-3.5 rounded-full border border-white/20"
                        style={{ backgroundColor: c.colorHex }}
                      />
                      <span>{c.label}</span>
                      {isSelected && <Check className="w-3.5 h-3.5" />}
                    </button>
                  );
                })}
              </div>

              <p className="text-xs text-zinc-400 pt-1 leading-relaxed italic">
                "{activeColorInfo.desc}"
              </p>
            </div>

            {/* Boutons d'Action Clés */}
            <div className="space-y-3">
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full flex items-center justify-center gap-3 rounded-full bg-[#25D366] px-6 py-4 text-sm font-semibold text-white shadow-xl hover:bg-[#20ba59] transition-all hover:scale-[1.02] active:scale-95"
              >
                <MessageCircle className="w-5 h-5 fill-current" />
                <span>Commander sur WhatsApp avec Sophia</span>
              </a>

              <Link
                href="/article/art-101"
                className="w-full flex items-center justify-center gap-2 rounded-full border border-brass-400/40 bg-ink-900 px-6 py-3.5 text-sm font-serif text-brass-300 hover:bg-brass-400 hover:text-ink-950 transition-all text-center"
              >
                <span>Voir la fiche catalogue complète</span>
              </Link>
            </div>

            {/* Fiche Technique & Savoir-Faire */}
            <div className="border-t border-white/10 pt-5 space-y-3">
              <h3 className="text-xs font-serif uppercase tracking-widest text-brass-300">
                Spécifications Artisanales
              </h3>
              <ul className="text-xs text-zinc-300 space-y-2 leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-brass-400 font-bold">•</span>
                  <span><strong>Cuir :</strong> Cuir de vachette pleine fleur grainé, tannage végétal de prestige.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-brass-400 font-bold">•</span>
                  <span><strong>Finitions :</strong> Fermoir quart-de-tour en laiton massif brossé or mat.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-brass-400 font-bold">•</span>
                  <span><strong>Porté :</strong> Poignée haute rigide + bandoulière réglable et amovible.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-brass-400 font-bold">•</span>
                  <span><strong>Confection :</strong> Atelier ELSI Abidjan — coutures sellier renforcées.</span>
                </li>
              </ul>
            </div>

            {/* Engagements ELSI */}
            <div className="grid grid-cols-3 gap-3 border-t border-white/10 pt-5 text-center text-zinc-400">
              <div className="space-y-1">
                <Clock className="w-4 h-4 mx-auto text-brass-400" />
                <p className="text-[11px] font-medium text-linen-100">24 h à Abidjan</p>
                <p className="text-[10px]">Livraison express</p>
              </div>
              <div className="space-y-1">
                <Truck className="w-4 h-4 mx-auto text-brass-400" />
                <p className="text-[11px] font-medium text-linen-100">Sous housse zippée</p>
                <p className="text-[10px]">Repassée vapeur</p>
              </div>
              <div className="space-y-1">
                <ShieldCheck className="w-4 h-4 mx-auto text-brass-400" />
                <p className="text-[11px] font-medium text-linen-100">Garantie 48 h</p>
                <p className="text-[10px]">Échange sans frais</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
