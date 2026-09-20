# CSV Library Conventions

Arch Studio stores persistent product data in project-local CSV files:

- `product-library.csv` uses the exact 33-column header in [product-schema.md](product-schema.md).
- `epd-library.csv` uses the exact 42-column header in [epd-schema.md](epd-schema.md) and is optional.

## File contract

- UTF-8 without a byte-order mark (BOM).
- One header row followed by zero or more data rows.
- Exact, case-sensitive header names and deterministic column order.
- RFC 4180-compatible quoting. Fields containing commas, double quotes, CR, or LF are quoted; embedded double quotes are doubled.
- CRLF record endings for deterministic writes. Embedded newlines remain part of quoted fields.
- Empty fields represent unavailable values. Do not write `null`, `N/A`, `—`, or `-` as placeholders.
- URL fields contain plain URLs, never spreadsheet formulas.

## Project boundary

Resolve the canonical project through [native context resolution](../skills/project/references/context-resolution.md), including supported identity and actual project instructions. A filename alone does not establish valid context. Store a selected persistent library at that project root; one-off supplied CSV work does not initialize or adopt a library.

## Safe mutation

Before any mutation:

1. Decode as UTF-8 without accepting a BOM.
2. parse the entire CSV in strict mode;
3. verify the exact header and every row's field count;
4. construct and validate the complete replacement in memory;
5. preview material changes and use the repository's single confirmation gate when user approval is required;
6. apply the owning operation's verified native publication contract, preserving complete old/new visibility and actual access metadata, then reread the entire result.

If decoding, parsing, or validation fails, leave the target byte-for-byte unchanged. Product-library
owns product mutations through its [native semantic contract](../tools/workspace/product-library-contract.md):
read-only preview, exact expected hash, stable request identity and the complete shared
[native mutation sequence](../docs/workspace-model.md#native-mutation-sequence). Durably retain and
independently reopen all original/prepared evidence before first publication. Resolve pending work,
prevent silent stale overwrite and recognize exact retries without duplicate rows. A cooperating lock
or check-then-replace alone does not protect against external writers. If the selected method cannot
meet the actual writer/access boundary, preserve current state and report the specific limitation.
Only finish after full actual byte/schema/access readback.

Historical `ffe/library/` operation files remain readable product recovery evidence; no helper is
needed to interpret their declared intent, bytes and hashes. EPD operations use the distinct
[native EPD owner](../tools/workspace/epd-library-contract.md), exact 42-column schema and retained
native intent/evidence; they do not inherit product request grammars, row identities or journals.
Native EPD preview/recovery are procedure stages, not previously supported runner operations.
Parsing/research need no persistence; only an explicitly selected save invokes library mutation.
Existing helpers and schemas remain historical compatibility assets. OSS allocation/delivery is
separately deferred; no implicit EPD conversion or product ownership transfer is authorized.

## Legacy configuration

`master-schedule.json` and `canoa.json` are evidence of an older cloud configuration, not local row data. Preserve them byte-for-byte. If no CSV exists, ask the user to export the former sheet as CSV and explicitly import that file. Never contact a remote sheet or claim its rows were migrated from JSON.
