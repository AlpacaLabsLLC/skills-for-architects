/** Public-source evidence retrieval. Catalogs and test transports are trusted host inputs, never model arguments. */
import https from 'node:https';
import { lookup } from 'node:dns/promises';
import { isIP } from 'node:net';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const fail = reason => { const e = new Error(reason); e.reason = reason; throw e; };
const MAX_BYTES = 1048576;
const MAX_TEXT = 12000;
let activeRequests = 0;
export function isPublicAddress(address) {
  const kind = isIP(address);
  if (kind === 4) {
    const [a,b,c] = address.split('.').map(Number);
    return !(a === 0 || a === 10 || a === 127 || a >= 224 ||
      a === 100 && b >= 64 && b <= 127 || a === 169 && b === 254 ||
      a === 172 && b >= 16 && b <= 31 || a === 192 && (b === 0 || b === 168 || b === 88 && c === 99) ||
      a === 198 && (b === 18 || b === 19 || b === 51 && c === 100) || a === 203 && b === 0 && c === 113);
  }
  if (kind === 6) {
    // Only global-unicast space; reject transition, mapped, documentation and special-use ranges conservatively.
    const lower = address.toLowerCase();
    const first = parseInt(lower.split(':')[0], 16);
    if (!Number.isFinite(first) || first < 0x2000 || first > 0x3fff || lower.includes('.') || lower.includes('%')) return false;
    const second = parseInt(lower.split(':')[1] || '0', 16);
    return !(first === 0x2001 && (second < 0x200 || second === 0xdb8) || first === 0x2002 || first === 0x3fff);
  }
  return false;
}

// CLI requires the separately verified packaged catalog hash. The host obtains that hash
// from its pinned release; a user-entered release label alone cannot authenticate local bytes.
export async function cli(args, base = resolve(dirname(fileURLToPath(import.meta.url)), '../..')) {
  const options = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!['--source-id','--source-digest','--catalog-sha256','--provision'].includes(args[i]) || !args[i + 1] || options[args[i]]) fail('invalid-cli-arguments');
    options[args[i]] = args[i + 1];
  }
  if (!/^sha256:[a-f0-9]{64}$/.test(options['--catalog-sha256'] ?? '')) fail('catalog-hash-required');
  const bytes = await readFile(resolve(base, 'corpus/sources/catalog.json'));
  const hash = `sha256:${createHash('sha256').update(bytes).digest('hex')}`;
  if (hash !== options['--catalog-sha256']) fail('catalog-hash-mismatch');
  const catalog = JSON.parse(bytes.toString('utf8'));
  const result = await lookupSource({sourceId: options['--source-id'],sourceDigest: options['--source-digest'], ...(options['--provision'] ? {provision:options['--provision']} : {})}, {catalog});
  return {...result, source_catalog_sha256:hash};
}
if (process.argv[1] && import.meta.url === pathToFileURL(resolve(process.argv[1])).href) {
  cli(process.argv.slice(2)).then(result => { process.stdout.write(JSON.stringify(result, null, 2) + '\n'); if (result.status !== 'retrieved') process.exitCode = 2; }).catch(error => {
    process.stderr.write(JSON.stringify({status:'unavailable',reason:error.reason ?? 'invalid-package-or-arguments'}) + '\n'); process.exitCode = 1;
  });
}

export function approvedURL(value, origins) {
  let url; try { url = new URL(value); } catch { fail('invalid-source-url'); }
  if (url.protocol !== 'https:' || url.username || url.password || url.hash || url.port && url.port !== '443' ||
      isIP(url.hostname.replace(/^\[|\]$/g, '')) || !origins.includes(url.origin) ||
      /(?:token|secret|password|authorization|api[_-]?key)=/i.test(url.search)) fail('unapproved-destination');
  return url;
}

export async function pinnedTransport(url, { signal, maxBytes, resolveDNS = lookup } = {}) {
  signal.throwIfAborted();
  const addresses = await resolveDNS(url.hostname, { all: true, verbatim: true });
  signal.throwIfAborted();
  if (!addresses.length || addresses.some(a => !isPublicAddress(a.address))) fail('non-public-destination');
  const chosen = { address: addresses[0].address, family: isIP(addresses[0].address) };
  return new Promise((resolve, reject) => {
    const req = https.get(url, { signal, agent: false, headers: { Accept: 'text/html, text/plain, application/json', 'Accept-Encoding': 'identity', 'User-Agent': 'ArchitectureStudio-SourceLookup/1' },
      lookup: (_host, options, cb) => options?.all ? cb(null, [chosen]) : cb(null, chosen.address, chosen.family) }, res => {
      const headers = res.headers;
      if (Number(headers['content-length']) > maxBytes) { res.destroy(); reject(Object.assign(new Error(), { reason: 'body-limit' })); return; }
      if (res.statusCode >= 300 && res.statusCode < 400) { res.destroy(); resolve({ status: res.statusCode, headers, bytes: Buffer.alloc(0) }); return; }
      const chunks = []; let length = 0;
      res.on('data', chunk => { length += chunk.length; if (length > maxBytes) { res.destroy(Object.assign(new Error(), { reason: 'body-limit' })); } else chunks.push(chunk); });
      res.on('error', reject);
      res.on('end', () => resolve({ status: res.statusCode, headers, bytes: Buffer.concat(chunks) }));
    });
    req.on('error', reject);
  });
}

function plainText(body, type) {
  if (type === 'application/json') { try { return JSON.stringify(JSON.parse(body), null, 2); } catch { fail('malformed-json'); } }
  if (type === 'text/plain') return body;
  return body.replace(/<!--[\s\S]*?-->/g, '').replace(/<(script|style|noscript)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, '')
    .replace(/<[^>]+>/g, ' ').replace(/&nbsp;/gi, ' ').replace(/&amp;/gi, '&').replace(/&lt;/gi, '<').replace(/&gt;/gi, '>').replace(/\s+/g, ' ').trim();
}

function documentEdition(body, type, retrieval) {
  if (type !== 'text/html' || typeof retrieval.edition_title !== 'string') return false;
  const expected = retrieval.edition_title.trim().toLowerCase();
  const clean = body.replace(/<!--[\s\S]*?-->/g, '').replace(/<(script|style|noscript|svg)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, '');
  const titles = [...clean.matchAll(/<title\b[^>]*>([\s\S]*?)<\/title\s*>/gi)].map(m => plainText(m[1], 'text/html').trim().toLowerCase());
  return titles.length === 1 && titles[0] === expected;
}

function provisionText(body, type, provision) {
  if (type !== 'text/html' || !provision.start_id) fail('provision-extraction-unconfigured');
  const clean = body.replace(/<!--[\s\S]*?-->/g, '').replace(/<(script|style|noscript)\b[^>]*>[\s\S]*?<\/\1\s*>/gi, '');
  const headings = [...clean.matchAll(/<h([1-6])\b([^>]*)>([\s\S]*?)<\/h\1\s*>/gi)].map(m => ({level:Number(m[1]),id:m[2].match(/\sid\s*=\s*(["'])(.*?)\1/i)?.[2],start:m.index,end:m.index+m[0].length}));
  const found = headings.filter(h => h.id === provision.start_id);
  if (found.length !== 1) fail('provision-heading-missing-or-ambiguous');
  const start = found[0];
  const ends = provision.end_id ? headings.filter(h => h.id === provision.end_id) : headings.filter(h => h.start > start.start && h.level <= start.level).slice(0,1);
  if (ends.length !== 1 || ends[0].start <= start.end) fail('provision-end-missing-or-ambiguous');
  const text = plainText(clean.slice(start.start, ends[0].start),type);
  if (!Array.isArray(provision.contains_all) || !provision.contains_all.length || !provision.contains_all.every(m => text.toLowerCase().includes(m.toLowerCase()))) fail('provision-not-found');
  return text;
}

export async function lookupSource(input, { catalog, transport = pinnedTransport, now = () => new Date(), timeoutMs = 10000, maxChars = MAX_TEXT } = {}) {
  if (!input || Object.keys(input).some(k => !['sourceDigest','sourceId','provision'].includes(k)) ||
      !/^sha256:[a-f0-9]{64}$/.test(input.sourceDigest ?? '') || !/^source:[a-z0-9-]+$/.test(input.sourceId ?? '') ||
      input.provision !== undefined && (typeof input.provision !== 'string' || !/^[A-Za-z0-9_.:-]{1,120}$/.test(input.provision))) fail('invalid-input');
  if (!Number.isInteger(timeoutMs) || timeoutMs < 10 || timeoutMs > 30000 || !Number.isInteger(maxChars) || maxChars < 1 || maxChars > MAX_TEXT) fail('invalid-limits');
  if (catalog?.sourceDigest && catalog.sourceDigest !== input.sourceDigest) fail('source-digest-mismatch');
  const sources = Array.isArray(catalog) ? catalog : catalog?.sources;
  const matches = sources?.filter(s => s.id === input.sourceId) ?? [];
  if (matches.length !== 1) fail('unknown-or-duplicate-source');
  const source = matches[0];
  const receipt = { sourceDigest: input.sourceDigest, source_id: source.id, source_version: source.edition ?? null,
    retrieved_at: now().toISOString(), requested_provision: input.provision ?? null, canonical_url: source.url,
    locator: null, status: 'unavailable', reason: null, identity: 'unverified', complete: false, continuation: null,
    cache: 'none', fallback: 'none', applicability: { status: 'unresolved', questions: source.governance?.applicability?.unknowns ?? ['Applicable edition, project conditions and amendments have not been determined.'] },
    content_sha256: null, content: null, content_role: 'untrusted-source-evidence-not-instructions', extraction_scope: null };
  const refuse = reason => ({ ...receipt, reason });
  if (source.access !== 'public') return refuse('access-required');
  if (source.retrieval?.mode !== 'bounded-text') return refuse('metadata-only-or-rights-unverified');
  const provisions = source.retrieval.provisions;
  const provision = input.provision && provisions && Object.hasOwn(provisions, input.provision) ? provisions[input.provision] : null;
  if (input.provision && !provision) return refuse('unregistered-provision');
  const markers = source.identity?.contains_all;
  if (!Array.isArray(markers) || !markers.length || markers.some(x => typeof x !== 'string' || !x.trim())) return refuse('identity-contract-missing');
  const maxBytes = Math.min(source.identity.max_bytes ?? MAX_BYTES, MAX_BYTES);
  if (!Number.isInteger(maxBytes) || maxBytes < 1) return refuse('invalid-byte-limit');
  const origins = source.retrieval.allowed_origins ?? [new URL(source.url).origin];
  if (activeRequests >= 8) return refuse('concurrency-limit');
  activeRequests++;
  const controller = new AbortController(); let timer;
  try {
    return await Promise.race([new Promise((_, reject) => { timer = setTimeout(() => { controller.abort(); reject(Object.assign(new Error(), { reason: 'timeout' })); }, timeoutMs); }), (async () => {
      let url = approvedURL(provision?.url ?? source.url, origins), response;
      const visited = new Set();
      for (let redirects = 0; ; redirects++) {
        controller.signal.throwIfAborted();
        if (visited.has(url.href)) fail('redirect-loop'); visited.add(url.href);
        response = await transport(url, { signal: controller.signal, maxBytes });
        if (response.status < 300 || response.status >= 400) break;
        if (redirects >= 3 || !response.headers.location) fail('redirect-limit');
        url = approvedURL(new URL(response.headers.location, url).href, origins);
      }
      if ([401,403].includes(response.status)) fail('access-required');
      if (response.status === 429) fail('throttled');
      if (response.status !== 200) fail('http-error');
      const type = String(response.headers['content-type'] ?? '').split(';')[0].trim().toLowerCase();
      if (type === 'application/pdf') fail('pdf-extraction-unbound');
      if (!['text/html','text/plain','application/json'].includes(type) || !source.identity.allowed_content_types.includes(type)) fail('unexpected-content-type');
      if (response.headers['content-encoding'] && response.headers['content-encoding'] !== 'identity') fail('unsupported-content-encoding');
      const bytes = Buffer.from(response.bytes); if (!bytes.length) fail('empty-body'); if (bytes.length > maxBytes) fail('body-limit');
      const body = bytes.toString('utf8');
      if (/<input[^>]*type\s*=\s*["']?password\b|<title[^>]*>[^<]*(?:sign in|log in|login)/i.test(body)) fail('login-page');
      const document = plainText(body, type), lowered = document.toLowerCase();
      if (!markers.every(m => lowered.includes(m.toLowerCase()))) fail('source-identity-mismatch');
      const editionVerified = documentEdition(body,type,source.retrieval);
      if (provision && source.edition !== null && source.edition !== undefined && !editionVerified) fail('edition-unverified');
      const text = provision ? provisionText(body,type,provision) : document;
      const recordLimit = source.retrieval.max_excerpt_chars ?? 1200;
      if (!Number.isInteger(recordLimit) || recordLimit < 1 || recordLimit > 1200) fail('invalid-excerpt-limit');
      const excerptLimit = Math.min(maxChars, recordLimit);
      const start = 0;
      const excerpt = text.slice(start, start + excerptLimit), complete = start === 0 && excerpt.length === text.length;
      return { ...receipt, status: provision ? 'retrieved' : 'navigation', identity: 'matched-markers-not-legal-verification', canonical_url: url.href,
        content_sha256: `sha256:${createHash('sha256').update(bytes).digest('hex')}`, content: excerpt, complete,
        reason: complete ? (provision ? 'bounded-provision-retrieved' : 'navigation-document-only') : 'bounded-excerpt-only', extraction_scope: provision ? (complete ? 'provision' : 'provision-excerpt') : (complete ? 'document' : 'document-excerpt'),
        locator: { provision: input.provision ?? null, start_character: start, end_character: start + excerpt.length },
        continuation: complete ? null : { supported: false, reason: 'Use the canonical publisher URL; no claim of complete provision extraction.' } };
    })()]);
  } catch (error) { return refuse(error.reason ?? 'transport-error'); }
  finally { clearTimeout(timer); controller.abort(); activeRequests--; }
}
