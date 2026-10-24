// Run: npm test  (node --test with native TypeScript type stripping)
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addItem, setQuantity, removeItem, subtotal, deliveryFee, parseStoredCart, countItems } from './cart.ts';
import type { Article } from './types';

const robe: Article = {
  id: 'a1', nom: 'Robe', description: '', prix: 40000, prix_promo: 30000,
  categorie: 'robes', genre: 'femme', tailles: ['M'], couleurs: ['Noir'], photos: [],
  en_stock: true, quantite_stock: 3,
};

test('addItem merges identical lines without mutating input', () => {
  const one = addItem([], robe, 'M', 'Noir');
  const two = addItem(one, robe, 'M', 'Noir');
  assert.equal(one[0].quantite, 1);
  assert.equal(two[0].quantite, 2);
  assert.equal(two.length, 1);
});

test('addItem caps quantity at stock and refuses out-of-stock articles', () => {
  let items = addItem([], robe, 'M', 'Noir');
  for (let i = 0; i < 10; i++) items = addItem(items, robe, 'M', 'Noir');
  assert.equal(items[0].quantite, 3);
  assert.deepEqual(addItem([], { ...robe, en_stock: false }, 'M', 'Noir'), []);
});

test('setQuantity / removeItem / totals', () => {
  const items = addItem(addItem([], robe, 'M', 'Noir'), robe, 'L', 'Noir');
  assert.equal(countItems(items), 2);
  assert.equal(subtotal(items), 60000);
  assert.equal(setQuantity(items, 0, 0).length, 1);
  assert.equal(removeItem(items, 1).length, 1);
  assert.equal(items.length, 2);
});

test('deliveryFee: Abidjan, intérieur, free threshold, empty cart', () => {
  const items = addItem([], robe, 'M', 'Noir');
  assert.equal(deliveryFee(items, 'Cocody'), 1500);
  assert.equal(deliveryFee(items, 'Intérieur du pays'), 2500);
  assert.equal(deliveryFee([], 'Cocody'), 0);
  assert.equal(deliveryFee([{ ...items[0], quantite: 4 }], 'Cocody'), 0);
});

test('parseStoredCart rejects malformed data', () => {
  assert.deepEqual(parseStoredCart('not json'), []);
  assert.deepEqual(parseStoredCart('{"a":1}'), []);
  assert.deepEqual(parseStoredCart('[{"quantite":-1}]'), []);
  assert.equal(parseStoredCart(JSON.stringify(addItem([], robe, 'M', 'Noir'))).length, 1);
});
