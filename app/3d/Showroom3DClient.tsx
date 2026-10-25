'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Check, MessageCircle, Sparkles } from 'lucide-react';
import Product3DViewer from '@/components/3d/Product3DViewer';

const WHATSAPP_PHONE = '2250574243752';
const COLOR_OPTIONS = [
  { key: 'noir', label: 'Noir', colorHex: '#171717' },
  { key: 'marron', label: 'Marron', colorHex: '#774126' },
  { key: 'bordeaux', label: 'Bordeaux', colorHex: '#642a31' },
  { key: 'bleu-marine', label: 'Bleu marine', colorHex: '#23364e' },
  { key: 'camel', label: 'Camel', colorHex: '#b87a43' },
  { key: 'gris', label: 'Gris', colorHex: '#77736d' },
];

export default function Showroom3DClient() {
  const [selectedColor, setSelectedColor] = useState('Marron');
  const activeColor = COLOR_OPTIONS.find((color) => color.label === selectedColor) ?? COLOR_OPTIONS[1];
  const whatsappMessage = encodeURIComponent(
    `Bonjour, j'ai vu la maquette 3D de la chaussure Derby homme. Pouvez-vous me confirmer le prix, les pointures et la disponibilité du coloris ${activeColor.label} ?`
  );
  const whatsappUrl = `https://wa.me/${WHATSAPP_PHONE}?text=${whatsappMessage}`;

  return (
    <main className="min-h-screen bg-ink-950 pb-20 pt-6 text-linen-100">
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
        <nav className="mb-7 flex items-center justify-between gap-4 border-b border-white/10 pb-4 text-xs text-zinc-400">
          <Link href="/" className="group flex items-center gap-2 transition-colors hover:text-brass-300">
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            <span>Retour à l’accueil</span>
          </Link>
          <span className="flex items-center gap-2 text-[10px] uppercase tracking-[0.18em] text-brass-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            Maquette 3D interactive
          </span>
        </nav>

        <div className="grid items-start gap-8 lg:grid-cols-12 lg:gap-12">
          <section className="space-y-4 lg:col-span-7" aria-label="Chaussure en vue 3D">
            <Product3DViewer
              modelSrc="/models/chaussure-homme-cognac.glb"
              posterSrc="/models/chaussure-homme-cognac-poster.png"
              alt="Maquette 3D d’une paire de chaussures Derby pour homme, coloris marron cognac"
              cameraOrbit="20deg 72deg 125%"
              selectedColor={selectedColor}
              onColorChange={setSelectedColor}
              colorOptions={COLOR_OPTIONS.map((color) => color.key)}
              showColorPicker={false}
              background="#d6d0c8"
              className="aspect-[4/3] w-full rounded-3xl border-white/10"
            />

            <div className="grid grid-cols-3 rounded-2xl border border-white/10 bg-ink-900/60 p-4 text-center text-xs text-zinc-400">
              <div>
                <span className="mb-1 block font-serif text-brass-300">Vue 360°</span>
                <span>Glisse pour pivoter</span>
              </div>
              <div className="border-x border-white/10 px-2">
                <span className="mb-1 block font-serif text-brass-300">Zoom</span>
                <span>Pince ou utilise la molette</span>
              </div>
              <div>
                <span className="mb-1 block font-serif text-brass-300">Coloris</span>
                <span>Aperçu simulé</span>
              </div>
            </div>
          </section>

          <section className="space-y-7 lg:col-span-5 lg:sticky lg:top-24">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-brass-400/30 bg-brass-400/10 px-3 py-1 text-xs text-brass-300">
                <Sparkles className="h-3.5 w-3.5" />
                Chaussures homme
              </div>
              <h1 className="text-display text-4xl leading-tight tracking-tight sm:text-5xl">
                Derby <span className="text-brass-300">Homme</span>
              </h1>
              <p className="mt-3 text-lg text-zinc-300">Coloris de référence : marron cognac</p>
              <p className="mt-5 font-serif text-xl text-brass-300">Prix à confirmer</p>
              <p className="mt-2 text-sm text-zinc-400">Pointures, disponibilité et délai à confirmer auprès de la boutique.</p>
            </div>

            <div className="space-y-4 rounded-2xl border border-white/10 bg-ink-900/60 p-5">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-brass-300">Coloris de la planche</p>
                <p className="mt-1 text-sm text-linen-100">Sélection : {activeColor.label}</p>
              </div>
              <div className="flex flex-wrap gap-3" aria-label="Aperçu indicatif des coloris">
                {COLOR_OPTIONS.map((color) => {
                  const isSelected = selectedColor === color.label;
                  return (
                    <button
                      key={color.key}
                      type="button"
                      onClick={() => setSelectedColor(color.label)}
                      aria-label={`Afficher le coloris ${color.label}`}
                      aria-pressed={isSelected}
                      className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-xs transition-colors ${
                        isSelected
                          ? 'border-brass-300 bg-brass-400 text-ink-950'
                          : 'border-white/10 bg-ink-950 text-zinc-300 hover:border-brass-400/50'
                      }`}
                    >
                      <span className="h-3.5 w-3.5 rounded-full border border-white/25" style={{ backgroundColor: color.colorHex }} />
                      {color.label}
                      {isSelected && <Check className="h-3.5 w-3.5" />}
                    </button>
                  );
                })}
              </div>
              <p className="text-xs leading-relaxed text-zinc-400">
                Les changements de couleur sont une simulation visuelle basée sur la planche fournie ; ils ne confirment pas le stock de ces coloris.
              </p>
            </div>

            <a
              href={whatsappUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex w-full items-center justify-center gap-3 rounded-full bg-[#25D366] px-6 py-4 text-sm font-semibold text-white transition-colors hover:bg-[#20ba59]"
            >
              <MessageCircle className="h-5 w-5 fill-current" />
              Demander le prix et la disponibilité
            </a>

            <div className="space-y-3 border-t border-white/10 pt-5">
              <h2 className="text-xs uppercase tracking-[0.16em] text-brass-300">D’après la planche de référence</h2>
              <dl className="grid grid-cols-[auto_1fr] gap-x-5 gap-y-2 text-sm">
                <dt className="text-zinc-500">Type</dt><dd>Derby à lacets</dd>
                <dt className="text-zinc-500">Coloris montré</dt><dd>Marron cognac</dd>
                <dt className="text-zinc-500">Semelle visible</dt><dd>Noire, à relief</dd>
              </dl>
              <p className="text-xs leading-relaxed text-zinc-400">
                Cette maquette 3D est construite à partir de la planche illustrée. Les dimensions indiquées sur celle-ci sont données à titre d’exemple ; les détails et caractéristiques du produit réel restent à confirmer.
              </p>
            </div>

            <Link href="/catalogue" className="inline-flex text-sm text-brass-300 underline-offset-4 hover:underline">
              Parcourir le catalogue
            </Link>
          </section>
        </div>
      </div>
    </main>
  );
}
