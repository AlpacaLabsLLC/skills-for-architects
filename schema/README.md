# Data contracts

This directory owns the portable schemas shared by Arch Studio skills. The contracts are intentionally file-based and provider-independent.

| Contract | Purpose |
|----------|---------|
| [product-schema.md](./product-schema.md) | Canonical FF&E product fields and vocabulary |
| [epd-schema.md](./epd-schema.md) | Optional EPD library fields and provenance requirements |
| [csv-conventions.md](./csv-conventions.md) | CSV encoding, quoting, headers, and interoperability rules |
| [sif-crosswalk.md](./sif-crosswalk.md) | Mapping between the product CSV and SIF dealer interchange |

Skills should link to these files instead of reproducing field definitions. A contract change must update every affected producer, consumer, fixture, and validation test together.

- [Component schema](components.schema.json) defines stable IDs and canonical owners.
- [Cluster schema](clusters.schema.json) defines membership, coverage and evaluation evidence.

The dependency-free `tools/validators/validate-categories.py` validates the schema
vocabulary used here and cross-file ownership, references, cycles and discovery.
It is not a general-purpose JSON Schema implementation.

## FF&E project and output contracts

- [Record revisions](ffe-record.schema.json): authoritative adopted items and schedules, separately from the reusable CSV library.
- [Accepted intake](ffe-intake.schema.json): source hashes, corrections, selected scope and explicit adoption basis.
- [Product identity](product-identity.schema.json): exact 1–80 character product tags shared by intake and outputs; job IDs and safe PDF filenames remain separate.
- [Audit observations](ffe-audit.schema.json): supplied evidence comparison; the validator does not retrieve sources.
- [Output contract](ffe-output.schema.json) and [template contract](ffe-output-template.schema.json): revision-pinned host production and completeness checks.
  Version 2 records explicit filename mappings while preserving exact tags.

See the [record workflow](../studio/ffe/README.md) and [shared product methods](../corpus/practice-methods/ffe/README.md). These contracts do not introduce an Arch Studio spreadsheet or PDF rendering engine.

- [Resolved document design](document-design.schema.json): pinned central assets, override layers, physical page dimensions and size-aware layout parameters.
- [Lighting observations](lighting-report.schema.json): separate reported inventories and calculation results with source version, scoped identity and physical/printed locators; no PDF parsing or implicit legacy conversion.

## Current local operations and records

- [Operation request](operation.schema.json): closed named operation and exact package pin.
- [Documents](documents.schema.json): new-model registered document identity and provenance; [workspace model](../docs/workspace-model.md) owns current writer and CSV semantics.
