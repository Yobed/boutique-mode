import type { Metadata } from 'next';
import { notFound } from 'next/navigation';
import ProductDetail from '@/components/product/ProductDetail';
import { getArticleById, getArticles } from '@/lib/supabase';

type Params = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Params): Promise<Metadata> {
  const { id } = await params;
  const article = await getArticleById(id);
  if (!article) return { title: 'Pièce introuvable' };
  return {
    title: article.nom,
    description: article.description.slice(0, 155),
    openGraph: { images: article.photos.slice(0, 1) },
  };
}

export default async function ArticlePage({ params }: Params) {
  const { id } = await params;
  const [article, all] = await Promise.all([getArticleById(id), getArticles()]);
  if (!article) notFound();

  const sameCategory = all.filter((a) => a.id !== id && a.categorie === article.categorie);
  const others = all.filter((a) => a.id !== id && a.categorie !== article.categorie && a.en_stock);
  const related = [...sameCategory, ...others].slice(0, 4);

  return <ProductDetail article={article} related={related} />;
}
