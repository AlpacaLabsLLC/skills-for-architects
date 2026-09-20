---
name: project
description: "Initialize or inspect a project, maintain sourced current facts and record durable decisions. Use for project context or remember-this requests; other record types retain their owners."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /as:project

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:project`), and applicable [workspace semantics](../../docs/workspace-model.md). Load only the required modes from the [shared catalog](../../corpus/host-contracts.json).

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Apply the [native workspace operations](../../docs/workspace-model.md#native-studio-and-project-operations) with the host’s own tools and ordinary task-specific code. Operation names identify semantic scope, not function calls or a dispatcher. No Arch Studio runner, executable download or reconstructed helper is required. Resolve canonical context before existing-workspace edits; fresh setup validates its explicit target and ancestor boundary instead. Existing exact authorization persists; ask only for material missing information or missing permission.

Own `PROJECT.md` current facts and documents of kind `decision`. The agreement skill owns only its bounded Agreement section in `PROJECT.md`; studio owns synchronized registered status. Decision reasoning is not duplicated into the fact manifest.

## Before changing records

Before persistent changes, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence): **Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Inspect pending work first. Finish and verify preparation before the first canonical write: separately reread every saved original and prepared file, check its complete actual bytes, establish durable saving, and inspect actual permissions, ownership and ACLs. Merely writing recovery files does not finish verification. Apply only that verified set. Mark complete only after fresh readback validates the entire affected result and its relationships. Read-only requests and inline drafts need no publication sequence.

Fresh setup prepares the entire declared project tree with retained identities. A fact edit affects PROJECT.md only. A decision registration affects the complete decision document plus DOCUMENTS.csv. Used-vocabulary renames include the manifest, every relocated document/referring file and its register changes; determine the complete set before applying any part. Studio-owned synchronized status includes both manifests.

## Fresh setup

Use `project.init` after confirming the exact target, immutable Project ID, display name, Type, advisory Kind/Status, client/code and Created date. Display name and Folder ID are distinct from Project ID. Ask for the firm's phases, scopes, originators and applicable stage vocabulary; defaults are proposals, not external normative codes. Standalone projects carry their template/stages in PROJECT.md; registered projects use STUDIO.md's template/stages. A valid standalone project remains valid and does not require studio creation.

The new shape is Format version 3, Document model 1. Preview the exact generated files; setup creates PROJECT.md, empty CSV registers, host instructions/skill roots and immutable folder identity, with no prose scaffold folders. It does not initialize Git, accounts or storage. No old-format converter exists. Existing live workspaces are not silently transformed. Inside a studio, studio orchestrates initialization and registration without recursive routing.

`project.status` reports identity and document verification; statuses and project Kind are advisory, not permission gates. Follow the receive-owned native document verification specification for the document findings; a missing capability is reported separately from observed identity. Use `documents.query` for decisions and dated records, `tasks.list` for actions and `invoice.status` for ledger facts. Do not infer complete state from missing/unreadable evidence.

## Facts and decisions

For `project.facts` (`remember`/`update`), distinguish sourced facts, choices and unresolved information. Preview each destination and preserve provenance/date. Record only confirmed changes. Approval to save a source does not approve promoting all its statements.

For `project.decision` (`record-decision`), capture one choice, context, actual options, deciders, proposed/decided status, rationale, consequences and exact sources. Allocate the next permanent decision number from registered decision records, without renumbering or reusing historical IDs. Prepare the authored Markdown with the bundled decision template; resolve its confirmed coordinates and register via `documents.register`, kind `decision`. Preserve unknowns and proposal status.

For supersession, receive a new decision document with `supersedes` referencing the original ID; preserve original bytes/history. Do not infer supersession from a later date alone. Query kind `decision` for listing; there is no separate path-based decision index.

## Vocabularies

`project.vocab` lists/adds/renames project phase, scope or originator values. Confirm unknown values; never invent them. A used value requires coordinated placement/link updates rather than an in-place manifest rename. Stage vocabulary belongs to studio (or the standalone manifest). An explicit request may create an empty phase folder; ordinary vocabulary edits do not precreate content directories.

Tasks, time, invoices, minutes, site reports and plans retain their corresponding owners. Use stable registered document IDs plus item anchors for provenance. Every durable mutation is read back; raw conversation is not archived merely because a fact/decision is saved.
