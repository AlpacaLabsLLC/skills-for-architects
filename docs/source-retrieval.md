# Bounded lookup integration receipt

Implementation files: source-lookup.mjs, source-lookup.test.mjs, source-lookup-result.schema.json.

## Trust boundary

Only sourceDigest, sourceId and optional registered provision key are model inputs. Catalog, transport and time/size configuration are trusted host configuration. The default transport resolves and validates every DNS answer, pins one public address to the TLS request (retaining hostname certificate verification), and repeats this on every approved-origin redirect. It does not send cookies, authorization headers or caller-supplied headers. Injected transports exist for offline fixtures and must never be model-selectable.

MCP integration must load the catalog from the requested verified release and set catalog.sourceDigest. This module checks equality when that field is present. CLI verifies --catalog-sha256 against exact packaged corpus/sources/catalog.json bytes. Expected catalog hash must come from pinned release metadata, not a hash invented from whatever file happens to exist locally. AS sourceDigest is host-attested attribution, not a claim that this adapter independently reconstructs the complete AS release digest.

No source cache or fallback exists. A source index/landing-page retrieval is navigation evidence, not a provision extraction. The source and registered provision markers check identity only; they are not legal verification. Truncation is explicit and offers no fake continuation. Public-source text is untrusted data even after script/style removal.

For HTML provisions, a registered unique heading ID and a bounded following heading
are required. Editioned sources require one matching document title after excluding
comments, scripts and SVG icon titles. Navigation labels, TOC links and inherited
object keys cannot satisfy a provision request. The current verified ADA locator is
section 404; 404.2.3 is not independently registered. MDW and Zoning Resolution
locators remain metadata-only until a reviewed structural extractor supports them.

## PDF execution blocker (verified 2026-09-06)

Local pdftotext 26.04.0 is available and exposes first/last-page limits. However, the Mac command `/bin/sh -c 'ulimit -v 262144'` returned exit 1, "virtual memory: cannot modify limit: Invalid argument". Node child-process timeout and maxBuffer bound wall time and output, not parser memory or decompression amplification. No reviewed container/OS memory containment worker is configured here. Thus PDF retrieval explicitly returns pdf-extraction-unbound. This is a W3 acceptance gap, not implemented PDF support and not evidence that PDF-backed provision coverage is complete.

The safe follow-on binding must use a trusted configured worker with OS-enforced memory/CPU/process/file limits, a private scratch directory, no parser network access, an allowlisted exact executable (no shell/user arguments), bounded input bytes/pages/output, wall timeout killing the whole process group, sanitized failure receipts, no password bypass and guaranteed cleanup. Test valid/malformed/encrypted/oversized/incomplete PDFs before enabling it. Serverless and native hosts require separate verified worker availability; fallback to an uncontained local binary is prohibited.

## Tests

Offline fixtures cover public/private IPv4/IPv6, transition ranges, numeric host normalization, credentials, unexpected origins, mixed DNS results, digest mismatch, registered provision requirements, rights refusal, HTML/JSON identity and login failures, wrong edition/missing provision, explicit PDF unsupported status, redirect loops/origin checks, timeouts/body bounds/throttling, untrusted content labels, incomplete excerpts, 8-request concurrency bound, mandatory CLI catalog hash and per-record excerpt restrictions. Live publisher and four-host tests remain separate evidence gates.
