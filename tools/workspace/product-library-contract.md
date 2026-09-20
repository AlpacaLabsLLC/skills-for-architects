# Native product-library operations

This is the semantic owner for `product_library.*` in the MCP successor. The host selects native
tools or ordinary task-specific code; operation IDs are scope names, not an Arch Studio dispatcher. No
Arch Studio executable, installed helper, bridge or prescribed journal engine is required.

## Boundary and data

Product-library owns the optional project-root `product-library.csv` and its operation evidence.
Resolve canonical context using the [workspace model](../../docs/workspace-model.md) and read the
project's actual instructions. A one-off workbook or supplied CSV is not automatically this library.
Do not initialize a project or a library merely to answer a read-only or parse-only request.
Reject symlinked library/recovery targets, unsafe paths and invalid context. Preserve unrelated files,
including old `master-schedule.json` and `canoa.json`; they are configuration, not recoverable rows.
A missing library with only old configuration needs an explicitly supplied CSV export, not a remote
connection, JSON converter or guessed migration.

Use the exact, case-sensitive **33 columns in order** from the authoritative
[product header and field schema](../../schema/product-schema.md#csv-header), with the
[CSV conventions](../../schema/csv-conventions.md). The optional `epd-library.csv` has a different
[42-column EPD schema](../../schema/epd-schema.md). It is not owned or mutated by these operations;
route an explicit EPD request to its [distinct native owner](epd-library-contract.md). Never reinterpret an EPD header as a product header,
truncate its columns or adopt EPD-specific fields into a product row.

Read complete actual UTF-8 bytes; reject BOM, undecodable text, invalid CSV quoting, a missing,
reordered, extra or duplicate header column, and any data row with other than 33 string cells.
A zero-byte file is invalid CSV; distinguish it from missing and a valid header-only file. Strict
CSV parsing supports commas, quotes and embedded CR/LF inside fields. Preserve parsed cell strings
and row order exactly, including whitespace and explicit zero. Missing information is blank, not
null or a fabricated placeholder. Library storage does not coerce dates, numbers, units, prices,
URLs, currency, categories or product identity. Supplied facts remain subject to the product schema
and their evidence; successful storage validation does not verify the facts or silently repair them.

For an actual changed replacement, serialize the exact header and complete resulting rows as
UTF-8 without BOM, minimal CSV quoting, doubled embedded quotes and CRLF record endings. Reopen and
strictly validate those actual prepared bytes before publication. This canonical serialization may
normalize record endings/quoting; the reviewed change preserves all unrelated cell values and row
order. A no-op retains existing bytes instead of performing incidental serialization cleanup.

## Inspect and preview

`product_library.status` and `product_library.validate` read the current target and report its path,
presence, validity, exact header, row count and actual SHA-256 when readable. Missing, zero-byte,
malformed and valid header-only states are distinct. Report unreadable/malformed data and preserve
it; do not present failure as zero rows. These operations create no library or operation directory.

`product_library.preview` takes the selected operation (`init`, `import`, `append`, `update`), exact
selected rows/changes or source, match fields when updating, and explicit replacement authorization
when importing. Read current bytes and compute the full proposal by the rules below. Return target,
operation, `before_sha256` (64 lowercase hex, or literal `missing` for absence), `after_sha256`, exact
header and complete resulting rows, plus a reviewable changed-cell/row summary. Preserve source
bytes/hash for imported proposals. Preview is read-only and `persisted: false`; it does not allocate
an operation record or authorize publication. A readable zero-byte file has its real empty-byte
SHA-256, never `missing`. Unavailable source or invalid proposal stops preview.

## Selected transformations

| Operation | Inputs, exact result and refusal |
|---|---|
| `product_library.init` | Explicit selected target; create only the exact header at an absent or explicitly selected zero-byte library. Refuse every nonempty target, including a valid header-only CSV, unless this is a verified retry of the same applied operation. No data conversion. |
| `product_library.import` | Complete source CSV bytes must validate against the 33-column schema. Retain exact source/hash. An absent, zero-byte or valid header-only target may receive the complete imported rows. A populated existing library must first be fully valid and have explicit authorization to replace its complete contents; otherwise refuse. Malformed nonempty targets remain untouched even with replacement authority. Replacement authorization applies only to import. |
| `product_library.append` | Require an existing valid library and one object or one nonempty array of objects. Every key and value must be a string and every key a known column. Missing columns become blank. Append the selected rows once in their supplied order, preserving every prior row/cell. Do not deduplicate by guessed SKU, URL or row-position identity; intentional distinct saves require their own operation identity. |
| `product_library.update` | Require an existing valid library, a known match column, an exact string match value (including an explicitly selected empty string), and one partial object of known string-valued columns. Match by exact cell equality; zero or multiple matching rows refuse without writes. Change only supplied columns in that one row. Omitted fields retain their exact values. An empty change object is a no-op only after validating the library and unique match; preserve original bytes. |

Preserve populated selections, Tags, Notes, user overrides and every unrelated field unless the
reviewed request explicitly changes them. Correction of a uniquely identified existing product uses
update; ambiguity needs explicit resolution. Never infer stable identity from row position. For a
reviewed multi-row cleanup, prepare one complete import with explicit replacement authority rather
than a per-row write loop. Batch append validates every input row before any publication. Do not
infer schedule adoption, quoted/specified status, quantity, pricing approval or verification from a save.

## Preview binding and native publication

Use the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence):
**Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Its actual access,
writer-protection, durable full-set readback and completion guarantees apply here. The affected
canonical file is `product-library.csv`; imported source files are immutable read guards. Retain
complete original/absence and complete prepared CSV plus actual mode, applicable ownership/ACLs,
source guards, exact intent and discoverable pending state before the first canonical change.
Close/synchronize and independently reread all retained content and validate the prepared CSV before
calling a publisher. Merely saving evidence, checking an in-memory row or writing a checksum is not
verification. Unknown access preservation or inadequate writer protection stops before mutation.

Bind each intended write to a stable request ID of 1–80 ASCII characters, first alphanumeric and
remaining alphanumeric/underscore/hyphen, the exact operation, selected row/change data, import
source hash, match column/value, explicit replacement choice and expected preview `before_sha256`.
This ID identifies the operation, not the product. Reusing it with different intent or preview state
is a conflict. Retain the original identity/preparation across retries; do not generate a replacement
ID merely because a response was lost. A new intentional append is a separate request.

Inspect prior pending operations before a new overlapping write. Malformed/checksum-inconsistent
evidence is a blocker. A distinct unresolved operation blocks this mutation until reconciled. The
expected missing condition must remain absent through native no-clobber publication; a real hash
must match current bytes under the demonstrated writer boundary. Do not replace a stale preview
hash with a newer one to force success: reread and reconcile the reviewed request. Cooperating locks
alone do not cover external editors; check-then-rename is not atomic compare-and-swap. A controlled
exclusive workspace may use a recorded recoverable sequence; otherwise report the missing guarantee.

Publish only a verified complete replacement with complete old/new visibility. Preserve existing
mode, applicable ownership and ACLs; a source copy must not widen effective access. Reopen the actual
library and validate complete bytes, header, rows, selected changes and preserved unrelated values
against the retained proposal. Read back access metadata. Only then mark the operation complete and
report request ID, target, before/after/current hashes, actual outcome and recovery reference.

## Repetition and recovery

An exact completed retry verifies retained intent, artifacts and completion evidence. If current
bytes equal its recorded result, return the existing result with no duplicate append or extra
canonical mutation. If later edits changed the library, report the original operation's recorded
completion and `current_matches_result: false`, with current hash; preserve those later bytes rather
than replaying the old action. A receipt alone cannot establish successful current state.

`product_library.recover` takes the exact project and existing request ID. Validate retained intent,
full original/absence and prepared bytes, checksums, schema and access metadata before considering
recovery. If current bytes still equal the proven before state, publish the same prepared result
under fresh guards. If they already equal after, verify it and finish missing completion evidence
without another write. Any third state, unexpected identity/access drift, corrupt evidence or
unavailable guarantee is a conflict: preserve current data and leave pending state explicit.
Do not blindly restore `before.csv`, delete locks, clear stale-looking state or allocate another ID.

### Existing operation evidence

Existing `ffe/library/operations/<request-id>/` records remain native-readable evidence. A historical
`request.json` has exactly `schema_version` (1), `request_id`, `request_sha256`, `request`,
`before_sha256` and `after_sha256`; its request ID must equal its directory name. The `request` object
contains exactly `operation`, `row`, `source_sha256`, `match_column`, `match_value`, `replace_existing`
and `expected_sha256`. Operation is one of init/import/append/update; validate its row/change and
match inputs against the selected transformation above. Unused optional values may be null; any
provided source hash is 64 lowercase hex, match fields are strings or null, replacement is boolean,
and expected state is a lowercase SHA-256 or `missing`. Unknown fields or fingerprint-valid malformed
intent remain a blocker. The fingerprint is SHA-256 of that request serialized as UTF-8 JSON with recursively
sorted keys, two-space indentation, literal non-ASCII characters, JSON nonfinite values disallowed,
and one final LF. Read a recorded `before.csv` unless before is `missing`, and always read `after.csv`;
their raw byte hashes must equal the request and after must pass full product CSV validation.

A historical `receipt.json`, when present, has exactly `schema_version: 1`, `request_id`,
`request_sha256`, `before_sha256`, `after_sha256`, `target: "product-library.csv"`,
`status: "committed"` and `readback_verified: true`, matching the validated request. Missing receipt
means pending, not failure or permission to repeat an allocation; malformed receipt/artifacts block
recovery. The receipt is historical completion evidence, not proof that the current CSV still equals
its result. An unpublished `.staging-*` directory is retained crash evidence, not proof that the CSV
changed. Do not execute a historical helper to interpret these records.

A native host revision/recovery facility may carry equivalent evidence without that directory or a
mandatory Arch Studio journal format. Conflicting operations must still discover historical and current
pending state. These format details preserve existing evidence; they do not prescribe a new runtime.

Requested durable authored reports use receive-owned `documents.resolve/register/query` semantics
and the shared document/register publication set. Library rows themselves are not registered
adopted schedules, and this optional report handoff never authorizes changes to item/schedule owners.
