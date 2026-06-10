# Agents

Agents are autonomous specialists that orchestrate multiple skills to complete a complex task. Unlike skills (single-purpose, invoked directly), agents assess the situation, choose a path, and exercise judgment.

Each agent ships **inside the plugin it orchestrates** (under that plugin's `agents/` directory), so installing a plugin registers its agent as a native Claude Code subagent — Claude can delegate to it automatically, and `/studio` routes to it by name.

## Available Agents

| Agent | Plugin | Domain | Skills it orchestrates |
|-------|--------|--------|----------------------|
| [site-planner](../plugins/01-site-planning/agents/site-planner.md) | 01-site-planning | Site Planning | environmental-analysis, mobility-analysis, demographics-analysis, history |
| [nyc-zoning-expert](../plugins/02-zoning-analysis/agents/nyc-zoning-expert.md) | 02-zoning-analysis | Due Diligence + Zoning | nyc-landmarks, nyc-dob-permits, nyc-dob-violations, nyc-acris, nyc-hpd, nyc-bsa, nyc-property-report, zoning-analysis-nyc, zoning-envelope |
| [workplace-strategist](../plugins/03-programming/agents/workplace-strategist.md) | 03-programming | Programming | occupancy-calculator, workplace-programmer |
| [sustainability-specialist](../plugins/05-sustainability/agents/sustainability-specialist.md) | 05-sustainability | Sustainability | epd-research, epd-compare, epd-parser, epd-to-spec |
| [product-and-materials-researcher](../plugins/06-materials-research/agents/product-and-materials-researcher.md) | 06-materials-research | Materials Research | product-research, product-spec-bulk-fetch, product-spec-pdf-parser, product-match, product-enrich |
| [ffe-designer](../plugins/06-materials-research/agents/ffe-designer.md) | 06-materials-research | FF&E Design | product-pair, product-data-cleanup, product-data-import, product-enrich, product-image-processor, csv-to-sif, sif-to-csv |
| [brand-manager](../plugins/07-presentations/agents/brand-manager.md) | 07-presentations | Presentations | slide-deck-generator, color-palette-generator, resize-images |

## How Agents Differ from Skills

| Layer | Behavior | Example |
|-------|----------|---------|
| **Skill** | Does one thing when invoked | `/product-research` searches the web for products |
| **Agent** | Assesses the input, chooses a path, orchestrates skills, exercises judgment | The researcher decides whether to search, extract from PDFs, or find alternatives based on what you give it |

Use an **agent** when the task is open-ended and multi-step (the agent decides which skills to run and in what order). Call a **skill** directly when you know exactly which single operation you need.

## How They Work Together

```
Address or site
      ↓
site-planner
      → climate, transit, demographics, neighborhood context
      ↓
nyc-zoning-expert
      → property records, zoning envelope, 3D visualization
      ↓
workplace-strategist
      → occupancy compliance, zone allocation, room schedule
      ↓
product-and-materials-researcher
      → finds products, extracts specs, tags and classifies
      ↓
sustainability-specialist
      → evaluates environmental impact, compares GWP, checks LEED
      ↓
ffe-designer
      → composes room packages, builds schedule, runs QA, exports
      ↓
brand-manager
      → builds the presentation, ensures visual consistency
```

Each agent works standalone. Use one, several, or all depending on the task.

## Usage

Three ways in:

1. **Automatic delegation** — with the plugin installed, Claude Code registers the agent and can delegate matching work to it on its own (the agent's `description` frontmatter drives this).
2. **`/studio` routing** — describe your task; the dispatcher classifies it and hands off to the right agent.
3. **Direct** — name the agent in your request ("have the ffe-designer clean this schedule up").
