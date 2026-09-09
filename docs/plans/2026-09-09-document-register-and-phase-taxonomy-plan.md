---
title: Document Register and Phase Taxonomy - Plan
type: feat
date: 2026-09-09
deepened: 2026-09-10
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: session-2026-09-09
execution: code
---

# Document register and phase taxonomy for Architecture Studio

- **Created:** 2026-09-09
- **Status:** Final for implementation, 2026-09-10. Release disposition (1.5 or next candidate) remains Federico's call per Q1; every other question is closed below. Recorded in the ALPA studio project `260302-INT-ARCHITECTURE-STUDIO` as decision 0004; work units tracked there as T0019 to T0029. This file is the implementation plan of record.
- **Planning mode:** Repository
- **Depth:** Standard
- **Owner:** Architecture Studio, project `260302-INT-ARCHITECTURE-STUDIO`
- **Authority:** Federico directed the design in the 2026-09-09 working session and asked for a detailed plan to be queued for a decision on whether it ships in 1.5 (Sharmila) or a later release candidate. This plan does not approve implementation, release or migration of any studio.

## Outcome

Architecture Studio gains one deterministic document model: every file in a project, received or authored, is a document with coordinates (phase, stage, scope, originator, date) plus kind, registered in `DOCUMENTS.csv`, placed by a path template the firm owns (AS default `<phase>/<stage>/<scope>/<originator>/<date>/`), and addressed by coordinates and id rather than by path. The project root holds manifests only. Skills stop composing or hard-coding paths; a single small library resolves coordinates to folders, hashes, registers and moves. Registers become CSV. The Local studio, already migrated by hand on 2026-09-09, becomes the fixture that proves the model.

## Problem Frame

On 2026-09-09 the latest Rosan Bosch drawing set for TGS could not be found: six PDFs were opened before the right one, the newest folder was mislabelled, and the actual set existed only as a WeTransfer link in email. The project folder mixed an eight-folder lifecycle taxonomy with AS typed records and had no index of files. Format 3 defines typed prose records and registers but says nothing about received or issued documents, and its registers are markdown tables that attracted prose.

The design settled in the session: phase is the firm's slice of a project (named, or a B101 phase when the project has one), stage is the B101 phase a document belongs to, scope is one kind of work, originator is who produced the file, date is the date on the document. Kind, status, package and provenance are columns, never folders. Received files keep the sender's name. Manifests are uppercase CSV; prose stays markdown.

## Scope

### Included

- A single deterministic library exposing resolve, hash, register, move, verify and migrate, callable as a script by the local plugin and as tools by the MCP tier.
- `DOCUMENTS.csv` as a canonical record; a new one-verb `receive` skill as its only writer.
- Phase, stage, scope and originator vocabularies owned by `PROJECT.md` and `STUDIO.md`.
- `TASKS.csv`, `TIME.csv`, `INVOICES.csv` replacing the markdown registers; `CHANGES.csv` and per-scope `SCHEDULE.csv` defined as records.
- No prose folders at the project root: `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/` and `agreement/` retired; decisions, event records, plans, proposals and agreements are documents with a kind, filed by coordinates.
- A project `Kind` axis (`building`, `initiative`, `software`, extensible) beside `Type`, driving stage and scope vocabularies and AEC skill applicability.
- A firm-owned document path template, AS five-level default.
- Skills that write files (site-visit-report, meeting-minutes, workplan, proposal, agreement, invoice, tasklist, timetracker, master-schedule) adopting the library.
- Workspace model, templates, lint, tests and the format 3 migration manifest.

### Excluded

- The product / placement / procurement split of the FF&E records (T0016, T0021, T0022); this plan only fixes where `SCHEDULE.csv` lives.
- Text extraction, sheet-index parsing and mailbox ingestion beyond a first pass; drawing take-off (T0010) and RFQ packaging (T0013) stay separate.
- A change-order skill; `CHANGES.csv` is defined here, not automated.
- Migration of any studio other than Local as a fixture; ALPA and PERSONAL studios migrate under the release, not this plan.
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
- **R8:** The library runs with Python 3 stdlib only, on macOS, Linux and Windows, under Claude Code and Codex, and its operations are exposable as MCP tools without change.
- **R9:** Migration is previewed, fail-closed and reversible, per the format 3 migration contract.
- **R10:** Every rule in R1 to R7 is checked by lint or a test, not by prose.

## Known Facts

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
- The hosted tier reuses the library's operations as MCP tools; no second implementation.

## Decisions

### D1 — One library, not many scripts
Deterministic behaviour (resolve, hash, register, move, verify, migrate) lives in one Python module with no dependencies. Everything else stays a directive. The existing `*-workspace.sh` scripts are not extended; the library takes their document-facing responsibilities and they shrink.

### D2 — Coordinates and ids, never paths
Skills carry `(phase, stage, scope, originator, date)` or a `doc-id`. The library owns the string. Templates and SKILL.md bodies name records by their register name from the canonical-owner table, never by a composed folder.

### D3 — Extend format 3 before release
Per the 2026-09-09 session, format 3 is amended rather than followed by a format 4. The migration manifest gains the register conversion and the folder rebuild. A workspace created on the unamended format 3 (private cohort) is recognised by its layout, `TASKS.md` and `proposals/` present and `DOCUMENTS.csv` absent, and converted only after the user sees the full preview and confirms; there is no silent conversion. Federico accepted keeping the version number at 3 on that condition, 2026-09-09.

### D4 — Vocabularies are data
Phases, scopes and originators are tables in `PROJECT.md`; stages are a table in `STUDIO.md`. The library validates against them and the project skill edits them. Unknown values are confirmed by the user, never invented.

### D5 — No prose folders; every authored record is a document
Decisions, meeting records, site visits, plans, proposals and agreements are documents we author, with `originator` = the studio's code, a `kind` (`decision`, `meeting`, `site-visit`, `workshop`, `call`, `plan`, `proposal`, `agreement`, `contract`), and the coordinates of what they concern. They file through the same template as received documents. Listing decisions is `kind = decision`; supersession uses the `supersedes` column. Records that span phases use a firm-named phase (`campus` on TGS). `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/`, `agreement/` and `contracts/` are all retired. Revised 2026-09-10 from the earlier version that kept `decisions/` and `meetings/`.

### D6 — Site visits are a kind of event record
A site visit report is an event record like minutes, a call or a workshop, distinguished by kind and by the stricter observation, participant-reported and limitation sections the site-visit skill enforces. One record shape, several templates.

### D7 — Project Kind
`Kind` (`building`, `initiative`, `software`, extensible by the studio) is asked at init, recorded in `PROJECT.md` and as a registry column, and is advisory. `Type` (`internal`, `client`) is unchanged. Stage and default scope vocabularies in `STUDIO.md` are keyed by kind (B101 phases for `building`; `discovery, design, build, release, operate` as the shipped default for `software`; firm-named for `initiative`). Skills declare `kinds:` next to geographic scope per decision 0003 and warn on mismatch.

### D8 — The path is the firm's, the coordinates are AS's
`STUDIO.md` carries one document path template. `resolve`, `verify` and `migrate` are functions of the template and the row. The empty template means "record where the firm put it, never move it". Manifests are the only names AS reserves.

## Work Units

Each unit is one module with its upstream input, downstream output and the contract it must keep. Units are ordered by dependency; W1 and W2 are the critical path.

### W1 — `documents` library
- **Location:** `skills/receive/scripts/documents.py`; invoked via `<plugin-root>/skills/receive/scripts/documents.py <op>` by every other skill.
- **Operations:** `resolve` coordinates plus kind to folder via the studio template; `hash` sha256; `register` append or update rows; `move` with link rewrite; `verify` files versus rows, duplicates, missing prefixes; `migrate` preview and apply with rollback.
- **Upstream:** `STUDIO.md` stage vocabulary, `PROJECT.md` phase/scope/originator tables, `DOCUMENTS.csv`.
- **Downstream:** every skill in W4 to W8; the MCP tools in W9.
- **Contract:** stdlib only; every op has `--dry-run`; output is JSON on stdout, human text on stderr; exit codes distinguish invalid coordinates, unknown vocabulary, collision and IO failure; never renames a received file; never writes outside the project root.
- **Tests:** fixture project built from the TGS and Hotel Sonido trees; one test per op; casing and prefix rules; collision by hash; link rewrite across `../`.

### W2 — Vocabularies, Kind and path template in the manifests
- **Location:** `skills/studio` (path template, stage and default-scope tables keyed by kind in `STUDIO.md`), `skills/project` (`Kind` in identity; phase, scope, originator tables in `PROJECT.md`; `project vocab add|list|rename`; `vocab add phase` may create the empty phase folder on request).
- **Upstream:** user confirmation at studio setup and project init.
- **Downstream:** W1 validation; W3 to W8 reads.
- **Contract:** tables bounded by markers like the projects registry; header-keyed parsing; a rename is a migration through W1, not an edit; the template validator rejects unknown `{field}` names; a kind with no stage table falls back to the firm-named list with a warning.

### W3 — `DOCUMENTS.csv` record and `receive` skill
- **Location:** new `skills/receive/`, one verb, `user-invocable: true`; register schema in `docs/workspace-model.md`.
- **Inputs:** a file, folder, zip, or Gmail message id plus coordinates; missing coordinates are asked, defaults proposed from filename, sender and date on the document.
- **Outputs:** files under the resolved folder, rows in `DOCUMENTS.csv`, text sidecars, sheet index for drawing sets, WeTransfer expiry in `source`.
- **Downstream:** `tasklist` when a document creates an action; `project` when a document changes a fact.
- **Question flow:** `receive` always asks for the coordinates (phase, stage, scope, originator, date, kind), proposing defaults it can read: originator from sender, date from the document, stage from the project's active stage, scope from sheet series or filename, kind from type and context. Under any non-empty template the folder follows from the answers and nothing else is asked. Under the empty template one more question is asked, where, answered by pointing at a folder or by the file already being there. The filename is never changed in either case.
- **Contract:** the only writer of `DOCUMENTS.csv`; idempotent on rehash; extracted packages keep their internal tree; a document that spans phases becomes one file and one row per phase only when it is physically split, otherwise one row with `phase` on the primary and the others in `notes`.

### W4 — Registers to CSV
- **Location:** `skills/tasklist` (`TASKS.csv`), `skills/timetracker` (`TIME.csv`), `skills/invoice` (`INVOICES.csv`), studio portfolio view; `CHANGES.csv` and `SCHEDULE.csv` schemas documented, no writer yet.
- **Contract:** fixed headers per record in the workspace model; append-only history preserved; markdown tables read once by the migration and never again; prose sections move to `PROJECT.md` under named headings.

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
- **Location:** `skills/project` (init asks `Kind`; creates only `PROJECT.md`, the registers and host files; `status` calls `verify`), `skills/studio` (setup asks for stage vocabulary; migration adds W3 to W6 steps to the manifest), `resolve-context.sh` trimmed to identity.
- **Contract:** no scaffold folders at all; `status` reports unreceived files, orphan rows, duplicate hashes, expired sources, template violations; migration recognises an unamended format 3 layout and converts only after previewed confirmation (D3).

### W9 — MCP tools
- **Location:** as-mcp / as-platform.
- **Contract:** `documents.resolve`, `documents.register`, `documents.verify` wrap W1 with identical semantics and JSON; no path composition in the server.

### W10 — Spec, lint, tests, docs
- **Location:** `docs/workspace-model.md`, `docs/plans/commercial-records/design.md`, `scripts/lint.sh`, `tests/`, `README.md`, `CHANGELOG.md`.
- **Contract:** canonical-owner table gains `DOCUMENTS.csv`, `CHANGES.csv`, `SCHEDULE.csv` and the document kinds; loses `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/`, `agreement/`; lint enforces R1, R2, R4, R6; a reference page states the AIA 5.12, B101, A201 §3.12, NCS and ISO 19650 basis with Uniclass excluded and why.

### W11 — Fixture and dogfood
- **Location:** Local studio, private.
- **Contract:** the Local studio, re-migrated to the revised model (decisions, meetings, contracts under their phases, `campus` phase on TGS), is the acceptance fixture; W1 `verify` must pass on it unchanged; W3 must ingest the RBS 2025-12-05 zip, the TGS millwork submittals from the mailbox and one WeTransfer link; the questions from the 2026-09-09 session (latest set, what arrived since a date, everything tied to a CO, what is only in email, what expires) must each be one register query.

## Dependencies and Risks

- W2 before W1 validation; W1 before everything else; W4 and W5 before W8's migration step; W9 after W1's JSON contract is frozen.
- The good-morning skill and ALPA `global_tasks.md` read `TASKS.md`; they break the day W4 ships unless updated together.
- Hosts without a shell (claude.ai, Cowork) depend on W9; until then `receive` is local-only.
- Windows path length with deep trees and long RBS filenames; test in W1.
- Mail ingestion depends on the Gmail token expiry problem (`reference_gmail_mcp_oauth_testing_expiry`); W3 must degrade to "file from disk" cleanly.
- Migration on studios with per-folder `.gitignore` artifact rules: the manifest must carry those rules to the root, or files silently start tracking.

## Pending Decision

- **Q1, release disposition, Federico:** which work units ship in 1.5 with Sharmila and which wait for the next candidate. Recommendation: W1, W2, W3, W8, W10 in 1.5, since shipping format 3 without them buys a second migration; W4 and W5 in 1.5 only if the migration stays one step; W6, W7, W9 and W11 beyond the fixture in the next candidate.

## Closed Questions

- **Q2:** the studio's own originator code is a vocabulary entry the studio sets (`local` for Estudio Local; `tgs` on the TGS project where the studio acts on the owner's side). The plugin ships no reserved word.
- **Q3:** `CHANGES.csv` is defined and migrated in this cycle; its writer is a later change-order skill.
- **Q4:** no generated views in this cycle; the register is the only view. Views remain possible later because they are a function of the row.
- **Q5:** `vocab add phase` records the phase; it creates the folder only with `--folder`. Stage, scope and originator folders appear only when a file is filed.

## Pending Work

- **T0029, fixture:** the Local studio still has `decisions/`, `meetings/` and `contracts/` at project roots and no `campus` phase on TGS. Re-migrating it is the first implementation step, before W1's tests, so the fixture matches this plan.

## Execution Order

1. W2 vocabulary and template tables, so W1 has something to validate against.
2. W1 library with its test fixture; freeze the JSON contract before anything calls it.
3. W3 `receive`, proven on the RBS 2025-12-05 zip and one mailbox attachment.
4. W8 init and status, so a new project starts on the model and an old one reports drift.
5. W4 registers to CSV, together with the good-morning skill and the ALPA task tracker.
6. W5 and W6 in either order; they only depend on W1 and W3.
7. W10 spec, lint, tests and docs, updated as each unit lands and completed last.
8. W11 fixture re-migration and the five acceptance queries.
9. W7 and W9 after the release line is drawn; they are candidates for the next release regardless of Q1.

## Definition of Done

- W1 passes its tests on the Local fixture and `verify` reports zero findings on TGS Campus and Hotel Sonido.
- No SKILL.md or template in the repo contains a composed document path; lint proves it.
- A fresh project initialised by `project init` has `PROJECT.md`, the registers and host files, and no folders.
- A firm template other than the default places, verifies and migrates a fixture project correctly.
- `receive` files a zip, a single PDF and a Gmail attachment into the right folder with a row each, on Claude Code and Codex.
- The workspace model, CHANGELOG and README describe the model in the same words as this plan, and the release notes state which work units shipped and which are deferred.
