---
name: workplan
description: "Prepare a proportionate work plan with outcomes, steps, dependencies and acceptance evidence. Use to plan substantial work or coordinate an approved team; a plan-only request does not authorize implementation."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /as:workplan

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:workplan`), and applicable [workspace semantics](../../docs/workspace-model.md). Load only the required modes from the [shared catalog](../../corpus/host-contracts.json).

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) and available native tools or ordinary task-specific code. Apply the receive-owned semantic document rules directly; no installed library, nested skill invocation, runner or executable reconstruction is required. Resolve context before durable work. Existing exact authorization persists; ask only for material missing information or missing permission.

Plan work, not a building/site/floor design. Route regulated/domain analysis to its proper owner. Inspect only enough evidence to make the plan reliable; distinguish facts from assumptions. Use applicable originals for external claims.

Quick straightforward tasks proceed within existing authorization. Meaningful multistep work that benefits from advance review receives a concise inline plan: intended result, concrete steps/outputs, relevant dependencies and checks. A durable plan is needed only when requested or useful for project continuity; do not create a file as an invocation tax. No rigid time threshold or compulsory Norma hop applies.

When parallel work benefits the task, state team size, roles, bounded assignments, concurrent work/dependencies, exclusive file ownership and integrator. Obtain only missing approval of that concrete work/team. Plan-only requests end at the plan. Prior exact approval survives resume. The main harness creates approved agents through actual exposed tools, verifies their identities and integrates results; workers return questions to the main loop. Unavailable/failed delegation is disclosed; only a material unapproved fallback needs further approval.

## Durable plan

Resolve one project and read relevant PROJECT.md facts, registered decisions/source documents and the Agreement section when present. Compare scope advisory findings without creating commercial gates. Choose enough detail for the task; the [plan template](templates/plan.md) is a useful structure, not a required heading/word quota.

Each work unit names its result, owner, affected surface, inputs/dependencies and meaningful acceptance evidence. Include known risks/unknowns that change execution. Never inflate a small task with a committee, duplicate registry, blanket benchmark or mandatory deterministic validator.

## Before changing records

Before persistent changes, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence): **Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Inspect pending work first. Finish and verify preparation before the first canonical write: separately reread every saved original and prepared file, check its complete actual bytes, establish durable saving, and inspect actual permissions, ownership and ACLs. Merely writing recovery files does not finish verification. Apply only that verified set. Mark complete only after fresh readback validates the entire affected result and its relationships. Read-only requests and inline drafts need no publication sequence.

Saving a plan affects the complete plan document plus DOCUMENTS.csv and any explicitly authorized attachment registrations. Prepare and verify that full set before writing the first member. Selected source records remain read guards. Plan publication does not include task import or implementation of the planned work.

Prepare Markdown; resolve confirmed document coordinates using `documents.resolve`; receive with kind `plan`. Paths follow the firm template. A revision is a new registered document with explicit `supersedes`, preserving the earlier plan. Reopen and report the actual document ID/path and remaining decisions.

Task register entries, project facts and durable decisions are separate promotions. Offer only useful selected handoffs; a saved plan does not silently import tasks or execute the work. Inline planning does not imply durable archival of conversation.

`workplan.prepare` means the authored preparation procedure above; it may produce an inline draft without a workspace write. Persistence uses the shared native document contract, restricted here to kind `plan` and authorized attachments. A saved record does not authorize its proposed actions or promote facts/decisions automatically.
