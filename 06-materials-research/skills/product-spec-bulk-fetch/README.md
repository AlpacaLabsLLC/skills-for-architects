# /product-spec-bulk-fetch

Bulk FF&E product spec extractor for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Feed it a list of product page URLs — get a standardized schedule written to your master Google Sheet.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../LICENSE)

## Usage

```
/product-spec-bulk-fetch
```

Then provide URLs — paste inline, point to a file, or give a Google Sheet column of product links.

```
/product-spec-bulk-fetch

https://www.hermanmiller.com/products/seating/lounge-chairs/eames-lounge-chair/
https://www.steelcase.com/products/collaborative-chairs/gesture/
https://www.ikea.pr/puertorico/es/pd/vardagen-vaso-art-70313106
```

### Input formats

- **Inline URLs** — one per line or comma-separated
- **File path** — a `.txt`, `.csv`, or `.md` file with URLs (one per line)
- **Google Sheet** — spreadsheet ID + column containing product URLs

### Output

Appends rows to the **master Google Sheet** (same sheet used by Norma Jean and all data-management skills) using the 33-column schema. Can also output to local CSV or markdown.

## How it fits

This is a **utility** — it can be called standalone or as part of a larger workflow:

| Context | How it's used |
|---------|--------------|
| Standalone | Designer has a list of URLs to batch-process |
| `/product-research` | Claude found candidates → bulk-fetch pulls full specs from their URLs |
| `/spec-package` | Step 1 of the full pipeline (fetch → cleanup → images) |

## Output Schema

33 columns matching the master schema. Key fields populated:

| Field | Example |
|-------|---------|
| Product Name | Eames Lounge Chair |
| Brand | Herman Miller |
| Category | Chair |
| W × D × H | 32.75 × 32.5 × 33.5 in |
| Materials | Molded plywood, leather |
| List Price | 5695.00 USD |
| Source | `bulk-fetch` |

Also extracts when available: Description, SKU, Designer, Vendor, Collection, Seat H, Weight, Sale Price, Warranty, Certifications, COM/COL, Indoor/Outdoor.

## Error Handling

Never stops a batch on a single failure:

- **Trade/dealer sites** with hidden pricing → row included, price left blank
- **JS-rendered pages** → may return partial data or fail (use Norma Jean for these)
- **Login-required pages** → logged as failed, batch continues
- **Non-product pages** → detected and skipped

After every batch: `Fetched: X/Y successful, Z partial, W failed`

## Works with

| Skill | Relationship |
|-------|-------------|
| [Norma Jean](https://github.com/AlpacaLabsLLC/norma-jean) | Same sheet — Norma Jean clips from browser, this fetches from URLs |
| `/product-research` | Research finds candidates, this pulls full specs |
| `/product-spec-bulk-cleanup` | Run after fetching to normalize the sheet |
| `/product-image-processor` | Run after fetching to process product images |

## License

MIT
