import type { Metadata } from 'next';
import Showroom3DClient from './Showroom3DClient';

export const metadata: Metadata = {
  title: 'Chaussure Derby Homme · Vue 3D 360° · Maison ELSI',
  description:
    'Explorez une maquette 3D interactive d’une chaussure Derby pour homme, réalisée à partir de la planche de référence fournie.',
  openGraph: {
    title: 'Chaussure Derby Homme · Maison ELSI',
    description: 'Maquette 3D interactive d’une Derby cognac à lacets.',
    images: ['/models/chaussure-homme-cognac-poster.png'],
  },
};

export default function Showroom3DPage() {
  return <Showroom3DClient />;
}
