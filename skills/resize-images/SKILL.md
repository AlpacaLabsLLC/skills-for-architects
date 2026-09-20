---
name: resize-images
description: "Batch-resize or convert a folder of images for web, social media, slides, or ARCH-size print output while preserving originals. Use for image resizing, format presets, or photo batches; not for product-image background removal."
allowed-tools:
  - Read
  - Bash
  - Glob
  - AskUserQuestion
---

# /as:resize-images — Image Resizer for Web, Social, and Print

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:resize-images`). Compose only applicable modes from the [shared catalog](../../corpus/host-contracts.json); declarations do not prove access or permission. Use the actual host’s [delivery route](../../docs/host-adapters.md).

## Select the requested batch

Resize photos and renders into requested copies while preserving originals. Reuse the supplied source folder and selected `web`, `social`, `slides` or `print` modes. Ask only for materially missing inputs, not information or authorization already supplied. This one-off operation requires no studio/project setup.

Read the complete [native resize owner](../../tools/transformers/resize-images-contract.md) for `resize_images.resize`: exact input and output membership, all twelve preset labels/dimensions/encoding settings, width-only web behavior, center crop, print rounding/DPI, first-frame/color scope, literal collision checks, failure and retry semantics. Use the actual host's available tools; no installed Arch Studio runner, executable handoff or universal dependency installation is required. The presets are Arch Studio-authored sizes, not current external platform requirements. A different requested dimension/crop needs an actually supported separately selected route.

## Inspect, prepare and publish

Scan the authorized folder non-recursively for supported `.jpg`, `.jpeg`, `.png`, `.tif`, `.tiff` and `.webp` files; report the count and stop explicitly on no supported inputs. Inspect actual access, source membership and collision boundaries before processing. Preserve originals, names, unrelated files and source access metadata. Duplicate stems or existing reserved outputs block except a proven exact retry.

Follow the owner's complete-batch preparation and the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence). Prepare every successful source's whole derivative group and any requested public report before the first publisher; failed sources contribute no partial derivative group and do not prevent preparing other sources. Durably finish, separately reopen and verify the entire retained original/prepared byte and access set. Publish complete files with no clobber; a direct public file creation followed by writing is insufficient. Reopen and inspect every actual image/report destination and access metadata, then the full protected/source set before completion. Reconcile interrupted or exact repeated work before making new copies.

## Inspect and report results

Verify decoded dimensions, format, print 300×300 DPI and actual crop/orientation/color behavior. Inspect the images for material subject clipping; center crop has no subject detection. Web limits width, print fits an unrotated box, and both avoid enlargement. Small inputs still receive every selected labelled output; social/slides enlarge to fill. Non-RGB/L sources convert to RGB with alpha discarded, and animated/multipage sources contribute only their initial frame. Do not promise ICC/EXIF preservation, metadata stripping or automatic orientation correction.

List actual output directories, filenames, dimensions and integer KiB, successful/failed source counts and concrete errors/omissions. Keep the compatible mechanical summary separate from [actual completion evidence](../../docs/completion-reporting.md); partial batch success is not full completion. No record adoption, registration, upload or external delivery is implicit.
