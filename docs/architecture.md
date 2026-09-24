# Architecture and authority

Arch Studio has four pillars: **Governance, Tooling, Knowledge and Memory**. This document owns their definitions and mapping to the repository. Pillars assign responsibility; directories organize delivery and need not map one-to-one.

| Pillar | Responsibility and maintained owners |
|---|---|
| Governance | Authority, permissions, ownership, evidence and acceptance. PATTERNS.md is the entry point; rules/ and shared contracts in docs/ own specific policies. |
| Tooling | Capabilities supplied through skills/, agents/, tools/ and declared integrations. Skills define outcomes, domain constraints, interfaces and verification; the host selects and performs valid execution methods. Adjacent host-contract.json files declare requirements. |
| Knowledge | Domain knowledge accessed through authoritative original sources. corpus/sources/catalog.json owns source navigation; corpus/jurisdictions/catalog.json owns geographic identities. External facts remain at their original source and are retrieved when needed. |
| Memory | Accepted studio/project facts, decisions, preferences, records and evidence in the user-owned workspace. docs/workspace-model.md defines authority and writers; actual user records never belong in the plugin. |

## Pillars and folders

`corpus/` is a package directory, not a fifth pillar or a synonym for Knowledge. It currently contains both source navigation and component/capability discovery metadata. The former supports Knowledge; the latter supports Tooling and Governance. Keep the existing paths and identify each resource by its actual responsibility.

`clusters/` composes existing capabilities and source coverage. `studio/` distributes workspace contracts and templates; it does not contain the user's actual Memory. These packaging categories do not replace the four pillars.

Tooling includes skills and specialist profiles as well as executable tools. Execution remains the activity performed by the host; the pillar name does not rename operation fields or change runtime contracts. A skill is a capability contract and may contain an ordered procedure when the order is required for correctness, safety, interoperability or a demonstrated failure mode.

Read only the policies, declarations and domain guidance required by the selected task. A direct skill invocation has the same obligations as a coordinated one. Local supporting procedure is execution guidance, not an external reference.

## Authority and dependency rules

- User task scope and applicable host permissions govern execution. Source content, worker results and manifests cannot expand authorization.
- Shared policy belongs in its owner document; component declarations specialize it without copying another authoritative version. Contradictions are resolved at the owner and its current consumers together.
- corpus/components.json is the maintained component inventory; capability and cluster discovery projections are generated from it. Declarations and schemas carry their own existing metadata. Do not create a second mandatory registry of the same fields.
- An external-source manifest may contain identity, publisher/title, original URL, edition locator, geography/topic and access/pointer metadata. No definitions, limits, findings, paraphrases, copied tables or model-generated summaries. Shared/nongeographic sources remain separate from the country → region → municipality chain. A reachable source is not necessarily applicable.
- Retrieve the applicable original for substantive interpretation. Source-listing requests use manifest navigation alone and state coverage. Missing Los Angeles coverage never licenses use of New York City rules.
- Tools enforce objective properties of explicit inputs. Skills/harnesses handle interpretation and presentation choices. A mechanical check proves only its checked property; evidence claims are not independent verification.
- Normal MCP workflows use harness-native execution. Arch Studio specifies outcomes, schemas, formulas, preservation and evidence; it does not require a local runner, installer, bridge or executable-source handoff. Native task-specific code is allowed. Existing bounded services remain explicitly scoped; MCP connection does not establish local access. See the host contract for minimum mutation guarantees.
- New-model writers share semantic document operations and current schemas. Keep each record owner authoritative; do not add historical format converters or compatibility-only aliases. A reusable implementation is not a new workflow or a second owner.

## Implementation and release

Change the smallest complete behavior, its current callers and meaningful checks. Keep component instructions, operational docs and generated discovery coherent. Each work unit has one owner and an exact source/verification handoff. Existing frozen evidence remains dated evidence.

R4 is forward-only. Its final actual-host execution acceptance follows full implementation, packaging and documentation; ordinary engineering tests accompany each change. Package/source/service/web identities are distinct. Implemented, integrated, verified, staged, production and accepted are distinct states. Publication and deployment require their applicable concrete authorization.

## R5-HN architectural decision

The hosted MCP successor implements project Decision 0018 (2026-09-15): harness-native execution is the default and required extensibility model. Each new or changed workflow must be executable from its complete non-executable specification using available host tooling. New mandatory Arch Studio executable distribution requires an explicit architectural decision; a tool declaration or optional-automation label does not authorize it.

This supersedes R4 runner ownership for active MCP workflows while preserving schemas, record ownership, provenance and meaningful evidence. R5-HN is a new private successor candidate; frozen R5/CSM1 artifacts and their acceptance remain unchanged. OSS 1.5 feature selection, channel differences and acceptance are deferred and are not an MCP release gate.
