import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { loadCatalog, validateShape, validateRelationships, checkSources } from '../tools/integrations/source-health.mjs';
const sourceID = 'source:nyc-zoning-resolution';
const response = (body, status = 200, headers = {}) => new Response(body, { status, headers: { 'content-type': 'text/html', ...headers } });
const check = async fetchImpl => (await checkSources([sourceID], { fetchImpl }))[0];

test('all maintained manifests validate; unknown editions remain null', async () => {
  const c = await loadCatalog(); assert.ok(c.sources.sources.length >= 41);
  assert.equal(c.sources.sources.find(s=>s.id==='source:nyc-pluto').edition, null);
  assert.equal(c.standards[0].rights, 'reference-metadata-only');
  assert.equal(c.integrations.integrations.find(i => i.id === 'integration:ec3').status, 'declaration-only');
});
test('schema rejects absent editions, embedded secrets, and invalid dates', async () => {
  const schema = JSON.parse(await readFile(new URL('../schema/source-catalog.schema.json', import.meta.url)));
  const c = (await loadCatalog()).sources;
  for (const mutate of [s => delete s.edition, s => s.effective_date = '2026-02-30', s => s.url = 'https://user:secret@example.com', s => s.url = 'https://example.com/?token=SECRET', s => s.extra_token = 'SECRET']) {
    const copy = structuredClone(c); mutate(copy.sources[0]); assert.throws(() => validateShape(copy, schema));
  }
});
test('relationships reject missing IDs, duplicate IDs and jurisdiction cycles', async () => {
  for (const mutate of [c => c.sources.sources[0].authority = 'authority:absent', c => c.sources.sources.push(c.sources.sources[0]), c => c.jurisdictions.jurisdictions[0].parent = 'jurisdiction:us-ny-nyc', c => c.sources.relationships[0].to = 'standard:absent']) {
    const c = await loadCatalog(); mutate(c); assert.throws(() => validateRelationships(c));
  }
});
test('shared standards referenced from two jurisdictions need no duplication', async () => {
  const c = await loadCatalog();
  c.jurisdictions.jurisdictions.push({ id: 'jurisdiction:fixture', name: 'Test fixture', parent: 'jurisdiction:us', coverage: 'routing-only' });
  for (const from of ['jurisdiction:fixture', 'jurisdiction:us-ny-nyc']) c.sources.relationships.push({ from, type: 'references', to: 'standard:astm-e84', edition: null, effective_date: null, evidence: 'fixture-only' });
  validateRelationships(c); assert.equal(c.standards.filter(s=>s.id==='standard:astm-e84').length, 1);
});
test('a matched response never claims applicable law or freshness', async () => {
  const result = await check(async (_url, options) => {
    assert.equal(options.redirect, 'manual'); assert.equal(options.credentials, 'omit');
    assert.deepEqual(Object.keys(options.headers), ['Accept']);
    return response('<title>Zoning Resolution</title>');
  });
  assert.equal(result.identity, 'matched-markers'); assert.equal(result.legal_applicability, 'unknown'); assert.equal(result.freshness, 'unknown'); assert.match(result.content_sha256, /^[a-f0-9]{64}$/);
});
test('redirects including private endpoints and secrets are not followed or returned', async () => {
  let calls = 0;
  const result = await check(async () => { calls++; return response('', 302, { location: 'http://127.0.0.1/?secret=SECRET' }); });
  assert.equal(calls, 1); assert.equal(result.reason, 'redirect-unverified'); assert.equal(result.identity, 'unknown'); assert.ok(!JSON.stringify(result).includes('SECRET'));
});
test('200 login page, replaced text, wrong media type, large body, denial and outage stay distinct', async () => {
  for (const [make, reason] of [
    [() => response('<title>Login</title>Zoning Resolution'), 'login-page'],
    [() => response('<input type="password">Zoning Resolution'), 'login-page'],
    [() => response('unrelated publication'), 'expected-markers-missing'],
    [() => response('Zoning Resolution', 200, { 'content-type': 'application/octet-stream' }), 'unexpected-content-type'],
    [() => response('x'.repeat(1048577)), 'body-limit'],
    [() => response('', 403), 'access-required'],
    [() => response('', 503), 'http-error'],
  ]) assert.equal((await check(async () => make())).reason, reason);
});
test('timeout aborts a pending response; transport error details never leak', async () => {
  const result = (await checkSources([sourceID], { timeoutMs: 20, fetchImpl: (_url, { signal }) => new Promise((_resolve, reject) => signal.addEventListener('abort', () => reject(new Error('SECRET')))) }))[0];
  assert.equal(result.reason, 'timeout');
  const failure = await check(async () => { throw new Error('SECRET credentials'); });
  assert.equal(failure.reason, 'transport-error'); assert.ok(!JSON.stringify(failure).includes('SECRET'));
});
test('concurrent checks are bounded; isolated failure does not discard successful sibling', async () => {
  let active = 0; let max = 0; let calls = 0;
  const results = await checkSources([sourceID, sourceID, sourceID, sourceID], { concurrency: 2, fetchImpl: async () => {
    const i = calls++; active++; max = Math.max(max, active);
    await new Promise(resolve => setTimeout(resolve, 5)); active--;
    if (i === 1) throw new Error('isolated failure'); return response('Zoning Resolution');
  }});
  assert.equal(max, 2); assert.equal(results.filter(r => r.identity === 'matched-markers').length, 3);
  assert.equal(results[1].reason, 'transport-error');
});
test('unknown IDs, arbitrary URLs, and invalid limits fail before network', async () => {
  let calls = 0; const fetchImpl = async () => { calls++; return response(''); };
  for (const ids of [['source:missing'], ['http://127.0.0.1'], new Array(101).fill(sourceID)]) await assert.rejects(checkSources(ids, { fetchImpl }));
  await assert.rejects(checkSources([sourceID], { concurrency: 9, fetchImpl }));
  await assert.rejects(checkSources([sourceID], { timeoutMs: 30001, fetchImpl }));
  assert.equal(calls, 0);
});
test('early responses cancel bodies without waiting on an uncooperative cancel handler', async () => {
  let cancelled = false;
  const result = await check(async () => new Response(new ReadableStream({ cancel() { cancelled = true; return new Promise(() => {}); } }), { status: 503 }));
  assert.equal(result.reason, 'http-error'); assert.equal(cancelled, true);
});
test('timeout remains active while a successful response body stalls', async () => {
  const result = (await checkSources([sourceID], { timeoutMs: 20, fetchImpl: async (_url, { signal }) => new Response(new ReadableStream({
    start(controller) { signal.addEventListener('abort', () => controller.error(new Error('SECRET'))); },
  }), { headers: { 'content-type': 'text/html' } }) }))[0];
  assert.equal(result.reason, 'timeout'); assert.equal(result.identity, 'unknown');
  assert.ok(!JSON.stringify(result).includes('SECRET'));
});
