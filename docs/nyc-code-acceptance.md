# NYC lookup acceptance and maintenance

This runbook extends [AS release delivery](release-delivery.md); it does not create another release pipeline. It records required checks, not completed tests. **No publication or deployment is authorized by this document.**

## Remaining acceptance gates

| Gate | Required evidence |
|---|---|
| N01–N13 coverage | Each declared lookup has a verified source/locator and an honest operation status. Many current records provide navigation or metadata only. A linked source, HTTP 200 or instruction card does not prove provision retrieval. |
| PDF execution | A reviewed parser worker with enforced memory/CPU/process limits, bounded pages/input/output and timeout/cleanup tests. Native `pdftotext` availability alone is insufficient; the current unbound PDF path stays unavailable. |
| Independent review | Fixed and retested code/security findings; a named qualified reviewer for reference classification, applicable-version behavior and rights restrictions. Agent review is not specialist approval. |
| Four hosts | Actual calls in ChatGPT desktop, Claude desktop, Codex terminal and Claude Code terminal against the same authorized staging candidate. Record host/runtime and observed tool identities, not status counts alone. |
| Release transition | Exact OSS/MCP package closure and binding parity; changed-digest refusal, candidate upgrade and rollback evidence. Previously accepted AS 1.5.0 deployments do not prove this new content works. |

Deployment of the new candidate requires separate authorization and authenticated clients. Do not advertise the entire N01–N13 slice as complete until its approved coverage denominator passes, or the product owner explicitly changes scope.

## Host evidence protocol

Before testing, the release owner supplies `EXPECTED_AS_VERSION`, `EXPECTED_SOURCE_DIGEST`, the staging connector name and immutable service build identity. Replace the placeholders below; do not reuse an earlier digest merely because the displayed AS version is unchanged. Run all three prompts in each host and preserve actual tool receipts.

Public lookup needs no Mac folder grant, Work/Cowork transition or project initialization. Native host tools may run the packaged integration only when exact-package provenance and its permitted execution path are verified. A workflow tool such as `as_nyc_building_code` is not the retrieval engine; the executable binding is `as_source_lookup` when discovered. Never invent availability from prose or silently substitute an installed AS skill.

### 1. Real HTML provision

```text
Use only Architecture Studio Staging for AS instructions/maps. Public network lookup is allowed; do not access local project folders or save files.

Call as_status and require EXPECTED_AS_VERSION and EXPECTED_SOURCE_DIGEST. Stop on mismatch and pin every later AS call to the returned digest. Discover the actual as_source_lookup schema; a catalog entry or workflow response does not count as an executable call.

Call as_ada_requirement for a bounded excerpt from federal ADA 2010 section 404, retaining the same digest. Read its required shared resources completely. Inspect source:us-ada-standards and its registered 404 locator; if not registered or supported in this candidate, report that blocker instead of guessing a URL. Section 404.2.3 has no independently verified heading selector in this candidate; do not substitute an alleged complete clear-width provision.

Call as_source_lookup using the registered source/provision and discovered input schema. Report whether the actual provision text was retrieved—not merely navigation or a TOC. Give a short sourced summary only if the text/edition/locator were verified. Report AS digest separately from external source edition, retrieval time, content hash, completeness, rights limits and applicability unknowns. Name every actual tool called. Do not claim compliance or hide partial/unavailable results.
```

Pass requires a real supported section excerpt and appropriately qualified answer; an explicit failure is useful evidence but not a successful-lookup pass. Section 404 exceeds the excerpt limit, so preserve `complete: false` and `provision-excerpt`; this test does not establish full-section coverage. Never interpret `complete` without its extraction scope.

### 2. Unknown applicable edition

```text
Use Architecture Studio Staging only for AS instructions/maps. Call as_status, require EXPECTED_AS_VERSION and EXPECTED_SOURCE_DIGEST, and pin subsequent calls. No local workspace is needed.

Call as_nyc_code_edition with: “Which NYC energy-code edition applies to an existing-building conversion? I have not supplied the filing/completeness date or other applicability facts.” Read the relevant maintained family/edition records and required resources.

Return only evidenced edition candidates and the material missing question(s). Do not select the newest edition, treat enactment as effectiveness, or assign one global code year to every regime. If the maintained edition map is incomplete, state that. If an executable source lookup is used, identify its actual call and distinguish the externally retrieved evidence from the packaged source map. Report the pinned digest and actual tools called; make no project changes.
```

Pass requires appropriate uncertainty, not a predetermined code year. A guessed year fails even if it happens to be correct for some projects.

### 3. Blocked source

```text
Use Architecture Studio Staging only for AS instructions/maps. Call as_status, require EXPECTED_AS_VERSION and EXPECTED_SOURCE_DIGEST, and pin subsequent calls. Do not request a folder grant.

Inspect source:nyc-fire-code and confirm its current metadata-only/access status. If this candidate supports it instead, select another explicitly metadata-only source from the pinned map and report the substitution before testing.

Call the discovered as_source_lookup with that registered source ID and the pinned digest. Report the actual unavailable/rights result. Do not fetch another URL, bypass access controls, run an uncontained PDF parser, use an old snapshot or answer the missing provision from memory. Identify the official access route, what remains unavailable, and actual tools called. No files should change.
```

Pass means the engine refuses as specified, returns no invented source text and the host preserves the boundary. It does not mean the blocked domain has provision coverage.

## Record the result once

For each host/case retain: timestamp; host/runtime; connector; AS version/digest; service build; discovered relevant tool names; workflow and executable calls separately; source/provision IDs; external URL/edition/hash; exact status/completeness; answer or refusal; and deviations. Classify `pass`, `fail` or `not run`. Do not turn metadata-only results, schema discovery or refreshed counts into lookup passes.

## Every source or AS upgrade

1. Edit the canonical geographic record or shared-standard record, never the generated compatibility catalog or packaged MCP copy. Preserve stable source IDs; keep family and edition identities separate. Attach evidence for dates, relationships, locators and rights changes. Missing review is explicit.
2. Regenerate the source/jurisdiction indexes with `node tools/integrations/geographic-catalog.mjs --write`; verify using `--check`. Run the source, route, package-closure and full repository regressions. Check every added route has registered source dependencies and every obsolete locator is removed or explicitly unsupported.
3. A source-map change changes the AS package digest. A publisher-body change changes the external content hash; it does not automatically change the AS release or prove a new legal edition. Inspect changed title, section boundaries, edition, effective dates and permissions before approving updated identity markers. Never relax a marker merely to restore green checks.
4. There is no silent source cache fallback. If caching is later introduced, use source/version/provision keys with timestamp and explicit freshness rules; invalidate affected evidence when identity/edition/rights change. Retain historical receipts as historical, not current authority.
5. Review changed engine bytes and dependencies separately from source content. Re-run SSRF, redirect, timeout/byte limits, malformed/PDF, wrong-edition/TOC, injection and partial-extraction tests. Bind the exact reviewed engine hash in the existing MCP pipeline; do not bypass a mismatch by updating an expected hash without review.
6. Build the candidate through the existing OSS-to-MCP converter. Prove transitive resource closure across `skills/`, `corpus/`, `tools/`, `clusters/` and referenced schemas; compare actual callable names and engine behavior, not just totals. Confirm stale AS digests are rejected and external publication changes are reported without mixing releases.
7. With authorization, deploy the immutable candidate to staging and run the four-host matrix. Verify new tool discovery/refresh in each host independently; reconnecting one client does not refresh another client or another conversation. OAuth/account installation and per-session tool discovery are distinct gates.
8. Exercise rollback to the previous known-good service/content pair in the authorized test environment, verify identities and a representative call, then restore the candidate if approved. Never mutate user workspaces for rollback testing. Promote only after the normal publication and production authorization gates pass.

Keep limitations in the coverage ledger and release recommendation. Do not rename an unavailable capability “complete” to meet a date, and do not broaden folder permissions or provider access to compensate for a missing binding.
