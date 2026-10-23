import React from 'react';
import Link from 'next/link';
import { MessageCircle, Phone, MapPin, ShieldCheck, Heart } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-dark-950 border-t border-white/10 text-zinc-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="space-y-3 md:col-span-1">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-gold-500 to-gold-300 flex items-center justify-center text-dark-950 font-serif font-black text-sm">
                B
              </div>
              <span className="font-serif text-lg font-bold text-white tracking-wide">
                BOUTIQUE <span className="text-gold-400">EN LIGNE</span>
              </span>
            </div>
            <p className="text-zinc-400 leading-relaxed text-xs">
              Votre référence mode & prêt-à-porter de luxe accessible. Des créations modernes et raffinées pour toutes vos occasions.
            </p>
            <div className="flex items-center gap-2 text-zinc-300 pt-1">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>100% Garanti & Paiement Sécurisé</span>
            </div>
          </div>

          {/* Quick Links */}
          <div className="space-y-2.5">
            <h4 className="font-serif font-bold text-sm text-white uppercase tracking-wider">
              Collections
            </h4>
            <ul className="space-y-1.5">
              <li><Link href="/catalogue?genre=femme" className="hover:text-gold-400 transition-colors">Robes & Ensembles Femme</Link></li>
              <li><Link href="/catalogue?genre=homme" className="hover:text-gold-400 transition-colors">Costumes & Chemises Homme</Link></li>
              <li><Link href="/catalogue?categorie=chemises" className="hover:text-gold-400 transition-colors">Créations Lin & Wax Chic</Link></li>
              <li><Link href="/catalogue?categorie=chaussures" className="hover:text-gold-400 transition-colors">Escarpins & Mocassins</Link></li>
              <li><Link href="/catalogue?promo=true" className="text-amber-400 hover:text-amber-300 transition-colors">Ventes Privées & Promos</Link></li>
            </ul>
          </div>

          {/* Zones de Livraison */}
          <div className="space-y-2.5">
            <h4 className="font-serif font-bold text-sm text-white uppercase tracking-wider">
              Livraison Express 24h
            </h4>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Expédition quotidienne partout à Abidjan : Cocody, Marcory, Plateau, Yopougon, Treichville, Port-Bouët, Bingerville.
            </p>
            <p className="text-xs text-zinc-400 leading-relaxed pt-1">
              Expéditions vers l'intérieur du pays via compagnies partenaires (Yamoussoukro, Bouaké, San-Pédro, Korhogo).
            </p>
          </div>

          {/* Contact & Support */}
          <div className="space-y-2.5">
            <h4 className="font-serif font-bold text-sm text-white uppercase tracking-wider">
              Contact & Commandes
            </h4>
            <div className="space-y-2">
              <a
                href="https://wa.me/2250778311541"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-emerald-400 hover:text-emerald-300 font-semibold"
              >
                <MessageCircle className="w-4 h-4" />
                <span>+225 07 78 31 15 41 (WhatsApp)</span>
              </a>
              <div className="flex items-center gap-2 text-zinc-400">
                <Phone className="w-4 h-4 text-gold-400" />
                <span>Service Client 7j/7 : 08h - 22h</span>
              </div>
              <div className="flex items-center gap-2 text-zinc-400">
                <MapPin className="w-4 h-4 text-gold-400" />
                <span>Abidjan, Côte d'Ivoire</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="mt-10 pt-6 border-t border-white/5 flex flex-col sm:flex-row items-center justify-between gap-4 text-center sm:text-left">
          <p>© {new Date().getFullYear()} Boutique en Ligne. Tous droits réservés.</p>
          <p className="flex items-center justify-center gap-1 text-zinc-500">
            Fait avec <Heart className="w-3.5 h-3.5 text-red-500 fill-red-500" /> • Propulsé par Next.js & IA Styliste
          </p>
        </div>
      </div>
    </footer>
  );
}
