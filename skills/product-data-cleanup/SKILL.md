---
name: product-data-cleanup
description: "Clean a local FF&E CSV schedule by normalizing casing, dimensions, units, language, materials, and formatting. Use when asked to clean, fix, or standardize product data."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

# /as:product-data-cleanup — Product Data Normalizer

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:product-data-cleanup`). Load only its referenced mode profiles from the [shared catalog](../../corpus/host-contracts.json). Compose modes required by the actual task; declarations are requirements, not proof of access or permission.

Library changes are owned by [/as:product-library](../product-library/SKILL.md). Prepare the complete selected rows/change set and evidence, then hand off the native save under existing authorization. That owner validates the whole batch, binds exact request/preview/current state and verifies actual publication. This skill does not independently mutate `product-library.csv`.

<!-- architecture-studio:harness-compatibility -->
> Host adapter: read [delivery-specific guidance](../../docs/host-adapters.md) for invocation, questions, target access and optional delegation.

## Record authority and host handoff

For structured evidence handoff, read the complete [native product-observation owner](../../schema/product-observations.md) and [schema](../../schema/product-observation.schema.json). Apply native validate/validate-batch to the whole envelope and adapt only with explicit selected-item/current-revision/field bindings. Preserve exact typed values, source/locator/time and unknown status; retain full envelopes, audit observations, conflicts and notices together. Existing null/blank/user overrides survive. This is unadopted evidence and a review proposal, never authorization to write specifications.

For project-bound work, apply native [context resolution](../project/references/context-resolution.md), use its validated project identity and read project instructions. Inline or one-off source work needs no project creation. Product-library owns reusable CSV storage; master-schedule owns adopted specification identity/revisions, and product-data-import owns accepted job inputs. Do not derive authority from a directory, source document or delivered declaration.

Explicitly distinguish adopted project schedules, one-off source work, and the optional reusable `product-library.csv`. Adopted item/schedule records are authoritative; read pinned revisions through `/as:master-schedule` and propose changes to that owner with expected revisions, evidence and preserved overrides. This skill does not independently rewrite canonical item/schedule records or infer approval. Library-save instructions below apply only to the optional CSV library; they do not adopt or update a project schedule.

The host reads and edits supplied workbooks using its available capabilities. Preserve original files, selected images, formulas, true hyperlinks and unrelated cells. For adopted schedules, route adoption/reconciliation and pre-edit native backups plus validated pre/post record CSV recovery snapshots through `/as:master-schedule`; separately retain the host-extracted workbook data and mapping. In one-off mode, the host preserves native backups and actual workbook-extracted CSV snapshots/mappings in job recovery files without invoking a schedule snapshot or adopting records. Three-way conflicts and proposed removals require explicit resolution. Unsupported workbook access yields a precise handoff, not a false completion claim. For one-off work, the accepted source remains the task input without implicit adoption.

Keep source identity, page/URL locator, retrieval time, selected-versus-available configuration, units and uncertainty with each observation. Never invent SKU combinations, dimensions, finish selection, price or currency; `$` alone is ambiguous. Preserve user choices until explicitly changed. Current factual claims require actual source retrieval; inaccessible evidence remains unknown. `/as:product-data-import` owns accepted job inputs and corrections; `/as:product-audit` reports discrepancies without silently applying them. `/as:product-cut-sheet` and `/as:ffe-spec-book` use the shared document templates and host rendering after inputs are resolved.


Takes a messy FF&E schedule and normalizes everything: casing, dimensions, units, language, materials vocabulary, currency formatting, and duplicates. Outputs a clean, consistent, spec-ready schedule.

Persistent cleanup operates on the nearest project's `product-library.csv`. Pasted tables may be previewed in Markdown but are not another persistent format.

## Input

The user provides a schedule in one of these ways:

1. **Project library** — the nearest `product-library.csv` under an ancestor containing `PROJECT.md`.
2. **CSV file path** — import only after its exact 33-column header is validated.
3. **Pasted table** — preview a proposed canonical mapping before any persistence.

If the input format is unclear, ask.

## Cleanup Rules

### 1. Casing

| Field | Rule | Example |
|-------|------|---------|
| Collection | Title Case | `cosm` → `Cosm` |
| Category | Title Case, singular | `chairs` → `Chair`, `TABLES` → `Table` |
| Materials | Sentence case, lowercase after first word | `MOLDED PLYWOOD, FULL GRAIN LEATHER` → `Molded plywood, full grain leather` |
| Colors/Finishes | Title Case per item | `walnut/black leather` → `Walnut / Black Leather` |

**Known brand abbreviations to preserve**: HAY, USM, B&B, DWR, CB2, HBF, OFS, SitOnIt, 3form, ICF

### 2. Category Normalization

Map free-text categories to the canonical vocabulary and alias table defined in `../../schema/product-schema.md`. Read that file for the full mapping of variations (English, Spanish, legacy terms) to canonical category names.

If a category is ambiguous, keep the closest match and add a `[?]` flag for the user to review.

### 3. Dimensions

**Splitting combined dimensions:**
| Input | → W | → D | → H | → Unit |
|-------|-----|-----|-----|--------|
| `32 x 24 x 30 in`, source says W×D×H | 32 | 24 | 30 | in |
| `80 × 60 × 75 cm`, source says W×D×H | 80 | 60 | 75 | cm |
| `W32 D24 H30`, no unit evidence | — | — | — | unknown; preserve raw |
| `32"W x 24"D x 30"H` | 32 | 24 | 30 | in |
| `Ancho: 80, Prof: 60, Alto: 75 cm` | 80 | 60 | 75 | cm |

**Dimension rules:**
- Always store as **separate W, D, H columns** with a **Unit column**
- If dimensions are already split, validate they're numeric (strip any unit text from the number)
- Interpret `"` as inches and `'` as feet. A feet or feet-inch value (`2'6"`) has no `in`/`cm`/`mm` Unit value: convert it to inches (`30`) only when the user requests conversion; otherwise preserve the raw value and flag it `[?]`
- Accept `×`, `x`, `X`, `by`, `por` as separators
- W × D × H is the output convention, not proof of source axis order. Use explicit source labels/legend; retain unassigned axes as unknown. Map L/B only with source terminology evidence. Keep overall/cutout/carton dimensions separate.
- Preserve original precision in evidence; round only a requested display projection.
- Missing units stay unknown regardless of magnitude. Do not infer inches or centimetres from plausible furniture sizes.

Keep the source unit by default. Convert only when requested, preserving the raw source and exact
conversion basis. Read [native dimension semantics](../../tools/transformers/evidence-contracts.md)
and apply `dimension_values.normalize` after explicit axis/unit mappings. Populate the actual dimensional output
columns when supported; putting raw dimensions only in Notes is not normalized output. Validate
structured observations before handoff, independently of CSV header validation.

### 4. Language Normalization

Detect the language of each field value and normalize to **English** unless the user specifies otherwise.

| Spanish (common in UY sources) | → English |
|-------------------------------|-----------|
| Silla | Chair (category) |
| Mesa | Table (category) |
| Escritorio | Desk (category) |
| Madera | Wood (material) |
| Cuero | Leather (material) |
| Acero | Steel (material) |
| Vidrio | Glass (material) |
| Tela | Fabric (material) |
| Mármol | Marble (material) |
| Roble | Oak (material) |
| Nogal | Walnut (material) |
| Blanco | White (color) |
| Negro | Black (color) |
| Natural | Natural (keep as-is) |
| Cromado | Chrome (finish) |

**Rule:** Translate category, material, and color/finish fields. Leave Product Name and Brand as-is (proper nouns).

If the user says "keep in Spanish" or specifies a target language, respect that.

### 5. Materials & Finishes Vocabulary

Standardize common material terms:

| Variations | → Standard |
|-----------|------------|
| SS, Stainless, S/S | Stainless steel |
| Ply, Plywood, Mold ply | Molded plywood |
| MDF, Medium density | MDF |
| HPL, High pressure laminate | HPL |
| Lam, Laminate | Laminate |
| Fab, Textile | Fabric |
| COM, C.O.M. | COM (Customer's Own Material) |
| COL, C.O.L. | COL (Customer's Own Leather) |
| Powder coat, PC, Pwdr | Powder-coated |
| Chrm, Chrome plated | Chrome |
| Anodized alum, Anod. | Anodized aluminum |
| Ven, Veneer | Veneer |
| Sol. wood, Solid | Solid wood |

### 6. Price & Currency

- Strip currency symbols (`$`, `€`, `£`, `¥`) from the price number. A symbol alone never sets the Currency column; apply the currency detection rule below
- Remove thousands separators (both `.` and `,` — detect locale: `1.234,56` is EU format, `1,234.56` is US)
- Store as plain decimal number: `5695.00`
- If price says "Contact", "Quote", "Trade", "A consultar", "Consultar" → leave the numeric price blank (unknown, never zero) and preserve the original price text in Notes
- Currency detection: `$` alone does not establish currency. Use explicit source or user-provided ISO currency; otherwise retain unknown. A site location alone is insufficient.
- If a schedule mixes currencies, keep each row's original currency. Add a note at the top.

### 7. Duplicate Detection

- Flag rows with identical Product Name + Brand as potential duplicates
- Flag rows with identical URL as potential duplicates; family/configurator links can represent different selected items
- Don't auto-delete — present duplicates to the user and ask what to keep

### 8. Whitespace & Formatting

- Trim leading/trailing whitespace from all fields
- Collapse multiple spaces to single space
- Remove line breaks within field values
- Normalize list separators: `wood / metal / glass` → `Wood, Metal, Glass` (comma-separated)
- Remove trailing commas or semicolons

## Workflow

### Step 1: Load the schedule
Read the input. Report: "Loaded N rows with M columns."
Map input columns to the canonical schema. If column mapping is ambiguous (e.g., a column called "Size" could be combined dimensions), ask the user.

### Step 2: Analyze issues
Scan all rows and produce a summary:
```
## Cleanup Preview

- **Casing**: X product names need Title Case
- **Categories**: Y rows have non-standard categories (mapping: "chairs" → Chair, etc.)
- **Dimensions**: Z rows have combined dimensions to split
- **Language**: W rows have Spanish-language fields to translate
- **Materials**: V rows have non-standard material terms
- **Prices**: U rows need currency formatting cleanup
- **Duplicates**: T potential duplicate rows found
- **Empty fields**: S rows missing dimensions, R rows missing price
```

### Step 3: Confirm scope
The issue summary is the change preview. Use previously selected cleanup groups and existing exact authorization; present unresolved selectable groups in one gate only when needed; do not ask the same question first in prose.

### Step 4: Apply fixes
Process every row through the active cleanup rules. Track every change made.

### Step 5: Present results
Show a **before/after diff** for a sample of changed rows (up to 5 examples). Then show the full cleaned table.

Report:
```
## Cleanup Complete

- Rows processed: N
- Changes made: X
- Flagged for review: Y (marked with [?])
```

### Step 6: Save
Read `../../schema/product-schema.md` and `../../schema/csv-conventions.md`. For multiple changed rows, materialize the complete proposed 33-column CSV as a temporary or user-visible review file, validate that candidate, preview the whole change once, and use existing exact authorization or ask once for the missing approval. After approval, hand the complete batch to product-library's native import operation; that owner performs one guarded publication, not a per-row loop. A genuinely single-record edit may instead use its native update with one uniquely matching stable field and exact request/current-state evidence. Never overwrite an arbitrary input or hand-edit `product-library.csv`.

## Edge Cases

- **Mixed-language schedule**: Detect dominant language per column, normalize to one language
- **Merged cells or irregular formatting**: Flag and ask user how to handle
- **Extra columns not in schema**: Reject persistence and preview how they would map to canonical fields
- **Empty rows**: List them in the preview as proposed removals; remove only within the approved scope
- **Header detection**: Auto-detect header row (first row with text that matches known field names). If uncertain, ask.

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
