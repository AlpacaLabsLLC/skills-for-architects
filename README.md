# Studio

> Agents, skills, and rules for architects, designers, and AEC professionals — use with [Claude Desktop](https://claude.ai) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Studio** teaches Claude architecture-specific workflows — site analysis, zoning, space programming, specifications, materials research, sustainability, and presentations.

**36 skills**, **7 agents**, **6 rules**, and **3 hooks** across **9 plugins**. Built by [ALPA](https://alpa.llc).

## Prerequisites

- **Claude Desktop** (recommended) or **Claude Code CLI**
- A [Claude subscription](https://claude.ai) (Pro, Max, Team, or Enterprise)

## What Are Skills and Plugins?

- **Skills** teach Claude about a design topic — like calculating occupancy loads, analyzing zoning envelopes, or writing CSI specs. You invoke them with a slash command (e.g. `/environmental-analysis`).
- **Plugins** group related skills together by project lifecycle phase.
- **Agents** are autonomous specialists that orchestrate multiple skills — they assess your input, choose a path, and exercise judgment. For example, the Site Planner runs all four site planning skills in parallel and synthesizes a unified brief.

## Quick Start

### Option A: Claude Desktop — recommended

1. Open **Customize** → **Browse plugins** → click **+** → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the plugins you want from the **Personal** tab
4. Type `/skills` in any conversation to verify

Updates sync through the marketplace automatically.

### Option B: Claude Code (CLI)

```bash
# Add the marketplace (one-time)
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects

# Install a single plugin
claude plugin install 01-site-planning@skills-for-architects

# Or clone and symlink individual skills
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/01-site-planning/skills/environmental-analysis ~/.claude/skills/environmental-analysis
```

Plugin-installed skills sync automatically. Symlinked skills stay in sync when you `git pull`.

## Where to Start

**Don't know which skill to use?** Type `/studio` followed by what you need:

```
/studio task chair, mesh back, under $800
/studio 123 Main St, Brooklyn NY
/studio I need a space program for 200 people
/studio parse this EPD
```

The router reads your request and hands off to the right agent or skill. Type `/skills` to see the full menu.

**Already know what you want?** Call any skill directly:

| I need to... | Run this |
|--------------|----------|
| Full NYC property due diligence | `/nyc-property-report 123 Main St` |
| Research a new site | `/environmental-analysis 123 Main St` |
| Check NYC zoning | `/zoning-analysis-nyc 123 Main St` |
| Analyze a lot in Uruguay | `/zoning-analysis-uruguay` |
| Build a space program | `/workplace-programmer` |
| Calculate occupancy loads | `/occupancy-calculator` |
| Write CSI specs | `/spec-writer` |
| Parse an EPD PDF | `/epd-parser ~/Downloads/EPD.pdf` |
| Find products | `/product-research` |
| Generate a slide deck | `/slide-deck-generator` |

## Plugins

Organized by project lifecycle — from due diligence through delivery.

| # | Plugin | Skills | Description |
|---|--------|--------|-------------|
| 0 | [00-due-diligence](./plugins/00-due-diligence) | 7 | NYC property data: landmarks, DOB permits, violations, ACRIS, HPD, BSA. |
| 1 | [01-site-planning](./plugins/01-site-planning) | 4 | Site research: environmental, mobility, demographics, history. |
| 2 | [02-zoning-analysis](./plugins/02-zoning-analysis) | 3 | Zoning envelope analysis and 3D visualization for NYC and Maldonado, Uruguay. |
| 3 | [03-programming](./plugins/03-programming) | 2 | Workplace strategy: space programs, occupancy loads, IBC compliance. |
| 4 | [04-specifications](./plugins/04-specifications) | 1 | CSI outline specifications from a materials list. |
| 5 | [05-sustainability](./plugins/05-sustainability) | 4 | EPD parsing, research, comparison, and CSI specification with GWP thresholds. |
| 6 | [06-materials-research](./plugins/06-materials-research) | 11 | FF&E product research, spec extraction, cleanup, and image processing. |
| 7 | [07-presentations](./plugins/07-presentations) | 2 | Slide deck generation and color palette creation. |
| 8 | [08-dispatcher](./plugins/08-dispatcher) | 2 | Studio router (`/studio`) and help menu (`/skills`). |

## All Skills

### 0. Due Diligence

| Skill | Description |
|-------|-------------|
| [`/nyc-landmarks`](./plugins/00-due-diligence/skills/nyc-landmarks) | LPC landmark and historic district check — designation status, LP number, architect, style, permit implications. |
| [`/nyc-dob-permits`](./plugins/00-due-diligence/skills/nyc-dob-permits) | DOB permit and filing history across Legacy BIS and DOB NOW — 4 datasets, grouped by job type. |
| [`/nyc-dob-violations`](./plugins/00-due-diligence/skills/nyc-dob-violations) | DOB and ECB violations — open violations flagged, ECB penalties with amounts assessed and balance due. |
| [`/nyc-acris`](./plugins/00-due-diligence/skills/nyc-acris) | ACRIS property transaction records — deeds, mortgages, liens via 3-table join. |
| [`/nyc-hpd`](./plugins/00-due-diligence/skills/nyc-hpd) | HPD violations, complaints, and registration for residential buildings. |
| [`/nyc-bsa`](./plugins/00-due-diligence/skills/nyc-bsa) | BSA variances and special permits — application history from 1998. |
| [`/nyc-property-report`](./plugins/00-due-diligence/skills/nyc-property-report) | Combined NYC property report — runs all 6 property skills, one document. |

### 1. Site Planning

| Skill | Description |
|-------|-------------|
| [`/environmental-analysis`](./plugins/01-site-planning/skills/environmental-analysis) | Climate and environmental site analysis — temperature, precipitation, wind, sun angles, flood zones, seismic risk, soil, topography. |
| [`/mobility-analysis`](./plugins/01-site-planning/skills/mobility-analysis) | Transit and mobility site analysis — subway, bus, bike, pedestrian infrastructure, walk scores, airport access. |
| [`/demographics-analysis`](./plugins/01-site-planning/skills/demographics-analysis) | Demographics and market site analysis — population, income, age, housing market, employment. |
| [`/history`](./plugins/01-site-planning/skills/history) | Neighborhood context and history — adjacent uses, architectural character, landmarks, commercial activity, planned development. |


### 2. Zoning Analysis

| Skill | Description |
|-------|-------------|
| [`/zoning-analysis-nyc`](./plugins/02-zoning-analysis/skills/zoning-analysis-nyc) | Buildable envelope analysis for lots in New York City — FAR, height, setbacks, use groups from PLUTO data and the Zoning Resolution. |
| [`/zoning-analysis-uruguay`](./plugins/02-zoning-analysis/skills/zoning-analysis-uruguay) | Buildable envelope analysis for lots in Maldonado, Uruguay — FOS, FOT, height, setbacks from TONE regulations. |
| [`/zoning-envelope`](./plugins/02-zoning-analysis/skills/zoning-envelope) | Interactive 3D zoning envelope viewer — exact lot polygon, extruded volumes, setback zones, height caps. |

### 3. Programming

| Skill | Description |
|-------|-------------|
| [`/workplace-programmer`](./plugins/03-programming/skills/workplace-programmer) | AI workplace strategy consultant — area splits, room schedules, seat counts from workplace research benchmarks. |
| [`/occupancy-calculator`](./plugins/03-programming/skills/occupancy-calculator) | IBC occupancy load calculator — per-area loads from Table 1004.5, egress requirements, use group classification. |

### 4. Specifications

| Skill | Description |
|-------|-------------|
| [`/spec-writer`](./plugins/04-specifications/skills/spec-writer) | CSI outline specs from a materials list — MasterFormat divisions, three-part sections, performance criteria. |

### 5. Sustainability

| Skill | Description |
|-------|-------------|
| [`/epd-parser`](./plugins/05-sustainability/skills/epd-parser) | Extract structured data from EPD PDFs — GWP, life cycle stages, certifications, LEED eligibility. |
| [`/epd-research`](./plugins/05-sustainability/skills/epd-research) | Search EC3, UL, Environdec, and manufacturer sites for EPDs by material or product category. |
| [`/epd-compare`](./plugins/05-sustainability/skills/epd-compare) | Side-by-side environmental impact comparison with LEED v4.1 MRc2 eligibility check. |
| [`/epd-to-spec`](./plugins/05-sustainability/skills/epd-to-spec) | CSI specification sections requiring EPDs and setting maximum GWP thresholds. |

### 6. Product & Materials Research

| Skill | Description |
|-------|-------------|
| [`/product-research`](./plugins/06-materials-research/skills/product-research) | Brief-based product research — describe what you need, Claude searches and returns curated candidates. |
| [`/product-spec-bulk-fetch`](./plugins/06-materials-research/skills/product-spec-bulk-fetch) | Extract FF&E specs from product URLs at scale — names, dimensions, materials, pricing, images. |
| [`/product-spec-bulk-cleanup`](./plugins/06-materials-research/skills/product-spec-bulk-cleanup) | Normalize messy FF&E schedules — casing, dimensions, materials, categories, deduplication. |
| [`/product-spec-pdf-parser`](./plugins/06-materials-research/skills/product-spec-pdf-parser) | Extract FF&E specs from PDFs — price books, fact sheets, spec sheets into standardized schedules. |
| [`/product-image-processor`](./plugins/06-materials-research/skills/product-image-processor) | Batch download, resize, and remove backgrounds from product images. |
| [`/ffe-schedule`](./plugins/06-materials-research/skills/ffe-schedule) | Turn raw product lists into formatted FF&E specification schedules. |
| [`/product-enrich`](./plugins/06-materials-research/skills/product-enrich) | Auto-tag products with categories, colors, materials, and style tags. |
| [`/product-match`](./plugins/06-materials-research/skills/product-match) | Find similar products from an image, name, or description. |
| [`/product-pair`](./plugins/06-materials-research/skills/product-pair) | Suggest complementary products that pair well with a given item. |
| [`/csv-to-sif`](./plugins/06-materials-research/skills/csv-to-sif) | Convert CSV product lists to SIF format for dealer systems. |
| [`/sif-to-csv`](./plugins/06-materials-research/skills/sif-to-csv) | Convert SIF files from dealers into readable spreadsheets. |

### 7. Presentations

| Skill | Description |
|-------|-------------|
| [`/slide-deck-generator`](./plugins/07-presentations/skills/slide-deck-generator) | Self-contained HTML slide decks — Helvetica, editorial layout, 22 slide types, keyboard/touch navigation. |
| [`/color-palette-generator`](./plugins/07-presentations/skills/color-palette-generator) | Color palettes from descriptions, images, or hex codes — swatches, WCAG contrast, example pairings. |

## Agents

Agents are autonomous specialists that orchestrate multiple skills. They assess your input, choose a path, and exercise judgment — unlike skills (single-purpose) or commands (fixed pipelines).

| Agent | Domain | What it does |
|-------|--------|-------------|
| [site-planner](./agents/site-planner.md) | Site Planning | Runs all site research in parallel, synthesizes a unified site brief with opportunities and constraints |
| [nyc-zoning-expert](./agents/nyc-zoning-expert.md) | Due Diligence + Zoning | Full NYC property and zoning analysis — due diligence, buildable envelope, 3D visualization |
| [workplace-strategist](./agents/workplace-strategist.md) | Programming | Translates headcount and work style into space programs — occupancy compliance, zone allocation, room schedules |
| [product-and-materials-researcher](./agents/product-and-materials-researcher.md) | Materials Research | Finds products from a brief, extracts specs from URLs/PDFs, tags and classifies, finds alternatives |
| [ffe-designer](./agents/ffe-designer.md) | FF&E Design | Builds clean schedules from messy inputs, composes room packages, runs QA, exports to dealer formats |
| [sustainability-specialist](./agents/sustainability-specialist.md) | Sustainability | Evaluates environmental impact — finds EPDs, compares GWP, checks LEED eligibility, writes spec thresholds |
| [brand-manager](./agents/brand-manager.md) | Presentations | Owns visual identity — builds decks, creates palettes, QAs deliverables for presentation readiness |

See the [agents directory](./agents) for full workflows and judgment rules.

## Rules

Rules are always-on conventions that apply across all plugins — units, code citations, terminology, and formatting. They're loaded automatically, not invoked.

| Rule | What it governs |
|------|-----------------|
| [units-and-measurements](./rules/units-and-measurements.md) | Imperial/metric, area types (GSF/USF/RSF), dimensions |
| [code-citations](./rules/code-citations.md) | Building code references, edition years, jurisdiction awareness |
| [professional-disclaimer](./rules/professional-disclaimer.md) | Disclaimer language, what AI outputs can and cannot claim |
| [csi-formatting](./rules/csi-formatting.md) | MasterFormat 2018 section numbers, three-part structure |
| [terminology](./rules/terminology.md) | AEC standard terms, abbreviations, material names |
| [output-formatting](./rules/output-formatting.md) | Tables, source attribution, file naming, list structure |

See the [rules directory](./rules) for full details.

## Hooks

Hooks are event-driven automations that fire during Claude Code sessions — after a file is written, before a commit. They're opt-in: copy the config into your Claude Code settings to activate.

| Hook | Event | What it does |
|------|-------|-------------|
| [post-write-disclaimer-check](./hooks/post-write-disclaimer-check.sh) | After Write | Warns if regulatory output is missing the professional disclaimer |
| [post-output-metadata](./hooks/post-output-metadata.sh) | After Write | Stamps markdown reports with YAML front matter (title, date, skill) |
| [pre-commit-spec-lint](./hooks/pre-commit-spec-lint.sh) | Before git commit | Flags malformed CSI section numbers in staged files |

See the [hooks directory](./hooks) for installation instructions.

## Contributing

Want to add a skill for the built environment? Here's how:

1. **Copy (fork)** this repository on GitHub
2. Create your skill in the appropriate plugin folder (or propose a new plugin)
3. Each skill needs:
   - A `SKILL.md` with clear instructions and domain knowledge
   - A `README.md` with install, usage, and sample output
   - Any supporting data files in a `data/` or `zoning-rules/` directory
4. Open a **pull request** (GitHub's way of proposing changes for review) — describe what the skill does, how you tested it, and sample output

For guidance on organizing skills across a team, read [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams).

## License

MIT — see [LICENSE](LICENSE).

---

Built by [ALPA](https://alpa.llc) — research, strategy, and technology for the built environment.

**Read more:** [Claude Code Cheat Sheet for Architects](https://alpa.llc/articles/claude-code-cheat-sheet) · [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams)
