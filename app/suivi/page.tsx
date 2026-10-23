'use client';

import React, { useState } from 'react';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import CartDrawer from '@/components/CartDrawer';
import StylistChatWidget from '@/components/StylistChatWidget';
import { CartItem } from '@/lib/types';
import { Search, PackageCheck, Truck, Clock, CheckCircle2, MapPin, MessageCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface OrderTimelineStep {
  title: string;
  description: string;
  time: string;
  done: boolean;
  current: boolean;
}

export default function OrderTrackingPage() {
  const [searchVal, setSearchVal] = useState('');
  const [searched, setSearched] = useState(false);
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [cartOpen, setCartOpen] = useState(false);
  const [stylistOpen, setStylistOpen] = useState(false);

  // Exemple d'étapes de suivi
  const timeline: OrderTimelineStep[] = [
    {
      title: 'Commande enregistrée',
      description: 'Détails validés et transmis au chef d\'atelier',
      time: 'Aujourd\'hui 10:15',
      done: true,
      current: false,
    },
    {
      title: 'Préparation & Contrôle Qualité',
      description: 'Vérification du tissu, repassage vapeur et mise sous housse',
      time: 'Aujourd\'hui 11:30',
      done: true,
      current: false,
    },
    {
      title: 'Prise en charge par le coursier',
      description: 'Colis confié au livreur express Abidjan (Moto n°14)',
      time: 'Aujourd\'hui 13:45',
      done: true,
      current: true,
    },
    {
      title: 'Livraison à destination',
      description: 'En route vers votre adresse de livraison (Cocody / Plateau)',
      time: 'Estimé entre 15:00 et 16:30',
      done: false,
      current: false,
    },
    {
      title: 'Remise en main propre',
      description: 'Essayage immédiat et règlement à la livraison (Espèces / Wave)',
      time: 'En attente',
      done: false,
      current: false,
    },
  ];

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchVal.trim()) return;
    setSearched(true);
  };

  return (
    <>
      <Navbar
        cartItems={cartItems}
        onOpenCart={() => setCartOpen(true)}
        onOpenStylist={() => setStylistOpen(true)}
      />

      <main className="flex-1 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 w-full">
        {/* Title */}
        <div className="text-center max-w-xl mx-auto space-y-3">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-gold-500/10 border border-gold-500/20 text-gold-400 text-xs font-semibold uppercase tracking-widest">
            <Truck className="w-3.5 h-3.5" />
            <span>Service Expéditions Abidjan</span>
          </div>
          <h1 className="font-serif text-3xl sm:text-4xl font-normal text-white">
            Suivi de Votre Commande
          </h1>
          <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed">
            Consultez en direct l'avancement de la préparation de vos vêtements et la géolocalisation du coursier.
          </p>
        </div>

        {/* Search Input */}
        <form onSubmit={handleSearch} className="mt-8 max-w-xl mx-auto">
          <div className="flex gap-2 p-1.5 rounded-2xl bg-dark-900 border border-white/10 shadow-xl focus-within:border-gold-500/50">
            <div className="flex items-center pl-3 text-zinc-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              placeholder="Numéro de commande (ex: CMD-849201) ou WhatsApp..."
              className="flex-1 bg-transparent px-2 py-2.5 text-xs sm:text-sm text-white placeholder-zinc-500 focus:outline-none"
            />
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-gold-500 hover:bg-gold-400 text-dark-950 font-bold text-xs uppercase tracking-wider transition-all duration-150 ease-premium motion-press whitespace-nowrap"
            >
              Suivre
            </button>
          </div>
          {!searched && (
            <p className="text-center text-[11px] text-zinc-500 mt-2">
              Astuce : Cliquez sur "Suivre" ou tapez un numéro pour afficher la simulation en temps réel.
            </p>
          )}
        </form>

        {/* Results Area */}
        {searched && (
          <div className="mt-10 space-y-8 animate-scale-in">
            {/* Status Card */}
            <div className="p-6 rounded-3xl bg-dark-900 border border-white/10 shadow-2xl space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-white/10">
                <div>
                  <span className="text-[11px] text-zinc-400 uppercase tracking-wider block">
                    Référence Commande
                  </span>
                  <span className="font-mono text-lg font-bold text-gold-400">
                    {searchVal.trim() ? searchVal.toUpperCase() : 'CMD-849201'}
                  </span>
                </div>
                <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-300 text-xs font-semibold self-start sm:self-auto">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse-subtle" />
                  <span>En cours de livraison</span>
                </div>
              </div>

              {/* Delivery Meta */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-xs">
                <div>
                  <span className="text-zinc-500 block">Destination :</span>
                  <span className="text-white font-medium flex items-center gap-1 mt-0.5">
                    <MapPin className="w-3.5 h-3.5 text-gold-400" />
                    Cocody, Abidjan
                  </span>
                </div>
                <div>
                  <span className="text-zinc-500 block">Mode de règlement :</span>
                  <span className="text-white font-medium mt-0.5 block">
                    À la livraison (Wave / Espèces)
                  </span>
                </div>
                <div>
                  <span className="text-zinc-500 block">Garantie Atelier :</span>
                  <span className="text-emerald-400 font-medium mt-0.5 block">
                    Essayage avant paiement
                  </span>
                </div>
              </div>
            </div>

            {/* Stepper Timeline */}
            <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-white/10 shadow-2xl">
              <h3 className="font-serif text-lg font-normal text-white mb-6">
                Journal d'Acheminement
              </h3>

              <div className="relative pl-6 space-y-8 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-white/10">
                {timeline.map((step, idx) => (
                  <div key={idx} className="relative">
                    {/* Step Icon */}
                    <div
                      className={`absolute -left-6 top-0 w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                        step.done
                          ? 'bg-gold-500 text-dark-950'
                          : step.current
                          ? 'bg-emerald-500 text-dark-950 ring-4 ring-emerald-500/20'
                          : 'bg-dark-950 border border-white/20 text-zinc-500'
                      }`}
                    >
                      {step.done ? (
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      ) : (
                        <span className="w-1.5 h-1.5 rounded-full bg-current" />
                      )}
                    </div>

                    {/* Step Info */}
                    <div className="space-y-0.5">
                      <div className="flex items-center gap-2">
                        <h4
                          className={`text-sm font-semibold ${
                            step.current
                              ? 'text-gold-400'
                              : step.done
                              ? 'text-white'
                              : 'text-zinc-500'
                          }`}
                        >
                          {step.title}
                        </h4>
                        {step.current && (
                          <span className="px-2 py-0.5 rounded-full bg-emerald-500/20 border border-emerald-500/40 text-emerald-300 text-[10px] font-bold uppercase">
                            Étape Actuelle
                          </span>
                        )}
                      </div>
                      <p className="text-xs text-zinc-400">{step.description}</p>
                      <div className="flex items-center gap-1 text-[11px] text-zinc-500 pt-0.5 font-mono">
                        <Clock className="w-3 h-3 text-zinc-500" />
                        <span>{step.time}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* WhatsApp Live Contact */}
              <div className="mt-8 pt-6 border-t border-white/10 flex flex-col sm:flex-row items-center justify-between gap-4">
                <p className="text-xs text-zinc-400 text-center sm:text-left">
                  Une précision sur votre adresse ou besoin d'ajuster l'horaire de livraison ?
                </p>
                <a
                  href={`https://wa.me/2250778311541?text=${encodeURIComponent(
                    `Bonjour Maison Élégance, je souhaite des nouvelles de ma commande ${searchVal || 'CMD-849201'}`
                  )}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs uppercase tracking-wider transition-all duration-150 ease-premium motion-press whitespace-nowrap"
                >
                  <MessageCircle className="w-4 h-4" />
                  <span>Joindre le Livreur sur WhatsApp</span>
                </a>
              </div>
            </div>
          </div>
        )}

        {/* Back Link */}
        <div className="mt-12 text-center">
          <Link
            href="/catalogue"
            className="inline-flex items-center gap-2 text-xs text-zinc-400 hover:text-gold-400 transition-colors duration-150 ease-premium"
          >
            <span>Retourner au catalogue de vêtements</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </main>

      <CartDrawer
        isOpen={cartOpen}
        onClose={() => setCartOpen(false)}
        cartItems={cartItems}
        onUpdateQuantity={(idx, q) => {
          const u = [...cartItems];
          u[idx].quantite = q;
          setCartItems(u);
        }}
        onRemoveItem={(idx) => setCartItems(cartItems.filter((_, i) => i !== idx))}
        onClearCart={() => setCartItems([])}
      />

      <StylistChatWidget
        isOpen={stylistOpen}
        onToggle={() => setStylistOpen(!stylistOpen)}
        onAddToCart={(art, t, c) => setCartItems([...cartItems, { article: art, taille: t, couleur: c, quantite: 1 }])}
      />

      <Footer />
    </>
  );
}
