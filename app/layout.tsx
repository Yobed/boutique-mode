import type { Metadata, Viewport } from 'next';
import Providers from '@/components/Providers';
import SiteChrome from '@/components/SiteChrome';
import Preloader from '@/components/fx/Preloader';
import './globals.css';

// Fonts, chosen by the client: Zodiak (titles, roman + italic) and Switzer (text & UI),
// both by the Indian Type Foundry, served by Fontshare's official CSS API under the ITF Free Font
// Licence (commercial web use allowed). The families are mapped to --font-display / --font-text in globals.css.
const FONTS_CSS = 'https://api.fontshare.com/v2/css?f[]=zodiak@400,401&f[]=switzer@400,500,600&display=swap';

export const metadata: Metadata = {
  title: {
    default: 'ELSI — Vêtements & accessoires d’exception à Abidjan',
    template: '%s · ELSI',
  },
  description:
    'Robes du soir, costumes tailleur, créations wax et accessoires. Livraison 24 h à Abidjan, essayage à la livraison, paiement à la réception.',
  keywords: ['ELSI', 'boutique Abidjan', 'robe de soirée', 'costume homme Abidjan', 'wax', 'prêt-à-porter Côte d’Ivoire'],
  openGraph: {
    title: 'ELSI — Abidjan',
    description: 'Vêtements & accessoires d’exception. Livraison 24 h, essayage à la livraison.',
    locale: 'fr_CI',
    type: 'website',
  },
};

export const viewport: Viewport = {
  themeColor: '#FFFFFF',
  colorScheme: 'light',
};

// Static string, no user input: flags JS before paint so scroll scenes hold their pre-reveal state,
// and plays the brand intro only on the first page view of the session.
const jsFlag =
  "var d=document.documentElement;d.classList.add('js');try{if(sessionStorage.getItem('elsi-intro'))d.classList.add('no-intro');else sessionStorage.setItem('elsi-intro','1')}catch(e){d.classList.add('no-intro')}";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{ __html: jsFlag }} />
        <link rel="preconnect" href="https://api.fontshare.com" />
        <link rel="preconnect" href="https://cdn.fontshare.com" crossOrigin="anonymous" />
        {/* eslint-disable-next-line @next/next/no-page-custom-font -- root layout, loaded once for every page */}
        <link rel="stylesheet" href={FONTS_CSS} />
      </head>
      <body className="flex min-h-screen flex-col">
        <Preloader />
        <Providers>
          <SiteChrome>{children}</SiteChrome>
        </Providers>
      </body>
    </html>
  );
}
