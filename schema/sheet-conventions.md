# Google Sheet Conventions

How to set up, structure, and interact with the master product Google Sheet. All FF&E skills in this plugin follow these conventions.

## Template Sheet

All projects use a copy of the **master template sheet**. The template has the correct column order, formatting, dropdowns, frozen rows, and section colors pre-configured.

Template ID: `1mWnExnSWTKJv0vbu1mDnrQFmv_Iz_fNklIeuBYfMB5k`

To start a new project: duplicate the template in Google Drive, rename it, and share it with your service account.

## One Sheet Per Project

Each project gets its own Google Sheets spreadsheet. A designer working on multiple projects maintains separate sheets — one per project.

The spreadsheet URL or ID is provided by the designer when first connecting. Store it in `master-schedule.json` — don't ask again within the same conversation.

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
Category | Brand | Vendor | Thumbnail | Product Name | Designer | Indoor/Outdoor | Description | SKU | Link | Collection | W | D | H | Seat H | Unit | Weight | Materials | Colors/Finishes | Selected Color/Finish | List Price | Sale Price | Currency | Lead Time | Warranty | Certifications | COM/COL | Clipped At | Image URL | Tags | Notes | Status | Source
```

### Formatting

- **Freeze row 1** — headers stay visible when scrolling down
- **Freeze columns A–E** — Category, Brand, Vendor, Thumbnail, Product Name stay visible when scrolling right
- **Bold the header row**
- **Currency format** — columns U (List Price) and V (Sale Price) as `$#,##0.00`

### Section Colors (optional)

Apply background colors to the header row to visually distinguish sections:

| Section | Columns | Header color |
|---------|---------|-------------|
| Product Identity | A–K | White |
| Dimensions | L–Q | Light blue `#D0E0F0` |
| Materials & Finish | R–T | Light green `#D0F0D0` |
| Pricing | U–W | Light yellow `#F0F0D0` |
| Logistics | X–AA | Light orange `#F0E0D0` |
| Meta | AB–AC | Light gray `#E8E8E8` |
| Research | AD–AG | Light purple `#E0D0F0` |

### Data starts at row 2

All read/write operations assume row 1 is headers and data begins at row 2.

## CRUD Patterns

All patterns use the Google Sheets MCP tools:

| Tool | Purpose |
|------|---------|
| `mcp__google-sheets__list_sheets` | List tabs in a spreadsheet |
| `mcp__google-sheets__get_sheet_data` | Read cell ranges |
| `mcp__google-sheets__update_cells` | Write a single range |
| `mcp__google-sheets__batch_update_cells` | Write multiple ranges |

### Read: All products

```
mcp__google-sheets__get_sheet_data
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "A1:AG"
```

Returns all rows including header. Row 1 = headers, rows 2+ = data.

### Read: Specific columns

```
mcp__google-sheets__get_sheet_data
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "E2:E"         # Product names only
  range: "E2:B"         # Name through Brand
  range: "AC2:AC"       # Image URLs only
```

### Read: Find the next empty row

Read column E (Product Name) to find where data ends:

```
mcp__google-sheets__get_sheet_data
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "E:E"
```

Count non-empty values. Next empty row = count + 1.

### Write: Append new rows

Calculate the next empty row number (N), then:

```
mcp__google-sheets__update_cells
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "A{N}:AG{N}"
  data: [[...33 values...]]
```

For multiple rows:

```
mcp__google-sheets__update_cells
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "A{N}:AG{N+count-1}"
  data: [[row1], [row2], ...]
```

### Write: Update specific cells

To update a single product's status (row 15):

```
mcp__google-sheets__update_cells
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "AF15"
  data: [["archived"]]
```

### Write: Update a column range

To update Tags and Notes for rows 10–12:

```
mcp__google-sheets__batch_update_cells
  spreadsheet_id: "{id}"
  sheet: "Products"
  ranges: {"AD10:AE12": [["tag1", "note1"], ["tag2", "note2"], ["tag3", "note3"]]}
```

### Write: Overwrite entire sheet (cleanup)

When `/product-data-cleanup` rewrites normalized data:

```
mcp__google-sheets__update_cells
  spreadsheet_id: "{id}"
  sheet: "Products"
  range: "A2:AG{lastRow}"
  data: [[...all rows...]]
```

### Formula cells

Columns D (Thumbnail) and J (Link) use Google Sheets formulas. Write them as strings starting with `=`:

- Column D: `=IMAGE(AC{row})`
- Column J: `=HYPERLINK("https://example.com/product", "Link")`

The MCP tool interprets strings starting with `=` as formulas.

### Empty cells

Use empty string `""` for fields with no value. Do not use `null`, `N/A`, or `—`.

### Timestamps

Column AB (Clipped At): ISO 8601 format — `2026-03-30T14:30:00Z`
