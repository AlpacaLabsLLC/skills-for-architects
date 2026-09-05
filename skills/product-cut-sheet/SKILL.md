---
name: product-cut-sheet
description: Produce one FF&E product cut sheet from a pinned item or explicit input snapshot using an accepted template. Use for a product sheet or a tag-named specification PDF; use spec-book for a complete package.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
---

# /as:product-cut-sheet — Produce a Product Sheet

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

Produce one selected product sheet, or an explicitly agreed product/finish grouping. Input: pinned item revision(s) or a one-off source snapshot, accepted template, exact tag, audience and image evidence. Output: an actual requested-format artifact and hash-bound receipt. This skill owns individual sheet job manifests and receipts; `/as:spec-book` owns package receipts. Neither owns item specifications or project decisions.

## 1. Resolve context and inputs

Resolve the nearest valid `PROJECT.md` using `/as:project` context resolution. Read its instructions. If unresolved, select a registered project through `/as:studio`; never create one implicitly or write into the plugin. Discover canonical records independently of indexes; preserve malformed records and report their path/problem. Project facts and decisions stay owned by `/as:project`; schedule adoption and revisions stay owned by `/as:master-schedule`.

Use existing task authorization. Ask once only for an unresolved material choice, covering exact target, audience and side effects in one gate; do not re-ask accepted scope/template choices. Read the supplied source before writing. Do not infer approval, price, availability or configuration from a generated sheet.

For **adopted** schedules, read the exact schedule snapshot through `python3 "<plugin-root>/tools/workspace/ffe_records.py" read --project <project-root> --schedule <schedule-id>`. Pin schedule ID/revision/hash and item ID/revision. Select the requested item(s) without changing their identity. For **one-off** work, preserve a source-identified input snapshot with stable local item IDs and positive snapshot revisions; explicitly record that no schedule adoption occurred. Never convert a workbook into authoritative records implicitly. Workbook editing/reconciliation belongs to the host and `/as:master-schedule`, not this output skill.

## 2. Bind template, audience and images

Resolve the centrally owned [document design system](../../studio/standards/documents/design-system.md) and [cut-sheet template](../../studio/templates/documents/product-cut-sheet/template.md). Layout/type rules live there, not in this skill. Use `document_contracts.py resolve` from the shared [output contracts](../../tools/renderers/README.md): explicitly selected project/job assets first, configured studio assets next, bundled assets last. A supplied accepted reference takes precedence for its declared rules; record `reference_overrides` and its hash rather than silently replacing it. Missing assets or incompatible dependencies block the affected output.

Resolve the requested physical preset/custom dimensions, portrait/landscape and displayed measurement units separately. Pin design/template IDs, versions, asset hashes, page dimensions, margins, content area and layout version in `resolved-design.json`. Pass it as `--design` to preparation and verification. Re-resolve current dependencies before verification; retain earlier resolved bytes. The host follows size-aware grid/type/overflow rules and inspects every actual page, image resolution and 100% print geometry. Do not scale a Letter layout to a board, substitute a nearby paper size, or imply product images have drawing scale. Unsupported combinations are explicit blockers.


Inspect the supplied template using the host's PDF/document capability. Record its hash and concrete page size, field order, typography, spacing, image placement and footer requirements. Preserve the accepted design; use a default only if no template was supplied and the task permits it. A template with an image placeholder is layout evidence, not proof of image completion.

Use [output contracts](../../tools/renderers/README.md) and [template contract](../../schema/ffe-output-template.schema.json). Set an explicit audience field allowlist; never feed excluded net prices, internal notes or full source records to a client renderer. Client output also requires inspection of metadata, attachments, hidden text, links and embedded images. An allowlist of fields alone cannot make an unsafe template safe.

Retain selected image/finish choices. `/as:product-image-processor` handles image preparation. Exact images, representative family imagery and missing images must remain distinct and sourced. A missing image blocks completion unless the user already authorized a labeled placeholder. Never substitute a generated image as product evidence. Image processing does not change the selection record.

Preserve exact requested tags. Unsafe filenames require a resolved naming choice, never silent normalization. Use a unique project-local `ffe/jobs/<job-id>/<revision>/` directory so `AP-05.pdf` does not overwrite another job or issued revision. Persist project-relative references. No cloud credentials or connector setup is part of this procedure.

## 3. Prepare and render

Create the explicit single-output contract and input snapshot, then run:

```bash
python3 "<plugin-root>/tools/renderers/ffe_outputs.py" prepare --input <snapshot.json> --contract <contract.json> --template <accepted-reference-or-template> --design <resolved-design.json> --output <new-job-revision>
```

The helper writes private controls under `internal/`, allowlisted data under `render/`, and an empty `delivery/`. It does not generate a PDF. Keep controls outside deliverables; use only projected data in the host renderer. Never copy the whole job folder into an external package.

Use the host's document/PDF skill and renderer to create `delivery/<exact-tag>.pdf` (or the explicitly requested format). Open and inspect every rendered page against the accepted reference. A saved HTML intermediate remains HTML; a download link or successful tool invocation is not a completed PDF. If rendering or source access is missing, retain the prepared work and state the exact missing capability. Hosted MCP context retrieval does not provide local filesystem or rendering access.

## 4. Verify and return

Read back current item/source, template, audience and image revisions; changes require a new prepared revision. Write the hash-bound host inspection evidence described in the output contract, including actual layout/image/link/audience, physical page size, clipping/overflow and image-resolution inspection. Run the helper's `check` command with the current input, contract and template. It checks actual PDF bytes, parseability, page counts, tags, denied-field leakage, hashes and evidence references. It cannot independently judge layout or hidden objects; the host must actually inspect those.

Preserve failed outputs and earlier receipts. Report `complete` only if the requested artifact exists, has been reopened/inspected, and all required checks pass. Otherwise report the affected item and precise blocker. Return a usable local artifact link, source/template/item revision references, image status and receipt; no external sending/upload without authorization. Corrections route to `/as:product-audit` or record owner, then produce a new output revision. A restored artifact never rolls back authoritative records.
