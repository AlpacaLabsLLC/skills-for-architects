# Changelog

All notable changes to **Arch Studio** (`AlpacaLabsLLC/skills-for-architects`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Arch Studio uses a sequential `major.minor.patch` release scheme, marks breaking migrations explicitly, and reserves patch releases for compatible corrections. A fourth segment (`major.minor.patch.n`) is reserved for content-only patches that change skill text without changing code or packaging.

## [Unreleased]

## [1.5.4] - 2026-11-25

A release on 1.5.3 that adds the Rhino cluster: seven skills for architectural modeling in Rhino 9 on macOS and Windows, with two ways in and the same skills in both: from Rhino's AI panel, or from your terminal, with Claude Code or another agent connected through Rhino 9's built-in MCP server (see the README). It also adds `start` and points the FF&E skills to the optional Norma index. It is **not fully compatible** with 1.5.3: it removes the Norma assistant and the agent definitions and renames `norma-support` to `support`, with no aliases; see Breaking for what to do instead. Install or update the plugin, then open a new AI panel session in Rhino 9, or connect your agent with `MCPConnect` and `MCPStart`.

### Breaking

These changes are owner-approved for this release. The changelog header reserves patch releases for compatible corrections; where this release ships as a patch, they are the explicit exception to that rule. None has a compatibility alias. Updating keeps the plugin's data folder (Rhino lessons and firm rules), studio and project folders, and a saved default-preference block, which still works and is refreshed the next time the preference is updated.

- **`/as:norma` is removed.** Arch Studio no longer has a coordinating assistant. Describe the task, or name the skill that owns it; for larger jobs, `workplan` shows the plan first. The session line no longer mentions a coordinator, and the default-preference procedure moved to `studio`. Norma is now a separate product index: to search products by that name, connect the Norma index MCP (`https://mcp.normaindex.com`, no login), which the FF&E skills use when it is connected ([setup](docs/norma-index.md)).
- **`/as:norma-support` is now `/as:support`.** The same help with setup, access, memory and troubleshooting, presented as Arch Studio support. Type `/as:support` instead.
- **The agent definitions are removed:** the Norma worker and the seven specialist agents (`site-planner`, `nyc-zoning-expert`, `workplace-strategist`, `product-and-materials-researcher`, `ffe-designer`, `sustainability-specialist`, `brand-manager`), and `docs/agents.md`. Every skill they combined runs directly as before: name the skill instead of the agent.

### Added

- **Rhino cluster (3D / BIM modeling).**
  - **`rhino-setup`** checks that Rhino 9's tools are ready, in the AI panel or a connected agent, reads the open document and its units, and names the user action when something is missing. It also says when the hosted Arch Studio MCP is connected beside the plugin: use one or the other.
  - **`rhino-model`** plans, builds and checks architectural models from a plain-language brief: it asks one question about its recommended values, answered with "Use all recommended" or "Go through each one by one", writes the model's requirements (each with its source) into the document before building, builds by script, and runs a requirements check that covers dimensions, counts, clearances, clashes, connectivity, hardware plausibility, proportion, cover and bearing. It reports what was met and what was not checked.
  - **`rhino-batch-image-export`** batch-exports view images of a model (options, views, layer sets) in one display mode, setting up the display modes, views and materials the export needs; every PNG is read back and the batch fails when a file is blank or has colour in a mode that must have none.
  - **`rhino-thinline`** holds the drawing conventions for black and white vector sheets (line hierarchy, hatch, labels and leaders, title block, layout) and checks the exported PDF.
  - **`rhino-axon`** makes the view for an axonometric sheet (camera, cut-away, hidden-line occlusion, detail cuts with hatched cut faces) and hands the linework to `rhino-thinline`.
  - **`rhino-bom`** takes quantities from a model built under one parent layer, reconciled to the object count, with a source on every line and a list of what is not counted. Qty is a piece count (`pcs` unless a count label such as `sheets` is given) unless a line sets `qty_is_total` to put the measure in Qty; on a counted line a length, area or volume unit is refused, and the measure goes under Total in its own unit.
  - **`rhino-agent-team`** runs several agents on one model split into one file per owner: a coordinator writes the set-out first (levels read off the host, each owner's share of shared space), the team check measures across the files every round and writes one issue note per fault to the owner who must move, and the model is settled only when every owner's own check passes and no note is open. It first tells the user when one agent would do.
- **Arch Studio in the Rhino AI panel.** The panel does not load plugin skills, so a Claude Code `SessionStart` hook adds one line pointing to `skills/as-rhino-index.md` in the installed version. When the user names an as-rhino skill or Arch Studio in Rhino, the model reads the skill by path. The hook (`hooks/as-rhino-context.sh`) is plain `sh` with no Python, so it runs in macOS's shell and in Git Bash on Windows; it reads nothing, sends nothing and never blocks a session. All the plugin's hooks now run on Windows under Git Bash, including the disclaimer check without `jq` or Python.
- **Local lessons for the Rhino skills.** `rhino-model`, `rhino-bom`, `rhino-batch-image-export`, `rhino-thinline` and `rhino-axon` read what earlier runs learned before planning and write what each run learned at the end, as plain text in the plugin's data folder, which survives updates. A lesson becomes a firm rule only after the user agrees, and it can never change a checker or its tests.
- **Model space only.** With a layout as the active view, Rhino puts new objects on the layout's page. `rhino-model`'s build scripts, `rhino-agent-team` and `rhino-batch-image-export` make a model view active first; the requirements check fails any part on a page (`baseline model space`), and `rhino-bom` refuses to count one.
- **Host contract.** `model-read` and `model-edit` modes for connected modeling applications, a `delivery: "plugin-only"` declaration, and a named exception that lets the Rhino skills ship helper scripts that run inside the user's Rhino.
- **`start`** (`/as:start`) shows the Arch Studio card as text, the plugin's version of the hosted MCP's `as_connect` welcome: the logotype, the installed release, a checklist (plugin installed, studio set up or not, Rhino 9 connected or not, Norma index connected or not), what Arch Studio is, how to use it, a tour of the practice areas, prompts to try and the footer. It only reads. The session-start message now points to it. It is plugin-only: through the hosted Arch Studio MCP, `as_connect` is the card.

### Changed

- **FF&E product search can use the Norma index.** `product-research` and `product-match` use the [Norma index](https://normaindex.com) MCP (`https://mcp.normaindex.com`, no login) when it is connected and suggest connecting it once when the user needs products; `ffe-spec-book` suggests it when an item has no product. All three work without it ([setup](docs/norma-index.md)).
- **The session line no longer names a coordinator,** and the optional default-preference block names Arch Studio instead of Norma (see Breaking).

### Known limits

- **Rhino 9 on macOS and Windows, plugin only.** The skills that run helper scripts (`rhino-model`'s requirements check, `rhino-batch-image-export`, `rhino-thinline`, `rhino-axon`, `rhino-bom`, `rhino-agent-team`) need the installed plugin; they are not available through hosted MCP. On Windows, Claude Code runs the plugin's hooks in Git Bash, so Git for Windows is needed; without it the panel gets no startup line. Claude Code has been run both ways in, in single runs on pre-release builds. Codex works from the terminal once Rhino's tools are pre-approved in its config (once, on macOS; see Evidence). The AI panel has been tested with Claude Code only; a plugin installed in Codex is not loaded by the panel (read from McNeel's plugin, not tested).
- **Name the skill or Arch Studio** in the AI panel; a plain modeling request loads no skill, by design. A panel session opened before the update needs a new session.
- **Checks are geometric, not engineering.** Nothing checks structure, code compliance, slopes or clearances beyond the requirements written for the model. `rhino-batch-image-export` judges colour only for Arctic and Monochrome and makes no interior views. `rhino-thinline` line weights and hatch patterns are working conventions, not proven in print.
- **One drawing sheet per document.** `rhino-axon` and `rhino-thinline` keep a sheet's request record, its building record and its main drawing settings in the document, not per layout, so a second sheet would fail the first sheet's check on requests that cannot be removed. `new_sheet` now refuses a second sheet before drawing anything; draw it in another document that holds the model but no sheet.
- **Cut faces are hatched in details only.** A cut-away in the main drawing is drawn in outline, not hatched, and there is no hatched main-view section.
- **Lessons hold two kinds only.** A lesson is either modeling practice or the user's own preference, recorded with what the user said; the lessons script refuses any other kind, so a design, architectural or engineering rule the agent inferred is not saved, and only those two kinds can become firm rules. The script cannot judge meaning: the agent declares the kind under the skill's rules and the script enforces the declaration. Lessons written before this release are kept and read but cannot be promoted until a kind is added.
- **Rhino teams need the same release on every machine.** `rhino-agent-team` stamps every file with the plugin version and its helpers' fingerprint and refuses "settled" until every owner matches the coordinator. Setup for teams is in `docs/firm-deployment.md`.
- **Rhino's AI settings can override the startup line.** A custom agent prompt or an extra MCP server set in Rhino's AI settings can override the plugin's startup line, so the panel may not find the Arch Studio skills; reset those settings.
- **The terminal connection can start Rhino 8.** On a Mac that also had Rhino 8, the Rhino MCP connection started Rhino 8 in a terminal run when it had to start a Rhino itself. Start the model's server with `MCPStart` first, and set `RHINO_MCP_DEFAULT_VERSION=9` in the connection, which sets its default version to 9 (the README's `claude mcp add` line does).
- **Evidence.** Single runs on pre-release builds, named because the skills changed after them; not reliability measurements.
  - **AI panel, with Claude Code:** on macOS (build `173b1e1`), `rhino-setup` passed and `rhino-model` built a 12 by 16 ft gable shed. On Windows 11 (10.0.26200) with Rhino 9.1.26315, all five Rhino skills that drive a document (`rhino-setup`, `rhino-model`, `rhino-batch-image-export`, `rhino-bom`, `rhino-axon`) ran in the panel on an earlier build, with the skill index opened by hand before the startup-hook fix; on build `584e284`, a new panel session found the skills through the startup line and `rhino-setup`'s connection check passed.
  - **Terminal, Claude Code:** on macOS (build `ebfaf34`), `rhino-setup`, a 12 by 16 ft gable shed whose requirements check passed, and an axonometric sheet whose sheet and PDF checks passed. On Windows (build `584e284`), with the pinned entry (`RHINO_MCP_DEFAULT_VERSION=9`, which started Rhino 9 itself when none was running), `rhino-setup`, `rhino-model` (including a build with a layout as the active view), `rhino-batch-image-export`, `rhino-bom` and `rhino-axon` each passed once; lessons were saved for `rhino-model` and `rhino-axon`.
  - **Terminal, Codex:** Codex CLI 0.163 on macOS (build `6e86f3f`), with `default_tools_approval_mode = "approve"` under its `rhino` server, installed the plugin, ran `rhino-setup`'s smoke test and modeled a 12 by 16 ft gable shed whose requirements check passed, once, against a headless document's own Rhino MCP server rather than through the router; without that line `codex exec` completed `get_context` but refused `run_python`, so no skill script ran. Codex loads the plugin's one hook and runs it only once it is trusted: it ran with hook trust and did not run without.
  - **Agent teams (`rhino-agent-team`):** measured with Claude Sonnet and pre-release skills in a test harness (headless Rhino, scripted rounds, no user, the harness's own tool server rather than Rhino's MCP connection). On one test row house, teams using the team skill had 0 to 21 first-round clashes in 6 runs, and three trade agents with no coordinator and only the modeling skill had 47 to 93 in 6 runs. The team also had the rest of its method and a coordinator turn before round 1, so this doesn't show which part made the difference. On a test barn, a five-owner team with a coordinator settled by the skill's own check in 1 of 4 completed runs, and in 1 of 2 on the last skill build run. A spend limit stopped the other 3. The skills changed between some runs, there was no comparison without a team, and this isn't a success rate. A team has not yet been run through either way in, or on Windows.
  - **Hooks:** tested in CI on Windows without Python.

## [1.5.3] - 2026-11-11

A compatible patch on 1.5.2. It removes the optional local runner, fixes a maintainer script and restores the Governance pillar name. No user action is required after installation; firms that installed through the local runner install from the marketplace like individuals.

### Added

- **`SECURITY.md`.** How to report a vulnerability privately.

### Changed

- **Governance pillar restored.** The first product pillar is again named **Governance**, undoing the 1.5.1.2 rename to **Studio**. Governance keeps the four responsibility areas introduced in 1.5.1.2: **Account and access**, **Configuration**, **Standards**, and **Assurance**. Tooling, Knowledge and Memory are unchanged. "Studio" alone again means the user's workspace only. Content-only: no technical identifier, directory, schema, protocol, skill, agent, record kind or behavior changes.
- **README.** Restructured for clarity, with the Arch Studio typemark. The legal entity in `LICENSE` and the README is now Alpaca Labs, LLC.
- **Lint workflow.** CI uses Python 3.13, since 3.13.7 is not available on the current `ubuntu-latest` runner.

### Removed

- **Optional local runner.** `tools/runner/` (package builder, installer, `bootstrap` scripts, `as-run` dispatcher, desktop MCP adapter, operation registry and runtime lock) is removed, together with the receive operation-registry fragment (`skills/receive/scripts/operations.json`), the operation request schema, the `tool:local-runner` component and the runner-only tests (`tests/test-local-runner.py`, `tests/test-operation-adapters.py`). No skill used it since 1.5.0. Firms install the plugin from the marketplace like individuals. Helper scripts under `tools/` and `skills/*/scripts/` and their tests remain as maintainer tooling; CI now installs their Python dependencies directly. (#45)

### Fixed

- **Context audit with a custom skills root.** `scripts/audit-skill-context.sh` now reports the name of each skill's folder when it is given a skills root, relative or absolute. It printed the supplied path before, which made fixture output harder to read and compare. `tests/test-context-audit-custom-root.sh` covers a relative root with a synthetic fixture.

### Acknowledgements

- [@dajiaohuang](https://github.com/dajiaohuang) implemented the context audit fix and wrote its regression test ([#44](https://github.com/AlpacaLabsLLC/skills-for-architects/pull/44)).
- [@fedenegro](https://github.com/fedenegro) reported the bug ([#12](https://github.com/AlpacaLabsLLC/skills-for-architects/issues/12)).

## [1.5.2] - 2026-10-14

A compatible patch on 1.5.1.2. It changes the Claude Code update-check hook, so it is a three-segment patch rather than a content-only release. No user action is required after installation.

### Changed

- **Update check and usage ping on by default.** The daily update check now runs without opt-in (turn off with `AS_UPDATE_CHECK_DISABLED=1` or `/as:studio updates disable`), and its request carries an anonymous usage ping: a locally generated random install ID and the plugin version. Set `AS_TELEMETRY_DISABLED=1` to turn the ping off. This replaces the earlier "disabled by default" telemetry promise (Decision 0023 amendment, 2026-10-14). The Codex package installs no lifecycle hook and sends neither.
- **Release procedure.** `docs/release-delivery.md` is now version-neutral, allows four-segment tags, and adds scope and tracker disposition, a role-specific contribution-credit audit, and rules for corrections after publication. It absorbs the unmerged August release checklist.

### Fixed

- **Skill Maker verification evidence.** Generated skills must show an observed fresh policy read and a separate observed read of the actual destination after publication. A claimed read, or a prepared file compared with itself, is no longer accepted as verification. `evals/skill-maker-policy/check-evidence.py` checks the order of normalized trace evidence and rejects those cases.

### Documentation

- Hosted module record routing (`docs/module-record-routing.md`), deterministic server JSON tool contracts (`docs/server-json-tools.md`) and the projected hosted-module data promise in `docs/data-governance.md`. These describe hosted surfaces; the plugin itself still uploads no studio, project or module records.

## [1.5.1.2] - 2026-09-30

A content-only four-segment patch on 1.5.1. No runtime behavior, technical identifier, directory, schema, protocol, skill, agent or record kind changes.

### Changed

- **Studio pillar.** The first product pillar is **Studio**, replacing the retired **Governance** pillar name. Studio is the product control plane for **Account and access**, **Configuration**, **Standards**, and **Assurance**. Tooling, Knowledge and Memory are unchanged. Lowercase governance remains where it names an actual responsibility, process, rule, policy or data-governance topic.

## [1.5.1.1] - 2026-09-29

A four-segment patch on 1.5.1 by owner decision. It removes a hook script, which is a code change, so it is an explicit exception to the content-only use of the fourth segment.

### Removed

- **`pre-commit-spec-lint` hook.** The CSI formatting lint that ran before every `git commit` Claude made, in any repository, is removed. It read any `NN-NN-NN` digit run on a line mentioning a spec as a malformed section number, so date-based IDs such as `BUG-2026-09-17-01` blocked unrelated commits; and it linted the working copy rather than the staged content, so other uncommitted edits could block a commit. `rules/csi-formatting.md` stays and is still applied by `spec-writer` and `epd-to-spec`; it is now advisory like the other rules. Claude Code loads three hook handlers across two events.

## [1.5.1] - 2026-09-24

### Breaking

- **Skill entry point renamed.** Use `ffe-spec-book` instead of `spec-book`; the old skill entry point is removed with no compatibility alias. Persisted document kinds, template paths and receipt identities remain unchanged. This release includes an owner-approved breaking rename as an explicit exception to the compatible-patch convention.

### Changed

- **Specification roles.** `spec-writer` drafts Project Manual sections; `epd-to-spec` adds their EPD/GWP requirements; `product-cut-sheet` records source-faithful facts for one product from a supplied PDF or URL. `ffe-spec-book` assembles the agreed product entries.
- **Central studio policy.** Studio setup offers an existing policy or the default governance policy. Skill Maker adds live references rather than policy snapshots. Generated skills reread the policy on invocation and before resumed policy-dependent actions, and pause those actions if the configured document is unreadable. Policy composes with provenance and existing governance and preserves prior authorization.
- **Studio-name branding.** Slide-deck text uses the resolved studio name or exactly `Insert Studio Name` when none is available, preserving existing slide layouts.
- **Skills and tools.** The four pillars are Governance, Tooling, Knowledge and Memory. Skills define bounded capabilities through outcomes, domain constraints, interfaces, evidence and verification. Skill Maker uses native host authoring where available and applies Arch Studio governance and validation. Server-side deterministic product tools remain planned for 1.6 or later; current MCP tool names, host tools and maintainer helper contracts retain their technical meanings.

### Fixed

- Slide-deck template examples remain comments instead of creating an unintended extra slide.
- Document-design guidance resolves both studio template paths against the studio workspace while preserving template precedence.
- Private source incorporates the packaging corrections already shipped in OSS 1.5.0, including four-segment update checks and current installation guidance.

Release scope: OSS plugin and production MCP. Channel publication and acceptance results are recorded separately; this changelog does not certify every host workflow.

## [1.5.0] - 2026-09-20

### Breaking

- **CSV registers replace the Markdown task and time registers.** New studios and projects keep `STUDIO.md` / `PROJECT.md` plus `DOCUMENTS.csv`, `CHANGES.csv`, `SCHEDULE.csv`, `TASKS.csv`, `TIME.csv` and `INVOICES.csv` with firm-defined vocabulary and document paths. `/as:tasklist` writes `TASKS.csv`; `/as:timetracker` writes `TIME.csv`. This release is forward-only: 1.4.x workspaces with `TASKS.md` and `TIMELOG.md` are not converted and no converter is shipped. Keep an existing workspace on 1.4.5 until it is set up again with 1.5.

### Changed

- **Harness-native execution.** Skills no longer invoke bundled scripts. Each workflow is a complete specification of outcomes, schemas, formulas, preservation and evidence that the host performs with its own tools (Claude Code or Codex); no runner, installer or bridge is required, and no skill step points at a `.py` or `.sh` file. Helper modules under `tools/` and `skills/*/scripts/` remain as maintainer tooling exercised by the test suite. Workflows that previously called a script now run a native inspect-prepare-verify-apply sequence and take more turns for the same output (in the release evaluation, `csv-to-sif` used three to four times the turns of 1.4.5 for an identical file; other cases were unchanged or faster).
- **Agents carry host contracts.** Each bundled agent ships a `*.host-contract.json` sidecar declaring the host tools it needs; the Markdown bodies shrink to the agent's judgement and hand off shared policy to its owner document.
- **Rules and hooks.** `rules/moments.md` states when the studio and project records are consulted; `hooks/codex-hooks.json` registers the Codex ambient hook; the update check accepts four-segment content-patch versions.
- **Records are project-owned, hosted delivery is optional.** The same content is delivered as a hosted MCP service under its own version. Install the plugin or connect the MCP, not both; the MCP does not execute skills or reach local files, and this plugin ships no MCP server entry.

### Added

- **Fifteen skills.** FF&E and specification: `product-library` (record owner), `product-audit`, `product-cut-sheet`, `product-url-clip`, `spec-book`, `drawing-quantity-extract`, `schedule-quantity-reconcile`, `lighting-report-extract`. Firm operations: `agreement`, `proposal`, `invoice`. Records and coordination: `receive` (document registration, identity and hash checks, path resolution, revision history), `norma` and `norma-support` (host-led coordination across the skill owners; direct skill requests stay with their owner), `architecture-knowledge`.
- **External-source navigation.** `corpus/` indexes original sources by geography and topic with identity, publisher, URL and edition metadata only; the applicable original is retrieved for interpretation. Local reference summaries, rule tables and alternate versions are removed.
- **New document model.** Register schemas under `schema/`, shared studio document templates under `studio/templates/` with metric and imperial page sizes, and the document design contract in `docs/`.
- **Architecture entry point.** `PATTERNS.md` links the governance, external-source knowledge, execution and user-owned memory contracts; `docs/architecture.md`, `docs/host-harness-contract.md` and `docs/workspace-model.md` are the owner documents.

## [1.4.5] - 2026-09-03

### Removed

- `ascii-name` and `clean-downloads`, which 1.4.4 documented as commands even though they were course examples, are now non-installable source examples under `assets/learn-examples/`. Users who relied on either command can copy its example directory into their user-owned skills directory, rename `SKILL.example.md` to `SKILL.md`, and adapt it as a custom skill. This correction does not migrate or change project or studio data.

### Fixed

- Claude Desktop installation no longer rejects the plugin because of recursively discovered teaching and template manifests. The two distinct learning examples and the Skill Maker template now live under `assets/` with non-installable `SKILL.example.md` filenames; the course references the canonical `/as:tasklist` skill instead of bundling a second `tasklist`; and recursive lint coverage rejects misplaced installable manifests, malformed examples, duplicate example names, and canonical/example name overlap. Thanks to [@antonchitana](https://github.com/antonchitana) for the report, diagnosis, and verified workaround.

## [1.4.4] - 2026-08-25

### Fixed

- Claude Code hook payload decoding now fails open when neither `jq` nor Python is available or when a payload is malformed. The pre-commit CSI lint and post-write disclaimer check no longer block ordinary Bash, Write, or Edit operations in those conditions; confirmed malformed CSI sections and missing required disclaimers still block. Thanks to [@Namine4](https://github.com/Namine4) for the original report and [@grigor-p](https://github.com/grigor-p) for extending the diagnosis and confirming the workaround.

## [1.4.3] - 2026-08-13

### Fixed

- `scripts/audit-skill-context.sh` now reads the description with the YAML parser instead of reconstructing it in AWK. A frontmatter description may be inline, quoted, folded, literal, or a plain multi-line scalar, and each form folds, chomps, and strips comments by its own rules. Six were measured wrong: a bare `description:` followed by indented continuation lines reported zero characters, a trailing `#` comment was counted as description text, a full-line comment likewise, a blank line inside a plain scalar folded to a space rather than a newline, a multi-line quoted scalar was truncated at its first line, and clip-chomped `>` and `|` scalars lost their final line break. Lengths are still byte lengths under `LC_ALL=C`, so every measured total is unchanged and `docs/reports/v1-4-skill-context-optimization.md` still reconciles exactly. PyYAML is now required to run the audit; it is already installed in CI for `scripts/lint.sh`. The script also accepts an optional skills root, which lets the parser be tested against fixtures, and `tests/test-context-audit-description-styles.sh` covers all sixteen description forms.

## [1.4.2] - 2026-08-10

### Added

- Added `.codex-plugin/plugin.json` and a repository Git marketplace at `.agents/plugins/marketplace.json`, allowing Codex to install Arch Studio as `as@skills-for-architects`.
- Added Codex `AGENTS.md` templates and `.agents/skills/` roots to new studio and project workspaces alongside the existing Claude Code files.
- Added a Codex compatibility contract test covering manifests, marketplace metadata, skill portability, workspace scaffolds, and documented installation commands.

### Changed

- All bundled skills now translate Arch Studio invocation syntax by host: `$skill-name` on Codex and `/as:skill-name` on Claude Code.
- Bundled scripts and references resolve from the loaded skill path through portable `<skill-root>` and `<plugin-root>` placeholders instead of requiring Claude-only environment variables.
- Skill Maker now targets `.agents/skills/` on Codex and `.claude/skills/` on Claude Code while preserving catalog, studio, project, and global ownership boundaries.
- Installation, data-governance, deployment, workspace, and contribution documentation now distinguishes the shared skill catalog from Claude Code-only native agents and hooks.

### Compatibility

- The studio/project record formats and `as` plugin identity are unchanged. Existing v1.4 workspaces remain valid; new scaffolds add empty Codex instruction and skill roots without moving or duplicating existing Claude Code skills.
- The bundled course is available as `$learn` on Codex and `/as:learn` on Claude Code. Its shared exercises preserve the six-module progress format while clearly branching for Codex's `AGENTS.md`, `.agents/skills/`, and new-session surfaces versus Claude Code's `CLAUDE.md`, `.claude/skills/`, and `/clear`; Claude-native agents and hooks remain unavailable on Codex.

## [1.4.1] - 2026-07-29

### Fixed

- `scripts/lint.sh` and `scripts/check-plugin-namespace.py` now read repository files as UTF-8 explicitly, and `lint.sh` exports `PYTHONIOENCODING=utf-8` for the Python processes it starts. Both previously relied on Python's platform default encoding, which is cp1252 on Windows, where eight of the fourteen lint checks aborted: reading a document containing box-drawing or em-dash characters raised `UnicodeDecodeError`, and printing a `✓` status mark raised `UnicodeEncodeError`. Linux and macOS behavior is unchanged. `tests/test-lint-untracked.sh` passes on Windows as a result.

## [1.4.0] - 2026-07-26

Arch Studio v1.4.0 is a breaking migration release. It preserves the public `1.x` release sequence while replacing the installed plugin identity and introducing the studio/project workspace architecture.

### Breaking

- **Shorter technical namespace.** Arch Studio now installs as `as@skills-for-architects`, and public commands use `/as:<skill>`. Existing users must remove the retired v1 install or installs, update the marketplace, install `as@skills-for-architects`, and reload plugins or restart Claude Code. User-owned project and workspace files are untouched. Manually maintained Claude settings must replace only the old plugin identifier with the new one.
- **One project-memory interface.** `/as:project` replaces `/as:project-dossier` and `/decision`; no compatibility aliases remain. Use `/as:project init`, `/as:project update` or `/as:project remember`, `/as:project decisions`, `/as:project record-decision`, and `/as:project supersede`.
- **Decision files are canonical.** `PROJECT.md` no longer maintains a Decisions table. Run `/as:project migrate` in an existing 1.x project; migration removes the table only after every row matches a decision file.

### Migration

Existing v1.3 users must update the `skills-for-architects` marketplace, uninstall `architecture-studio@skills-for-architects`, install `as@skills-for-architects`, and reload plugins or restart Claude Code. The reinstall changes plugin code only; it does not delete or rewrite user-owned project or workspace files.

Users moving directly from v1.2 or earlier should uninstall any installed numbered plugins (`00-due-diligence` through `09-project-dossier`), update the marketplace, and install `as@skills-for-architects`. They do not need to install v1.3 first.

After reinstalling, run `/as:studio`. If an existing project uses the v1.x `PROJECT.md` Decisions table, open that project and run `/as:project migrate`; review the proposed migration before approving it. Plugin reinstall does not migrate project records automatically.

Existing local welcome and update-check preferences remain in place because their stable `.architecture-studio-*` filenames and state location do not change with the plugin identifier.

### Architecture and extensibility

- **User-reviewed feedback** — `/as:studio-feedback` prepares minimal bug or feature fields, flags sensitive project information, explains that opening GitHub transmits the displayed URL parameters, and never submits an issue automatically.
- **GitHub issue forms** — bug and feature templates share exact field identifiers with `/as:studio-feedback` so users arrive at an editable, prefilled report.
- **Opt-in update notice** — update checking remains disabled until enabled through `/as:studio`; when enabled it is throttled to one bare request per day, fails silently, and notifies once per newer version.
- **Studio workspace setup** — `/as:studio init`, `/as:studio status`, `/as:studio projects`, `/as:studio create-project`, `/as:studio register-project`, and `/as:studio archive-project` manage a portable `STUDIO.md` registry and descendant project folders. Setup records working units, default country/state-or-region/city, and a plain-language data-governance boundary.
- **Firm-owned skills** — initialized studios include `.claude/skills/`, and `/as:skill-maker` defaults private firm procedures there from descendant projects.
- **Deterministic setup helpers and fixtures** — studio/project scaffolding, collision refusal, registration, archive, and lossless project migration have executable shell coverage.
- **Agent documentation moved outside `agents/`** so Claude registers exactly the seven intended native subagents rather than treating the former index README as an eighth agent.

### Data boundaries and onboarding

- **Lightweight onboarding** — running `/as:studio` displays the Arch Studio mark, creator, ALPA ownership/contact, license, and repository provenance before moving into setup. Setup uses one structured interaction gate per question or confirmation instead of asking once in prose and again in the UI. The first-session hook is now a concise visible discovery notice rather than an instruction that rewrites the user’s first response.
- **Project-record integrations** — meeting minutes, site reports, analysis skills, work plans, tasks, and time tracking hand facts and decisions to `/as:project` and discover decision files directly.
- **Installation remains non-mutating** — installing the plugin creates no user workspace, account, cloud store, git repository, or project files.
- **Local CSV product data** — `product-library.csv` is the sole persistent FF&E library; EPD parsing remains PDF-first, with `epd-library.csv` created only when the user explicitly saves reusable records. SIF conversion remains available as bounded interchange, not as the persistent schedule source.
- **Honest legacy migration** — existing `master-schedule.json` and `canoa.json` files are preserved as cloud-configuration evidence. Users export their former cloud rows to CSV before import; Arch Studio does not claim to migrate disconnected data.
- **Reserved connector boundary** — `/as:studio init` creates a root `.mcp.json` containing only an empty `mcpServers` object. It configures no provider, endpoint, credential, or OAuth flow, and projects do not receive MCP manifests.
- **Deferred formats and integrations** — XLS/XLSX product support and configured studio connectors remain outside v1.4.
- **Privacy disclosure** — documents the feedback transmission boundary and ordinary Cloudflare request metadata without treating endpoint traffic as anonymous users or daily active users.

### Project workflow and memory

- **Typed project-record workflow** — `/as:meeting-minutes` preserves discussion and promotion candidates, `/as:site-visit-report` separates observation from reported information and interpretation, `/as:tasklist` owns permanent action IDs and lifecycle history, and `/as:timetracker` reconstructs dated activity while requiring user-confirmed durations.
- **Linked record graph** — project facts, decisions, minutes, site reports, tasks, plans, and time entries remain independently owned, project-relative artifacts with explicit source links and non-destructive histories.

- **`/as:workplan` project context** — reads and cites relevant `PROJECT.md` facts, decision records, meetings, site reports, and tasks; decided records constrain plans, proposed decisions remain unresolved, and superseded decisions remain historical context.
- **`/as:studio` routing and `/as:tool-catalog` discoverability** — typed-record deliverables route to their owning skills, while an explicitly requested plan or coordination strategy retains `/as:workplan` precedence.
- **Project Dossier documentation renamed Project Records** to describe the connected workflow without implying one central record or database.

- **`/as:workplan`** — a self-contained, Markdown-only planning workflow for repository, operational, and AEC project-delivery work. It distinguishes work planning from floor plans and regulated analysis, separates facts from assumptions, traces requirements and decisions into verifiable work units, uses optional harness capabilities only when available, and stops at an explicit execution handoff.

### Learning and extension tooling

- **`/as:skill-maker`** — scaffold a new skill in three steps, no interview: copy the canonical bundled template, apply the PATTERNS.md checklist (read at runtime, single source), verify with `scripts/lint.sh` inside the catalog or a portable checklist outside it.
- **Post-install discovery** — a `SessionStart` hook (`session-start-welcome`) emits one concise notice that `/as:studio` and `/as:learn` are available, without changing the user’s first response. Together with the opt-in version notice, Arch Studio now has four hook handlers across three events.
- **`/as:learn` teaches three framing concepts** threaded through the course: this version stores project files locally while sending prompts and needed file contents to the configured Claude service, Arch Studio is an open-source harness on Claude Code, and course/project memory is plain markdown files — with an explicit markdown explainer at the first file creation. Future cloud-based versions may require accounts and use a different data model.
- **Terminal preflight** in the README — a hand-to-a-colleague page covering install → login → `/as:learn` for people who have never opened a terminal.

- **`/as:learn` restructured to six modules named for their lessons** (How we interact with each other · Nothing without your "yes" · Let's set some guidelines first · Plan first, build second · Creating your own skills · Get started) for an honest ~75-minute core plus a 30–60 min capstone. Plan mode, subagents, and the precedent study moved to a planned advanced track. Data privacy is taught in Module 2 alongside consent; Module 6 opens with a source-check and absence drill on a faithful summary (no planted errors), then a professional checklist offered but never imposed (firm data-governance policy, low-stakes project, work on a copy) and one real task; quitting /learn is honored immediately at any point. The deliverable thread is a site-visit report and a learner-built `/site-report` skill. The five sandbox project types were replaced by a single project — a fictional Brooklyn art museum expansion — one example path, same engineered flaws. Permission-prompt narration covers the "stop asking" option; the tutor spec itself was cut roughly in half. Old 0-indexed PROGRESS.md files migrate by content.
- Starter binder template: "Sign documents off as" → "Document attribution block" (AI documents are never signed or sealed), plus phase names and date-format lines.

### Fixes and optimization

- Clarified `/as:learn` and the welcome hook's data model: this version stores project files locally but sends prompts and needed contents to the configured Claude service; future cloud-based versions may require accounts and use a different model.
- Hardened `/as:skill-maker` target resolution, existing-skill collision handling, bundled-resource paths, and lint coverage for newly generated untracked files.
- Made the first-session welcome verify each bundled surface it reports and persist its one-time marker only after valid context is emitted.
- Removed the Shift+Tab plan-mode instruction (Shift+Tab cycles permission modes and can land in auto-accept — the opposite of the course's safety promise); plan-first is taught as a prompt phrase.
- Removed six stale duplicate sandbox files at the `sandbox/` root left over from the pre-selection layout.

## [1.3.0] - 2026-07-20

### Breaking

- **One plugin.** The 10-plugin marketplace (`00-due-diligence` … `09-project-dossier`) is consolidated into a single flat plugin, **`architecture-studio`** — one install now loads all 40 skills, all 7 agents, and both hooks. `marketplace.json` has a single entry with source `"./"`; the `plugins/` tree and all per-plugin manifests are gone. Existing per-plugin installs will not receive this or any future update — see Migration below.
- **Skill renames** — `skills-menu` → `skills` (help menu, still invoked as `/skills`) and `history` → `site-history` (invoke as `/site-history`, formerly `/history`). All other skill names are unchanged; they simply live flat under `skills/`.
- **`post-output-metadata` hook removed.** The Dispatcher's 3 hooks are now the plugin's 2: `post-write-disclaimer-check` and `pre-commit-spec-lint`, registered from the root `hooks/hooks.json`.

### Migration

Uninstall every old per-plugin install you have, refresh the marketplace, and install the single plugin:

```bash
# Uninstall the old per-plugin installs (skip any you never installed)
for p in 00-due-diligence 01-site-planning 02-zoning-analysis 03-programming \
         04-specifications 05-sustainability 06-materials-research \
         07-presentations 08-dispatcher 09-project-dossier; do
  claude plugin uninstall "$p@skills-for-architects"
done

# Refresh and install the one plugin
claude plugin marketplace update skills-for-architects
claude plugin install architecture-studio@skills-for-architects
```

Everything the ten plugins provided is included; no skill was dropped. **Community-marketplace maintainers:** listings that pin a pre-1.3.0 commit or reference `plugins/<name>` source paths no longer resolve — re-pin to the `v1.3.0` tag and replace the ten entries with the single `architecture-studio` entry (source `"./"`).

### Added

- **`/learn`** — a guided, resumable Claude Code course for architects: eight hands-on modules on a bundled sandbox project, a starter `CLAUDE.md` template distilled from the studio rules, and three example skills to study and modify. Progress persists in `PROGRESS.md`.
- **`/learn` sandbox choice** — the course opens with a menu of five fictional practice projects (Brooklyn loft conversion, healthcare campus, workplace fit-out, restaurant, ground-up school), each with the same six deliberately messy files and identical planted flaws, so every module works on any of them. All characters are roles (the owner, the zoning consultant) — no invented names.
- **`/learn` progress bar** — a 24-cell ASCII bar in the return check-in and after each completed module.
- **`/studio` → `/learn`** — the router now sends users who are new to Claude Code to the course, and the fallback menu points at it.

### Fixed

- **Socrata corrections** (`nyc-property-report` + the six NYC data skills `nyc-acris`, `nyc-bsa`, `nyc-dob-permits`, `nyc-dob-violations`, `nyc-hpd`, `nyc-landmarks`) — `socrata-reference.md` is now the single source of truth; dataset IDs and field names corrected and live-verified against NYC Open Data. New `pluto-resolution.md` documents address→BBL resolution for `nyc-property-report`.
- **Hooks** — `pre-commit-spec-lint` now detects real `git commit` invocations (compound commands, `-C` flags) and exits 2 with the CSI message on stderr; `post-write-disclaimer-check` reads the written file from disk, handles both `Write` and `Edit` tool payloads, and emits proper `{"decision":"block"}` JSON; `hooks.json` drops an invalid `"if"` key and matches `Write|Edit` on PostToolUse. Both scripts are BSD-safe (grep boundaries, `printf` over `echo -e`).
- **Skill-relative data paths** — `occupancy-calculator` reads its bundled `data/*.json` from the skill's own directory instead of a hardcoded `~/.claude/skills/...` path.
- **EPD baseline policy** (`epd-compare`, `epd-to-spec`) — industry-average baselines must be citable (named source + publication year, labeled in the comparison table); uncitable baselines are omitted, never guessed.
- **Zoning and occupancy content** — corrections across `zoning-analysis-nyc`'s zoning-rules references (contextual districts, manufacturing, commercial, residential) and `zoning-envelope`; `occupancy-calculator` gross/net guidance tightened. Smaller doc fixes in `workplace-programmer`, `mobility-analysis`, the EPD skills, and `slide-deck-generator`.

### Changed

- **Disclaimer pipeline wired end-to-end** — all 11 regulatory skills (`zoning-analysis-nyc`, `zoning-envelope`, `occupancy-calculator`, `epd-to-spec`, `nyc-property-report` and its six data skills) now end regulatory output with the canonical disclaimer block plus the `requires-disclaimer` marker the hook checks for; `zoning-envelope` carries an HTML-adapted variant for the 3D viewer. `rules/README.md` no longer claims rules auto-load.
- **Skill descriptions rewritten with trigger + boundary phrasing** across 32 skills — the description is the only signal Claude uses to auto-select among 40 skills.
- **`scripts/lint.sh` rewritten for the flat layout** — count consistency is derived from the tree (skills, agents, hooks, `/skills` menu, README, `marketplace.json`), plus regression checks pinning the 1.3.0 fixes; CI installs its own dependencies.
- **README and `/skills` menu rebuilt for one plugin** — single-entry install, counts derived (40 skills, 7 agents), and the old 00–09 taxonomy kept as documentation-only groups.

## [1.2.1] - 2026-06-10

### Changed

- **README** — "What's New in 1.2" section added below the headline, summarizing the dossier plugin, native subagents, and self-registering hooks; links to the CHANGELOG for full history.

## [1.2.0] - 2026-06-10

### Added

- **`09-project-dossier` plugin** (`1.0.0`) — persistent per-project state as plain files in the project folder. `/project-dossier` maintains `PROJECT.md`, the facts layer (identity, site, zoning, program, code — every entry sourced and dated, updated in place). `/decision` captures the reasoning layer: ADR-style records in `decisions/NNNN-slug.md` with context, options considered, the call, consequences, and a status (proposed / decided / superseded — never deleted, never renumbered). Eleven analysis skills now read the dossier before fetching, append their findings after completing, and propose `/decision` when an analysis forces a choice (zoning path, code edition, GWP threshold). Collaboration is deliberately git-native: files, not infrastructure.
- **Agents register as native Claude Code subagents.** The 7 agents moved from the repo root into their plugins' `agents/` directories with `name`/`description` frontmatter — installing a plugin now registers its agent (automatic delegation, routing by description). `/studio` still routes to them; reading the agent file inline is the documented fallback when a plugin isn't installed. `agents/README.md` remains as the cross-plugin index.
- **Hooks auto-register.** The 3 hooks moved to `plugins/08-dispatcher/hooks/` with a `hooks.json` — enabling the Dispatcher plugin registers them automatically. The manual `settings-snippet.json` merge is retired (users who merged it should remove those entries).

### Changed

- **`slide-deck-generator` restructured for progressive disclosure** — `SKILL.md` 869 → 145 lines; component markup moved to `slide-types.md`, the HTML/CSS/JS template to `html-template.md`, the image workflow to `image-handling.md`, each loaded on demand.
- **4 NYC due-diligence descriptions rewritten** (`nyc-acris`, `nyc-bsa`, `nyc-dob-permits`, `nyc-dob-violations`) with trigger + boundary phrasing — the description is the only signal Claude uses to auto-select among 39 skills.
- **`allowed-tools` added** to the 4 skills missing it: `occupancy-calculator`, `workplace-programmer`, `color-palette-generator`, `slide-deck-generator`.
- **`rules/` enforcement documented honestly** — 2 rules are hook-enforced (disclaimer, CSI), 5 are advisory conventions the skills are written against; nothing auto-loads a `rules/` directory.
- **README** — architecture diagram reflects plugin-native agents and hooks; counts now 39 skills / 10 plugins.

### Removed

- **`user-invocable` frontmatter field** from 25 skills — not part of the current SKILL.md schema; skills are slash-invocable by default. `PATTERNS.md` §1 updated.

## [1.1.3] - 2026-06-10

### Changed

- **README** — release badge added next to the license badge; Materials Research plugin row notes SIF + [Norma](https://norma.llc) export; CHANGELOG linked from Contributing.

## [1.1.2] - 2026-06-10

### Changed

- **`06-materials-research` is standalone** (plugin `1.1.0`). The plugin's config file is renamed `canoa.json` → `master-schedule.json`; `/master-schedule` migrates a legacy `canoa.json` automatically on its next run. `/product-spec-bulk-fetch` now points schedule export at [Norma](https://norma.llc). The Google Sheet workflow itself has no product dependency.
- **NYC zoning terminology** (plugin `02-zoning-analysis` `1.1.1`). `zoning-analysis-nyc`'s reference-file table header and step heading renamed from "Normativa" to "Zoning Rules" / "Rules File".
- **`PATTERNS.md` examples are self-contained.** External-org references removed from the conventions doc (sibling-repo list, naming tables, dispatcher reference implementations, layout names); examples now draw on this repo and canoa only.

## [1.1.1] - 2026-05-08

### Changed

- **`PATTERNS.md` rule #6 expanded.** Versioning discipline now spans three artifacts that must move together on every shipped change: the JSON `version` field (`plugin.json` and/or `marketplace.json` `metadata.version`), a git tag (`git tag -a vX.Y.Z`), and a GitHub release (`gh release create vX.Y.Z --notes-file <changelog-section>`). The rule previously stopped at JSON + CHANGELOG, leaving repo discoverability gaps — `git checkout v1.1.0` didn't resolve, no shareable release URL existed. Backfilled tags + releases for `v1.1.0` (this repo) and `v0.2.0` (canoa).

## [1.1.0] - 2026-05-08

### Added

- **`PATTERNS.md`** — canonical reference for ALPA's plugin and marketplace conventions. Ten principles distilled from canoa V1 and skills-for-architects v1.0: small one-verb skills, dispatcher matching plugin name, `<plugin>-<verb>` naming for single-plugin layouts, marker-driven rules, version bump per ship, public default, MCP bundling via `${CLAUDE_PLUGIN_ROOT}`, hard rules captured from real production bugs. Linked from README. Rule #6 (versioning) covers both `plugin.json` and `marketplace.json` `metadata.version`.
- `.gitignore` covering macOS, editor, and local-env artifacts.
- `scripts/lint.sh` — repo lint script with six structural checks: no tracked `.DS_Store`, JSON validity, SKILL.md frontmatter (`name` + `description` required), count consistency (plugins, per-plugin skill counts, marketplace.json), internal markdown link resolution, and shellcheck on `hooks/*.sh`.
- `.github/workflows/lint.yml` — runs `scripts/lint.sh` on push to `main` and on every PR.

### Changed

- **Disclaimer hook is now marker-driven, not keyword-sniffed.** `rules/professional-disclaimer.md` now requires every regulatory output to end with the canonical disclaimer block followed by `<!-- architecture-studio:requires-disclaimer -->`. The `post-write-disclaimer-check` hook checks for the marker and verifies the canonical block is present, instead of pattern-matching keywords like `FAR`, `setback`, `egress`. This eliminates false positives on non-regulatory documents that mention regulated terms in passing (READMEs, changelogs, meeting notes) and false negatives on terse regulatory replies that happen not to use those keywords.
- **Skill counts now reflect actual file count.** README headline, details summary, plugin table, and the dispatcher's `/skills` menu all read **37 skills** (up from "35"). The 2-skill gap was the dispatcher's `/studio` and `/skills`, which were uncounted by convention. The README catalog now includes a Dispatcher section listing them. `scripts/lint.sh` enforces that headline, details summary, catalog row count, plugin-table per-row counts, skills-menu, and `marketplace.json` plugin list all match the real file count — drift fails CI.

### Removed

- 11 tracked `.DS_Store` files. Now ignored repo-wide via `.gitignore`.

## [1.0.0] - 2026-05-06

First public release.

### Added

- **7 agents** — `site-planner`, `nyc-zoning-expert`, `workplace-strategist`, `product-and-materials-researcher`, `ffe-designer`, `sustainability-specialist`, `brand-manager`.
- **35 skills** across **9 plugins**:
  - `00-due-diligence` (7) — NYC landmarks, DOB permits, DOB violations, ACRIS, HPD, BSA, combined property report.
  - `01-site-planning` (4) — environmental, mobility, demographics, history.
  - `02-zoning-analysis` (2) — `/zoning-analysis-nyc` (PLUTO + Zoning Resolution), `/zoning-envelope` (Three.js 3D viewer).
  - `03-programming` (2) — workplace programmer, IBC occupancy calculator.
  - `04-specifications` (1) — CSI MasterFormat outline specs.
  - `05-sustainability` (4) — EPD parse, research, compare, spec.
  - `06-materials-research` (12) — product research, spec extraction, schedule cleanup, image processing, master schedule, SIF crosswalk.
  - `07-presentations` (3) — slide decks, color palettes, image resizing.
  - `08-dispatcher` (2) — `/studio` router, `/skills` menu.
- **7 rules** — units & measurements, code citations, professional disclaimer, CSI formatting, terminology, output formatting, transparency.
- **3 hooks** — post-write disclaimer check, post-output metadata, pre-commit spec lint.
- Marketplace install: `claude plugin marketplace add AlpacaLabsLLC/skills-for-architects`.

[Unreleased]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.4...HEAD
[1.5.4]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.3...v1.5.4
[1.5.3]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.2...v1.5.3
[1.5.2]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.1.2...v1.5.2
[1.5.1.2]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.1.1...v1.5.1.2
[1.5.1.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.1...v1.5.1.1
[1.5.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.5.0...v1.5.1
[1.5.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.4.5...v1.5.0
[1.4.5]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.4.5
[1.4.4]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.4.4
[1.4.3]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.4.3
[1.4.2]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.4.2
[1.4.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.4.1
[1.4.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.4.0
[1.3.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.3.0
[1.2.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.2.1
[1.2.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.2.0
[1.1.3]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.3
[1.1.2]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.2
[1.1.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.1
[1.1.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.0
[1.0.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.0.0
