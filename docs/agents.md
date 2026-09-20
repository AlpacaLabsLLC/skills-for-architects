# Specialist profiles

Arch Studio retains seven specialist profiles and one optional Norma worker. They help an available host coordinate
multi-step work using the same owning skills. A profile is not an independent service, model,
background agent or permission grant. Native registration and delegation depend on the host
and must be observed; package presence alone is not proof.

The harness may select a domain skill directly. Norma coordinates substantial multistep work with workplan, presents a concrete plan and useful team assignments, and preserves existing authorization. It does not add a plan gate to quick tasks. When the host exposes delegation and
the request permits it, Norma may use one of these profiles with the same scope, source
identities, unresolved facts, outputs, validation state and authorization. Otherwise the host
follows the relevant skills directly. Direct skill calls and existing profile names remain valid.

## Available profiles

| Agent | Domain | Skills it orchestrates |
|-------|--------|----------------------|
| [site-planner](../agents/site-planner.md) | Site Planning | environmental-analysis, mobility-analysis, demographics-analysis, site-history |
| [nyc-zoning-expert](../agents/nyc-zoning-expert.md) | Due Diligence + Zoning | nyc-landmarks, nyc-dob-permits, nyc-dob-violations, nyc-acris, nyc-hpd, nyc-bsa, nyc-property-report, zoning-analysis-nyc, zoning-envelope |
| [workplace-strategist](../agents/workplace-strategist.md) | Programming | occupancy-calculator, workplace-programmer |
| [sustainability-specialist](../agents/sustainability-specialist.md) | Sustainability | epd-research, epd-compare, epd-parser, epd-to-spec |
| [product-and-materials-researcher](../agents/product-and-materials-researcher.md) | Materials Research | product-research, product-spec-bulk-fetch, product-spec-pdf-parser, product-match, product-enrich |
| [ffe-designer](../agents/ffe-designer.md) | FF&E Design | product-pair, product-data-cleanup, product-data-import, product-enrich, product-image-processor, csv-to-sif, sif-to-csv |
| [brand-manager](../agents/brand-manager.md) | Presentations | slide-deck-generator, color-palette-generator, resize-images |

| [norma](../agents/norma.md) | Optional Claude Code worker | Executes an already resolved authorized assignment; returns questions to the main harness |

## Scope and completion

Read the profile's declaration and selected skill references. Listed skills describe its domain;
they are not an automatic full pipeline. A request for a product comparison does not authorize
library adoption, a project record change or a presentation. Necessary dependencies within an
already authorized deliverable remain part of that work.

The host remains responsible for actual tool access and permissions. Specialists return sourced
results and precise incomplete work; Norma continues the authorized task and gives a coherent
answer. Retrieval and typed proposals do not prove execution or factual accuracy. Every canonical
write stays with its skill owner, and every output needs that owner's validation.

Studio retains workspace administration and forwards other architecture-task requests once to
Norma. Naming an agent or using a legacy studio route never creates credentials, independent
memory, a hosted service or outbound-message authority.

A disclosed team exists only after the harness successfully creates its agents through exposed tools. If creation fails or is unavailable, report that before claiming team execution; continue only within the actual authorized capabilities. The optional Norma worker never runs onboarding or asks the user directly.
