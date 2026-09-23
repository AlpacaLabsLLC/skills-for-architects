# Terminology

This rule governs style and first-use, not factual definitions. For neutral professional-practice terms, AIA document-family orientation, document purpose, and source boundaries, use [architecture-knowledge](../skills/architecture-knowledge/SKILL.md) and its applicable original-source routes. No local definitions are a reference authority.

## Product name

The product is **Arch Studio** in every sentence, on every channel. Do not use "Architecture Studio" or "AS" as the product name in prose. Identifiers keep their technical form: the plugin `as@skills-for-architects`, commands `/as:<skill>` and `$<skill>`, tools `as_<name>`, the `.as-folder.json` record, the `as` monogram, repository and folder names. Release labels read "Arch Studio 1.5". The word "Studio" alone means the user's workspace, never the product.

**Why:** three names for one product read as three products. Lint rejects the two retired forms outside identifiers and the license text.

## Skill, workflow and tool

- A **skill** is procedural instructions for one bounded outcome, performed by the assistant with its available host capabilities. Hosted delivery exposes each skill through an `as_<name>` MCP entry point; plugin invocation uses the host’s skill syntax. The canonical catalog currently contains 61 skills.
- A product **tool** means a server-side deterministic operation, planned for 1.6 or later; 1.5.1 does not add these operations. Current MCP skill entry points such as `as_<skill>` deliver instructions; existing status, resource and validation utilities retain their separate contracts. Native host tools, `allowed-tools`, helper paths under `tools/` and persisted `tools-only` identifiers retain their technical meanings and names.
- A **workflow**, on the framework pages (architecturestudio.ai/framework/execution) and in customer-facing copy, names a distinct, smaller feature: a skill that sequences other skills, with a typed handoff between steps ("a skill that sequences other skills"). This is a different, much smaller count (7 at last count) than the skill catalog. Do not use "workflow" as a plain synonym for "skill".
- **"Workflow instructions"** is the MCP delivery mechanism for any skill (see [host-harness contract](../docs/host-harness-contract.md)); it does not imply composition. Release-ledger and catalog fields named `workflows` (for example `counts.workflows`) count entries at this delivery layer, which today happens to equal the skill count. Do not present that field as the composed-Workflows feature count, or the reverse.

**Why:** the release ledger, PATTERNS.md's own prose, and the site's Workflows feature page each use "workflow" for a different thing, with no cross-reference between them. A release-notes author or a reader cannot tell which is meant without checking three separate places, and every ambiguous use so far has produced a wrong published number.

## Specification deliverable names

These are Arch Studio routing terms, not definitions of professional standards:

- **Project Manual section:** design/performance, submittal and execution requirements; `spec-writer` owns the section and `epd-to-spec` owns its EPD/GWP requirements.
- **Product cut sheet / FF&E spec book entry:** source-faithful facts for one selected product from a supplied PDF or URL; `product-cut-sheet` owns the entry.
- **FF&E specification book:** the agreed ordered set of product entries; `ffe-spec-book` owns assembly and package receipts.

When “specification” or “spec book” is ambiguous, resolve the requested deliverable from its inputs and purpose before choosing a skill. Persisted document kind `spec-book` and its template/receipt identities remain unchanged.

## Word choice

Use precise language appropriate to the reader and preserve the user’s project vocabulary. Retrieve original definitions when a professional term’s meaning affects the requested conclusion. Style preferences do not establish technical equivalence or a regulatory definition.

## First use

- Define an abbreviation on first use, then use it consistently.
- Do not assume the reader knows an abbreviation.
- Domain-specific abbreviations such as FAR, FOS, FOT, NSF, USF, and RSF must always be defined on first use.
- Preserve a user-supplied term when it is the name of a project record, product, or organization.

## Style

- Prefer clear generic names over informal shorthand unless the user requests the shorthand.
- Identify proprietary names as supplied; do not silently treat a brand name as a generic requirement.
- Capitalize proprietary names and lowercase their generic equivalents.
- Do not turn generic terminology into a project fact, a contract interpretation, a regulatory conclusion, or a permission to act.

## Numeric Style

- Spell out one through nine in prose; use numerals for 10 and above
- Always use numerals in tables, dimensions, and technical data
- Use numerals with units: "4 SF", "6 LF", "3 stories"
