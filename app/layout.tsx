import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: "Boutique en Ligne — Mode & Prêt-à-Porter Chic à Abidjan",
  description: "Découvrez notre collection exclusive de robes de soirée, costumes sur mesure, chemises lin & wax et accessoires. Livraison 24h à Abidjan et partout en Côte d'Ivoire.",
  keywords: "boutique en ligne, vetements abidjan, robe soiree, costume homme abidjan, pret a porter chic cote d'ivoire, wax lin",
  openGraph: {
    title: "Boutique en Ligne — Prêt-à-Porter d'Exception",
    description: "Habillez votre élégance au quotidien. Livraison 24h et conseils avec notre Styliste IA.",
    locale: 'fr_FR',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr" className="dark">
      <body className="min-h-screen bg-dark-950 text-white flex flex-col selection:bg-gold-500 selection:text-dark-950">
        {children}
      </body>
    </html>
  );
}
