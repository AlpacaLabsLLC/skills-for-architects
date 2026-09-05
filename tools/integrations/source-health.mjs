#!/usr/bin/env node
/** Shared source checks. No side effects on import; no credentials or persistent cache. */
import { readFile, readdir, access } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { createHash } from 'node:crypto';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '../..');
const readJSON = async path => JSON.parse(await readFile(path, 'utf8'));
const fail = path => { throw new Error(`Invalid source contract at ${path}`); };

// Implements the bounded vocabulary used by the bundled schemas; not a general JSON Schema engine.
export function validateShape(value, schema, path = '$') {
  if ('const' in schema && value !== schema.const) fail(path);
  if (schema.enum && !schema.enum.includes(value)) fail(path);
  const type = value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;
  if (schema.type && ![].concat(schema.type).some(t => t === type || t === 'integer' && Number.isInteger(value))) fail(path);
  if (value === null) return;
  if (type === 'object') {
    for (const key of schema.required ?? []) if (!(key in value)) fail(`${path}.${key}`);
    for (const [key, child] of Object.entries(value)) {
      if (!(key in (schema.properties ?? {}))) { if (schema.additionalProperties === false) fail(path); }
      else validateShape(child, schema.properties[key], `${path}.${key}`);
    }
  }
  if (type === 'array') {
    if (value.length < (schema.minItems ?? 0)) fail(path);
    value.forEach((v, i) => validateShape(v, schema.items ?? {}, `${path}[${i}]`));
  }
  if (type === 'number' && (!Number.isFinite(value) || value < (schema.minimum ?? -Infinity) || value > (schema.maximum ?? Infinity))) fail(path);
  if (type === 'string') {
    if (value.length < (schema.minLength ?? 0) || schema.pattern && !new RegExp(schema.pattern).test(value)) fail(path);
    if (schema.format === 'date' && (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0, 10) !== value)) fail(path);
    if (schema.format === 'date-time' && (!/^\d{4}-\d{2}-\d{2}T.*Z$/.test(value) || !Number.isFinite(Date.parse(value)))) fail(path);
    if (schema.format === 'https-url') {
      let url; try { url = new URL(value); } catch { fail(path); }
      if (url.protocol !== 'https:' || url.username || url.password || url.hash || /(?:token|key|secret|password|authorization)/i.test(url.search)) fail(path);
    }
  }
}

export async function loadCatalog(base = root) {
  const specs = [['sources', 'corpus/sources/catalog.json', 'source-catalog'], ['jurisdictions', 'corpus/jurisdictions/catalog.json', 'jurisdiction-catalog'], ['integrations', 'tools/integrations/catalog.json', 'integration-catalog']];
  const catalog = {};
  for (const [key, path, name] of specs) {
    catalog[key] = await readJSON(resolve(base, path));
    validateShape(catalog[key], await readJSON(resolve(base, `schema/${name}.schema.json`)));
  }
  catalog.standards = [];
  for (const name of (await readdir(resolve(base, 'corpus/shared-references'))).filter(n => n.endsWith('.json'))) {
    const standard = await readJSON(resolve(base, 'corpus/shared-references', name));
    validateShape(standard, await readJSON(resolve(base, 'schema/shared-standard.schema.json')));
    catalog.standards.push(standard);
  }
  validateRelationships(catalog);
  for (const s of catalog.sources.sources) for (const skill of s.existing_skills) {
    if (!/^[a-z0-9-]+$/.test(skill)) fail('existing_skills');
    await access(resolve(base, 'skills', skill, 'SKILL.md'));
  }
  for (const integration of catalog.integrations.integrations) if (integration.implementation) {
    if (!/^tools\/integrations\/[a-z0-9.-]+$/.test(integration.implementation)) fail('implementation');
    await access(resolve(base, integration.implementation));
  }
  for (const relationship of catalog.sources.relationships) {
    if (!/^(?:skills|corpus)\/[a-zA-Z0-9/_.-]+$/.test(relationship.evidence) || relationship.evidence.split('/').includes('..')) fail('evidence');
    await access(resolve(base, relationship.evidence));
  }
  return catalog;
}

export function validateRelationships(catalog) {
  const jurisdictions = catalog.jurisdictions.jurisdictions;
  const authorities = catalog.sources.authorities;
  const integrations = catalog.integrations.integrations;
  const sources = catalog.sources.sources;
  const all = [...jurisdictions, ...authorities, ...integrations, ...sources, ...catalog.standards];
  const ids = new Set(all.map(x => x.id));
  if (ids.size !== all.length) fail('duplicate IDs');
  const has = (list, id) => list.some(x => x.id === id);
  for (const j of jurisdictions) {
    let current = j; const seen = new Set();
    while (current) {
      if (seen.has(current.id)) fail('jurisdiction cycle'); seen.add(current.id);
      if (current.parent && !has(jurisdictions, current.parent)) fail('jurisdiction parent');
      current = jurisdictions.find(x => x.id === current.parent);
    }
  }
  for (const a of authorities) if (!has(jurisdictions, a.jurisdiction)) fail('authority jurisdiction');
  for (const s of sources) if (!has(authorities, s.authority) || !has(jurisdictions, s.jurisdiction) || !has(integrations, s.adapter)) fail('source references');
  for (const r of catalog.sources.relationships) if (!ids.has(r.from) || !ids.has(r.to)) fail('relationship references');
  for (const i of integrations) if ((i.status === 'implemented') !== Boolean(i.implementation) || i.credential_reference && i.status === 'implemented') fail('integration execution');
}

async function checkSource(source, { timeoutMs = 5000, fetchImpl = globalThis.fetch, now = () => new Date() } = {}) {
  if (!Number.isInteger(timeoutMs) || timeoutMs < 10 || timeoutMs > 30000) throw new Error('timeoutMs must be 10–30000');
  const result = { source_id: source.id, checked_at: now().toISOString(), reachability: 'unknown', identity: 'unknown', edition: source.edition, effective_date: source.effective_date, legal_applicability: 'unknown', freshness: 'unknown', http_status: null, reason: null };
  if (source.access !== 'public') return { ...result, reason: 'access-required' };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let reader; let response;
  try {
    // Redirects are never followed: avoid login portals, changed publishers and credential forwarding.
    response = await fetchImpl(source.url, { method: 'GET', redirect: 'manual', credentials: 'omit', signal: controller.signal, headers: { Accept: source.identity.allowed_content_types.join(', ') } });
    result.http_status = response.status;
    result.reachability = 'reachable';
    if (response.status >= 300 && response.status < 400) return { ...result, reason: 'redirect-unverified' };
    if ([401, 403].includes(response.status)) return { ...result, reason: 'access-required' };
    if (!response.ok) return { ...result, reason: 'http-error' };
    const contentType = (response.headers.get('content-type') ?? '').split(';')[0].trim().toLowerCase();
    if (!source.identity.allowed_content_types.includes(contentType)) return { ...result, reason: 'unexpected-content-type' };
    if (!response.body) return { ...result, reason: 'empty-body' };
    reader = response.body.getReader();
    const chunks = []; let size = 0;
    while (true) {
      const { done, value } = await reader.read(); if (done) break;
      size += value.length;
      if (size > source.identity.max_bytes) return { ...result, reason: 'body-limit' };
      chunks.push(Buffer.from(value));
    }
    const bytes = Buffer.concat(chunks); const body = bytes.toString('utf8').toLowerCase();
    if (/<input[^>]*type\s*=\s*["']?password\b|<title[^>]*>[^<]*(?:sign in|log in|login)/i.test(body)) return { ...result, reason: 'login-page' };
    const matches = source.identity.contains_all.every(token => body.includes(token.toLowerCase()));
    return { ...result, identity: matches ? 'matched-markers' : 'mismatch', reason: matches ? 'expected-markers-found' : 'expected-markers-missing', content_sha256: createHash('sha256').update(bytes).digest('hex') };
  } catch {
    // Never return transport exception text, body, headers, redirect destinations or credential material.
    return { ...result, reachability: controller.signal.aborted ? 'unknown' : result.reachability, reason: controller.signal.aborted ? 'timeout' : 'transport-error' };
  } finally {
    controller.abort();
    // Cancellation is best-effort and must never hold a bounded receipt open.
    const cancellation = reader ? reader.cancel() : response?.body?.cancel();
    cancellation?.catch(() => {});
    clearTimeout(timer);
  }
}

export async function checkSources(ids, { concurrency = 3, ...options } = {}) {
  const catalog = await loadCatalog();
  if (!Number.isInteger(concurrency) || concurrency < 1 || concurrency > 8) throw new Error('concurrency must be 1–8');
  const sources = ids.map(id => catalog.sources.sources.find(s => s.id === id));
  if (sources.some(s => !s)) throw new Error('Unknown source ID');
  if (sources.length > 100) throw new Error('At most 100 source checks per invocation');
  const results = new Array(sources.length); let next = 0;
  await Promise.all(Array.from({ length: Math.min(concurrency, sources.length) }, async () => {
    while (next < sources.length) { const i = next++; results[i] = await checkSource(sources[i], options); }
  }));
  return results;
}

async function main(args) {
  const catalog = await loadCatalog();
  if (args.length === 1 && args[0] === '--validate') return { valid: true, sources: catalog.sources.sources.length };
  if (args[0] !== '--check' || args.length < 2) throw new Error('Usage: node tools/integrations/source-health.mjs --validate | --check source:ID [source:ID ...]');
  return { checks: await checkSources(args.slice(1)) };
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).then(value => process.stdout.write(JSON.stringify(value, null, 2) + '\n')).catch(() => {
    process.stderr.write('Source check failed: invalid arguments, unavailable package files, or invalid manifest. No source request is made for an invalid catalog.\n'); process.exitCode = 1;
  });
}
