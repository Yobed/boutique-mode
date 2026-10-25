'use client';

import React, { useEffect, useRef, useState } from 'react';
import Script from 'next/script';
import { RotateCw, ZoomIn, ZoomOut, RefreshCw, Sparkles, Check } from 'lucide-react';

interface Product3DViewerProps {
  modelSrc: string; // Ex: "/models/sac-elsi.glb"
  posterSrc?: string; // Ex: "/models/sac-elsi-poster.png"
  alt?: string;
  autoRotate?: boolean;
  className?: string;
  cameraOrbit?: string;
  selectedColor?: string;
  onColorChange?: (color: string) => void;
  showColorPicker?: boolean;
  /** Teintes à afficher. Par défaut, garde la palette historique à trois teintes. */
  colorOptions?: string[];
  /** false : modèle déjà coloré d'après la photo, ni recoloration du matériau ni sélecteur de teintes. */
  recolor?: boolean;
  /** Fond CSS du visualiseur (défaut sombre). */
  background?: string;
}

const DEFAULT_BACKGROUND = '#0b0d11';

const COLOR_MAP: Record<string, { label: string; bg: string; factor: [number, number, number, number] }> = {
  noir: {
    label: 'Noir',
    bg: '#18181b',
    factor: [0.009, 0.009, 0.012, 1.0],
  },
  bordeaux: {
    label: 'Bordeaux',
    bg: '#581c24',
    factor: [0.098, 0.012, 0.018, 1.0],
  },
  cognac: {
    label: 'Cognac',
    bg: '#8b4513',
    factor: [0.258, 0.061, 0.006, 1.0],
  },
  marron: {
    label: 'Marron',
    bg: '#774126',
    factor: [0.184, 0.055, 0.021, 1.0],
  },
  'bleu-marine': {
    label: 'Bleu marine',
    bg: '#23364e',
    factor: [0.016, 0.038, 0.078, 1.0],
  },
  camel: {
    label: 'Camel',
    bg: '#b87a43',
    factor: [0.479, 0.195, 0.058, 1.0],
  },
  gris: {
    label: 'Gris',
    bg: '#77736d',
    factor: [0.184, 0.168, 0.15, 1.0],
  },
};

export default function Product3DViewer({
  modelSrc,
  posterSrc,
  alt = 'Visualisation 3D interactive du produit',
  autoRotate = true,
  className = '',
  cameraOrbit = '0deg 75deg 105%',
  selectedColor = 'Noir',
  onColorChange,
  showColorPicker = true,
  colorOptions,
  recolor = true,
  background = DEFAULT_BACKGROUND,
}: Product3DViewerProps) {
  const viewerRef = useRef<any>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isRotating, setIsRotating] = useState(autoRotate);
  const [currentColor, setCurrentColor] = useState(selectedColor);

  // Sync external prop selectedColor
  useEffect(() => {
    if (selectedColor && selectedColor !== currentColor) {
      setCurrentColor(selectedColor);
    }
  }, [selectedColor]);

  // Ensure <model-viewer> is registered even if Next Script is delayed
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.customElements?.get('model-viewer')) {
      const script = document.createElement('script');
      script.type = 'module';
      script.src = 'https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js';
      script.onerror = () => {
        const fallback = document.createElement('script');
        fallback.type = 'module';
        fallback.src = '/libs/model-viewer.min.js';
        document.head.appendChild(fallback);
      };
      document.head.appendChild(script);
    }
  }, []);

  // Sync leather color when user chooses a variant (Noir / Bordeaux / Cognac)
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer) return;

    const applyColor = () => {
      setIsLoaded(true);
      if (!recolor || !viewer.model?.materials) return;

      const materials = viewer.model.materials.filter((material: any) => {
        const name = material.name?.toLowerCase() || '';
        return name.includes('cuir') || name.includes('leather');
      });
      const targets = materials.length ? materials : viewer.model.materials.slice(0, 1);
      const norm = (currentColor || '').toLowerCase().trim().replace(/\s+/g, '-');
      const found = COLOR_MAP[norm] || COLOR_MAP.noir;

      for (const material of targets) {
        material.pbrMetallicRoughness?.setBaseColorFactor(found.factor);
      }
    };

    viewer.addEventListener('load', applyColor);
    if (viewer.loaded) applyColor();

    return () => viewer.removeEventListener('load', applyColor);
  }, [currentColor, recolor]);

  const handleSelectColor = (colorKey: string) => {
    const label = COLOR_MAP[colorKey]?.label || colorKey;
    setCurrentColor(label);
    if (onColorChange) onColorChange(label);
  };

  const visibleColorKeys = colorOptions ?? ['noir', 'bordeaux', 'cognac'];

  const resetCamera = () => {
    if (viewerRef.current) {
      viewerRef.current.cameraOrbit = cameraOrbit;
      viewerRef.current.fieldOfView = 'auto';
    }
  };

  const toggleAutoRotate = () => {
    if (viewerRef.current) {
      viewerRef.current.autoRotate = !isRotating;
      setIsRotating(!isRotating);
    }
  };

  const zoom = (direction: 'in' | 'out') => {
    if (viewerRef.current) {
      const currentFov =
        parseFloat(viewerRef.current.fieldOfView?.replace('deg', '') || '') || 45;
      const step = 8;
      const newFov =
        direction === 'in'
          ? Math.max(15, currentFov - step)
          : Math.min(80, currentFov + step);
      viewerRef.current.fieldOfView = `${newFov}deg`;
    }
  };

  return (
    <div
      className={`relative w-full aspect-square rounded-2xl overflow-hidden border border-brass-400/20 shadow-2xl group select-none ${className}`}
      style={{ backgroundColor: background }}
    >
      {/* Script Google Model Viewer autonome */}
      <Script
        src="https://ajax.googleapis.com/ajax/libs/model-viewer/4.0.0/model-viewer.min.js"
        type="module"
        strategy="afterInteractive"
      />

      {/* Web Component <model-viewer> */}
      {/* @ts-ignore */}
      <model-viewer
        ref={viewerRef}
        src={modelSrc}
        poster={posterSrc}
        alt={alt}
        auto-rotate={isRotating ? '' : undefined}
        camera-controls=""
        touch-action="pan-y"
        shadow-intensity="1.4"
        shadow-softness="0.8"
        exposure="1.0"
        environment-image="neutral"
        tone-mapping="neutral"
        camera-orbit={cameraOrbit}
        interaction-prompt="auto"
        onLoad={() => setIsLoaded(true)}
        style={
          {
            width: '100%',
            height: '100%',
            backgroundColor: background,
            '--poster-color': 'transparent',
          } as any
        }
      >
        {/* Slot de chargement / poster */}
        <div
          slot="poster"
          className="w-full h-full flex flex-col items-center justify-center text-linen-100"
          style={{ backgroundColor: background }}
        >
          {posterSrc ? (
            <img
              src={posterSrc}
              alt={alt}
              className="w-full h-full object-contain filter drop-shadow-2xl"
            />
          ) : (
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="w-8 h-8 animate-spin text-brass-400" />
              <span className="text-xs font-serif tracking-widest uppercase text-brass-300">
                Chargement de la pièce 3D...
              </span>
            </div>
          )}
        </div>
        {/* @ts-ignore */}
      </model-viewer>

      {/* Badge 3D Interactif Luxueux */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-ink-950/85 backdrop-blur-md border border-brass-400/40 text-linen-100 text-[11px] font-serif tracking-wider uppercase shadow-xl pointer-events-none">
        <Sparkles className="w-3.5 h-3.5 text-brass-400 animate-pulse" />
        <span>Rendu 3D 360°</span>
      </div>

      {/* Sélecteur de Couleurs Flottant Direct sur le Viewer */}
      {showColorPicker && recolor && (
        <div className="absolute top-4 right-4 z-10 flex items-center gap-2 p-1.5 rounded-full bg-ink-950/85 backdrop-blur-md border border-brass-400/30 shadow-xl">
          {visibleColorKeys.map((key) => {
            const info = COLOR_MAP[key];
            if (!info) return null;
            const isSelected =
              currentColor.toLowerCase().trim().replace(/\s+/g, '-') === key;
            return (
              <button
                key={key}
                type="button"
                onClick={() => handleSelectColor(key)}
                title={`Teinte : ${info.label}`}
                className={`relative flex items-center justify-center w-7 h-7 rounded-full transition-all duration-300 ${
                  isSelected
                    ? 'ring-2 ring-brass-400 scale-110 shadow-lg'
                    : 'opacity-75 hover:opacity-100 hover:scale-105'
                }`}
                style={{ backgroundColor: info.bg }}
              >
                {isSelected && (
                  <Check className="w-3.5 h-3.5 text-brass-300 drop-shadow" />
                )}
              </button>
            );
          })}
        </div>
      )}

      {/* Guide tactile discret au bas */}
      <div className="absolute bottom-4 left-4 z-10 hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-ink-950/70 backdrop-blur-sm border border-white/5 text-[11px] text-zinc-400 pointer-events-none">
        <span>Glissez pour faire pivoter à 360° · Pincez pour zoomer</span>
      </div>

      {/* Barre d'actions rapides (flottante) */}
      <div className="absolute bottom-4 right-4 z-10 flex items-center gap-1.5 p-1.5 rounded-xl bg-ink-950/85 backdrop-blur-md border border-brass-400/30 text-linen-100 shadow-xl opacity-90 transition-opacity group-hover:opacity-100">
        <button
          type="button"
          onClick={() => zoom('in')}
          title="Zoom avant"
          className="p-2 rounded-lg hover:bg-brass-400/20 hover:text-brass-300 transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={() => zoom('out')}
          title="Zoom arrière"
          className="p-2 rounded-lg hover:bg-brass-400/20 hover:text-brass-300 transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={toggleAutoRotate}
          title={isRotating ? 'Mettre en pause' : 'Rotation automatique'}
          className={`p-2 rounded-lg transition-colors ${
            isRotating
              ? 'text-brass-400 bg-brass-400/20'
              : 'hover:bg-brass-400/20 hover:text-brass-300'
          }`}
        >
          <RotateCw className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={resetCamera}
          title="Réinitialiser l'angle de vue"
          className="p-2 rounded-lg hover:bg-brass-400/20 hover:text-brass-300 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
