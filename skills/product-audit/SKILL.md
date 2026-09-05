---
name: product-audit
description: Audit a product, selection or FF&E schedule against sourced evidence and flag discrepancies, unknowns and stale specifications. Use to check product data; not to repair records, certify compliance or generate cut sheets.
allowed-tools:
  - Read
  - Write
  - Glob
  - Grep
  - Bash
  - WebFetch
  - WebSearch
---

# /as:product-audit — Audit a product selection

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

## Input and authority

Accept one item, selected tags, or a complete schedule. Resolve exactly one owning project using `<plugin-root>/skills/project/scripts/resolve-context.sh` before reading/writing project records. Read its instructions. A missing or ambiguous boundary is not permission to create a project. For a one-off comparison, accept an explicitly supplied snapshot without adopting a schedule. Read `<plugin-root>/corpus/practice-methods/ffe/README.md` and `<plugin-root>/schema/ffe-audit.schema.json`.

For adopted schedules, use `/as:master-schedule` to read the pinned item/schedule revisions. Item IDs are immutable; tags and workbook rows are only locators. An old workbook or optional `product-library.csv` does not override current records. One-off library comparisons retain the exact header and `<plugin-root>/schema/csv-conventions.md` conventions.

## Steps

1. Establish the requested scope, revision, source basis and **live** versus **snapshot** mode. Default a request to check current product facts to live retrieval. No routine second confirmation is needed for a read-only comparison.
2. **Live audit always retrieves/re-parses the relevant sources in this invocation.** Use the host browser/PDF capabilities; do not present cached catalog data as freshly verified. Record source/page or field locator and observed-at time. If access fails, keep `unavailable`; do not downgrade to snapshot comparison silently. Snapshot mode explicitly compares saved observations and cannot establish current facts.
3. Separate manufacturer/dealer, selected versus available configuration, actual model/accessory and installed/cutout dimensions. Preserve unknown prices/currency, evidence conflicts and user overrides. A variant combination is not a manufacturer-confirmed SKU without source evidence.
4. Build the typed audit input. Invoke `python3 "<plugin-root>/tools/validators/ffe_audit.py" <audit-input.json>` when local execution is available. The helper compares supplied observations only: it performs no retrieval and cannot authenticate the host's evidence. If unavailable, follow the same contract with available host tools and explicitly label the execution route; never claim the helper ran.
5. Present discrepancies, missing evidence, stale observations and conflicting sources, tied to immutable item/revision and field. Exact value comparisons do not convert units: resolve dimensional meaning and units before constructing comparable observations. Missing evidence is unknown, not proof that the specification is wrong.
6. When a durable report is requested/authorized, preview the exact collision-safe target under `ffe/jobs/<job-id>/audits/`, then save the report and source references. Use one confirmation gate only if required and not already authorized. Refuse overwrite; preserve previous reports. Do not persist machine-absolute paths in records. Report the actual file created.

## Output and handoff

The schema/result includes input hash, item IDs/revisions, source locators, findings and comparison mode. `matches-supplied-observations` means only that the supplied values match; it is not product certification or legal compliance.

Audit does not mutate item/schedule specifications, decisions, recovery snapshots or the optional library. Propose corrections to `/as:master-schedule`; sourcing goes to `/as:product-research`, PDF/URL extraction to their existing skills. Selection rationale and approval go through `/as:project`; never infer them from an artifact or audit result. After resolved findings, `/as:product-cut-sheet` and `/as:spec-book` consume the exact selected revisions. Cross-skill handoff does not require a subagent or separate Norma runtime.
