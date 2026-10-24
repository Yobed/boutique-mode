import { test } from 'node:test';
import assert from 'node:assert/strict';
import { normalizePhoneCI, validateContact, validateDelivery, orderNumber } from './checkout.ts';

test('normalizePhoneCI accepts national and international Ivorian formats', () => {
  assert.equal(normalizePhoneCI('07 78 31 15 41'), '0778311541');
  assert.equal(normalizePhoneCI('+225 07 78 31 15 41'), '0778311541');
  assert.equal(normalizePhoneCI('00225-0578311541'), '0578311541');
  assert.equal(normalizePhoneCI('0912345678'), null);
  assert.equal(normalizePhoneCI('0778'), null);
  assert.equal(normalizePhoneCI(''), null);
});

test('validateContact flags missing name and bad phone', () => {
  assert.deepEqual(validateContact({ nom: 'Awa K.', telephone: '0700000000' }), {});
  const e = validateContact({ nom: ' ', telephone: '123' });
  assert.ok(e.nom && e.telephone);
});

test('validateDelivery requires a known commune and a landmark', () => {
  assert.deepEqual(validateDelivery({ commune: 'Cocody', adresse: 'Angré 8e tranche' }), {});
  const e = validateDelivery({ commune: 'Paris', adresse: '' });
  assert.ok(e.commune && e.adresse);
});

test('orderNumber is prefixed and stable for a given time', () => {
  assert.match(orderNumber(1_700_000_000_000), /^ELSI-[0-9A-Z]{6}$/);
  assert.equal(orderNumber(42_000_000_000), orderNumber(42_000_000_000));
});
