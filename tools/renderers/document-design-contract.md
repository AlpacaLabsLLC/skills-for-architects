# Native document design resolution

This owns `document_contracts.resolve` for MCP delivery. The host uses available native file and
JSON tools; Arch Studio supplies this procedure, schemas and authored design assets. No installed
Arch Studio runner, executable, copied helper source or universal process capability is required.
Resolution selects and validates design data; it renders no pages and does not complete a document.
The [output owner](ffe-output-contract.md) consumes its result.

## Scope, encoding and custody

Inputs are explicit `kind` (`product-cut-sheet` or `spec-book`), physical `page` preset or `custom`,
`orientation` (`portrait` or `landscape`), displayed `measurement_units` (`metric` or `imperial`),
optional custom width/height/units, optional selected project asset root and configured studio root,
and an authorized new result destination. One-off resolution needs no project creation. Resolve
project context only when its records or selected assets are needed.

Use [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence) for a saved
resolution. Inspect pending state and retain full original selected manifests/assets and prepared
result; finish durable saves and separately reopen and validate all retained bytes and access
metadata before the first publisher. Guard current asset membership/hashes and destination absence.
Publish the complete result without clobbering another file. Reopen actual destination bytes and
access metadata and recheck the full selected asset set before completion. An exact retained retry
verifies and returns the same resolution; changed selected assets or intent require a new result.
Do not regenerate or overwrite historical resolutions.

Parse UTF-8 JSON losslessly: reject duplicate object keys, nonfinite numbers and invalid Unicode.
Use exact integer-kind versions and column counts; booleans are not numbers. Logical fingerprints
use SHA-256 over compact UTF-8 JSON, sorted Unicode scalar object keys, `ensure_ascii=False`, no final
newline, and the number/string grammar in [observation encoding](../../schema/product-observations.md).
Keep integer versus binary64, signed floating zero and exact string values. Stored result bytes
are UTF-8, two-space indented JSON, unescaped Unicode and one LF. Raw asset SHA-256 hashes include
all original bytes. Do not normalize line endings before hashing.

## Select complete asset dependencies

Search layers in this exact priority: explicitly selected project assets; configured studio assets;
bundled `studio/` assets. A project asset root must exist as a real directory; configured studio
must have valid `STUDIO.md`. Asset roots mirror `standards/documents/` and `templates/documents/`.
For the configured studio layer, `<studio-root>` is the workspace directory containing that
`STUDIO.md`, not the plugin’s bundled `studio/` directory.
Select each manifest independently, allowing partial overrides. If a candidate exists at a higher
layer but is malformed, unsafe or incomplete, stop; do not fall through to a lower layer. Reject
symlink files, unsafe ancestors, escapes from the selected authorized root and missing regular files.

Resolve these manifests in order:

1. `standards/documents/design-system.json`, ID `as.document-design-system`.
2. `templates/documents/<kind>/manifest.json`, ID `as.<kind>-template`; the configured studio
   candidate is `<studio-root>/templates/documents/<kind>/manifest.json`.
3. For a book only, also `templates/documents/product-cut-sheet/manifest.json`, ID
   `as.product-cut-sheet-template`; the configured studio candidate is
   `<studio-root>/templates/documents/product-cut-sheet/manifest.json`. The book's `dependencies`
   must equal `["product-cut-sheet"]`.

Each manifest has integer `schema_version: 1`, exact expected ID, nonempty string `version` and
nonempty object `assets`. Retain its complete original UTF-8 text and raw hash. For every declared
asset in manifest insertion order, resolve its relative name within that manifest directory;
require an authorized regular nonsymlink file and exact declared SHA-256. Decode its full UTF-8
text without normalization. A selected manifest's missing or wrong-hash asset is an error even if
another layer has that asset. An explicitly selected project asset root must supply at least one
effective asset; an empty/noncontributing override is an error.

Each selected template's `design_system` must equal the chosen system's exact `{id, version}`.
Every selected template must support the requested preset and orientation. The chosen system's
`presets` must equal the bundled canonical preset mapping; override assets may not redefine named
physical sizes. An accepted reference can supply explicit `reference_overrides` to the output
contract; it does not silently change named paper dimensions, required content or audience rules.

## Resolve physical page and layout

Named presets are `letter`, `legal`, `tabloid`, `ansi-c`, `ansi-d`, `ansi-e`, `arch-a`, `arch-b`,
`arch-c`, `arch-d`, `arch-e`, `arch-e1`, `a4`, `a3`, `a2`, `a1`, `a0`. Read exact widths/heights/units
from the bundled design-system manifest. Named presets reject supplied custom dimensions/units.
For `custom`, require finite positive numeric width and height and units `in` or `mm`. Physical
units and displayed product measurement units remain separate.

Convert inches with factor 72 points/inch; millimeters with factor `72 / 25.4`. Sort the resulting
dimensions into short and long edges, then orient short/long for portrait or long/short for landscape.
Require short edge at least `custom_limits_pt.min_short` and long edge no more than
`custom_limits_pt.max_long` from the selected system (bundled values 360 and 3600 points). Select
first tier in `compact`, `standard`, `board` whose `max_short_pt` includes the short edge; reject
unsupported sizes. Use the entire selected tier object and its declared `layout_version`.

Require finite positive margin, body, title, minimum type and gutter points; exact positive integer
orientation-specific column count; `body_pt >= minimum_type_pt >= 9`. Compute content width/height
as page width/height minus twice the margin. Both must be positive; `(content_width -
(columns - 1) * gutter_pt) / columns` must be at least 90 points. Never scale a Letter design onto
a board or substitute a nearby physical preset. Round stored page width/height and content
width/height to six decimal places using the historical binary64 nearest-even decimal rounding.
The fingerprint uses those actual stored number kinds and values. A host unable to reproduce the
encoding or physical precision must report that capability gap before publication.

## Exact resolved result

Validate [document-design.schema.json](../../schema/document-design.schema.json) and this procedure.
The result has exactly `schema_version: 1`, `kind`, `identities`, `assets`, `override_layers`, `page`,
`layout`, `fingerprint`:

- `identities`: one entry per selected manifest, in the order above, exactly
  `{id, version, layer, manifest_sha256}`.
- `assets`: each manifest first followed by its declared assets, each exactly
  `{layer, path, sha256, text}`. Paths are relative to that layer's root; manifest hashes are raw
  byte hashes and every asset hash must equal SHA-256 of its retained UTF-8 text bytes.
- `override_layers`: distinct selected layer labels in first-occurrence order (`project`, `studio`,
  `bundled`), not a reordered set.
- `page`: exactly `preset`, `orientation`, rounded `width_pt`, `height_pt`, `physical_units`,
  `measurement_units`, `margin_pt`, rounded `content_width_pt`, `content_height_pt`, `rotation: 0`,
  `user_unit: 1`.
- `layout`: `id` tier, `version` system layout version, `columns` selected orientation count, plus
  all original selected tier members including maximum short edge and both orientation counts.
- `fingerprint`: logical SHA-256 of this result with only `fingerprint` omitted.

Revalidate positive page/content dimensions, all asset text hashes, full identities/dependencies,
and the fingerprint on read. A self-consistent saved resolution is an immutable snapshot, not proof
that central assets remain current. Immediately before output check or resume, resolve the current
same selected dependencies again and compare exact kind-preserving values/hashes. Keep both versions
as evidence. Return `status: "resolved"`, fingerprint, page, layout and identities, with
`workflowCompleted: false`; saving design data does not render or inspect a deliverable.
