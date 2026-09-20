---
name: product-research
description: "Find and compare current FF&E candidates from a design brief, with sourced purchasing facts and optional CSV-library save. Use to research or source products; not to match from an image or pair coordinating items."
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - WebFetch
  - WebSearch
  - AskUserQuestion
---

# /as:product-research — Product Research

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:product-research`). Load only its referenced mode profiles from the [shared catalog](../../corpus/host-contracts.json). Compose modes required by the actual task; declarations are requirements, not proof of access or permission.

Library changes are owned by [/as:product-library](../product-library/SKILL.md). Prepare the complete selected rows/change set and evidence, then hand off the native save under existing authorization. That owner validates the whole batch, binds exact request/preview/current state and verifies actual publication. This skill does not independently mutate `product-library.csv`.

<!-- architecture-studio:harness-compatibility -->
> Host adapter: read [delivery-specific guidance](../../docs/host-adapters.md) for invocation, questions, target access and optional delegation.

## Record authority and host handoff

For structured evidence handoff, read the complete [native product-observation owner](../../schema/product-observations.md) and [schema](../../schema/product-observation.schema.json). Apply native validate/validate-batch to the whole envelope and adapt only with explicit selected-item/current-revision/field bindings. Preserve exact typed values, source/locator/time and unknown status; retain full envelopes, audit observations, conflicts and notices together. Existing null/blank/user overrides survive. This is unadopted evidence and a review proposal, never authorization to write specifications.

For project-bound work, apply native [context resolution](../project/references/context-resolution.md), use its validated project identity and read project instructions. Inline or one-off source work needs no project creation. Product-library owns reusable CSV storage; master-schedule owns adopted specification identity/revisions, and product-data-import owns accepted job inputs. Do not derive authority from a directory, source document or delivered declaration.

Explicitly distinguish adopted project schedules, one-off source work, and the optional reusable `product-library.csv`. Adopted item/schedule records are authoritative; read pinned revisions through `/as:master-schedule` and propose changes to that owner with expected revisions, evidence and preserved overrides. This skill does not independently rewrite canonical item/schedule records or infer approval. Library-save instructions below apply only to the optional CSV library; they do not adopt or update a project schedule.

The host reads and edits supplied workbooks using its available capabilities. Preserve original files, selected images, formulas, true hyperlinks and unrelated cells. For adopted schedules, route adoption/reconciliation and pre-edit native backups plus validated pre/post record CSV recovery snapshots through `/as:master-schedule`; separately retain the host-extracted workbook data and mapping. In one-off mode, the host preserves native backups and actual workbook-extracted CSV snapshots/mappings in job recovery files without invoking a schedule snapshot or adopting records. Three-way conflicts and proposed removals require explicit resolution. Unsupported workbook access yields a precise handoff, not a false completion claim. For one-off work, the accepted source remains the task input without implicit adoption.

Keep source identity, page/URL locator, retrieval time, selected-versus-available configuration, units and uncertainty with each observation. Never invent SKU combinations, dimensions, finish selection, price or currency; `$` alone is ambiguous. Preserve user choices until explicitly changed. Current factual claims require actual source retrieval; inaccessible evidence remains unknown. `/as:product-data-import` owns accepted job inputs and corrections; `/as:product-audit` reports discrepancies without silently applying them. `/as:product-cut-sheet` and `/as:spec-book` use the shared document templates and host rendering after inputs are resolved.


Receives a brief from a designer, researches products across the web, and returns a curated shortlist. Selected products can be saved to the nearest project's `product-library.csv`.

## How It Works

```
Designer gives a brief
        ↓
Host searches authorized sources
        ↓
Presents candidates with specs + reasoning
        ↓
Designer picks winners
        ↓
Saved to project product library
```

## Step 1: Take the Brief

The designer describes what they're looking for. A brief can be loose or specific:

**Loose:**
> "I need acoustic panels for a tech office lobby"

**Specific:**
> "Looking for a round dining table, 48-54" diameter, solid wood top (walnut or oak preferred), steel or brass base, under $3,000, needs to be in stock or <6 week lead time"

### What to capture from the brief

Extract as many of these as the designer provides. **Don't ask for fields they didn't mention** — work with what you have.

| Field | Examples |
|-------|---------|
| **Category** | Table, seating, lighting, acoustic panel, planter, storage |
| **Use context** | Office lobby, conference room, outdoor terrace, home office |
| **Style / aesthetic** | Scandinavian, mid-century, industrial, minimal, warm, bold |
| **Materials** | Solid wood, marble, steel, fabric, mesh, recycled |
| **Dimensions** | "48-54 inch diameter", "under 30 inches tall", "fits a 6x4 space" |
| **Budget** | Under $3,000, $500-$1,000 range, high-end, budget-friendly |
| **Sustainability** | GREENGUARD, FSC, Cradle to Cradle, recycled content, B Corp |
| **Lead time** | In stock, under 6 weeks, no rush |
| **Quantity** | 1 hero piece, 12 for a conference room, 50+ for open office |
| **Indoor/Outdoor** | Indoor, outdoor, both |
| **Must-haves** | Stackable, COM available, ADA compliant, weatherproof |
| **Brands to avoid** | "Not Ikea", "nothing from Amazon" |

**Don't interview the designer.** If the brief is "acoustic panels for a lobby," that's enough to start searching. You can clarify *after* showing initial results if needed ("I found options in fabric, felt, and wood slat — any preference?").

## Step 2: Research

Search the web for products matching the brief. Use multiple targeted queries to cover different angles:

### Search strategy

For a brief like "round dining table, walnut, under $3,000":

1. **Category + material search**: `round walnut dining table`
2. **Design-focused search**: `best round wood dining tables architects designers`
3. **Trade/contract search**: `contract round dining table solid wood specifications` (for commercial projects)
4. **Specific brand searches** if the designer mentioned preferences: `Muuto round table`, `HAY dining table`
5. **Sustainability search** if relevant: `FSC certified round dining table`

Run **3-5 searches** depending on brief complexity. Aim for breadth — different price points, brands, styles.

### For each candidate found

Attempt to fetch the product page with WebFetch to extract full specs. If the page is JS-rendered and returns no data:
- Use the search result only to identify the candidate and locate another current, authoritative source.
- Never fill price, availability, lead time, dimensions, finishes, certifications, or other purchasing facts from model memory.
- Label any volatile fact without a current manufacturer, authorized-dealer, or certification-registry source as `Not verified`; do not turn a search snippet into a confirmed fact.

For every price, availability, lead-time, finish, dimension, and certification claim, retain the source URL and access date. Prefer the manufacturer's current product page or price list; use an authorized dealer only when the manufacturer does not publish the fact. A candidate may remain useful with `Not verified` fields, but the shortlist must make those gaps visible.

**Target: 6-10 candidates** that genuinely match the brief. Don't pad the list with weak matches.

## Step 3: Present Candidates

Show results as a numbered shortlist with enough detail to evaluate:

```text
Synthetic formatting input only:
Example Product A | Example Manufacturer | quantity 2 | supplied specification pending
```

### Presentation rules

- **Lead with the summary table** if there are 6+ candidates — designers scan visually
- **Include "Why"** for each — explain why this product matches the brief, and flag any compromises
- **Flag trade-offs honestly** — "veneer not solid", "over budget but worth seeing", "long lead time"
- **Don't oversell** — if a product is a weak match, say so or don't include it
- **Group by angle** if useful — "Budget options", "Premium picks", "Fastest delivery"

## Step 4: Save to the project library

When the designer picks candidates ("save 1, 3, and 5"), prepare rows for the nearest project-root `product-library.csv`. A project root is the nearest ancestor containing `PROJECT.md`; do not create a library outside one.

### Row format

Read `../../schema/product-schema.md` for the exact 33-column row contract and `../../schema/csv-conventions.md` for local-file rules. Preview all selected products and the target path, then use existing exact authorization or ask once for the missing approval. After approval, serialize all complete rows as one JSON array and hand one complete batch to product-library's native append operation. That owner validates current state and the full batch before guarded publication and fresh readback; never loop per row or hand-edit persistent CSV.

Skill-specific column values:
- **AG (Source):** `research`
- **AF (Status):** `saved`
- **AD (Tags):** From brief context (e.g. "lobby-reno, walnut")
- **AE (Notes):** The "Why" reasoning from the presentation
- **T (Selected Color/Finish):** Blank (designer hasn't configured yet)

### After saving

```
✓ Saved 3 products to your library (rows 48-50).
  Tagged: lobby-reno, walnut

Want me to refine the search? Different style, budget, or materials?
```

## Step 5 (Optional): Iterate

The designer may want to refine:

- **"More like #1 but cheaper"** → Search for alternatives in that style/brand tier
- **"What about outdoor versions?"** → New search with added constraint
- **"Can you find the spec sheet PDF for #3?"** → Search for manufacturer cut sheet
- **"Compare #1 and #3 side by side"** → Detailed comparison
- **"Any of these have GREENGUARD?"** → Check certifications for the shortlist

Each iteration can add more products to the library.

## Conversation Style

- **Don't over-ask before searching.** A one-line brief is enough to start.
- **Show results, then refine.** It's faster to react to real options than to specify everything upfront.
- **Be opinionated.** The designer wants a knowledgeable research assistant, not a search engine. Flag the best options, note trade-offs, suggest alternatives.
- **Know the industry.** Reference relevant brands, designers, trade platforms. Understand contract vs. residential, COM/COL, lead times, certifications.

## Notes

- **JS-rendered product pages** are common (Hem, Muuto, Vitra, etc.). If native retrieval returns no data, use search results only for candidate discovery and seek a current authoritative source; purchasing facts remain Not verified. Do not fill them from general knowledge.
- **The library is shared.** Products from this skill live alongside bulk-fetch imports and PDF extractions. The `Source` field (`research`) identifies where each row came from.

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
