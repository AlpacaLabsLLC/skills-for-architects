# Skills for Architects

> Skills and plugins for [Claude](https://claude.ai) — use with Claude Desktop or [Claude Code](https://docs.anthropic.com/en/docs/claude-code). From site research to zoning, programming, specifications, and creative delivery.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Claude is an AI assistant made by Anthropic. These skills teach it architecture-specific workflows — site analysis, space programming, specifications, and more.

**16 skills** across **6 plugins** for architects, designers, and AEC professionals.

## Prerequisites

- **Claude Desktop** (recommended) or **Claude Code CLI**
- A [Claude subscription](https://claude.ai) (Pro, Max, Team, or Enterprise)

## What Are Skills and Plugins?

- **Skills** teach Claude about a design topic — like calculating occupancy loads, analyzing zoning envelopes, or writing CSI specs. You invoke them with a slash command (e.g. `/environmental-analysis`).
- **Plugins** group related skills together. Some plugins include a skill that runs the others in sequence — for example, `/site-due-diligence-nyc` runs all four site planning skills plus zoning in one go.

## Quick Start

### Option A: Claude Desktop — recommended

1. Open **Customize** → **Browse plugins** → click **+** → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the plugins you want from the **Personal** tab
4. Type `/skills` in any conversation to verify

Updates sync through the marketplace automatically.

### Option B: Claude Code (CLI)

```bash
# Install a single plugin
claude install github:AlpacaLabsLLC/skills-for-architects/01-site-planning

# Or install all plugins
claude install github:AlpacaLabsLLC/skills-for-architects
```

Skills stay in sync automatically when the source is updated.

## Where to Start

Pick your task, run the skill:

| I need to... | Run this | Plugin |
|--------------|----------|--------|
| Research a new site | `/environmental-analysis 123 Main St` | Site Planning |
| Understand neighborhood context | `/history 123 Main St` | Site Planning |
| Check NYC zoning | `/zoning-analysis-nyc 123 Main St` | Zoning Analysis |
| Build a space program | `/workplace-programmer` | Programming |
| Calculate occupancy loads | `/occupancy-calculator` | Programming |
| Write CSI specs | `/spec-writer` | Specifications |
| Find FF&E products | `/product-research` | Materials Research |
| Generate a slide deck | `/slide-deck-generator Q1 results` | Presentations |
| Full NYC site due diligence | `/site-due-diligence-nyc 123 Main St` | Site Planning |

## Plugins

Organized by project lifecycle — from site research through delivery.

| # | Plugin | Skills | Description |
|---|--------|--------|-------------|
| 1 | [01-site-planning](./01-site-planning) | 4 | Site research: environmental, mobility, demographics, history. |
| 2 | [02-zoning-analysis](./02-zoning-analysis) | 1 | Buildable envelope analysis from zoning regulations and public data APIs. |
| 3 | [03-programming](./03-programming) | 2 | Workplace strategy: space programs, occupancy loads, IBC compliance. |
| 4 | [04-specifications](./04-specifications) | 2 | CSI outline specs and construction punch lists. |
| 5 | [05-materials-research](./05-materials-research) | 5 | FF&E product research, spec extraction, cleanup, and image processing. |
| 6 | [06-presentations](./06-presentations) | 2 | Slide deck generation and color palette creation. |

## All Skills

### 1. Site Planning

| Skill | Description |
|-------|-------------|
| [`/environmental-analysis`](./01-site-planning/skills/environmental-analysis) | Climate and environmental site analysis — temperature, precipitation, wind, sun angles, flood zones, seismic risk, soil, topography. |
| [`/mobility-analysis`](./01-site-planning/skills/mobility-analysis) | Transit and mobility site analysis — subway, bus, bike, pedestrian infrastructure, walk scores, airport access. |
| [`/demographics-analysis`](./01-site-planning/skills/demographics-analysis) | Demographics and market site analysis — population, income, age, housing market, employment. |
| [`/history`](./01-site-planning/skills/history) | Neighborhood context and history — adjacent uses, architectural character, landmarks, commercial activity, planned development. |


### 2. Zoning Analysis

| Skill | Description |
|-------|-------------|
| [`/zoning-analysis-nyc`](./02-zoning-analysis/skills/zoning-analysis-nyc) | Buildable envelope analysis for lots in New York City — FAR, height, setbacks, use groups from PLUTO data and the Zoning Resolution. |

### 3. Programming

| Skill | Description |
|-------|-------------|
| [`/workplace-programmer`](./03-programming/skills/workplace-programmer) | AI workplace strategy consultant — area splits, room schedules, seat counts from workplace research benchmarks. |
| [`/occupancy-calculator`](./03-programming/skills/occupancy-calculator) | IBC occupancy load calculator — per-area loads from Table 1004.5, egress requirements, use group classification. |

### 4. Specifications

| Skill | Description |
|-------|-------------|
| [`/spec-writer`](./04-specifications/skills/spec-writer) | CSI outline specs from a materials list — MasterFormat divisions, three-part sections, performance criteria. |
| [`/redline-punch-list`](./04-specifications/skills/redline-punch-list) | Field notes to structured punch lists — CSI divisions, trade assignments, priority levels. |

### 5. Product & Materials Research

| Skill | Description |
|-------|-------------|
| [`/product-research`](./05-materials-research/skills/product-research) | Brief-based product research — describe what you need, Claude searches and returns curated candidates. |
| [`/product-spec-bulk-fetch`](./05-materials-research/skills/product-spec-bulk-fetch) | Extract FF&E specs from product URLs at scale — names, dimensions, materials, pricing, images. |
| [`/product-spec-bulk-cleanup`](./05-materials-research/skills/product-spec-bulk-cleanup) | Normalize messy FF&E schedules — casing, dimensions, materials, categories, deduplication. |
| [`/product-spec-pdf-parser`](./05-materials-research/skills/product-spec-pdf-parser) | Extract FF&E specs from PDFs — price books, fact sheets, spec sheets into standardized schedules. |
| [`/product-image-processor`](./05-materials-research/skills/product-image-processor) | Batch download, resize, and remove backgrounds from product images. |

### 6. Presentations

| Skill | Description |
|-------|-------------|
| [`/slide-deck-generator`](./06-presentations/skills/slide-deck-generator) | Self-contained HTML slide decks — Helvetica, editorial layout, 22 slide types, keyboard/touch navigation. |
| [`/color-palette-generator`](./06-presentations/skills/color-palette-generator) | Color palettes from descriptions, images, or hex codes — swatches, WCAG contrast, example pairings. |

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
