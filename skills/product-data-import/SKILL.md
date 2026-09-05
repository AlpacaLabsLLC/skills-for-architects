---
name: product-data-import
description: Generate a formatted FF&E specification schedule from notes, CSV, or pasted lists and optionally save it to the project's 33-column CSV library. Use when asked to import products or build a schedule.
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /as:product-data-import — Product Data Importer

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

## Record authority and host handoff

Before project writes, run `<plugin-root>/skills/project/scripts/resolve-context.sh` for the supplied path and use its validated project result; follow `<plugin-root>/skills/project/references/context-resolution.md` for other results. Read `<plugin-root>/corpus/practice-methods/ffe/README.md` and [FF&E record contract](../../studio/ffe/README.md).

Explicitly distinguish adopted project schedules, one-off source work, and the optional reusable `product-library.csv`. Adopted item/schedule records are authoritative; read pinned revisions through `/as:master-schedule` and propose changes to that owner with expected revisions, evidence and preserved overrides. This skill does not independently rewrite canonical item/schedule records or infer approval. Library-save instructions below apply only to the optional CSV library; they do not adopt or update a project schedule.

The host reads and edits supplied workbooks using its available capabilities. Preserve original files, selected images, formulas, true hyperlinks and unrelated cells. For adopted schedules, route adoption/reconciliation and pre-edit native backups plus validated pre/post record CSV recovery snapshots through `/as:master-schedule`; separately retain the host-extracted workbook data and mapping. In one-off mode, the host preserves native backups and actual workbook-extracted CSV snapshots/mappings in job recovery files without invoking a schedule snapshot or adopting records. Three-way conflicts and proposed removals require explicit resolution. Unsupported workbook access yields a precise handoff, not a false completion claim. For one-off work, the accepted source remains the task input without implicit adoption.

Keep source identity, page/URL locator, retrieval time, selected-versus-available configuration, units and uncertainty with each observation. Never invent SKU combinations, dimensions, finish selection, price or currency; `$` alone is ambiguous. Preserve user choices until explicitly changed. Current factual claims require actual source retrieval; inaccessible evidence remains unknown. `/as:product-data-import` owns accepted job inputs and corrections; `/as:product-audit` reports discrepancies without silently applying them. `/as:product-cut-sheet` and `/as:spec-book` use the shared document templates and host rendering after inputs are resolved.


Takes raw product data and formats it as a Markdown preview or as rows in the nearest project's `product-library.csv`, using the shared 33-column schema.

## When to Use

- Designer has a list of products in notes or conversation and needs it formatted for a deliverable
- A rough product list needs to become a spec-ready schedule with item numbers, quantities, and extended pricing
- Products from multiple sources need to be consolidated into one formatted schedule
- An existing schedule needs to be reformatted to match the standard schema

## Step 1: Accept Input

The designer provides product data in any format:

**Raw notes:**
```
3x Eames Lounge Chair, Herman Miller, walnut/black leather, $5,695 each
2x Nelson Platform Bench 48", Herman Miller, natural maple, $2,195
1x Noguchi Coffee Table, Herman Miller, walnut/glass, $2,095
Pendant light for above the table - something by Flos, budget $800-1200
```

**Pasted CSV:**
```
Product, Brand, Qty, Price
Eames Lounge Chair, Herman Miller, 3, $5695
Nelson Bench 48, Herman Miller, 2, $2195
```

**A file path:**
```
/as:product-data-import ./product-list.csv
```

**Conversational:**
```
"We need 8 task chairs — Steelcase Leap V2, black, about $1,200 each.
 Also 4 monitor arms, any brand, under $300."
```

Accept whatever the designer gives. Don't ask for more structure — work with what you have.

### Accepted job manifest

For a specification-output job, read `<plugin-root>/schema/ffe-intake.schema.json`. Prepare an explicit input containing mode, job ID, source references/hashes/status, selected tags, optional accepted template source, adopted record basis when relevant, superseded job ID when correcting prior inputs, actor and reason. Show the target and material scope; existing explicit authorization satisfies the single gate. Invoke `python3 "<plugin-root>/tools/transformers/ffe_intake.py" --project <project-root> --input <intake.json>`. The helper creates `ffe/jobs/<job-id>/input-manifest.json` exclusively and does not adopt records. Corrections create a new job linked by `supersedes`, even when the corrected attachment has identical bytes but different scope. Do not overwrite a prior job manifest. The output workflow additionally resolves and pins the effective shared design-system/template dependencies.

## Step 2: Parse and Enrich

For each product in the input:

1. **Extract known fields:** product name, brand, quantity, price, dimensions, materials, finish, category
2. **Retain evidence:** Extract only supplied or actually retrieved facts. Keep missing dimensions, materials and weight unknown; identify which source and selected configuration support each field.
3. **Assign categories:** Map to the canonical vocabulary defined in `../../schema/product-schema.md`
4. **Calculate extended prices:** Unit price × quantity
5. **Preserve item numbers:** Retain supplied tags. If missing, propose unique tags for review; generated labels are not user-confirmed IDs. Canonical opaque item identity belongs to master-schedule.
6. **Flag unknowns:** If a product is vague ("pendant light, Flos, $800-1200"), note it as "TBD — needs specification" and include budget range

### Category prefixes for item numbers

Item number prefixes are defined in `../../schema/product-schema.md` under **Item Number Prefixes**. Read that file for the full mapping of canonical categories to prefixes (e.g. Chair → S, Table → T, Light → L).

## Step 3: Present the Schedule

Show the formatted schedule as a markdown table. The following is an illustrative populated layout, not a source of product facts; populate actual values only from the task evidence:

```
## FF&E Schedule — [Project Name if known]

[n] items · [total qty] units · $[total extended] estimated

| Item # | Product | Brand | Qty | W | D | H | Unit | Materials | Finish | Unit $ | Ext $ | Lead | Notes |
|--------|---------|-------|-----|---|---|---|------|-----------|--------|--------|-------|------|-------|
| S-01 | Eames Lounge Chair | Herman Miller | 3 | 32.75 | 32.5 | 33.5 | in | Molded plywood, leather | Walnut/Black | $5,695 | $17,085 | 8-12w | |
| T-01 | Nelson Platform Bench 48" | Herman Miller | 2 | 48 | 18.5 | 14 | in | Solid maple | Natural | $2,195 | $4,390 | 6-8w | |
| T-02 | Noguchi Coffee Table | Herman Miller | 1 | 50 | 36 | 15.75 | in | Walnut, glass | — | $2,095 | $2,095 | 6-8w | |
| L-01 | TBD Pendant | Flos | 1 | — | — | — | — | — | — | $800-$1,200 | $800-$1,200 | — | Needs specification |

**Subtotals by category:**
- Seating: $17,085 (3 units)
- Tables: $6,485 (3 units)
- Lighting: $800-$1,200 (1 unit, TBD)
- **Total: $24,370-$24,770**
```

### Presentation rules

- **Group by category**, sorted by item number within each group
- **Show subtotals** per category and a grand total
- **Flag TBD items** clearly — include budget range if given
- **Show dimensions** only from supplied or retrieved evidence; leave blank and note "dims TBD" otherwise
- **Don't fabricate prices** — if you're unsure, note "price TBD" or "estimated" and use the designer's stated budget
- **Currency** — retain the evidenced ISO currency or leave unknown; total only compatible currencies and explicit quantities

## Step 4: Choose persistence

The Markdown schedule is always available without a write. For adopted schedules, hand proposed records to `/as:master-schedule`. For optional reusable library storage, use the validated project-root `product-library.csv`. Keep the modes distinct.

## Step 5: Save

Read `../../schema/product-schema.md` for the exact header, category vocabulary, and values. Read `../../schema/csv-conventions.md` for parsing and mutation rules. Preview the complete batch, row count, totals, target path, and material field changes, then use the single confirmation gate. After approval, serialize all complete rows as one JSON array and invoke `python3 "<plugin-root>/skills/master-schedule/scripts/csv-library.py" append product --project <project-root> --row-json <batch.json>` exactly once. The helper owns batch validation and one atomic replacement; never loop per row or rewrite the persistent CSV directly.

Skill-specific column values:
- **AG (Source):** `product-data-import`
- **AF (Status):** `saved`; use `specified` only for an explicitly established selection, never as approval evidence
- **AD (Tags):** Item number (e.g. "S-01") + any project tags
- **AE (Notes):** `Qty: 3 · Ext: $17,085` (quantity and extended price, since the schema has no dedicated Qty column)

### Quantity handling

The product library is one row per product, not per unit. Put quantity and extended price in `Notes`, for example `Qty: 3 · Ext: $17,085`.

## Step 6: Summary

After saving:

```
✓ FF&E Schedule saved to [product-library.csv path]
  [n] line items · [total qty] units · $[total] estimated
  [n] items fully specified, [n] items need specification (TBD)
```

If there are TBD items, offer to research them:

```
Want me to research the TBD items? I can use /as:product-research to find specific products for:
- L-01: Flos pendant, $800-$1,200 budget
```

## Pairs With

- `/as:product-research` — research specific products to fill TBD slots
- `/as:product-spec-bulk-fetch` — pull full specs from product URLs
- `/as:product-data-cleanup` — normalize the schedule after assembly
- `/as:product-enrich` — auto-tag categories, colors, and materials
- `/as:csv-to-sif` — convert the schedule to SIF for dealer procurement
