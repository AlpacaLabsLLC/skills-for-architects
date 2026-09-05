# FF&E specification evidence

These original methods govern architectural product selections across appliances, plumbing, finishes and furniture. They are data/evidence conventions, not engineering design or regulatory approval.

## One authority per record

An explicitly adopted schedule and its immutable item revisions own the specification. Master-schedule owns record changes; research, extraction, cleanup and audit propose changes. A workbook is a mapped view, an optional 33-column product library is reusable data, and CSV/native backups are recovery material. None silently overwrites adopted records. A one-off task uses an explicit source snapshot without automatic adoption.

Freeze source identity, accepted scope/corrections, template and selected tags before producing outputs. Preserve IDs across retagging/reordering. Keep field evidence and approval/rationale distinct. A new revision does not inherit approval merely because the previous revision was approved. Missing rationale is unknown. No artifact creation proves delivery or acceptance.

## Product and evidence distinctions

| Topic | Required distinction |
|---|---|
| Identity | Manufacturer/brand versus dealer/vendor; product family versus confirmed model, option or accessory; project item ID versus orderable SKU |
| Configuration | Available options versus actual selected finish/handing/size; dependencies must be evidenced. Never concatenate options into a claimed manufacturer SKU |
| Dimensions | Width/depth/height with unit and meaning; product envelope versus cutout, rough-in, clearance, shipping carton and overall assembly |
| Pricing | List, sale, dealer net, quote, estimate and budget are different. Record amount, currency, basis/date and scope; unknown is not zero or a default currency |
| Quantities | Ordered units and room allocations belong to the item selection, not the product family; do not multiply prices of incompatible scope |
| Images | Selected exact variant versus representative family; preserve chosen image/finish. Missing or inaccessible image is explicit, never silently substituted |
| Evidence | Source file/hash/revision or URL, page/locator, retrieval date, observed value, uncertainty and override basis. Search snippets/training memory are leads, not verified specification fields |
| Source precedence | Explicit user corrections supersede prior inputs only within their stated scope. Manufacturer evidence generally describes products; a project quote/selection may govern actual price/configuration |

## Category methods

**Appliances:** identify full model/series and whether the line is the appliance, trim, panel, handle or installation kit. Keep electrical/connection and dimensional observations distinct from a determination of compatibility. A missing dishwasher/freezer drawer cannot be filled with a visually similar family product. Record capacity, handing, panel-ready status, included accessories and cutout dimensions only when sourced.

**Plumbing:** distinguish fixture, fitting, valve/body, trim, drain and accessory. Record selected finish/code separately from available finish range, and product-level versus finish-level grouping explicitly. A matching finish name does not prove matching manufacturer code. Rough-in and connection facts remain sourced observations; required components and compatibility require evidence.

**Finishes/textiles:** distinguish base material, applied finish/colorway, product pattern, size/thickness and sample versus orderable product. Record test/certification claims with their exact subject and source; a marketing claim is not a project compliance verdict. Retain declared units and the selected finish rather than normalizing to a family default.

**Furniture/modular systems:** distinguish family URL from a selected configuration, required components and upholstery/COM information. A sofa URL can be partially described while SKU and total price remain unresolved; no configuration engine is implied.

## Host source and workbook procedure

Use the host's browser/PDF/workbook tools and record their actual results. Read workbook headers, formulas, true hyperlink targets and embedded/linked images before proposing writes. Preserve unrelated cells and styling. Native backup/recoverable revision and validated CSV snapshots are complementary; CSV does not preserve a full workbook. Read back actual writes. Stop conflicts at reconciliation rather than replacing the entire workbook from an old snapshot.

Audit live claims require fresh retrieval in the current invocation; snapshot comparisons are explicitly historical. Sources that cannot be accessed stay unverified. Inspect rendered final PDFs and count expected versus actual tags; HTML and ready/download-link metadata are not evidence of valid PDF completion.

## Source basis

These methods are original AS operational conventions, derived from product-data contracts and observed source/template failure modes. Product facts must still be retrieved from the actual manufacturer document, user-selected workbook, quote or accepted reference for each task. See [product schema](../../../schema/product-schema.md), [CSV conventions](../../../schema/csv-conventions.md) and [shared architecture guidance](../../../docs/category-authoring.md). No customer data or licensed standards text is included here.
