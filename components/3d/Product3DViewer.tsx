'use client';

import React, { useEffect, useRef, useState } from 'react';
import Script from 'next/script';
import { RotateCw, ZoomIn, ZoomOut, Maximize2, RefreshCw } from 'lucide-react';

interface Product3DViewerProps {
  modelSrc: string; // Ex: "/models/sac_cuir.glb"
  posterSrc?: string; // Ex: "/models/sac_cuir_poster.png"
  alt?: string;
  autoRotate?: boolean;
  className?: string;
  cameraOrbit?: string;
  selectedColor?: string;
}

export default function Product3DViewer({
  modelSrc,
  posterSrc,
  alt = "Visualisation 3D du produit",
  autoRotate = true,
  className = "",
  cameraOrbit = "45deg 75deg 105%",
  selectedColor,
}: Product3DViewerProps) {
  const viewerRef = useRef<any>(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [isRotating, setIsRotating] = useState(autoRotate);

  // Sync leather color when user chooses a variant (Noir / Bordeaux / Cognac)
  useEffect(() => {
    const viewer = viewerRef.current;
    if (!viewer) return;

    const applyColor = () => {
      setIsLoaded(true);
      if (!viewer.model?.materials) return;
      const mat = viewer.model.materials.find((m: any) => m.name === 'Cuir');
      if (mat && selectedColor) {
        const colorMap: Record<string, [number, number, number, number]> = {
          'Noir': [0.035, 0.035, 0.035, 1.0],
          'Bordeaux': [0.32, 0.04, 0.07, 1.0],
          'Cognac': [0.46, 0.22, 0.07, 1.0],
        };
        const c = colorMap[selectedColor] || colorMap['Noir'];
        if (mat.pbrMetallicRoughness) {
          mat.pbrMetallicRoughness.setBaseColorFactor(c);
        }
      }
    };

    viewer.addEventListener('load', applyColor);
    if (viewer.loaded) applyColor();

    return () => viewer.removeEventListener('load', applyColor);
  }, [selectedColor]);

  const resetCamera = () => {
    if (viewerRef.current) {
      viewerRef.current.cameraOrbit = cameraOrbit;
      viewerRef.current.fieldOfView = "auto";
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
      const currentFov = parseFloat(viewerRef.current.fieldOfView.replace('deg', '')) || 45;
      const step = 8;
      const newFov = direction === 'in' ? Math.max(15, currentFov - step) : Math.min(80, currentFov + step);
      viewerRef.current.fieldOfView = `${newFov}deg`;
    }
  };

  return (
    <div className={`relative w-full aspect-square bg-[#0e1117] rounded-2xl overflow-hidden border border-white/10 group ${className}`}>
      {/* Script Google Model Viewer autonome */}
      <Script
        src="/libs/model-viewer.min.js"
        type="module"
        strategy="lazyOnload"
      />

      {/* Web Component <model-viewer> */}
      {/* @ts-ignore */}
      <model-viewer
        ref={viewerRef}
        src={modelSrc}
        poster={posterSrc}
        alt={alt}
        auto-rotate={isRotating ? "" : undefined}
        camera-controls=""
        touch-action="pan-y"
        shadow-intensity="1.2"
        shadow-softness="0.8"
        exposure="1.0"
        camera-orbit={cameraOrbit}
        interaction-prompt="auto"
        onLoad={() => setIsLoaded(true)}
        style={{
          width: '100%',
          height: '100%',
          backgroundColor: '#0e1117',
          '--poster-color': 'transparent'
        } as any}
      >
        {/* Slot de chargement / poster */}
        <div slot="poster" className="w-full h-full flex flex-col items-center justify-center bg-[#0e1117] text-white/50">
          {posterSrc ? (
            <img src={posterSrc} alt={alt} className="w-full h-full object-contain" />
          ) : (
            <div className="flex flex-col items-center gap-2">
              <RefreshCw className="w-6 h-6 animate-spin text-amber-500/80" />
              <span className="text-xs tracking-widest uppercase text-white/40">Chargement 3D...</span>
            </div>
          )}
        </div>
      {/* @ts-ignore */}
      </model-viewer>

      {/* Badge 3D Interactif */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 px-3 py-1.5 rounded-full bg-black/60 backdrop-blur-md border border-white/10 text-white text-xs tracking-wider uppercase pointer-events-none">
        <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
        Vue 3D Interactive
      </div>

      {/* Barre d'actions rapides (flottante) */}
      <div className="absolute bottom-4 right-4 z-10 flex items-center gap-1.5 p-1.5 rounded-xl bg-black/70 backdrop-blur-md border border-white/10 text-white/80 opacity-90 transition-opacity group-hover:opacity-100">
        <button
          type="button"
          onClick={() => zoom('in')}
          title="Zoom avant"
          className="p-2 rounded-lg hover:bg-white/10 hover:text-white transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={() => zoom('out')}
          title="Zoom arrière"
          className="p-2 rounded-lg hover:bg-white/10 hover:text-white transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={toggleAutoRotate}
          title={isRotating ? "Pause rotation" : "Activer rotation"}
          className={`p-2 rounded-lg transition-colors ${isRotating ? "text-amber-400 bg-amber-400/10" : "hover:bg-white/10 hover:text-white"}`}
        >
          <RotateCw className="w-4 h-4" />
        </button>

        <button
          type="button"
          onClick={resetCamera}
          title="Réinitialiser l'angle"
          className="p-2 rounded-lg hover:bg-white/10 hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
}
