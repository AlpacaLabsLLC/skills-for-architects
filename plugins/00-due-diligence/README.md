# Due Diligence

A Claude Code plugin for looking up building and property data in New York City. 7 skills that query NYC Open Data (Socrata) across landmarks, DOB permits, violations, ACRIS property records, HPD, and BSA variances. No API key required.

## The Problem

Architects and developers routinely need to check 6+ different NYC databases before starting work on a building — DOB for permits and violations, LPC for landmarks, ACRIS for ownership, HPD for residential compliance, BSA for variances. Each has its own portal, its own search interface, and its own data format. A thorough property check takes 30-60 minutes of manual clicking.

## The Solution

7 standalone skills that each query a specific data domain, plus an orchestrator that runs all of them and produces a combined report. Every skill resolves addresses via PLUTO (no API key needed) and returns structured markdown.

```
Address / BBL / BIN
       │
       ├──→ /nyc-landmarks         → LPC check
       ├──→ /nyc-dob-permits       → permit history
       ├──→ /nyc-dob-violations    → violations + ECB
       ├──→ /nyc-acris             → deeds, mortgages
       ├──→ /nyc-hpd               → residential violations
       └──→ /nyc-bsa               → variances
       │
       └──→ /nyc-property-report   → combined report (all 6)

```

## Data Sources

All queries use the NYC Open Data Socrata API. No authentication required.

| Source | Datasets | What it provides |
|--------|----------|-----------------|
| PLUTO | `64uk-42ks` | Address resolution, BBL, BIN, building class, zoning, lot data |
| LPC | `7mgd-s57w` | Landmark status, historic districts |
| DOB | `ipu4-2q9a`, `ic3t-wcy2`, `rbx6-tga4`, `w9ak-ipjd` | Permits and filings (legacy + DOB NOW) |
| DOB | `3h2n-5cm9`, `6bgk-3dad`, `sjhj-bc8q` | Violations and ECB penalties |
| ACRIS | `bnx9-e6tj`, `8h5j-fqxa`, `636b-3b5g`, `7isb-wh4c` | Property transactions (3-table join) |
| HPD | `wvxf-dwi5`, `csn4-vhvf`, `ygpa-z7cr`, `tesw-yqqr` | Residential violations, complaints, registration |
| BSA | `yvxd-uipr` | Variances and special permits |

## Skills

| Skill | Description |
|-------|-------------|
| [nyc-landmarks](skills/nyc-landmarks/) | LPC landmark & historic district check |
| [nyc-dob-permits](skills/nyc-dob-permits/) | DOB permit & filing history across legacy and DOB NOW |
| [nyc-dob-violations](skills/nyc-dob-violations/) | DOB + ECB violations with open items flagged |
| [nyc-acris](skills/nyc-acris/) | ACRIS property records — deeds, mortgages, ownership chain |
| [nyc-hpd](skills/nyc-hpd/) | HPD violations, complaints & building registration (residential) |
| [nyc-bsa](skills/nyc-bsa/) | BSA variances & special permits |
| [nyc-property-report](skills/nyc-property-report/) | Combined report — runs all 6 skills, one document |

## Agent

For full NYC property + zoning analysis (due diligence, zoning envelope, 3D visualization), see the [NYC Zoning Expert](../../agents/nyc-zoning-expert.md) agent — it orchestrates all 7 skills in this plugin plus the zoning analysis skills.

## Install

**Claude Desktop:**

1. Open the **+** menu → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the **Due Diligence** plugin

**Claude Code (terminal):**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 00-due-diligence@skills-for-architects
```

**Manual:**

```bash
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/00-due-diligence/skills/nyc-landmarks ~/.claude/skills/nyc-landmarks
```

## License

MIT
