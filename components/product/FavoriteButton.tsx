'use client';

import { Heart } from 'lucide-react';
import { useStore } from '@/lib/store-context';

export default function FavoriteButton({ id, nom, className = '' }: { id: string; nom: string; className?: string }) {
  const { favorites, toggleFavorite } = useStore();
  const active = favorites.includes(id);
  return (
    <button
      type="button"
      onClick={() => toggleFavorite(id)}
      aria-pressed={active}
      aria-label={active ? `Retirer ${nom} des favoris` : `Ajouter ${nom} aux favoris`}
      data-active={active}
      className={`icon-heart grid h-11 w-11 place-items-center ${active ? 'text-brass-300' : 'text-ivory/80 hover:text-ivory'} ${className}`}
    >
      <Heart className="h-[18px] w-[18px]" strokeWidth={1.6} />
    </button>
  );
}
