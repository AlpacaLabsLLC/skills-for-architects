# Host-harness contract for every AS skill and agent

Required architecture contract, adopted for the Sharmila 1.5 release plan on 2026-09-07.
Documentation adoption does not establish that all existing skills/agents or hosts pass it.

## Ownership

AS owns domain procedures, typed-record authority, evidence requirements, validations and proposed
changes. The host owns the conversation and available browser, email, spreadsheet, filesystem,
rendering and process capabilities. An AS-owned executable helper is allowed only through a declared,
reviewed binding. Instruction delivery is not execution, access or workflow completion.

Authentication is capability-specific: Gmail connection does not prove Drive discovery, Google Sheets
read/edit access or access to one particular spreadsheet. Host names and work-mode labels are not
capability proof. Probe the actual authorized target with a bounded read before relying on access.

## Required declaration

Every skill/agent must declare the following in its instruction contract, with a shared machine-readable
representation and conformance checks to be implemented by the release work:

| Field | Requirement |
|---|---|
| Domain responsibility | One bounded outcome; owned records and explicit non-owners |
| Inputs | Required source/context, target identity, release pinning where applicable |
| Required/optional capabilities | Semantic operations such as spreadsheet.read, spreadsheet.edit, file.read, image.transform; none when unnecessary |
| Side effects | Read-only, scratch output, clip-history write, canonical mutation, or external send; distinguish each |
| Access check | Evidence needed to establish the exact target can be read/edited; a connector listing is insufficient |
| Handoff | What the host must do, exact target/range, input evidence and expected result |
| Authorization | Existing user scope, missing approval and host permission requirements; do not duplicate semantic confirmations |
| Preservation | Unrelated data, formulas, links, images, selected values and record identities that must remain intact |
| Retry/concurrency | Idempotency, expected version/content, conflict refusal and interrupted-operation behavior |
| Completion | Required fresh readback/output inspection and receipt; separate partial/blocked/unverified from completed |
| Fallback | Native permission/handoff request when available, otherwise precise user action; never invent a grant mechanism |

Agents must satisfy this contract themselves and preserve it when delegating. Agent coordination does
not confer permissions, transfer record ownership or establish child-task completion without evidence.
Read-only knowledge skills can declare no workspace/application capability; do not add needless setup.

## Execution sequence

1. Resolve task intent and exact source/target; identify whether it is a one-off document or adopted record view.
2. Discover actual host capabilities and perform the narrow authorized access check.
3. If unavailable, invoke a real host permission/handoff mechanism when exposed. Otherwise explain the
   missing capability and exact next step. Preserve task context; never silently create a replacement file.
4. Load AS instructions and required context completely. Prepare the domain result or exact change proposal.
5. Obtain only missing authorization, then ask the host to execute the bounded operation.
6. Freshly read the actual destination, verify material invariants, and report tool/result evidence.
7. Mark completion only when the workflow's required evidence exists. Resume safely after interruptions.

## Google Sheets example

A user supplies a spreadsheet link and asks to update product specifications:

- The host resolves spreadsheet ID, worksheet/tab and applicable range; confirms read access and needed edit capability.
- AS determines selected items, source facts, discrepancies and approved changes. For an explicitly adopted schedule,
  master-schedule owns canonical revision changes and the sheet is a reconciled view. Otherwise treat it as a one-off
  user-owned document: do not silently adopt records or require local studio setup.
- The host reads values AND relevant formulas, hyperlink targets, images and structure. Preserve a suitable recoverable
  revision/backup before mutation; a CSV alone cannot preserve spreadsheet features.
- Preview target cells and material changes when not already authorized. The host applies only those edits, preserving
  sharing, formatting and unrelated data. Sending the sheet or changing sharing permissions is separate authority.
- Use provider revision/precondition protection when exposed. Otherwise re-read affected content before mutation,
  record that atomic compare-and-swap is unavailable, and stop if conflicts cannot be safely excluded/resolved.
- Fresh provider readback verifies values and preserved features; visual inspection verifies requested presentation.
  A local export is not proof that the Google Sheet changed. Provider acceptance alone is not full visual verification.
- No Apps Script, raw credential reuse or new connector is silently substituted for missing host capability.

## Acceptance

Test Gmail-only, Sheets-read-only, Sheets-edit, wrong account/target, missing image/formula access,
permission denial, expired access, concurrent edit, partial update and interrupted retry conditions.
Require a Google Sheets isolated-copy workflow, in addition to local XLSX evidence. Customer sending,
sharing changes and edits to originals are not authorized by tests. Public fixtures remain synthetic.
