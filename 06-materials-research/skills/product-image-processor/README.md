# /product-image-processor

Batch product image processor for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). Read image URLs from a Google Sheet, download at full resolution, normalize sizing, and remove backgrounds — saving output at each stage.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](../../../LICENSE)

### Dependencies

Requires Python 3.9+ with:

- **Pillow** — image resizing and format conversion
- **rembg + onnxruntime** — AI background removal (u2net model)

The skill auto-installs missing packages on first run. The u2net model (~170MB) downloads once and is cached.

## Usage

```
/product-image-processor
```

Then provide a Google Sheet ID. In the master schema, Image URLs are in column AC and Product Names in column C.

```
/product-image-processor

Sheet: 1FMScYW9guezOWc_m4ClTQxxFIpS6TNRr373R-MJGzgE
```

### Output

Three folders, one per processing stage:

```
product-images-YYYY-MM-DD/
├── originals/    # Raw downloads (any format)
├── resized/      # Max 2000px longest edge, PNG
└── nobg/         # Background removed, transparent PNG
```

## How it fits

This is a **utility** that processes images from any source:

| Context | How it's used |
|---------|--------------|
| Standalone | Process images from any Google Sheet with image URLs |
| After `/product-spec-bulk-fetch` | Process images from fetched products |
| After `/product-research` | Process images from research results |
| On the master sheet | Process all product images in the library |

## Processing Pipeline

| Stage | What happens | Tool |
|-------|-------------|------|
| Download | `curl -L` each URL, preserve original format | curl |
| Resize | Scale to max 2000px longest edge, convert to PNG, skip upscaling | Pillow |
| BG Remove | AI background removal via u2net, output transparent PNG | rembg |

## Error Handling

Never stops a batch on a single failure:

- **Download failures** (404, timeouts) — logged and skipped
- **Resize failures** (corrupt files) — logged and skipped
- **rembg failures** (vectors, icons) — logged, original kept

After every batch: success/failure counts per stage.

## Works with

| Skill | Relationship |
|-------|-------------|
| [Norma Jean](https://github.com/AlpacaLabsLLC/norma-jean) | Processes images from the same master sheet |
| `/product-research` | Processes images from research results |
| `/product-spec-bulk-fetch` | Processes images from fetched products |
| `/product-spec-bulk-cleanup` | Run cleanup first, then process images |

## License

MIT
