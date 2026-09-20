---
name: product-enrich
description: "Enrich FF&E schedule rows with categories, colors, materials, and style tags. Use to tag, categorize, or fill those missing fields; not to research new products."
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

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:product-enrich`). Load only its referenced mode profiles from the [shared catalog](../../corpus/host-contracts.json). Compose modes required by the actual task; declarations are requirements, not proof of access or permission.

Library changes are owned by [/as:product-library](../product-library/SKILL.md). Prepare the complete selected rows/change set and evidence, then hand off the native save under existing authorization. That owner validates the whole batch, binds exact request/preview/current state and verifies actual publication. This skill does not independently mutate `product-library.csv`.

<!-- architecture-studio:harness-compatibility -->
> Host adapter: read [delivery-specific guidance](../../docs/host-adapters.md) for invocation, questions, target access and optional delegation.

## Record authority and host handoff

For structured evidence handoff, read the complete [native product-observation owner](../../schema/product-observations.md) and [schema](../../schema/product-observation.schema.json). Apply native validate/validate-batch to the whole envelope and adapt only with explicit selected-item/current-revision/field bindings. Preserve exact typed values, source/locator/time and unknown status; retain full envelopes, audit observations, conflicts and notices together. Existing null/blank/user overrides survive. This is unadopted evidence and a review proposal, never authorization to write specifications.

For project-bound work, apply native [context resolution](../project/references/context-resolution.md), use its validated project identity and read project instructions. Inline or one-off source work needs no project creation. Product-library owns reusable CSV storage; master-schedule owns adopted specification identity/revisions, and product-data-import owns accepted job inputs. Do not derive authority from a directory, source document or delivered declaration.

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
```text
Synthetic formatting input only:
Example Product A | Example Manufacturer | quantity 2 | supplied specification pending
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

```text
Synthetic formatting input only:
Example Product A | Example Manufacturer | quantity 2 | supplied specification pending
```

Flag any products where enrichment is uncertain:
```
⚠ "Custom Reception Desk" — unknown product, category set to Desk but verify
```

## Step 4: Apply

### To the project library
Read `../../schema/product-schema.md` and `../../schema/csv-conventions.md`. Map enrichment only to canonical named fields: `Category`, `Materials`, `Colors/Finishes`, and appended `Tags`; place noncanonical subcategory detail in `Notes`. Do not overwrite a populated field unless the preview explicitly calls that out.

For multiple enriched rows, materialize the complete proposed 33-column CSV as a temporary or user-visible review file. Validate it, preview every material change and the target `product-library.csv` once, then use existing exact authorization or ask once for the missing approval. After approval, hand the complete batch to product-library's native import operation for one guarded publication, not a per-row loop. A genuinely single-record enrichment may use that owner's native update with a uniquely matching stable field and exact request/current-state evidence.

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

## Original product evidence

Retrieve exact selected manufacturer/product/variant facts from original documents for the task. Example data is synthetic and never evidence. Do not copy product facts, certifications, prices or vendor format definitions into the plugin as reusable reference knowledge. Preserve unresolved values and distinguish representative imagery from the exact selected variant.

## Native output and owner handoff

A requested durable authored report uses receive's native document owner for exact coordinate-based placement, query and registration; do not compose project folders from labels. One-off reports use only their explicitly authorized destination and require no studio/project setup. Canonical adopted revisions and reusable library saves remain with their owners. Existing exact authorization persists; obtain only missing material scope or native permission.

For any output this skill actually saves or edits, apply the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence) to its complete affected set. Retain all original bytes/access, source/identity guards, complete prepared output and absence/preconditions; finish durable saves and independently reread **all** retained/prepared content and access before the first publisher. Preserve unrelated data and actual workbook features when applicable. Reopen every actual destination's complete bytes and mode/applicable ownership/ACLs, and verify changes, source lineage and protected originals before reporting completion. Correct bytes, a creation-mode argument or an emitted receipt alone is insufficient. Unsupported protection or uncertain publication stays blocked/pending with recovery evidence.

Use native capabilities suited to the selected mode; process execution is optional when the chosen method needs it. No Arch Studio runner, executable download or source reconstruction is required. Read-only/inline work does not need write capability. Report actual research/extraction, validated proposal and any independently verified owner save separately; do not claim an owner handoff has completed without its actual evidence.

## Native workbook preservation comparison

When an explicitly selected before/after native `.xlsx` or `.xlsm` pair and permitted cell edits are
available, load the complete [workbook comparison owner](../../tools/validators/workbook-preservation-contract.md)
and perform native `workbook_preservation.compare` with actual ZIP/XML inspection. Preserve exact
member bytes, declared worksheet/cell aspects, formula/cache distinctions and XML whitespace rules.
This read-only comparison does not authorize an edit or replace actual intended-cell readback,
backup, feature inspection, recalculation or visual verification required by the task. Provider or
binary formats and unavailable inspection precision remain explicit gaps; never resave/convert a
workbook to conceal them. No Arch Studio helper or process runtime is mandatory.
