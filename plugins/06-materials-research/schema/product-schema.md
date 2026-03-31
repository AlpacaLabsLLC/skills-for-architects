# FF&E Product Schema

Version 1.0 · 33 columns (A–AG)

One row per product. All FF&E skills in this plugin read and write to this schema — whether the target is a Google Sheet, CSV file, or markdown table. Compatible with [Norma Jean](https://github.com/AlpacaLabsLLC/norma-jean) (columns A–AC) and all `/product-*` skills (columns A–AG).

## Column Reference

### Product Identity (A–J)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| A | Link | Formula | `=HYPERLINK(url, "Link")` | Source page URL. Blank for PDFs or manually entered products. |
| B | Thumbnail | Formula | `=IMAGE(image_url)` | Product hero image. Blank if no image available. |
| C | Product Name | Text | Title Case | Full product name as listed by manufacturer. |
| D | Description | Text | Sentence case | 1–2 sentence description or tagline. |
| E | SKU | Text | As listed | Model number, part number, or catalog number. |
| F | Brand | Text | Title Case | Manufacturer name. Preserve known abbreviations (HAY, USM, HBF, OFS, DWR, CB2). |
| G | Designer | Text | Title Case | Designer or design studio if attributed. Blank if N/A. |
| H | Vendor | Text | Title Case | Retailer or website selling the product. May differ from Brand. |
| I | Collection | Text | Title Case | Product line or collection name. Blank if N/A. |
| J | Category | Text | Title Case | One of 22 canonical terms. See **Category Vocabulary** below. |

### Dimensions (K–P)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| K | W | Number | Decimal | Width. Numeric only, no units. |
| L | D | Number | Decimal | Depth. Numeric only, no units. |
| M | H | Number | Decimal | Height. Numeric only, no units. |
| N | Seat H | Number | Decimal | Seat height. Seating products only, blank otherwise. |
| O | Unit | Text | `in`, `cm`, or `mm` | Dimension unit. Keep manufacturer's original — do not convert. |
| P | Weight | Text | As stated | Weight with unit, e.g. "45 lbs", "20 kg". |

### Materials & Finish (Q–S)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| Q | Materials | Text | Comma-separated | Primary materials, e.g. "Molded plywood, full grain leather". |
| R | Colors/Finishes | Text | Comma-separated | All available color and finish options. |
| S | Selected Color/Finish | Text | — | Designer's specific selection. Often blank initially. |

### Pricing (T–V)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| T | List Price | Number | Decimal, no symbol | Manufacturer list price. No currency symbols or commas. |
| U | Sale Price | Number | Decimal, no symbol | Discounted price if applicable. Blank otherwise. |
| V | Currency | Text | ISO code | `USD`, `EUR`, `GBP`, `UYU`, etc. Default `USD`. |

### Logistics (W–AA)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| W | Lead Time | Text | As stated | Delivery estimate, e.g. "8–12 weeks", "In stock". |
| X | Warranty | Text | As stated | Warranty terms if found. |
| Y | Certifications | Text | Comma-separated | GREENGUARD, FSC, BIFMA, Cradle to Cradle, etc. |
| Z | COM/COL | Text | `COM`, `COL`, or `COM/COL` | Customer's Own Material / Leather availability. Blank if N/A. |
| AA | Indoor/Outdoor | Text | `Indoor`, `Outdoor`, or `Indoor/Outdoor` | Use context. Blank if unspecified. |

### Meta (AB–AC)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| AB | Clipped At | Text | ISO 8601 | Timestamp when row was created, e.g. `2026-03-30T14:30:00Z`. |
| AC | Image URL | Text | Direct URL | Primary product image URL. Blank for PDFs. |

### Research (AD–AG)

| Col | Field | Type | Format | Notes |
|-----|-------|------|--------|-------|
| AD | Tags | Text | Comma-separated | Project tags, room IDs, item numbers, cross-references. E.g. `S-01, lobby-reno, walnut`. |
| AE | Notes | Text | Free text | Skill-specific notes, reasoning, flags, variant info. See **Notes Conventions** below. |
| AF | Status | Text | Lowercase | Row lifecycle state. See **Status Values** below. |
| AG | Source | Text | Lowercase | Which skill created the row. See **Source Values** below. |

## Norma Jean Compatibility

Norma Jean (Chrome extension) writes columns A–AC (29 columns). Skills extend this with AD–AG (4 columns). Both share the same header row. Norma Jean always sets Source to `norma-jean`.

## Category Vocabulary

Use exactly ONE of these 22 terms in column J:

Chair · Table · Sofa · Bed · Light · Storage · Desk · Shelving · Rug · Mirror · Accessory · Tabletop · Kitchen · Bath · Window · Door · Outdoor Furniture · Textile · Acoustic · Planter · Partition · Other

### Category Aliases

Map free-text categories to canonical terms. This table covers English variations, Spanish translations, and legacy terms.

| Canonical | Also matches |
|-----------|-------------|
| Chair | Chairs, Seating, Silla, Sillas, Task Chair, Lounge Chair, Stool, Stools, Bench seating, Office Chair |
| Table | Tables, Mesa, Mesas, Conference Table, Coffee Table, Side Table, Dining Table |
| Sofa | Couch, Loveseat, Settee, Sofá |
| Bed | Beds, Cama, Daybed, Bunk |
| Light | Lights, Lighting, Lamp, Lamps, Luminaria, Luminarias, Pendant, Sconce, Fixture, Chandelier |
| Storage | Cabinet, Cabinets, Credenza, Filing, Locker, Estante |
| Desk | Desks, Escritorio, Workstation (only if clearly a desk, not a table) |
| Shelving | Shelf, Shelves, Bookcase, Bookshelf, Estantería |
| Rug | Rugs, Carpet, Alfombra, Tapete |
| Mirror | Mirrors, Espejo |
| Accessory | Accessories, Accesorios, Clock, Cushion, Throw, Tray, Vase |
| Tabletop | Dinnerware, Glassware, Flatware, Serveware, Vajilla |
| Kitchen | Kitchen fixtures, Cocina |
| Bath | Bathroom, Baño, Bath fixtures |
| Window | Curtain, Drape, Blind, Shade, Cortina, Persiana |
| Door | Doors, Puerta |
| Outdoor Furniture | Outdoor, Exterior, Mueble exterior |
| Textile | Textiles, Fabric, Upholstery, Tapiz |
| Acoustic | Acoustic panel, Sound panel, Baffle, Panel acústico |
| Planter | Planters, Plant pot, Maceta, Jardinera |
| Partition | Partitions, Divider, Screen, Panel, Biombo, Mampara |
| Other | Anything that doesn't fit above |

If a category is ambiguous, use the closest match and add `[?]` for the user to review.

## Item Number Prefixes

Used by `/ffe-schedule` to number items within a schedule. Each category maps to a prefix:

| Category | Prefix |
|----------|--------|
| Chair | S |
| Sofa | S |
| Table | T |
| Desk | D |
| Storage | ST |
| Shelving | ST |
| Light | L |
| Acoustic | AC |
| Textile | TX |
| Rug | TX |
| Accessory | AX |
| Tabletop | AX |
| Mirror | AX |
| Kitchen | FX |
| Bath | FX |
| Window | FX |
| Door | FX |
| Bed | EQ |
| Planter | PL |
| Partition | PT |
| Outdoor Furniture | OT |
| Other | OT |

Numbered sequentially within each prefix: S-01, S-02, T-01, L-01, etc.

## Status Values

| Value | Meaning |
|-------|---------|
| `saved` | Default after any skill writes a row. |
| `specified` | Product is part of a formal FF&E schedule. |
| `quoted` | Dealer has returned pricing. |
| `archived` | No longer under consideration. |

## Source Values

| Value | Written by |
|-------|-----------|
| `research` | `/product-research` |
| `norma-jean` | Norma Jean Chrome extension |
| `bulk-fetch` | `/product-spec-bulk-fetch` |
| `pdf-parser` | `/product-spec-pdf-parser` |
| `ffe-schedule` | `/ffe-schedule` |
| `product-match` | `/product-match` |
| `product-pair` | `/product-pair` |
| `product-enrich` | `/product-enrich` |
| `sif-to-csv` | `/sif-to-csv` |

## Notes Conventions

Column AE (Notes) holds skill-specific metadata. Each skill appends structured data using `|` as delimiter:

| Skill | Notes format |
|-------|-------------|
| `/product-research` | The "Why" reasoning for each candidate |
| `/ffe-schedule` | `Qty: 3 · Ext: $17,085` (quantity and extended price) |
| `/product-spec-pdf-parser` | `Variant: Diamond, Black \| Origin: Sweden \| Source: filename.pdf` |
| `/product-match` | Similarity reasoning |
| `/product-pair` | Design pairing reasoning |
| `/sif-to-csv` | `Sell: $1,200 · Ext List: $4,180 · Ext Sell: $3,600` (dealer pricing) |

## Tags Conventions

Column AD (Tags) holds comma-separated identifiers. Skills append to existing tags — never overwrite.

| Skill | Tags format |
|-------|------------|
| `/ffe-schedule` | Item number: `S-01` |
| `/product-match` | `match:{source-product-name}` |
| `/product-pair` | `pair:{source-product-name}` |
| `/product-enrich` | Style tags: `Mid-Century Modern, Iconic` |
| Any skill | Project tags from designer: `lobby-reno, walnut` |

## CSV Header

When writing to CSV, use this exact header row:

```csv
Link,Thumbnail,Product Name,Description,SKU,Brand,Designer,Vendor,Collection,Category,W,D,H,Seat H,Unit,Weight,Materials,Colors/Finishes,Selected Color/Finish,List Price,Sale Price,Currency,Lead Time,Warranty,Certifications,COM/COL,Indoor/Outdoor,Clipped At,Image URL,Tags,Notes,Status,Source
```

## Empty Cells

Use empty string `""` for fields with no value. Do not use `null`, `N/A`, `—`, or `-`.
