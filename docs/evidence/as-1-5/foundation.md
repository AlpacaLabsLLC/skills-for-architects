# AS 1.5 foundation implementation receipt

- Date: 2026-09-05
- Integrated functional source: `2957b9195d0a9cd8a4638c237d5ef46741b3ccf0`
- Documentation correction: `4eaacce` (candidate release history and maintained context measurement)
- Branch: `feat/as-1-5-foundation`; unpublished local integration branch
- Baseline: `4d4b067b9d57dfb5f50108d915ddf9aad5ed3a71`

## Implemented and checked

- 50 public skills preserved; 60 registered components and nine practice clusters.
- Shared professional knowledge, namespace validator and Studio templates have canonical owners, with compatibility forwarding where applicable. A fresh export outside the repository passes validation, including the hidden Studio MCP template.
- Source/jurisdiction/standard/integration manifests validate. Three existing NYC sources have bounded live identity evidence; no applicable-law conclusion is inferred. EC3 is declaration-only.
- Duplicate amendments/invoices and control-character/escape injection are rejected before record mutation. Commercial lifecycle and migration/recovery fixtures preserve identity, issued terms and ledger history.
- Source-health checks accept maintained IDs, limit time/bytes/concurrency, report redirects and unknown identity explicitly, and isolate failures. The library performs no automatic startup work, credential reads or project-record writes.
- OSS 1.5.0 and MCP service 0.1.0 are documented as independently versioned releases. The 1.5 changelog remains Unreleased; no historical forecast date is presented as publication.

## Verification

[Machine-readable local receipt](foundation-checks.json) retains all 45 initial check results (lint plus 44 shell contracts) and the explicit follow-up correction. The initial suite had one failure: the retained context-size report was stale after skill guidance changed. Its measured body total was refreshed from 450,601 to 451,371 bytes, preserving the prior observation; the context audit, release contract and final CI-mode lint then passed. No runtime changes followed the full suite.

The full suite ran with Node 24.20.0. The source contract suite contains 12 deterministic Node tests, all passing with zero skips. The installed component test exercised an isolated Claude CLI marketplace installation because that executable was present. Codex compatibility was checked by its repository contracts; this does not claim a fresh user-visible Codex workflow or any desktop MCP workflow.

An independent implementation agent reviewed the merged integrity checks, source request/cleanup boundary and category/source references without running tests concurrently. No additional blocking defects were reported. See [Studio verification](studio.md) and [live source evidence](../source-health/2026-09-05-validation.md).

## Hosted handoff and remaining gates

The parallel MCP readiness team owns the hosted implementation. Its final package must consume this integrated foundation source, include the new canonical roots and resources, and revalidate changed script contracts. Local test success does not establish resource completeness in the existing MCP packager.

Remaining: final MCP projection/bindings (including source-health binding if advertised), service/content version separation in runtime status, real client workflow/rendering evidence, CI-to-deployment linkage, upgrade/client-refresh/rollback, published OSS source verification and production handoff. Shared studio services and Norma expansion remain outside scope. See [release delivery](../../release-delivery.md).

No public push, tag, release, MCP deployment, production change or user-data migration was performed by this foundation team.
