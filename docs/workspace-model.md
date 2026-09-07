# Workspace and memory model

Architecture Studio separates the installed plugin from the user-owned worksurface. Plugin updates replace plugin code; they do not own or migrate studio records silently.

## Studio

```text
studio/
├── .as-folder.json           immutable studio-folder identity
├── STUDIO.md                 settings and project registry
├── AGENTS.md                 Codex working instructions
├── CLAUDE.md                 Claude Code working instructions
├── .mcp.json                 studio-only connector boundary
├── .agents/skills/           firm-created Codex skills
├── .claude/skills/           firm-created Claude Code skills
├── Operations/               ongoing studio operations
├── Standards/                firm-wide standards and reusable templates
├── References/               external source material and code references
├── TASKS.md                  optional portfolio-mode action register
└── Projects/
```

`/as:studio` creates or inspects this structure only after the user confirms the exact target. Setup asks separately for the project-naming policy and folder taxonomy. The AS folder standard shown above uses `Projects/{Client Account or Internal}/{YYYYMM} {Project Name}`; a firm may instead record its own safe relative roots and plain-language convention. The empty connector manifest belongs at studio level because credentials and integrations are organizational concerns, not project records. There is no separate studio `templates/` directory.

`STUDIO.md` and `PROJECT.md` carry integer `Format version` fields. Workspace format 3 writers accept format `3`, fail closed on older or unknown versions, and require an explicit previewed migration before changing them. Registered projects must resolve physically below the non-symlinked studio root.

The `STUDIO.md` Projects table is bounded by `<!-- projects:start -->` / `<!-- projects:end -->` and parsed by header name. Its columns are Project ID, Project, Client, Code, Type, Status, Folder, Opened, and Folder ID. `Folder` is a readable cached path; `Folder ID` is the durable pointer. One unique valid row remains resolvable in every supported status, even after its folder moves inside the studio; status reports the stale readable path as drift. Legacy format-3 rows without Folder ID remain path-resolved until explicitly adopted. Status is advisory context rather than an action gate. Studio-root resolution returns structured `invalid-project` diagnostics for registered rows whose complete identity or filesystem boundary fails validation, while `no-projects` is reserved for a truly empty registry.

Every folder directly referenced by an AS manifest or index carries `.as-folder.json`. The same config is used at the studio root, the four managed roots, intermediate grouping folders created or adopted by AS, and registered project roots. It deliberately contains only `format`, immutable `folder_id`, and `kind`; human names and paths stay outside it so renames do not create identity drift. Ordinary content folders such as `meetings/` or `docs/plans/` do not receive configs merely for existing.

## Project

```text
Projects/Smith Institution/202609 Museum Expansion/
├── .as-folder.json           immutable project-folder identity
├── PROJECT.md                sourced project facts
├── AGENTS.md                 Codex project instructions
├── CLAUDE.md                 Claude Code project instructions
├── decisions/                durable reasoning and supersession history
├── meetings/                 typed meeting records
├── site-reports/             field observations and limitations
├── docs/plans/               work plans
├── proposals/                optional project-local fee proposals
├── agreement/                optional contract context, SOWs, and amendments
├── INVOICES.md               optional user-directed invoice ledger
├── TASKS.md                  default project-mode action register
├── TIMELOG.md                user-confirmed time
├── product-library.csv       optional FF&E library
├── epd-library.csv           optional EPD library
├── .agents/skills/           project-only Codex skills
└── .claude/skills/           project-only Claude Code skills
```

## Canonical ownership

| Information | Canonical owner |
|-------------|-----------------|
| Studio settings and project registry | `STUDIO.md` |
| Sourced project facts | `PROJECT.md` |
| Durable decisions and supersession | `decisions/` |
| Meeting source context | `meetings/` |
| Field observations and limitations | `site-reports/` |
| Planned work | `docs/plans/` |
| Proposal terms and lifecycle | Individual files in `proposals/` |
| Agreement context, SOWs, and amendments | `agreement/` |
| Invoice facts and billing history | `INVOICES.md` |
| Actions and status history | Project `TASKS.md`, or one studio `TASKS.md` in portfolio mode |
| Confirmed durations | `TIMELOG.md` |
| FF&E product data | `product-library.csv` |
| Optional persisted EPD data | `epd-library.csv` |

Records cross-reference one another by stable identifiers. Meetings and site reports may propose facts, decisions, or tasks, but promotion into the canonical record requires an explicit handoff and user confirmation. `PROJECT.md` points to decisions rather than maintaining a second decision index.

Format 3 uses the project as the single durable entity for internal and client work. Project ID, free-form display name, client code, registered folder, and Folder ID are separate values. Project and Folder IDs are immutable; human names and paths are not. `STUDIO.md` records an advisory naming policy (`as`, `firm`, or `none`) separately from its folder taxonomy (`as` or `firm`). The AS Project ID suggestion is uppercase `YYMMDD-CCC-PROJECT-NAME`; the AS folder convention is human-readable. Firm-defined work preserves the user's conventions, and convention mismatch never invalidates an otherwise safe, uniquely registered project. Universal identity records Type, Status, Created, Client code, and Client.

Canonical singleton records use uppercase names such as `PROJECT.md`, `TASKS.md`, `TIMELOG.md`, and `INVOICES.md`. Directories and individual repeatable records use lowercase kebab-case, including `decisions/`, `meetings/`, `site-reports/`, `docs/plans/`, `proposals/`, and `agreement/sow/`. Proposal filenames use `YYYY-MM-short-title-proposal-rev-NN.md`, while the document itself shows `Rev. NN`. Project IDs follow the studio's advisory policy and are not derived from directory names.

Commercial records remain inside their owning project. Proposal files are discovered directly without a studio-wide register or firm-wide number. Sending records a SHA-256 checksum for the protected issued-terms block; later lifecycle evidence stays outside it, and changed terms use a new revision. Agreement context may cite that project-relative path and checksum without copying the proposal. Invoice records may use an agreement when one exists or explicit user input when it does not. These tools surface context but do not enforce a proposal, agreement, invoice, or project-status sequence.

Studios default to project task mode: each project has one writable `TASKS.md`, and an all-project list is a read-only merged view. A studio may explicitly choose portfolio task mode, where one studio-root `TASKS.md` is authoritative and every task carries a Project ID. The modes are mutually exclusive; populated registers require a previewed migration rather than an automatic merge or split.

Canonical studio and project records use a one-writer operating model in workspace format 3. Task-mode changes preflight all affected registers and keep rollback copies until the new topology and manifest commit together. The format-2 migration previews a complete identity manifest, preserves registered project folders, adds project Folder IDs, updates only known structured references, converts registered global proposal files into project-local records with legacy-number metadata, and restores its scoped backup—including newly created folder configs—if mutation or verification fails. Standalone migration also snapshots a recognized generated `CLAUDE.md` before replacing it with the canonical `@AGENTS.md` import; custom instructions require separate review, and a valid standalone root `PROPOSALS.md` blocks project-only mutation until a studio-owned commercial migration is confirmed. Simultaneous edits from multiple Codex or Claude sessions, or synchronized-folder clients, are not supported.

This structure keeps records readable without Architecture Studio and lets them travel through the firm’s existing local, network, or synchronized storage system.

Project initialization creates both empty skill roots shown above. Skills created under the active host's project root are project-only; firm-wide skills belong at the studio root. Start or restart Codex or Claude Code from the intended studio or project scope if a newly created skill is not visible.
