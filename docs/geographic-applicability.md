# Practice areas and geographic applicability

Architectural direction adopted 2026-09-07 by Federico Negro in Architecture Studio project
decision 0003, “Separate practice areas from geographic applicability.” This document defines
the target contract; it does not claim that all catalog metadata or runtime checks implement it.

## Independent dimensions

Practice areas classify **what work is requested**. Geography constrains **which procedures
and evidence apply**. Storage paths alone enforce neither.

| Layer | Responsibility |
|---|---|
| Project or one-off request | Sourced site location, known jurisdictions and material use/work/date context |
| Reference | Authority, jurisdiction, spatial coverage, edition, effective dates and access limitations |
| Skill | Narrow procedure, supported geography, required context and unsupported-case behavior |
| Tool | Stable capability contract, geographic/input limits and applicability checks appropriate to its operation |
| Practice-area catalog | Primary discovery home plus explicit coverage, dependencies and validation evidence |

Studio defaults do not establish site applicability. One-off work need not create a project.
Internal projects need no invented site or jurisdiction. Multi-site work must distinguish
the locations and findings rather than infer one global jurisdiction for the entire project.

## Packaging and reference organization

- Keep public skills at `skills/<name>/`; preserve stable tool identities in the registry.
  Existing tool implementation directories may remain organized by technical responsibility.
- Organize jurisdiction-dependent references through the existing [geographic corpus](../corpus/jurisdictions/README.md)
  and [source catalog](../corpus/sources/catalog.json). Shared standards and general methods
  remain separately owned; refer to canonical records rather than copying their contents.
- Geographic nesting conveys organization, not legal precedence or automatic applicability.
  Federal, state and local provisions may all matter; a standard's publication does not prove adoption.
- A location-independent method does not imply worldwide data availability. Solar calculation
  and jurisdiction-specific flood mapping have different coverage contracts.

## Practice-area boundaries

| Primary area | Owns | Does not substitute for |
|---|---|---|
| Site Analysis | Physical/environmental conditions, mobility and contextual investigation | Regulatory requirements or professional site investigations |
| Property Due Diligence | Ownership, permits, occupancy records, violations and property-specific restrictions | General code applicability or design approval |
| Code & Regulatory | Authorities, editions, provisions, requirements and bounded regulatory analysis | Verified existing conditions or a compliance certification |

Give each skill one primary discovery home and allow secondary cross-references. Do not duplicate
skills to achieve multiple discovery views. Zoning analysis belongs primarily to Code & Regulatory;
property-specific relief records belong primarily to Property Due Diligence. A flood map is site
evidence; flood-resistant construction provisions are regulatory evidence.

## Execution contract

1. Resolve the requested work and project/request location when geography is material.
2. Identify other material applicability inputs: dates, use, work scope and source coverage.
3. Select a supported skill/tool and relevant authorities. Ask for missing material inputs;
   do not assume that the latest edition or deepest geographic folder governs.
4. Retrieve evidence and check its spatial, temporal and substantive applicability.
5. Report sources, limitations and unresolved applicability. Distinguish unknown, unsupported,
   unavailable, and evidence of absence. Never substitute NYC rules for an unsupported location.
6. Route explicitly authorized persistence through the owning project-record skill.

Enforce deterministic geographic constraints in tools where available and retain procedural
checks in skills. Do not trust a model's routing choice alone. Metadata/source discovery,
successful retrieval, applicable evidence and validated workflows are separate states.

## Compatibility and implementation status

The current [cluster guide](practice-clusters.md) describes the existing manifests, not this
completed target. Existing `Site & Zoning` naming and overlapping memberships remain pending
alignment. Do not hand-edit that generated guide; change its source manifests/generator together.

Follow-on work must implement primary/secondary membership, machine-readable applicability,
routing and negative tests, and regenerate OSS/MCP catalogs. Preserve public names and inputs,
existing project IDs and user records. Do not silently drop explicit save requests when a
parser delegates persistence to its owner. No workspace migration is authorized by this contract.

Required acceptance examples include: a one-off request without a project; an NYC request needing
federal/state/local evidence; a Maldonado request that cannot use NYC procedures; a missing or
ambiguous location; a future-effective edition; and a portable calculation with no jurisdictional
data dependency. Documentation alone does not pass these checks.
