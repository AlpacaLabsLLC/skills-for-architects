---
name: meeting-minutes
description: "Turn supplied meeting notes or transcripts into sourced minutes, keeping discussion, statements, confirmed/proposed decisions and proposed actions distinct."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /as:meeting-minutes

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:meeting-minutes`), and applicable [workspace semantics](../../docs/workspace-model.md). Load only the required modes from the [shared catalog](../../corpus/host-contracts.json).

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) and available native tools or ordinary task-specific code. Apply the receive-owned semantic document rules directly; no installed library, nested skill invocation, runner or executable reconstruction is required. Resolve context before durable work. Existing exact authorization persists; ask only for material missing information or missing permission.

Own authored event documents of kind `meeting`. Preserve the [minutes template](templates/meeting-minutes.md) distinctions: discussion, stated information, confirmed decisions in the meeting, proposed decisions, proposed tasks and open questions. A meeting-confirmed choice is not automatically a durable project decision. Unknown attendees, attribution, dates or actions remain unknown.

Resolve the project and source scope. Distinguish event date, source date, creation date and revision. Use only supplied/authorized evidence; no access or transcript completeness is inferred. List stable item IDs so later promotions cite exact statements.

## Before changing records

Before persistent changes, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence): **Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Inspect pending work first. Finish and verify preparation before the first canonical write: separately reread every saved original and prepared file, check its complete actual bytes, establish durable saving, and inspect actual permissions, ownership and ACLs. Merely writing recovery files does not finish verification. Apply only that verified set. Mark complete only after fresh readback validates the entire affected result and its relationships. Read-only requests and inline drafts need no publication sequence.

Saving minutes affects the complete meeting document plus DOCUMENTS.csv and any explicitly authorized attachment registrations. Prepare and verify that full set before writing the first member. Source notes/transcripts remain read guards; a saved meeting record does not authorize changes to PROJECT.md, TASKS.csv or decision records.

Prepare the minutes, confirm missing phase/stage/scope/originator/date/kind coordinates, then apply `documents.resolve` and `documents.register` as native semantic procedures with kind `meeting`. Preserve received attachment names; attachments use their own registered IDs and actual links. Explicit revisions receive a new record with `supersedes`; do not overwrite prior bytes or silently invent numbering to disguise collision.

Read back the saved document before offering promotion. Show selected fact, decision and task candidates separately; general approval of minutes does not promote them. Project owns sourced current facts/decisions, tasklist owns TASKS.csv. Preserve reported/proposed status throughout the handoff. Direct invocation works without a coordinator or another skill-call tool; print the bounded next action if unavailable.

`meeting.prepare` means the authored preparation procedure above; it may produce an inline draft without a workspace write. Persistence uses the shared native document contract, restricted here to kind `meeting` and authorized attachments. A saved record does not authorize its proposed actions or promote facts/decisions automatically.
