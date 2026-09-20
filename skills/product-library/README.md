# Product Library

Owns the reusable 33-column `product-library.csv` and local transaction receipts. It previews exact
changes, preserves user fields, rejects stale hashes, and recovers interrupted requests without
duplicating successful saves. Adopted schedules remain owned by master-schedule.

Invoke `$product-library` on Codex or `/as:product-library` on Claude Code. Follow the skill's native product-library operation contracts and current schemas with the host's available tools; no runner is required. See [the skill](SKILL.md) for the
preview/request-ID contract and cooperating-writer concurrency limitations.
