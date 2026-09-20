# Contributing

Contributions should preserve Arch Studio’s governance, memory ownership, and portable file contracts.

Private firm and project skills belong in the user-owned studio workspace and do not require an upstream contribution. Use `$skill-maker` on Codex or `/as:skill-maker` on Claude Code. The process below is for general-purpose work proposed to the maintained public plugin.

## Local prerequisites

`./scripts/lint.sh` and the test suite degrade quietly when a tool is absent — checks are skipped with a notice rather than failing, and CI enforces them afterwards. Install these so a local run means what it says:

| Tool | Needed for | Without it |
|---|---|---|
| `python3` with `pyyaml` (`pip install pyyaml`) | SKILL.md frontmatter validation in `scripts/lint.sh`; `scripts/audit-skill-context.sh` | Frontmatter, JSON, count, and link checks skip; the audit script exits with an install hint |
| `jq` | JSON manifest checks | Manifest validation skips |
| Node.js >=18 (CI uses 24.20.0) | Source/integration contract validation and explicit source-health checks | Source validation requires installation; CI enforces it |
| `shellcheck` | Shell-script analysis | Skipped locally with a notice; CI enforces it |

A run that reports `all checks passed` with skip notices above it has not verified everything. Read the notices.

## Add or change a skill

1. Fork the repository and create a focused branch.
2. Add or update the directory under `skills/`.
3. Keep `SKILL.md` authoritative for harness behavior and `README.md` focused on human-facing purpose, inputs, outputs, and examples.
4. Add the skill once to [`skills/README.md`](./skills/README.md).
5. Register public skills and shared components in `corpus/components.json` and reference their IDs from the appropriate `clusters/` manifests. Update shared rules or schemas only when behavior genuinely changes for multiple consumers.
6. Add focused contract coverage and run `./scripts/lint.sh` plus the relevant tests.
7. Open a pull request describing the behavior, verification, and representative output.

Record an adjacent defect in the owning project with its source and consequence. Do not expand the approved slice or post an external issue/comment without applicable authorization. Durable project records, not chat mentions, carry unfinished work.

Read [PATTERNS.md](./PATTERNS.md) for naming, layout, dispatcher behavior, versioning, and lessons from prior defects.

Do not include client data, firm secrets, credentials, or proprietary procedures in a pull request. Codex invokes catalog and private skills as `$name`; Claude Code uses namespaced catalog commands such as `/as:site-history` and local `/{name}` commands for private workspace skills.

## Documentation ownership

- Root `README.md`: product, installation, first use, and architectural orientation
- `skills/README.md`: complete tooling catalog
- `docs/agents.md`: orchestration model and agent roster
- `rules/README.md`: governance conventions and enforcement strength
- `hooks/README.md`: lifecycle automation and configuration
- `schema/README.md`: shared data contracts
- `docs/`: cross-cutting product architecture and durable plans

Avoid copying authoritative instructions into multiple places. Link to the owning document instead.

## Shared ownership and distribution

For the R5-HN MCP successor, make each operation executable from its owning non-executable specification: inputs, exact transformation/formulas, preserved state, conflict/retry/recovery rules and observable completion. Ordinary host task-specific code is allowed; no mandatory Arch Studio runner, installer, bridge or executable source reconstructed through MCP. Maintainer scripts/validators/build dependencies are separate. Any future mandatory Arch Studio executable requires an explicit architectural decision.

Keep callable procedures flat under `skills/`. External-source navigation has one canonical metadata owner under `corpus/sources/catalog.json`; external reference content is not bundled. Maintainer executable implementations live under `tools/`; cluster manifests live under `clusters/`, and distributed Studio contracts under `studio/`. These package directories never contain a user's actual studio records. Skill-private assets can remain with their skill; current callers use the shared owner implementation; R4 adds no compatibility-only aliases or historical converters.

A new practice area composes registered components and declared coverage. A new geography contributes maintained sources, authority relationships, necessary adapters and evaluation cases. Directory ancestry does not establish legal applicability. A source URL or skill instruction is not evidence of an executable tool or validated workflow.

Run the foundation validators and all affected contracts before proposing a change. Structural changes must be checked in an exported package outside the Git checkout. Notify the MCP maintainer of new resource roots, moved canonical paths and changed script contracts; the hosted package must be rebuilt from the reviewed Arch Studio source. See [release delivery](docs/release-delivery.md).

## Slice execution

Use the approved project plan and its latest owner amendments. State the outcome, base SHA, file owner, affected callers and checks. Work in a stable focused worktree; keep primary checkouts clean, preserve unrelated changes and stage explicit files. Update the owner contract and its current consumers as one coherent change. Independent agents may work in parallel only with exclusive file ownership and explicit dependency handoffs.

Review every component, rewrite only affected or conflicting ones and preserve valid alternative workflows. Deterministic tools enforce objective invariants; harness judgment is not replaced by a fixture-specific renderer or a mandatory validator runtime. R4 is forward-only; new-model operation integrity remains required.

Ordinary engineering checks accompany implementation. For R5-HN, the bounded tasklist/context MCP pilot runs on a nonproduction endpoint and must pass its predefined repeated protocol before catalog replication. Final actual-host execution verification runs after full implementation, package and documentation integration. Independent review distinguishes observed passes from missing or unsupported routes. Record exact tested commits, results and skips; later changes invalidate affected evidence. Do not equate implemented, integrated, staged, production and accepted.

Private-source integration does not authorize public publication or production promotion. Preserve actual prior deployment recovery, source custody and frozen evaluation artifacts. Reuse applicable user authorization instead of adding repeated gates. Retire worktrees only after integration or verified preservation and after checking their active consumers.

R5-HN is MCP first. Preserve current OSS artifacts and isolate shared changes in the private successor; OSS feature selection, packaging and acceptance are a separate owner decision. Do not impose parity or publish OSS to satisfy the MCP gate. Preserve frozen conversational/support candidates and their existing acceptance.
