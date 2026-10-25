// Run: npm test  (node --test with native TypeScript type stripping)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { attachGeneratedModel, isSheetPhoto, modelKey, type Models3dManifest } from './models3d.ts';
import type { Article } from './types';

const sac: Article = {
  id: 'ART-009', nom: 'Sac', description: '', prix: 1, categorie: 'sacs', genre: 'femme',
  tailles: ['Unique'], couleurs: ['Noir'], photos: [], en_stock: true, quantite_stock: 1,
};

const manifest: Models3dManifest = {
  'art-009': { src: '/models/art-009.glb', poster: '/models/art-009-poster.png', cameraOrbit: '0deg 75deg 105%', recolor: false, status: 'ok' },
  'art-010': { src: '/models/art-010.glb', status: 'review' },
};

test('modelKey matches the Python safe_id normalisation', () => {
  assert.equal(modelKey('ART 009'), 'art-009');
  assert.equal(modelKey('  sac_Cuir-Noir '), 'sac_cuir-noir');
  assert.equal(modelKey('--x--'), 'x');
});

test('recognises multi-view sheets so they are never used as thumbnails', () => {
  assert.equal(isSheetPhoto('/images/planches/art-102-planche.jpg'), true);
  assert.equal(isSheetPhoto('/images/planches/art-102-face.jpg'), false);
  assert.equal(isSheetPhoto('https://images.unsplash.com/photo-1?w=1200'), false);
});

test('attaches an approved generated model without recoloring', () => {
  const result = attachGeneratedModel(sac, manifest);
  assert.equal(result.modele_3d?.src, '/models/art-009.glb');
  assert.equal(result.modele_3d?.recolor, false);
  assert.equal(sac.modele_3d, undefined, 'input article is not mutated');
});

test('carries the viewer background for dark products', () => {
  const dark: Models3dManifest = { 'art-009': { src: '/models/x.glb', background: '#d9dce1', status: 'ok' } };
  assert.equal(attachGeneratedModel(sac, dark).modele_3d?.background, '#d9dce1');
  assert.equal(attachGeneratedModel(sac, manifest).modele_3d?.background, undefined);
});

test('ignores entries still under review', () => {
  assert.equal(attachGeneratedModel({ ...sac, id: 'art-010' }, manifest).modele_3d, undefined);
});

test('keeps a model defined on the article itself', () => {
  const own = { ...sac, modele_3d: { src: '/models/sac-elsi.glb' } };
  assert.equal(attachGeneratedModel(own, manifest).modele_3d?.src, '/models/sac-elsi.glb');
});

test('an override entry replaces the model defined on the article, a plain entry does not', () => {
  const own = { ...sac, modele_3d: { src: '/models/sac-elsi.glb' } };
  const replace: Models3dManifest = { 'art-009': { src: '/models/art-009.glb', override: true, status: 'ok' } };
  assert.equal(attachGeneratedModel(own, replace).modele_3d?.src, '/models/art-009.glb');
  const review: Models3dManifest = { 'art-009': { src: '/models/art-009.glb', override: true, status: 'review' } };
  assert.equal(attachGeneratedModel(own, review).modele_3d?.src, '/models/sac-elsi.glb');
});

test('articles without an entry are returned unchanged', () => {
  assert.equal(attachGeneratedModel({ ...sac, id: 'inconnu' }, manifest).modele_3d, undefined);
});
