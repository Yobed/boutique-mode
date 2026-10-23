import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#fbf8f3',
          100: '#f5eee3',
          200: '#ebd9c4',
          300: '#dec09f',
          400: '#cfa277',
          500: '#c18556',
          600: '#b46f47',
          700: '#96573c',
          800: '#794735',
          900: '#633c2e',
          950: '#351e17',
        },
        gold: {
          400: '#e5c158',
          500: '#d4af37',
          600: '#a88424',
        },
        atelier: {
          deep: '#0a231b',
          emerald: '#12382c',
          silk: '#1a5d46',
          gold: '#d4af37',
        },
        dark: {
          800: '#1c1c22',
          900: '#141418',
          950: '#0c0c0e',
        }
      },
      fontFamily: {
        sans: ['"Tenor Sans"', 'system-ui', 'sans-serif'],
        serif: ['Italiana', 'Georgia', 'serif'],
        display: ['Italiana', 'Georgia', 'serif'],
      },
      transitionTimingFunction: {
        'premium': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      animation: {
        'fade-up': 'fadeUp 500ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'fade-in': 'fadeIn 350ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'scale-in': 'scaleIn 350ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'drawer-in': 'drawerSlideIn 400ms cubic-bezier(0.4, 0, 0.2, 1) forwards',
        'pulse-subtle': 'pulseSubtle 3s ease-in-out infinite',
        'shimmer': 'shimmer 2.5s infinite',
      },
      keyframes: {
        fadeUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.97)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        drawerSlideIn: {
          '0%': { transform: 'translateX(100%)' },
          '100%': { transform: 'translateX(0)' },
        },
        pulseSubtle: {
          '0%, 100%': { opacity: '1', transform: 'scale(1)' },
          '50%': { opacity: '0.92', transform: 'scale(1.02)' },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
};

export default config;
