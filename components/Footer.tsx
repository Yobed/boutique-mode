import Link from 'next/link';
import { BRAND, WHATSAPP_DISPLAY, waLink } from '@/lib/config';

const COLUMNS = [
  {
    title: 'Collection',
    links: [
      { href: '/catalogue?genre=femme', label: 'Femme' },
      { href: '/catalogue?genre=homme', label: 'Homme' },
      { href: '/catalogue?categorie=accessoires', label: 'Accessoires' },
      { href: '/catalogue?promo=true', label: 'Prix doux' },
    ],
  },
  {
    title: 'Service',
    links: [
      { href: '/suivi', label: 'Suivre ma commande' },
      { href: '/catalogue?favoris=1', label: 'Mes favoris' },
      { href: '/commande', label: 'Finaliser ma commande' },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="border-t border-ivory/[0.07] bg-ink-950 text-zinc-400">
      <div className="mx-auto grid max-w-[1440px] gap-12 px-[var(--gutter)] py-16 md:grid-cols-[1.4fr_1fr_1fr_1.2fr] md:py-20">
        <div className="space-y-5">
          <p className="text-display text-5xl tracking-[0.3em] text-ivory">{BRAND.name}</p>
          <p className="max-w-xs text-sm leading-relaxed">
            Vêtements et accessoires choisis, ajustés et repassés dans notre atelier d’Abidjan, livrés sous housse jusqu’à votre porte.
          </p>
        </div>

        {COLUMNS.map((col) => (
          <nav key={col.title} aria-label={col.title}>
            <h2 className="mb-4 text-[11px] uppercase tracking-label text-zinc-500">{col.title}</h2>
            <ul className="space-y-2.5 text-sm">
              {col.links.map((l) => (
                <li key={l.href}>
                  <Link href={l.href} className="link-draw text-zinc-300 hover:text-ivory">
                    {l.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        ))}

        <div className="space-y-3 text-sm">
          <h2 className="mb-4 text-[11px] uppercase tracking-label text-zinc-500">Atelier & Conciergerie</h2>
          <p className="text-zinc-300">Atelier & Salon Privé : Cocody Danga, Abidjan</p>
          <a href={waLink()} target="_blank" rel="noopener noreferrer" className="link-draw tabular block text-emerald-300 hover:text-emerald-200">
            WhatsApp {WHATSAPP_DISPLAY}
          </a>
          <p>Tous les jours, 8 h – 21 h</p>
          <p>Livraison Abidjan 24 h · Échange garanti 48 h</p>
        </div>
      </div>
      <div className="mx-auto flex max-w-[1440px] flex-col justify-between gap-2 border-t border-ivory/[0.06] px-[var(--gutter)] py-6 text-xs text-zinc-500 sm:flex-row">
        <p>© {new Date().getFullYear()} {BRAND.name} · Cocody Danga, Abidjan · RCCM CI-ABJ-2024-B-14892</p>
        <p>Paiement sécurisé à la réception · Échange 48 h · Wave · Orange Money · MTN MoMo</p>
      </div>
    </footer>
  );
}
