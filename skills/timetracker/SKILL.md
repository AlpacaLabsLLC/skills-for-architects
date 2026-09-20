---
name: timetracker
description: "Reconstruct evidence-based work descriptions and append user-confirmed durations to TIME.csv. Use for time logging and corrections; never infer hours or billing from activity."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /as:timetracker

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:timetracker`), and applicable [workspace semantics](../../docs/workspace-model.md). Load only the required modes from the [shared catalog](../../corpus/host-contracts.json).

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) and [native context procedure](../project/references/context-resolution.md). The harness performs the semantic operations below using its available native tools; ordinary task-specific code is allowed. No Arch Studio runtime, installer, bridge, supplied script or source checkout is required. Direct skill invocation is valid. Existing exact authorization persists; ask only for material missing facts or unavailable access.

Own project TIME.csv. Resolve one valid project through `context.resolve`; folders, Git roots and current directory alone never establish a project. A standalone valid project needs no studio.

## Before changing records

Before persistent changes, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence): **Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Inspect pending work first. Finish and verify preparation before the first canonical write: separately reread every saved original and prepared file, check its complete actual bytes, establish durable saving, and inspect actual permissions, ownership and ACLs. Merely writing recovery files does not finish verification. Apply only that verified set. Mark complete only after fresh readback validates the entire affected result and its relationships. Read-only requests and inline drafts need no publication sequence.

Time append/correction affects the complete TIME.csv only. Selected project/document/source records are read guards; their existence does not authorize edits or inferred hours. A correction preserves the original entry and adds one new confirmed entry under the ledger semantics.

Resolve the requested period; ask if absent. Perform `time.list` as native reads, then read the selected project’s DOCUMENTS.csv for relevant dated plans/decisions/events and inspect PROJECT.md, TASKS.csv and selected source artifacts. Explicit semantic work/event dates take priority; Git or modification times may suggest evidence but never duration. Report sources inspected and unavailable channels; quiet records do not prove no work or a complete timesheet.

Prepare descriptions with blank hours, stable source document IDs/items and confidence. Group evidence for the same activity; don't inflate it by file counts. Flag evidence already logged. Every finite positive duration comes from the user; meeting lengths, timestamps, commits and task status never supply hours. Unknown source/work dates remain unresolved.

`time.append` writes confirmed date, positive hours, description, sources and optional correction target. IDs are permanent E-numbers; exact repeat rows return the existing entry. Corrections are new entries referencing an existing E-ID; never edit/delete/renumber the original. No net-billing rule is inferred. Preview exact rows when not already authorized, apply, then re-read. Do not claim completeness beyond inspected evidence.

## Native execution and completion

Follow the exact [TIME semantics](../../docs/workspace-model.md#native-time-operations) for header,
whole-register validation, sources, decimal hours, permanent allocation and retry identity. The
operation names identify work, not an executable interface. `time.list` reads only; `time.append`
adds one confirmed row and preserves every earlier row. Do not turn existing time entries into
billing facts or silently subtract a correction from the original duration.

Before append, bind the selected project, exact user-confirmed row and actual current register.
A preview does not reserve an ID. Reconcile a concurrent allocation from a fresh full read or
stop before writing. Check prior evidence after interruption; an already applied row is a no-op.

Use the verified single-register preparation from the mutation sequence. If a required guarantee is unavailable, preserve the confirmed entry and report the observed limitation before writing.

Re-read the actual canonical file after publication. Report owner path, entry ID, confirmed date,
hours and sources, correction target if any, whether a new row was written or a repeat was found,
and preservation checks. Separate evidence inspected from channels that were unavailable; a
successful save or instruction retrieval does not prove a complete timesheet.
