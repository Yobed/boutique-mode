'use client';

import { useRef } from 'react';
import type { KeyboardEvent } from 'react';
import { motion } from 'motion/react';

interface Props {
  label: string;
  options: string[];
  value: string;
  onChange: (v: string) => void;
  /** Must be unique on the page: drives the shared-layout highlight. */
  groupId: string;
  size?: 'sm' | 'md';
}

/** Accessible radiogroup; the selected highlight glides between options (layoutId). */
export default function VariantSelector({ label, options, value, onChange, groupId, size = 'md' }: Props) {
  const refs = useRef<(HTMLButtonElement | null)[]>([]);
  if (options.length === 0) return null;

  const onKey = (e: KeyboardEvent<HTMLButtonElement>, i: number) => {
    const delta = e.key === 'ArrowRight' || e.key === 'ArrowDown' ? 1 : e.key === 'ArrowLeft' || e.key === 'ArrowUp' ? -1 : 0;
    if (!delta) return;
    e.preventDefault();
    const next = (i + delta + options.length) % options.length;
    onChange(options[next]);
    refs.current[next]?.focus();
  };

  // Touch targets stay ≥ 44px; the compact size only applies with a fine pointer.
  const pad = size === 'sm' ? 'h-11 min-w-11 px-2.5 text-xs [@media(pointer:fine)]:h-9 [@media(pointer:fine)]:min-w-9' : 'h-11 min-w-11 px-4 text-sm';

  return (
    <div role="radiogroup" aria-label={label} className="flex flex-wrap gap-1.5">
      {options.map((opt, i) => {
        const selected = opt === value;
        return (
          <button
            key={opt}
            ref={(el) => {
              refs.current[i] = el;
            }}
            type="button"
            role="radio"
            aria-checked={selected}
            tabIndex={selected ? 0 : -1}
            onClick={() => onChange(opt)}
            onKeyDown={(e) => onKey(e, i)}
            className={`tabular relative border border-ivory/15 ${pad} transition-colors duration-feedback ${
              selected ? 'text-ink-950' : 'text-zinc-300 hover:border-ivory/40 hover:text-ivory'
            }`}
          >
            {selected && (
              <motion.span
                layoutId={`variant-${groupId}`}
                className="absolute inset-0 bg-ivory"
                transition={{ type: 'spring', stiffness: 520, damping: 42, mass: 0.8 }}
                aria-hidden
              />
            )}
            <span className="relative">{opt}</span>
          </button>
        );
      })}
    </div>
  );
}
