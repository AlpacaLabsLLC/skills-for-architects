---
name: studio
description: "Open, inspect or configure an Arch Studio workspace and register projects. Use for studio administration; direct domain skills and tools-only use remain available."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - AskUserQuestion
---

# /as:studio

Before acting, read the [host contract](../../docs/host-harness-contract.md), this component's [declaration](host-contract.json) (`skill:studio`), and applicable [workspace semantics](../../docs/workspace-model.md). Load only the required modes from the [shared catalog](../../corpus/host-contracts.json).

<!-- architecture-studio:harness-compatibility -->
Use the [host adapter](../../docs/host-adapters.md) for native invocation. Apply the [native workspace operations](../../docs/workspace-model.md#native-studio-and-project-operations) with the host’s own tools and ordinary task-specific code. Operation names identify semantic scope, not function calls or a dispatcher. No Arch Studio runner, executable download or reconstructed helper is required. Resolve canonical context before existing-workspace edits; fresh setup validates its explicit target and ancestor boundary instead. Existing exact authorization persists; ask only for material missing information or missing permission.

Own STUDIO.md, project registration, synchronized registered Status and the studio-only connector boundary. Read [moments](../../rules/moments.md) for state-aware welcome and no-folder behavior. Do not repeat a declined setup nudge. A supplied task proceeds directly; no welcome/menu replay. Tools-only and valid standalone project use require no studio scaffolding.

## Before changing records

Before persistent changes, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence): **Inspect → Prepare → Verify preparation → Apply → Verify result → Complete**. Inspect pending work first. Finish and verify preparation before the first canonical write: separately reread every saved original and prepared file, check its complete actual bytes, establish durable saving, and inspect actual permissions, ownership and ACLs. Merely writing recovery files does not finish verification. Apply only that verified set. Mark complete only after fresh readback validates the entire affected result and its relationships. Read-only requests and inline drafts need no publication sequence.

Fresh setup prepares the whole declared studio tree and identities. Project-mode registration changes STUDIO.md while guarding the existing project's identity; portfolio registration also includes any permitted removal of a header-only local TASKS.csv and the project task-pointer update in the same prepared set. Status/archive changes prepare both STUDIO.md and PROJECT.md before either publisher runs. Task-mode changes include every affected register and ownership reference. Single-setting edits remain bounded to their declared file/field; optional preference/connector edits retain their separate exact authorization.

## Setup

`/as:studio` (Codex: `$studio`) offers four paths: set up a studio, use the skills without setup (tools only), open an existing studio, or learn on the sample project with `/as:learn`. Tools only writes nothing and needs no later setup prompt in that conversation.

Fresh setup walks the user through the four decisions Arch Studio is built around, one step each, in this order. Ask only for missing values. Show each step's defaults; "use defaults" or "skip" takes them, and every default is listed again in the preview. Use `studio.init` for a confirmed exact fresh target; the [workspace model](../../docs/workspace-model.md#studioinit) defines each input and record.

0. **Location and name.** Exact empty or absent target folder and studio name → STUDIO.md `Studio`, `.as-folder.json`.
1. **Governance: who approves what.** Read the [studio policy contract](../../docs/studio-policy.md). Ask once whether the user has an AI-use policy or wants the offered default, show the default before adoption, and allow decline; skipping records a decline. Who approves what and where review limits fall belong in that policy document, not in new settings. State the built-in limits without asking: larger jobs get a work plan first, findings are offered to records rather than written silently, building-code, zoning and specification output is marked for professional review. Existing references stay in place; a default is created only at the resolved Standards root's `governance/ai-policy.md`. Record the reference and adoption choice in STUDIO.md's Data governance section. Preserve already-configured choices on unrelated edits; Skill Maker only consumes them. No policy is silently adopted or migrated.
2. **Practice areas: which services the studio offers.** Offer the shipped [practice areas](../../docs/practice-clusters.md) (default all), then working units and jurisdiction (No default is valid) → STUDIO.md Practice areas table, `Working units`, `Country`, `State/region`, `City`. The selection is advisory: it orders skill suggestions and never hides or blocks a skill; geographic coverage stays a property of each skill.
3. **Memory: what the studio and its projects remember, and where.** Explain that records stay in this folder: STUDIO.md is the registry, each project keeps PROJECT.md, DOCUMENTS.csv, TASKS.csv, TIME.csv and INVOICES.csv. Ask for project phases by project Kind, naming policy (`as`, `firm`, `none`) and Project ID convention, folder taxonomy, managed roots, document path template and task register (`project` or `portfolio`) → STUDIO.md settings, `stages` and `default-scopes` tables, managed-root `.as-folder.json`. Naming and taxonomy are separate advisory choices. Preserve confirmed human names/casing. The shipped building/software/initiative phases are Arch Studio-owned defaults, not an asserted external standard.
4. **Tooling: what the assistant can use.** State without asking: all bundled skills stay available; firm skills go in `.agents/skills/` (Codex) and `.claude/skills/` (Claude Code), written later with `/as:skill-maker`; `.mcp.json` starts empty and connectors are a separate later request. Then ask: “Would you like this assistant to use Arch Studio by default for architecture and project work?” Follow the [preference protocol](../norma/references/assistant-preference.md). When the exact scoped preference edit has been previewed, the same setup approval can cover it; a general yes never approves an unseen file edit. Otherwise retain session guidance and obtain only missing concrete authorization. Do not persist a global preference implicitly.

Then show one preview grouped by those decisions: the exact target, files, managed roots, recorded values, any adopted policy file, and the data boundary (records stay in the user workspace; content supplied to a configured model follows that provider's terms; setup creates no ALPA account/cloud storage/Git repository). One concrete setup gate covers all of it; nothing is written before it. Format version stays 3; Document model 1 identifies the fresh record shape. No existing workspace conversion or backward-compatibility setup is provided.

Claude Code may ask with `AskUserQuestion`; Codex asks the same questions in plain conversation, one decision at a time. Steps, defaults, records and the approval gate are identical on both hosts.

An existing studio revisits one decision only on explicit request (for example “change our practice areas”, “set our AI policy”, “change naming”), with an exact preview of the affected STUDIO.md section or setting. Existing studios are never walked through again or migrated automatically; one without a Practice areas table stays valid.

MCP instruction delivery does not install lifecycle hooks. Background update preference is an installed-package feature outside this MCP workflow; report it unavailable here without inspecting or creating package state. Do not infer enablement from connection or general setup approval.

Apply the reviewed `studio.init` preparation with native tools. Reopen STUDIO.md, identity, connector manifest (`mcpServers` empty), managed roots and host skill roots. Installation/connection checks do not prove workspace creation.

## Projects and settings

- `studio.status` lists valid and invalid registrations, identity drift and task mode read-only. Unknown or archived status does not hide a project. No authentication/network checks are implied.
- Create-project orchestrates `project.init` then `studio.register`; each uses the same already-approved identity/target. A partially completed project is reported and registration resumed without recreating it.
- `studio.register` requires an existing new-model descendant with immutable unique Project ID and Folder ID. Paths are relative cached locations; do not infer identity from a human folder name.
- `studio.set-status` and `studio.archive` change only the selected registry Status cell and the matching PROJECT.md Status Value cell. Preserve its existing Source and Date cells exactly unless the user separately authorized those specific provenance changes; do not replace Source with the operation name. Before publication and on actual readback, compare the field-level diff across both files and reject any other changed cell. Activity never establishes completion or acceptance.
- `studio.set-naming` changes the advisory policy/convention without renaming existing IDs or folders.
- `studio.task-mode` switches only empty current-model task registers between project and studio portfolio ownership, preserving the one-writer topology. Populated registers require a separately specified current-data operation, not an automatic merge/split or historical converter.

Only studio owns `.mcp.json`, at studio root. Setup leaves it empty; connector configuration/authentication requires separately available capabilities and scope. Projects never receive this manifest. Firm extensions stay in the relevant host's studio skill root.

General domain work may hand off once to Norma with scope, completed outputs and existing authorization; an explicit studio administration task stays here. Main-harness agent creation follows approved roles/assignments and real capabilities. Do not claim that instructions or a welcome executed a workflow.

## Optional preferences and connectors

Use `studio.preference` only for the optional default-assistant choice, applying the [preference protocol](../norma/references/assistant-preference.md) with the verified native instruction mechanism and concrete authorized diff. No persistence claim follows from connection or a saved file alone. MCP background lifecycle update checks remain unavailable; do not invoke installed-package update operations through this workflow.

`studio.connectors` owns the studio `.mcp.json` boundary. Fresh setup creates exactly an empty `mcpServers` object. A later explicitly requested configuration must use verified connector/host documentation and a reviewed exact change, preserving other entries. Configure only the known authorized server; authentication, external messages and account provisioning require their actual separate capabilities and authorization. No arbitrary connector endpoint or secret is inferred from workspace setup.

After administration, use the shared [completion reporting](../../docs/completion-reporting.md) contract. Report actual changes and readbacks; a connection or welcome is not workspace creation.
