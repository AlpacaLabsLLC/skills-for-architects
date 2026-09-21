---
title: Document Register and Phase Taxonomy - Plan
type: feat
date: 2026-09-09
deepened: 2026-09-10
artifact_contract: ce-unified-plan/v1
artifact_readiness: pending-r4-baseline-reconciliation
product_contract_source: session-2026-09-09
execution: code
---

# Document register and phase taxonomy for Architecture Studio

- **Created:** 2026-09-09
- **Status:** Complete local module allocated to R4 by Federico on 2026-09-13. R4 W1 reconciles the actual source and reusable implementation before execution. Recorded in the ALPA studio project `260302-INT-ARCHITECTURE-STUDIO` as decision 0004; work units tracked there as T0019 to T0029. This file remains the detailed implementation plan, subordinate to the current R4 scope and contracts.
- **Planning mode:** Repository
- **Depth:** Standard
- **Owner:** Architecture Studio, project `260302-INT-ARCHITECTURE-STUDIO`
- **Authority:** Federico directed the design in the 2026-09-09 working session and asked for a detailed plan to be queued for a decision on whether it ships in 1.5 (Sharmila) or a later release candidate. This plan does not approve implementation, release or migration of any studio.

**R4 reconciliation — 2026-09-13, latest owner direction:** The [R4 umbrella](../../../../docs/ALPA/10-PROJECTS/INTERNAL/260302-INT-ARCHITECTURE-STUDIO/docs/plans/2026-09-12-as-r4-architecture-and-host-contract.md) governs. Federico states there are no users requiring backward compatibility: implement the complete new local model and fresh setup, without historical workspace conversion, Markdown-register importers, 1.4.5 upgrade tests or compatibility-only adapters. These obligations are removed, not deferred. This narrows the earlier complete-local-module-and-migration allocation while retaining the new model. Local W1–W8 and W10–W11 apply only to the forward model; W9 server bindings remain H2. Use the R4 W1 candidate from accepted R3 `a664b5d` with explicit carry-forward reconciliation. P0 is complete. Actual Mac/Windows × CLI/desktop execution proof is the final acceptance activity after full implementation, packaging and documentation; no early host proof gates implementation. Ordinary engineering checks remain with the changes. Use fresh synthetic new-model fixtures and preserve live originals. No live conversion is required or authorized. Raw conversation has not been archived.

## Outcome

Architecture Studio gains one deterministic document model: every file in a project, received or authored, is a document with coordinates (phase, stage, scope, originator, date) plus kind, registered in `DOCUMENTS.csv`, placed by a path template the firm owns (AS default `<phase>/<stage>/<scope>/<originator>/<date>/`), and addressed by coordinates and id rather than by path. The project root holds manifests only. Skills stop composing or hard-coding paths; a single small library resolves coordinates to folders, hashes, registers and moves. Registers become CSV. Fresh synthetic projects prove the new model without changing the live studio.

## Problem Frame

On 2026-09-09 the latest Rosan Bosch drawing set for TGS could not be found: six PDFs were opened before the right one, the newest folder was mislabelled, and the actual set existed only as a WeTransfer link in email. The project folder mixed an eight-folder lifecycle taxonomy with AS typed records and had no index of files. Format 3 defines typed prose records and registers but says nothing about received or issued documents, and its registers are markdown tables that attracted prose.

The design settled in the session: phase is the firm's slice of a project (named, or a B101 phase when the project has one), stage is the B101 phase a document belongs to, scope is one kind of work, originator is who produced the file, date is the date on the document. Kind, status, package and provenance are columns, never folders. Received files keep the sender's name. Manifests are uppercase CSV; prose stays markdown.

## Scope

### Included

- A single deterministic library exposing resolve, hash, register, move and verify through the shared R4 local runner. Its interfaces remain reusable by later H2 server bindings without a second implementation.
- `DOCUMENTS.csv` as a canonical record; a new one-verb `receive` skill as its only writer.
- Phase, stage, scope and originator vocabularies owned by `PROJECT.md` and `STUDIO.md`.
- `TASKS.csv`, `TIME.csv`, `INVOICES.csv` replacing the markdown registers; `CHANGES.csv` and per-scope `SCHEDULE.csv` defined as records.
- No prose folders at the project root: `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/` and `agreement/` retired; decisions, event records, plans, proposals and agreements are documents with a kind, filed by coordinates.
- A project `Kind` axis (`building`, `initiative`, `software`, extensible) beside `Type`, driving stage and scope vocabularies and AEC skill applicability.
- A firm-owned document path template, AS five-level default.
- Skills that write files (site-visit-report, meeting-minutes, workplan, proposal, agreement, invoice, tasklist, timetracker, master-schedule) adopting the library.
- Workspace model, templates, lint and tests for fresh new-model projects.

### Excluded

- The product / placement / procurement split of the FF&E records (T0016, T0021, T0022); this plan only fixes where `SCHEDULE.csv` lives.
- Text extraction, sheet-index parsing and mailbox ingestion beyond a first pass; drawing take-off (T0010) and RFQ packaging (T0013) stay separate.
- A change-order skill; `CHANGES.csv` is defined here, not automated.
- Automatic conversion of any live studio, including Local, ALPA and PERSONAL. Legacy conversion is outside the forward-only implementation and is not an acceptance prerequisite.
- Uniclass, NCS sheet naming for received sets, and any human-facing generated views.

## Evidence Reviewed

- ALPA studio project `260302-INT-ARCHITECTURE-STUDIO`: PROJECT.md, TASKS.md, decisions 0001 (hosted tier alongside the local plugin), 0002 (readable folder taxonomy versus immutable folder identity), 0003 (practice areas versus geographic applicability), 0004 (this model).
- The 2026-09-07 TGS procurement-day user-test report in the same project (`docs/evaluations/2026-09-07-user-test-tgs-procurement-day.md`), schema findings section.
- This repository at `3f63a2f`: [docs/workspace-model.md](../workspace-model.md), [docs/plans/commercial-records/design.md](commercial-records/design.md), skill path usage (studio 96 STUDIO.md mentions, TASKS.md 54, agreement/ 40, INVOICES.md 29, proposals/ 24), scripts `studio-workspace.sh`, `project-workspace.sh`, `resolve-context.sh`, `folder-identity.sh`, `agreement-workspace.sh`, `invoice-ledger.sh`, `proposal-workspace.sh`, `csv-library.py`.
- Local studio after the hand migration: `Local/STUDIO.md` (document taxonomy and register rows added), TGS Campus (353 register rows, 4 phases, 7 stages in use), Hotel Sonido (173 rows), Lote 74, Lote 20321, Lote 12131, four scaffold projects. Validator passing on TGS.
- External: AIA Best Practice 5.12 taxonomy, B101-2017 article 3 phases, A201-2017 §3.12 submittals, US National CAD Standard, ISO 19650-2 UK annex.

## Requirements

- **R1:** One path template per studio, AS default `{phase}/{stage}/{scope}/{originator}/{date}`; every `{field}` is a register column; a firm may reorder, drop or add fields. Single-phase projects use the B101 phase as the phase. Under the default template no other folder may exist at those levels. Cross-phase records use a phase the firm names (TGS: `campus`).
- **R1a:** The project root holds `PROJECT.md` and the registers only, plus host files. No prose folder exists at the root.
- **R2:** Stage folders carry a sequence prefix from the studio vocabulary: `0-predesign`, `1-SD`, `2-DD`, `3-CD`, `4-procurement`, `5-construction`, `6-closeout` by default; RIBA or firm lists allowed.
- **R3:** Received files keep their filename. Classification lives in the register: kind, stage, package, status, supersedes, source.
- **R4:** Casing: uppercase basename for every manifest and register, lowercase for structural folders, confirmed names untouched.
- **R5:** Paths are never composed by a skill. Skills pass coordinates to the library or look up an id in the register.
- **R6:** `DOCUMENTS.csv` has exactly one writer, the `receive` skill through the library. A file with no row is unreceived and `status` reports it.
- **R7:** Registers are CSV with fixed headers; prose belongs in `PROJECT.md` and in authored documents (decisions, event records, plans, proposals, agreements) filed by coordinates.
- **R11:** Every project carries a `Kind`; stage and default scope vocabularies are keyed by kind; AEC skills declare the kinds they apply to and warn, never block, on mismatch.
- **R8:** The document library uses Python 3 stdlib, packaged through the shared R4 local runner with its managed runtime. Verify the actual Mac/Windows × CLI/desktop routes selected in R4 W1/W5; a product name or successful MCP connection is not execution proof. Linux portability is a design property, not an added R4 host acceptance target. Later H2 bindings reuse the same operation semantics.
- **R9:** New-model file operations preserve identity/content/history, validate inputs before writes and handle interrupted writes without data loss. No legacy workspace migration is required.
- **R10:** Every rule in R1 to R7 is checked by lint or a test, not by prose.

## Historical Observations — September 9–10; not current compatibility requirements

- Format 3 is unreleased; changing its record shape now costs one migration, not two.
- The Local studio already satisfies R1 to R4 by hand; its DOCUMENTS.csv rows have kind and stage but empty source and sheet columns for most files.
- The three throwaway scripts from 2026-09-09 (`tgs_migrate.py`, `tgs_migrate3.py`, `tgs_migrate4.py`, `local_migrate.py`) implement resolve, hash, dedupe, move, link rewrite and register generation once each. They are the draft of the library and are not portable as written.
- The AS resolver (`resolve-context.sh`) returns identity, roots, registry and task mode; it has no notion of document coordinates.
- The good-morning skill and the ALPA task tracker read `TASKS.md`; they follow the rename in the same release.
- Per feedback `feedback_use_as_skills_on_as_projects`, record edits on AS projects route through skills; today the resolver fails on this machine, which is T0002.

## Assumptions

- `local` (studio) and `tgs` (owner-side role) are both valid originator codes for "us"; the project vocabulary decides, not the plugin.
- A package that has internal structure (a zip's extracted tree, a model release with `releases/` and `working/`) keeps that structure below its date folder; the register row for the package points at the folder.
- Large binaries (zip, ifc, rvt) may be ignored by git and still hold a row; `path` may be external.
- Future H2 server bindings reuse the library's operations; no second implementation or R4 server-execution requirement.

## Decisions

### D1 — One library, not many scripts
Deterministic behaviour (resolve, hash, register, move, verify) lives in one Python module with no dependencies. Everything else stays a directive. The existing `*-workspace.sh` scripts are not extended; the library takes their document-facing responsibilities and they shrink.

### D2 — Coordinates and ids, never paths
Skills carry `(phase, stage, scope, originator, date)` or a `doc-id`. The library owns the string. Templates and SKILL.md bodies name records by their register name from the canonical-owner table, never by a composed folder.

### D3 — Fresh new-model setup, no legacy conversion
The latest September 13 owner direction removes historical format detection, old-register conversion and package/data downgrade requirements. Implement the new record shapes directly. Historical decision-0004 migration prose records the earlier design; it does not impose an R4 backward-compatibility requirement. Do not modify live workspaces as an implementation or acceptance step.

### D4 — Vocabularies are data
Phases, scopes and originators are tables in `PROJECT.md`; stages are a table in `STUDIO.md`. The library validates against them and the project skill edits them. Unknown values are confirmed by the user, never invented.

### D5 — No prose folders; every authored record is a document
Decisions, meeting records, site visits, plans, proposals and agreements are documents we author, with `originator` = the studio's code, a `kind` (`decision`, `meeting`, `site-visit`, `workshop`, `call`, `plan`, `proposal`, `agreement`, `contract`), and the coordinates of what they concern. They file through the same template as received documents. Listing decisions is `kind = decision`; supersession uses the `supersedes` column. Records that span phases use a firm-named phase (`campus` on TGS). `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/`, `agreement/` and `contracts/` are all retired. Revised 2026-09-10 from the earlier version that kept `decisions/` and `meetings/`.

### D6 — Site visits are a kind of event record
A site visit report is an event record like minutes, a call or a workshop, distinguished by kind and by the stricter observation, participant-reported and limitation sections the site-visit skill enforces. One record shape, several templates.

### D7 — Project Kind
`Kind` (`building`, `initiative`, `software`, extensible by the studio) is asked at init, recorded in `PROJECT.md` and as a registry column, and is advisory. `Type` (`internal`, `client`) is unchanged. Stage and default scope vocabularies in `STUDIO.md` are keyed by kind (B101 phases for `building`; `discovery, design, build, release, operate` as the shipped default for `software`; firm-named for `initiative`). Skills declare `kinds:` next to geographic scope per decision 0003 and warn on mismatch.

### D8 — The path is the firm's, the coordinates are AS's
`STUDIO.md` carries one document path template. `resolve`, `verify` and `move` are functions of the template and the row. The empty template means "record where the firm put it, never move it". Manifests are the only names AS reserves.

## Work Units

Each unit is one module with its upstream input, downstream output and the contract it must keep. Units are ordered by dependency; W1 and W2 are the critical path.

### W1 — `documents` library
- **Location:** `skills/receive/scripts/documents.py`; invoked via `<plugin-root>/skills/receive/scripts/documents.py <op>` by every other skill.
- **Operations:** `resolve` coordinates plus kind to folder via the studio template; `hash` sha256; `register` append or update rows; `move` with link rewrite; `verify` files versus rows, duplicates, missing prefixes.
- **Upstream:** `STUDIO.md` stage vocabulary, `PROJECT.md` phase/scope/originator tables, `DOCUMENTS.csv`.
- **Downstream:** every skill in W4 to W8; the MCP tools in W9.
- **Contract:** stdlib only; every op has `--dry-run`; output is JSON on stdout, human text on stderr; exit codes distinguish invalid coordinates, unknown vocabulary, collision and IO failure; never renames a received file; never writes outside the project root.
- **Tests:** fresh synthetic project with representative document cases; one test per op; casing and prefix rules; collision by hash; link rewrite across `../`.

### W2 — Vocabularies, Kind and path template in the manifests
- **Location:** `skills/studio` (path template, stage and default-scope tables keyed by kind in `STUDIO.md`), `skills/project` (`Kind` in identity; phase, scope, originator tables in `PROJECT.md`; `project vocab add|list|rename`; `vocab add phase` may create the empty phase folder on request).
- **Upstream:** user confirmation at studio setup and project init.
- **Downstream:** W1 validation; W3 to W8 reads.
- **Contract:** tables bounded by markers like the projects registry; header-keyed parsing; a vocabulary rename is a coordinated new-model operation through W1; the template validator rejects unknown `{field}` names; a kind with no stage table falls back to the firm-named list with a warning.

### W3 — `DOCUMENTS.csv` record and `receive` skill
- **Location:** new `skills/receive/`, one verb, `user-invocable: true`; register schema in `docs/workspace-model.md`.
- **Inputs:** a file, folder, zip, or Gmail message id plus coordinates; missing coordinates are asked, defaults proposed from filename, sender and date on the document.
- **Outputs:** files under the resolved folder, rows in `DOCUMENTS.csv`, text sidecars, sheet index for drawing sets, WeTransfer expiry in `source`.
- **Downstream:** `tasklist` when a document creates an action; `project` when a document changes a fact.
- **Question flow:** `receive` always asks for the coordinates (phase, stage, scope, originator, date, kind), proposing defaults it can read: originator from sender, date from the document, stage from the project's active stage, scope from sheet series or filename, kind from type and context. Under any non-empty template the folder follows from the answers and nothing else is asked. Under the empty template one more question is asked, where, answered by pointing at a folder or by the file already being there. The filename is never changed in either case.
- **Contract:** the only writer of `DOCUMENTS.csv`; idempotent on rehash; extracted packages keep their internal tree; a document that spans phases becomes one file and one row per phase only when it is physically split, otherwise one row with `phase` on the primary and the others in `notes`.

### W4 — Registers to CSV
- **Location:** `skills/tasklist` (`TASKS.csv`), `skills/timetracker` (`TIME.csv`), `skills/invoice` (`INVOICES.csv`), studio portfolio view; `CHANGES.csv` and `SCHEDULE.csv` schemas documented, no writer yet.
- **Contract:** fixed headers per record in the workspace model; append-only history preserved; new registers are created directly as CSV; new prose uses `PROJECT.md` or registered authored documents. No old Markdown table converter.

### W5 — Commercial records as documents
- **Location:** `skills/proposal`, `skills/agreement`, `skills/invoice`.
- **Contract:** a proposal is a document with kind `proposal` and `originator = <studio>`; a signed agreement, SOW or amendment is a document with kind `agreement` or `contract` from its originator; the agreement *context* (parties, term, fees, caps, scope blocks) moves from `AGREEMENT.md` into a `## Agreement` section of `PROJECT.md` citing the document ids; checksum sealing of issued proposal terms unchanged; the scope guard reads `PROJECT.md`; `proposals/`, `agreement/` and `contracts/` are not created or read.

### W6 — Writing skills become document writers
- **Location:** `skills/site-visit-report`, `skills/meeting-minutes`, `skills/workplan`, the decision writer in `skills/project`.
- **Contract:** each writes one markdown document with a kind through W1's `resolve` and registers it through W3; the record's coordinates are asked (phase, scope, stage) with defaults from the project's active phase; attachments are documents cited by id; `list` verbs are register queries by kind; `site-visit-report` and `meeting-minutes` are two templates over the event-record kind; `site-reports/`, `docs/plans/`, `decisions/` and `meetings/` are neither created nor read.

### W7 — FF&E records placement
- **Location:** `skills/master-schedule`, `skills/product-data-import`, `skills/csv-to-sif`, `skills/sif-to-csv`.
- **Contract:** `product-library.csv` remains the catalogue layer at the root; a scope schedule is `<phase>/<stage>/<scope>/SCHEDULE.csv` resolved by W1; no other structural change, the placement split is its own plan.

### W8 — Project and studio skills
- **Location:** `skills/project` (init asks `Kind`; creates only `PROJECT.md`, the registers and host files; `status` calls `verify`), `skills/studio` (setup asks for stage vocabulary; fresh setup creates the new register/model declarations), `resolve-context.sh` trimmed to identity.
- **Contract:** no scaffold folders at all; `status` reports unreceived files, orphan rows, duplicate hashes, expired sources, template violations; fresh setup uses the new shape directly; no old-layout detection or conversion (D3).

### W9 — MCP tools
- **Allocation:** H2, excluded from R4. This historical unit is not an R4 execution prerequisite or a substitute for a missing local host bridge.
- **Location:** as-mcp / as-platform.
- **Contract:** `documents.resolve`, `documents.register`, `documents.verify` wrap W1 with identical semantics and JSON; no path composition in the server.

### W10 — Spec, lint, tests, docs
- **Location:** `docs/workspace-model.md`, `docs/plans/commercial-records/design.md`, `scripts/lint.sh`, `tests/`, `README.md`, `CHANGELOG.md`.
- **Contract:** canonical-owner table gains `DOCUMENTS.csv`, `CHANGES.csv`, `SCHEDULE.csv` and the document kinds; loses `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/`, `agreement/`; lint enforces R1, R2, R4, R6. External standards use original-source navigation metadata under R4 W4; do not create a local explanatory reference summary. Document AS-owned design decisions separately from external authority.

### W11 — New-model fixtures
- **Location:** Isolated fresh synthetic projects; no existing studio conversion.
- **Contract:** verify authored/received records, firm-defined coordinates, zip/PDF/attachment-provenance and expiring-link examples on the new model. Exercise the five queries: latest set, arrivals since a date, documents tied to a change, email-only provenance and expiry. State unknowns. File-operation tests preserve identities, hashes, links and history and prevent duplicate rows on repeat calls. Actual host execution of the fully integrated package occurs last under R4 W10; ordinary local checks accompany implementation.

## Dependencies and Risks

- R4 W1 baseline reconciliation precedes this plan's implementation. Here, W2 precedes W1 validation; W1 precedes dependent callers; W4–W7 and all affected consumers precede integrated W8 new-model acceptance. W9 remains a later H2 dependency on the frozen operation contracts.
- The good-morning skill and ALPA `global_tasks.md` read `TASKS.md`; they break the day W4 ships unless updated together.
- Required host routes must expose a usable local execution and file-access facility through the R4 shared runner. Verify actual capabilities; where a bridge is missing, identify the concrete gap and propose a bounded local integration under R4 W5. Do not assume product capabilities from names, count unsupported handling as passed coverage, or import W9/H2 remote execution to satisfy R4.
- Windows path length with deep trees and long RBS filenames; test in W1.
- Mail ingestion depends on the Gmail token expiry problem (`reference_gmail_mcp_oauth_testing_expiry`); W3 must degrade to "file from disk" cleanly.
- Fresh project templates must keep intended artifact ignore rules; document operations must not accidentally start tracking private/binary inputs.

## Release Allocation

- **Q1 resolved by Federico, September 13:** the complete local module, W1–W8 and W10–W11, is included in R4 across its W3/W5/W8/W10. W9 server bindings remain H2. Do not reopen the historical split-release recommendation. The final public/package version is determined by R4's release review; allocation does not authorize publication or live-workspace conversion.

## Closed Questions

- **Q2:** the studio's own originator code is a vocabulary entry the studio sets (`local` for Estudio Local; `tgs` on the TGS project where the studio acts on the owner's side). The plugin ships no reserved word.
- **Q3:** `CHANGES.csv` is defined for new-model projects in this cycle; its writer is a later change-order skill.
- **Q4:** no generated views in this cycle; the register is the only view. Views remain possible later because they are a function of the row.
- **Q5:** `vocab add phase` records the phase; it creates the folder only with `--folder`. Stage, scope and originator folders appear only when a file is filed.

## Pending Work

- **T0029, fixture:** use fresh synthetic new-model projects; the former live/copy re-migration requirement is removed. Canonical task status is unchanged by this plan correction.

## Execution Order

1. Consume R4 W1's reconciled source and module inventory; prepare fresh synthetic new-model fixtures.
2. W2 vocabulary and template tables, then W1 library and fixtures; freeze JSON contracts and integrate the shared R4 runner before dependent callers.
3. W3 `receive`, proven on representative zip, PDF and authorized/synthetic attachment inputs.
4. W8 init and status, so a new project starts on the model and current-model status reports inconsistencies.
5. W4 new CSV register definitions, together with good-morning, the ALPA task tracker and every other affected reader.
6. W5 commercial writers, W6 authored records and W7 FF&E placement; all are included in R4 and coordinated before new-model acceptance.
7. W8 fresh setup and current writer/reader integration, followed by W11 new-model fixtures and the five register queries. Check invalid input, interrupted document writes and repeat-operation idempotence.
8. W10 spec, lint, tests and docs follow each changed module and close with integrated R4 W8/W10 evidence. Actual host execution verification is the last acceptance activity after full implementation. No legacy conversion work is required. W9 remains H2.

## Definition of Done

- W1 passes its tests on fresh synthetic projects; `verify` reports zero unexplained findings on the new-model fixtures. Live originals remain unchanged.
- No SKILL.md or template in the repo contains a composed document path; lint proves it.
- A fresh project initialised by `project init` has `PROJECT.md`, the registers and host files, and no folders.
- A firm template other than the default places, moves and verifies documents in a fresh fixture project correctly.
- `receive` files a zip, a single PDF and an authorized or synthetic mailbox attachment into the right folder with a row each, using the actual local runner routes claimed by R4. Provider integration success is claimed only with authorized provider evidence, separately from fixture behavior.
- The workspace model, CHANGELOG and README describe the same model; release notes identify the complete local allocation, actual verified host routes, fresh setup requirements and separate H2 server bindings.
