---
name: product-enrich
description: Enrich FF&E schedule rows with categories, colors, materials, and style tags. Use to tag, categorize, or fill those missing fields; not to research new products.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /as:product-enrich — Product Enrichment

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

## Record authority and host handoff

Before project writes, run `<plugin-root>/skills/project/scripts/resolve-context.sh` for the supplied path and use its validated project result; follow `<plugin-root>/skills/project/references/context-resolution.md` for other results. Read `<plugin-root>/corpus/practice-methods/ffe/README.md` and [FF&E record contract](../../studio/ffe/README.md).

Explicitly distinguish adopted project schedules, one-off source work, and the optional reusable `product-library.csv`. Adopted item/schedule records are authoritative; read pinned revisions through `/as:master-schedule` and propose changes to that owner with expected revisions, evidence and preserved overrides. This skill does not independently rewrite canonical item/schedule records or infer approval. Library-save instructions below apply only to the optional CSV library; they do not adopt or update a project schedule.

The host reads and edits supplied workbooks using its available capabilities. Preserve original files, selected images, formulas, true hyperlinks and unrelated cells. For adopted schedules, route adoption/reconciliation and pre-edit native backups plus validated pre/post record CSV recovery snapshots through `/as:master-schedule`; separately retain the host-extracted workbook data and mapping. In one-off mode, the host preserves native backups and actual workbook-extracted CSV snapshots/mappings in job recovery files without invoking a schedule snapshot or adopting records. Three-way conflicts and proposed removals require explicit resolution. Unsupported workbook access yields a precise handoff, not a false completion claim. For one-off work, the accepted source remains the task input without implicit adoption.

Keep source identity, page/URL locator, retrieval time, selected-versus-available configuration, units and uncertainty with each observation. Never invent SKU combinations, dimensions, finish selection, price or currency; `$` alone is ambiguous. Preserve user choices until explicitly changed. Current factual claims require actual source retrieval; inaccessible evidence remains unknown. `/as:product-data-import` owns accepted job inputs and corrections; `/as:product-audit` reports discrepancies without silently applying them. `/as:product-cut-sheet` and `/as:spec-book` use the shared document templates and host rendering after inputs are resolved.


Takes product rows from the nearest project's `product-library.csv` or pasted data and proposes missing category, color, material, and style metadata.

## When to Use

- After a bulk import where products are missing categories or tags
- When a designer clips products quickly without filling in details
- To standardize metadata across products from different sources
- Before generating an FF&E schedule (enriched data makes better schedules)

## Step 1: Accept Input

Accept product data in any format:

**CSV file:**
```
/as:product-enrich ./products.csv
```

**Pasted data:**
```
/as:product-enrich
Eames Lounge Chair, Herman Miller
Saarinen Tulip Table, Knoll
PH 5 Pendant, Louis Poulsen
Togo Sofa, Ligne Roset
```

## Step 2: Analyze Each Product

For each product, distinguish sourced specification fields from explicitly labeled tentative descriptive classifications:

### Category
Map to the canonical vocabulary (22 terms) defined in `../../schema/product-schema.md`.

### Subcategory
More specific classification within the category:
- Chair → Task Chair, Lounge Chair, Dining Chair, Side Chair, Stool, Bench
- Table → Dining Table, Coffee Table, Side Table, Console Table, Conference Table
- Light → Pendant, Floor Lamp, Table Lamp, Wall Sconce, Ceiling, Task Light, Chandelier
- Sofa → Sofa, Sectional, Loveseat, Daybed, Settee
- Storage → Credenza, Bookcase, Filing Cabinet, Wardrobe, Sideboard, Dresser
- Desk → Writing Desk, Executive Desk, Standing Desk, Workstation

### Primary Color
The color of the evidenced selected configuration; family availability does not establish selection:
- Use standard color names: Black, White, Gray, Brown, Beige, Navy, Blue, Green, Red, Orange, Yellow, Pink, Purple, Natural, Walnut, Oak, Teak, Chrome, Brass, Copper, Multi

### Material
Primary materials, comma-separated:
- Wood (specify type if known: Walnut, Oak, Maple, Teak, Birch, Ash, Beech)
- Metal (specify: Steel, Aluminum, Brass, Chrome, Iron, Copper)
- Upholstery (specify: Leather, Fabric, Velvet, Bouclé, Mohair, Linen, Wool)
- Other: Glass, Marble, Concrete, Ceramic, Plastic, Fiberglass, Rattan, Cane, Acrylic

### Style Tags
2-4 descriptive tags from:
- Period/movement: Mid-Century Modern, Art Deco, Bauhaus, Scandinavian, Japanese, Industrial, Contemporary, Traditional, Minimalist, Postmodern, Memphis
- Character: Organic, Geometric, Sculptural, Modular, Stackable, Compact, Statement, Classic, Iconic
- Context: Residential, Contract, Hospitality, Healthcare, Education, Outdoor

### Image Analysis
If product data includes the named `Image URL` field, inspect it for tentative visual descriptions. An image alone cannot verify material composition or selected finish. The image may suggest:
- Apparent color under the shown lighting
- Apparent texture, explicitly labeled as inferred
- Style characteristics

## Step 3: Present Preview

Show a preview with evidence status before applying. This illustrative table is not product evidence; do not copy its example finishes into real selections:

```
## Product Enrichment Preview

| Product | Brand | Category | Subcategory | Color | Material | Style Tags |
|---------|-------|----------|-------------|-------|----------|------------|
| Eames Lounge Chair | Herman Miller | Chair | Lounge Chair | Walnut/Black | Molded plywood, Leather | Mid-Century Modern, Iconic, Residential |
| Saarinen Tulip Table | Knoll | Table | Dining Table | White | Marble, Aluminum | Mid-Century Modern, Sculptural, Organic |
| PH 5 Pendant | Louis Poulsen | Light | Pendant | White | Aluminum | Scandinavian, Classic, Iconic |
| Togo Sofa | Ligne Roset | Sofa | Sofa | Brown | Fabric | Contemporary, Organic, Sculptural |

4 products enriched. Apply? (y/n)
```

Flag any products where enrichment is uncertain:
```
⚠ "Custom Reception Desk" — unknown product, category set to Desk but verify
```

## Step 4: Apply

### To the project library
Read `../../schema/product-schema.md` and `../../schema/csv-conventions.md`. Map enrichment only to canonical named fields: `Category`, `Materials`, `Colors/Finishes`, and appended `Tags`; place noncanonical subcategory detail in `Notes`. Do not overwrite a populated field unless the preview explicitly calls that out.

For multiple enriched rows, materialize the complete proposed 33-column CSV as a temporary or user-visible review file. Validate it, preview every material change and the target `product-library.csv` once, then use the single confirmation gate. After approval, invoke `python3 "<plugin-root>/skills/master-schedule/scripts/csv-library.py" import product --project <project-root> --source <review.csv> --replace-existing` exactly once for one atomic replacement; never loop `update`. A genuinely single-record enrichment may use the same plugin-root helper's `update` command once with a uniquely matching stable field.

### To conversation
Output the enriched table in markdown.

## Step 5: Summary

```
✓ Enriched 4 products
  Categories: 4 assigned (0 already had values)
  Colors: 4 assigned
  Materials: 4 assigned
  Style tags: 14 total tags across 4 products
  Uncertain: 1 (flagged for review)
```

## Pairs With

- `/as:product-spec-bulk-fetch` — fetch specs first, then enrich the results
- `/as:product-data-cleanup` — cleanup normalizes formatting, enrich adds metadata
- `/as:product-data-import` — enriched products make better formatted schedules
- `/as:product-match` — enriched tags help find better matches
