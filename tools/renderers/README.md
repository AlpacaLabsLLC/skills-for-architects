# FF&E output contracts

This document specifies the FF&E output contract: inputs, design resolution, identity and
filename rules, and the verification evidence a completed PDF job requires. Hosted
product-cut-sheet and spec-book workflows follow these rules natively with the host's own
tools; they do not require an Arch Studio runner, package or dependency installation.

`ffe_outputs.py` and `document_contracts.py` are retained maintainer reference
implementations and test oracles for this contract. They prepare local data and check PDF
output; they do not render, fetch products, mutate item records or send files. The CLI
examples below describe those development interfaces, not steps a workflow must execute.
Do not retrieve or reconstruct these modules through conversation.

## Shared design resolution

Both skills reference the central [design system](../../studio/standards/documents/design-system.md), [cut-sheet template](../../studio/templates/documents/product-cut-sheet/template.md) and [book template](../../studio/templates/documents/spec-book/template.md). The resolver packages their exact text/hash/identity into portable internal job evidence. It draws no pages.

```bash
python3 tools/renderers/document_contracts.py resolve --kind spec-book --page a4 --orientation portrait --measurement-units imperial --output resolved-design.json
```

Presets: `letter`, `legal`, `tabloid`, `ansi-c`, `ansi-d`, `ansi-e`, `arch-a`, `arch-b`, `arch-c`, `arch-d`, `arch-e`, `arch-e1`, `a4`, `a3`, `a2`, `a1`, `a0`. Each supports both orientations. `--page custom --custom-width 10 --custom-height 16 --custom-units in` resolves explicit custom size (also `mm`); short edge must be at least 360 pt and long edge no more than 3600 pt. Named presets cannot be redefined through custom CLI dimensions. Displayed measurement units are independent of paper units.

Optional `--studio <registered-studio-root>` requires STUDIO.md. Optional `--project-assets <selected-project-assets-root>` explicitly selects a reference asset root. Roots mirror `standards/documents/` and `templates/documents/`. Precedence is selected project assets, configured studio assets, bundled defaults. Partial overrides fall back for unselected components, but a selected manifest's missing/incorrect declared assets fail rather than silently falling back. IDs and compatible design-system versions must remain declared; content and manifest hashes pin actual changes. Update a manifest asset hash when deliberately changing its content. The book always also resolves the shared cut-sheet template. No defaults are copied into user workspaces.

A separately supplied accepted PDF/reference is pinned by `--template`; name its rule overrides in `reference_overrides`. Required content and audience constraints still apply. The host re-resolves current dependencies before `check`; a previously saved resolution is an immutable snapshot, not proof that central assets are still current. [Resolved-design schema](../../schema/document-design.schema.json) defines the receipt shape.

## Inputs and ownership

`product-cut-sheet` owns an individual sheet job manifest/receipt; `spec-book` owns a package manifest/receipt. The owning skill applies the same contract natively. `master-schedule` owns adopted schedule/item records; outputs only consume its snapshot API. The host owns actual rendering, spreadsheet operation, visual inspection and authorized delivery.

Use the shared [completion report](../../docs/completion-reporting.md) when returning artifacts.
Preserve requested, produced and verified counts, source/check evidence, unresolved items and
actual canonical-write status. A successful preparation or supplied inspection flag does not
establish an inspected delivery, and an export does not prove a provider save.

The input is the record read API snapshot: `{schema_version:1,schedule_id,revision,hash,items:[{item_id,revision,tag,fields,provenance,decision_refs}],source}`. Adopted inputs require schedule identity, revision and hash. For one-off work, omit schedule identity, retain a source description/hash and use stable snapshot-local item IDs with revision 1. A selected subset remains explicitly scoped; pins refer to the full parent schedule revision. No snapshot is silently adopted.

A contract conforming to [template schema](../../schema/ffe-output-template.schema.json) must explicitly include:

```json
{
  "schema_version": 1,
  "mode": "adopted",
  "audience": "client",
  "allowed_fields": ["Product Name", "Manufacturer", "Model", "Finish", "Dimensions", "Source URL"],
  "template_accepted": true,
  "layout_requirements": ["Letter portrait", "Use accepted reference typography and field positions"],
  "missing_image_policy": "block",
  "combined_pdf": true,
  "front_matter_pages": 0,
  "reference_overrides": [],
  "outputs": [
    {"tag": "AP-05", "item_ids": ["item-uuid"], "expected_pages": 1,
     "images": {"item-uuid": {"path": "images/selected.png", "source": "https://manufacturer.example/product", "status": "exact"}}}
  ]
}
```

Image paths resolve relative to the input snapshot file and must stay within that source bundle. Place an `images/` folder beside the snapshot and reference `images/selected.png`. Absolute paths, parent traversal and symlinks (including ancestor directories) are rejected. Copy explicitly authorized image bytes into that bundle before preparing the job; do not widen access to make a path work. Use selected PNG/JPEG/GIF/WebP raster bytes; extract PDF imagery through host tooling first. HTML/error responses and path escapes are rejected. Exact and representative images retain source/hash; a missing-image policy of `labeled-placeholder` must be explicitly authorized and visibly labeled. The host verifies actual image identity, finish and suitability; resizing alone is not evidence. Finishes grouped into one output are explicit item ID lists. Every scoped input item must occur exactly once. Expected page counts include only agreed content; combined output includes explicitly declared `front_matter_pages` before sheets when requested (default zero), with cover/index defined by the central book template. All pages share the declared geometry; mixed-size books are unsupported.

## Product identity and filenames

Intake `selected_tags` and output `tag` use the same exact identity contract: 1–80 ASCII letters,
digits, dots, underscores or hyphens, starting with a letter or digit. A tag such as `SX.A-001`
stays exact and defaults to `SX.A-001.pdf`. Job IDs retain their separate dot-free rule. Group tags
identify the explicitly agreed output grouping; they need not equal every grouped item's tag.

Version 1 retains the historical manifest shape and derives each filename as `tag + '.pdf'`.
It now accepts the shared supported identity lengths; existing jobs are neither rewritten nor
rehashed. For an identity unsafe as a filename (for example `CON` or `A.`), or an explicit legacy
filename choice, use output contract `schema_version: 2` and set `outputs[].filename`:

```json
{"tag": "CON", "filename": "console-fixture.pdf", "item_ids": ["item-1"], "expected_pages": 1}
```

Mappings are explicit and reversible through the prepared manifest's tag/filename pairs. Each
filename requires a safe 1–80 character stem and lowercase `.pdf`; path separators, trailing-dot
stems, Windows device names (including extensions) and `combined.pdf` are reserved. All filenames,
mapped and default, are checked for case-insensitive collisions. Exact tag duplicates fail;
case-distinct identities may coexist only with distinct safe filenames. No suffix or normalized tag
is generated automatically. Separators/traversal/whitespace/Unicode are outside this bounded identity
contract, including when a filename mapping is supplied.

Version-2 preparation always pins `filename` on each render and manifest output, including default
names. Missing version-2 metadata fails; only actual version-1 manifests use the legacy fallback.
Both `check` and `resume` read the recorded version. Mapping changes invalidate the affected output;
issued files and earlier jobs remain untouched. A historical renamed tag is preserved as recorded:
do not infer its original canonical ID from the filename or invent a reverse mapping. A corrected
identity/mapping requires a new reviewed job, with intake supersession where its scope changes.

Manifest and render identities, filenames and item groupings must agree with the original ordered
contract. Updating both derived files or their render hash cannot authorize a different tag or mapping.
Resume also checks the prior receipt's output metadata against the prior manifest.

PDF identity checks require the exact bare `tag`, including dots, on the sheet. Filename text such
as `SX.A-001.pdf`, a mapped filename, or a wrong variant like `SX.A-001-wide` cannot satisfy it.
The contract does not provide an option to accept filename-only identity evidence. Visual inspection
after the final rendering and all source/audience/denied-field checks remain required.

```bash
python3 tools/renderers/ffe_outputs.py prepare --input snapshot.json --contract contract.json --template accepted.pdf --design resolved-design.json --output new-job-revision
```

The target must not exist. This writes:

```text
new-job-revision/
  internal/manifest.json   # Private controls; never send externally
  render/data.json        # Scalar allowlisted fields, explicit images
  render/assets/          # Content-addressed selected image copies
  delivery/               # Host writes only requested PDFs here
```

Do not publish or ZIP the whole job. Manifest `denied_values` are private comparison controls, not render inputs. Only `delivery/` may be considered for external delivery after inspection and authorization. Templates are not copied blindly into public outputs. Source and template files remain unchanged.

## Verification

The host must render/open **every page**, compare the accepted reference requirements, inspect imagery, follow intended links and inspect hidden text/metadata/attachments. Record honest evidence for each output, tied to current file bytes:

```json
{
  "fingerprint": "prepared-job-fingerprint",
  "artifacts": {
    "AP-05.pdf": {
      "sha256": "actual-pdf-sha256",
      "template_sha256": "accepted-template-sha256",
      "design_fingerprint": "resolved-design-fingerprint",
      "rendered_pages_inspected": true,
      "layout_matches": true,
      "images_checked": true,
      "links_checked": true,
      "audience_checked": true,
      "page_geometry_checked": true,
      "overflow_checked": true,
      "image_resolution_checked": true,
      "evidence": "project-relative path to actual page inspection evidence"
    }
  }
}
```

`combined.pdf` needs its own entry when requested. Booleans are host attestations, not permission to invent an inspection. Use [receipt schema](../../schema/ffe-output.schema.json) for consumers.

```bash
python3 tools/renderers/ffe_outputs.py check --job new-job-revision --input current-snapshot.json --contract current-contract.json --template current-template.pdf --design current-resolved-design.json --inspection inspection.json --receipt new-job-revision/internal/receipt-001.json
```

Read current records before supplying the snapshot. Source, template, contract or asset changes block stale completion. The check verifies **every** MediaBox/CropBox to within 0.1 pt of declared dimensions, with unrotated pages and UserUnit 1; other geometry blocks rather than being silently resized. It checks exact expected files, actual PDF header/end marker and successful parsing, expected page counts, tag presence/order excluding cover/index pages, render hashes, host evidence hashes and a supplemental denied-value scan of text/metadata. The scan does not prove absence of hidden objects, short values or an unsafe template; host audience inspection remains required. Receipts explicitly state this limit. An incomplete package returns exit 2 and an itemized receipt; malformed inputs or absent capability return blocked, never complete. Receipt paths must be new. No prior receipt is overwritten.

```bash
python3 tools/renderers/ffe_outputs.py resume --previous old-job-revision --job new-job-revision --receipt old-job-revision/internal/receipt-001.json
```

Resume is read-only: it compares per-output input/template/audience/layout/image fingerprints and actual previously verified file hashes. Copy only reported reusable individual PDFs into the new job, rebuild the combined PDF, and perform current checks. Changed items are invalidated; previous issued files remain intact. The manifest is trusted project-local control data, not an authenticity signature or a substitute for the record owner's integrity checks.

For other requested formats, host rendering and inspection may produce an explicitly labeled artifact, but this contract certifies only PDFs. Do not report non-PDF output as PDF-verified.
