# Product Research

FF&E product research for Claude Code. Give it a brief, it searches the web, and comes back with a curated shortlist. Save the winners to your master Google Sheet.

## How it works

```
Brief → Search → Candidates → Pick → Sheet
```

1. **Brief** — Tell Claude what you're looking for ("round walnut dining table under $3k")
2. **Research** — Claude searches across brands, trade platforms, and design publications
3. **Candidates** — Get 6-10 options with specs, pricing, and reasoning
4. **Pick** — Choose which products to save
5. **Sheet** — Saved to the master Google Sheet

## Usage

```
/product-research
```

Then describe what you need — loose or specific:

```
# Loose
"acoustic panels for a tech office lobby"

# Specific
"round dining table, 48-54" dia, solid walnut or oak,
steel base, under $3,000, needs to ship in 6 weeks"
```

## What it understands

Category, use context, style, materials, dimensions, budget, sustainability certs, lead time, quantity, indoor/outdoor, brand preferences, and must-haves. **Only mention what matters — it works with whatever you give it.**

## Works with

| Tool | How |
|------|-----|
| `/product-data-cleanup` | Normalize the sheet after adding products |
| `/product-spec-bulk-fetch` | Batch-add from URLs |
| `/product-spec-pdf-parser` | Extract from PDF catalogs |
| `/product-image-processor` | Process images from the sheet |

## License

MIT
