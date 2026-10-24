import Image from 'next/image';
import type { CartItem } from '@/lib/types';
import { formatFCFA } from '@/lib/config';
import { unitPrice } from '@/lib/cart.ts';

interface Props {
  items: CartItem[];
  sousTotal: number;
  livraison: number;
}

export default function OrderSummary({ items, sousTotal, livraison }: Props) {
  return (
    <div>
      <ul className="divide-y divide-ivory/[0.06]">
        {items.map((item) => (
          <li key={`${item.article.id}-${item.taille}-${item.couleur}`} className="flex gap-4 py-4">
            <div className="relative h-20 w-[60px] shrink-0 overflow-hidden bg-ink-800">
              {item.article.photos[0] && <Image src={item.article.photos[0]} alt="" fill sizes="60px" className="object-contain p-1 mix-blend-multiply" />}
              <span className="tabular absolute right-0 top-0 grid h-5 min-w-5 place-items-center bg-ivory px-1 text-[10px] text-ink-950">{item.quantite}</span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-display text-[15px] leading-snug">{item.article.nom}</p>
              <p className="mt-0.5 text-xs text-zinc-500">
                {item.taille} · {item.couleur}
              </p>
            </div>
            <p className="tabular text-sm">{formatFCFA(unitPrice(item.article) * item.quantite)}</p>
          </li>
        ))}
      </ul>
      <dl className="tabular space-y-2 border-t border-ivory/[0.08] pt-4 text-sm">
        <div className="flex justify-between text-zinc-300">
          <dt>Sous-total</dt>
          <dd>{formatFCFA(sousTotal)}</dd>
        </div>
        <div className="flex justify-between text-zinc-300">
          <dt>Livraison</dt>
          <dd>{livraison === 0 ? <span className="text-emerald-300">Offerte</span> : formatFCFA(livraison)}</dd>
        </div>
        <div className="flex items-baseline justify-between border-t border-ivory/[0.08] pt-3">
          <dt className="text-ivory">Total</dt>
          <dd className="text-display text-2xl">{formatFCFA(sousTotal + livraison)}</dd>
        </div>
      </dl>
    </div>
  );
}
