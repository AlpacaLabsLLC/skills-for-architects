# /sif-to-csv

Convert SIF (Standard Interchange Format) files from dealers into readable CSV spreadsheets, for [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../LICENSE)

## Install

```bash
# Via plugin system
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 06-materials-research@skills-for-architects

# Or symlink just this skill
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/06-materials-research/skills/sif-to-csv ~/.claude/skills/sif-to-csv
```

## Usage

```
/sif-to-csv ~/Documents/project/dealer-quote.sif
```

Parses SIF field codes, expands manufacturer codes, calculates sell prices from discounts, and outputs a clean spreadsheet. Handles Standard, CET, and Cyncly Worksheet SIF dialects.

## SIF Field Reference

| Code | Name | Description |
|------|------|-------------|
| `SF` | Specification File | Project reference (header) |
| `ST` | Specification Title | Display title (header) |
| `PN` | Product Number | SKU — starts each record |
| `PD` | Product Description | Product name |
| `MC` | Manufacturer Code | 3-5 char code (HMI, KNL, STC) |
| `MN` | Manufacturer Name | Full brand name |
| `QT` / `NT` | Quantity | Integer (QT standard, NT alternate) |
| `PL` | List Price | Unit price |
| `P1`-`P5` | Price Tiers | Alternate price tiers |
| `I1` / `I2` | Cyncly Prices | List / purchase price |
| `GC` | Category | Product category |
| `G0` | Vendor ID | Vendor identifier |
| `TG` | Side Mark / Tag | Room or area |
| `S-` / `S%` | Sell Discount % | Sell = PL - (PL × S- × 0.01) |
| `P%` / `B%` | Purchase % | Cost = PL × (P% × 0.01) |
| `ON`/`OD` | Option | Finish, fabric, color (paired) |
| `AN`/`AD` | Attribute | Dimensions, weight (paired) |
| `WT` | Weight | Product weight |
| `VO` | Volume | Product volume |
| `ProductURL` | Product URL | Link to product page |
| `ImageURL` | Image URL | Link to product image |

Manufacturer code variants: `MC` (standard), `MG` (Cyncly), `EC` (CET).

## What's Included

| File | Purpose |
|------|---------|
| `SKILL.md` | Skill definition with full SIF spec, parsing rules, and manufacturer code expansion |

## License

MIT
