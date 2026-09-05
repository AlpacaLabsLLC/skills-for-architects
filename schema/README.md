# Data contracts

This directory owns the portable schemas shared by Architecture Studio skills. The contracts are intentionally file-based and provider-independent.

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
- [Audit observations](ffe-audit.schema.json): supplied evidence comparison; the validator does not retrieve sources.
- [Output contract](ffe-output.schema.json) and [template contract](ffe-output-template.schema.json): revision-pinned host production and completeness checks.

See the [record workflow](../studio/ffe/README.md) and [shared product methods](../corpus/practice-methods/ffe/README.md). These contracts do not introduce an AS spreadsheet or PDF rendering engine.
