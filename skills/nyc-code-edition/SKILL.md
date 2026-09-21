---
name: nyc-code-edition
description: "Find evidenced NYC code-edition candidates for one regime and project timeline. Use for \"which NYC code edition applies\"; not for set one global NYC code year or choose newest by default."
allowed-tools:
  - Read
  - Bash
  - WebFetch
---

# /as:nyc-code-edition

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

Find evidenced NYC code-edition candidates for one regime and project timeline. This is a read-only lookup, not professional approval.

## Contract

- **Input:** Regime; filing/work dates and existing-building facts if known.
- **Primary output:** Edition-candidate evidence with unresolved applicability.
- **Source dependencies:** `source:nyc-construction-codes`, `source:nyc-existing-building-code`, `source:nyc-electrical-code`, `source:nyc-energy-code`, `source:nyc-fire-code`.
- **Coverage:** N12; NYC scope with explicitly linked state/federal dependencies.
- **Not this operation:** Set one global NYC code year or choose newest by default.

## Procedure

1. Extract the stated input. Ask only for a missing value that materially prevents this lookup. An identified-section request does not require a studio, project, address or folder grant. Do not assume an edition or extend NYC coverage to another jurisdiction.
2. Read [the shared lookup procedure](../../corpus/jurisdictions/us/ny/nyc/local-procedures/lookup.md) completely, then load the named source records from [the canonical source index](../../corpus/sources/catalog.json). Retain the AS release digest separately from external source version/hash. Read only the relevant referenced records.
3. Separate enacted, published and effective dates. Build candidates separately for the requested regime; if filing/work dates or transition conditions are missing, ask the one material question or leave applicability unknown. Never resolve code applicability from the server's AS version.
4. Execute the shared lookup for the selected registered source and provision when a permitted route exists. Follow the receipt's completeness and identity results; unavailable, metadata-only, edition-uncertain or incomplete retrieval must stay visible. Do not fill missing regulatory text from memory or an unrelated source.
5. Return the primary output inline with source ID, publisher, source kind, edition/date status, section/locator and official link, retrieval timestamp/hash when available, and unresolved applicability conditions. State actual AS/native tools called and whether a provision or only navigation/metadata was retrieved. Do not calculate, approve a product or mutate project records. Saving evidence is a separate user-requested governed workflow.

## Regulatory output

End every report with this block and marker:

> **Disclaimer:** This is an AI-generated analysis for preliminary planning purposes. All findings must be verified by a licensed professional before use in design, permitting, or regulatory submissions.

<!-- architecture-studio:requires-disclaimer -->
