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
| `/spec-package` | Runs fetch → cleanup → images in sequence | Full pipeline for a batch of URLs |

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

## Commands

| Command | Description |
|---------|-------------|
| [spec-package](commands/spec-package.md) | Full pipeline — fetch → cleanup → images in sequence |

## Master Schema

All skills write to a shared 33-column Google Sheet:

| Section | Columns |
|---------|---------|
| Product (A–J) | Link, Thumbnail, Product Name, Description, SKU, Brand, Designer, Vendor, Collection, Category |
| Dimensions (K–P) | W, D, H, Seat H, Unit, Weight |
| Materials & Finish (Q–S) | Materials, Colors/Finishes, Selected Color/Finish |
| Pricing (T–V) | List Price, Sale Price, Currency |
| Logistics (W–AA) | Lead Time, Warranty, Certifications, COM/COL, Indoor/Outdoor |
| Meta (AB–AC) | Clipped At, Image URL |
| Research (AD–AG) | Tags, Notes, Status, Source |

### Category vocabulary (22 terms)

Chair, Table, Sofa, Bed, Light, Storage, Desk, Shelving, Rug, Mirror, Accessory, Tabletop, Kitchen, Bath, Window, Door, Outdoor Furniture, Textile, Acoustic, Planter, Partition, Other

## Install

```bash
claude install github:AlpacaLabsLLC/skills-for-architects/06-materials-research
```

## License

MIT
