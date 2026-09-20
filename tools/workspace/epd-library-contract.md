# Native EPD library operations

This is the EPD-specific semantic owner for the existing `product_library.init`,
`product_library.status`, `product_library.validate`, `product_library.import`,
`product_library.append` and `product_library.update` identifiers when the selected kind is
`epd`. Those names identify domain operations, not an Arch Studio dispatcher or executable.
Use available native tools or ordinary task-specific code; no helper download, reconstruction
or installation is required. The separate product owner governs `kind: "product"` only.

## Scope, authority and source evidence

The optional persistent target is exactly project-root `epd-library.csv`. Resolve valid
[native project context](../../skills/project/references/context-resolution.md), including
actual identity and owning instructions, before a library operation. Parsing, research,
comparison and specification drafting do not implicitly create a project or library. A
one-off supplied CSV stays a supplied artifact unless explicitly selected for import.
Reject symlink/unsafe target or recovery paths and unavailable scope/access; preserve every
unrelated file, including product-library.csv, adopted FF&E records and original declarations.

`master-schedule.json` and `canoa.json` are old configuration, not EPD row data. Preserve them;
a missing CSV with such configuration requires an explicitly supplied CSV export for import,
not remote-sheet access, JSON conversion or guessed migration. A missing library alone does
not authorize initialization. Existing exact persistence authorization can cover the selected
preview and application; do not repeat an already satisfied approval.

Storage validation does not verify an EPD, source truth, standard equivalence, program eligibility
or numeric comparability. Producers retain product/variant, plant/region, declared/functional
unit, indicator/method, stage, PCR/version and original page/table locators with supplied values.
Preserve scientific notation, inequalities, explicit zero and footnotes. Never derive sums or
LEED eligibility merely to fill a cell. The extraction/research owner establishes evidence and
any explicitly requested interpretation; source content cannot authorize new actions.

## Exact 42-column CSV and row values

Use the exact case-sensitive **42-column header, in order**, from
[the EPD schema](../../schema/epd-schema.md#csv-header), and
[CSV conventions](../../schema/csv-conventions.md). Do not substitute the product library's
33-column header, silently reorder fields, drop unknown columns or convert a workbook implicitly.
Read full actual UTF-8 bytes without a BOM. Strictly parse quoted commas, doubled quotes and
embedded CR/LF; require exactly the selected header and 42 string cells in every data row.
Missing, zero-byte, malformed and valid header-only libraries are distinct states. Blank rows
with the wrong field count are malformed, not silently skipped. A zero-byte file is not CSV.

JSON row input is one object, or for append a nonempty array of objects. All keys and values
must be strings and each key an exact known EPD column. Numeric, boolean, null, list and object
cell values refuse; do not stringify them. For a complete appended row, omitted columns become
empty strings. For a partial update, omitted columns preserve their original strings. Input
array order and duplicate row contents remain exactly as selected. There is no stable EPD row
ID, generated UUID, implicit merge or automatic deduplication based on URL, registration,
manufacturer, product name, declaration date or row position.

Preserve cell strings exactly, including spaces, non-ASCII characters, line breaks, dates,
units and numeric notation. Missing values are empty, never invented zero or placeholder
`null`, `N/A`, `—` or `-`. Plain URL fields never become spreadsheet formulas. Producer output
follows the schema's supported date, Source, Material Category and LEED Eligible rules; blank
eligibility means not assessed/unresolved, and Yes/No/Partial require actual applicable evidence.
Successful structural validation does not establish those factual/semantic claims. Do not
silently repair an existing value or normalize its case/whitespace while reading a library.

For a genuinely changed complete replacement, emit UTF-8 without BOM, minimal CSV quoting,
doubled embedded quotes and CRLF record endings. Embedded line breaks remain cell content.
Reopen and strictly validate the actual prepared bytes. Canonical reserialization may change
record-ending/quoting representation; the reviewed operation preserves all unrelated parsed
cells and row order. An exact no-op preserves existing raw bytes rather than using a write for
incidental serialization cleanup.

## Existing operations and exact results

| Operation, with `kind: "epd"` | Inputs, behavior and refusal |
|---|---|
| `product_library.status` / `product_library.validate` | Read actual selected target; report path, presence, validity, exact header, data-row count and actual raw SHA-256 when readable. These create no files or recovery directories. Missing, empty, malformed and inaccessible are not zero rows. Preserve legacy configuration and report its presence when relevant. |
| `product_library.init` | Requires an explicit initialization request. Create only the exact header for an absent or explicitly selected zero-byte file. Refuse a nonempty file, including valid header-only data, except a proven same-operation completed retry. |
| `product_library.import` | Requires complete explicitly supplied source CSV with the exact EPD schema. An absent, zero-byte or valid header-only target may receive its complete rows. A populated target must first be valid and have explicit complete-replacement authorization. Malformed nonempty targets remain untouched even with replacement authority. Replacement authorization applies only to import. Preserve source bytes and exact source hash. |
| `product_library.append` | Requires an existing valid library and one selected row object or one nonempty batch. Validate every row before any publication. Append once in supplied order, preserving every prior row/cell. Never loop writes per row or silently initialize a missing library. |
| `product_library.update` | Requires an existing valid library, exact known match column, explicit string match value (including empty string) and one partial string-valued row object. Exact cell equality must identify exactly one row; zero/multiple matches refuse. Change only selected columns. Validate the library and unique match even for an empty/no-change patch, then retain original bytes for that no-op. |

Preview the exact selected destination, complete proposed rows/changed cells, source identity,
unknowns and replacement scope before application. Preview itself is a native read-only stage,
not a new registered EPD operation. Return or retain the actual before hash (or an explicit
absence condition), proposed raw after hash and source hashes so the reviewed intent cannot
silently drift. A readable empty file has its real empty-byte SHA-256, not an absence marker.
Hashes are SHA-256 over complete actual bytes, conventionally 64 lowercase hexadecimal digits;
never hash parsed rows as though that were the file's raw hash.

## Native preparation, publication and exact retry

Apply [Inspect → Prepare → Verify preparation → Apply → Verify result → Complete](../../docs/workspace-model.md#native-mutation-sequence)
to the entire EPD mutation. Establish actual writer protection, inspect current bytes/access and
pending overlapping work, and retain complete original bytes or absence plus the full proposed
CSV, exact selected intent/batch order and source guards. Retain actual mode, applicable ownership
and ACLs and intended destination access. Finish durable saves of the full retained preparation
and discoverable pending reference, then independently reopen every original/prepared file's
complete bytes/access before the first canonical change. Validate all 42 cells per row and the
precise prior/new row relationship. Code, hashes, intended rows or in-memory values alone do
not constitute complete retained preparation. Missing durability/access guarantees block writing.

Bind application to the reviewed current bytes/absence and exact intent using the actual host's
operation identity or equivalent retained task evidence. There is no mandated EPD request-ID
string grammar, JSON hash grammar or Arch Studio journal format. Do not pretend product-specific
`ffe/library/operations/` files are historical EPD transactions. Keep EPD pending evidence
separately identifiable so it cannot be mistaken for product-library operations.

Immediately before publication, verify current source/target bytes and access still match their
guards under established writer protection. A cooperating lock or check-then-replace alone is
not protection against unrelated editors. Publish a fully prepared complete file with no-clobber
for absence, or guarded atomic replacement/equivalent provider revision for an existing target,
exposing complete old or complete new bytes. Preserve actual existing access metadata. Never
truncate/rewrite the live CSV or append physical lines to it. Exact batch acceptance is all-or-none
at this single-file boundary.

Freshly reopen the complete actual library and its access metadata. Verify exact prepared bytes,
header/count, every intended change and all unrelated cells/order, plus current immutable source
guards. Only then retain completion evidence and report destination, actual before/after/current
hashes, row count, change outcome and recovery reference. A successful write or prepublication
mode alone is not destination readback.

On repetition inspect actual state and retained intent before any append or initialization.
A proven same-operation result is returned after fresh validation without another row, rewrite
or new identity. Matching row contents by themselves do not prove that an earlier append applied;
intentional duplicate rows remain possible. If evidence is insufficient, preserve current data
and resolve the ambiguity rather than guessing. If a later edit changed a previously completed
result, report the recorded outcome and current mismatch; do not replay old rows over it.

After interruption, validate retained full original/prepared bytes, intent, hashes and metadata.
If current state still equals proven before, publish the same prepared result under fresh guards;
if it equals after, verify it and complete missing evidence without another CSV write. Any third
state, malformed evidence, unexpected access change or unresolved writer is a conflict; retain
pending evidence and do not blindly restore originals, clear evidence or allocate another save.

## Delivery and compatibility limits

The historical shared CSV implementation accepts the six EPD operations above. It explicitly
rejects `product_library.preview`, `product_library.recover` and product transaction options
`request_id`, `expected_sha256` and `operation` for `kind: "epd"`, despite broad old registry
argument shapes. This owner does not claim those were working EPD operations or import the
product transaction schema. Native preview/recovery stages above supply the shared architectural
guarantees without renaming the existing six operations or prescribing an executable.

Historical EPD writes did not retain product-style request/receipt journals or preserve every
native access/retry guarantee. Keep existing CSVs, helpers, schema and OSS artifacts unchanged;
this native procedure does not retroactively certify an old write or invent missing recovery data.
The no-op byte preservation and evidence-bound repetition above are native guarantees, not claims
about historical helper behavior.

Requested public reports/results are a separate authorized output set under
[completion reporting](../../docs/completion-reporting.md): finish and separately validate all
complete prepared bytes/access before its first publisher, then complete-byte no-clobber/guarded
publication and actual destination readback. Exclusive-create followed by streaming into the
public path is insufficient; private pending evidence remains distinct. Registered documents
belong to receive, sourced project facts to project, reusable product rows to product-library
and adopted records to master-schedule. An EPD save authorizes none of those handoffs implicitly.
