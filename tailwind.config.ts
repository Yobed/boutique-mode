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
          400: '#fbbf24',
          500: '#d4af37',
          600: '#b8962c',
        },
        dark: {
          800: '#18181b',
          900: '#0f0f12',
          950: '#09090b',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Playfair Display', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
};

export default config;
