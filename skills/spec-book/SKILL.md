---
name: spec-book
description: Assemble a complete ordered FF&E specification package from an explicit item scope, composing product cut sheets with resumable verification. Use for a spec book, all scheduled product PDFs, or a combined specification package.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# /as:spec-book — Assemble a Specification Package

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

Compose `/as:product-cut-sheet`; do not duplicate extraction, research or sheet layout logic. Input: explicit ordered scope, pinned schedule/item revisions or a one-off snapshot, accepted template, grouping and audience. Output: individual/combined artifacts as requested and a package revision receipt owned by this skill. Item/schedule records remain owned by `/as:master-schedule`; decisions and project facts remain owned by `/as:project`.

## 1. Resolve and freeze the package

Resolve the nearest valid `PROJECT.md`, read instructions, and preserve malformed/unindexed records. Do not infer context from plugin installation. If unresolved, select a registered project through `/as:studio`; never create one implicitly. Use project-relative references and preserve source originals. Read before write. No issue/approval state is inferred from artifact generation.

Reuse authorization and supplied corrections. Ask once only if a material choice remains unresolved; combine exact target, scope, template, audience and effects in the single gate. For an adopted schedule, pin the full schedule ID/revision/hash and each selected item ID/revision using the record read helper. For one-off work, explicitly pin a source snapshot without adoption. Do not let an older workbook, cached scope or historic output package replace a corrected accepted source. Schedule updates, workbook reconciliation and recovery route to their owner.

Build an explicit ordered expected-tag list. Define product-versus-finish grouping through `outputs[].item_ids`; never assume one spreadsheet row equals one sheet. For AP-01–AP-13, the expected set is exactly those 13 tags, not a prior 24-item selection. Omissions require recorded user authorization and a revised scope; a missing or failed item is not an authorized omission. Preserve exact tags and isolate filenames by unique `ffe/jobs/<job-id>/<revision>/` folder.

## 2. Prepare and compose sheets

Resolve the centrally owned [document design system](../../studio/standards/documents/design-system.md) and [cut-sheet template](../../studio/templates/documents/product-cut-sheet/template.md) plus [book template](../../studio/templates/documents/spec-book/template.md). Layout/type rules live there, not in this skill. Use `document_contracts.py resolve` from the shared [output contracts](../../tools/renderers/README.md): explicitly selected project/job assets first, configured studio assets next, bundled assets last. A supplied accepted reference takes precedence for its declared rules; record `reference_overrides` and its hash rather than silently replacing it. Missing assets or incompatible dependencies block the affected output.

Resolve the requested physical preset/custom dimensions, portrait/landscape and displayed measurement units separately. Pin design/template IDs, versions, asset hashes, page dimensions, margins, content area and layout version in `resolved-design.json`. Pass it as `--design` to preparation and verification. Re-resolve current dependencies before verification; retain earlier resolved bytes. The host follows size-aware grid/type/overflow rules and inspects every actual page, image resolution and 100% print geometry. Do not scale a Letter layout to a board, substitute a nearby paper size, or imply product images have drawing scale. Unsupported combinations are explicit blockers.


Follow [output contracts](../../tools/renderers/README.md). Bind accepted template hash/layout, audience field allowlist, sourced images, expected page counts and whether a combined PDF was requested. Declare `front_matter_pages` when cover/index pages are requested, using the central book template; default is zero. The host verifies final index destinations and page numbering after assembly. Keep client rendering inputs free of internal fields. Private controls, excluded values and source files never enter `delivery/`.

Run `ffe_outputs.py prepare` once for the exact package snapshot and contract. Invoke `/as:product-cut-sheet` logic for each output using the same pinned inputs and template, writing the requested tag-named PDFs into the package delivery directory. Preserve all selected finish/image decisions and distinguish exact/representative/missing imagery. Missing renderer/source/image blocks the affected output unless the approved contract permits a labeled placeholder. Do not claim remote execution from MCP instruction retrieval.

Merge actual PDFs in the explicit expected order using host PDF tooling when combined output is requested. Preserve links and readable text. Reopen the merged output and inspect every page. Never rename HTML to PDF or return links as proof that a batch finished.

## 3. Resume and invalidate deliberately

On interruption, retain manifests, failures and individual evidence. Prepare a new revision from current source/template/audience/image inputs. Run:

```bash
python3 "<plugin-root>/tools/renderers/ffe_outputs.py" resume --previous <previous-job-revision> --job <new-job-revision> --receipt <previous-receipt.json>
```

The read-only helper identifies previously verified individual files whose item data/revision, grouping, template, audience, layout and images still match, and whose actual file hash still verifies. Copy only those reusable files into the new job; regenerate invalidated items. A corrected AP-05 invalidates its sheet. A changed template/audience invalidates every affected sheet. Combined output is rebuilt and checked. No automatic background work, retries or overwrite of issued revisions is implied.

Re-read the current authoritative revision set immediately before completion. The helper checks the input snapshot it is given; it cannot discover a newer record unless the host supplies the current read. A restored PDF is not authority to revert schedule data. Do not regenerate record identity while resuming.

## 4. Verify completeness and return

Record genuine host visual inspection against the accepted template, image outcomes, working links and audience safety for every individual/combined artifact; bind evidence to artifact and template hashes. Use `ffe_outputs.py check` with current input, contract, template and a new receipt path. Require exact expected file set, page counts and tag order. Unknown renderer capabilities, inaccessible sources or one failed item mean an incomplete package; never mark the whole job complete from successful first items.

Return the requested usable artifact links plus a summary of expected/verified/failed items, omissions (if explicitly authorized), source/template/record revisions and stale outputs. Preserve previous receipts and issued artifacts. Sending, uploading and sharing remain separately authorized host actions. Internal receipts must not be bundled for clients. The output helper checks PDF structure/text and hash-bound host evidence; only actual host inspection establishes visual fidelity and hidden-content safety.
