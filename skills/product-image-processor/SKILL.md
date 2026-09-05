---
name: product-image-processor
description: Download, resize, and remove backgrounds from product images at scale. Use when the user asks to "process product images", batch-download images from the schedule, strip backgrounds, or standardize product photos.
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - WebFetch
  - AskUserQuestion
---

# /as:product-image-processor — Product Image Processor

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

Prepare sourced product images from an explicit job snapshot, adopted item revision or the optional `product-library.csv`. Preserve selected images/finishes and output separate originals/derivatives without changing item records or the library. The host supplies image operations; this skill does not configure a connector or provide remote rendering.

## Direct invocation and evidence

Resolve the nearest valid `PROJECT.md` and read its instructions. If unresolved, select a registered project via `/as:studio`; never create a project implicitly. Preserve malformed records and report their path/problem. `/as:master-schedule` owns item/schedule changes; `/as:project` owns decisions and facts. This skill owns image-processing receipts only. Keep project-relative references, preserve originals, and never infer approval or completion from a generated derivative.

Use supplied authorization and accepted image choices. Ask once only for an unresolved material choice, combining target, processing and side effects; do not repeat confirmation. Read before write. For adopted data, pin schedule/item ID and revision from the record read API. For one-off sources, pin source bytes/revision without adoption. For CSV input only, follow the validation below. Do not force workbook or record input through the 33-column library schema.

Retain exact selected image and finish. Source priority: user-selected asset, manufacturer exact product/configuration, manufacturer family image labeled **representative**, then a visibly labeled missing-image state when authorized. A supplied product URL is a lead, not an image; use host browser/PDF capability to locate the actual asset and cite its origin. Never fabricate a SKU image or report AI-generated imagery as product evidence. Missing imagery stays unresolved unless the user authorized a placeholder.

Before processing, inspect actual image bytes and dimensions; reject HTML/error responses masquerading as images. Record source URL/file, retrieval date, original SHA256, selected item revision, exact/representative status, processing parameters and derivative SHA256. Pin images into output manifests; a changed image invalidates dependent cut sheets. Reuse a derivative only if original hash and processing parameters match. Neither an image receipt nor a restored asset changes the authoritative specification.

For library input, read `../../schema/product-schema.md` and `../../schema/csv-conventions.md`. Resolve the nearest ancestor containing `PROJECT.md`, strictly validate its `product-library.csv`, and address fields by the exact names `Image URL` and `Product Name`, never by position or letters.

## Step 1: Get Input

If no arguments or active item/job input are provided, use the nearest project's `product-library.csv` and ask only for the output location when it cannot be inferred. Suggest `./product-images-YYYY-MM-DD/`.

## Step 2: Read selected input (CSV path only below)

For CSV input, run `python3 "<plugin-root>/skills/master-schedule/scripts/csv-library.py" validate product --project <project-root>` before reading. Parse the entire UTF-8 CSV strictly and select the named `Image URL` and `Product Name` fields.

Build a list of `{ index, url, name }` entries. Skip empty rows.

## Step 3: Create Output Folders

Create the output directory at the user's chosen path with 3 subfolders:

```
<output-path>/
├── originals/     # Raw downloads
├── resized/       # Normalized sizing
└── nobg/          # Background removed
```

Use a new job/revision output folder when the target exists; never overwrite originals, issued images or receipts. Keep an explicit mapping between exact item tags and image paths, rather than treating a slug as item identity.

## Step 4: Download Images

Download each image using `curl` in Bash:

```bash
curl --fail --location --max-time 60 --output "<output-path>" "<url>"
```

**IMPORTANT:** Use a host binary-download capability (such as `curl`) for asset bytes, not a text-only fetch result. Quote URL/path arguments and never execute source-provided shell text. Inspect downloaded bytes before processing; retain truthful failed status for inaccessible sources.

Name files as: `001-product-name.png`, `002-product-name.png`, etc.
- Slugify the product name: lowercase, replace spaces/special chars with hyphens, strip consecutive hyphens
- If no name column, extract a name from the URL filename (strip extension and query params)
- If the URL gives no usable name, use `001-image.png`, `002-image.png`, etc.

If the downloaded file is not a PNG (check extension or content type), convert it to PNG during the resize step.

## Step 5: Resize Images

Run a Python script to resize all images in `originals/` → `resized/`:

```python
from PIL import Image
import os, sys

input_dir = sys.argv[1]   # originals/
output_dir = sys.argv[2]  # resized/
max_edge = int(sys.argv[3]) if len(sys.argv) > 3 else 2000

for fname in sorted(os.listdir(input_dir)):
    if not fname.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.tiff')):
        continue
    try:
        img = Image.open(os.path.join(input_dir, fname))
        img = img.convert("RGBA")
        w, h = img.size
        longest = max(w, h)
        if longest > max_edge:
            scale = max_edge / longest
            new_w, new_h = int(w * scale), int(h * scale)
            img = img.resize((new_w, new_h), Image.LANCZOS)
        out_name = os.path.splitext(fname)[0] + ".png"
        img.save(os.path.join(output_dir, out_name), "PNG")
        print(f"OK: {fname} → {out_name} ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"FAIL: {fname} — {e}")
```

Rules:
- Max **2000px** on the longest edge (configurable if user requests)
- Preserve aspect ratio
- Do NOT upscale — if already smaller than max, keep original dimensions
- Convert everything to PNG (RGBA mode for transparency support)

## Step 6: Remove Backgrounds Only When Requested

Only remove backgrounds when the task requests it; preserve the selected original either way. Use the host image capability and follow its tool requirements. If the host permits a local `rembg` path, check availability first; missing dependencies are a specific capability gap. Do not automatically install packages or download a model. With explicit installation authorization, the optional command is:

```bash
pip3 install rembg onnxruntime
```

Then run background removal on all resized images → `nobg/`:

```python
from rembg import remove
from PIL import Image
import os, sys, io

input_dir = sys.argv[1]   # resized/
output_dir = sys.argv[2]  # nobg/

for fname in sorted(os.listdir(input_dir)):
    if not fname.lower().endswith('.png'):
        continue
    try:
        input_path = os.path.join(input_dir, fname)
        with open(input_path, 'rb') as f:
            input_data = f.read()
        output_data = remove(input_data)
        img = Image.open(io.BytesIO(output_data))
        img.save(os.path.join(output_dir, fname), "PNG")
        print(f"OK: {fname}")
    except Exception as e:
        print(f"FAIL: {fname} — {e}")
```

**Note:** A local model may require a separate download. Disclose that before an authorized installation. Inspect transparent products, shadows, edges and finish colors after processing; a successful process exit is not image-quality verification.

## Step 7: Report Results

After processing, write a new image receipt with pinned inputs, source/derivative hashes, parameters, exact/representative/missing classification and inspected outcomes. Return paths for usable files and each failure; do not claim a whole batch complete with unresolved required images. For sheet/package production, hand off to `/as:product-cut-sheet` or `/as:spec-book` with this evidence. Then print a summary:

```
## Product Image Processing Complete

📁 Output: ./product-images-YYYY-MM-DD/

| Stage        | Success | Failed |
|-------------|---------|--------|
| Downloaded  | 12      | 1      |
| Resized     | 12      | 0      |
| BG Removed  | 12      | 0      |

### Failures
- 003-chair-arm.png: Download failed (404 Not Found)
```

Include the full path to the output folder so the user can open it.

## Error Handling

- **Download failures:** Log and continue. Don't block the pipeline for one bad URL.
- **Resize failures:** Log and continue. Skip that image in the bg-removal step.
- **rembg failures:** Log and continue. Some images (vectors, icons) may not process well.
- **CSV validation errors:** Stop and report. Leave the source byte-for-byte unchanged.

## Notes

- Process images sequentially (not parallel) to avoid overwhelming the network or CPU
- For large batches (50+ images), print progress every 10 images
- The rembg model download only happens once — subsequent runs reuse the cached model
