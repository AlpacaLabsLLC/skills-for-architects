# Architecture Studio

> Agents, skills, and rules for architects, designers, and AEC professionals — use with [Claude Desktop](https://claude.ai) or [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Architecture Studio** teaches Claude architecture-specific workflows — site analysis, zoning, space programming, specifications, materials research, sustainability, and presentations.

**7 agents**, **36 skills**, **7 rules**, and **3 hooks** across **9 plugins**. Built by [ALPA](https://alpa.llc).

## Architecture

```
Architecture Studio
├── /studio                              ← entry point
│
├── agents/
│   ├── site-planner                     4 skills · site research + synthesis
│   ├── nyc-zoning-expert                9 skills · property records + zoning + 3D
│   ├── workplace-strategist             2 skills · occupancy + programming
│   ├── product-and-materials-researcher 5 skills · find, extract, tag
│   ├── ffe-designer                     6 skills · schedule, QA, export
│   ├── sustainability-specialist        4 skills · EPDs, GWP, LEED
│   └── brand-manager                    2 skills · decks + palettes
│
├── plugins/
│   ├── 00-due-diligence                 7 skills
│   ├── 01-site-planning                 4 skills
│   ├── 02-zoning-analysis               3 skills
│   ├── 03-programming                   2 skills
│   ├── 04-specifications                1 skill
│   ├── 05-sustainability                4 skills
│   ├── 06-materials-research           11 skills
│   ├── 07-presentations                 2 skills
│   └── 08-dispatcher                    2 skills
│
├── rules/
│   ├── units-and-measurements
│   ├── code-citations
│   ├── professional-disclaimer
│   ├── csi-formatting
│   ├── terminology
│   └── output-formatting
│
└── hooks/
    ├── post-write-disclaimer-check
    ├── post-output-metadata
    └── pre-commit-spec-lint
```

**Agents** orchestrate skills across plugins — they assess your input, choose a path, and exercise judgment. **Skills** are single-purpose tools invoked with a slash command. **Rules** govern every output. **Hooks** are event-driven automations. Skills are grouped into **plugins** (installable bundles organized by project lifecycle).

## Quick Start

### Install

**Claude Desktop:** Open **Customize** → **Browse plugins** → **+** → **Add marketplace from GitHub** → enter `AlpacaLabsLLC/skills-for-architects`

**Claude Code:**
```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 01-site-planning@skills-for-architects
```

### Use

Type `/studio` followed by what you need. The router reads your request and hands off to the right agent or skill.

```
/studio task chair, mesh back, under $800
/studio 123 Main St, Brooklyn NY
/studio I need a space program for 200 people
/studio parse this EPD
```

Type `/skills` for the full menu. Or call any skill directly by name (e.g. `/environmental-analysis 123 Main St`).

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

See the [agents directory](./agents) for full workflows and handoff logic.

## Plugins & Skills

Organized by project lifecycle — from due diligence through delivery.

| # | Plugin | Skills | Description |
|---|--------|--------|-------------|
| 0 | [Due Diligence](./plugins/00-due-diligence) | 7 | NYC property data: landmarks, DOB permits, violations, ACRIS, HPD, BSA. |
| 1 | [Site Planning](./plugins/01-site-planning) | 4 | Site research: environmental, mobility, demographics, history. |
| 2 | [Zoning Analysis](./plugins/02-zoning-analysis) | 3 | Zoning envelope analysis and 3D visualization for NYC and Uruguay. |
| 3 | [Programming](./plugins/03-programming) | 2 | Workplace strategy: space programs, occupancy loads, IBC compliance. |
| 4 | [Specifications](./plugins/04-specifications) | 1 | CSI outline specifications from a materials list. |
| 5 | [Sustainability](./plugins/05-sustainability) | 4 | EPD parsing, research, comparison, and GWP thresholds. |
| 6 | [Materials Research](./plugins/06-materials-research) | 11 | FF&E product research, spec extraction, cleanup, and image processing. |
| 7 | [Presentations](./plugins/07-presentations) | 2 | Slide deck generation and color palette creation. |
| 8 | [Dispatcher](./plugins/08-dispatcher) | 2 | Studio router (`/studio`) and help menu (`/skills`). |

<details>
<summary><strong>All 36 skills</strong></summary>

### Due Diligence

| Skill | Description |
|-------|-------------|
| [`/nyc-landmarks`](./plugins/00-due-diligence/skills/nyc-landmarks) | LPC landmark and historic district check |
| [`/nyc-dob-permits`](./plugins/00-due-diligence/skills/nyc-dob-permits) | DOB permit and filing history |
| [`/nyc-dob-violations`](./plugins/00-due-diligence/skills/nyc-dob-violations) | DOB and ECB violations |
| [`/nyc-acris`](./plugins/00-due-diligence/skills/nyc-acris) | ACRIS property transaction records |
| [`/nyc-hpd`](./plugins/00-due-diligence/skills/nyc-hpd) | HPD violations, complaints, and registration |
| [`/nyc-bsa`](./plugins/00-due-diligence/skills/nyc-bsa) | BSA variances and special permits |
| [`/nyc-property-report`](./plugins/00-due-diligence/skills/nyc-property-report) | Combined NYC property report — all 6 above |

### Site Planning

| Skill | Description |
|-------|-------------|
| [`/environmental-analysis`](./plugins/01-site-planning/skills/environmental-analysis) | Climate, precipitation, wind, sun angles, flood zones, seismic risk, soil |
| [`/mobility-analysis`](./plugins/01-site-planning/skills/mobility-analysis) | Transit, walk/bike/transit scores, pedestrian infrastructure |
| [`/demographics-analysis`](./plugins/01-site-planning/skills/demographics-analysis) | Population, income, age, housing market, employment |
| [`/history`](./plugins/01-site-planning/skills/history) | Neighborhood context, landmarks, commercial activity, planned development |

### Zoning Analysis

| Skill | Description |
|-------|-------------|
| [`/zoning-analysis-nyc`](./plugins/02-zoning-analysis/skills/zoning-analysis-nyc) | NYC buildable envelope — FAR, height, setbacks, use groups from PLUTO |
| [`/zoning-analysis-uruguay`](./plugins/02-zoning-analysis/skills/zoning-analysis-uruguay) | Maldonado, Uruguay — FOS, FOT, height, setbacks from TONE |
| [`/zoning-envelope`](./plugins/02-zoning-analysis/skills/zoning-envelope) | Interactive 3D zoning envelope viewer |

### Programming

| Skill | Description |
|-------|-------------|
| [`/workplace-programmer`](./plugins/03-programming/skills/workplace-programmer) | Space programs from headcount and work style |
| [`/occupancy-calculator`](./plugins/03-programming/skills/occupancy-calculator) | IBC occupancy loads, egress, plumbing fixture counts |

### Specifications

| Skill | Description |
|-------|-------------|
| [`/spec-writer`](./plugins/04-specifications/skills/spec-writer) | CSI outline specs — MasterFormat divisions, three-part sections |

### Sustainability

| Skill | Description |
|-------|-------------|
| [`/epd-parser`](./plugins/05-sustainability/skills/epd-parser) | Extract data from EPD PDFs — GWP, life cycle stages, certifications |
| [`/epd-research`](./plugins/05-sustainability/skills/epd-research) | Search EC3, UL, Environdec for EPDs by material or category |
| [`/epd-compare`](./plugins/05-sustainability/skills/epd-compare) | Side-by-side environmental impact comparison |
| [`/epd-to-spec`](./plugins/05-sustainability/skills/epd-to-spec) | CSI specs with EPD requirements and GWP thresholds |

### Materials Research

| Skill | Description |
|-------|-------------|
| [`/product-research`](./plugins/06-materials-research/skills/product-research) | Find products from a design brief |
| [`/product-spec-bulk-fetch`](./plugins/06-materials-research/skills/product-spec-bulk-fetch) | Extract specs from product URLs at scale |
| [`/product-spec-bulk-cleanup`](./plugins/06-materials-research/skills/product-spec-bulk-cleanup) | Normalize messy FF&E schedules |
| [`/product-spec-pdf-parser`](./plugins/06-materials-research/skills/product-spec-pdf-parser) | Extract specs from PDF catalogs |
| [`/product-image-processor`](./plugins/06-materials-research/skills/product-image-processor) | Batch download, resize, remove backgrounds |
| [`/ffe-schedule`](./plugins/06-materials-research/skills/ffe-schedule) | Format raw product data into a schedule |
| [`/product-enrich`](./plugins/06-materials-research/skills/product-enrich) | Auto-tag products with categories, colors, materials |
| [`/product-match`](./plugins/06-materials-research/skills/product-match) | Find similar products |
| [`/product-pair`](./plugins/06-materials-research/skills/product-pair) | Suggest complementary products |
| [`/csv-to-sif`](./plugins/06-materials-research/skills/csv-to-sif) | Convert CSV to SIF for dealer systems |
| [`/sif-to-csv`](./plugins/06-materials-research/skills/sif-to-csv) | Convert SIF to readable spreadsheets |

### Presentations

| Skill | Description |
|-------|-------------|
| [`/slide-deck-generator`](./plugins/07-presentations/skills/slide-deck-generator) | HTML slide decks — editorial layout, 22 slide types |
| [`/color-palette-generator`](./plugins/07-presentations/skills/color-palette-generator) | Color palettes from descriptions, images, or hex codes |

</details>

## Rules

Always-on conventions that govern every output — loaded automatically, not invoked.

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

Event-driven automations — opt-in via Claude Code settings.

| Hook | Event | What it does |
|------|-------|-------------|
| [post-write-disclaimer-check](./hooks/post-write-disclaimer-check.sh) | After Write | Warns if regulatory output is missing the professional disclaimer |
| [post-output-metadata](./hooks/post-output-metadata.sh) | After Write | Stamps markdown reports with YAML front matter |
| [pre-commit-spec-lint](./hooks/pre-commit-spec-lint.sh) | Before git commit | Flags malformed CSI section numbers |

See the [hooks directory](./hooks) for installation instructions.

## Contributing

Want to add a skill for the built environment?

1. **Fork** this repository
2. Create your skill in the appropriate plugin folder (or propose a new plugin)
3. Each skill needs a `SKILL.md` with instructions and domain knowledge, a `README.md`, and any supporting data files
4. Open a **pull request** — describe what the skill does, how you tested it, and sample output

For guidance on organizing skills across a team, read [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams).

## License

MIT — see [LICENSE](LICENSE).

---

Built by [ALPA](https://alpa.llc) — research, strategy, and technology for the built environment.

**Read more:** [Claude Code Cheat Sheet for Architects](https://alpa.llc/articles/claude-code-cheat-sheet) · [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams)
