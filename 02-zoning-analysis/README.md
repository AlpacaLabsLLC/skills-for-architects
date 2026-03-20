# Zoning Analysis

A Claude Code plugin for zoning envelope analysis. Give it an address or lot identifier and it calculates the buildable envelope — FAR, height limits, setbacks, yards, permitted uses, parking requirements, and available bonuses — using live PLUTO data and the NYC Zoning Resolution.

## The Problem

Zoning analysis is one of the most time-consuming and error-prone tasks in early-stage design. The NYC Zoning Resolution alone is thousands of pages, with contextual districts, overlays, special districts, and recent City of Yes reforms that interact in complex ways. Getting it wrong means redesign, delays, or BSA applications.

## The Solution

A skill that queries the city's PLUTO dataset for lot-specific data, identifies the applicable zoning district(s), loads the relevant rules, and produces a structured analysis. It handles split zones, contextual suffixes, overlays, and special districts — and always includes caveats about what requires professional verification.

```
                    ┌──────────────────────┐
                    │  Address, BBL, or BIN│
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    PLUTO Query       │
                    │    (Socrata API)     │
                    │                      │
                    │  Lot area, zoning,   │
                    │  FAR, building class,│
                    │  overlays, landmarks │
                    └──────────┬───────────┘
                               │
                    ┌──────────┴───────────┐
                    │                      │
                    ▼                      ▼
          ┌─────────────────┐   ┌─────────────────┐
          │ Zoning District │   │ Overlays &      │
          │ Rules           │   │ Special Dists.  │
          │                 │   │                 │
          │ R/C/M prefix    │   │ Mapped overlays │
          │ Contextual      │   │ Special purpose │
          │ suffixes        │   │ districts       │
          │ (A/B/D/X)       │   │ City of Yes     │
          └────────┬────────┘   └────────┬────────┘
                   │                     │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │   Zoning Analysis    │
                   │                      │
                   │ • Floor area (FAR)   │
                   │ • Height & setback   │
                   │ • Yards & coverage   │
                   │ • Permitted uses     │
                   │ • Parking reqs       │
                   │ • Bonuses            │
                   │ • Restrictions       │
                   │ • Development        │
                   │   potential          │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  Markdown Report     │
                   │  with caveats        │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │  /zoning-envelope    │
                   │                      │
                   │  Interactive 3D      │
                   │  HTML viewer         │
                   │  (Three.js)          │
                   └──────────────────────┘
```

## Data Flow

### Input

One of:
- **Address + Borough/Zip** — "123 Main St, Brooklyn 11201"
- **BBL** — 10-digit Borough-Block-Lot number
- **BIN** — Building Identification Number

### Data sources

| Source | What it provides |
|--------|-----------------|
| [NYC PLUTO](https://data.cityofnewyork.us/resource/64uk-42ks.json) (Socrata API) | Lot area, zoning district, FAR, building class, overlays, landmark status |
| Bundled zoning rules (`zoning-rules/*.md`) | Residential, commercial, manufacturing district rules, contextual districts, special districts, use groups, parking, City of Yes reforms |

### Output

A structured markdown report with:
- Lot Summary (from PLUTO)
- Zoning Classification (district type, contextual suffix)
- Bulk Parameters (floor area, height & setback, yards & coverage)
- Permitted Uses (by use group)
- Parking Requirements
- Bonuses & Incentives
- Restrictions
- Development Potential (max buildable SF)
- Envelope Data (machine-readable JSON for `/zoning-envelope`)
- Caveats (mandatory warnings about professional verification)

Optionally, run `/zoning-envelope` on the report to generate an interactive 3D viewer — a self-contained HTML file with the exact lot polygon, extruded buildable volumes, setback zones, and height caps.

## Skills

| Skill | Description |
|-------|-------------|
| [zoning-analysis-nyc](skills/zoning-analysis-nyc/) | Buildable envelope analysis for NYC lots — FAR, height, setbacks, use groups from PLUTO and the Zoning Resolution |
| [zoning-envelope](skills/zoning-envelope/) | Interactive 3D envelope viewer — generates a self-contained HTML file from any zoning analysis report |

## Install

```bash
claude install github:AlpacaLabsLLC/skills-for-architects/02-zoning-analysis
```

## License

MIT
