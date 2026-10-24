'use client';

import type { InputHTMLAttributes, ReactNode } from 'react';
import { AnimatePresence, motion } from 'motion/react';

interface Props extends InputHTMLAttributes<HTMLInputElement> {
  id: string;
  label: string;
  hint?: string;
  error?: string;
  children?: ReactNode;
}

/** Labelled input with hint + animated error, wired for screen readers. */
export default function Field({ id, label, hint, error, children, ...input }: Props) {
  const describedBy = [hint && `${id}-hint`, error && `${id}-err`].filter(Boolean).join(' ') || undefined;
  return (
    <div>
      <label htmlFor={id} className="mb-2 block text-[11px] uppercase tracking-label text-zinc-400">
        {label}
      </label>
      {children ?? (
        <input
          id={id}
          aria-invalid={!!error}
          aria-describedby={describedBy}
          className={`h-12 w-full border bg-transparent px-4 text-base text-ivory transition-colors duration-feedback placeholder:text-zinc-500 focus:outline-none ${
            error ? 'border-ember-400' : 'border-ivory/20 hover:border-ivory/35 focus:border-brass-300'
          }`}
          {...input}
        />
      )}
      {hint && !error && (
        <p id={`${id}-hint`} className="mt-1.5 text-xs text-zinc-500">
          {hint}
        </p>
      )}
      <AnimatePresence>
        {error && (
          <motion.p id={`${id}-err`} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-1.5 text-xs text-ember-300">
            {error}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}
