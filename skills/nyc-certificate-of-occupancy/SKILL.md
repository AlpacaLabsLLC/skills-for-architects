---
name: nyc-certificate-of-occupancy
description: "Retrieve NYC Certificate of Occupancy evidence for an identified property. Use for \"certificate of occupancy or legal use by floor\"; not for infer legal occupancy from PLUTO, a permit, or absence of a search result."
allowed-tools:
  - Read
  - Bash
  - WebFetch
---

# /as:nyc-certificate-of-occupancy

<!-- architecture-studio:harness-compatibility -->
> Harness note: use `/as:<skill>` on Claude Code and `$<skill>` on Codex. Resolve `<skill-root>` as the directory containing this loaded `SKILL.md` and `<plugin-root>` as the plugin root that contains `skills/`, and use equivalent native tools when host tool names differ.

Retrieve NYC Certificate of Occupancy evidence for an identified property. This is a read-only lookup, not professional approval.

## Contract

- **Input:** Address and borough or BIN/BBL; certificate/date if known.
- **Primary output:** Property-specific occupancy-record evidence.
- **Source dependencies:** `source:nyc-certificate-of-occupancy`.
- **Coverage:** N13; NYC scope with explicitly linked state/federal dependencies.
- **Not this operation:** Infer legal occupancy from PLUTO, a permit, or absence of a search result.

## Procedure

1. Extract the stated input. Ask only for a missing value that materially prevents this lookup. An identified-section request does not require a studio, project, address or folder grant. Do not assume an edition or extend NYC coverage to another jurisdiction.
2. Read [the shared lookup procedure](../../corpus/jurisdictions/us/ny/nyc/local-procedures/lookup.md) completely, then load the named source records from [the canonical source index](../../corpus/sources/catalog.json). Retain the AS release digest separately from external source version/hash. Read only the relevant referenced records.
3. Match address/borough and BIN or BBL, document identifier, issue/amendment date and floor/use exactly. If the official record cannot be retrieved, report unavailable; no record found is not proof no certificate exists. Never infer the certificate from PLUTO or filed-work records.
4. Execute the shared lookup for the selected registered source and provision when a permitted route exists. Follow the receipt's completeness and identity results; unavailable, metadata-only, edition-uncertain or incomplete retrieval must stay visible. Do not fill missing regulatory text from memory or an unrelated source.
5. Return the primary output inline with source ID, publisher, source kind, edition/date status, section/locator and official link, retrieval timestamp/hash when available, and unresolved applicability conditions. State actual AS/native tools called and whether a provision or only navigation/metadata was retrieved. Do not calculate, approve a product or mutate project records. Saving evidence is a separate user-requested governed workflow.

## Regulatory output

End every report with this block and marker:

> **Disclaimer:** This is an AI-generated analysis for preliminary planning purposes. All findings must be verified by a licensed professional before use in design, permitting, or regulatory submissions.

<!-- architecture-studio:requires-disclaimer -->
