'use client';

import { useEffect, useRef, useState } from 'react';
import type { FormEvent } from 'react';
import Link from 'next/link';
import { AnimatePresence, motion } from 'motion/react';
import { ArrowLeft, Check } from 'lucide-react';
import { useStore } from '@/lib/store-context';
import { deliveryFee, subtotal } from '@/lib/cart.ts';
import { COMMUNES, formatFCFA, waLink } from '@/lib/config';
import { createCommande } from '@/lib/supabase';
import type { CartItem, Commande } from '@/lib/types';
import { PAYMENT_LABELS, normalizePhoneCI, orderNumber, validateContact, validateDelivery } from '@/lib/checkout.ts';
import type { CheckoutForm, FieldErrors, PaymentMethod } from '@/lib/checkout.ts';
import Field from '@/components/checkout/Field';
import OrderSummary from '@/components/checkout/OrderSummary';

const STEPS = ['Coordonnées', 'Livraison', 'Paiement'] as const;
const TITLES = ['À qui livrons-nous ?', 'Où vous trouver ?', 'Comment régler ?'] as const;
const SILK = [0.16, 1, 0.3, 1] as const;

const stepMotion = {
  enter: (dir: number) => ({ opacity: 0, x: 32 * dir, filter: 'blur(3px)' }),
  center: { opacity: 1, x: 0, filter: 'blur(0px)' },
  exit: (dir: number) => ({ opacity: 0, x: -32 * dir, filter: 'blur(3px)' }),
};

interface Confirmed {
  numero: string;
  total: number;
  whatsapp: string;
}

function whatsappRecap(numero: string, form: CheckoutForm, items: CartItem[], fee: number, total: number): string {
  const lines = items.map((i) => `• ${i.article.nom} — ${i.taille}, ${i.couleur} × ${i.quantite}`).join('\n');
  return [
    `Bonjour ELSI, voici ma commande ${numero} :`,
    lines,
    `Livraison : ${form.commune}, ${form.adresse}${form.instructions ? ` (${form.instructions})` : ''} — ${fee ? formatFCFA(fee) : 'offerte'}`,
    `Paiement : ${PAYMENT_LABELS[form.paiement].titre}`,
    `Total : ${formatFCFA(total)}`,
    `Nom : ${form.nom} · ${form.telephone}`,
  ].join('\n');
}

export default function CheckoutFlow() {
  const { items, hydrated, clear } = useStore();
  const [step, setStep] = useState(0);
  const [dir, setDir] = useState(1);
  const [form, setForm] = useState<CheckoutForm>({ nom: '', telephone: '', commune: 'Cocody', adresse: '', instructions: '', paiement: 'livraison' });
  const [errors, setErrors] = useState<FieldErrors>({});
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirmed, setConfirmed] = useState<Confirmed | null>(null);
  const headingRef = useRef<HTMLHeadingElement>(null);
  const firstRender = useRef(true);
  const pendingFocus = useRef(false);

  const sousTotal = subtotal(items);
  const fee = deliveryFee(items, form.commune);
  const total = sousTotal + fee;

  // Confirmation screen: announce it. Step changes focus their heading once the
  // incoming step has finished animating (onAnimationComplete below).
  useEffect(() => {
    if (firstRender.current) {
      firstRender.current = false;
      return;
    }
    headingRef.current?.focus();
  }, [confirmed]);

  const set = <K extends keyof CheckoutForm>(key: K, value: CheckoutForm[K]) => {
    setForm((f) => ({ ...f, [key]: value }));
    if (errors[key]) setErrors((e) => ({ ...e, [key]: undefined }));
  };

  const goTo = (target: number) => {
    pendingFocus.current = true;
    setDir(target > step ? 1 : -1);
    setStep(target);
  };

  const submit = async () => {
    setSubmitting(true);
    setSubmitError(null);
    const numero = orderNumber();
    const payload: Commande = {
      numero_commande: numero,
      client_nom: form.nom.trim(),
      client_telephone: normalizePhoneCI(form.telephone) ?? form.telephone,
      client_adresse: [form.adresse.trim(), form.instructions.trim()].filter(Boolean).join(' — '),
      commune_livraison: form.commune,
      articles_commande: items,
      montant_total: total,
      frais_livraison: fee,
      statut: 'en_attente',
      canal_origine: 'web',
      mode_paiement: form.paiement,
    };
    const result = await createCommande(payload).catch((err: unknown) => ({
      success: false,
      error: err instanceof Error ? err.message : 'Erreur réseau',
    }));
    setSubmitting(false);
    if (!result.success) {
      setSubmitError('La commande n’a pas pu être enregistrée. Réessayez, ou envoyez-la directement sur WhatsApp : rien n’est perdu.');
      return;
    }
    setConfirmed({ numero, total, whatsapp: waLink(whatsappRecap(numero, form, items, fee, total)) });
    clear();
  };

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    const found = step === 0 ? validateContact(form) : step === 1 ? validateDelivery(form) : {};
    setErrors(found);
    const firstInvalid = Object.keys(found)[0];
    if (firstInvalid) {
      document.getElementById(`f-${firstInvalid}`)?.focus();
      return;
    }
    if (step < 2) goTo(step + 1);
    else void submit();
  };

  if (!hydrated) {
    return <div role="status" aria-label="Chargement du panier" className="skeleton mx-auto mt-16 h-96 max-w-3xl" />;
  }

  if (confirmed) {
    return (
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: SILK }}
        className="mx-auto flex max-w-xl flex-col items-center px-[var(--gutter)] py-24 text-center"
      >
        <motion.span
          initial={{ scale: 0.6, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.2, duration: 0.5, ease: SILK }}
          className="grid h-16 w-16 place-items-center rounded-full border border-brass-400 text-brass-300"
        >
          <Check className="h-7 w-7" strokeWidth={1.6} />
        </motion.span>
        <h1 ref={headingRef} tabIndex={-1} className="text-display mt-8 text-5xl focus:outline-none">
          Merci, {form.nom.trim().split(' ')[0]}.
        </h1>
        <p className="mt-4 text-zinc-300">
          Commande <span className="tabular text-brass-300">{confirmed.numero}</span> enregistrée · {formatFCFA(confirmed.total)}.
        </p>
        <p className="mt-2 max-w-[44ch] text-sm text-zinc-400">
          Envoyez le récapitulatif sur WhatsApp : l’atelier vous confirme le créneau de livraison.
        </p>
        <a href={confirmed.whatsapp} target="_blank" rel="noopener noreferrer" className="mt-8 w-full bg-emerald-600 py-4 text-[13px] font-medium uppercase tracking-label text-ivory hover:bg-emerald-500">
          Envoyer le récapitulatif sur WhatsApp
        </a>
        <Link href="/catalogue" className="link-draw mt-5 text-sm text-zinc-300">
          Retour à la collection
        </Link>
      </motion.section>
    );
  }

  if (items.length === 0) {
    return (
      <section className="mx-auto flex max-w-xl flex-col items-center gap-5 px-[var(--gutter)] py-28 text-center">
        <h1 className="text-display text-4xl">Votre panier est vide</h1>
        <p className="text-zinc-400">Ajoutez une pièce pour passer commande.</p>
        <Link href="/catalogue" className="bg-ivory px-7 py-3.5 text-xs font-medium uppercase tracking-label text-ink-950 hover:bg-brass-300">
          Voir la collection
        </Link>
      </section>
    );
  }

  return (
    <div className="mx-auto grid max-w-[1200px] gap-12 px-[var(--gutter)] pb-24 pt-10 lg:grid-cols-[minmax(0,1fr)_380px] lg:gap-20">
      <div>
        <ol aria-label="Étapes de la commande" className="mb-3 flex gap-6 text-[11px] uppercase tracking-label">
          {STEPS.map((label, i) => (
            <li key={label} aria-current={i === step ? 'step' : undefined}>
              <button
                type="button"
                disabled={i >= step}
                onClick={() => goTo(i)}
                className={`py-2 transition-colors ${i === step ? 'text-ivory' : i < step ? 'text-brass-300 hover:text-brass-200' : 'text-zinc-500'}`}
              >
                <span className="tabular mr-1.5">{i + 1}.</span>
                {label}
              </button>
            </li>
          ))}
        </ol>
        <div className="mb-10 h-px bg-ivory/10" role="progressbar" aria-valuemin={1} aria-valuemax={3} aria-valuenow={step + 1} aria-label="Progression de la commande">
          <motion.div className="h-px origin-left bg-brass-400" animate={{ scaleX: (step + 1) / 3 }} transition={{ duration: 0.6, ease: SILK }} />
        </div>

        <form onSubmit={onSubmit} noValidate>
          <AnimatePresence mode="wait" custom={dir} initial={false}>
            <motion.fieldset
              key={step}
              custom={dir}
              variants={stepMotion}
              initial="enter"
              animate="center"
              exit="exit"
              transition={{ duration: 0.32, ease: SILK }}
              onAnimationComplete={(def) => {
                if (def !== 'center' || !pendingFocus.current) return;
                pendingFocus.current = false;
                headingRef.current?.focus();
              }}
              className="space-y-6"
            >
              <legend className="sr-only">{STEPS[step]}</legend>
              <h1 ref={headingRef} tabIndex={-1} className="text-display text-4xl focus:outline-none md:text-5xl">
                {TITLES[step]}
              </h1>

              {step === 0 && (
                <>
                  <Field id="f-nom" label="Nom complet" autoComplete="name" value={form.nom} onChange={(e) => set('nom', e.target.value)} error={errors.nom} maxLength={80} />
                  <Field
                    id="f-telephone"
                    label="Numéro WhatsApp"
                    type="tel"
                    inputMode="tel"
                    autoComplete="tel"
                    placeholder="07 00 00 00 00"
                    hint="Le coursier vous appelle sur ce numéro avant de passer."
                    value={form.telephone}
                    onChange={(e) => set('telephone', e.target.value)}
                    error={errors.telephone}
                  />
                </>
              )}

              {step === 1 && (
                <>
                  <Field id="f-commune" label="Commune" error={errors.commune}>
                    <select
                      id="f-commune"
                      value={form.commune}
                      onChange={(e) => set('commune', e.target.value)}
                      className="h-12 w-full border border-ivory/20 bg-ink-950 px-4 text-base text-ivory focus:border-brass-300 focus:outline-none"
                    >
                      {COMMUNES.map((c) => (
                        <option key={c}>{c}</option>
                      ))}
                    </select>
                  </Field>
                  <Field
                    id="f-adresse"
                    label="Quartier et repère"
                    placeholder="Angré 8e tranche, près de la pharmacie"
                    autoComplete="street-address"
                    value={form.adresse}
                    onChange={(e) => set('adresse', e.target.value)}
                    error={errors.adresse}
                    maxLength={160}
                  />
                  <Field
                    id="f-instructions"
                    label="Précisions (facultatif)"
                    placeholder="Portail vert, 2e étage, après 18 h…"
                    value={form.instructions}
                    onChange={(e) => set('instructions', e.target.value)}
                    maxLength={160}
                  />
                  <p className="text-sm text-zinc-400">
                    Frais pour {form.commune} : <span className="tabular text-ivory">{fee === 0 ? 'offerts' : formatFCFA(fee)}</span>
                  </p>
                </>
              )}

              {step === 2 && (
                <div role="radiogroup" aria-label="Mode de paiement" className="space-y-2">
                  {(Object.keys(PAYMENT_LABELS) as PaymentMethod[]).map((m) => {
                    const selected = form.paiement === m;
                    return (
                      <label
                        key={m}
                        className={`flex cursor-pointer items-start gap-4 border p-4 transition-colors duration-feedback ${selected ? 'border-brass-300' : 'border-ivory/15 hover:border-ivory/30'}`}
                      >
                        <input type="radio" name="paiement" value={m} checked={selected} onChange={() => set('paiement', m)} className="mt-1 accent-brass-400" />
                        <span>
                          <span className="block text-ivory">{PAYMENT_LABELS[m].titre}</span>
                          <span className="text-sm text-zinc-400">{PAYMENT_LABELS[m].detail}</span>
                        </span>
                      </label>
                    );
                  })}
                </div>
              )}
            </motion.fieldset>
          </AnimatePresence>

          <AnimatePresence>
            {submitError && (
              <motion.div role="alert" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-8 border border-ember-400/60 p-4 text-sm text-ember-300">
                <p>{submitError}</p>
                <a href={waLink(whatsappRecap('(à confirmer)', form, items, fee, total))} target="_blank" rel="noopener noreferrer" className="link-draw mt-2 inline-block text-emerald-300">
                  Envoyer la commande sur WhatsApp
                </a>
              </motion.div>
            )}
          </AnimatePresence>

          <div className="mt-10 flex items-center gap-4">
            {step > 0 && (
              <button type="button" onClick={() => goTo(step - 1)} className="flex h-14 items-center gap-2 px-2 text-sm text-zinc-300 hover:text-ivory">
                <ArrowLeft className="h-4 w-4" /> Retour
              </button>
            )}
            <button
              type="submit"
              disabled={submitting}
              aria-busy={submitting}
              className="tabular ml-auto h-14 min-w-[min(240px,100%)] flex-1 bg-ivory px-6 text-[13px] font-medium uppercase tracking-label text-ink-950 transition-colors duration-feedback hover:bg-brass-300 disabled:cursor-wait disabled:opacity-70 sm:flex-none"
            >
              {submitting ? 'Enregistrement…' : step < 2 ? 'Continuer' : `Confirmer · ${formatFCFA(total)}`}
            </button>
          </div>
        </form>
      </div>

      <aside aria-label="Récapitulatif" className="lg:sticky lg:top-[calc(var(--header-h)+24px)] lg:self-start">
        <details className="border-y border-ivory/[0.08] lg:border-0" open>
          <summary className="flex cursor-pointer list-none items-center justify-between py-4 text-sm lg:pointer-events-none lg:pb-2">
            <span className="text-display text-2xl">Récapitulatif</span>
            <span className="tabular text-zinc-300 lg:hidden">{formatFCFA(total)}</span>
          </summary>
          <OrderSummary items={items} sousTotal={sousTotal} livraison={fee} />
        </details>
      </aside>
    </div>
  );
}
