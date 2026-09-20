# External-source navigation contract

`corpus/sources/catalog.json` is the only editable external-source authority. It is metadata, never reference content. `schema/source-catalog.schema.json` defines its shape. `corpus/jurisdictions/catalog.json` holds geographic parent identities; `tools/integrations/catalog.json` holds execution adapters, not another source registry.

## Metadata and geography

A source has one stable ID, publisher authority, title, original URL, known edition/date locators, access conditions, topic selectors and current skill consumers. Supplemental locators identify original metadata, historical editions or access pages. Unknown metadata stays null/unknown; a recorded date is not a declaration that the edition controls a project. No definitions, research findings, regulatory tables, derived datasets, field dictionaries or copied vendor manuals are allowed.

Jurisdiction IDs follow the country → state/region → municipality hierarchy. Shared/nongeographic sources have null jurisdiction; this does not mean universally applicable. NYC sources live under US → New York State → New York City. LA has no registered coverage; report that gap without substituting NYC. Directory grouping is not legal precedence. A source can be found through several topics without copying its identity.

## Directory and substantive requests

For “list all NYC code sources,” filter registered source metadata for NYC and code/zoning topics; label related mapping/data routes and state/federal/shared routes separately. Deduplicate IDs and state that “all” covers the matching available Arch Studio manifest entries, not every authority in NYC. Do not fetch content, infer current applicability or create records for a directory-only answer. Missing manifests reduce reported coverage.

For interpretation, retrieve the applicable original or authorized user-supplied document. Verify jurisdiction, date, edition, adoption/amendments and task scope from it. Cite actual source/section/version used. Keep evidence in task memory outside the plugin. Inaccessible or uncertain originals leave dependent conclusions unresolved. Model memory, snippets and local summaries are not substitutes.

## Pointer checks

A source may have a declared adapter and identity probe; directory-only entries have null adapter/identity. `source-health.mjs` validates the manifest and performs only explicitly requested supported checks with bounded requests. Pointer-only sources remain unknown with no fabricated check. Reachability and marker matching establish neither source truth, source currency, legal applicability nor host workflow execution. Check metadata is dated evidence, not content.

Source relationships are navigation-only published-by/references links backed by original URLs. Legal adoption, amendment or supersession is established at task time from originals, not an asserted local relationship graph. Schemas and Arch Studio-authored procedures remain local implementation assets. Synthetic fixtures must not reproduce an external table under another label.
