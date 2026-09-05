# FF&E output contracts

`ffe_outputs.py` is a dependency-free, local Python 3 data-preparation and package-verification helper. It does **not** render documents, fetch products, mutate item records, send files, or expose a remote filesystem. `check` additionally requires host-installed Poppler `pdfinfo` and `pdftotext`; missing tools produce a blocked result. No dependency is installed automatically.

## Inputs and ownership

`product-cut-sheet` owns an individual sheet job manifest/receipt; `spec-book` owns a package manifest/receipt. The owning skill runs the same helper. `master-schedule` owns adopted schedule/item records; outputs only consume its snapshot API. The host owns actual rendering, spreadsheet operation, visual inspection and authorized delivery.

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
  "outputs": [
    {"tag": "AP-05", "item_ids": ["item-uuid"], "expected_pages": 1,
     "images": {"item-uuid": {"path": "images/selected.png", "source": "https://manufacturer.example/product", "status": "exact"}}}
  ]
}
```

Image paths resolve relative to the input snapshot file and must stay within that source bundle. Use selected PNG/JPEG/GIF/WebP raster bytes; extract PDF imagery through host tooling first. HTML/error responses and path escapes are rejected. Exact and representative images retain source/hash; a missing-image policy of `labeled-placeholder` must be explicitly authorized and visibly labeled. The host verifies actual image identity, finish and suitability; resizing alone is not evidence. Finishes grouped into one output are explicit item ID lists. Every scoped input item must occur exactly once. Unsafe/case-colliding/reserved tags are rejected instead of silently renamed. Expected page counts include only agreed content; combined output concatenates sheets without extra front matter in this helper version.

```bash
python3 tools/renderers/ffe_outputs.py prepare --input snapshot.json --contract contract.json --template accepted.pdf --output new-job-revision
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
      "rendered_pages_inspected": true,
      "layout_matches": true,
      "images_checked": true,
      "links_checked": true,
      "audience_checked": true,
      "evidence": "project-relative path to actual page inspection evidence"
    }
  }
}
```

`combined.pdf` needs its own entry when requested. Booleans are host attestations, not permission to invent an inspection. Use [receipt schema](../../schema/ffe-output.schema.json) for consumers.

```bash
python3 tools/renderers/ffe_outputs.py check --job new-job-revision --input current-snapshot.json --contract current-contract.json --template current-template.pdf --inspection inspection.json --receipt new-job-revision/internal/receipt-001.json
```

Read current records before supplying the snapshot. Source, template, contract or asset changes block stale completion. The helper checks exact expected files, actual PDF header/end marker and successful parsing, expected page counts, tag presence/order, render hashes, host evidence hashes and a supplemental denied-value scan of text/metadata. The scan does not prove absence of hidden objects, short values or an unsafe template; host audience inspection remains required. Receipts explicitly state this limit. An incomplete package returns exit 2 and an itemized receipt; malformed inputs or absent capability return blocked, never complete. Receipt paths must be new. No prior receipt is overwritten.

```bash
python3 tools/renderers/ffe_outputs.py resume --previous old-job-revision --job new-job-revision --receipt old-job-revision/internal/receipt-001.json
```

Resume is read-only: it compares per-output input/template/audience/layout/image fingerprints and actual previously verified file hashes. Copy only reported reusable individual PDFs into the new job, rebuild the combined PDF, and perform current checks. Changed items are invalidated; previous issued files remain intact. The manifest is trusted project-local control data, not an authenticity signature or a substitute for the record owner's integrity checks.

For other requested formats, host rendering and inspection may produce an explicitly labeled artifact, but this helper certifies only PDFs. Do not report non-PDF output as PDF-verified.
