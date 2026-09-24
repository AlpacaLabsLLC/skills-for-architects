<div align="center">

```
 █████╗ ██████╗  ██████╗██╗  ██╗    ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗
██╔══██╗██╔══██╗██╔════╝██║  ██║    ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗
███████║██████╔╝██║     ███████║    ███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║
██╔══██║██╔══██╗██║     ██╔══██║    ╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║
██║  ██║██║  ██║╚██████╗██║  ██║    ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝
```

**Arch Studio**

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/AlpacaLabsLLC/skills-for-architects)](https://github.com/AlpacaLabsLLC/skills-for-architects/releases)

</div>

> A local-first framework for architecture firms to build, govern, and share their own AI-assisted workflows—use with [Codex](https://developers.openai.com/codex/) or [Claude Code](https://code.claude.com/docs).

**Arch Studio** provides a governance layer, persistent studio and project memory, and clear extension points for firm-wide and project-specific skills. The bundled AEC skills and agents are working reference implementations and starting templates: use them directly, study their patterns, or build procedures that reflect how your own practice works.

Firm-created skills remain in the user-owned studio workspace, outside the installed plugin cache. They can stay private to a firm or project, or be developed for contribution back to the open-source project.

**One plugin**—`as` v1.5.1—with a shared skill catalog for Codex and Claude Code. The repository contains **5 hooks**: Claude Code loads four handlers across three events, while Codex loads one ambient `SessionStart` hook. Claude Code also loads **8 agents** and **8 rules**. Created by Federico Negro in 2026 and built by [ALPA](https://alpa.llc) (`hello@alpa.llc`). Copyright © 2026 Alpaca Design Lab LLC; MIT-licensed.

## What’s new in 1.5.1

The 61-skill catalog now separates Project Manual sections, source-faithful product cut sheets and FF&E books. Use `ffe-spec-book` for book assembly: the `spec-book` skill entry point is removed immediately, with no alias. Existing `spec-book` document kinds, templates and receipts retain their identities.

Studio setup offers an existing central governance policy or a reusable default. Skill Maker references the selected policy live, rereads it when a skill runs or resumes, and pauses policy-dependent actions if it cannot read it. Slide decks use the studio’s name as text, or exactly `Insert Studio Name` when unavailable. Document-template paths now explicitly resolve inside the studio workspace.

Skills define bounded capabilities through outcomes, domain constraints, interfaces, evidence and verification; the host executes them. Product tools will be server-side deterministic operations in 1.6 or later; this release adds no server-side execution. Manifest versions and these notes describe the source candidate; channel publication requires the separate receipts in the [release guide](docs/release-delivery.md).

## What’s new in 1.5.0

Arch Studio 1.5.0 is harness-native: every bundled skill is a complete specification that Claude Code or Codex performs with its own tools, with no bundled script to run and no runner to install. It adds fifteen skills (FF&E and specification, firm operations, document registration and Norma coordination), original-source navigation under `corpus/`, and CSV project registers.

Breaking: new studios and projects use `DOCUMENTS.csv`, `CHANGES.csv`, `SCHEDULE.csv`, `TASKS.csv`, `TIME.csv` and `INVOICES.csv` in place of the 1.4.x `TASKS.md` and `TIMELOG.md`. The release is forward-only; existing workspaces are not converted. See [CHANGELOG.md](CHANGELOG.md).

### Foundation organization and delivery

Arch Studio packages source and capability catalogs under `corpus/`, maintainer tools under `tools/`, skills under `skills/`, practice clusters under `clusters/`, and workspace contracts under `studio/`. These directories support the four pillars below; they are not a second pillar taxonomy. Actual firm and project records remain in the user's workspace.

The same content is also delivered as a hosted MCP service under its own version. Install the plugin or connect the MCP, not both: the MCP delivers instructions, does not execute skills and has no access to local files, and this plugin ships no MCP server entry. See [release delivery and acceptance](docs/release-delivery.md).

## What’s new in 1.4.5

A packaging fix for Claude Desktop installation. Teaching examples and the Skill Maker template now live outside the installable `skills/` tree, and the learning material points to the canonical `/as:tasklist` skill instead of bundling a second skill with the same name. Recursive checks prevent misplaced skill manifests and canonical/example name overlap from returning.

Compatibility note: `ascii-name` and `clean-downloads` were documented as commands in 1.4.4 even though they were course examples stored inside the installable tree. They are source examples, not installed commands, in 1.4.5. If you used either command, copy its directory from `assets/learn-examples/` into your user-owned skills directory, rename `SKILL.example.md` to `SKILL.md`, and adapt it as a custom skill. No project or studio data migration is required.

## What’s new in 1.4.4

A maintenance hotfix for Claude Code hook enforcement. Missing JSON decoders and malformed hook payloads now fail open, so ordinary Bash, Write, and Edit operations continue; confirmed malformed CSI sections and missing required disclaimers still block. Upgrading from 1.4.3 requires nothing.

## What’s new in 1.4.3

A maintenance patch. `scripts/audit-skill-context.sh` now reads skill descriptions with the YAML parser instead of reconstructing them, correcting six frontmatter forms that were measured wrong — most visibly a plain multi-line description, which reported zero characters. No bundled skill used an affected form, so every published measurement is unchanged and no skill, record format, or command behavior moves. Upgrading from 1.4.2 requires nothing.

## What’s new in 1.4.2

Arch Studio v1.4.2 adds Codex as a supported host without changing the `as` plugin identity or the user-owned studio/project record formats introduced in v1.4.

- **Codex-native packaging.** `.codex-plugin/plugin.json` and the Git marketplace entry let Codex install the repository as `as@skills-for-architects`.
- **Cross-harness skills.** Every bundled skill maps Claude Code's `/as:<skill>` syntax to Codex's `$<skill>` syntax and resolves bundled scripts from the loaded skill path instead of a Claude-only environment variable.
- **Portable workspaces.** Studio and project scaffolds create `AGENTS.md` plus `.agents/skills/` for Codex alongside the existing Claude Code files.
- **Preserved boundaries.** Claude-specific agents and hooks remain available on Claude Code; Codex loads the shared skills and the same local project-record contracts.

Full history is in the [CHANGELOG](./CHANGELOG.md).

## Architecture

| Pillar | Responsibility |
|---|---|
| Governance | Authority, permissions, ownership, evidence and acceptance |
| Tooling | Skills, specialist profiles, tools and integrations; the host performs execution |
| Knowledge | Access to applicable authoritative original sources and their provenance |
| Memory | Accepted studio/project facts, decisions, preferences, records and evidence |

The [architecture and authority map](docs/architecture.md) owns these definitions and their folder mapping. `corpus/` contains both source navigation and capability discovery; it is not another name for Knowledge. [PATTERNS](PATTERNS.md) links the governing policies, including the [host-harness contract](docs/host-harness-contract.md).

The plugin supplies instructions, schemas, helpers and templates. A user studio owns its `STUDIO.md`, registered projects and firm instructions. Fresh projects own `PROJECT.md`, `DOCUMENTS.csv`, `TASKS.csv`, `TIME.csv` and `INVOICES.csv`; received and authored documents are registered and placed through the firm's path template. Received filenames are preserved. Read the [workspace model](docs/workspace-model.md) for exact ownership and the [data-governance boundary](docs/data-governance.md).

## Extend Arch Studio

Arch Studio separates maintained plugin capabilities from the procedures a firm creates for itself:

| Layer | Location | Purpose |
|-------|----------|---------|
| Bundled reference skills | Installed plugin | Working AEC skills, examples, and reusable patterns maintained upstream |
| Studio skills | `studio/.agents/skills/` (Codex) or `studio/.claude/skills/` (Claude Code) | Firm standards, internal procedures, shared templates, and practice-specific workflows |
| Project skills | `<registered-project>/.agents/skills/` or `.claude/skills/` | Client-, jurisdiction-, delivery-, or project-specific procedures |
| Upstream contributions | This repository | General-purpose capabilities proposed for the open-source project |

`/as:skill-maker` creates or updates a bounded capability at the correct ownership level. It uses the host’s native skill maker when available, applies Arch Studio governance and validates the result. Without a native maker it authors a minimal portable skill under the same contracts. Skills define outcomes, constraints and verification; ordered steps belong only where their order is required.

## Quick start

### Install

**Codex:** add the Git marketplace, install the plugin, and start Codex:

```bash
codex plugin marketplace add AlpacaLabsLLC/skills-for-architects
codex plugin add as@skills-for-architects
codex
```

Then open studio administration:

```text
$studio
```

**Claude:** Open **Customize → Plugins → + → Add marketplace**, choose a repository source, enter `AlpacaLabsLLC/skills-for-architects`, and install **Arch Studio**. Workspace, hook, and subagent behavior depends on the Claude surface and permissions your organization enables; the workflow below is tested with Claude Code.

**Claude Code:**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install as@skills-for-architects
claude
```

After Claude Code opens, run:

```text
/as:studio
```

The studio entry point offers paths to set up a studio, use the skills without setup, open an existing studio, or learn on a fictional practice project. Start the course with `$learn` on Codex or `/as:learn` on Claude Code. Arch Studio creates no studio, project, ALPA account, cloud store, or git repository until you approve an exact local target.

### Use

Describe your architecture/project task to Norma, the coordinator inside your existing assistant. It uses the current Arch Studio inventory and preserves scope, sources and permissions. Studio remains the administration entry point; its general-task form forwards to Norma. Direct skill calls remain available. Example names below require discovery in the active host:

```text
# Codex
$norma task chair, mesh back, under $800
$norma 123 Main St, Brooklyn NY

# Claude Code
/as:norma task chair, mesh back, under $800
/as:norma 123 Main St, Brooklyn NY
```

Use `$tool-catalog` on Codex or `/as:tool-catalog` on Claude Code for the complete menu. You can also invoke a skill directly—for example, `$environmental-analysis 123 Main St` on Codex or `/as:environmental-analysis 123 Main St` on Claude Code. New to AI-assisted project work? Start with `$learn` on Codex or `/as:learn` on Claude Code.

`as` is the technical plugin namespace for Arch Studio. Use the exact skill entry point exposed by the active host, including any required plugin namespace. Optional [default preferences](skills/norma/references/assistant-preference.md) require a supported target, exact diff and approval; they do not create a new assistant or connection.

### Fresh setup and local operations

Use the package installed for the selected channel. Start with an ordinary task or ask Norma for help; create a studio/project only when you need durable records. The new document model uses fresh setup rather than converting a historical workspace.

Record and file operations follow each skill's semantic contract and run with the connected assistant's own tools, within its existing permissions. No Arch Studio runner, installer or bridge is required, and executable source is never reconstructed from instructions. A hosted workflow connection delivers instructions and does not itself establish file access or workflow completion. See the [host-harness contract](docs/host-harness-contract.md), [host adapters](docs/host-adapters.md) and [release delivery](docs/release-delivery.md) for the actual acceptance boundary.

### Three ways to use Arch Studio

- **Use the references.** Invoke the bundled skills as installed; Claude Code also exposes the native agents. No studio workspace is required. Selecting tools-only onboarding creates no workspace files; an invoked skill may create only the output you ask it to produce.
- **Build your practice layer.** Create a studio when you want persistent settings, linked projects, and firm- or project-specific skills.
- **Contribute upstream.** Generalize a capability that benefits other practices and propose it to the open-source project.

All three paths use the same plugin architecture. You can begin with the reference skills and create a studio later without migration or cleanup.

### Host setup

For Codex, follow the current [Codex setup documentation](https://developers.openai.com/codex/) and the Codex install commands above. For Claude Code, follow the current [Claude Code setup instructions](https://code.claude.com/docs/en/setup), then run the marketplace and plugin commands above. Invoke `$studio` on Codex or `/as:studio` on Claude Code. The bundled course is available as `$learn` on Codex and `/as:learn` on Claude Code; it clearly branches where Claude-native agents, hooks, and `/clear` have no Codex equivalent.

## Bundled reference agents

These seven specialist profiles and the optional Norma worker can be used when the host exposes and permits delegation. Otherwise use the same underlying skills directly or through Norma. Package presence does not establish native registration; the Codex package does not register the Claude agent files as Codex roles.

These profiles illustrate how narrower skills combine. Use one only after the host exposes it and the request permits delegation; otherwise follow the owning skills directly. Listed skills define a domain, not an automatic sequence.

| Agent | Domain | What it does |
|-------|--------|--------------|
| [site-planner](./agents/site-planner.md) | Site planning | Runs separate environmental, mobility, demographic, and history streams before synthesis |
| [nyc-zoning-expert](./agents/nyc-zoning-expert.md) | Due diligence + zoning | Combines NYC property research, zoning analysis, buildable envelope, and visualization |
| [workplace-strategist](./agents/workplace-strategist.md) | Programming | Translates headcount and work style into occupancy-informed programs and room schedules |
| [product-and-materials-researcher](./agents/product-and-materials-researcher.md) | Materials research | Finds products, extracts specifications, classifies data, and identifies alternatives |
| [ffe-designer](./agents/ffe-designer.md) | FF&E design | Builds schedules and room packages, performs QA, and prepares dealer interchange |
| [sustainability-specialist](./agents/sustainability-specialist.md) | Sustainability | Researches EPDs, compares GWP, checks eligibility, and prepares specification thresholds |
| [brand-manager](./agents/brand-manager.md) | Presentations | Builds decks, creates palettes, and checks deliverables for presentation readiness |

| [norma](./agents/norma.md) | Optional Claude Code worker | Executes an already resolved, authorized assignment; questions return to the main harness |

See the [agents index](./docs/agents.md) for complete workflows and handoff logic.

## Bundled reference skills

All bundled skills live in one flat catalog and install together. They make Arch Studio useful immediately and provide concrete patterns firms can build from; they do not define the limits of the system or prescribe one firm’s way of practicing. These groups describe their role in practice, not separate plugins.

| Layer | Group | Description |
|-------|-------|-------------|
| Firm operations | Dispatcher | Studio setup and routing, the tool menu, skill creation, and reviewed feedback |
| Firm operations | Learn | Guided, resumable introduction to Codex and Claude Code for architects |
| Project management | Project records | Facts, decisions, `/as:workplan`, meetings, site reports, tasks, and confirmed time |
| Project management | Commercial records | Project-local proposals with protected issued terms, optional agreement context with an advisory scope guard, and append-only invoice ledgers |
| Professional practice | Architecture knowledge | Source-backed US vocabulary for phases, CD terminology, AIA relationships, and CSI/NCS context |
| Practice and design | Due diligence | NYC landmarks, permits, violations, ownership, housing, and BSA records |
| Practice and design | Site planning | Environmental, mobility, demographic, and site-history research |
| Practice and design | Zoning analysis | NYC zoning analysis and interactive buildable-envelope visualization |
| Practice and design | Programming | Workplace programs, occupancy loads, egress, and plumbing fixtures |
| Practice and design | Specifications | Project Manual sections and EPD requirements with professional-review markers |
| Practice and design | Sustainability | EPD parsing, research, comparison, and GWP requirements |
| Practice and design | FF&E and materials | Product research, extraction, cleanup, schedules, imagery, CSV, and SIF |
| Practice and design | Presentations | Slide decks, color palettes, and image preparation |

Browse the [complete tooling catalog](./skills/README.md) for every command, input, output, and supporting skill document.

Choose the specification skill by the requested document:

| Deliverable | Skill |
|---|---|
| Project Manual section with design, submittal and execution requirements | [spec-writer](./skills/spec-writer/SKILL.md) |
| Source-faithful product entry from a supplied PDF or URL | [product-cut-sheet](./skills/product-cut-sheet/SKILL.md) |
| Ordered FF&E specification book assembled from product sheets | [ffe-spec-book](./skills/ffe-spec-book/SKILL.md) |
| Project Manual EPD submittal requirements and sourced GWP limits | [epd-to-spec](./skills/epd-to-spec/SKILL.md) |

## Rules

Cross-cutting conventions shape every skill’s output. Hooks check only their declared mechanical conditions. Other guidance is consumed by the skills and agents that need it; a rule file is not a general runtime validator.

| Rule | What it governs |
|------|-----------------|
| [units-and-measurements](./rules/units-and-measurements.md) | Imperial and metric defaults, area types, and dimensions |
| [code-citations](./rules/code-citations.md) | Edition years, jurisdiction awareness, and building-code references |
| [professional-disclaimer](./rules/professional-disclaimer.md) | Required disclaimer language and limits on regulated output |
| [csi-formatting](./rules/csi-formatting.md) | Formatting procedure using task-supplied original standards; no bundled code mapping |
| [terminology](./rules/terminology.md) | Style and first-use conventions; architecture knowledge is linked from the rule |
| [output-formatting](./rules/output-formatting.md) | Tables, source attribution, file naming, and list structure |
| [transparency](./rules/transparency.md) | Visible inputs, assumptions, calculations, and sources |
| [moments](./rules/moments.md) | Shared session line, proportionate setup and invocation guidance |

See the [rules index](./rules/README.md) for the enforcement boundary.

## Hooks

These event-driven automations are Claude Code-specific. They register with the Claude package when it is enabled; the Codex manifest intentionally omits them.

| Hook | Event | What it does |
|------|-------|--------------|
| [session-start-welcome](./hooks/session-start-welcome.sh) | First session after install | Confirms that built-in skills are ready and points to optional studio setup and learning |
| [post-write-disclaimer-check](./hooks/post-write-disclaimer-check.sh) | After Write or Edit | Flags marked regulatory output that is missing the professional disclaimer |
| [pre-commit-spec-lint](./hooks/pre-commit-spec-lint.sh) | Before git commit | Flags malformed CSI section numbers |
| [version-check](./hooks/version-check.sh) | Enabled startup sessions, at most daily | Checks for a newer release only after explicit opt-in |

Background update checking is disabled by default. If enabled, it makes at most one bare request per 24 hours to `version.alpa.llc`, sends no project content or Arch Studio identifier, and fails silently. Cloudflare still processes ordinary request metadata such as IP address, headers, and timestamps.

See the [hooks index](./hooks/README.md) for behavior and customization.

## Data and privacy

Arch Studio runs inside the user's own Codex or Claude Code session. Model-side data controls, retention, and account or organization policies remain managed by the selected provider. Review OpenAI's [privacy policy](https://openai.com/policies/privacy-policy/) for Codex or Anthropic's [Privacy Center](https://privacy.claude.com/) for Claude, together with the settings and administrator policies for the active account.

- Arch Studio does not upload or store studio or project records with ALPA.
- Prompts and files sent to the configured LLM are handled under that provider account and its data terms.
- Research skills contact the public sources named in their documentation when the user runs them.
- New studios reserve `.mcp.json` with an empty `mcpServers` object. Arch Studio does not select providers, configure OAuth, or bundle credentials.
- `/as:studio-feedback` prepares fields locally. Opening the prefilled GitHub URL sends the displayed query parameters immediately; Arch Studio never submits the issue.

Read the complete [data-governance documentation](./docs/data-governance.md).

## Extend your own studio

Firms can create private studio and project skills without forking this repository. Those skills live in the user-owned workspace, can follow internal standards, and are not overwritten by plugin updates. Start with `/as:skill-maker` and choose the studio or project destination.

## Contribute upstream

When a capability has value across practices, it can be proposed to the shared plugin. A strong upstream skill contains no firm or client secrets, has clear inputs and outputs, preserves provenance and professional-review boundaries, and includes representative tests or examples.

Read [CONTRIBUTING.md](./CONTRIBUTING.md) before proposing a skill or changing a shared contract. Repository conventions live in [PATTERNS.md](./PATTERNS.md), and shared data contracts live in [`schema/`](./schema).

Firms preparing a controlled pilot should also read the concise [firm deployment guide](./docs/firm-deployment.md) for ownership, access, backup, rollout, and incident responsibilities.

For guidance on organizing skills across a team, read [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams).

## License

MIT—see [LICENSE](LICENSE).

---

Built by [ALPA](https://alpa.llc)—research, strategy, and technology for the built environment.

**Read more:** [Claude Code Cheat Sheet for Architects](https://alpa.llc/articles/claude-code-cheat-sheet) · [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams)
