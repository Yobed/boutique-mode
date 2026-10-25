import type { Article } from './types';

/**
 * Modèles 3D générés par `npm run 3d:catalog` / `3d:product` (voir docs/3d-pipeline/NEURAL_IMAGE_TO_3D.md).
 * Le manifeste `config/models3d.json` est indexé par identifiant d'article normalisé.
 * Seules les entrées validées (status "ok") sont attachées au site ; "review" attend un contrôle visuel.
 */
export interface GeneratedModel {
  src: string;
  poster?: string;
  cameraOrbit?: string;
  recolor?: boolean;
  background?: string;
  override?: boolean;
  status: string;
}

export type Models3dManifest = Record<string, GeneratedModel>;

/** Les planches multi-vues (`*-planche.jpg`) sont larges : elles se lisent en pleine largeur, jamais en vignette. */
export const isSheetPhoto = (src: string): boolean => src.includes('-planche.');

/** Même normalisation que `safe_id` côté Python (scripts/3d_pipeline/image_to_3d.py). */
export function modelKey(id: string): string {
  return id.trim().toLowerCase().replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '');
}

/**
 * Un modèle 3D déjà défini sur l'article est prioritaire, sauf si l'entrée du manifeste porte `override`
 * (modèle généré depuis la planche fournie, qui remplace l'ancien) ; sinon on utilise celui généré depuis la photo.
 */
export function attachGeneratedModel(article: Article, manifest: Models3dManifest): Article {
  const entry = manifest[modelKey(article.id)];
  if (!entry || entry.status !== 'ok' || !entry.src) return article;
  if (article.modele_3d && !entry.override) return article;
  const { src, poster, cameraOrbit, recolor, background } = entry;
  return { ...article, modele_3d: { src, poster, cameraOrbit, recolor, background } };
}
