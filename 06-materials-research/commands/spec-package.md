---
description: Run a full FF&E spec extraction pipeline — fetch specs from URLs, clean up the data, and process product images. All output goes to the master Google Sheet.
argument-hint: [product URLs or file path with URLs]
---

Run this three-step pipeline in sequence. All steps read from and write to the **master Google Sheet** using the 33-column schema defined in `../schema/product-schema.md`. See `../schema/sheet-conventions.md` for CRUD patterns.

## Step 1: Product Spec Bulk Fetch

Invoke the `/product-spec-bulk-fetch` skill with the user's product URLs. Extract product specs into the master schema and append rows to the Google Sheet. Set `Source` to `bulk-fetch`.

## Step 2: Product Spec Bulk Cleanup

Invoke the `/product-spec-bulk-cleanup` skill on the sheet. Normalize casing, map categories to the unified vocabulary, translate non-English fields, standardize dimensions and materials, and flag duplicates.

## Step 3: Product Image Processor

Invoke the `/product-image-processor` skill on the sheet. Download images from the Image URL column (AC), resize, and remove backgrounds.

## Handoff

Between each step, confirm the data carried forward:
- **After Step 1:** Number of products fetched (successful / partial / failed), rows appended
- **After Step 2:** Number of records cleaned, fields normalized, duplicates flagged
- **After Step 3:** Number of images processed, output directory, any failed downloads
