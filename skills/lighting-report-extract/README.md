# Lighting report extraction

Read reported simulation results with exact surface names and physical/printed page evidence.

For requested quantities, keep luminaire inventory separate from calculation results. Repeated
surfaces do not add fixtures. The [observation contract](../../tools/transformers/evidence-contracts.md#lighting-inventory-and-calculation-results)
defines explicit source-backed inventory identities, unresolved/conflicting observations and host
verification. The host applies that contract natively to prepared observations with its own tools; no Arch Studio runner or package is required, and the extraction never adopts a schedule.
Use `/as:lighting-report-extract` or `$lighting-report-extract`. The host supplies PDF/OCR/inspection;
the result is not a new simulation, lighting design or code-compliance determination.
