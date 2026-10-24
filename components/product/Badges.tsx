import { Truck } from 'lucide-react';
import type { Article } from '@/lib/types';
import { FREE_DELIVERY_THRESHOLD } from '@/lib/config';
import { unitPrice } from '@/lib/cart.ts';

type Badge = { key: string; className: string; label: string; icon?: boolean };

/** Derived only from real data: stock, flags, price. At most two, in priority order. */
export function badgesFor(article: Article): Badge[] {
  if (!article.en_stock || article.quantite_stock <= 0) return [{ key: 'out', className: 'badge-out', label: 'Épuisé' }];
  const list: Badge[] = [];
  if (article.modele_3d) list.push({ key: '3d', className: 'badge-new !bg-brass-400/20 !text-brass-300 !border-brass-400/30', label: '✦ Vue 3D' });
  if (article.nouveaute) list.push({ key: 'new', className: 'badge-new', label: 'Nouveau' });
  if (article.prix_promo)
    list.push({ key: 'sale', className: 'badge-sale', label: `−${Math.round((1 - article.prix_promo / article.prix) * 100)} %` });
  if (unitPrice(article) >= FREE_DELIVERY_THRESHOLD)
    list.push({ key: 'ship', className: 'badge-ship', label: 'Livraison offerte', icon: true });
  return list.slice(0, 2);
}

export default function Badges({ article, className = '' }: { article: Article; className?: string }) {
  const list = badgesFor(article);
  if (list.length === 0) return null;
  return (
    <ul className={`flex flex-col items-start gap-1.5 ${className}`} aria-label="Informations">
      {list.map((b) => (
        <li key={b.key} className={`badge ${b.className}`}>
          {b.icon && <Truck className="h-3 w-3" aria-hidden />}
          {b.label}
        </li>
      ))}
    </ul>
  );
}
