import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import { getArticleById } from '@/lib/supabase';
import Showroom3DClient from './Showroom3DClient';

export const metadata: Metadata = {
  title: 'Studio produit · Maison ELSI',
  description:
    'Consultez les photos et les informations du produit. Une vue 3D est affichée uniquement après validation de sa fidélité au produit physique.',
};

export default async function Showroom3DPage() {
  const article = await getArticleById('art-101');
  if (!article) notFound();
  return <Showroom3DClient article={article} />;
}
