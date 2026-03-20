# Zoning Analysis

A Claude Code plugin for NYC site intelligence — zoning envelope analysis and property data lookup. Give it an address or lot identifier and it calculates the buildable envelope (FAR, height limits, setbacks, yards, permitted uses, parking requirements, bonuses) using live PLUTO data and the NYC Zoning Resolution, and pulls building records (landmarks, DOB permits, violations, ACRIS ownership, HPD, BSA variances) from NYC Open Data.

## The Problem

Zoning analysis is one of the most time-consuming and error-prone tasks in early-stage design. The NYC Zoning Resolution alone is thousands of pages, with contextual districts, overlays, special districts, and recent City of Yes reforms that interact in complex ways. Getting it wrong means redesign, delays, or BSA applications.

Beyond zoning, site due diligence requires checking landmark status, active DOB violations, permit history, ownership records (ACRIS), HPD complaints, and BSA variances — each from a different city database with different query formats.

## The Solution

A set of skills that query the city's open data APIs for lot-specific data, identify applicable rules and records, and produce structured reports. The zoning skill handles split zones, contextual suffixes, overlays, and special districts. The property report skill queries 7 data domains across NYC Open Data. Both always include caveats about what requires professional verification.

```
                    ┌──────────────────────┐
                    │  Address, BBL, or BIN│
                    └──────────┬───────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  Geoclient   │ │  PLUTO       │ │  NYC Open    │
     │  API         │ │  (Socrata)   │ │  Data APIs   │
     │              │ │              │ │              │
     │  BBL, BIN,   │ │  Lot area,   │ │  Landmarks,  │
     │  geo coords  │ │  zoning, FAR │ │  permits,    │
     └──────┬───────┘ └──────┬───────┘ │  violations, │
            │                │         │  ACRIS, HPD, │
            │                │         │  BSA         │
            │                │         └──────┬───────┘
            │                │                │
     ┌──────┴────────────────┴───┐    ┌──────┴───────┐
     │                           │    │              │
     ▼                           ▼    ▼              │
  ┌─────────────────┐  ┌──────────────────┐         │
  │ Zoning District │  │ Property Report  │         │
  │ Rules           │  │                  │         │
  │                 │  │ • Landmarks      │         │
  │ R/C/M prefix    │  │ • DOB permits    │         │
  │ Contextual      │  │ • Violations     │         │
  │ suffixes        │  │ • ACRIS records  │         │
  │ Overlays        │  │ • HPD            │         │
  │ Special dists   │  │ • BSA variances  │         │
  └────────┬────────┘  └────────┬─────────┘         │
           │                    │                    │
           ▼                    ▼                    │
  ┌─────────────────┐  ┌──────────────────┐         │
  │ Zoning Analysis │  │ Property Report  │         │
  │                 │  │                  │         │
  │ • Floor area    │  │ property-{slug}  │         │
  │ • Height/setback│  │ .md              │         │
  │ • Yards/coverage│  └──────────────────┘         │
  │ • Permitted uses│                               │
  │ • Parking reqs  │                               │
  │ • Bonuses       │                               │
  │ • Dev potential │                               │
  └────────┬────────┘                               │
           │                                        │
           ▼                                        │
  ┌──────────────────┐                              │
  │ /zoning-envelope │                              │
  │                  │                              │
  │ Interactive 3D   │                              │
  │ HTML viewer      │                              │
  │ (Three.js)       │                              │
  └──────────────────┘                              │
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
| [NYC Geoclient](https://api.nyc.gov/geo/geoclient/v2/) | BBL/BIN resolution, geographic identifiers, coordinates |
| [NYC Open Data](https://data.cityofnewyork.us) (Socrata APIs) | LPC landmarks, DOB permits & violations, ACRIS property records, HPD violations & registration, BSA applications |
| Bundled zoning rules (`zoning-rules/*.md`) | Residential, commercial, manufacturing district rules, contextual districts, special districts, use groups, parking, City of Yes reforms |

### Output

**Zoning analysis** — a structured markdown report with:
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

**Property report** — a structured markdown report with:
- Property Identification (BBL, BIN, geographic IDs)
- Landmark Status (LPC designation, historic districts)
- DOB Permits & Filings (legacy + DOB NOW)
- DOB & ECB Violations (with open violations flagged)
- ACRIS Property Records (deeds, mortgages, ownership chain)
- HPD Violations & Registration (residential buildings)
- BSA Variances & Special Permits

Optionally, run `/zoning-envelope` on the zoning report to generate an interactive 3D viewer — a self-contained HTML file with the exact lot polygon, extruded buildable volumes, setback zones, and height caps.

## Skills

| Skill | Description |
|-------|-------------|
| [zoning-analysis-nyc](skills/zoning-analysis-nyc/) | Buildable envelope analysis for NYC lots — FAR, height, setbacks, use groups from PLUTO and the Zoning Resolution |
| [nyc-property-report](skills/nyc-property-report/) | NYC property data — landmarks, DOB permits, violations, ACRIS records, HPD, and BSA variances from NYC Open Data APIs |
| [zoning-envelope](skills/zoning-envelope/) | Interactive 3D envelope viewer — generates a self-contained HTML file from any zoning analysis report |

## Commands

| Command | Description |
|---------|-------------|
| [nyc-due-diligence](commands/nyc-due-diligence.md) | Full NYC site due diligence — runs zoning analysis + property report + 3D envelope viewer in sequence |

## Install

```bash
claude install github:AlpacaLabsLLC/skills-for-architects/02-zoning-analysis
```

## License

MIT
