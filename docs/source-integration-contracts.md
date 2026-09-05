# Source and integration contracts

AS 1.5 distributes a small, validated source map. The manifests identify sources;
they do not resolve all applicable law or bundle licensed standards. The same files
and checking library can be packaged into OSS and hosted MCP. A hosted binding,
scheduler and persistent health store are **not implemented** by this module.

## Ownership and files

| File | Owns |
|---|---|
| [Source catalog](../corpus/sources/catalog.json) | Authority identities, official URLs, document kinds, dates, access and rights, identity markers, and explicit relationships |
| [Jurisdiction catalog](../corpus/jurisdictions/catalog.json) | Geographic hierarchy and bounded coverage declarations |
| [ASTM E84 reference](../corpus/shared-references/astm-e84.json) | A single metadata-only shared standard identifier; no licensed text or adopted edition |
| [Integration catalog](../tools/integrations/catalog.json) | Execution routes, implementation status, data recipients, credential references and input/output contracts |
| [Checker](../tools/integrations/source-health.mjs) | Local validation and explicit asynchronous public-source health operation |

The existing NYC zoning, PLUTO and construction-code references are representative
entries. US and New York State are routing parents, not new supported regulatory
implementations. A construction-code index is not a provision-level code corpus.
Unknown edition, effective date and checked-at fields remain `null`; an index URL
that says “latest” does not select a project's applicable edition.

Relationships may distinguish publication, adoption, amendment, incorporation,
reference, interpretation and supersession. Every recorded edge requires evidence
and carries edition/effective-date fields, including explicit unknowns. Current
catalog edges only assert existing publication provenance. Adding a standard ID
never implies its adoption into NYC law. The schema permits that relationship when
its evidence and edition have been established. Project-specific applicability
and conclusions belong in governed Studio/project records.

## Validate without network

Requires Node.js 18 or later; no npm install or external dependency:

```sh
node tools/integrations/source-health.mjs --validate
bash tests/test-source-contracts.sh
```

Validation reads the four bundled JSON schemas, rejects unknown properties,
missing required fields, bad types/dates and credential-bearing URLs, and checks
IDs, hierarchy cycles, relationship targets, evidence paths, skill references and
implementation paths. The validator implements only the schema vocabulary used
in these files; it is not a general-purpose JSON Schema engine. If a maintainer
adds another schema keyword, they must implement its enforcement and tests.

## Check a maintained source explicitly

```sh
node tools/integrations/source-health.mjs --check source:nyc-zoning-resolution source:nyc-pluto
```

The CLI accepts registered source IDs, never arbitrary URLs or request headers.
Checks do not run at import/startup and do not mutate catalogs or private records.
A completed check can report degradation; CLI exit zero means a report was produced,
not that sources passed. Invalid arguments/catalogs exit nonzero before requests.
The default is three concurrent requests, a five-second timeout per request and
at most 100 checks per invocation. Each manifest caps received bytes (maximum 1 MiB).
Redirects are reported without following them, including same-host redirects;
a maintainer must verify a replacement URL before changing the source map.

A host can call the shared asynchronous operation:

```js
import { checkSources } from './tools/integrations/source-health.mjs';
const results = await checkSources(['source:nyc-zoning-resolution'], {
  concurrency: 2, // allowed 1–8
  timeoutMs: 5000, // allowed 10–30000
});
```

The library loads the package-owned catalog internally. Do not accept an uploaded
catalog or expose the test-only injected transport option as a remote input.
Hosted deployment must protect its package from untrusted writes, retain egress
controls and publish an explicit reviewed binding. Central scheduling is future
MCP work, not a capability inferred from this callable library.

Results separate reachability, identity markers, freshness and legal applicability.
Only the first two are checked; freshness and applicability always remain unknown.
A matching marker identifies expected page structure, not an unchanged legal
edition. SHA-256 describes only the response bytes checked. Compare it with prior
receipts to flag changes for inspection; it does not interpret amendments. Login
pages, missing markers, redirects, unavailable responses, byte limits, and timeouts
have distinct reasons. A transport error does not establish publisher outage.

The timeout includes response streaming through the native fetch abort signal.
The finalizer aborts the request and requests body cancellation on every exit,
without waiting on uncooperative cancellation. Individual transport failures do
not discard other checks. Test transports must honor the abort signal; injected
transports are not a supported public server capability. Results exclude response
bodies, headers, redirect destinations, URLs, and exception messages.

## External integrations and credentials

EC3 is a declaration-only entry motivated by the existing EPD research procedure.
It does not implement API calls, provider scopes, token validation, OAuth, an MCP
connection or a hosted service. Required scopes remain unknown until a separate
adapter is implemented and verified. `AS_EC3_API_TOKEN` is an example credential
**reference name**, never a value read by the source checker.

The host/user owns authentication for a host-connected integration. A future
AS-server binding would need its own scoped secure credential storage and explicit
input transfer. Secrets must never enter the distributed catalog, source-health
reports or ordinary Studio/project records. Studio initialization still leaves
its reserved `.mcp.json` empty; declaring an integration does not configure one.

No test result here establishes current EC3 provider requirements, legal reuse
rights, or actual publisher applicability. Inspect access/reuse conditions at
retrieval and preserve provenance where permitted.
