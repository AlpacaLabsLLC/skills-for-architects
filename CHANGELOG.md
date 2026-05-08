# Changelog

All notable changes to **Architecture Studio** (`AlpacaLabsLLC/skills-for-architects`) are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **`PATTERNS.md`** — canonical reference for ALPA's plugin and marketplace conventions. Ten principles distilled from canoa V1, normativa v0.8, and skills-for-architects v1.0: small one-verb skills, dispatcher matching plugin name, `<plugin>-<verb>` naming for single-plugin layouts, marker-driven rules, version bump per ship, public default, MCP bundling via `${CLAUDE_PLUGIN_ROOT}`, hard rules captured from real production bugs. Linked from README.
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

[Unreleased]: https://github.com/AlpacaLabsLLC/skills-for-architects/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/AlpacaLabsLLC/skills-for-architects/releases/tag/v1.0.0
