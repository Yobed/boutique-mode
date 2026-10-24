'use client';

import React, { useEffect, useRef, useState } from 'react';
import { X, Ruler, Sparkles, Check } from 'lucide-react';

interface SizeGuideModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenStylist?: () => void;
}

export default function SizeGuideModal({ isOpen, onClose, onOpenStylist }: SizeGuideModalProps) {
  const [tab, setTab] = useState<'femme' | 'homme' | 'chaussures'>('femme');
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!isOpen) return;
    const previous = document.activeElement as HTMLElement | null;
    closeRef.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => {
      window.removeEventListener('keydown', onKey);
      previous?.focus();
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[75] overflow-y-auto flex items-center justify-center p-4" role="dialog" aria-modal="true" aria-labelledby="guide-titre">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-ink-950/85 animate-fade-in" onClick={onClose} aria-hidden />

      {/* Modal Container */}
      <div className="relative w-full max-w-2xl bg-dark-900 border border-ivory/10 p-6 sm:p-8 text-ivory shadow-lift animate-scale-in z-10">
        {/* Header */}
        <div className="flex items-center justify-between pb-5 border-b border-ivory/10">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-gold-500/10 border border-gold-500/20 text-gold-400">
              <Ruler className="w-5 h-5" />
            </div>
            <div>
              <h2 id="guide-titre" className="font-serif text-xl sm:text-2xl font-normal text-ivory">
                Guide des tailles & mensurations
              </h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                Barème officiel des confections ELSI
              </p>
            </div>
          </div>
          <button
            ref={closeRef}
            type="button"
            onClick={onClose}
            aria-label="Fermer le guide des tailles"
            className="p-2.5 text-zinc-400 hover:text-ivory hover:bg-ivory/10 transition-colors duration-150 ease-premium motion-press"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 my-5 p-1.5 rounded-2xl bg-dark-950 border border-ivory/5">
          <button
            type="button"
            onClick={() => setTab('femme')}
            className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all duration-150 ease-premium motion-press ${
              tab === 'femme'
                ? 'bg-gold-500 text-dark-950 shadow-md font-bold'
                : 'text-zinc-400 hover:text-ivory'
            }`}
          >
            Femme (Robes, Ensembles)
          </button>
          <button
            type="button"
            onClick={() => setTab('homme')}
            className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all duration-150 ease-premium motion-press ${
              tab === 'homme'
                ? 'bg-gold-500 text-dark-950 shadow-md font-bold'
                : 'text-zinc-400 hover:text-ivory'
            }`}
          >
            Homme (Costumes, Lin)
          </button>
          <button
            type="button"
            onClick={() => setTab('chaussures')}
            className={`flex-1 py-2 text-xs font-semibold rounded-xl transition-all duration-150 ease-premium motion-press ${
              tab === 'chaussures'
                ? 'bg-gold-500 text-dark-950 shadow-md font-bold'
                : 'text-zinc-400 hover:text-ivory'
            }`}
          >
            Chaussures & Escarpins
          </button>
        </div>

        {/* Table Content */}
        <div className="overflow-x-auto">
          {tab === 'femme' && (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-ivory/10 text-gold-400 font-serif">
                  <th className="py-2.5 px-3">Taille</th>
                  <th className="py-2.5 px-3">FR / EUR</th>
                  <th className="py-2.5 px-3">Tour Poitrine</th>
                  <th className="py-2.5 px-3">Tour Taille</th>
                  <th className="py-2.5 px-3">Tour Hanches</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ivory/5 text-zinc-300">
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">XS</td>
                  <td className="py-2.5 px-3 text-zinc-400">34</td>
                  <td className="py-2.5 px-3">78 - 82 cm</td>
                  <td className="py-2.5 px-3">60 - 64 cm</td>
                  <td className="py-2.5 px-3">86 - 90 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">S</td>
                  <td className="py-2.5 px-3 text-zinc-400">36 - 38</td>
                  <td className="py-2.5 px-3">83 - 88 cm</td>
                  <td className="py-2.5 px-3">65 - 70 cm</td>
                  <td className="py-2.5 px-3">91 - 96 cm</td>
                </tr>
                <tr className="bg-ivory/5">
                  <td className="py-2.5 px-3 font-bold text-gold-300">M</td>
                  <td className="py-2.5 px-3 text-zinc-400">38 - 40</td>
                  <td className="py-2.5 px-3">89 - 94 cm</td>
                  <td className="py-2.5 px-3">71 - 76 cm</td>
                  <td className="py-2.5 px-3">97 - 102 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">L</td>
                  <td className="py-2.5 px-3 text-zinc-400">42 - 44</td>
                  <td className="py-2.5 px-3">95 - 102 cm</td>
                  <td className="py-2.5 px-3">77 - 84 cm</td>
                  <td className="py-2.5 px-3">103 - 110 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">XL</td>
                  <td className="py-2.5 px-3 text-zinc-400">46 - 48</td>
                  <td className="py-2.5 px-3">103 - 110 cm</td>
                  <td className="py-2.5 px-3">85 - 92 cm</td>
                  <td className="py-2.5 px-3">111 - 118 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">XXL</td>
                  <td className="py-2.5 px-3 text-zinc-400">50 - 52</td>
                  <td className="py-2.5 px-3">111 - 120 cm</td>
                  <td className="py-2.5 px-3">93 - 102 cm</td>
                  <td className="py-2.5 px-3">119 - 128 cm</td>
                </tr>
              </tbody>
            </table>
          )}

          {tab === 'homme' && (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-ivory/10 text-gold-400 font-serif">
                  <th className="py-2.5 px-3">Taille</th>
                  <th className="py-2.5 px-3">Veste / Costume</th>
                  <th className="py-2.5 px-3">Tour Poitrine</th>
                  <th className="py-2.5 px-3">Tour Ceinture</th>
                  <th className="py-2.5 px-3">Col Chemise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ivory/5 text-zinc-300">
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">S</td>
                  <td className="py-2.5 px-3 text-zinc-400">46 - 48</td>
                  <td className="py-2.5 px-3">92 - 96 cm</td>
                  <td className="py-2.5 px-3">78 - 82 cm</td>
                  <td className="py-2.5 px-3">37 - 38 cm</td>
                </tr>
                <tr className="bg-ivory/5">
                  <td className="py-2.5 px-3 font-bold text-gold-300">M</td>
                  <td className="py-2.5 px-3 text-zinc-400">50 - 52</td>
                  <td className="py-2.5 px-3">97 - 102 cm</td>
                  <td className="py-2.5 px-3">83 - 88 cm</td>
                  <td className="py-2.5 px-3">39 - 40 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">L</td>
                  <td className="py-2.5 px-3 text-zinc-400">54</td>
                  <td className="py-2.5 px-3">103 - 108 cm</td>
                  <td className="py-2.5 px-3">89 - 94 cm</td>
                  <td className="py-2.5 px-3">41 - 42 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">XL</td>
                  <td className="py-2.5 px-3 text-zinc-400">56 - 58</td>
                  <td className="py-2.5 px-3">109 - 116 cm</td>
                  <td className="py-2.5 px-3">95 - 102 cm</td>
                  <td className="py-2.5 px-3">43 - 44 cm</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">XXL</td>
                  <td className="py-2.5 px-3 text-zinc-400">60</td>
                  <td className="py-2.5 px-3">117 - 124 cm</td>
                  <td className="py-2.5 px-3">103 - 110 cm</td>
                  <td className="py-2.5 px-3">45 - 46 cm</td>
                </tr>
              </tbody>
            </table>
          )}

          {tab === 'chaussures' && (
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-ivory/10 text-gold-400 font-serif">
                  <th className="py-2.5 px-3">Pointure FR / EUR</th>
                  <th className="py-2.5 px-3">Longueur Pied (cm)</th>
                  <th className="py-2.5 px-3">Taille UK</th>
                  <th className="py-2.5 px-3">Taille US</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ivory/5 text-zinc-300">
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">37</td>
                  <td className="py-2.5 px-3">23.5 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">4</td>
                  <td className="py-2.5 px-3 text-zinc-400">6</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">38</td>
                  <td className="py-2.5 px-3">24.2 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">5</td>
                  <td className="py-2.5 px-3 text-zinc-400">7</td>
                </tr>
                <tr className="bg-ivory/5">
                  <td className="py-2.5 px-3 font-bold text-gold-300">39</td>
                  <td className="py-2.5 px-3">24.8 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">5.5</td>
                  <td className="py-2.5 px-3 text-zinc-400">7.5</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">40</td>
                  <td className="py-2.5 px-3">25.5 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">6.5</td>
                  <td className="py-2.5 px-3 text-zinc-400">8.5</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">41</td>
                  <td className="py-2.5 px-3">26.2 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">7.5</td>
                  <td className="py-2.5 px-3 text-zinc-400">9</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">42</td>
                  <td className="py-2.5 px-3">27.0 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">8</td>
                  <td className="py-2.5 px-3 text-zinc-400">9.5</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">43</td>
                  <td className="py-2.5 px-3">27.8 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">9</td>
                  <td className="py-2.5 px-3 text-zinc-400">10.5</td>
                </tr>
                <tr>
                  <td className="py-2.5 px-3 font-bold text-ivory">44</td>
                  <td className="py-2.5 px-3">28.5 cm</td>
                  <td className="py-2.5 px-3 text-zinc-400">10</td>
                  <td className="py-2.5 px-3 text-zinc-400">11.5</td>
                </tr>
              </tbody>
            </table>
          )}
        </div>

        {/* Reassurance Guarantee Footer */}
        <div className="mt-6 pt-4 border-t border-ivory/10 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2 text-xs text-zinc-400">
            <Check className="w-4 h-4 text-emerald-400 flex-shrink-0" />
            <span>Essayage à la livraison & échange de taille gratuit sous 48h à Abidjan.</span>
          </div>

          {onOpenStylist && (
            <button
              onClick={() => {
                onClose();
                onOpenStylist();
              }}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gold-500/10 border border-gold-500/30 text-gold-300 hover:bg-gold-500/20 text-xs font-semibold transition-all duration-150 ease-premium motion-press whitespace-nowrap"
            >
              <Sparkles className="w-3.5 h-3.5 text-gold-400" />
              <span>Doute ? Demander à Sophia</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
