'use client';

import React from 'react';
import { CategorieVêtement, GenreVêtement } from '@/lib/types';
import { Filter, RotateCcw } from 'lucide-react';

interface FilterSidebarProps {
  selectedCategorie: CategorieVêtement;
  onSelectCategorie: (cat: CategorieVêtement) => void;
  selectedGenre: GenreVêtement;
  onSelectGenre: (genre: GenreVêtement) => void;
  selectedTaille: string;
  onSelectTaille: (taille: string) => void;
  maxPrice: number;
  onMaxPriceChange: (p: number) => void;
  onlyPromo: boolean;
  onTogglePromo: (val: boolean) => void;
  onReset: () => void;
}

const CATEGORIES: { label: string; value: CategorieVêtement }[] = [
  { label: 'Tous les articles', value: 'tous' },
  { label: 'Robes & Ensembles', value: 'robes' },
  { label: 'Costumes & Vestons', value: 'costumes' },
  { label: 'Chemises & Lin/Wax', value: 'chemises' },
  { label: 'Pantalons & Jupes', value: 'pantalons' },
  { label: 'Chaussures & Escarpins', value: 'chaussures' },
  { label: 'Sacs', value: 'sacs' },
  { label: 'Bijoux & Accessoires', value: 'accessoires' },
  { label: 'Hauts & T-shirts', value: 't-shirts' },
];

const TAILLES = ['Toutes', 'XS', 'S', 'M', 'L', 'XL', 'XXL', '37', '38', '39', '40', '41', '42', '43', '44'];

export default function FilterSidebar({
  selectedCategorie,
  onSelectCategorie,
  selectedGenre,
  onSelectGenre,
  selectedTaille,
  onSelectTaille,
  maxPrice,
  onMaxPriceChange,
  onlyPromo,
  onTogglePromo,
  onReset,
}: FilterSidebarProps) {
  return (
    <div className="space-y-7 text-ivory">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-ivory/10">
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gold-400" />
          <h2 className="text-display text-xl text-ivory">Filtres</h2>
        </div>
        <button
          onClick={onReset}
          className="text-[11px] text-zinc-400 hover:text-gold-400 flex items-center gap-1 transition-colors"
        >
          <RotateCcw className="w-3 h-3" />
          <span>Réinitialiser</span>
        </button>
      </div>

      {/* Genre */}
      <div>
        <label className="text-zinc-400 block mb-3 uppercase tracking-label text-[11px]">
          Rayon
        </label>
        <div className="grid grid-cols-3 gap-1.5 bg-dark-950 p-1 border border-ivory/5">
          {(['tous', 'femme', 'homme'] as GenreVêtement[]).map((g) => (
            <button
              key={g}
              type="button"
              onClick={() => onSelectGenre(g)}
              className={`py-2 px-2 text-xs font-semibold capitalize transition-all duration-150 ease-premium motion-press ${
                selectedGenre === g
                  ? 'bg-gold-500 text-dark-950 shadow-sm'
                  : 'text-zinc-400 hover:text-ivory'
              }`}
            >
              {g}
            </button>
          ))}
        </div>
      </div>

      {/* Catégories */}
      <div>
        <label className="text-zinc-400 block mb-3 uppercase tracking-label text-[11px]">
          Catégorie
        </label>
        <div className="space-y-1">
          {CATEGORIES.map((c) => (
            <button
              key={c.value}
              type="button"
              onClick={() => onSelectCategorie(c.value)}
              className={`w-full text-left px-3 py-2 text-xs font-medium transition-all duration-150 ease-premium motion-press flex items-center justify-between ${
                selectedCategorie === c.value
                  ? 'bg-gold-500/15 text-gold-400 font-bold border border-gold-500/30'
                  : 'text-zinc-400 hover:text-ivory hover:bg-ivory/5'
              }`}
            >
              <span>{c.label}</span>
              {selectedCategorie === c.value && <span className="w-1.5 h-1.5 rounded-full bg-gold-400" />}
            </button>
          ))}
        </div>
      </div>

      {/* Tailles */}
      <div>
        <label className="text-zinc-400 block mb-3 uppercase tracking-label text-[11px]">
          Taille
        </label>
        <div className="flex flex-wrap gap-1.5">
          {TAILLES.map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => onSelectTaille(t === 'Toutes' ? '' : t)}
              className={`min-w-9 px-2.5 py-2 text-xs font-semibold border transition-all duration-150 ease-premium motion-press ${
                (t === 'Toutes' && !selectedTaille) || selectedTaille === t
                  ? 'border-gold-400 bg-gold-400/15 text-gold-300'
                  : 'border-ivory/10 bg-dark-950 text-zinc-400 hover:border-ivory/20'
              }`}
            >
              {t}
            </button>
          ))}
        </div>
      </div>

      {/* Prix Maximum */}
      <div>
        <div className="flex justify-between items-center mb-2">
          <label className="text-zinc-400 uppercase tracking-label text-[11px]">
            Budget Max
          </label>
          <span className="text-xs font-bold text-gold-400">
            {maxPrice >= 100000 ? 'Illimité' : `${maxPrice.toLocaleString('fr-FR')} FCFA`}
          </span>
        </div>
        <input
          type="range"
          min="15000"
          max="100000"
          step="5000"
          value={maxPrice}
          onChange={(e) => onMaxPriceChange(Number(e.target.value))}
          className="w-full accent-gold-500 cursor-pointer bg-dark-950"
        />
      </div>

      {/* Promotions Only */}
      <div className="pt-2 border-t border-ivory/10 flex items-center justify-between">
        <label htmlFor="promo-toggle" className="text-xs font-semibold text-zinc-300 cursor-pointer">
          Afficher uniquement les Promos
        </label>
        <input
          id="promo-toggle"
          type="checkbox"
          checked={onlyPromo}
          onChange={(e) => onTogglePromo(e.target.checked)}
          className="w-4 h-4 rounded accent-gold-500 cursor-pointer"
        />
      </div>
    </div>
  );
}
