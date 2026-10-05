# Stateless server JSON tools and native parity

These four deterministic tools are available only where the live host exposes the corresponding
registration. These are executable structured-data
operations, separate from workflow-instruction delivery and Materials record writes. They need
no module enablement, local checkout, runner, install, shell or server-side source fetch.
Use them only if actual discovery shows the matching tool; naming one is not registration proof.

The wrapper is a closed object with `documentJson`: the complete JSON document **as a string**.
This preserves Python integer versus floating-point kinds (`1` versus `1.0`), exact large integers
and canonical digest bytes. Do not round-trip original evidence through a parser that loses those
kinds. Maximum document size is 4 MB of UTF-8, subject also to the host/transport's actual body
limit. Inputs are structured data, not files, executable code, shell commands or arbitrary paths.

| Tool | Additional wrapper fields | JSON document and result |
|---|---|---|
| `as_reconcile_quantities` | None | `{left:[rows],right:[rows]}`; exact sorted tag/scope/unit comparison with source rows and match/conflict/missing/unknown statuses |
| `as_audit_observations` | None | Exact audit envelope below; supplied-observation findings and the canonical input hash |
| `as_normalize` | Required `operation`: `dimensions`, `lighting-report`, `drawing-quantities`, `delivery-coverage`; optional `targetUnit` only for `dimensions` | Supplied evidence under the corresponding native operation contract; no inferred identity, units or coverage |
| `as_validate_record` | `record`: `product-observation`, `product-observation-batch` (default), `task` | One observation, a nonempty observation batch, or supplied TASKS.csv row object/array; validation findings, never rewritten rows |

Successful tools return `tool`, `contract` (the reference operation with `@1`),
`release:{version,sourceDigest}` and canonical `structuredContent.resultJson`, retaining number kinds.
The text content carries the same envelope with the parsed `result`. Observation validation also
reports `schema:{source,sha256}` separately from the release digest.
Parse/render that result with a lossless method where exact numeric evidence matters. Invalid
requests return bounded `invalid_input`, `invalid_json` or `input_too_large` errors; no partial result, retrieval, adoption or specification mutation occurred.
For observation validation, tool/result metadata identifies the bundled source schema digest.
Keep the actual tool result and the source digest with requested evaluation evidence.

## Quantity comparison

Reconcile caps each side at 100000 rows. Each row requires nonblank `tag`, `scope`, `unit`, `source`, and explicit `quantity` (finite
nonnegative number or null). Scope/unit strings are exact identities. Duplicate keys on either
side must be explicitly aggregated or resolved first; the tool never fuzzy-matches, combines
scenes/variants, interprets absence as zero, or selects an authoritative quantity. A match proves
agreement of supplied values, not extraction correctness, coverage or approval.

## Observation audit

Supply exactly `schema_version:1`, `mode:"live"|"snapshot"`, `started_at`, `items`, `observations`.
There are 1–10000 items and at most 100000 observations. Items require nonempty `item_id` and
`tag`, integer `revision>=1`, and `fields`. Each observation has exactly `item_id`, `field`,
`value`, `status:"observed"|"unavailable"`, `source:{reference,locator}`, and `observed_at`.
Timestamps include a timezone and must be no more than five minutes in the future.

The host retrieves/parses current source evidence for a live audit; the server only compares the
supplied observations. Live observations before `started_at` are stale. Preserve unavailable,
conflicting, source-value-unknown, not-demonstrated and discrepancy findings in returned order.
The hash uses the audit owner's Python ASCII-escaped canonical input representation. No legal
compliance, source authentication or record correction is performed.

## Explicit dimensions

Supply `raw` original evidence, `axes` with explicit `W`/`D`/`H` positive finite numeric values,
source `unit`, and dimensional `meaning`: overall, cutout, clearance, shipping, assembly or
rough-in. Missing/unsupported source unit, mapping or meaning stays unresolved. Unsupported
target unit, nonnumeric/bool axes or overflow is rejected. Partial explicit axes remain partial
with `missing_axes`; conversion never guesses axis order, units or installed/cutout equivalence.

## Other normalize operations

For `lighting-report`, `drawing-quantities` and `delivery-coverage`, read the complete
[owning evidence contracts](../tools/transformers/evidence-contracts.md). Lighting groups only asserted
source-backed inventory; drawing quantities count reviewed instances without proving source coverage;
delivery coverage assesses the supplied ledger without fetching artifacts or verifying their evidence.
`targetUnit` is rejected outside the dimensions operation. Partial dimension axes remain `normalized`
with `missing_axes` when the other required evidence is valid; no axis is inferred.

## Product observations

Read the complete [observation schema](../schema/product-observation.schema.json) and
[semantics](../schema/product-observations.md). Keep manufacturer/model/SKU and optional offering
identity, original source reference/time, content digest, selected versus available configuration,
typed fields, source status and locators, quantity meaning/unit, price currency/basis and image
variant match. Unknown/unavailable field values remain null, not invented defaults.
Validation performs neither item binding nor adoption. Native `product_observations.adapt` remains
a separate host-owned reviewed-proposal operation; these four tools do not register a generic
adapter dispatcher or write specifications.

## Task validation

`as_validate_record` with `record:"task"` accepts one supplied 13-column TASKS.csv row or an array
of at most 10000 rows. It returns `valid`, `record:"task"`, `row_count`, `columns`, bounded findings
`{row,code,key}`, `rows_rewritten:false` and `specification_mutated:false`. Findings name the column,
not its private value. Project, studio and library-row validation are not exposed by these tools.

## Invocation authority

Use the live input and output schemas. Documentation does not prove tool availability or authorize
execution. Missing tools or unsupported record types produce an explicit limitation; do not invent
aliases, dispatcher operations or declaration fields. Local semantic operations remain separately
host-owned, and the deployed tool schema governs an actual invocation.

## Native local route

The installed plugin and hosts without these exact server tools may perform the same selected
read-only computation through granted native capabilities and ordinary task-specific code.
Read the owning semantic contract: [quantity/dimension procedures](../tools/transformers/evidence-contracts.md),
[audit contract](../tools/validators/ffe-audit-contract.md), or product-observation semantics above.
Preserve exact typed evidence, ordering, rejection rules, number kinds, source/variant identity,
wall-clock freshness and canonical hash behavior. Run the relevant parity cases for the chosen
method; do not claim a server invocation, source validation or hash parity without its evidence.

No bundled Python file is an installation requirement, downloaded executable or mandatory runner.
Missing precision or validation capability produces an explicit limitation while retaining input
evidence. Deterministic native computation grants no file publication or Materials save authority;
the [module-or-local record resolver](module-record-routing.md) still governs durable module work.
