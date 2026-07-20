<div align="center">

```
 █████╗ ██████╗  ██████╗██╗  ██╗    ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗
██╔══██╗██╔══██╗██╔════╝██║  ██║    ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗
███████║██████╔╝██║     ███████║    ███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║
██╔══██║██╔══██╗██║     ██╔══██║    ╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║
██║  ██║██║  ██║╚██████╗██║  ██║    ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝
```

**Architecture Studio**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/AlpacaLabsLLC/skills-for-architects)](https://github.com/AlpacaLabsLLC/skills-for-architects/releases)

</div>

> One plugin of agents, skills, and rules for architects, designers, and AEC professionals — use with [Claude Desktop](https://claude.ai) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

**Architecture Studio** teaches Claude architecture-specific workflows — site analysis, zoning, space programming, specifications, materials research, sustainability, and presentations.

**One plugin** — `architecture-studio` v1.3.0 — with **40 skills**, **7 agents**, **7 rules**, and **2 hooks**. Built by [ALPA](https://alpa.llc).

## What's New in 1.3

- **One flat plugin.** The ten-plugin marketplace is now a single plugin: one install gets every skill, agent, and hook. The old per-plugin taxonomy (Due Diligence, Site Planning, Zoning, …) survives below as documentation groups — nothing to choose at install time.
- **Renames:** the site history skill is now `/site-history` (formerly `history`); the help menu skill is `/skills` (formerly `skills-menu`).
- **`/learn`** — a guided, resumable course teaching architects Claude Code itself, on a bundled sandbox project you pick (loft conversion, healthcare campus, workplace, restaurant, or ground-up school).

Full history in the [CHANGELOG](./CHANGELOG.md).

## Architecture

```
Architecture Studio (one plugin: architecture-studio)
├── skills/          40 skills — one directory each, flat
│   ├── /studio      ← entry point: describe a task, get routed
│   └── /skills      ← help menu
├── agents/           7 orchestration subagents
├── hooks/            2 event-driven automations (auto-register)
├── rules/            7 cross-cutting conventions (2 hook-enforced, 5 advisory)
└── schema/           shared FF&E product schema (33 columns) + SIF crosswalk
```

**Agents** orchestrate skills — they assess your input, choose a path, and exercise judgment; each registers as a native Claude Code subagent. **Skills** are single-purpose tools invoked with a slash command. **Rules** are cross-cutting conventions. **Hooks** are event-driven automations that register automatically when the plugin is enabled.

## Quick Start

### Install

**Claude Desktop:** Open **Customize** → **Browse plugins** → **+** → **Add marketplace from GitHub** → enter `AlpacaLabsLLC/skills-for-architects` → install **Architecture Studio**

**Claude Code:**
```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install architecture-studio@skills-for-architects
```

That single install loads all 40 skills, all 7 agents, and the 2 hooks.

### Use

Type `/studio` followed by what you need. The router reads your request and hands off to the right agent or skill.

```
/studio task chair, mesh back, under $800
/studio 123 Main St, Brooklyn NY
/studio I need a space program for 200 people
/studio parse this EPD
```

Type `/skills` for the full menu. Or call any skill directly by name (e.g. `/environmental-analysis 123 Main St`). New to Claude Code entirely? Start with `/learn`.

## Agents

Agents are the orchestration layer. Describe your task — the agent decides which skills to call, in what order, and what judgment to apply.

| Agent | Domain | What it does |
|-------|--------|-------------|
| [site-planner](./agents/site-planner.md) | Site Planning | Runs all site research in parallel, synthesizes a unified brief with opportunities and constraints |
| [nyc-zoning-expert](./agents/nyc-zoning-expert.md) | Due Diligence + Zoning | Full NYC property and zoning analysis — due diligence, buildable envelope, 3D visualization |
| [workplace-strategist](./agents/workplace-strategist.md) | Programming | Translates headcount and work style into space programs — occupancy compliance, zone allocation, room schedules |
| [product-and-materials-researcher](./agents/product-and-materials-researcher.md) | Materials Research | Finds products from a brief, extracts specs from URLs/PDFs, tags and classifies, finds alternatives |
| [ffe-designer](./agents/ffe-designer.md) | FF&E Design | Builds clean schedules from messy inputs, composes room packages, runs QA, exports to dealer formats |
| [sustainability-specialist](./agents/sustainability-specialist.md) | Sustainability | Evaluates environmental impact — finds EPDs, compares GWP, checks LEED eligibility, writes spec thresholds |
| [brand-manager](./agents/brand-manager.md) | Presentations | Owns visual identity — builds decks, creates palettes, QAs deliverables for presentation readiness |

See the [agents index](./agents/README.md) for full workflows and handoff logic.

## Skill Groups

All 40 skills live flat in [`skills/`](./skills) and install together. The groups below are documentation only — the former plugin taxonomy, kept because it maps to the project lifecycle from due diligence through delivery.

| Group | Skills | Description |
|-------|--------|-------------|
| [Due Diligence](#due-diligence) | 7 | NYC property data: landmarks, DOB permits, violations, ACRIS, HPD, BSA. NYC Open Data (Socrata) — no API key required. |
| [Site Planning](#site-planning) | 4 | Site research: environmental, mobility, demographics, site history. |
| [Zoning Analysis](#zoning-analysis) | 2 | Zoning envelope analysis and 3D visualization for NYC. |
| [Programming](#programming) | 2 | Workplace strategy: space programs, occupancy loads, IBC compliance. |
| [Specifications](#specifications) | 1 | CSI outline specifications from a materials list. |
| [Sustainability](#sustainability) | 4 | EPD parsing, research, comparison, and GWP thresholds. |
| [Materials Research](#materials-research) | 12 | FF&E product research, spec extraction, cleanup, and image processing. Exports to SIF dealer formats and [Norma](https://norma.llc). |
| [Presentations](#presentations) | 3 | Slide deck generation, color palettes, and image resizing for web, social, slides, and print. |
| [Dispatcher](#dispatcher) | 2 | Studio router (`/studio`) and help menu (`/skills`). |
| [Project Dossier](#project-dossier) | 2 | Persistent project facts (`PROJECT.md`) and ADR-style decision records. |
| [Learn](#learn) | 1 | Guided course teaching architects Claude Code itself — hands-on, resumable. |

### Due Diligence

All lookups query the NYC Open Data Socrata API and resolve addresses via PLUTO — no authentication required. Each skill's own README documents the exact datasets it queries.

| Skill | Description |
|-------|-------------|
| [`/nyc-landmarks`](./skills/nyc-landmarks) | LPC landmark and historic district check |
| [`/nyc-dob-permits`](./skills/nyc-dob-permits) | DOB permit and filing history |
| [`/nyc-dob-violations`](./skills/nyc-dob-violations) | DOB and ECB violations |
| [`/nyc-acris`](./skills/nyc-acris) | ACRIS property transaction records |
| [`/nyc-hpd`](./skills/nyc-hpd) | HPD violations, complaints, and registration |
| [`/nyc-bsa`](./skills/nyc-bsa) | BSA variances and special permits |
| [`/nyc-property-report`](./skills/nyc-property-report) | Combined NYC property report — all 6 above |

### Site Planning

Each skill takes an address, researches authoritative public sources (NOAA, USGS, EPA, Census Bureau, BLS, MTA, DOT, LPC, National Register), and writes a structured markdown report with a Key Metrics table.

| Skill | Description |
|-------|-------------|
| [`/environmental-analysis`](./skills/environmental-analysis) | Climate, precipitation, wind, sun angles, flood zones, seismic risk, soil |
| [`/mobility-analysis`](./skills/mobility-analysis) | Transit, walk/bike/transit scores, pedestrian infrastructure |
| [`/demographics-analysis`](./skills/demographics-analysis) | Population, income, age, housing market, employment |
| [`/site-history`](./skills/site-history) | Neighborhood context, landmarks, commercial activity, planned development |

### Zoning Analysis

| Skill | Description |
|-------|-------------|
| [`/zoning-analysis-nyc`](./skills/zoning-analysis-nyc) | NYC buildable envelope — FAR, height, setbacks, use groups from PLUTO and bundled Zoning Resolution rules |
| [`/zoning-envelope`](./skills/zoning-envelope) | Interactive 3D zoning envelope viewer — self-contained HTML from any zoning analysis report |

### Programming

| Skill | Description |
|-------|-------------|
| [`/workplace-programmer`](./skills/workplace-programmer) | Space programs from headcount and work style — area splits, room schedules, seat counts backed by industry research |
| [`/occupancy-calculator`](./skills/occupancy-calculator) | IBC occupancy loads (Table 1004.5), egress width, exit counts, plumbing fixtures |

### Specifications

| Skill | Description |
|-------|-------------|
| [`/spec-writer`](./skills/spec-writer) | CSI outline specs — MasterFormat 2020 divisions, three-part sections, `[REVIEW REQUIRED]` flags |

### Sustainability

The four skills form a natural pipeline — parse EPD PDFs → research registries → compare on GWP → generate spec language — but each works standalone. All share one EPD data schema covering impact indicators and LEED MRc2 eligibility.

| Skill | Description |
|-------|-------------|
| [`/epd-parser`](./skills/epd-parser) | Extract data from EPD PDFs — GWP, life cycle stages, certifications |
| [`/epd-research`](./skills/epd-research) | Search EC3, UL, Environdec for EPDs by material or category |
| [`/epd-compare`](./skills/epd-compare) | Side-by-side environmental impact comparison with LEED eligibility check |
| [`/epd-to-spec`](./skills/epd-to-spec) | CSI specs with EPD requirements and GWP thresholds |

### Materials Research

Every skill reads from and writes back to one master Google Sheet — a shared 33-column schema regardless of source. Column definitions, category vocabulary, sheet conventions, and the SIF dealer crosswalk live in [`schema/`](./schema): [product-schema.md](./schema/product-schema.md) · [sheet-conventions.md](./schema/sheet-conventions.md) · [sif-crosswalk.md](./schema/sif-crosswalk.md).

| Skill | Description |
|-------|-------------|
| [`/master-schedule`](./skills/master-schedule) | Connect a product library sheet to the project (auto-runs before other skills) |
| [`/product-research`](./skills/product-research) | Find products from a design brief |
| [`/product-spec-bulk-fetch`](./skills/product-spec-bulk-fetch) | Extract specs from product URLs at scale |
| [`/product-spec-pdf-parser`](./skills/product-spec-pdf-parser) | Extract specs from PDF catalogs, price books, and spec sheets |
| [`/product-data-cleanup`](./skills/product-data-cleanup) | Normalize casing, categories, dimensions, materials, language |
| [`/product-data-import`](./skills/product-data-import) | Turn raw product lists into formatted FF&E specification schedules |
| [`/product-enrich`](./skills/product-enrich) | Auto-tag products with categories, colors, materials, and style tags |
| [`/product-match`](./skills/product-match) | Find similar products from an image, name, or description |
| [`/product-pair`](./skills/product-pair) | Suggest complementary products |
| [`/product-image-processor`](./skills/product-image-processor) | Batch download, resize, remove backgrounds |
| [`/csv-to-sif`](./skills/csv-to-sif) | Convert CSV to SIF for dealer systems |
| [`/sif-to-csv`](./skills/sif-to-csv) | Convert SIF files into readable spreadsheets |

### Presentations

| Skill | Description |
|-------|-------------|
| [`/slide-deck-generator`](./skills/slide-deck-generator) | Self-contained HTML slide decks — editorial layout, 22 slide types |
| [`/color-palette-generator`](./skills/color-palette-generator) | Color palettes from descriptions, images, or brand references, with WCAG contrast checks |
| [`/resize-images`](./skills/resize-images) | Batch-resize photos for web (WebP), social, slides (4:3/16:9), and print (ARCH A/B/C at 300 DPI) |

### Dispatcher

| Skill | Description |
|-------|-------------|
| [`/studio`](./skills/studio) | Smart router — describe a task and get routed to the right agent or skill |
| [`/skills`](./skills/skills) | Help menu listing all available skills and agents |

### Project Dossier

Two layers of persistent per-project state, as plain files in the project folder: **facts** (`PROJECT.md` — what is, each entry sourced and dated) and **reasoning** (`decisions/` — why it is, ADR-style). Analysis skills check the dossier before fetching, append findings after, and propose `/decision` when an analysis forces a choice. Files, not a platform — shared however the project already is.

| Skill | Description |
|-------|-------------|
| [`/project-dossier`](./skills/project-dossier) | Create or update `PROJECT.md` — sourced, dated project facts |
| [`/decision`](./skills/decision) | ADR-style decision records — context, options, the call, consequences |

### Learn

| Skill | Description |
|-------|-------------|
| [`/learn`](./skills/learn) | Guided course teaching architects Claude Code — 8 hands-on modules (~15–20 min each) on a bundled sandbox project you pick from five types, resumable anytime. Module 6 is a planted-error exercise in challenging AI output before you ever touch a real project. |

## Rules

Cross-cutting conventions every skill is written against. Two are hook-enforced (professional-disclaimer, csi-formatting); the other five are advisory references — see [rules/](./rules) for the honest breakdown.

| Rule | What it governs |
|------|-----------------|
| [units-and-measurements](./rules/units-and-measurements.md) | Imperial/metric, area types (GSF/USF/RSF), dimensions |
| [code-citations](./rules/code-citations.md) | Building code references, edition years, jurisdiction awareness |
| [professional-disclaimer](./rules/professional-disclaimer.md) | Disclaimer language, what AI outputs can and cannot claim |
| [csi-formatting](./rules/csi-formatting.md) | MasterFormat 2018 section numbers, three-part structure |
| [terminology](./rules/terminology.md) | AEC standard terms, abbreviations, material names |
| [output-formatting](./rules/output-formatting.md) | Tables, source attribution, file naming, list structure |
| [transparency](./rules/transparency.md) | Show your work — link sources, expose inputs, make outputs verifiable |

## Hooks

Event-driven automations — they ship with the plugin and register automatically when it's enabled. No settings merge needed.

| Hook | Event | What it does |
|------|-------|-------------|
| [post-write-disclaimer-check](./hooks/post-write-disclaimer-check.sh) | After Write or Edit | Warns if regulatory output is missing the professional disclaimer |
| [pre-commit-spec-lint](./hooks/pre-commit-spec-lint.sh) | Before git commit | Flags malformed CSI section numbers |

See the [hooks directory](./hooks) for details and customization.

## Contributing

Want to add a skill for the built environment?

1. **Fork** this repository
2. Create your skill as a new directory under [`skills/`](./skills)
3. Each skill needs a `SKILL.md` with instructions and domain knowledge, a `README.md`, and any supporting data files
4. Open a **pull request** — describe what the skill does, how you tested it, and sample output

For the full conventions we apply across all our plugins (naming, layout, dispatcher pattern, versioning, hard rules from real bugs), read [PATTERNS.md](./PATTERNS.md). Release history lives in the [CHANGELOG](./CHANGELOG.md).

For guidance on organizing skills across a team, read [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams).

## License

MIT — see [LICENSE](LICENSE).

---

Built by [ALPA](https://alpa.llc) — research, strategy, and technology for the built environment.

**Read more:** [Claude Code Cheat Sheet for Architects](https://alpa.llc/articles/claude-code-cheat-sheet) · [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams)
