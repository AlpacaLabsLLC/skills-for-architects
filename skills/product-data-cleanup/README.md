# /product-data-cleanup

FF&E schedule normalizer for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Takes a messy furniture schedule — mixed casing, combined dimensions, Spanish material names, inconsistent categories — and cleans it into consistent, procurement-ready data.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../../LICENSE)

## Usage

```
/product-data-cleanup 1FMScYW9guezOWc_m4ClTQxxFIpS6TNRr373R-MJGzgE
```

Or point to a file:

```
/product-data-cleanup ~/Documents/product-data-import.csv
```

Or paste a markdown table directly in the conversation.

### Input formats

- **Master Google Sheet** — the shared product library
- **File path** — `.csv`, `.tsv`, or `.md`
- **Pasted table** — markdown or tab-separated data

### Output

Cleans the data in place (Google Sheet) or saves as a new file with `-clean` suffix.

## How it fits

This is a **utility** that normalizes data regardless of source:

| Context | How it's used |
|---------|--------------|
| Standalone | Clean up any FF&E schedule |
| After `/product-spec-bulk-fetch` | Normalize fetched data |
| After `/product-spec-pdf-parser` | Normalize parsed PDF data |
| After `/product-research` | Normalize research results |
| On the master sheet | Clean up the entire library — data from all sources |

## What It Cleans

### Casing

```
eames lounge chair    →  Eames Lounge Chair
HERMAN MILLER         →  Herman Miller
HAY                   →  HAY  (preserved — known abbreviation)
```

### Categories

Maps free text to 22 canonical categories (unified vocabulary shared by all skills):

| Input | → Canonical |
|-------|-------------|
| chairs, silla, seating, stool | Chair |
| mesa, conference table | Table |
| luminaria, pendant, sconce, lighting | Light |
| cabinet, credenza, estante | Storage |
| acoustic panel, baffle | Acoustic |
| biombo, mampara, divider | Partition |

Also: Sofa, Bed, Desk, Shelving, Rug, Mirror, Accessory, Tabletop, Kitchen, Bath, Window, Door, Outdoor Furniture, Textile, Planter, Other.

### Dimensions

Splits combined strings into separate W/D/H + Unit columns:

| Before | W | D | H | Unit |
|--------|---|---|---|------|
| `32 x 24 x 30 in` | 32 | 24 | 30 | in |
| `Ancho: 80, Prof: 60, Alto: 75 cm` | 80 | 60 | 75 | cm |

Units are never converted — manufacturer's original spec preserved for ordering.

### Language

Translates Spanish material and finish terms:

| Spanish | → English |
|---------|-----------|
| Madera → Wood | Cuero → Leather | Acero → Steel |
| Mármol → Marble | Nogal → Walnut | Cromado → Chrome |

Product names and brands stay untouched.

### Materials vocabulary

Standardizes abbreviations: SS → Stainless steel, PC → Powder-coated, COM → COM (Customer's Own Material), etc.

### Price & currency

Strips symbols, detects locale (EU vs US formatting), normalizes to plain decimal.

### Duplicates

Flags identical Product Name + Brand or identical URL — presents for review, never auto-deletes.

## Works with

| Skill | Relationship |
|-------|-------------|
| `/product-research` | Normalizes research results after saving |
| `/product-spec-bulk-fetch` | Normalizes fetched data |
| `/product-spec-pdf-parser` | Normalizes parsed PDF data |
| `/product-image-processor` | Run after cleanup for processed images |

## License

MIT
