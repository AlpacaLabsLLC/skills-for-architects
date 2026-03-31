# Product & Materials Research

A Claude Code plugin for building and maintaining an FF&E product library. Designers discover, capture, and organize furniture, fixtures, and equipment from across the web into a single structured Google Sheet — eliminating the spreadsheet chaos of copy-pasting specs from dozens of manufacturer sites.

## The Problem

Interior designers and architects spend hours manually collecting product data — browsing vendor sites, copying dimensions and pricing into spreadsheets, downloading images, normalizing inconsistent formats. Data ends up scattered across browser bookmarks, email attachments, PDF catalogs, and half-filled spreadsheets with mismatched columns.

## The Solution

One master Google Sheet. Multiple ways to get products in. Every entry structured to the same 33-column schema regardless of source — whether it was clipped from a browser, extracted from a PDF catalog, or found through AI-powered research.

```
┌─────────────────────────────────────────────────────────────────┐
│                       THE DESIGNER                              │
│                                                                 │
│   "Find me walnut        Browsing Hem,       Has a PDF catalog  │
│    tables under $3k"     sees a good chair   from a trade show  │
└──────────┬───────────────────┬───────────────────┬──────────────┘
           │                   │                   │
           ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ /product-research│ │   Norma Jean     │ │  /pdf-parser     │
│                  │ │                  │ │  /bulk-fetch     │
│ "Here are 8      │ │  Alt+C → clipped │ │                  │
│  candidates..."  │ │  in 3 seconds    │ │  12 products     │
│                  │ │                  │ │  extracted        │
│ Claude searches  │ │ Designer browses │ │                  │
│ the web          │ │ and clips        │ │ Batch processing │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                     │
         ▼                    ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                   MASTER GOOGLE SHEET                            │
│                   33 columns · one row per product               │
│                                                                 │
│  ┌─────────┬──────────┬───────────┬────────┬─────────┬────────┐ │
│  │ Product │Dimensions│ Materials │Pricing │Logistics│Research│ │
│  │ Name    │ W  D  H  │ Materials │ List $ │Lead Time│ Tags   │ │
│  │ Brand   │ Seat H   │ Finishes  │ Sale $ │Warranty │ Notes  │ │
│  │ SKU     │ Unit     │ Selected  │Currency│Certs    │ Status │ │
│  │ Designer│ Weight   │           │        │COM/COL  │ Source │ │
│  └─────────┴──────────┴───────────┴────────┴─────────┴────────┘ │
│                                                                 │
│  Source: research · norma-jean · bulk-fetch · pdf-parser         │
│                                                                 │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
       ┌────────────────┐  ┌────────────────────┐
       │ /bulk-cleanup  │  │ /image-processor   │
       │                │  │                    │
       │ Normalize the  │  │ Download, resize,  │
       │ entire sheet   │  │ remove backgrounds │
       └────────────────┘  └────────────────────┘
```

## Data Flow

### Getting products in

| Source | Skill | Input | What happens |
|--------|-------|-------|-------------|
| Research brief | `/product-research` | "Find me sustainable acoustic panels under $300" | Claude searches the web, returns 6-10 candidates with specs and reasoning. Designer picks winners → saved to sheet. |
| Browser | [Norma Jean](https://github.com/AlpacaLabsLLC/norma-jean) | Alt+C on any product page | Chrome extension reads the rendered DOM, sends to Claude for extraction, writes structured row to sheet in ~3 seconds. |
| URL list | `/product-spec-bulk-fetch` | List of product page URLs | Fetches each page, extracts specs via AI, appends rows to sheet. Handles partial results and failures gracefully. |
| PDF catalog | `/product-spec-pdf-parser` | PDF file or folder of PDFs | Extracts text via PyMuPDF, Claude parses product data from price books, fact sheets, and spec sheets. Handles variants and SKU expansion. |

### Processing products

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `/product-spec-bulk-cleanup` | Normalizes casing, maps categories to unified vocabulary, splits combined dimensions, translates Spanish→English, standardizes material terms, detects duplicates | After any batch import, or periodically on the whole sheet |
| `/product-image-processor` | Downloads images from Image URL column, resizes to max 2000px, removes backgrounds via AI | When you need clean product images for presentations or deliverables |

### Data flows through, not around

Every skill reads from and writes back to the same Google Sheet. Data from a Norma Jean clip can be cleaned by `/bulk-cleanup`, then its images processed by `/image-processor`. A `/product-research` result can be re-fetched by `/bulk-fetch` to pull fuller specs. The `Source` column tracks where each row came from, but once in the sheet, all rows are equal.

```
/product-research ──┐
                    │
Norma Jean ─────────┼──→ Master Sheet ──→ /bulk-cleanup ──→ Master Sheet
                    │         │
/bulk-fetch ────────┤         └──→ /image-processor ──→ local image files
                    │
/pdf-parser ────────┘
```

## Skills

| Skill | Type | Description |
|-------|------|-------------|
| [product-research](skills/product-research/) | Workflow | Give a brief, get curated candidates with specs and reasoning |
| [product-spec-bulk-fetch](skills/product-spec-bulk-fetch/) | Utility | Batch-extract specs from product page URLs |
| [product-spec-bulk-cleanup](skills/product-spec-bulk-cleanup/) | Utility | Normalize casing, categories, dimensions, materials, language |
| [product-spec-pdf-parser](skills/product-spec-pdf-parser/) | Utility | Extract specs from PDF catalogs, price books, and spec sheets |
| [product-image-processor](skills/product-image-processor/) | Utility | Download, resize, and remove backgrounds from product images |
| [ffe-schedule](skills/ffe-schedule/) | Workflow | Turn raw product lists into formatted FF&E specification schedules |
| [product-enrich](skills/product-enrich/) | Utility | Auto-tag products with categories, colors, materials, and style tags |
| [product-match](skills/product-match/) | Workflow | Find similar products from an image, name, or description |
| [product-pair](skills/product-pair/) | Workflow | Suggest complementary products that pair well with a given item |
| [csv-to-sif](skills/csv-to-sif/) | Utility | Convert CSV product lists to SIF format for dealer systems |
| [sif-to-csv](skills/sif-to-csv/) | Utility | Convert SIF files from dealers into readable spreadsheets |

## Agents

Two agents orchestrate the skills in this plugin:

| Agent | What it does |
|-------|-------------|
| [Product & Materials Researcher](../../agents/product-and-materials-researcher.md) | Finds products from a brief, extracts specs from URLs/PDFs, tags and classifies, finds alternatives |
| [FF&E Designer](../../agents/ffe-designer.md) | Builds clean schedules from messy inputs, composes room packages, runs QA, exports to dealer formats |

## Master Schema

All skills write to a shared 33-column Google Sheet. The full column reference, category vocabulary, CSV header, and CRUD patterns are in the schema directory:

- **[schema/product-schema.md](schema/product-schema.md)** — column definitions, types, formats, category vocabulary, category aliases, status/source values, item number prefixes
- **[schema/sheet-conventions.md](schema/sheet-conventions.md)** — tab naming, header formatting, section colors, CRUD patterns with MCP tools

Quick reference:

| Section | Columns |
|---------|---------|
| Product Identity | A–J |
| Dimensions | K–P |
| Materials & Finish | Q–S |
| Pricing | T–V |
| Logistics | W–AA |
| Meta | AB–AC |
| Research | AD–AG |

## Install

**Claude Desktop:**

1. Open the **+** menu → **Add marketplace from GitHub**
2. Enter `AlpacaLabsLLC/skills-for-architects`
3. Install the **Materials Research** plugin

**Claude Code (terminal):**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install 06-materials-research@skills-for-architects
```

**Manual:**

```bash
git clone https://github.com/AlpacaLabsLLC/skills-for-architects.git
ln -s $(pwd)/skills-for-architects/plugins/06-materials-research/skills/product-research ~/.claude/skills/product-research
```

## License

MIT
