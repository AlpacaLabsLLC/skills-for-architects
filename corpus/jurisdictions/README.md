# Geographic source ownership

Authored source, authority and jurisdiction records live under their maintained
geography. `catalog.json` here and `../sources/catalog.json` are generated indexes,
not independent authoring locations. Stable IDs survive file moves.

Run `node tools/integrations/geographic-catalog.mjs --write` after an intentional
record edit, and `--check` in review/CI. The generator rejects duplicate identities,
unresolved jurisdiction/authority/adapter references and circular precedence.
Do not infer geographic coverage from a directory: source receipts and the
Code & Regulatory coverage ledger describe supported operations and limitations.

Records are original source maps, not a redistributed legal corpus. Null dates
and pending review mean unknown, not current or approved. Effective edition is
regime- and project-specific; enacted and effective are separate events.
Public reachability is neither permission to redistribute nor legal authority.
