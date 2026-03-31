# Google Sheet Conventions

How to set up, structure, and interact with the master product Google Sheet. All FF&E skills in this plugin follow these conventions.

## One Sheet Per Project

Each project gets its own Google Sheets spreadsheet. A designer working on multiple projects maintains separate sheets — one per project.

The spreadsheet URL or ID is provided by the designer when first connecting. Store it for the session — don't ask again within the same conversation.

### Extracting Sheet ID from URL

```
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit#gid=0
```

## Tab Naming

| Tab | Purpose | Required |
|-----|---------|----------|
| Products | Main product library — all rows live here | Yes |
| Archive | Products no longer under consideration | Optional |
| Shortlist | Designer's picks for presentation | Optional |
| Quoted | Products with dealer pricing | Optional |

Tab names are Title Case, no special characters. Skills default to the "Products" tab.

## Header Row Setup

### Row 1: Column headers

Write the exact field names from the [product schema](product-schema.md) into row A1:AG1:

```
Link | Thumbnail | Product Name | Description | SKU | Brand | Designer | Vendor | Collection | Category | W | D | H | Seat H | Unit | Weight | Materials | Colors/Finishes | Selected Color/Finish | List Price | Sale Price | Currency | Lead Time | Warranty | Certifications | COM/COL | Indoor/Outdoor | Clipped At | Image URL | Tags | Notes | Status | Source
```

### Formatting

- **Freeze row 1** — headers stay visible when scrolling down
- **Freeze columns A–C** — Link, Thumbnail, Product Name stay visible when scrolling right
- **Bold the header row**

### Section Colors (optional)

Apply background colors to the header row to visually distinguish sections:

| Section | Columns | Header color |
|---------|---------|-------------|
| Product Identity | A–J | White |
| Dimensions | K–P | Light blue `#D0E0F0` |
| Materials & Finish | Q–S | Light green `#D0F0D0` |
| Pricing | T–V | Light yellow `#F0F0D0` |
| Logistics | W–AA | Light orange `#F0E0D0` |
| Meta | AB–AC | Light gray `#E8E8E8` |
| Research | AD–AG | Light purple `#E0D0F0` |

### Data starts at row 2

All read/write operations assume row 1 is headers and data begins at row 2.

## CRUD Patterns

All patterns use three Google Sheets MCP tools:

| Tool | Purpose |
|------|---------|
| `mcp__google__sheets_spreadsheet_get` | Inspect sheet structure (tabs, row count) |
| `mcp__google__sheets_values_get` | Read cell ranges |
| `mcp__google__sheets_values_update` | Write cell ranges |

### Read: All products

```
mcp__google__sheets_values_get
  spreadsheet_id: "{id}"
  range: "Products!A1:AG"
```

Returns all rows including header. Row 1 = headers, rows 2+ = data.

### Read: Specific columns

```
mcp__google__sheets_values_get
  spreadsheet_id: "{id}"
  range: "Products!C2:C"        # Product names only
  range: "Products!C2:F"        # Name through Brand
  range: "Products!AC2:AC"      # Image URLs only
```

### Read: Find the next empty row

Read column C (Product Name) to find where data ends:

```
mcp__google__sheets_values_get
  spreadsheet_id: "{id}"
  range: "Products!C:C"
```

Count non-empty values. Next empty row = count + 1.

### Write: Append new rows

Calculate the next empty row number (N), then:

```
mcp__google__sheets_values_update
  spreadsheet_id: "{id}"
  range: "Products!A{N}:AG{N}"
  values: [[...33 values...]]
```

For multiple rows:

```
mcp__google__sheets_values_update
  spreadsheet_id: "{id}"
  range: "Products!A{N}:AG{N+count-1}"
  values: [[row1], [row2], ...]
```

### Write: Update specific cells

To update a single product's status (row 15):

```
mcp__google__sheets_values_update
  spreadsheet_id: "{id}"
  range: "Products!AF15"
  values: [["archived"]]
```

### Write: Update a column range

To update Tags and Notes for rows 10–12:

```
mcp__google__sheets_values_update
  spreadsheet_id: "{id}"
  range: "Products!AD10:AE12"
  values: [["tag1", "note1"], ["tag2", "note2"], ["tag3", "note3"]]
```

### Write: Overwrite entire sheet (cleanup)

When `/product-spec-bulk-cleanup` rewrites normalized data:

```
mcp__google__sheets_values_update
  spreadsheet_id: "{id}"
  range: "Products!A2:AG{lastRow}"
  values: [[...all rows...]]
```

### Formula cells

Columns A (Link) and B (Thumbnail) use Google Sheets formulas. Write them as strings starting with `=`:

- Column A: `=HYPERLINK("https://example.com/product", "Link")`
- Column B: `=IMAGE("https://example.com/image.jpg")`

The MCP tool interprets strings starting with `=` as formulas.

### Empty cells

Use empty string `""` for fields with no value. Do not use `null`, `N/A`, or `—`.

### Timestamps

Column AB (Clipped At): ISO 8601 format — `2026-03-30T14:30:00Z`
