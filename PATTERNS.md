# Arch Studio extension patterns

Start with the [architecture and authority map](docs/architecture.md), the owner of the four pillars — Governance, Tooling, Knowledge and Memory — and their folder mapping. Use it to find the owner of the policy needed for the task; do not load the whole repository.

## Skill, tool, source or record

- A **skill** owns one bounded outcome and the domain knowledge, constraints, interfaces and verification needed to achieve it. Give the host room to choose valid methods. Include ordered procedure only when sequence is required by a domain rule, interoperability contract, safety constraint or observed failure. A meaningful multistep procedure can invoke several owners with explicit handoffs; do not split useful procedures merely to satisfy a verb or line-count quota. "Workflow" is a distinct, defined term (see [terminology](rules/terminology.md#skill-workflow-and-tool)); do not use it as a synonym for "skill" or "procedure" here or elsewhere.
- A product **tool** is a server-side deterministic operation planned for 1.6 or later. Current MCP skill entry points deliver instructions; existing status, resource and validation utilities, native host tools and maintainer helpers retain their distinct technical contracts. No server-side execution is added in 1.5.1.
- An **operation** names bounded semantic work with explicit inputs/results, preservation, failure and retry requirements in its owning specification. Native host tools perform it; no matching Arch Studio function or dispatcher is required. Maintainer tooling has declared dependencies and meaningful fixtures, without becoming a customer runtime requirement. Validate prepared changes before writes and make repeats safe.
- **External references stay external.** Maintain navigation metadata in the [source catalog](corpus/sources/catalog.json), not local copies, summaries, paraphrases, rule tables, findings or alternate versions. This applies in skills, agents, schemas, examples, defaults and fixtures as well as corpus folders. Fetch the applicable original at task time. A URL check proves reachability only. See the [source contract](docs/source-integration-contracts.md).
- **Memory** is accepted project state and evidence in the resolved user workspace. It is never a reusable substitute for the applicable original source. Arch Studio-owned procedures, schemas and clearly synthetic fixtures may remain local.

A future product tool must have objective input/output semantics, general usefulness across projects, support valid alternatives and justify its maintenance/runtime cost. A normal MCP workflow must remain executable from its semantic contract without Arch Studio helper installation. Do not encode one customer fixture's answer. Preserve judgment when inputs or presentation require interpretation.

## Authoring skills

Use the active host's native skill-authoring capability when available; otherwise author a minimal skill in the host's supported format. Arch Studio supplies the governing contracts, not a substitute tutorial for the host. State the outcome, necessary inputs and outputs, evidence requirements, domain invariants and observable done condition. Do not add generic reasoning advice or mandatory steps that the host can derive from those requirements. Preserve a procedure when its order is itself a requirement, and explain that requirement in the owning skill.

Before adding a skill, check for an existing owner of the same capability. Validate the result against the applicable owners below, the host's format, and relevant repository checks. Behavioral value over the host without the skill requires a representative comparison; structural lint alone does not establish it. Retire instructions that no longer provide useful information or measured benefit.

## Governing owners

| Concern | Read when needed |
|---|---|
| Host capabilities, permissions, handoffs and invariants | [Host-harness contract](docs/host-harness-contract.md) and the selected adjacent host-contract.json |
| Installation, invocation and optional delegation | [Host adapters](docs/host-adapters.md) |
| Completion evidence and limitations | [Completion reporting](docs/completion-reporting.md) |
| Project identity, records, document operations and writer ownership | [Workspace model](docs/workspace-model.md) |
| Agent roles and skill discovery | [Agents](docs/agents.md), [skills](skills/README.md) and corpus/components.json |
| Package/channel identities and release checks | [Release delivery](docs/release-delivery.md) |
| Names, voice and cross-cutting rules | [Terminology](rules/terminology.md) and [rules](rules/README.md) |
| Contributions and source verification | [Contributing](CONTRIBUTING.md) |

## Collaboration contract

The harness owns the conversation, interpretation, available host capabilities and actual agent creation. Arch Studio owns domain capability contracts, required procedures, record authority and evidence. Direct skill selection is valid. Norma coordinates substantial multistep work with workplan; quick tasks proceed within existing authorization. Disclose a useful team before approval, verify actual creation afterward and keep questions in the main loop. Never ask again for authorization already covering the action.

The host checks identity, requested membership, revision links and declared preservation using the owning contracts and its available tools. The host chooses valid methods, resolves source meaning and inspects presentation. A completion report summarizes these observations; it is not another validator or a universal required runtime. See the existing reporting contract.

Use available native host capabilities and the owning semantic specification. Ordinary task-specific code is allowed; Arch Studio executable source is not handed through MCP for installation or reconstruction. Host access remains specific to the actual target. Missing capabilities, unresolved source facts and unperformed visual inspection remain explicit. The host contract defines mutation guarantees and source-content authority.

## Keep changes small and coherent

Keep flat skill identities and useful colocated helpers. Review all components; rewrite only conflicting or affected ones. One authoritative implementation or policy per concern. Update current consumers with their owner contract. No arbitrary directory rewrite, blanket benchmark, mandatory coordinator hop or historical compatibility layer.

Headers/manifests use the formats required by the supported host. README owns the ASCII branding; there is no branding requirement on other surfaces. Private workspace data and production credentials never enter the package. The [release guide](docs/release-delivery.md) governs publication, not a development commit.
