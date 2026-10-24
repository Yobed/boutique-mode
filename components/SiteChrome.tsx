'use client';

import type { ReactNode } from 'react';
import { usePathname } from 'next/navigation';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import CartDrawer from '@/components/CartDrawer';
import StylistChatWidget from '@/components/StylistChatWidget';
import CartFeedback from '@/components/chrome/CartFeedback';
import Cursor from '@/components/fx/Cursor';
import { useStore } from '@/lib/store-context';

/** Storefront chrome rendered once for every route (the back-office keeps its own). */
export default function SiteChrome({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { stylistOpen, setStylistOpen, add } = useStore();

  if (pathname?.startsWith('/admin')) return <>{children}</>;

  return (
    <>
      <a
        href="#contenu"
        className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[100] focus:bg-brass-400 focus:px-4 focus:py-2 focus:text-ink-950"
      >
        Aller au contenu
      </a>
      <Navbar />
      <main id="contenu" className="flex-1">
        {children}
      </main>
      <Footer />
      <CartDrawer />
      <StylistChatWidget
        isOpen={stylistOpen}
        onToggle={() => setStylistOpen(!stylistOpen)}
        onAddToCart={(article, taille, couleur) => add(article, taille, couleur)}
        hideLauncher={pathname?.startsWith('/article') || pathname?.startsWith('/commande')}
      />
      <CartFeedback />
      <Cursor />
    </>
  );
}
