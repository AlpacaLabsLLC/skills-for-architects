---
name: nyc-mechanical-code
description: "Find a provision in an identified NYC Mechanical Code edition. Use for \"mechanical-code requirement\"; not for design HVAC or calculate ventilation rates."
allowed-tools:
  - Read
  - Bash
  - WebFetch
---

# /as:nyc-mechanical-code

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

Find a provision in an identified NYC Mechanical Code edition. This is a read-only lookup, not professional approval.

## Contract

- **Input:** Edition and provision or mechanical topic.
- **Primary output:** Mechanical provision evidence.
- **Source dependencies:** `source:nyc-mechanical-code`.
- **Coverage:** N01; NYC scope with explicitly linked state/federal dependencies.
- **Not this operation:** Design HVAC or calculate ventilation rates.

## Procedure

1. Extract the stated input. Ask only for a missing value that materially prevents this lookup. An identified-section request does not require a studio, project, address or folder grant. Do not assume an edition or extend NYC coverage to another jurisdiction.
2. Read [the shared lookup procedure](../../corpus/jurisdictions/us/ny/nyc/local-procedures/lookup.md) completely, then load the named source records from [the canonical source index](../../corpus/sources/catalog.json). Retain the AS release digest separately from external source version/hash. Read only the relevant referenced records.
3. Use the named source dependencies to locate the requested topic or provision. Preserve the source's document kind and edition; guidance, property evidence and enacted law are not interchangeable. An index is a navigation result, not the requested provision.
4. Execute the shared lookup for the selected registered source and provision when a permitted route exists. Follow the receipt's completeness and identity results; unavailable, metadata-only, edition-uncertain or incomplete retrieval must stay visible. Do not fill missing regulatory text from memory or an unrelated source.
5. Return the primary output inline with source ID, publisher, source kind, edition/date status, section/locator and official link, retrieval timestamp/hash when available, and unresolved applicability conditions. State actual AS/native tools called and whether a provision or only navigation/metadata was retrieved. Do not calculate, approve a product or mutate project records. Saving evidence is a separate user-requested governed workflow.

## Regulatory output

End every report with this block and marker:

> **Disclaimer:** This is an AI-generated analysis for preliminary planning purposes. All findings must be verified by a licensed professional before use in design, permitting, or regulatory submissions.

<!-- architecture-studio:requires-disclaimer -->
