import { getArticles } from '@/lib/supabase';
import type { Article } from '@/lib/types';
import SceneHero from '@/components/home/SceneHero';
import SceneProof from '@/components/home/SceneProof';
import SceneGenres from '@/components/home/SceneGenres';
import SceneUnivers from '@/components/home/SceneUnivers';
import SceneCollectionSavoir from '@/components/home/SceneCollectionSavoir';
import SceneSteps from '@/components/home/SceneSteps';
import SceneTestimonials from '@/components/home/SceneTestimonials';
import SceneFAQ from '@/components/home/SceneFAQ';
import { SHOW_CUSTOMER_PROOF } from '@/lib/marketing';
import SceneFinalCta from '@/components/home/SceneFinalCta';
import Marquee from '@/components/fx/Marquee';

export const revalidate = 300;

const PROMISES = [
  'Livraison 24 h à Abidjan',
  'Paiement sécurisé à la réception',
  'Échange de taille garanti 48 h',
  'Pièces repassées sous housse',
  'Wave, Orange Money, MTN MoMo',
  'Conseil style privé sur WhatsApp',
];

// Persuasion sequence: attention (gallery hero) → reassurance (ribbon) → proof (numbers) → easy choice (doors)
// → story & authority (univers, savoir-faire) → desire (collection) → zero risk (steps) → social proof → action.
export default async function HomePage() {
  const articles = await getArticles();
  const hero = articles.find((a) => a.id === 'art-101') ?? articles.find((a) => a.vedette && a.en_stock) ?? articles[0];
  const featured = articles.filter((a) => a.id !== hero?.id && a.en_stock && (a.vedette || a.nouveaute));
  const signature = (featured.length >= 4 ? featured : articles.filter((a) => a.id !== hero?.id)).slice(0, 8);

  return (
    <>
      {hero && <SceneHero article={hero} side={['art-201', 'art-301'].map((id) => articles.find((a) => a.id === id)).filter((a): a is Article => !!a)} />}
      <div className="border-y border-ink/10 bg-paper py-5 lg:py-7">
        <Marquee speed={50}>
          {PROMISES.map((p) => (
            <span key={p} className="text-display flex shrink-0 items-center whitespace-nowrap text-[clamp(1.5rem,1rem+1.8vw,2.8rem)] italic">
              <span className="px-8">{p}</span>
              <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-indigo" />
            </span>
          ))}
        </Marquee>
      </div>
      <SceneProof />
      <SceneGenres />
      <SceneUnivers />
      <SceneCollectionSavoir articles={signature} total={articles.length} />
      <SceneSteps />
      {SHOW_CUSTOMER_PROOF && <SceneTestimonials />}
      <SceneFAQ />
      <SceneFinalCta />
    </>
  );
}
