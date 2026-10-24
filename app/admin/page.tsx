'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { Package, TrendingUp, CheckCircle2, Clock, Truck, ShieldAlert, ArrowLeft, RefreshCw } from 'lucide-react';
import { Commande } from '@/lib/types';
import { supabase } from '@/lib/supabase';

export default function AdminDashboardPage() {
  const [commandes, setCommandes] = useState<Commande[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchCommandes = async () => {
    setLoading(true);
    if (!supabase) {
      // Mock orders for demo
      setCommandes([
        {
          id: '1',
          numero_commande: 'CMD-849201',
          client_nom: 'Mme Affi Marie',
          client_telephone: '07 55 44 33 22',
          client_adresse: 'Riviera 3 carrefour Jacques Prévert',
          commune_livraison: 'Cocody',
          articles_commande: [
            {
              article: {
                id: 'art-001',
                nom: 'Robe Soirée Émeraude Satinée',
                description: '',
                prix: 32000,
                categorie: 'robes',
                genre: 'femme',
                tailles: ['M'],
                couleurs: ['Vert Émeraude'],
                photos: ['https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=800'],
                en_stock: true,
                quantite_stock: 10,
              },
              taille: 'M',
              couleur: 'Vert Émeraude',
              quantite: 1,
            },
          ],
          montant_total: 33500,
          frais_livraison: 1500,
          statut: 'en_attente',
          canal_origine: 'whatsapp',
          created_at: new Date(Date.now() - 3600000).toISOString(),
        },
      ]);
      setLoading(false);
      return;
    }

    try {
      const { data } = await supabase
        .from('commandes')
        .select('*')
        .order('created_at', { ascending: false });

      if (data) setCommandes(data as Commande[]);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCommandes();
  }, []);

  const totalCA = commandes.reduce((sum, c) => sum + (c.montant_total || 0), 0);
  const totalEnAttente = commandes.filter((c) => c.statut === 'en_attente').length;

  return (
    <div className="min-h-screen bg-dark-950 text-ivory p-6 sm:p-10">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-ivory/10">
          <div>
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-xs text-zinc-400 hover:text-gold-400 transition-colors mb-2"
            >
              <ArrowLeft className="w-4 h-4" />
              <span>Voir la Boutique Client</span>
            </Link>
            <h1 className="font-serif text-3xl font-bold text-ivory flex items-center gap-3">
              <span>Tableau de Bord Gérant</span>
              <span className="text-xs px-2.5 py-1 rounded-full bg-gold-500/20 text-gold-400 border border-gold-500/30 font-sans font-bold">
                Admin 0 FCFA
              </span>
            </h1>
          </div>

          <button
            onClick={fetchCommandes}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-ivory/10 hover:bg-ivory/15 text-xs font-semibold text-zinc-200"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Actualiser</span>
          </button>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div className="p-5 rounded-2xl bg-dark-900 border border-ivory/10 space-y-2">
            <span className="text-xs text-zinc-400 uppercase tracking-wider font-semibold">Chiffre d'Affaires</span>
            <div className="text-2xl sm:text-3xl font-bold text-gold-400">
              {totalCA.toLocaleString('fr-FR')} FCFA
            </div>
          </div>
          <div className="p-5 rounded-2xl bg-dark-900 border border-ivory/10 space-y-2">
            <span className="text-xs text-zinc-400 uppercase tracking-wider font-semibold">Commandes Totales</span>
            <div className="text-2xl sm:text-3xl font-bold text-ivory">{commandes.length}</div>
          </div>
          <div className="p-5 rounded-2xl bg-dark-900 border border-ivory/10 space-y-2">
            <span className="text-xs text-zinc-400 uppercase tracking-wider font-semibold">En Attente de Livraison</span>
            <div className="text-2xl sm:text-3xl font-bold text-amber-400">{totalEnAttente}</div>
          </div>
        </div>

        {/* Commandes List */}
        <div className="space-y-4">
          <h2 className="font-serif text-xl font-bold text-ivory">Dernières Commandes Reçues</h2>

          {loading ? (
            <div className="text-zinc-500 text-sm py-8 text-center">Chargement des commandes...</div>
          ) : commandes.length === 0 ? (
            <div className="text-zinc-500 text-sm py-12 text-center bg-dark-900 rounded-2xl border border-ivory/5">
              Aucune commande pour le moment. Dès qu'un client valide son panier sur le site ou sur WhatsApp, elle apparaîtra ici !
            </div>
          ) : (
            <div className="overflow-x-auto bg-dark-900 border border-ivory/10 rounded-2xl">
              <table className="w-full text-left text-xs text-zinc-300">
                <thead className="bg-dark-950 text-zinc-400 uppercase text-[10px] tracking-wider border-b border-ivory/10">
                  <tr>
                    <th className="p-4">N° Commande</th>
                    <th className="p-4">Client</th>
                    <th className="p-4">Téléphone</th>
                    <th className="p-4">Commune</th>
                    <th className="p-4">Articles</th>
                    <th className="p-4">Total</th>
                    <th className="p-4">Canal</th>
                    <th className="p-4">Statut</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-ivory/5">
                  {commandes.map((cmd) => (
                    <tr key={cmd.numero_commande} className="hover:bg-ivory/5 transition-colors">
                      <td className="p-4 font-mono font-bold text-gold-400">{cmd.numero_commande}</td>
                      <td className="p-4 font-semibold text-ivory">{cmd.client_nom}</td>
                      <td className="p-4">
                        <a
                          href={`https://wa.me/225${cmd.client_telephone.replace(/\D/g, '')}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-emerald-400 hover:underline"
                        >
                          {cmd.client_telephone}
                        </a>
                      </td>
                      <td className="p-4">{cmd.commune_livraison}</td>
                      <td className="p-4">
                        {cmd.articles_commande?.map((item, idx) => (
                          <div key={idx} className="truncate max-w-xs">
                            • {item.article.nom} ({item.taille}) x{item.quantite}
                          </div>
                        ))}
                      </td>
                      <td className="p-4 font-bold text-ivory">{cmd.montant_total.toLocaleString('fr-FR')} FCFA</td>
                      <td className="p-4 uppercase text-[10px] font-bold">
                        <span className={`px-2 py-0.5 rounded ${cmd.canal_origine === 'whatsapp' ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/30' : 'bg-purple-950 text-purple-400 border border-purple-500/30'}`}>
                          {cmd.canal_origine}
                        </span>
                      </td>
                      <td className="p-4">
                        <span className="px-2 py-1 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold text-[10px] uppercase">
                          {cmd.statut.replace('_', ' ')}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
