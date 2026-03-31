# Agents

Agents are autonomous specialists that orchestrate multiple skills to complete a complex task. Unlike skills (single-purpose, invoked directly), agents assess the situation, choose a path, and exercise judgment.

## Available Agents

| Agent | Domain | Skills it orchestrates |
|-------|--------|----------------------|
| [site-planner](./site-planner.md) | Site Planning | environmental-analysis, mobility-analysis, demographics-analysis, history |
| [nyc-zoning-expert](./nyc-zoning-expert.md) | Due Diligence + Zoning | nyc-landmarks, nyc-dob-permits, nyc-dob-violations, nyc-acris, nyc-hpd, nyc-bsa, nyc-property-report, zoning-analysis-nyc, zoning-envelope |
| [workplace-strategist](./workplace-strategist.md) | Programming | occupancy-calculator, workplace-programmer |
| [product-and-materials-researcher](./product-and-materials-researcher.md) | Materials Research | product-research, product-spec-bulk-fetch, product-spec-pdf-parser, product-match, product-enrich |
| [ffe-designer](./ffe-designer.md) | FF&E Design | product-pair, product-spec-bulk-cleanup, ffe-schedule, product-image-processor, csv-to-sif, sif-to-csv |
| [sustainability-specialist](./sustainability-specialist.md) | Sustainability | epd-research, epd-compare, epd-parser, epd-to-spec |
| [brand-manager](./brand-manager.md) | Presentations | slide-deck-generator, color-palette-generator |

## How Agents Differ from Skills

| Layer | Behavior | Example |
|-------|----------|---------|
| **Skill** | Does one thing when invoked | `/product-research` searches the web for products |
| **Agent** | Assesses the input, chooses a path, orchestrates skills, exercises judgment | The researcher decides whether to search, extract from PDFs, or find alternatives based on what you give it |

## How They Work Together

```
Address or site
      ↓
Site Planner
      → climate, transit, demographics, neighborhood context
      ↓
NYC Zoning Expert
      → property records, zoning envelope, 3D visualization
      ↓
Workplace Strategist
      → occupancy compliance, zone allocation, room schedule
      ↓
Product & Materials Researcher
      → finds products, extracts specs, tags and classifies
      ↓
Sustainability Specialist
      → evaluates environmental impact, compares GWP, checks LEED
      ↓
FF&E Designer
      → composes room packages, builds schedule, runs QA, exports
      ↓
Brand Manager
      → builds the presentation, ensures visual consistency
```

Each agent works standalone. Use one, several, or all depending on the task.

## Usage

Agents are reference documents — they define how Claude should behave when delegating complex work. To invoke an agent's behavior, describe your task and Claude will follow the agent's workflow.
