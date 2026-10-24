'use client';

import { useState } from 'react';
import type { FormEvent } from 'react';
import { AnimatePresence, motion } from 'motion/react';
import { Check } from 'lucide-react';
import { getCommandeStatut } from '@/lib/supabase';
import type { StatutLookup } from '@/lib/supabase';
import type { StatutCommande } from '@/lib/types';
import { waLink } from '@/lib/config';

const STEPS: { key: StatutCommande; titre: string; detail: string }[] = [
  { key: 'en_attente', titre: 'Commande reçue', detail: 'L’atelier vérifie la disponibilité de votre taille.' },
  { key: 'confirmee', titre: 'Préparée en atelier', detail: 'Contrôle des coutures, repassage vapeur, mise sous housse.' },
  { key: 'en_livraison', titre: 'Chez le coursier', detail: 'Il vous appelle avant d’arriver.' },
  { key: 'livree', titre: 'Essayée et livrée', detail: 'Vous ne payez que ce que vous gardez.' },
];

export default function SuiviPage() {
  const [numero, setNumero] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<StatutLookup | null>(null);

  const search = async (e: FormEvent) => {
    e.preventDefault();
    if (!numero.trim()) return;
    setLoading(true);
    setResult(await getCommandeStatut(numero));
    setLoading(false);
  };

  const current = result?.kind === 'found' ? STEPS.findIndex((s) => s.key === result.statut) : -1;
  const cancelled = result?.kind === 'found' && result.statut === 'annulee';
  const askWhatsApp = waLink(`Bonjour ELSI, où en est ma commande ${numero.trim().toUpperCase()} ?`);

  return (
    <section className="mx-auto max-w-3xl px-[var(--gutter)] pb-28 pt-14 md:pt-20">
      <h1 className="text-display text-[clamp(2.6rem,1.6rem+3vw,4.6rem)] leading-none">Où en est ma commande ?</h1>
      <p className="mt-5 max-w-[48ch] text-zinc-300">Saisissez le numéro reçu à la confirmation, par exemple ELSI-K3F9Q2.</p>

      <form onSubmit={search} className="mt-10 flex flex-col gap-3 sm:flex-row" role="search">
        <label htmlFor="numero" className="sr-only">
          Numéro de commande
        </label>
        <input
          id="numero"
          value={numero}
          onChange={(e) => setNumero(e.target.value)}
          maxLength={32}
          autoComplete="off"
          placeholder="ELSI-……"
          className="tabular h-14 flex-1 border border-ivory/20 bg-transparent px-4 text-lg uppercase tracking-[0.08em] placeholder:text-zinc-500 focus:border-brass-300 focus:outline-none"
        />
        <button type="submit" disabled={loading} aria-busy={loading} className="h-14 bg-ivory px-8 text-[13px] font-medium uppercase tracking-label text-ink-950 hover:bg-brass-300 disabled:opacity-70">
          {loading ? 'Recherche…' : 'Suivre'}
        </button>
      </form>

      <div aria-live="polite" className="mt-12">
        <AnimatePresence mode="wait">
          {result && result.kind !== 'found' && (
            <motion.div key={result.kind} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="border-t border-ivory/10 pt-6">
              <p className="text-ivory">{result.kind === 'not_found' ? 'Aucune commande ne porte ce numéro.' : 'Le suivi en ligne n’est pas disponible pour le moment.'}</p>
              <p className="mt-2 text-sm text-zinc-400">L’atelier vous répond sur WhatsApp, numéro de commande en main.</p>
              <a href={askWhatsApp} target="_blank" rel="noopener noreferrer" className="link-draw mt-4 inline-block py-1 text-emerald-300">
                Demander sur WhatsApp
              </a>
            </motion.div>
          )}

          {result?.kind === 'found' && (
            <motion.div key="found" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="border-t border-ivory/10 pt-8">
              {cancelled ? (
                <p className="text-ember-300">Cette commande a été annulée. Écrivez-nous si c’est une erreur.</p>
              ) : (
                <ol className="relative space-y-8 pl-10">
                  <span aria-hidden className="absolute bottom-2 left-[11px] top-2 w-px bg-ivory/10" />
                  {STEPS.map((s, i) => {
                    const done = i < current || (i === current && s.key === 'livree');
                    const now = i === current && s.key !== 'livree';
                    return (
                      <motion.li
                        key={s.key}
                        aria-current={now ? 'step' : undefined}
                        initial={{ opacity: 0, x: -8 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.15 + i * 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                        className="relative"
                      >
                        <span
                          aria-hidden
                          className={`absolute -left-10 top-0.5 grid h-6 w-6 place-items-center rounded-full border bg-ink-950 ${
                            done ? 'border-brass-400 !bg-brass-400 text-ink-950' : now ? 'border-brass-300 text-brass-300' : 'border-ivory/20 text-transparent'
                          }`}
                        >
                          {done ? <Check className="h-3.5 w-3.5" /> : <span className="h-1.5 w-1.5 rounded-full bg-current" />}
                        </span>
                        <p className={done || now ? 'text-ivory' : 'text-zinc-500'}>
                          {s.titre}
                          {now && <span className="ml-3 text-[11px] uppercase tracking-label text-brass-300">en cours</span>}
                        </p>
                        <p className="mt-1 text-sm text-zinc-400">{s.detail}</p>
                      </motion.li>
                    );
                  })}
                </ol>
              )}
              <a href={askWhatsApp} target="_blank" rel="noopener noreferrer" className="link-draw mt-10 inline-block py-1 text-sm text-emerald-300">
                Une question sur la livraison ? Écrire sur WhatsApp
              </a>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </section>
  );
}
