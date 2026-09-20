# NYC property identity procedure

Before querying, use the [geographic contract](../../docs/geographic-applicability.md) and the selected skill's [declaration](../../corpus/geographic-applicability.json). Require a resolved NYC target from supplied or relevant project evidence. A bare numeric identifier or studio default does not resolve a contradictory/missing jurisdiction. One-off lookups need no project setup.

Accept the supplied address, parcel/building identifier or exact selected source record. Use the PLUTO and Building Footprints routes in the [source catalog](../../corpus/sources/catalog.json); retrieve their current original metadata before interpreting identifiers, columns, normalization or relationships. Use the [query procedure](socrata-reference.md). Preserve the original input and matched source identity.

Try the most specific supplied identity first. Normalize only according to verified source requirements. An address match may be ambiguous; present candidate identities and ask for the material choice. Do not silently merge multiple lots/buildings or pick a first match. Resolve the selected parcel/building relationship from actual publisher fields and retain multiple mappings if the requested scope includes them. Missing or conflicting evidence leaves the identity unresolved. Collect only fields relevant to the requested report.
