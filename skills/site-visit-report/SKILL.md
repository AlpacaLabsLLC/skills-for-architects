---
name: site-visit-report
description: "Prepare a sourced site-visit record separating direct observations, participant reports, interpretations, limitations and proposed follow-ups."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /as:site-visit-report

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:site-visit-report`), and applicable [workspace semantics](../../docs/workspace-model.md). Load only the required modes from the [shared catalog](../../corpus/host-contracts.json).

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) and available native tools or ordinary task-specific code. Apply the receive-owned semantic document rules directly; no installed library, nested skill invocation, runner or executable reconstruction is required. Resolve context before durable work. Existing exact authorization persists; ask only for material missing information or missing permission.

Own authored event documents of kind `site-visit`. Use the [site template](templates/site-visit-report.md). Keep direct observations, participant-reported information, interpretations, issues and proposed actions separate; give stable item labels. Record participants, date, visit scope and access/visibility/weather/testing/equipment/document limits. Inaccessible or concealed work is Not observed, never no issue observed. Do not fabricate photo identity, location, dates or certainty about concealed conditions.

Resolve the project and authorized notes/photos. Distinguish visit, source and created dates. Inspect available photos before describing their content; a filename or caption alone is not visual evidence. Link registered attachments by ID and actual resolved path. This record does not certify code, life-safety, structural, MEP, accessibility, environmental or contractual compliance; route substantive conclusions to the relevant specialist/professional workflow.

## Before changing records

Before persistent changes, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence): **Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Inspect pending work first. Finish and verify preparation before the first canonical write: separately reread every saved original and prepared file, check its complete actual bytes, establish durable saving, and inspect actual permissions, ownership and ACLs. Merely writing recovery files does not finish verification. Apply only that verified set. Mark complete only after fresh readback validates the entire affected result and its relationships. Read-only requests and inline drafts need no publication sequence.

Saving a report affects the complete site-visit document plus DOCUMENTS.csv and any explicitly authorized attachment registrations. Prepare and verify that full set before writing the first member. Notes/photos remain source read guards; no project-fact, task or decision promotion belongs to this publication set.

Prepare the report, then resolve confirmed coordinates and register through `documents.register`, kind `site-visit`. An explicit revision is a new document with `supersedes`; preserve old bytes. For client/authority-facing or regulated-conclusion reports, apply the existing [disclaimer procedure](../../rules/professional-disclaimer.md) when applicable, including the required terminal `<!-- architecture-studio:requires-disclaimer -->` marker; do not invent a universal disclaimer for an internal administrative draft.

Reopen the actual report and inspect requested presentation. Only after saving, offer selected project-fact/decision/task promotions with exact item IDs. Report approval alone is not promotion approval. Keep observations, reports and interpretations in their original epistemic category. No silent mutation of PROJECT.md, TASKS.csv or decision records.

`site_visit.prepare` means the authored preparation procedure above; it may produce an inline draft without a workspace write. Persistence uses the shared native document contract, restricted here to kind `site-visit` and authorized attachments. A saved record does not authorize its proposed actions or promote facts/decisions automatically.
