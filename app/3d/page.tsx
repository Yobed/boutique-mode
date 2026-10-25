import type { Metadata } from 'next';
import Showroom3DClient from './Showroom3DClient';

export const metadata: Metadata = {
  title: 'Studio 3D 360° · Sac à Main Signature · Maison ELSI',
  description:
    'Explorez le Sac à Main Signature ELSI en 3D interactive 360°. Testez les teintes de cuir en temps réel et commandez directement sur WhatsApp.',
  openGraph: {
    title: 'Studio 3D 360° · Maison ELSI',
    description:
      'Modèle 3D immersif : pivotez à 360°, zoomez sur les détails de maroquinerie et changez les teintes de cuir en direct.',
    images: ['/models/sac-elsi-poster.png'],
  },
};

export default function Showroom3DPage() {
  return <Showroom3DClient />;
}
