# Changelog

All notable changes to **Architecture Studio** (`AlpacaLabsLLC/skills-for-architects`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[Unreleased]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.2.0
[1.1.3]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.3
[1.1.2]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.2
[1.1.1]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.1
[1.1.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.1.0
[1.0.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.0.0
