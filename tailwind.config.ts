import type { Config } from 'tailwindcss';

// Every colour resolves to an OKLCH triplet declared in app/globals.css (:root), direction « Galerie ».
// New code uses the role names (paper, panel, stone, ink, mute, indigo, cola, green).
// Legacy names from the former dark theme are re-pointed to the matching role, inverted,
// so a dark surface with light text becomes a light surface with dark text:
//   ink-950 → paper, ink-900 → panel, ink-800 → stone, ivory → ink, brass/gold → indigo, zinc → mute.
const v = (name: string) => `oklch(var(--${name}) / <alpha-value>)`;

const indigo = { 200: v('indigo-200'), 300: v('indigo-300'), 400: v('indigo-400'), 500: v('indigo-500'), 600: v('indigo-600'), 700: v('indigo-700') };
const cola = { 300: v('cola-300'), 400: v('cola-400'), 500: v('cola-500') };
const green = {
  200: v('green-200'), 300: v('green-300'), 400: v('green-400'), 500: v('green-500'),
  600: v('green-600'), 900: v('green-900'), 950: v('green-950'),
};
const mute = { 200: v('mute-200'), 300: v('mute-300'), 400: v('mute-400'), 500: v('mute-500'), 600: v('mute-600') };

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Roles
        paper: v('paper'),
        panel: v('panel'),
        stone: { DEFAULT: v('stone'), deep: v('stone-deep') },
        ink: { DEFAULT: v('ink'), 950: v('paper'), 900: v('panel'), 800: v('stone'), 700: v('stone-deep') },
        mute: { DEFAULT: v('mute-400'), ...mute },
        indigo: { DEFAULT: v('indigo-400'), tint: v('indigo-tint'), ...indigo },
        cola: { DEFAULT: v('cola-300'), ...cola },
        green: { DEFAULT: v('green-300'), ...green },

        // Legacy aliases
        dark: { 950: v('paper'), 900: v('panel'), 800: v('stone') },
        ivory: v('ink'),
        linen: { DEFAULT: v('stone'), deep: v('stone-deep'), ink: v('ink'), muted: v('mute-400') },
        brass: indigo,
        gold: indigo,
        ember: cola,
        amber: cola,
        red: { 400: v('cola-300'), 500: v('cola-400'), 600: v('cola-500') },
        emerald: green,
        atelier: { deep: v('green-950'), emerald: v('green-900'), silk: v('green-600'), gold: v('indigo-400') },
        zinc: { ...mute, 800: v('stone-deep'), 900: v('stone') },
      },
      fontFamily: {
        sans: ['var(--font-text)', '"Helvetica Neue"', 'Arial', 'sans-serif'],
        serif: ['var(--font-display)', 'Georgia', 'serif'],
        display: ['var(--font-display)', 'Georgia', 'serif'],
      },
      transitionTimingFunction: {
        premium: 'var(--ease-silk)',
        silk: 'var(--ease-silk)',
        velvet: 'var(--ease-velvet)',
        curtain: 'var(--ease-curtain)',
      },
      transitionDuration: {
        feedback: 'var(--dur-feedback)',
        ui: 'var(--dur-ui)',
        story: 'var(--dur-story)',
      },
      borderRadius: {
        chip: '999px',
        card: '2px',
        plate: '0px',
      },
      boxShadow: {
        lift: '0 24px 48px -28px oklch(0.2 0.02 270 / 0.35)',
        drawer: '-24px 0 60px -30px oklch(0.2 0.02 270 / 0.3)',
      },
      animation: {
        'fade-up': 'fadeUp var(--dur-ui) var(--ease-silk) both',
        'fade-in': 'fadeIn var(--dur-ui) var(--ease-silk) both',
        'scale-in': 'scaleIn var(--dur-ui) var(--ease-silk) both',
      },
      keyframes: {
        fadeUp: { '0%': { opacity: '0', transform: 'translateY(14px)' }, '100%': { opacity: '1', transform: 'none' } },
        fadeIn: { '0%': { opacity: '0' }, '100%': { opacity: '1' } },
        scaleIn: { '0%': { opacity: '0', transform: 'scale(0.97)' }, '100%': { opacity: '1', transform: 'none' } },
      },
    },
  },
  plugins: [],
};

export default config;
