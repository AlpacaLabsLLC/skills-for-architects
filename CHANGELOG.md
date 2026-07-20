# Changelog

All notable changes to **Architecture Studio** (`AlpacaLabsLLC/skills-for-architects`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Post-install welcome** — a `SessionStart` hook (`session-start-welcome`) fires once on the first session after install: confirms the plugin loaded (with a partial-install warning if skills are missing) and offers `/learn`. Hook count is now 3.
- **`/learn` teaches three framing concepts** threaded through the course: work stays local (files never leave the machine except what's asked about), Architecture Studio is an open-source harness on Claude Code, and memory is plain markdown files — with an explicit markdown explainer at the first file creation.
- **Terminal preflight** in the README — a hand-to-a-colleague page covering install → login → `/learn` for people who have never opened a terminal.

### Changed

- **`/learn` restructured to seven modules** for an honest ~90-minute core: the former Module 5 (plan mode, subagents) and the Module 4 precedent study moved to a planned advanced track; "plan first" remains taught in Module 2. Module 1's deliverable is now a site-visit report (not "minutes") with a source spot-check; Module 4 builds `/site-report`; Module 5 (Trust) adds a client-data/discretion beat; the capstone gains a mandatory pre-check (firm policy, low-stakes project, always work on a copy) and an honest 30–60 min label. Permission-prompt narration now covers the "stop asking" option. Existing 8-row PROGRESS.md files migrate by module name.
- Starter binder template: "Sign documents off as" → "Document attribution block" (AI documents are never signed or sealed), plus phase names and date-format lines.

### Fixed

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

[Unreleased]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.3.0
[1.2.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.2.1
[1.2.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.2.0
[1.1.3]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.3
[1.1.2]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.2
[1.1.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.1
[1.1.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.0
[1.0.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.0.0
