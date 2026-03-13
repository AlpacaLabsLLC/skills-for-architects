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
5. **Sheet** — Saved to the same Google Sheet used by Norma Jean and other skills

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

## How it relates to Norma Jean

| | Norma Jean | /product-research |
|--|-----------|-------------------|
| **Mode** | Sidecar — you browse, it clips | Brief — you describe, it searches |
| **Who drives** | The designer | Claude |
| **Input** | Alt+C on a product page | "Find me..." |
| **Output** | Row in Google Sheet | Curated shortlist → Google Sheet |
| **Best for** | Known products, fast capture | Discovery, exploration, alternatives |

Both write to the same master sheet with the same schema.

## Works with

| Tool | How |
|------|-----|
| [Norma Jean](https://github.com/AlpacaLabsLLC/norma-jean) | Same sheet, different door — sidecar mode |
| `/product-spec-bulk-cleanup` | Normalize the sheet after adding products |
| `/product-spec-bulk-fetch` | Batch-add from URLs |
| `/product-spec-pdf-parser` | Extract from PDF catalogs |
| `/product-image-processor` | Process images from the sheet |

## License

MIT
