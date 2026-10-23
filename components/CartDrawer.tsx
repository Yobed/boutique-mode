'use client';

import React, { useState } from 'react';
import { CartItem, Commande } from '@/lib/types';
import { X, Trash2, Plus, Minus, ShoppingBag, MessageCircle, CheckCircle, ShieldCheck } from 'lucide-react';
import { createCommande } from '@/lib/supabase';

interface CartDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  cartItems: CartItem[];
  onUpdateQuantity: (index: number, newQty: number) => void;
  onRemoveItem: (index: number) => void;
  onClearCart: () => void;
}

export default function CartDrawer({
  isOpen,
  onClose,
  cartItems,
  onUpdateQuantity,
  onRemoveItem,
  onClearCart,
}: CartDrawerProps) {
  const [nom, setNom] = useState('');
  const [telephone, setTelephone] = useState('');
  const [adresse, setAdresse] = useState('');
  const [commune, setCommune] = useState('Cocody');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [orderSuccess, setOrderSuccess] = useState<string | null>(null);

  if (!isOpen) return null;

  const subtotal = cartItems.reduce(
    (sum, item) => sum + (item.article.prix_promo || item.article.prix) * item.quantite,
    0
  );
  const fraisLivraison = commune.toLowerCase().includes('intérieur') || commune.toLowerCase().includes('interieur') ? 2500 : 1500;
  const total = subtotal + (cartItems.length > 0 ? fraisLivraison : 0);

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    if (cartItems.length === 0) return;

    setIsSubmitting(true);
    const numeroCommande = `CMD-${Date.now().toString().slice(-6)}`;

    const commandePayload: Commande = {
      numero_commande: numeroCommande,
      client_nom: nom || 'Client Boutique',
      client_telephone: telephone || 'Non précisé',
      client_adresse: adresse || 'Non précisé',
      commune_livraison: commune,
      articles_commande: cartItems,
      montant_total: total,
      frais_livraison: fraisLivraison,
      statut: 'en_attente',
      canal_origine: 'web',
    };

    try {
      await createCommande(commandePayload);

      // Génération du message WhatsApp récapitulatif
      const itemsList = cartItems
        .map(
          (item) =>
            `- *${item.article.nom}* (Taille: ${item.taille}, Qté: ${item.quantite}) = *${(
              (item.article.prix_promo || item.article.prix) * item.quantite
            ).toLocaleString('fr-FR')} FCFA*`
        )
        .join('\n');

      const waMsg = encodeURIComponent(
        `🛍️ *NOUVELLE COMMANDE - BOUTIQUE EN LIGNE*\n` +
        `Numéro : *${numeroCommande}*\n\n` +
        `👤 *Client :* ${nom}\n` +
        `📞 *Contact :* ${telephone}\n` +
        `📍 *Livraison :* ${commune} (${adresse})\n\n` +
        `📦 *Articles commandés :*\n${itemsList}\n\n` +
        `🚚 *Frais de livraison :* ${fraisLivraison.toLocaleString('fr-FR')} FCFA\n` +
        `💰 *TOTAL À PAYER :* *${total.toLocaleString('fr-FR')} FCFA*\n\n` +
        `Merci de me confirmer la livraison !`
      );

      setOrderSuccess(numeroCommande);
      onClearCart();

      // Redirection automatique WhatsApp
      window.open(`https://wa.me/2250778311541?text=${waMsg}`, '_blank');
    } catch (err) {
      console.error(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/70 backdrop-blur-sm animate-fade-in"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-dark-950 border-l border-white/10 text-white flex flex-col shadow-2xl animate-drawer-in">
          {/* Header */}
          <div className="p-5 border-b border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-gold-400" />
              <h2 className="font-serif font-bold text-lg text-white">Mon Panier</h2>
              <span className="text-xs bg-white/10 text-zinc-300 px-2 py-0.5 rounded-full font-mono">
                {cartItems.reduce((acc, i) => acc + i.quantite, 0)}
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors duration-150 ease-premium motion-press"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {orderSuccess ? (
              <div className="py-12 text-center space-y-4">
                <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto animate-bounce" />
                <h3 className="font-serif text-xl font-bold text-white">Commande Enregistrée !</h3>
                <p className="text-sm text-zinc-400">
                  Votre commande <strong className="text-gold-400">{orderSuccess}</strong> a été transmise. Un récapitulatif a été ouvert sur WhatsApp pour confirmation.
                </p>
                <button
                  onClick={() => {
                    setOrderSuccess(null);
                    onClose();
                  }}
                  className="px-6 py-2.5 rounded-full bg-gold-500 text-dark-950 font-bold text-xs uppercase tracking-wider"
                >
                  Continuer mes achats
                </button>
              </div>
            ) : cartItems.length === 0 ? (
              <div className="py-16 text-center space-y-3">
                <ShoppingBag className="w-12 h-12 text-zinc-600 mx-auto" />
                <p className="text-zinc-400 text-sm">Votre panier est actuellement vide.</p>
                <button
                  onClick={onClose}
                  className="px-5 py-2 rounded-full border border-gold-500/40 text-gold-400 text-xs font-semibold hover:bg-gold-500/10 transition-colors"
                >
                  Découvrir les vêtements
                </button>
              </div>
            ) : (
              <>
                {/* List of items */}
                <div className="space-y-3">
                  {cartItems.map((item, idx) => (
                    <div
                      key={`${item.article.id}-${item.taille}-${idx}`}
                      className="flex gap-3 p-3 rounded-xl bg-dark-900 border border-white/5 items-center"
                    >
                      <img
                        src={item.article.photos[0]}
                        alt={item.article.nom}
                        className="w-16 h-20 object-cover rounded-lg bg-zinc-800 flex-shrink-0"
                      />
                      <div className="flex-1 min-w-0">
                        <h4 className="font-serif font-bold text-sm text-white truncate">
                          {item.article.nom}
                        </h4>
                        <div className="text-xs text-zinc-400 mt-0.5">
                          Taille : <span className="text-gold-300 font-semibold">{item.taille}</span>
                        </div>
                        <div className="text-xs text-gold-400 font-bold mt-1">
                          {(
                            (item.article.prix_promo || item.article.prix) * item.quantite
                          ).toLocaleString('fr-FR')}{' '}
                          FCFA
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                          <button
                            type="button"
                            onClick={() => onUpdateQuantity(idx, item.quantite - 1)}
                            className="p-1 rounded bg-white/5 hover:bg-white/10 text-zinc-300 transition-transform duration-100 ease-premium motion-press"
                          >
                            <Minus className="w-3 h-3" />
                          </button>
                          <span className="text-xs font-bold text-white px-1">
                            {item.quantite}
                          </span>
                          <button
                            type="button"
                            onClick={() => onUpdateQuantity(idx, item.quantite + 1)}
                            className="p-1 rounded bg-white/5 hover:bg-white/10 text-zinc-300 transition-transform duration-100 ease-premium motion-press"
                          >
                            <Plus className="w-3 h-3" />
                          </button>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => onRemoveItem(idx)}
                        className="p-2 text-zinc-500 hover:text-red-400 transition-colors duration-150 ease-premium motion-press"
                        title="Supprimer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>

                {/* Formulaire de livraison */}
                <form id="order-form" onSubmit={handleSubmitOrder} className="pt-4 border-t border-white/10 space-y-3">
                  <h3 className="font-serif font-bold text-sm text-gold-400">
                    Informations de Livraison
                  </h3>

                  <div>
                    <label className="text-[11px] text-zinc-400 block mb-1">Nom complet *</label>
                    <input
                      type="text"
                      required
                      value={nom}
                      onChange={(e) => setNom(e.target.value)}
                      placeholder="Ex: Kouamé Jean"
                      className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-gold-500"
                    />
                  </div>

                  <div>
                    <label className="text-[11px] text-zinc-400 block mb-1">Numéro WhatsApp *</label>
                    <input
                      type="tel"
                      required
                      value={telephone}
                      onChange={(e) => setTelephone(e.target.value)}
                      placeholder="Ex: 07 78 31 15 41"
                      className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-gold-500"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="text-[11px] text-zinc-400 block mb-1">Commune / Ville *</label>
                      <select
                        value={commune}
                        onChange={(e) => setCommune(e.target.value)}
                        className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-gold-500"
                      >
                        <option value="Cocody">Cocody</option>
                        <option value="Marcory">Marcory</option>
                        <option value="Plateau">Plateau</option>
                        <option value="Yopougon">Yopougon</option>
                        <option value="Koumassi">Koumassi</option>
                        <option value="Treichville">Treichville</option>
                        <option value="Port-Bouët">Port-Bouët</option>
                        <option value="Bingerville">Bingerville</option>
                        <option value="Autre commune">Autre commune</option>
                        <option value="Intérieur du pays">Intérieur du pays</option>
                      </select>
                    </div>
                    <div>
                      <label className="text-[11px] text-zinc-400 block mb-1">Quartier / Repère</label>
                      <input
                        type="text"
                        value={adresse}
                        onChange={(e) => setAdresse(e.target.value)}
                        placeholder="Ex: Angré 8ème tranche"
                        className="w-full bg-dark-900 border border-white/10 rounded-xl px-3 py-2 text-xs text-white focus:outline-none focus:border-gold-500"
                      />
                    </div>
                  </div>
                </form>
              </>
            )}
          </div>

          {/* Footer Totals & CTA */}
          {cartItems.length > 0 && !orderSuccess && (
            <div className="p-5 border-t border-white/10 bg-dark-900/90 space-y-3">
              <div className="space-y-1.5 text-xs text-zinc-400">
                <div className="flex justify-between">
                  <span>Sous-total articles :</span>
                  <span className="text-white font-medium">{subtotal.toLocaleString('fr-FR')} FCFA</span>
                </div>
                <div className="flex justify-between">
                  <span>Frais de livraison :</span>
                  <span className="text-white font-medium">{fraisLivraison.toLocaleString('fr-FR')} FCFA</span>
                </div>
                <div className="flex justify-between text-sm font-bold text-white pt-2 border-t border-white/10">
                  <span>Total à payer :</span>
                  <span className="text-gold-400 text-base">{total.toLocaleString('fr-FR')} FCFA</span>
                </div>
              </div>

              <button
                type="submit"
                form="order-form"
                disabled={isSubmitting}
                className="w-full py-3.5 px-4 rounded-xl bg-gradient-to-r from-emerald-600 to-emerald-500 hover:from-emerald-500 hover:to-emerald-400 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-emerald-600/20 transition-all duration-150 ease-premium motion-press"
              >
                <MessageCircle className="w-4 h-4" />
                <span>{isSubmitting ? 'Validation...' : 'Valider la commande sur WhatsApp'}</span>
              </button>

              <div className="flex items-center justify-center gap-2 text-[10px] text-zinc-400 pt-1">
                <ShieldCheck className="w-3.5 h-3.5 text-gold-400" />
                <span>Paiement à la livraison ou Wave / Orange Money</span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
