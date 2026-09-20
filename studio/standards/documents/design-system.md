# Arch Studio document design system — 1.0.0

This is the shared original design contract for FF&E sheets and specification books. Skills reference it; the host renders it. It is not a PDF engine. An explicitly accepted project reference controls its declared layout/branding overrides; configured studio assets follow, then these bundled defaults. Record override scope rather than silently replacing an accepted reference.

## Page and measurement policy

Use the exact presets in `design-system.json`, portrait or landscape; metric and imperial presets are distinct physical sizes. Custom dimensions require units and valid positive sizes within supported limits. Printed pages use their declared physical size at 100%. Displayed product measurement units are a separate setting; do not label product images as scaled drawings. A requested drawing scale must be explicitly recorded and verified by the relevant drawing workflow.

The shared resolver returns physical width/height, margins, content area, typography and grid parameters. Compact sheets use readable 10.5 pt body type, 24 pt titles, 36 pt margins and one product content module. Larger sheets use additional grid capacity and whitespace rather than enlarged Letter pages; standard sheets use 11 pt body, 30 pt titles and 54 pt margins, boards use 12 pt body, 40 pt titles and 72 pt margins. Table headers and footnotes never fall below 9 pt. Use an available sans-serif family, preferring studio-specified fonts, then Arial, Helvetica or Liberation Sans; record substitution and check glyph coverage.

Portrait and landscape reflow columns/image regions. Respect content area, grid gutter and minimum readable type. Wide formats may use side-by-side image/specification regions; portrait compact formats stack them. Do not stretch or crop the product to fill a box. Keep aspect ratios; target at least 150 effective PPI at printed image size and disclose lower resolution. Preserve required fields with continuation pages if necessary; do not silently omit content or shrink below minimum type. Adjust expected page count before output validation.

## Shared visual and content rules

- Hierarchy: studio/project identity; exact item tag and location/quantity; product category/name/configuration; sourced specification fields/features; source/reference footer.
- Use high contrast dark text on a light background. Status and uncertainty must be expressed in words, not color alone. Preserve links as actual PDF link targets when supplied; inspect links after merging.
- Tables retain units and column headings, repeat headers across continuation pages, and keep each value with its label. Mark unknown data explicitly; a blank may not imply verified absence.
- Exact selected product imagery remains distinct from visibly labeled `Representative product image` or `Product image unavailable`. Decorative imagery never stands in for product evidence.
- Footer: project identity, exact tag where applicable, revision/date and page number. Approval status is displayed only when supported by a decision reference for the pinned revision; generation is not approval.
- Audience field allowlists apply before rendering. Inspect visible and hidden text, metadata, attachments, annotations, links and image content; never distribute private controls or render inputs by default.

## Host acceptance

Inspect every rendered page against effective template and accepted project reference: typography, field order, margins, clipping, overflow, image treatment, image resolution, page numbering and links. Verify every PDF MediaBox and CropBox against the declared dimensions; this contract version requires unrotated page boxes and UserUnit 1. The host must materialize a true landscape page rather than rely on rotation metadata. Unsupported combinations block completion, never fall back to Letter. The native output check verifies geometry and evidence bindings, while visual judgment remains the host's responsibility.
