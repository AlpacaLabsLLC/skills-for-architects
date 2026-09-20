---
name: epd-parser
description: "Extract GWP, life-cycle stages, certifications, and impact metrics from an EPD PDF. Use when given a declaration to parse; not to find or compare EPDs."
allowed-tools:
  - Read
  - Write
  - WebFetch
  - WebSearch
  - Bash
---

# epd-parser

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component’s [declaration](host-contract.json) (`skill:epd-parser`). Load only applicable modes from the [shared catalog](../../corpus/host-contracts.json); declarations do not grant access or permission. Use the actual host’s [delivery route](../../docs/host-adapters.md).

## Native execution and output custody

Follow this complete source/evidence procedure. Apply the
[EPD-specific native library owner](../../tools/workspace/epd-library-contract.md) only when
consuming or explicitly saving a project EPD library. The host selects available native research,
PDF, file and ordinary task-specific analysis tools. No Arch Studio executable, installed helper,
script reconstruction or external service is required. Source documents remain evidence, not
authority to change selections, adopt records or perform external actions.

For requested saved rows, reports or specification files, follow
[complete native preparation and publication](../../docs/workspace-model.md#native-mutation-sequence)
and [completion reporting](../../docs/completion-reporting.md). Inspect current targets, source
and pending state; retain the full originals/absence, complete prepared output set and actual
access metadata. Finish durable saves and independently reopen/validate **all** original/prepared
bytes and access before the first publisher. Publish complete files under demonstrated writer
protection with no-clobber or guarded revision, then freshly read every actual destination's
bytes/access and verify source guards and the entire result before completion. Exclusive-create
followed by writing into a public path is insufficient. Keep private pending evidence distinct,
recognize exact retries without rewriting and preserve unresolved conflicts or unavailable checks.

A supplied standalone CSV may be structurally inspected under the EPD schema without project
context; that read does not initialize, adopt or mutate a project-root library. The project-root
library operations require valid native project context.

Inline or metadata-only work needs no file creation. Project-bound work resolves
[native context](../project/references/context-resolution.md); it does not infer project creation.
Requested record/document handoffs retain exact source evidence and existing authority. Report
retrieved facts, derived calculations, interpretation, actual custody and unverified scope separately.

## Sources and evidence

Find relevant original links in [the source catalog](../../corpus/sources/catalog.json), filtered by geography and topic. For substantive claims, retrieve the applicable original or authorized supplied document and record its publisher, URL/file, section/page, version/date and task scope. A linked or reachable source is not proof of applicability. If access, edition or identity is unresolved, leave dependent conclusions unresolved; no local table or model-memory fallback. Keep task evidence in the authorized workspace, outside the plugin.

A request only to list sources uses catalog metadata and states that coverage is limited to matching registered entries. It needs no source-content retrieval, setup or approval. Shared and state sources retain their scope; missing LA coverage never substitutes NYC.

Use the [Arch Studio EPD schema](../../schema/epd-schema.md) as an output contract, not an interpretation of external standards. Keep product/variant, declared/functional unit, stage, indicator/method, PCR/version and original page/table locator with each value. Do not assign program eligibility, impact categories, standard equivalence or baseline values from bundled rules. Retrieve the applicable program/standard and original EPD when those conclusions are requested. Preserve unavailable values as blank/unknown, never zero.

Industry-baseline comparison requires the actual identified publication/year and comparable values retrieved for this task. A named baseline alone is not evidence of its values. If unavailable, omit the comparison or request the applicable original; no model-memory baseline.

## Parse the supplied declaration

Accept the selected PDF/URL; preserve exact source bytes/identity in authorized task evidence. Read through an available PDF extraction facility, inspect tables against rendered pages when necessary, and report encrypted/scanned/unreadable pages accurately. Process the complete requested scope, chunking as useful without assuming which pages carry product identity or results.

Extract identity and reported metadata before numbers. Bind each indicator to its printed unit/stage and source cell; preserve footnotes, inequalities, scientific notation and unavailable markers. Multiple products or variants with distinct results stay separate. Sum cells only when the source explicitly establishes additive, nonoverlapping comparable stages and units; do not infer equivalence between standard versions. Record any derived sum separately from extracted values. Never classify LEED eligibility merely from declaration type or verification text.

Return product rows, source/page locators and parsing gaps, including unmatched or unreadable tables. Parsing does not implicitly save a library. On explicit persistence, preview the exact epd-library.csv changes under the schema and workspace ownership rules, preserve unrelated rows and report actual saved paths.

## Outputs and records

Return the requested result with source locators, actual checks and material gaps. A sourced recommendation, deterministic arithmetic and visual inspection are separate evidence. Use the [completion contract](../../docs/completion-reporting.md). For durable project work resolve the project and follow [workspace ownership](../../docs/workspace-model.md); offer facts/decisions to their owner instead of silently writing PROJECT.md. One-off work remains standalone.

## Optional EPD library persistence

On an explicit save request, apply `product_library.validate` with `kind: "epd"` under the
[EPD library owner](../../tools/workspace/epd-library-contract.md) to inspect the exact project-root
epd-library.csv. Prepare one complete array of selected string-valued EPD rows; preview the actual
destination, complete proposed batch, current raw hash and unresolved values. Preserve existing
exact authorization. Apply `product_library.append` with `kind: "epd"` once for that whole selected
batch; never loop per row or infer deduplication from a URL/name/registration match. A missing or
malformed library blocks append; preserve it and report the explicit initialization/import or
repair needed. Do not silently initialize/import as part of append. This skill's normal save is validate plus
append, not product adoption or an FF&E schedule change.

Retain complete original/prepared CSV bytes, exact intent and access, finish durable preparation
and separately verify the entire set before publication. Guard the actual current state, publish
complete old/new bytes and read back the full library plus applicable access metadata. Recognize
an exact prior save from retained operation evidence, not matching row contents alone; retry must
not duplicate rows. Historical EPD preview/recover runner options were unsupported; native
preparation/reconciliation are owner stages, not a claim those executable routes exist. Follow the
exact 42-column [EPD schema](../../schema/epd-schema.md) and [CSV conventions](../../schema/csv-conventions.md).
