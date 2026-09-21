# Code & Regulatory routing

Studio remains the dispatcher. This reference maps the user's one requested operation to an atomic card; it does not execute a new agent. Coverage is NYC plus explicitly linked federal/state records, not a generic world-code database.

## First decision

- Unknown/non-NYC jurisdiction: ask the material location question or report missing maintained coverage. Do not apply NYC provisions in Dubai or Montevideo. Federal ADA is separately US-scoped.
- Authority question → `nyc-authority-resolver`; edition/applicability timeline → `nyc-code-edition`; exact provision across a known regime → `nyc-code-section`; amendments → `nyc-amendment-check`; incorporated standard edition → `nyc-referenced-standard`.
- Named family/topic → the matching card below. A specifically named family takes precedence over the general section helper. Do not invoke every lookup in the cluster.

## Atomic intent map

| Coverage | Card | Primary result |
|---|---|---|
| N01 | `nyc-building-code` | Building-code provision evidence |
| N01 | `nyc-existing-building-code` | Existing-building provision evidence |
| N01 | `nyc-plumbing-code` | Plumbing provision evidence |
| N01 | `nyc-mechanical-code` | Mechanical provision evidence |
| N01 | `nyc-fuel-gas-code` | Fuel-gas provision evidence |
| N01 | `nyc-construction-administration` | Administrative provision evidence |
| N02 | `nyc-electrical-code` | Electrical provision evidence |
| N03 | `nyc-fire-code` | Fire Code provision evidence |
| N03 | `nyc-fdny-rule` | FDNY rule evidence |
| N04 | `nyc-energy-code` | Energy Code provision evidence |
| N04 | `nyc-ll97-applicability` | LL97 applicability evidence with unresolved conditions |
| N04 | `nyc-emissions-limit` | Emissions-limit citation, unit and period |
| N05 | `nyc-zoning-provision` | Zoning provision evidence |
| N06 | `nyc-housing-maintenance` | Housing Maintenance Code provision evidence |
| N06 | `nyc-multiple-dwelling-law` | State-owned MDL provision evidence |
| N07 | `nyc-noise-requirement` | Noise requirement evidence |
| N07 | `nyc-asbestos-requirement` | Asbestos procedural requirement evidence |
| N07 | `nyc-air-emissions-requirement` | Air-emissions requirement evidence |
| N07 | `nyc-stormwater-requirement` | Stormwater requirement evidence |
| N07 | `nyc-sewer-requirement` | Sewer requirement evidence |
| N07 | `nyc-hazardous-material-requirement` | Authority-qualified hazardous-material requirement evidence |
| N08 | `nyc-accessibility-requirement` | NYC accessibility provision evidence with separate federal pointer |
| N08 | `ada-requirement` | Federal ADA provision evidence |
| N09 | `nyc-lpc-requirement` | LPC requirement evidence |
| N10 | `nyc-sidewalk-requirement` | Sidewalk requirement evidence |
| N10 | `nyc-curb-cut-requirement` | Curb-cut requirement evidence |
| N10 | `nyc-plaza-requirement` | Program-qualified plaza requirement evidence |
| N10 | `nyc-street-tree-requirement` | Street-tree requirement evidence |
| N10 | `nyc-utility-connection-requirement` | Water-connection requirement evidence |
| N11 | `nyc-material-requirement` | Application-qualified material requirement evidence |
| N11 | `nyc-interior-finish-requirement` | Interior wall/ceiling finish requirement evidence |
| N11 | `nyc-floor-finish-requirement` | Floor-finish requirement evidence |
| N11 | `nyc-furnishing-requirement` | Furnishing requirement evidence |
| N11 | `nyc-drapery-requirement` | Drapery requirement evidence |
| N12 | `nyc-local-law` | Identified Local Law evidence |
| N12 | `nyc-agency-rule` | Identified agency-rule evidence |
| N12 | `nyc-buildings-bulletin` | Buildings Bulletin evidence and document classification |
| N12 | `nyc-code-note` | Code Note guidance evidence |
| N12 | `nyc-executive-order` | Executive-order evidence and scope unknowns |
| N13 | `nyc-certificate-of-occupancy` | Property-specific occupancy-record evidence |
| N12 | `nyc-authority-resolver` | Candidate-authority map with triggers and unknowns |
| N12 | `nyc-code-edition` | Edition-candidate evidence with unresolved applicability |
| N12 | `nyc-code-section` | Identified provision evidence |
| N12 | `nyc-amendment-check` | Bounded amendment evidence and search limitations |
| N11 | `nyc-referenced-standard` | Referenced-standard metadata and authorized access route |

## Preserve adjacent owners

- Address-specific ACRIS, DOB permits/violations, HPD violations/complaints, BSA relief and LPC designation remain `nyc-acris`, `nyc-dob-permits`, `nyc-dob-violations`, `nyc-hpd`, `nyc-bsa`, `nyc-landmarks`; aggregate due diligence stays `nyc-property-report`.
- Buildable-area analysis remains `zoning-analysis-nyc`; visualization remains `zoning-envelope`. An exact ZR provision goes to `nyc-zoning-provision`, not a full feasibility exercise.
- Occupant-load calculation remains `occupancy-calculator` with its own jurisdiction and factor-verification gate. A lookup does not perform or validate that calculation.
- Outline specs remain `spec-writer`; EPD language stays `epd-to-spec`; product evidence/audit stays with FF&E. This cluster does not approve products or compare submitted test data against requirements.

## High-confusion distinctions

Hanging curtains/decorative textiles → drapery; wall/ceiling attached finishes → interior finish; carpet/flooring → floor finish; loose/upholstered furniture → furnishing. Ask the application question if the material name alone is ambiguous. Do not default all textiles to NFPA 701 or all finishes to ASTM E84. Determine the referenced test and edition from the controlling provision.

DOT pedestrian plazas and zoning privately owned public spaces require distinct source routes. NYC accessibility and federal ADA do not replace each other. DEP water-connection coverage does not imply private utility coverage. LL97 applicability screening, published limit lookup and emissions calculation are distinct; only the first two are provided here.

## Required result discipline

Use [lookup.md](lookup.md) and preserve unavailable, metadata-only, edition-uncertain and incomplete outcomes. A known source is not proof the requirement applies. No folder setup is required for public conversational lookup. Fixture expectations are in `tests/fixtures/nyc-code-routes.json`; they are not evidence that a host was tested.
