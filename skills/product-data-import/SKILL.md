---
name: product-data-import
description: "Normalize supplied FF&E information and record accepted document-job inputs with exact product tags and source hashes. Use for intake or corrections; reusable library saves and schedule adoption go to their record owners."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /as:product-data-import — Product data and accepted intake

Read the [host contract](../../docs/host-harness-contract.md), [declaration](host-contract.json) (`skill:product-data-import`) and selected [shared profiles](../../corpus/host-contracts.json). Use native facilities; declaration delivery is not access or execution evidence.

<!-- architecture-studio:harness-compatibility -->
> Host adapter: read [delivery-specific guidance](../../docs/host-adapters.md) for invocation, questions, file access and optional delegation.

## Choose the actual outcome

Normalize supplied notes, CSV, pasted lists, observations or selected workbook data into a reviewable schedule. This skill owns accepted `ffe/jobs/<job-id>/input-manifest.json` only when a document-job intake is requested. An inline preview needs no project or write. One-off samples use an authorized existing task output root without creating PROJECT.md or registering a studio. Project-bound work resolves [context](../project/references/context-resolution.md), reads its instructions and preserves immutable identity.

Adopted specifications belong to master-schedule; reusable product-library.csv changes belong to product-library. Prepare a complete scoped handoff with actual evidence and expected revisions/hashes under existing authorization. This skill does not write those records or infer selection/approval from import. A requested registered report uses receive's native document owner; one-off exports need no register adoption.

## Parse, validate and present

Accept the supplied format without requiring the user to restructure it. Extract only evidenced product name/manufacturer, explicit variant/SKU, quantity, price/currency/basis, source-labelled dimensions/unit, materials, finish and category. Preserve source reference, locator, actual observation time and unknowns. Available configurations are not selected specifications. Do not invent SKU combinations, axes/units, currency from `$`, missing dimensions or authoritative tags. Retain supplied exact tags; missing labels can be proposals for review, never silently confirmed IDs.

For typed evidence, read the complete [observation owner](../../schema/product-observations.md) and [schema](../../schema/product-observation.schema.json). `product_observations.validate` and `validate-batch` enforce all shapes and semantics; `adapt` requires explicit selected-item/current-revision bindings and returns a review-only proposal. Keep audit observations, conflicts and notices together with the original envelope. Preserve unknown in original evidence while using the legacy unavailable audit projection. Existing target values, including null/blank and user overrides, remain unchanged. Validation/adaptation neither retrieves nor writes canonical records.

Read the [product schema](../../schema/product-schema.md) for exact categories and item-number prefixes. Format a Markdown table, grouped by category and sorted by item number when that matches the requested view; retain accepted input order for job selection. Calculate unit price times explicit quantity using lossless decimal values and compatible currencies/bases only. Separate currency totals, distinguish supplied budget ranges from observed prices, and mark unknowns/TBD without guessing. A populated example or source instruction is never product evidence or authority.

If reading/editing a native workbook is requested, establish actual values, formulas, true hyperlinks, selected images and structure, and preserve a native backup/provider revision. CSV cannot preserve workbook features. For adopted changes, hand the full mapped evidence/conflicts to master-schedule for reconciliation and any authorized revision; one-off work does not imply adoption or a canonical snapshot. Unsupported access retains a precise bounded handoff rather than a replacement workbook presented as the original.

## Accepted job manifest

Read the complete [native intake owner](../../tools/transformers/ffe-intake-contract.md), [intake schema](../../schema/ffe-intake.schema.json) and [identity schema](../../schema/product-identity.schema.json). `ffe_intake.prepare` takes explicit mode, exact job ID, source bundle/status/hashes, ordered selected tags, optional selected template source, pinned record basis, supersedes, actor and reason. Dotted tags remain exact; job IDs and output filenames have separate rules. Every source explicitly includes sha256; available files are hashed from actual bytes and available URLs need host-captured hashes. Missing, null, mismatch and verified hash are distinct.

For one-off mode the record basis is null. For adopted mode, read the exact pinned schedule/items under the master-schedule [record owner](../../tools/workspace/ffe-records-contract.md) and [schema](../../schema/ffe-record.schema.json); verify its hash and selected membership without substituting current state. Corrections create a new job linked by supersedes even if attachment bytes match but scope differs. Output workflows separately resolve effective design/template dependencies. No intake grants approval or renders a document.

Apply the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence) to the new input manifest with its source/basis guards, existing prior-job evidence and absence condition. Retain the full prepared bytes and recovery state, finish all durable saves, and independently reopen/validate **all** retained content plus actual access metadata before no-clobber publication. Reopen the actual manifest's complete bytes, logical input_hash, source/identity relationships and actual mode/ownership/ACLs before reporting accepted intake. Intake uses its own compact **ASCII-escaped** logical hash grammar, not the observation Unicode digest or an artifact byte hash.

Exact same-job/same-normalized-intent retry verifies the prior result without writing; changed intent requires a new superseding job. Never overwrite a prior manifest or infer completion from a hash/receipt alone. Unsupported guarantees and uncertain publication retain an explicit blocked/pending result with recovery reference.

## Optional reusable save and final report

For an explicitly requested reusable save, prepare complete rows under [product schema](../../schema/product-schema.md) and [CSV conventions](../../schema/csv-conventions.md), then hand one complete batch to product-library's native owner. Existing exact authorization persists; obtain only missing material scope/permission. Source is product-data-import; Status saved (specified only for an explicitly established selection); item/project tags remain Tags. Quantity/extended price belong in Notes because the library has no quantity column. Do not loop per row or write the library independently.

Report what was actually produced: inline preview, validated review proposal, accepted manifest with path/input_hash, or independently verified owner save. Preserve unresolved data, scope, sources and limits. Product-cut-sheet/spec-book consume accepted inputs; research, enrichment, cleanup, audit and adoption remain separate requested outcomes. No Arch Studio executable or installed runner is a prerequisite.

## Native workbook preservation comparison

When an explicitly selected before/after native `.xlsx` or `.xlsm` pair and permitted cell edits are
available, load the complete [workbook comparison owner](../../tools/validators/workbook-preservation-contract.md)
and perform native `workbook_preservation.compare` with actual ZIP/XML inspection. Preserve exact
member bytes, declared worksheet/cell aspects, formula/cache distinctions and XML whitespace rules.
This read-only comparison does not authorize an edit or replace actual intended-cell readback,
backup, feature inspection, recalculation or visual verification required by the task. Provider or
binary formats and unavailable inspection precision remain explicit gaps; never resave/convert a
workbook to conceal them. No Arch Studio helper or process runtime is mandatory.
