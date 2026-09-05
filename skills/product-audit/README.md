# Product audit

Compare one product or an FF&E selection against explicitly sourced observations. Findings distinguish discrepancies, inaccessible sources, unknown values and stale evidence while preserving current records.

Use `$product-audit` on Codex or `/as:product-audit` on Claude Code. Supply an item/schedule and choose current-source checking or an explicitly labeled saved-snapshot comparison. The skill can save a revision-linked audit report; corrections remain owned by master-schedule.

The [comparison helper](../../tools/validators/ffe_audit.py) uses Python's standard library. It does not fetch sources, edit specifications, or certify compliance. The host must retrieve and inspect evidence for a live audit.
