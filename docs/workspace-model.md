# Workspace and memory model

Arch Studio owns semantic procedures and schemas; the user owns studio/project records. R5-HN MCP workflows use native host tooling and preserve the R4 local record shape. `Format version` remains `3`; `Document model` is `1`. These fields identify the current schema, not a migration instruction. Existing live workspaces are neither converted nor used as implementation fixtures.

## Native mutation sequence

For a canonical mutation, apply these stages to the complete affected set defined by its owning
operation below. They are execution prerequisites, not a required user-facing checklist, Arch Studio runtime
or journal format. Read-only work skips them. Use a native provider revision/recovery facility or
ordinary task-specific tools with demonstrated equivalent guarantees.

1. **Inspect.** Resolve exact authority, identities, current revisions and the complete read/write
   set. Discover pending operations before starting another overlapping mutation; reconcile or stop.
   Establish the available writer protection and inspect applicable permissions, ownership and ACLs.
   Ordinary read/write access or mode bits alone do not establish ACL absence or preservation.
2. **Prepare.** Retain the full original bytes and access metadata of every affected existing file,
   absence conditions for new paths, and the full intended bytes/trees for every replacement or
   addition. Retain exact intent, permanent IDs and publication order. For a multi-file operation,
   this entire set must exist before the first canonical change; a hash, intended row, generated
   code or in-memory object cannot substitute for retained content.
3. **Verify preparation.** Finish the native durable-save operation for **all** recovery content and
   its discoverable pending reference. Establish successful complete writes, flush/synchronization
   or equivalent provider durability, then independently reopen/read every retained original and
   prepared file/revision. Compare actual bytes/tree membership and metadata to the intended set,
   and validate its schemas and cross-file relationships. Only this verified complete set is ready
   to publish. Saving recovery files without reading them back, or validating each file only when
   its publisher is reached, does not satisfy this stage. A failed check leaves canonical state
   untouched. No particular filesystem call is universal; use actual native guarantees and stop
   when the required durability or applicable access metadata cannot be established.
4. **Apply.** Publish only the verified set, in its retained order, with fresh source/revision and
   access-metadata guards before each change. Each register/manifest replacement exposes complete
   old or complete new bytes. Preserve durable pending/progress evidence throughout a recoverable
   multi-file sequence; a mixed intermediate set remains pending. A publisher cannot mark the whole
   operation complete just because the last write returned successfully.
5. **Verify result.** Reopen all actual destinations, including access metadata, and verify the
   entire affected set: intended changes, permanent identities, hashes, history, links, removals
   and preserved unrelated data as applicable. Reconcile interruption or uncertain results from
   the retained set and fresh guards; never restore over intervening edits or replay an allocation.
6. **Complete.** Only after the full result verification passes, persist the completion state and
   report the observed outcome. Failed or unavailable verification retains an explicit pending or
   incomplete result with its recovery reference. An exact retry verifies prior application before
   adding any record/event. A completion receipt alone is not evidence that these stages occurred.

For example, registering `A.md` prepares the original DOCUMENTS.csv, A.md absence condition,
complete prepared A.md and complete prepared DOCUMENTS.csv, and verifies all retained content
before either destination changes. Synchronizing project/studio status prepares and verifies both
complete original manifests and both complete replacements before publishing either. The native
method remains host-selected; no Arch Studio executable is supplied or required.

## Boundaries and identity

`STUDIO.md` is the studio authority and project registry. `PROJECT.md` alone establishes an implicit project boundary. A valid standalone project is supported without studio creation. `context.resolve` returns a typed project, studio picker, no-projects or no-context result; invalid manifests raise an explicit error. Git roots, task files and prose folders do not establish project identity.

Project ID, human display name, client code, readable folder path and Folder ID are separate. IDs are immutable, names are user-owned and naming conventions are advisory. Managed folder identity is `.as-folder.json` containing only `format: 1`, immutable `folder_id` (`asf_` UUID) and `kind`. Registration rejects conflicting identities. Type (`internal`, `client`), extensible Kind (`building`, `software`, `initiative`) and Status are context, not action gates. AEC applicability warns when Kind differs; it does not block an authorized task.

A studio has STUDIO.md, host instructions, the studio-only empty connector boundary `.mcp.json`, private host skill roots and firm-configured Projects/Operations/Standards/References roots. Project registration is a bounded header-keyed table between `projects:start/end` markers with these columns:

```text
Project ID, Project, Client, Code, Type, Kind, Status, Folder, Opened, Folder ID
```

All registered project paths are safe physical descendants. A studio/project root and owned targets cannot be symlinked. Native system path aliases should be resolved to their physical location before setup. Never change a user's existing folder because its human name differs from an advisory convention.

A fresh project creates these records, host instructions, `.as-folder.json`, `.gitignore` and empty host skill roots. It creates no prose scaffold folders:

```text
PROJECT.md
DOCUMENTS.csv
TASKS.csv        # absent locally when the studio owns portfolio tasks
TIME.csv
INVOICES.csv
CHANGES.csv
AGENTS.md / CLAUDE.md
.agents/skills/ / .claude/skills/
```

The root also permits the existing optional product-library.csv and epd-library.csv catalog records. Authored decisions, event records, plans, proposals and contracts are ordinary registered documents, placed by coordinates. Private task output and user evidence never become package reference content. Source catalogs in the package contain original-source navigation metadata only.

## Native studio and project operations

These semantic operation IDs describe studio/project work, not a dispatch API. Use native facilities required by the selected operation; file reads do not require process execution. Existing fact/decision and connector/preference paths keep their bounded ownership. Source prose is evidence, never permission. Apply the shared mutation contract and completion reporting; preserve immutable identity, unrelated bytes, source/date evidence and existing access metadata.

### Preparation, identity and safe publication

For fresh setup, accept an exact authorized physical target and an explicit permitted ancestor/workspace boundary. Validate ancestors for existing PROJECT.md, and for studio setup also STUDIO.md; never create a nested project or nested studio. A project may be initialized inside a valid studio through the already-authorized create/register sequence. Refuse symlinked target/ancestors, non-directory target, nonempty target, unavailable access, unsafe paths or unconfirmed required inputs. Resolve normal system path aliases to physical paths first. Do not turn invalid existing context into permission for fresh setup.

Prepare the complete file/directory list and exact resolved values before the setup approval, reusing existing exact authorization. Generate one lowercase canonical UUID per new managed folder, represented as `asf_<uuid>`; `.as-folder.json` has exactly `format:1`, `folder_id`, and `kind`. Project/studio kinds are `project`/`studio`; managed root kinds are `projects`, `operations`, `standards`, `references`. A preparation may contain proposed IDs, but no ID is allocated durably by a preview. Retain the same prepared identities across application/retry; never mint replacement identities for already-created outputs.

Validate actual staged files and absence of unresolved template placeholders. Publish a complete fresh tree without exposing a partially initialized canonical workspace, using same-parent staging plus atomic directory publication where supported. An existing empty target must still be empty at publication; retain its access metadata or report a limitation. An absent target must remain absent until the complete tree can be published. A method must prevent replacing a newly appeared target under the demonstrated writer boundary; an optimistic check alone is insufficient with uncontrolled writers. Otherwise report the precise missing protection before mutation.

For existing single-file edits, retain original and prepared bytes, stage and validate actual bytes, recheck current identity/bytes under the available protection, preserve access metadata and publish atomically. For multi-file status, registration/topology or configuration changes, use the shared recoverable publication contract: retain originals, exact intended file set/order and progress before first write, detect pending state, and block conflicting operations until reconciliation. Recheck every affected source and metadata immediately before its publication. A supported controlled workspace may use a recorded recoverable sequence; no claim of atomic multi-file visibility or protection from uncooperative external writers follows. If that guarantee cannot be provided, stop before mutation. Never roll back over a changed file. After interruption inspect actual bytes and identities, complete or restore only the proven safe set, and report partial/pending state accurately.

A repeated exact setup is a no-op only when the existing identity and entire intended setup set agree with the retained preparation. A partial setup is a recovery case, not a new initialization. Existing workspaces with other content are not automatically converted. A repeated field/registration/configuration request is a no-op when its exact desired state already holds; it must not duplicate rows, append spurious history or replace identities. Readback must cover the complete affected set and the invariant that each project has one canonical task owner.

### `studio.init`

Required confirmed inputs: studio name; exact target; working units; country, State/region and city (each may be `No default`); project naming policy `as`, `firm` or `none`; Project ID convention; advisory folder taxonomy and project folder convention; four managed-root paths; task mode `project` or `portfolio`; document path template; nonempty stage and proposed-scope vocabularies keyed by Kind. Defaults are proposals, not inferred firm standards.

Managed-root keys are exactly projects/operations/standards/references. Their paths are safe nonempty studio-relative paths, distinct and nonoverlapping; they cannot collide with reserved root files, host skill directories or each other. Values must not escape through `..`, absolute paths or symlinks. Default root suggestions are Projects/Operations/Standards/References. Default document template is `{phase}/{stage}/{scope}/{originator}/{date}`; allowed fields are DOCUMENTS.csv columns, and an explicitly empty template is valid. Reject unknown/unbalanced template fields or literal path escape. Vocabulary entries are nonempty unique safe single path components; preserve confirmed casing. Defaults by Kind are building: 0-predesign,1-sd,2-dd,3-cd,4-procurement,5-construction,6-closeout; software: 0-discovery,1-design,2-build,3-release,4-operate; initiative: 0-plan,1-deliver,2-review. Proposed scopes are building: architecture,interiors; software: product,engineering; initiative: operations. Confirm overrides and arbitrary additional Kinds; a `*` stage vocabulary may cover an otherwise unmatched Kind.

Fill `studio/templates/studio/STUDIO.md`: settings use exactly one Setting/Value row each for Format version=3, Document model=1, Studio, Folder ID, Working units, Country, State/region, City, Task register, Project naming, Project ID convention, Folder taxonomy, Project folder convention, Document path template; each managed root has `<Title> root` and `<Title> folder ID`. The empty projects table has the canonical ten columns and one projects marker pair. Stages and default-scopes tables each have one marker pair with Kind/Value columns and one row per confirmed value. Substitute row placeholders with complete table rows, never a comma-separated cell standing for multiple entries.

Create STUDIO.md, `.as-folder.json`, studio AGENTS.md and CLAUDE.md (use the forwarding `skills/project/templates/CLAUDE.md`, with `@AGENTS.md`; the full legacy studio CLAUDE template is not used by this native operation), `.mcp.json` containing exactly `{"mcpServers":{}}`, `.agents/skills/`, `.claude/skills/`, and each managed root with its `.as-folder.json`. Portfolio mode additionally creates root TASKS.csv containing only the canonical task header plus LF; project mode creates no root task register. Do not create projects, Git repositories, accounts or additional prose scaffold directories. Disclose the workspace/model-provider data boundary in the setup preview; setup does not configure external connectors.

### `project.init`

Required confirmed inputs: exact target, immutable Project ID, display name, Type (`internal` or `client`), advisory Kind and Status, client and client code, Created date at YYYY-MM-DD precision, nonempty phases/scopes/originators, and applicable stage vocabulary. Preserve supplied names/casing and sources; reject line breaks/pipes in table cell values rather than silently changing them. Display name, Project ID and Folder ID are distinct. Status is an explicit label, not derived from activity.

Use `skills/project/templates/PROJECT.md`. Its Identity table has Field/Value/Source/Date; Format version=3, Document model=1, Project ID, Project, Type, Kind, Status, Created, Client code, Client and Document path template each occur once. Initial sources are `project setup` with the confirmed Created date. Fill bounded phases/scopes/originators tables with Value rows; fill standalone stage defaults with Kind/Value rows. Registered projects use the owning studio's template/stages; their local standalone defaults do not override that authority. The record links point to DOCUMENTS.csv, TIME.csv and INVOICES.csv. Tasks links point to local TASKS.csv in project mode or explicitly to the owning studio portfolio register filtered by Project ID.

Create PROJECT.md, `.as-folder.json`, AGENTS.md, CLAUDE.md (`@AGENTS.md`), `.gitignore`, `.agents/skills/`, `.claude/skills/`, and empty DOCUMENTS.csv, TIME.csv, INVOICES.csv, CHANGES.csv with the exact headers in this document/template assets and one LF. In project mode also create empty TASKS.csv with its exact header; portfolio mode requires an explicit validated owning studio already in portfolio mode and omits local TASKS.csv. `.gitignore` may contain the standard user-artifact exclusions `*.pdf`, `*.zip`, `*.ifc`, `*.rvt`, `.as-document-transaction/`; it does not initialize Git. Never create project `.mcp.json` or phase/document scaffold folders implicitly. Inside a studio, initialize then register using the same approved identity/preparation; interrupted registration never authorizes recreating the project.

### `studio.status`, `project.status` and `studio.register`

Studio status is read-only: report settings, task mode and every registry row including archived/unknown statuses and invalid identity/path/metadata findings. Validate row Project ID, Folder ID and PROJECT.md values for Project, Client, Code↔Client code, Type, Kind, Status and Opened↔Created. IDs and Folder IDs are unique. Cached relative Folder may resolve by unique physical Folder ID inside the authorized studio; report drift without silently rewriting it. Invalid, missing or unreadable evidence is not an empty registry or a hidden project. Project status reports exact context/identity and applies the receive-owned document verification specification for document findings; task/invoice queries remain their owners' semantics and do not derive complete state from missing evidence.

Register only an existing valid model1 project physically inside the studio, with nonconflicting immutable IDs and a safe studio-relative Folder. Derive one row from observed PROJECT.md/identity: Project ID, Project, Client, Code=Client code, Type, Kind, Status, Folder, Opened=Created, Folder ID. Validate the whole current registry before mutation. Repeating that exact registration is a no-op; same Project ID/Folder ID/path identifying different data is a conflict, not an overwrite. Append one row, preserving all unrelated registry/settings bytes.

Project-mode registration requires a valid local task register and no competing studio portfolio owner. Portfolio registration requires a valid studio task register; a project-local TASKS.csv is removable only if it is valid and header-only. A populated, missing required or malformed register blocks registration/topology mutation. Coordinate removal of an empty local register, project task-pointer text and new registry row as one recoverable affected set. No existing task is moved or merged. Registration does not silently correct unrelated manifest drift.

### `studio.set-status`, `studio.archive`, `studio.set-naming`, `studio.task-mode`

Status takes an exact uniquely registered Project ID and explicit single-line label; archive requests the label `archived`. Validate the complete registry and target before mutation. Change only the selected row's Status and PROJECT.md Identity Status, retaining its existing Source/Date columns unless the user explicitly authorizes sourced metadata changes. Preserve all other fields, including Agreement content, IDs, Created and other projects. Treat the two files as a recoverable unit. Same value in both files is a no-op; preexisting disagreement is a reported conflict, not automatic repair. Read back both exact values before success. No commercial acceptance, completion, billing or permission follows from status.

Naming takes policy as/firm/none and a confirmed Project ID convention. Change only those STUDIO settings; do not rename folders/IDs or change taxonomy. Same values are a no-op. Preserve other settings and registration rows.

Task-mode accepts project/portfolio. Same valid topology is a no-op. Before switching, validate all registrations and every current canonical task register, requiring exact current header and zero rows. In project mode there must be one local register per registered project and no studio TASKS.csv; in portfolio mode there must be one studio register and no local project TASKS.csv. Missing, malformed, populated or competing registers stop the entire operation before any write. Switching project→portfolio creates one empty studio TASKS.csv and removes the empty project registers; reverse creates one empty register per project and removes the empty studio register. Update only STUDIO Task register and each project's task-pointer text together with that file set. Preview all paths and preserve all identities/settings/other content. Use the recoverable multi-file publication guarantees, not an automatic populated-register merge/split. New register permissions must not widen any effective preexisting access; if equivalent ownership/access cannot be preserved across the target topology, report a limitation before mutation.

### `project.vocab`, `project.facts`, `project.decision`

Vocab axes are phase/scope/originator, owned by the project bounded tables. List is read-only. Add an explicitly confirmed safe unique component once; existing exact value is a no-op. Rename requires one exact old value and an absent new value; preserve row order and unrelated bytes. Inspect DOCUMENTS.csv and source placements before determining whether the value is used. An unused rename changes only that table. A used rename must follow receive-owned coordinated relocation/link/hash/history semantics together with the vocabulary update, preserving issued/accepted protection; lacking that route, stop before the manifest edit. Stage changes are studio authority (standalone manifest when no studio) and require explicit firm vocabulary scope. Only an explicitly requested phase-add folder creates an empty phase directory.

Facts distinguish confirmed current facts, proposed choices and unresolved information. Preview the exact PROJECT.md section/cells, source locator and effective date; save only approved sourced assertions. Keep Agreement edits with agreement, Status synchronization with studio, and reasoning with decisions. Preserve unrelated sections and provenance; never promote every statement in a saved source, infer confirmation or treat raw chat as archived. A repeated exact fact/source/date is a no-op. Conflicting evidence requires clarification or explicitly labeled uncertainty, not silent replacement of a sourced fact.

Decision authoring takes the actual choice, context, considered options, deciders, proposed/decided status, rationale, consequences and exact sources; preserve unknowns and proposal status. Read all registered decision records to allocate one permanent next decision number above historical numbers, separately from the receive-owned D-number. Ambiguous numbering or unreadable prior decisions blocks allocation. Retain the selected number/preparation across retry. Fill `skills/project/templates/decision.md` and use receive-owned resolve/register with confirmed coordinates and kind=decision. The document ID, byte hash, filename/placement, source and history follow receive semantics; do not invent a parallel decision index. Supersession requires explicit authorization and a new registered document whose supersedes names the original D-ID; preserve original bytes and history. Listing uses document kind=decision. A saved decision does not automatically update current facts, tasks or Agreement.

### `studio.preference` and `studio.connectors`

Default-assistant preference follows the owning Norma preference protocol with native tooling, actual host configuration evidence, chosen scope and the exact authorized owned-block diff. No supplied path alone proves the host reads it. Retain unrelated bytes, approval/current-source linkage, duplicate/malformed-block refusal, stale protection and readback. No/cancel writes nothing; unavailable persistence gives session guidance without claiming a save. Background lifecycle update checks are installed-package features, outside this MCP operation, and must not create or inspect their state.

Studio connector setup owns only studio-root `.mcp.json`; project folders never receive it. Initialization is empty. For an explicitly requested later server configuration, verify the host's connector format and supplied server identity, preview exact scoped JSON change, preserve other entries and publish only with existing concrete authorization. Unknown endpoint/options/credentials are missing inputs, not invented values. Actual authentication or external service actions require separately available capabilities and authorization; a saved manifest alone proves neither connection nor permission.

## Coordinates and firm placement

PROJECT.md owns bounded `phases`, `scopes` and `originators` tables (`Value` column). STUDIO.md owns a `stages` table (`Kind`, `Value`) and `Document path template`. A standalone project carries stages/template itself. The shipped stage names are Arch Studio-owned defaults, not copies or assertions of an external professional standard. A firm may replace or extend them; unknown vocabulary needs confirmation. Stage order is represented by the firm's stage value prefix. Confirmed names/casing remain unchanged.

The default template is `{phase}/{stage}/{scope}/{originator}/{date}`. Template fields name DOCUMENTS.csv columns. Firms may reorder/drop fields or use other explicitly supplied register fields. Values are safe single path components; paths must remain inside the project. An empty template means receive at an explicitly chosen existing/in-project folder without imposing placement. The document date is its supplied date, preserving YYYY-MM precision when a day is unknown. Arrival time is distinct.

`documents.resolve` owns every path. Skills supply coordinates, kind and template metadata; they never compose folders. Scoped `SCHEDULE.csv` placement projects the firm template onto its phase/stage/scope fields, in the firm's order, then appends the reserved filename. Other FF&E record semantics remain with master-schedule. No additional placement/procurement split is implied.

A project-spanning document has one primary confirmed phase and records other phases in notes, unless the original is physically split. Received names and package internal trees remain intact. New folders appear when documents are received, except an expressly requested empty phase folder.

## Canonical owners

| Information | Owner |
|---|---|
| Studio settings and project registry | studio → STUDIO.md |
| Current sourced project facts and vocabularies | project → PROJECT.md |
| Document identity, placement, revision links, provenance, history | receive-owned document library → DOCUMENTS.csv |
| Durable choices and rationale | project → document kind `decision` |
| Meeting/event account | meeting-minutes → kind `meeting` |
| Site observations and limitations | site-visit-report → kind `site-visit` |
| Durable work plan | workplan → kind `plan` |
| Proposal terms and lifecycle | proposal → kind `proposal` |
| Governing agreements/SOWs/amendments | agreement → kinds `agreement`, `contract` |
| Sourced agreement context and scope | agreement → bounded Agreement section in PROJECT.md |
| Action lifecycle | tasklist → canonical TASKS.csv |
| Confirmed duration | timetracker → TIME.csv |
| Billing facts/history | invoice → INVOICES.csv; issued artifact kind `invoice` |
| Project change register | CHANGES.csv defined; no automated writer in R4 |
| Adopted scope schedule | master-schedule → resolved SCHEDULE.csv |
| Reusable product / optional EPD data | product-library / existing explicit-save EPD owners |

Receive owns the document-register procedure. Other authored-record owners follow that same semantic procedure; no nested harness invocation, installed library or dispatcher is required. Saving an event or plan does not automatically promote facts, decisions, tasks, time, acceptance or payment. Exact prior user authorization persists.

## CSV contracts

UTF-8, RFC-style CSV quoting, LF record separators and exact headers. Empty cells mean unknown/not supplied, never zero or inferred permission. Preserve malformed files without rewriting them. The headers and rules below are authoritative without executable source. New document row schemas are also described by `schema/documents.schema.json`.

DOCUMENTS.csv:

```text
id,sha256,filename,path,type,kind,phase,stage,scope,originator,date,received_at,title,sheet,package,status,supersedes,source,change_id,notes,history
```

IDs are permanent `D000001` values. `path` is project-relative; `sha256` describes exact bytes (or a package tree hash covering every file and directory, including empty directories). `source` is a JSON object carrying supplied provenance, such as type, original URL, message ID, edition or expiry. `history` is an append-only JSON array in the same register, not a second ledger. `supersedes` names an existing document ID; a newer date alone does not establish revision lineage. Filesystem registration does not certify source truth, approval, applicability or visual quality.

TASKS.csv uses the same header in project and portfolio modes:

```text
id,project_id,description,owner,due,status,created,updated,completed,cancelled,source,related,history
```

IDs are permanent T-numbers allocated above the greatest historical ID. Project mode owns a project-local file; portfolio mode owns one studio file filtered by Project ID. All-project project-mode views are read-only merges, with qualified display IDs. Source is an exact `D000001#item` or `conversation:YYYY-MM-DD#instruction-N`. Lifecycle states are open, in-progress, blocked, completed and cancelled. History stays in its JSON cell. Reopen preserves previous closure dates/history. Switching task topology operates only on empty current registers; no legacy merge/split converter is included.

### Native task operations

Read the entire canonical register before a task operation. Header order is exact; every row has
13 cells. Validate UTF-8/CSV, unique IDs matching `T` plus at least four decimal digits, nonempty
project_id/description/source, declared statuses, actual calendar dates (`YYYY-MM-DD`, or supplied
`YYYY-MM` precision), and a JSON array in each history cell. Created/updated are required;
due/completed/cancelled may be blank, except a completed/cancelled row requires its corresponding
closure date. Reject invalid rows anywhere in the register, including other portfolio projects;
preserve the entire original byte-for-byte until an explicitly authorized repair. Do not replace
an old header with this one or treat a missing file as an empty register.

The native context result identifies exactly one owning TASKS.csv. In project mode each row must
carry that project ID. In portfolio mode each row must refer to a registered project, and writes
select only the exact intended project; IDs allocate across the entire portfolio. Read-only
all-project views qualify IDs as `project-id:task-id`, keep source register identity, and report
missing/malformed projects independently. They are not a second writable register.

| Semantic operation | Required facts and transformation |
|---|---|
| `tasks.list` | Read and validate the whole register, then return the selected project's rows and owner path. Do not mutate, allocate IDs or append history. |
| `tasks.add` | Require an observable nonempty single-line description and exact provenance. Owner defaults to `Unassigned`; due and related default to blank. Allocate `T` + max numeric historical ID + 1, padded to at least four digits (empty register starts `T0001`). Set project_id to the selected project, status `open`, created/updated to the actual operation date, closure cells blank, and history to one `created` event. Preview the actual row if its exact content is not already authorized. |
| `tasks.update` | Select exactly one existing task ID in the intended project. Only description, owner, due, related and an active status (`open`, `in-progress`, `blocked`) are routine-change fields. Preserve ID, project_id, created, source, closure dates and prior history. Never close through update or reactivate a closed task; explicit lifecycle operations own those changes. Metadata on a closed row may change while its status remains unchanged. |
| `tasks.complete` | Set an active task to `completed`, set completed to the operation date. A cancelled task must be reopened first. Already completed is a no-op. Preserve cancelled if historically populated. |
| `tasks.cancel` | Require the user's nonempty reason; set status `cancelled` and cancelled to the operation date. Already cancelled is a no-op. Preserve any historical completed date. |
| `tasks.reopen` | Require the user's nonempty reason; set status `open`, preserving all previous closure dates/history. Already open is a no-op. |

Source is either a real registered document ID plus item locator (`D000001#item`, six or more ID
digits, nonempty whitespace-free item) or a specific user instruction
(`conversation:YYYY-MM-DD#instruction-N`). Validate the actual date and registered document
membership in the selected project's DOCUMENTS.csv for document sources. Do not fabricate a
document registration or promote an action from a plan/event merely because it is mentioned.
Same source in the selected project requires linking/updating the existing task or a user-confirmed
nonempty distinct reason for a genuinely different action. A confirmed distinct task still needs
retry detection; a repeated distinct reason does not authorize repeated additions.

History is embedded JSON, quoted as one CSV cell. Preserve earlier events as data, in order.
The initial event is `{"event":"created","date":"YYYY-MM-DD","distinct_reason":""}`;
use the supplied distinct reason when applicable. A real mutation appends exactly one event with
`event` equal to `update`, `complete`, `cancel` or `reopen`, `date` equal to the actual operation date,
`before` equal to the full prior row except its history cell, and `reason` equal to the supplied
reason (otherwise empty). Set updated to that same date. Do not rewrite past events or clear old
closure evidence. Descriptions, source tokens and required reasons must be nonempty single-line
text without control characters or `|`; dates and JSON keep their declared formats.

### Task mutation, repeat and recovery evidence

Task mutations must expose either the complete old TASKS.csv or the complete new TASKS.csv at
publication, never a partially rewritten canonical register. Stage and validate the complete new
file, preserve required access metadata, and use native atomic replacement with the required
conflict protection, or a provider conditional revision with equivalent complete-state visibility.
Finish and close the staged write, handling short writes and write failures before publication.
Reopen the actual staged file and verify its complete bytes match the prepared replacement; parse
and validate those actual bytes, not only the in-memory row set. A short or failed staged write
must never be published. Apply equivalent prepared-revision validation for a provider method.
Do not truncate the canonical file, open it for overwrite and stream replacement rows, or copy
staged bytes over the existing file in place: a backup does not close the crash window between
truncation and the completed write. Apply the shared single-record and ID-allocation guarantees.
Retain the exact prior bytes/revision and prepared replacement
before publishing. Preserve existing file permissions, applicable ownership and ACLs; a replacement
that changes access is not equivalent to an in-place edit. Verify the chosen native method can
preserve the observed access metadata and stop if it would widen access. Use a native conditional
write or demonstrably exclusive access covering the
relevant writers; atomic rename alone does not exclude an intervening editor. Recheck protected
state, stage/validate the full register, publish, then reread and validate the actual destination.
Read-only access supports list; inability to meet write protection supports no canonical mutation.

Before a retry, compare original authorized intent, prior before/after evidence and actual current
rows/history. If the original change is already applied, return the existing ID/result without a
second allocation, history event, date change or write. An update whose requested fields already
equal current fields is a no-op. For add, exact source plus the same intended row and initial event
can identify the prior result; a conflicting row or uncertain distinct-action match requires
reconciliation, not another ID. If a later edit intervened, reconcile it rather than reapplying the
old request over it. A missing completion response is not proof that publication failed.

An interrupted replacement may leave the old register or the complete new register. Determine
which from preserved bytes/revisions and actual readback; verify the new state as applied or
resume from the unchanged old state after a fresh conflict check. A partial, malformed or otherwise
unexpected register remains explicit pending recovery and blocks further mutations. This is recovery
for an observed damaged or externally changed state, not permission to select a publication method
that can expose a partial canonical file. Restore prior bytes only when that restore cannot erase
intervening changes. Recovery evidence can use the
host's native revisions or existing task/session evidence; no Arch Studio journal engine or second task
history ledger is required.

Report the exact register, project ID, affected task IDs, changed/no-op/blocked or partial result,
observed native protection, before/after evidence and fresh checks. Verify row count, global unique
IDs, preserved access metadata, requested fields/status/source, appended event count and preservation of all unrelated rows
and earlier history. Instruction retrieval or a successful save command alone is not completion.

TIME.csv:

```text
id,date,hours,description,sources,correction
```

### Native time operations

TIME.csv belongs to the selected project even when its task register is a studio portfolio.
Resolve one valid project through the native context procedure. Read the complete existing
register; a missing file, old header or malformed row is an error, never an empty register to
create or repair implicitly. Require the exact six-column header and six cells per row, unique
permanent IDs matching `E` plus at least four decimal digits, valid calendar dates at supplied
`YYYY-MM-DD` or `YYYY-MM` precision, positive finite decimal hours, a nonempty description and
a nonempty JSON array of nonempty source strings. Preserve unknown date precision; do not
substitute an inferred work date. Existing malformed rows remain byte-for-byte unchanged.

Every new duration must be explicitly confirmed by the user. Timestamps, meeting lengths,
commits, task status and activity counts are evidence of work, never evidence of hours or
billability. Hours are exact decimal values: do not round through binary floating point or
silently choose a billing increment. Preserve existing decimal text. A new row may preserve
the confirmed decimal scale; exponent notation, if supplied, must still represent the same
finite decimal value. Zero, negative, infinity, NaN, blank and nonnumeric hours are invalid.

Sources are exact ordered tokens in one JSON-array CSV cell. Each new source is either a
registered document ID plus nonempty item locator (`D000001#item`, six or more ID digits,
whitespace-free item) or a specific user instruction (`conversation:YYYY-MM-DD#instruction-N`).
Validate source dates and actual membership of document IDs in this project's DOCUMENTS.csv;
never invent registration or a conversation instruction. Descriptions and source tokens are
nonempty single-line text without control characters or `|`. A correction is blank or the
ID of an existing earlier entry in this register; do not create dangling/self/cyclic correction
links. Retain all original entries, including entries corrected more than once.

| Semantic operation | Required facts and transformation |
|---|---|
| `time.list` | Read and validate the whole project TIME.csv, then return preserved entries and its owner path. Requested date filtering affects display only. Report the inspected period and unavailable evidence; quiet records do not prove no work or a complete timesheet. No writes or allocation. |
| `time.append` | Require confirmed date, positive decimal hours, description and nonempty sources. Correction defaults to blank. Allocate `E` plus greatest historical numeric ID + 1, padded to at least four digits; an empty valid register starts `E0001`. Append exactly one row. Corrections are new positive-duration entries pointing to an existing entry; they do not edit/delete the original or define net billing. |

Before allocation, detect a repeat by the same date, exact description, ordered source tokens,
correction target and numerically equal decimal hours. JSON whitespace and equivalent decimal
spellings (`1.0` and `1.00`) do not make a new approved duration. Return the existing ID without
changing any bytes. If several historical entries match, preserve them, report the ambiguity
and do not append another. A genuinely separate but identical-looking activity requires distinct
confirmed provenance; do not fabricate a distinguishing token. The register has no history
column: do not add one or turn corrections into hidden edits.

INVOICES.csv:

```text
id,invoice_number,period_start,period_end,currency,base,expenses,total,sent,paid,status,correction,document_id,history
```

### Native invoice operations

INVOICES.csv always belongs to the selected project. Read and validate the whole canonical
register before any operation. Require the exact fourteen-column header and fourteen cells per
row; permanent unique IDs matching `I` plus at least four decimal digits; nonempty unique invoice
numbers; nonempty currency; finite decimal base, expenses and total with exact `base + expenses
= total`; valid supplied period dates and optional sent/paid dates; a declared status; and a JSON
array in history. Do not silently rewrite malformed data, repair a missing register or renumber
invoices. An invoice number is its exact supplied text, independent of the permanent I-ID.

Period start/end are required calendar dates at supplied `YYYY-MM-DD` or `YYYY-MM` precision;
retain that precision and reject a reversed period. If mixed precision leaves the requested
billing interval materially ambiguous, resolve it rather than inventing days. Sent and paid
are explicit calendar dates when populated. A row with status sent requires sent; a row with
status paid requires paid. Paid does not require an invented sent date. Preserve earlier dates
when moving to paid or void. Currency and invoice number are nonempty single-line text without
control characters or `|`; do not silently uppercase or convert currency identifiers.

Base, expenses and total are explicit finite decimal values, including explicitly supplied
negative adjustments or zero. Missing means unknown, never zero. Check arithmetic with exact
decimal operations; never infer amounts from TIME.csv, task progress or activity, choose an
exchange rate, impose rounding or net a correction against another invoice. Confirmed agreement
terms may supply facts, but an agreement is not required when the user supplies the facts.

Correction is blank or an existing earlier I-ID in the same register; reject dangling/self/cyclic
references. A correction is a distinct append with its own unique invoice number. document_id
is blank or a real registered D-ID in this project's DOCUMENTS.csv of kind `invoice`; inspect
the existing registration when supplied. Registration of a new invoice artifact belongs to its
own authorized document workflow, not an implicit invoice-ledger side effect. Keep PROJECT.md,
agreement/proposal terms and all other registers unchanged.

| Semantic operation | Required facts and transformation |
|---|---|
| `invoice.init` | Read and validate the setup-created register, report its owner path and current state, and make no changes. Missing/invalid remains an error; init does not create or replace it. |
| `invoice.allocate` | Read and validate, then report `I` plus greatest historical numeric ID + 1 padded to at least four digits (`I0001` for a valid empty register). This preview reserves nothing; append recalculates from actual current state. |
| `invoice.status` | Return preserved rows and exact decimal totals of every nonvoid row grouped by exact currency identifier. Draft, sent and paid rows all contribute; void rows do not. Never combine currencies, silently net corrections or describe this sum as outstanding/unpaid balance. Read-only. |
| `invoice.append` | Require invoice_number, period_start/end, currency, base, expenses and total. Optional sent, paid, correction and document_id default to blank; status defaults to draft. Explicit initial sent/paid statuses require their corresponding supplied dates. Validate all facts, allocate from the whole current historical register, append one row and initialize history with one created event using the actual operation date. Do not accept a caller-selected permanent ID or imported replacement history. |
| `invoice.set-lifecycle` | Select one exact I-ID and an explicitly evidenced event sent, paid or void with its date. Preserve invoice identity, number, period, currency, amounts, correction and document linkage. Apply only the transition rules below and append one event for an actual change. This records evidence; it never sends an invoice/message, charges money or establishes payment from inference. |

Lifecycle rules:

- Draft may become sent, paid or void when the corresponding event is explicitly evidenced.
- Sent may become paid or void. Repeating sent with the same date is a no-op; an explicitly
  requested correction to its sent date appends a new sent event and preserves earlier history.
- Paid may become void. It cannot move back to sent or draft. Repeating paid with the same date
  is a no-op; an explicitly requested correction to its paid date appends a paid event.
- Void cannot move to another lifecycle state. Repeating void is a no-op, retaining the originally
  recorded void event/date. No lifecycle operation erases earlier sent or paid dates/history.
- No operation infers that a sent invoice was paid, backfills sent for a paid row, or transmits an
  external message. Resolve missing event/date evidence before mutation.

History is embedded JSON in the existing CSV cell. A new invoice has exactly
`{"event":"created","date":"YYYY-MM-DD"}`, with the actual operation date rather than an
invented issue/payment date. A real lifecycle change appends
`{"event":"sent|paid|void","date":"<supplied event date>","before":"<prior status>"}`.
These event shapes are closed: created events contain only `event` and `date`; lifecycle
events contain only `event`, `date` and `before`. Validate those exact keys before publication
and again on readback. Explicit authorization/evidence establishes that the lifecycle fact may
be recorded; it does not add an `evidence` key, another history field or a CSV column. Retain
supporting execution evidence separately within the authorized operation's evidence boundary.
Preserve all earlier events as data in order. Sent/paid set only their corresponding date cell;
void sets status and records its date in history, without a new schema column. Initial status
and supplied sent/paid cells record explicit initial facts; do not manufacture additional history.

Append retry first checks existing invoice_number. If every requested fact matches the existing
row (decimal amounts compared numerically), return its ID with no rewrite or created event.
Equivalent decimal scale or JSON formatting alone does not authorize another invoice. A differing
row with that number is a collision requiring reconciliation or a separately authorized correction
with a distinct number. If a prior append succeeded and later lifecycle changes explain the
current state, retain that append's ID and report the observed lifecycle using saved request/history
evidence; never revert it to the original draft or append a duplicate. When evidence cannot
establish the prior operation, preserve the conflicting state and ask for the missing decision.

### Time and invoice publication and recovery

These are native single-register operations under the shared minimum mutation guarantees, not
calls to a supplied runtime. Read-only previews neither allocate durable identity nor prove write
access. Keep exact confirmed intent, owner identity, original bytes/revision, intended complete
replacement and enough evidence to distinguish a repeated request from a different operation.
Guard the whole owning register, ID/number allocation and any source/document registration used
for validation. Reconcile relevant intervening changes before publication; never overwrite them
based on a stale read or claim that an advisory lock excludes arbitrary external writers.

Fully write a separate replacement, handle short writes/failures, close it, reopen actual staged
bytes, compare them to the prepared replacement and validate the complete CSV and requested
transformation before publication. Preserve existing mode, owner/group, ACL and other relevant
access metadata; use atomic replacement or an equivalent native conditional revision that exposes
a complete old or complete new register. Never truncate, stream into or partially overwrite the
canonical register. If these guarantees cannot be established, preserve it and report the actual
native limitation. Ordinary task-specific host code is allowed; no Arch Studio runner, installer,
bridge, downloaded helper or source checkout is required.

After an interruption, inspect actual canonical bytes/history and retained operation evidence.
If the complete intended result is present, verify and report it without replay or duplicate event.
If the complete original state remains, revalidate identity, sources and concurrency before safe
resume. A third state needs reconciliation; do not blindly restore backups, regenerate an ID or
repeat a lifecycle event. After publication, reread the actual canonical destination and verify
header, row count, global IDs, invoice-number uniqueness, exact intended change, decimal values,
all preserved rows/history/metadata and protected files. Report owner path, affected permanent ID,
new write versus repeat, exact confirmed facts and remaining external action. Do not claim broader
billing, completeness or payment correctness than the inspected evidence supports.

CHANGES.csv is defined without an automated writer:

```text
id,description,status,source,document_ids,date,notes
```

SCHEDULE.csv keeps the current master-schedule-owned schema. Document placement does not redefine selected item membership, approval, revision or workbook preservation.

## Native document operations

These names describe semantic work, not an executable API. Receive owns the rules below;
authored-record owners apply them directly with available native tools. Context, field/identity
validation and protection cover the entire affected register, not only matching rows. Preview
unconfirmed targets and metadata; already authorized exact writes need no repeated approval.

### Validate records and paths

Use the exact 21-column DOCUMENTS.csv header above. Require one complete string-valued cell per
column, unique permanent IDs matching `D` followed by at least six digits, unique project-relative
paths, and filename equal to the final path component. SHA-256 is 64 lowercase hexadecimal digits.
Kind and phase/stage/scope/originator are nonempty single-line values without control characters
or `|`; the coordinates must belong to the applicable confirmed vocabulary. Preserve supplied
case and spelling. Document dates are valid YYYY-MM-DD or YYYY-MM; received_at is an actual ISO
arrival timestamp with timezone. Source decodes to a JSON object and history to an array of event
objects with a nonempty event name. Validate any source expiry date. Blank optional values remain
blank. Every supersedes target must exist in the full register and its directed lineage must be
acyclic. Do not infer revision relationships from filenames, dates or identical content.

Owned paths must be portable relative paths inside the resolved physical project. Reject absolute
paths, empty/dot/parent segments, backslashes, control characters and `:<>"|?*`, trailing spaces or
dots in a component, and reserved Windows device names (CON, PRN, AUX, NUL, COM1–9, LPT1–9,
including extensions). Reject symlinked roots, identity/register files, targets, ancestors and
package members. Require ordinary files/directories; do not copy devices or special files.
An explicitly supplied source may be outside the project only within its authorized read scope.
It does not authorize a write there. Preserve original sources and received filenames.

`documents.resolve` validates all five coordinates and kind, then substitutes the confirmed
Document path template with supplied coordinate/metadata values. Each substituted value is one
safe component, with no path separator. Template fields must name declared register columns;
missing values or malformed/absolute templates stop resolution. An empty template uses the exact
confirmed project-relative destination folder. For scoped SCHEDULE.csv, require phase/stage/scope,
retain only template segments using those coordinates in their original order, then append
SCHEDULE.csv. Resolution does not create folders, reserve an ID or adopt schedule membership.

### Exact content identity

`documents.hash` is read-only. A file hash is SHA-256 of its exact raw bytes, without newline,
Unicode, image or archive normalization. A package hash covers every descendant directory and
ordinary file, including empty directories. Its byte stream starts with UTF-8 `package` plus a
zero byte. Sort all descendants by their case-sensitive project-independent relative POSIX path
components (lexicographic component order). For each directory append UTF-8 `directory`, a zero
byte, its relative POSIX path in UTF-8, and a zero byte. For each file append UTF-8 `file`, a zero
byte, its relative POSIX path in UTF-8, a zero byte, and the 32 raw bytes of that file's SHA-256.
Hash the complete stream with SHA-256. The package root name and filesystem metadata are excluded;
its internal names, bytes and empty directories are included. No symlink traversal is allowed.

Retain observed source and register revisions. Recheck the source and complete prepared copy
before publication; reading a hash once does not protect against a later source change. Report
hashes as content observations, not evidence of external truth, approval or malicious-tamper safety.

### Register, query and update

| Operation | Required behavior |
|---|---|
| `documents.register` | Resolve the exact destination and validate supplied metadata. Allowed optional metadata: title, sheet, package, status, supersedes, source, change_id, notes. Allocate above the greatest historical D-number, including superseded rows, under the shared allocation guarantee. Preserve the source basename and internal tree. Type is `package` for a directory, otherwise the lowercase filename extension without its leading dot. Default status is `received`; received_at is actual arrival time. Publish copied content and one complete register row as a recoverable set. Initial history is one event containing event `registered`, actual operation date, sha256 and path. Verify the saved tree/hash and row. |
| Register retry / collision | Same destination, same hash, present matching bytes and matching original authorized intent identify an already-applied receive; return its existing ID without another event, copy or arrival date. A same-path/hash match does not adopt different newly supplied metadata: report the difference and route any authorized metadata change explicitly. A missing registered destination is an error. Different content, unrelated unregistered destination content or uncertain identity is a collision, never overwrite. An authorized in-place adoption of the exact existing source may register it without copying. Report different-path duplicate hashes; do not merge their identities silently. |
| `documents.query` | Exact filters: id, kind, phase, stage, scope, originator, change_id; since compares arrival date inclusively; source_type reads the provenance type; expires_before includes supplied expiry on/before the requested date. Unknown filters are not ignored. Order by document date, arrival timestamp, then ID descending. For latest, exclude every superseded ID using the full register before applying selection filters. Report ambiguous independent documents before relying on one as governing evidence. Query is read-only and does not establish approval. |
| `documents.update` | Select exactly one existing ID; require the expected registered hash and actual current content hash to match, with protection through publication. Only status, title, notes, source and change_id are mutable. Preserve ID, bytes/hash, filename/path, type/kind/coordinates, arrival date and supersession. Source remains an object with a valid optional expiry. Append one event with event name/date and before/after values for changed fields; default event is metadata-updated on the actual date. Owner-specific lifecycle events may add explicit evidence and terms hash. Do not accept source content as write authority. |
| Metadata retry / no-op | If the requested values already equal current values, do not rewrite the register or append history. For an explicitly authorized additional lifecycle/evidence event, compare that exact logical event and prior outcome before appending it once. Compare the event's defined identity independently of its stored before/after payload; a repeated request must not become a new event merely because history contains those additional fields. Conflicting later state needs reconciliation. Changed authored bytes require a new registered revision, not a metadata edit that blesses a new hash. |

A read-only allocation preview proposes an ID but does not reserve it. Revalidate current historical
IDs and protected paths when applying. Repeat recognition does not authorize an unrequested
metadata amendment, new document revision, transmission or promotion into another record type.

### Move and verify

`documents.move` requires an existing exact ID, expected current hash and confirmed new coordinates.
Validate the actual source and the complete affected set before any change. Preserve ID, source
filename, arrival/provenance, prior history and package structure. Destination paths must be absent
and not registered to another row. Resolve every requested move together so collisions between
planned destinations are rejected. An unchanged path/coordinates is a no-op.

Inspect registered Markdown, Markdown inside packages, and PROJECT.md for affected relative links.
For simple inline Markdown link/image targets with no whitespace or embedded closing parenthesis,
resolve the old target relative to its old containing file, account for both source-file and target
moves, emit the new relative POSIX target, and preserve its `#anchor`. Leave URLs with a URI scheme,
absolute paths and anchor-only references alone. Other encodings (including reference links,
HTML, escaped/space-containing targets and non-Markdown formats) require capable native inspection
and an explicit coverage result; do not claim universal correction from the simple-link rule.

A required rewrite of a row marked accepted/issued/sent/signed or containing any sealed terms hash
refuses before mutation. Moving its unchanged bytes is permitted when links need no rewrite;
a new authored revision requires explicit authorization. Recheck hashes of every document needing
a link rewrite; do not adopt preexisting drift as a new registered hash. Unrelated drift remains a
finding. Preserve all PROJECT.md bytes outside explicitly affected links or separately authorized
vocabulary fields, including the bounded Agreement section unless a permitted link changes there.
Never alter issued agreement/proposal terms through a link update.

Recompute affected document/package hashes from their actual prepared bytes. A moved row appends
one event with event `moved`, actual date, old path in `from`, new path and new sha256. An unmoved
row whose links change uses event `links-updated` with the same fields. A coordinate-only change
appends `coordinates-updated`, actual date and the confirmed coordinates. Unrelated rows/hashes
and all earlier history remain unchanged. Publish the full file/directory/register/manifest set
under the recovery rules below, then verify destinations, links, hashes, IDs and old-path removal.

`documents.verify` reads the full register and actual tree. Report missing files, mismatched hashes,
duplicate hashes, expired provenance, invalid vocabulary/template placement, and unreceived files.
Expiry means before the explicit as-of date (default actual date). Packages cover their contained
files; root registers, PROJECT/AGENTS/CLAUDE, folder identity, optional product/EPD libraries and
scoped SCHEDULE.csv are not unreceived documents. Hidden host/recovery files are not ordinary
received content, but any pending operation must be reported separately. Verification never repairs,
reseals, establishes domain truth or substitutes for requested visual/content inspection.

### Publication and recovery

Apply the shared single-record/allocation/multi-file guarantees. Stage complete new files and
validate their actual reread bytes against the intended bytes and schemas before publication;
handle short writes and failures before touching canonical state. Each individual register or
manifest replacement must expose complete old or complete new bytes. Preserve existing permissions,
applicable ownership and ACLs; copying a source must not widen its access without explicit authority.
Use actual preconditions/exclusive access covering all relevant writers and source files. Cooperating
locks alone do not exclude external editors. Refuse before canonical writes if protection or access
metadata preservation is unavailable. Keep the prepared result and a concrete limitation.

Use the [native mutation sequence](#native-mutation-sequence) for the complete document, register,
link and manifest set. Its verification of all retained recovery content precedes the first
per-file publisher, and its full result verification precedes the completion marker. A valid
intermediate mixture is explicitly pending; other conflicting operations must detect it and stop.
No particular Arch Studio journal format or transaction engine is required; inability to retain
and discover safe recovery state blocks that method.

`documents.recover` inspects actual destinations, retained before/prepared state and the recorded
intent. Report which changes completed and which remain. Resume or restore only after fresh guards
show that no unrelated intervening edits would be lost. Never blindly restore a historical backup,
clear a supposedly stale lock, delete unreferenced evidence or mint replacement IDs. An existing
`.as-document-transaction` is pending historical evidence to inspect, not permission to replay its
old executable. A lost response may mean publication succeeded; exact already-applied retries
return the existing result without another event or allocation. Unresolved partial state stays
explicitly incomplete. Recovery must retain source originals, unrelated records and protected terms.

## Native commercial operations

Proposal and agreement workflows apply the receive-owned document rules directly. These are local
record operations; none sends email, uploads documents, signs an agreement, establishes payment or
infers commercial acceptance. Such external actions need their own existing explicit authorization.
Require current registered document bytes and hashes, including their publication-time guards.

### Proposals and protected terms

`proposal.create` prepares a Markdown proposal from authorized facts/terms and the owning template,
then registers kind proposal/status draft at confirmed coordinates. Require exactly one start marker
`<!-- issued-terms:start -->` and one later end marker `<!-- issued-terms:end -->`, with a nonempty
terms body; stray, duplicate, reversed or nested markers are invalid. Preserve unknowns rather than
inventing approval or commercial terms. Additional rendered letters are separate registered artifacts.

For compatibility with existing valid seals, decode UTF-8 text, normalize CRLF and lone CR to LF,
then take the body between the exact markers, removing at most one LF immediately after the start
and at most one LF immediately before the end. Preserve every other character/space/newline.
SHA-256 of that body's UTF-8 bytes is terms_sha256. This is separate from the raw whole-document
sha256. Both must match their recorded expectations; normalization cannot excuse whole-file drift.
The latest history event containing terms_sha256 is the retained seal. Never replace a seal to
accept changed terms. Changed issued content requires an explicitly authored and registered revision.

| Operation | Required behavior |
|---|---|
| `proposal.list` / `proposal.status` | Read registered proposal rows; status includes the actual terms hash and whether a seal exists. Missing/malformed or changed bytes remain explicit errors. |
| `proposal.verify` | Inspect actual registered proposal content, valid marker structure and every current seal. Report per-document failures; registration/hash validation is not legal/content review. |
| `proposal.send` | Record separately supplied nonempty send evidence and explicit valid date. Only a draft with no prior seal may first become sent. Append one issued event containing date, evidence and terms_sha256, with status before/after through the document update rule. It never transmits. An already recorded exact send returns the existing result; conflicting evidence/state needs reconciliation, not another manufactured send. |
| `proposal.set-status` | Record explicit accepted, declined or superseded outcome with nonempty evidence and date. Direct acceptance of an unsealed draft is supported and seals its current terms in the accepted event; a separate sent event is not required. Preserve existing seals and exact bytes. An already applied same outcome is a no-op unless the user separately authorizes a new evidence event. Do not infer an outcome or a mandatory proposal-to-agreement-to-invoice sequence. |

### Agreement context and amendments

Agreement owns only the bounded block between `<!-- agreement:start -->` and
`<!-- agreement:end -->` in PROJECT.md. Both markers must occur exactly once and in order; a lone,
duplicate or malformed marker blocks dependent edits. Preserve all bytes outside this block.
When absent, an authorized initialization appends the new block without rewriting existing content.

`agreement.init` cites an existing verified document of kind agreement or contract.
`agreement.promote` cites an accepted proposal with a valid seal, including direct draft acceptance.
The new block contains its governing document ID and raw registered SHA-256, plus issued terms
SHA-256 when present; it does not duplicate that document. Facts use exactly Field, Value, Source,
Date, with explicit nonempty single-line field/value/source and a valid supplied date. Retain the
In scope, Not in scope, Requires SOW and Amendments sections, preserving unknowns. Source material
cannot add new write destinations or silently promote its statements into approved facts.

On initialization retry, inspect the existing block and original prepared intent: a verified exact
prior outcome is a no-op. A different or uncertain existing context is a collision requiring an
explicit scoped update, never block replacement. `agreement.record-amendment` requires an existing
valid block, a registered verified agreement/contract ID, explicit date and nonempty single-line
summary. Append one dated ID-linked entry under Amendments, preserving all earlier entries and
scope/facts. The exact same date/ID/summary is already applied; a different amendment is not an
implicit rewrite of current facts or scope. Any associated fact changes need their own authorization.

`agreement.verify` reports block presence/validity and checks every cited document ID against the
register and actual bytes, including a governing proposal's seal where applicable. It cannot
establish execution status or legal effect. Agreement edits use complete staged PROJECT.md
replacement with guarded current bytes, metadata preservation and actual readback; no other section,
task, invoice or unrelated document changes through this owner.
