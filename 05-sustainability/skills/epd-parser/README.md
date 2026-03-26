# /epd-parser

Extract structured environmental impact data from EPD PDFs for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Parses Environmental Product Declaration PDFs — extracting GWP, life cycle stages, program operator metadata, and LEED eligibility into a standardized 42-column schema.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../LICENSE)

## Install

```bash
claude install github:AlpacaLabsLLC/skills-for-architects/05-sustainability
```

## Usage

```
/epd-parser ~/Downloads/EPD11075.pdf
```

A folder of EPDs:

```
/epd-parser ~/Documents/project-epds/
```

## What it extracts

- **Product identity** — manufacturer, product name, declared unit, CSI division
- **EPD metadata** — registration number, program operator, PCR, standard version, validity dates, system boundary
- **Impact indicators** — GWP-total, GWP-fossil, GWP-biogenic (A1-A3), plus A4-A5, B1-B7, C1-C4, D when available
- **Additional impacts** — ODP, AP, EP, POCP
- **Resource use** — renewable/non-renewable primary energy, fresh water, recycled content, waste
- **LEED eligibility** — flags product-specific vs. industry-average, third-party verification status

Handles EN 15804+A1 and +A2 formats, multi-product EPDs, non-English documents, and varying table layouts across program operators (UL, NSF, Environdec, IBU, ASTM).

Output saves to CSV (42-column EPD schema) or Google Sheets.

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Extraction workflow, 42-column schema, edge case handling |

## License

MIT
