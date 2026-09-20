# Native FF&E output preparation, inspection and reuse

This owns `ffe_outputs.prepare`, `ffe_outputs.check`, `ffe_outputs.resume` and shared product/output
filename semantics for MCP delivery. The host supplies native files, image decoding, PDF rendering,
PDF inspection and authorized publication. Arch Studio supplies procedures, schemas and design
assets; no Arch Studio executable, helper reconstruction, runtime installation or universal process
capability is required. Preparation renders nothing. Receipt creation never adopts a product,
changes an item/schedule revision, issues an approval or authorizes sending.

Read [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence),
[document design resolution](document-design-contract.md), the unchanged
[output contract schema](../../schema/ffe-output-template.schema.json),
[receipt schema](../../schema/ffe-output.schema.json) and
[identity schema](../../schema/product-identity.schema.json). For adopted inputs use the
[record owner](../workspace/ffe-records-contract.md); accepted intake belongs to the
[intake owner](../transformers/ffe-intake-contract.md). Output snapshots are derived projections,
not newly signed canonical records. Rendering from a workbook never authorizes editing it.

## Native operation sequence and recovery

For preparation the affected set is the complete new job revision: `internal/manifest.json`,
`render/data.json`, all selected `render/assets/` files and required directory membership. Guard
full original source snapshot, accepted contract, current record pins, template, resolved design
and all original images. For checking the affected set is the new receipt, its bound immutable companion and separately retained
inspection evidence; guard every job member, dependency and actual delivery artifact. Resuming only
reads old/new jobs and receipts; subsequent authorized copies are new output publications with the
same safeguards. Existing issued outputs and receipts stay immutable.

Inspect pending state before allocating a revision or writing. Retain all full original bytes,
original access metadata and complete prepared bytes for the whole affected set. Finish native
durable saves, then independently reopen and validate all saved originals/prepared bytes and access
metadata **before the first publisher**. Guard current hashes/membership and all destination absence
conditions. Publish complete old-or-new file bytes with native no-clobber creation/atomic replacement
or an equivalent provider condition. Never truncate a canonical destination. A multi-file job is
recoverable as a set, not necessarily atomically visible as a set; retain a pending state until all
required destination bytes, access metadata and the full current dependency set have been freshly
read back and verified. Read actual staged bytes before publication, not just in-memory values.

Use a unique authorized project `ffe/jobs/<job-id>/<revision>/` or explicitly selected one-off task
folder. An unrelated existing destination blocks. An exact retained interrupted/replayed request
may verify already-published identical members and finish the same prepared job without allocating
new IDs or changing pins. Different scope/template/intent or unexplained mixed state requires a new
reviewed revision or precise safe refusal; no silent overwrite, rollback or timestamp regeneration.
Retain failures and prior evidence. A missing renderer/access/inspection facility blocks only the
affected required action; never call prepared JSON a completed PDF.

## Encoding and exact identity

Parse full UTF-8 JSON, rejecting duplicate keys, nonfinite numbers and invalid Unicode. Preserve
integer versus binary64, booleans, null, signed floating zero, strings and array order. Use the
compact sorted-Unicode UTF-8 logical SHA-256 grammar in
[observation encoding](../../schema/product-observations.md): `ensure_ascii=False`, no final newline.
Every equality used for current intent, pins and reuse is kind-preserving; Python's historical
`true == 1 == 1.0` equivalence cannot authorize a changed record. Stored manifest/render/receipt
JSON retains insertion order, two-space indentation, unescaped Unicode and one final LF. Raw hashes
include actual complete bytes and line endings. Existing historical files/hashes are never rewritten.

A product/output tag is exactly 1–80 ASCII letters, digits, dots, underscores or hyphens, starting
with a letter/digit. Preserve case and punctuation; no automatic normalization, suffix or reverse
identity inference. Job IDs have their separate dot-free rule. Output grouping tags need not equal
every grouped item's tag. Tags are exact-unique within ordered outputs.

Version is exact integer 1 or 2. Version 1 forbids `filename` and derives `tag + ".pdf"`. Version 2
allows an explicit filename; a safe omitted name defaults the same way, but **every prepared version-2
manifest and render output must carry its resolved filename**. A filename has a 1–80-character stem
matching the tag alphabet/start rule and lowercase `.pdf`; stem must not end in a dot. The stem's
first dot-delimited component, case-insensitive, cannot be `CON`, `PRN`, `AUX`, `NUL`, `COM1`–`COM9`
or `LPT1`–`LPT9`. `combined.pdf` is reserved. Reject case-insensitive filename collisions, including
case-distinct tags unless explicit distinct safe version-2 mappings resolve them. An unsafe tag's
derived filename requires an explicit version-2 mapping; the tag itself remains unchanged. Never
infer original IDs from historical filenames or change old manifest versions.

PDF identity is the exact bare tag, with neither adjacent character in `[A-Za-z0-9._-]`. Thus
`SX.A-001.pdf` or `SX.A-001-wide` cannot satisfy `SX.A-001`. No filename-only identity option exists.

## Prepare: validate complete input and scope

Inputs are parsed `snapshot`, accepted output `contract`, actual accepted template/reference bytes,
validated current `design` resolution and authorized new job destination. Validate the whole
contract schema plus these rules before preparing any output:

- Required mode `adopted` or `one-off`; audience `client` or `internal`; actual accepted template
  choice represented by boolean `template_accepted: true`; explicit boolean `combined_pdf`.
- Nonempty unique `allowed_fields` strings; nonempty `layout_requirements` of nonblank strings;
  optional `reference_overrides` is an array of nonblank strings naming accepted overrides.
  Preserve literal text. Missing-image policy is `block` or explicitly authorized `labeled-placeholder`.
- `front_matter_pages` defaults to 0 and is an exact nonnegative integer. Nonzero requires combined
  output and a `spec-book` design. Multiple output groups or any combined output require that design.
- Nonempty snapshot `items`, with exact-unique nonempty string `item_id`, exact positive integer
  `revision` and object `fields`. Preserve all original fields/provenance/decision references in
  private source evidence. Adopted snapshots require nonempty `schedule_id`, positive integer
  schedule `revision` and lowercase 64-hex `hash`; verify them with the record owner's full current
  read and membership. One-off IDs are stable snapshot-local IDs with exact positive snapshot revisions, not adopted UUIDs.
  Both modes require nonempty object/string `source`; absence is not manufactured provenance.
- Output group has only `tag`, nonempty unique `item_ids`, positive integer `expected_pages`, optional
  `images`, and version-2 optional `filename`. Each item ID must occur in the selected snapshot.
  Across all groups every selected item occurs **exactly once**. Preserve group and item order.
  `images` is an object whose keys are only IDs in that group; the whole mapping may be empty `{}`. Empty/malformed per-item image objects are
  not valid declared images; represent absence by omitting the mapping.

For intake-backed jobs verify the accepted immutable input manifest's hash, source statuses/hashes,
selected tags/template and adopted basis using its owner. Retain the untouched record read/source
extraction and its raw hash. Derive only the accepted subset, preserving full parent schedule pins
and item IDs/revisions. Put accepted input hash, source references/status, selected tags and original
record source in the projection's source evidence. Product-versus-finish grouping is explicit.
Unavailable requested items remain unresolved in the scope ledger; do not shrink the denominator.

Only allowlisted scalar field values (`null`, string, finite number or boolean) enter render rows,
in allowlist order for keys present in the item. Nested values need an explicit lossless source-to-
display mapping retained privately. In particular a structured hyperlink keeps separate label and
true URL fields; printed URL-looking text does not replace an actual inspected PDF annotation.
Never mutate adopted records to satisfy a renderer.

Private `denied_values` preserve, in group/item/original field order, historical textual forms of
non-allowlisted string/integer/binary64/boolean values whose string representation is nonblank.
Booleans render as historical `True`/`False`, numbers use their historical string grammar, not JSON
lowercase booleans. Null and nested objects are not included in this supplemental list. This list
is private comparison material, never a renderer input or proof of complete privacy protection.

## Prepare: image provenance and exact saved structures

A declared image is exactly `{path, source, status}`, with nonempty string source and status `exact`
or `representative`. Its path is relative to the original snapshot bundle; reject absolute paths,
parent traversal, escapes and symlinks at any component. Require authorized complete regular bytes.
Supported raster signatures are PNG, JPEG, GIF87a/GIF89a and RIFF with WEBP marker; the host must
also decode/inspect the actual image, dimensions and suitability, refusing HTML/error/corrupt images.
Use native tooling to extract a PDF image first when authorized. Preserve image choice, finish,
source and raw hash; a generated image cannot establish product evidence.

A copied asset name is its lowercase raw SHA-256 plus original file suffix lowercased, preserving
historical naming. Deduplicate only identical content-addressed names; copy exact selected bytes
into `render/assets/`. A row image is `{path: "assets/<name>", sha256, status, source}`; representative
images add exact label `Representative product image`. Missing mappings require authorized
placeholder policy and produce `{status: "missing", label: "Product image unavailable"}`. Never
silently substitute representative imagery for an exact selection.

Saved structures and fingerprints are unchanged:

1. Each render row is `{item_id, revision, fields, image}`. Each render group is `{tag, items}` plus
   version-2 resolved `filename`. `render/data.json` is `{schema_version, audience, outputs}`.
2. Each manifest output is `{fingerprint, tag, items, expected_pages}` plus version-2 `filename`.
   Its `items` are ordered `{item_id, revision}` pins. Its fingerprint hashes this exact logical
   object: `{rows: <render rows>, design: <design fingerprint>, source: <snapshot source>,
   schedule_id: <snapshot schedule_id or null>, evidence: <ordered original item provenance or {}>,
   group: <original accepted group including only originally present optional fields>,
   template: <raw template SHA-256>, audience: <contract audience>, fields: <allowed_fields>,
   layout: <layout_requirements>}`. Do not insert omitted contract defaults before hashing.
3. Whole job `fingerprint` hashes `{snapshot: <whole supplied derived snapshot>, contract: <whole
   accepted contract>, design: <design fingerprint>, template_sha256: <raw template hash>,
   assets: <sorted content-addressed asset names>}`.
4. `internal/manifest.json` is exactly `{schema_version, fingerprint, mode, audience, design,
   source_sha256, schedule, template_sha256, contract, outputs, denied_values, status, render_sha256}`.
   `source_sha256` is logical snapshot hash. `schedule` retains only present snapshot `schedule_id`,
   `revision`, `hash`. `status` is `prepared`; `render_sha256` is the raw saved render/data.json hash.
   Design and contract retain complete exact values, including accepted optional-field presence.

The new job has `internal/`, `render/`, `render/assets/`, `delivery/`. Preparation leaves delivery
empty; the native renderer subsequently creates only requested PDFs there. Keep source/template,
raw record reads, private controls and denied values outside delivery. Never ZIP or share a whole
job as the client deliverable. Report prepared status/fingerprint/manifest and
`workflowCompleted: false`; no PDF exists merely because preparation passed.

## Check: current dependencies, bindings and actual PDFs

Re-resolve current design assets and current adopted records/intake/source evidence; rebuild the
same derived projection and explicit mapping. Compare complete kind-preserving design and contract,
logical snapshot hash, raw accepted template hash, every copied **and current selected original**
image hash, exact render raw hash and all pinned identities. Changed source/scope/mapping/template/
audience/image/record revisions invalidate current completion and require a new prepared revision.
Do not treat a previously saved current-read file as a fresh canonical read.

Validate every manifest/render/accepted-contract version and ordered `(tag, filename)` pair. Both
manifest and render item ID lists must exactly equal each original group `item_ids` in order;
manifest expected pages must match. Recompute preparation fingerprints from retained accepted inputs
and source evidence. Updating two derived files or their hashes cannot authorize a new identity,
filename or group. Require all recorded file paths to stay in their authorized real directories.

The delivery directory must contain the **exact** resolved individual filenames, plus `combined.pdf`
only if requested; extra files/directories/symlinks are failures. Each file must have complete `%PDF-`
bytes, an `%%EOF` marker within the last 2048 bytes, and successful actual PDF parsing. Encrypted,
malformed or unreadable PDFs cannot be verified. Use available native PDF facilities with equivalent
capability; no specific package or executable is mandated.

For every page inspect actual MediaBox and CropBox: each coordinate must be within 0.1 point of
`[0, 0, design.page.width_pt, design.page.height_pt]`, rotation 0 and UserUnit 1 (default1 if absent).
Record actual media width/height. Individual page count equals declared expected_pages. Combined
count is sum of those counts plus declared front matter. Mixed size, rotated or silently resized
pages fail. Actual every-page rendered visual inspection must verify layout, typography, clipping,
image quality/resolution, 100% print geometry and accepted reference rules after the final render.

Each actual artifact must have hash-bound inspection evidence carrying its actual raw `sha256`,
current `template_sha256`, current `design_fingerprint` and a nonblank authorized evidence reference.
The reference resolves to preserved actual inspection evidence, not an asserted pathname. Required
true flags are `rendered_pages_inspected`, `layout_matches`, `images_checked`, `links_checked`,
`audience_checked`, `page_geometry_checked`, `overflow_checked`, `image_resolution_checked`.
Every flag requires the host to have actually performed that check. Combined output needs its own
entry. Inspection top-level `fingerprint` equals the prepared job fingerprint.

Inspect exact hyperlink annotation targets against source bindings, cover/index destinations and
page numbering. Inspect hidden text/layers, metadata, attachments and embedded images against the
audience restrictions; an allowlist or plain-text scan alone does not prove privacy safety. Unknown
facts permitted by the explicit artifact scope remain labeled unknown; this is no universal product
truth or legal-compliance gate.

Retain these supplemental mechanical guards, distinct from actual visual/source inspection:

- Extract full PDF text plus metadata. Collapse whitespace for denied-value search. Build visible
  values from all projected scalar fields using historical textual forms and whitespace collapse.
  A non-allowlisted normalized value of length at least four, unless equal to a visible normalized
  value, must not occur in normalized text/metadata. Short values, identical visible values, hidden
  objects and unsafe templates remain limitations requiring host inspection; do not claim scan
  completeness. Preserve case-sensitive matching.
- Required representative/missing image labels must occur in whitespace-normalized text for every
  relevant row. Actual image/source/finish suitability also requires inspection.
- Individual PDF contains its exact bare tag. Combined PDF contains each exact tag in declared order
  using its first text occurrence **after** the declared front-matter pages; front matter cannot
  satisfy identity. Per-page grouping/content/link checks supplement this text-order guard.

Malformed/current-pin failures block verification without a completed receipt. For inspectable
packages, retain each precise missing-file/extra-file/geometry/identity/inspection failure and any
artifacts actually verified; one valid item never establishes package completion. Do not suppress
other required failures after the first successful artifact.

## Native receipt and publication

Publish a new immutable [schema-conforming receipt](../../schema/ffe-output.schema.json) only after
actual prepared receipt bytes have been reopened/validated and custody checks above pass. It has
exactly the schema's top-level members: `schema_version`, `fingerprint`, `schedule`, `outputs`,
`template_sha256`, `audience`, `verified_artifacts`, `failures`, `status`, `workflowCompleted`,
`verification`, `design`. Copy unchanged pins/output metadata from the validated manifest.
`design` carries `{fingerprint, identities, page, layout}`. Each actually verified artifact is
`{file, sha256, pages, page_boxes}`; each page-box entry records `{page, width_pt, height_pt,
rotation: 0, user_unit: 1}` in physical page order.

`status: "complete"`, `workflowCompleted: true` and empty failures require **all** applicable
requested workflow checks above, including real visual/link/privacy inspection and actual complete
publication/access readback. A mechanically valid PDF or supplied flag alone is insufficient.
`status: "incomplete"`, `workflowCompleted: false` carries at least one precise required failure.
For the completion receipt itself, first verify actual dependency/artifact full set, stage and
validate receipt bytes, publish, then freshly reread the actual receipt bytes/access and entire
required set before returning a completed response. Retained pending state prevents an interrupted
receipt publication from being treated as acknowledged completion.

Retain source SHA-256, mechanical result, source-fact status, unresolved specification details,
actual visual inspection provenance/limits and all source/code/tool evidence in the immutable private
companion defined by [native output evidence binding](../transformers/evidence-contracts.md#native-output-evidence-binding).
Its required members are exact integer `schema_version: 1`, `kind: "native-ffe-output-evidence"`,
`fingerprint`, `receipt_path`, `receipt_sha256`, `source_sha256`, `mechanical_status`,
`source_fact_status`, `source_facts_independently_verified`, `unresolved_specifications`,
`visual_inspection` and `evidence`; retain additional actual task evidence. Follow the complete field
types, relative-path/actual-raw-hash rules and evidence-reference verification at that owner.
Prepare complete receipt bytes first, hash them, then prepare the companion binding that raw receipt
hash and fingerprint. Receipt verification prose names the companion path but never hashes it,
avoiding a hash cycle. Reopen and validate **both** full prepared files and access as one set before
publishing either; publish receipt then companion, then freshly read back both actual files,
referenced evidence, artifacts and access before completion. A receipt alone after interruption
remains pending, not a completed native workflow. `verification` names that evidence and accurately describes native PDF parsing
plus actual host visual/link/audience inspection, with any remaining limitations. This deliberately
corrects the old helper/schema contradiction: old helper receipts always set workflowCompleted false
and added schema-forbidden top-level fields. Do not rewrite those historical receipts or change the
schema; interpret them as historical evidence with their recorded limitations, never as a new native
completion certificate. No independent source-fact verification is inferred from output generation.

Before returning each link, use native `delivery_coverage.verify-links` from
[evidence contracts](../transformers/evidence-contracts.md) with actual artifact/receipt paths, explicit job-relative `companion_evidence`, actual raw
`companion_sha256` and current expected item/revision/source/template hashes. Return exact requested links, expected/
accounted/verified/unresolved counts and actual revisions/image status. Registration/placement
belongs to the document owner under existing authorization; external send/upload/sharing remains
a separately authorized host action. Receipt creation does not issue or approve the underlying work. For a separately requested non-PDF
format, native rendering and appropriate inspection may produce an explicitly labeled artifact,
but these PDF receipt/geometry checks do not certify it. Do not call non-PDF output PDF-verified.

## Resume: bounded read-only reuse plan

Read full old/new manifests and render data, validate their contract/version/ordered filename/group
bindings as above and verify their retained current inputs. Prior receipt fingerprint must equal
old manifest fingerprint; prior receipt `outputs` must exactly equal old manifest outputs, with
kind-preserving equality. Preserve historical receipt bytes; a prior partially successful receipt
can identify individually verified files without becoming a complete package. Reject ambiguous or
malformed duplicate verified-artifact entries rather than choosing an arbitrary occurrence.

In new output order, a prior individual is reusable only when exact tag resolves to the same exact
filename, old/new per-output fingerprints match, a prior verified_artifacts entry identifies that
filename and the actual prior regular file's raw hash still equals the recorded hash. All other
new filenames are invalidated. Missing/changed old files invalidate those items; they do not justify
record rollback. Combined PDF is always rebuilt and fully reverified. A prior receipt's metadata
must not authorize changed grouping or naming by itself.

Return `{status: "resume-plan", workflowCompleted: false, reusable: [{file, sha256}],
invalidated: [<filenames>], combined: "rebuild and reverify", instruction: <bounded copy/current
inspection instruction>}` without mutating any job. If authorized, copy only reported reusable exact
bytes into the new job with retained full preparation and actual destination byte/access readback;
then inspect/check the new complete package from fresh dependencies. Keep prior issued files and
receipts untouched. Resume does not recreate IDs, assume approval, silently retry delivery or run
in the background.
