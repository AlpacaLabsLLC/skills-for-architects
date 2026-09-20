# Adopted FF&E records

`master-schedule` owns item and schedule records. Other skills propose changes and consume pinned snapshots; they do not overwrite these records. `product-library` owns the optional reusable 33-column `product-library.csv` and guarded transaction evidence under `ffe/library/`; legacy master-schedule library requests delegate to that owner. Adoption is explicit; a one-off workbook task never adopts records silently.

## Authority and storage

- `ffe/items/<UUID>/revisions/000001.md`: immutable, globally owned item specification, tag, field evidence, decision links, actor and change reason. Retagging preserves identity. Each subsequent item revision links its predecessor hash.
- `ffe/schedules/<UUID>/revisions/000001/schedule.md`: immutable schedule membership and order, pinning project-relative item paths/revisions/hashes, source, lifecycle, approval evidence, actor and reason. Only this publication boundary makes an item revision current for that schedule. Another schedule may continue pinning an earlier item revision.
- `ffe/recovery/<schedule UUID>/<snapshot UUID>/`: immutable recovery receipt, record snapshot, validated CSV and optional native workbook backup. These are copies, not another authoritative schedule.

Markdown contains a readable title, revision, actor and reason plus one deterministic fenced JSON payload governed by `schema/ffe-record.schema.json`. Never edit canonical Markdown manually. Hashes detect accidental changes, not malicious forgery. No index establishes authority. Revision files are discovered directly and the linked item hashes checked. Approved schedule revisions require explicit evidence references; an output or selection is never inferred to be approval. Decisions remain owned by `project` and linked, not copied into another decision ledger.

## Record operations

Perform these operations natively under the [FF&E record contract](../../tools/workspace/ffe-records-contract.md) with the host's own tools; no Arch Studio runner, package or installation is required. The project root must contain `PROJECT.md`; resolve the owning project and read its instructions first. No credentials, spreadsheet engine, remote filesystem or network service is implied.

`tools/workspace/ffe_records.py` is a retained maintainer reference implementation and test oracle for that contract. The command forms below name its development interface to summarize each operation's inputs and effects; they are not steps a workflow must execute. Do not retrieve or reconstruct it through conversation.

| Operation (reference form) | Inputs / effect |
|---|---|
| `adopt --input proposal.json` | Explicit adoption. Required `name`, `actor`, `reason`, `items`; optional source object, lifecycle and approval_refs. Assigns opaque IDs to new items and schedule. |
| `read --schedule UUID [--revision N]` | Returns joined JSON snapshot with schedule ID/revision/hash, pinned item_refs and full items. Does not modify records. |
| `revise --schedule UUID --expected-revision N --input proposal.json` | Full reviewed membership, retaining IDs and observed item revisions; refuses stale schedule/item revisions. Removal additionally requires `--allow-remove`. |
| `reconcile --schedule UUID --base-revision N --input workbook.json` | Three-way field merge of the revision originally exported, current records and full host-read workbook data. Returns proposed changes, conflicts, removal IDs and current expected revision. Always review; this command never writes. |
| `snapshot --schedule UUID [--revision N] --phase pre-edit --native source.xlsx [--input extraction.json]` | Preserve a project-local native source, its checksum and tabular record snapshot. Extraction metadata contains field_mapping/extraction_gaps. Repeat with post-edit after actual host readback/reconciliation. |
| `recover --schedule UUID --snapshot UUID --destination restored.xlsx --kind native` | Copy validated recovery data into a NEW artifact. Other kinds: csv, json. Never overwrite a file or roll back canonical records. |
| `export --schedule UUID --destination schedule.csv [--revision N]` | Rebuild a new CSV view from canonical records. Existing paths refuse. |

Each item input has `tag`, `fields` (lossless JSON object), `provenance`, `decision_refs` and, after adoption, `item_id` and `revision`. Field evidence is `{status: supplied|verified|unknown|inferred, source?, retrieved_at?, note?}`. Omitted evidence becomes unknown; absent facts stay absent or null. True hyperlink targets can be fields containing `{label,url}`; a displayed label or null evaluated formula is not evidence that a URL is absent. Do not coerce these records into the optional library schema.

Consumers use the contract's read operation. Output generators pin schedule_id/revision/hash and item_id/revision, preserving issued artifacts separately. Receipts reference the exact set; a later record revision makes matching older output stale, not deleted.

## Workbook operation and recovery

Before any host workbook edit: preserve the native workbook (or a verifiable recoverable provider revision), extract its actual structured values AND formulas/true links/selected images via a capable host, and record the field mapping and gaps. The snapshot CSV reflects the pinned record; it must not be falsely labeled a complete workbook extraction. Preserve the host's extracted input separately, including disagreements, and reconcile it against the revision from which the workbook was produced. Read actual edited cells back before post-edit snapshot. A host without reliable workbook access stops the affected operation.

CSV cells use JSON encoding to retain type distinctions, nested hyperlink values, null and empty strings without formula execution; absent fields remain blank. Recovery CSV does not restore formulas/styles/images. Native backup and CSV are complementary. Rebuilding a workbook is a host operation with losses disclosed. A recovered older view cannot silently supersede current records.

## Concurrency and failure

One project writer only: an exclusive `ffe/.write-lock` serializes cooperating record operations. Stale revisions refuse before commit. A revision stages new item files and publishes the complete schedule directory atomically; ordinary exceptions remove unpublished item files. A process crash may leave the lock, staging directories or unreferenced append-only item files. Stop and inspect those against published schedule references; do not auto-delete evidence or clear a lock assumed stale. Concurrent external editors and cloud synchronization are unsupported. Historical removal cannot silently resurrect an ID; review retained history explicitly.

These record operations do not edit workbooks, infer approval, send artifacts, restore provider revisions or bypass host permissions.
