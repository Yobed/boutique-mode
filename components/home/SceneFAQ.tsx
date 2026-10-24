'use client';

import { useState } from 'react';
import { ChevronDown, HelpCircle, MessageCircle } from 'lucide-react';
import { waLink, WHATSAPP_DISPLAY } from '@/lib/config';

interface FAQItem {
  q: string;
  a: string;
}

const FAQS: FAQItem[] = [
  {
    q: 'Comment se déroule la livraison à Abidjan et à l’intérieur ?',
    a: 'À Abidjan, nous livrons sous 24 h directement à votre porte (Cocody, Plateau, Marcory, Riviera, Yopougon, Zone 4...). Chaque tenue arrive repassée à la vapeur, sur cintre et protégée sous une housse zippée. Pour l’intérieur du pays, l’expédition sécurisée prend 48 à 72 h.',
  },
  {
    q: 'Quand et comment s’effectue le règlement ?',
    a: 'Vous ne payez rien à l’avance en ligne. Le règlement se fait à la réception lors de la remise en main propre de votre colis par le coursier. Vous pouvez payer en espèces ou par transfert direct Wave, Orange Money ou MTN MoMo en toute sécurité.',
  },
  {
    q: 'Comment fonctionne l’échange de taille sous 48 h ?',
    a: 'Vous essayez votre pièce tranquillement chez vous, dans votre intimité. Si la taille ou la coupe doit être ajustée, écrivez-nous simplement sur WhatsApp : notre coursier passe faire l’échange directement à votre porte sous 48 h, sans aucuns frais d’échange.',
  },
  {
    q: 'Comment être sûr·e de choisir la bonne taille avant d’acheter ?',
    a: 'Sophia, notre première d’atelier, est disponible tous les jours de 8 h à 21 h sur WhatsApp. Vous pouvez lui transmettre vos mensurations ou votre taille habituelle : elle vous confirme la coupe parfaite avant même le départ du colis.',
  },
  {
    q: 'Puis-je venir essayer directement à votre atelier ?',
    a: 'Oui. Notre atelier et salon privé est situé à Cocody Danga, Abidjan. Nous y accueillons nos clientes et clients sur rendez-vous pour des séances d’essayage privé, des ajustements de demi-mesure et la découverte de nos collections capsules.',
  },
  {
    q: 'Quelle est la garantie sur les matières et les finitions ?',
    a: 'Chaque création est confectionnée dans des matières nobles (cuir pleine fleur, lin pur lourd, wax certifié grand teint) et contrôlée à la main. Nous appliquons une garantie atelier de 30 jours couvrant coutures, boutons et finitions avec réparation prise en charge.',
  },
];

export default function SceneFAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(0);

  const toggle = (idx: number) => {
    setOpenIndex(openIndex === idx ? null : idx);
  };

  return (
    <section aria-labelledby="faq-titre" className="relative bg-ink-900 py-[var(--section)] text-ivory">
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
        <div className="grid gap-12 lg:grid-cols-12 lg:gap-16">
          {/* Column left: Title & Reassurance */}
          <div className="lg:col-span-5 lg:sticky lg:top-[calc(var(--header-h)+6vh)] lg:self-start">
            <div className="inline-flex items-center gap-2 text-[11px] uppercase tracking-label text-brass-400">
              <HelpCircle className="h-3.5 w-3.5 text-brass-400" />
              <span>Questions fréquentes</span>
            </div>
            <h2 id="faq-titre" className="text-display mt-4 text-[clamp(2.4rem,1.5rem+3vw,4.8rem)] leading-[0.98]">
              Tout savoir <em className="text-brass-300">avant de commander.</em>
            </h2>
            <p className="mt-6 text-[16px] leading-relaxed text-zinc-300">
              Des règles commerciales limpides, zéro zone d'ombre. Nous répondons à toutes vos questions en toute transparence.
            </p>

            <div className="mt-8 rounded border border-brass-400/20 bg-ink-950/70 p-6">
              <h3 className="font-serif text-lg text-brass-200">Une hésitation particulière ?</h3>
              <p className="mt-2 text-sm text-zinc-400">
                Sophia vous répond en direct pour valider une coupe ou préparer une tenue pour un événement précis.
              </p>
              <a
                href={waLink('Bonjour Sophia, j’ai une question avant de passer commande.')}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-5 inline-flex items-center gap-2.5 rounded border border-emerald-500/40 bg-emerald-950/40 px-5 py-3 text-xs uppercase tracking-wider text-emerald-200 transition-colors hover:border-emerald-300 hover:bg-emerald-900/60"
              >
                <MessageCircle className="h-4 w-4" />
                <span>Poser ma question à Sophia ({WHATSAPP_DISPLAY})</span>
              </a>
            </div>
          </div>

          {/* Column right: Accordion items */}
          <div className="divide-y divide-ivory/[0.08] border-y border-ivory/[0.08] lg:col-span-7">
            {FAQS.map((item, idx) => {
              const isOpen = openIndex === idx;
              return (
                <div key={item.q} className="py-6 transition-colors">
                  <button
                    type="button"
                    onClick={() => toggle(idx)}
                    aria-expanded={isOpen}
                    className="flex w-full items-start justify-between gap-6 text-left"
                  >
                    <span className="text-display text-[clamp(1.15rem,0.95rem+0.5vw,1.4rem)] leading-snug text-ivory">
                      {item.q}
                    </span>
                    <span
                      className={`grid h-8 w-8 shrink-0 place-items-center rounded-full border border-ivory/10 transition-transform duration-300 ${
                        isOpen ? 'rotate-180 border-brass-400 text-brass-300' : 'text-zinc-400'
                      }`}
                    >
                      <ChevronDown className="h-4 w-4" />
                    </span>
                  </button>
                  {isOpen && (
                    <div className="mt-4 pr-12 text-sm leading-relaxed text-zinc-300 transition-all">
                      {item.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
