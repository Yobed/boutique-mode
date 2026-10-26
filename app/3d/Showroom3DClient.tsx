'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Check, MessageCircle, Sparkles, ExternalLink } from 'lucide-react';
import Product3DViewer from '@/components/3d/Product3DViewer';
import { formatFCFA } from '@/lib/config';

const WHATSAPP_PHONE = '2250574243752';

interface ShowroomItem {
  id: string;
  badge: string;
  nom: string;
  subtitle: string;
  prix?: number;
  description: string;
  modelSrc: string;
  posterSrc: string;
  cameraOrbit?: string;
  background?: string;
  specs: { label: string; value: string }[];
  articleHref?: string;
}

const SHOWROOM_ITEMS: ShowroomItem[] = [
  {
    id: 'art-102',
    badge: 'Maroquinerie · V2.2 Certifiée',
    nom: 'Sac Messager Structuré Havane',
    subtitle: 'Restauration V2.2 : anse unique continue, galbe maroquinier',
    prix: 78000,
    description: 'Sac messager structuré couleur havane en cuir pleine fleur, doté d’une anse supérieure galbée continue et d’un rabat frontal avec attaches maroquinières précises.',
    modelSrc: '/models/art-102.glb',
    posterSrc: '/models/art-102-poster.png',
    cameraOrbit: '0deg 75deg 105%',
    background: '#12141a',
    articleHref: '/article/art-102',
    specs: [
      { label: 'Type', value: 'Sac messager à rabat' },
      { label: 'Matière', value: 'Cuir pleine fleur havane' },
      { label: 'Construction', value: 'Anse unique continue, galbe souple' },
      { label: 'Format AR 1:1', value: '28 cm de hauteur (sol Z_min=0)' },
    ],
  },
  {
    id: 'art-103',
    badge: 'Maroquinerie · V2.2 Certifiée',
    nom: 'Sac Trapèze Croco Jaune Kita',
    subtitle: 'Restauration V2.2 : arêtes biseautées, passepoil maroquinier',
    prix: 54000,
    description: 'Sac trapèze en cuir embossé façon croco couleur jaune kita. Coutures adoucies par un biseau régulier sans effet boîte à 90°, anse aérienne et fermoir tourniquet doré.',
    modelSrc: '/models/art-103.glb',
    posterSrc: '/models/art-103-poster.png',
    cameraOrbit: '0deg 75deg 105%',
    background: '#14161a',
    articleHref: '/article/art-103',
    specs: [
      { label: 'Type', value: 'Sac trapèze à main & bandoulière' },
      { label: 'Matière', value: 'Cuir embossé crocodile' },
      { label: 'Finition', value: 'Passepoil arrondi, bouclerie dorée' },
      { label: 'Format AR 1:1', value: '28 cm de hauteur' },
    ],
  },
  {
    id: 'art-104',
    badge: 'Maroquinerie · V2.2 Certifiée',
    nom: 'Vanity Rond Cuir Chocolat',
    subtitle: 'Restauration V2.2 : cylindre de révolution & anse ajourée',
    prix: 38000,
    description: 'Véritable vanity cylindrique de révolution en cuir chocolat avec fermeture circulaire zippée et anse supérieure cintrée munie d’un passage de main traversant.',
    modelSrc: '/models/art-104.glb',
    posterSrc: '/models/art-104-poster.png',
    cameraOrbit: '0deg 75deg 105%',
    background: '#131418',
    articleHref: '/article/art-104',
    specs: [
      { label: 'Type', value: 'Vanity case cylindrique de voyage' },
      { label: 'Matière', value: 'Cuir lisse chocolat' },
      { label: 'Topologie', value: 'Cylindre de révolution, anse ajourée (Genus 1)' },
      { label: 'Format AR 1:1', value: '20 cm de hauteur, D=12.1 cm' },
    ],
  },
  {
    id: 'art-101',
    badge: 'Maroquinerie · V2.2 Certifiée',
    nom: 'Sac Cabas Cuir Cognac',
    subtitle: 'Restauration V2.2 : double anse distincte, 0 oreille sur les flancs',
    prix: 85000,
    description: 'Grand cabas en cuir pleine fleur cognac à surpiqûres sellier. Silhouette naturelle avec flancs sans fausses poignées et double anse indépendante fixée par boucles métalliques.',
    modelSrc: '/models/art-101.glb',
    posterSrc: '/models/art-101-poster.png',
    cameraOrbit: '0deg 75deg 105%',
    background: '#15171e',
    articleHref: '/article/art-101',
    specs: [
      { label: 'Type', value: 'Cabas cabine & journée' },
      { label: 'Matière', value: 'Cuir tanné végétal cognac' },
      { label: 'Anses', value: 'Double anse distincte ajourée (Genus 2)' },
      { label: 'Format AR 1:1', value: '35 cm de hauteur (sol Z_min=0)' },
    ],
  },
  {
    id: 'art-105',
    badge: 'Maroquinerie · V2.2 Certifiée',
    nom: 'Sac Bourse Plissé Ivoire',
    subtitle: 'Certification V2.2 : godets plissés naturels & anse ajourée',
    prix: 45000,
    description: 'Sac bourse du soir en cuir nappa ivoire souple, assemblé en godets plissés main avec anse rigide arrondie et assise horizontale stable.',
    modelSrc: '/models/art-105.glb',
    posterSrc: '/models/art-105-poster.png',
    cameraOrbit: '0deg 75deg 105%',
    background: '#121419',
    articleHref: '/article/art-105',
    specs: [
      { label: 'Type', value: 'Sac bourse du soir' },
      { label: 'Matière', value: 'Cuir nappa ivoire plissé' },
      { label: 'Anse', value: 'Anse cintrée ajourée (Genus 1)' },
      { label: 'Format AR 1:1', value: '25 cm de hauteur' },
    ],
  },
  {
    id: 'chaussure',
    badge: 'Chaussures homme · R&D',
    nom: 'Derby Homme Cognac',
    subtitle: 'Maquette interactive 3D d’après planche de référence',
    description: 'Paire de chaussures Derby pour homme en cuir marron cognac, à 5 œillets et semelle noire travaillée en relief.',
    modelSrc: '/models/chaussure-homme-cognac.glb',
    posterSrc: '/models/chaussure-homme-cognac-poster.png',
    cameraOrbit: '20deg 72deg 125%',
    background: '#d6d0c8',
    specs: [
      { label: 'Type', value: 'Derby à lacets' },
      { label: 'Matière', value: 'Cuir marron cognac' },
      { label: 'Semelle', value: 'Noire à relief structuré' },
      { label: 'Origine', value: 'Planche de référence' },
    ],
  },
];

export default function Showroom3DClient() {
  const [selectedId, setSelectedId] = useState<string>('art-102');
  const activeItem = SHOWROOM_ITEMS.find((it) => it.id === selectedId) ?? SHOWROOM_ITEMS[0];

  const whatsappMessage = encodeURIComponent(
    `Bonjour Maison ELSI, j'ai exploré le modèle 3D du « ${activeItem.nom} » sur le showroom. Est-il disponible pour une commande ?`
  );
  const whatsappUrl = `https://wa.me/${WHATSAPP_PHONE}?text=${whatsappMessage}`;

  return (
    <main className="min-h-screen bg-ink-950 pb-20 pt-6 text-linen-100">
      <div className="mx-auto max-w-[1440px] px-[var(--gutter)]">
        {/* Navigation Bar */}
        <nav className="mb-6 flex items-center justify-between gap-4 border-b border-white/10 pb-4 text-xs text-zinc-400">
          <Link href="/" className="group flex items-center gap-2 transition-colors hover:text-brass-300">
            <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
            <span>Retour à l’accueil</span>
          </Link>
          <span className="flex items-center gap-2 text-[10px] uppercase tracking-[0.18em] text-brass-300">
            <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            Showroom 3D V2.2 Interactif
          </span>
        </nav>

        {/* Product Picker Pills */}
        <div className="mb-8 flex items-center gap-2 overflow-x-auto pb-2 [scrollbar-width:none]">
          {SHOWROOM_ITEMS.map((item) => {
            const isSelected = item.id === selectedId;
            return (
              <button
                key={item.id}
                type="button"
                onClick={() => setSelectedId(item.id)}
                className={`flex shrink-0 items-center gap-2 rounded-full px-4 py-2 text-xs font-medium transition-all ${
                  isSelected
                    ? 'bg-brass-400 text-ink-950 font-semibold shadow-lg shadow-brass-400/20'
                    : 'border border-white/10 bg-ink-900/60 text-zinc-300 hover:border-brass-400/40 hover:text-white'
                }`}
              >
                <Sparkles className={`h-3 w-3 ${isSelected ? 'text-ink-950' : 'text-brass-400'}`} />
                <span>{item.nom}</span>
              </button>
            );
          })}
        </div>

        {/* Main 3D Viewer & Info Grid */}
        <div className="grid items-start gap-8 lg:grid-cols-12 lg:gap-12">
          {/* 3D Viewer Stage */}
          <section className="space-y-4 lg:col-span-7" aria-label="Visualiseur 3D interactif">
            <div className="relative overflow-hidden rounded-3xl border border-white/10 bg-ink-900/50 shadow-2xl">
              <Product3DViewer
                key={activeItem.modelSrc}
                modelSrc={activeItem.modelSrc}
                posterSrc={activeItem.posterSrc}
                alt={`Rendu 3D interactif de ${activeItem.nom}`}
                cameraOrbit={activeItem.cameraOrbit ?? '0deg 75deg 105%'}
                recolor={false}
                background={activeItem.background ?? '#0b0d11'}
                className="aspect-[4/3] w-full"
              />
            </div>

            <div className="grid grid-cols-3 rounded-2xl border border-white/10 bg-ink-900/60 p-4 text-center text-xs text-zinc-400">
              <div>
                <span className="mb-1 block font-serif text-brass-300">Vue 360°</span>
                <span>Glissez pour faire pivoter</span>
              </div>
              <div className="border-x border-white/10 px-2">
                <span className="mb-1 block font-serif text-brass-300">Zoom</span>
                <span>Pincez ou molette de souris</span>
              </div>
              <div>
                <span className="mb-1 block font-serif text-brass-300">Échelle 1:1</span>
                <span>Calage AR sol précis</span>
              </div>
            </div>
          </section>

          {/* Product Detail Sidebar */}
          <section className="space-y-7 lg:col-span-5 lg:sticky lg:top-24">
            <div>
              <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-brass-400/30 bg-brass-400/10 px-3 py-1 text-xs text-brass-300">
                <Sparkles className="h-3.5 w-3.5" />
                {activeItem.badge}
              </div>
              <h1 className="text-display text-3xl leading-tight tracking-tight sm:text-4xl">
                {activeItem.nom}
              </h1>
              <p className="mt-2 text-sm text-brass-300/90">{activeItem.subtitle}</p>
              {activeItem.prix && (
                <p className="mt-4 font-serif text-2xl text-linen-100">
                  {formatFCFA(activeItem.prix)}
                </p>
              )}
              <p className="mt-4 text-sm leading-relaxed text-zinc-300">
                {activeItem.description}
              </p>
            </div>

            {/* Action buttons */}
            <div className="space-y-3">
              {activeItem.articleHref && (
                <Link
                  href={activeItem.articleHref}
                  className="flex w-full items-center justify-center gap-2 rounded-full bg-brass-400 px-6 py-3.5 text-sm font-semibold text-ink-950 transition-colors hover:bg-brass-300"
                >
                  <ExternalLink className="h-4 w-4" />
                  Voir la fiche produit complète & Commander
                </Link>
              )}
              <a
                href={whatsappUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex w-full items-center justify-center gap-3 rounded-full bg-[#25D366] px-6 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-[#20ba59]"
              >
                <MessageCircle className="h-5 w-5 fill-current" />
                Commander sur WhatsApp
              </a>
            </div>

            {/* Technical Specs */}
            <div className="space-y-3 border-t border-white/10 pt-5">
              <h2 className="text-xs uppercase tracking-[0.16em] text-brass-300">Spécifications du modèle 3D</h2>
              <dl className="grid grid-cols-[auto_1fr] gap-x-5 gap-y-2 text-sm">
                {activeItem.specs.map((s, idx) => (
                  <div key={idx} className="contents">
                    <dt className="text-zinc-500">{s.label}</dt>
                    <dd className="text-zinc-200">{s.value}</dd>
                  </div>
                ))}
              </dl>
            </div>
          </section>
        </div>
      </div>
    </main>
  );
}
