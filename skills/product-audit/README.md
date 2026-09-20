# Product audit

Compare one product or an FF&E selection against explicitly sourced observations. Findings distinguish discrepancies, inaccessible sources, unknown values and stale evidence while preserving current records.

Use `$product-audit` on Codex or `/as:product-audit` on Claude Code. Supply an item/schedule and choose current-source checking or an explicitly labeled saved-snapshot comparison. The skill can save a revision-linked audit report; corrections remain owned by master-schedule.

The host performs the comparison natively under the [audit contract](../../tools/validators/ffe-audit-contract.md) with its own available tools; no Arch Studio runner or package is required. The audit does not edit specifications or certify compliance. The host must retrieve and inspect evidence for a live audit.
