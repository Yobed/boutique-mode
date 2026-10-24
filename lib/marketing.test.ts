import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deliveryLabel } from './marketing.ts';

test('delivery label rolls over to the next month', () => {
  assert.match(deliveryLabel(new Date(2026, 9, 31, 22, 0)), /dimanche 1 novembre/);
});

test('delivery label is tomorrow on an ordinary day', () => {
  assert.match(deliveryLabel(new Date(2026, 9, 24, 9, 0)), /dimanche 25 octobre/);
});
