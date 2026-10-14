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

**Current release: 1.5.2 · Preparing 1.5.3**

</div>

> A local-first framework for architecture firms to build, govern, and share their own AI-assisted workflows—use with [Codex](https://developers.openai.com/codex/) or [Claude Code](https://code.claude.com/docs).

Arch Studio gives Codex and Claude Code a governance layer, persistent studio and project memory, and extension points for firm-wide and project-specific skills. The bundled AEC skills and agents are working reference implementations: use them directly, study their patterns, or build procedures that reflect how your own practice works. Firm-created skills stay in your own studio workspace, outside the installed plugin, and are not overwritten by updates.

**One plugin**—`as` v1.5.2—with a shared skill catalog for both hosts. The repository contains **4 hooks**: Claude Code loads three handlers across two events, while Codex loads one ambient `SessionStart` hook. Claude Code also loads **8 agents** and **8 rules**.

## Contents

- [Install](#install)
- [Use](#use)
- [What's new in 1.5.2](#whats-new-in-152)
- [What's included](#whats-included)
- [Architecture](#architecture)
- [Extend and contribute](#extend-and-contribute)
- [Data and privacy](#data-and-privacy)
- [License](#license)

## Install

**Claude Code**

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install as@skills-for-architects
claude
```

Then run `/as:studio`.

**Claude app:** open **Customize → Plugins → + → Add marketplace**, choose a repository source, enter `AlpacaLabsLLC/skills-for-architects`, and install **Arch Studio**. Workspace, hook, and subagent behavior depends on the Claude surface and permissions your organization enables; the workflow is tested with Claude Code.

**Codex**

```bash
codex plugin marketplace add AlpacaLabsLLC/skills-for-architects
codex plugin add as@skills-for-architects
codex
```

Then run `$studio`.

Host setup: [Claude Code setup instructions](https://code.claude.com/docs/en/setup) · [Codex documentation](https://developers.openai.com/codex/).

The studio entry point offers to set up a studio, use the skills without setup, open an existing studio, or learn on a fictional practice project. Arch Studio creates no studio, project, ALPA account, cloud store, or git repository until you approve an exact local target.

Arch Studio is also delivered as a hosted MCP service under its own version. Install the plugin or connect the MCP, not both: the MCP delivers instructions, does not execute skills and has no access to local files. See [release delivery](docs/release-delivery.md).

## Use

Describe an architecture or project task to Norma, the coordinator inside your existing assistant, or call a skill directly:

```text
# Claude Code
/as:norma task chair, mesh back, under $800
/as:environmental-analysis 123 Main St

# Codex
$norma task chair, mesh back, under $800
$environmental-analysis 123 Main St
```

- **Full menu:** `/as:tool-catalog` (Claude Code) or `$tool-catalog` (Codex).
- **New to AI-assisted project work?** `/as:learn` or `$learn` runs a guided, resumable course; it branches where Claude-native agents, hooks, and `/clear` have no Codex equivalent.
- **No setup required.** Start with an ordinary task; create a studio or project only when you want durable records. You can add a studio later without migration.

`as` is the technical plugin namespace. Use the exact entry point the active host exposes. Skills run with the assistant's own tools and permissions; no Arch Studio runner, installer or bridge is required. See the [host-harness contract](docs/host-harness-contract.md) and [host adapters](docs/host-adapters.md). Optional [default preferences](skills/norma/references/assistant-preference.md) require a supported target, exact diff and approval.

## What's new in 1.5.2

A compatible patch on 1.5.1.2. No user action is required after upgrading.

- **Update check and usage ping on by default (Claude Code).** The daily update check now runs without opt-in, and its request carries an anonymous usage ping: a random install ID generated once and stored locally, plus the plugin version. No names, account, firm, file paths, project content or user text are sent. Set `AS_TELEMETRY_DISABLED=1` to turn the ping off; set `AS_UPDATE_CHECK_DISABLED=1` or run `/as:studio updates disable` to turn the update check off. This replaces the earlier "disabled by default" promise. The Codex package installs no lifecycle hook, so it sends neither. Details in [Data and privacy](#data-and-privacy).
- **Skill Maker verification fix.** Generated skills must show an observed fresh policy read and a separate observed read of the actual destination after publication; a claimed read, or a prepared file compared with itself, no longer counts as verification.

Full release history, including breaking changes in 1.5.0 and 1.5.1, is in the [CHANGELOG](CHANGELOG.md).

## What's included

### Agents

Seven specialist profiles plus an optional Norma worker, usable when the host exposes and permits delegation. Otherwise use the same skills directly or through Norma. The Codex package does not register these files as Codex roles. See the [agents index](./docs/agents.md).

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

### Skills

All bundled skills live in one flat catalog and install together. Browse the [complete tooling catalog](./skills/README.md) for every command, input and output.

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

Choosing a specification skill:

| Deliverable | Skill |
|---|---|
| Project Manual section with design, submittal and execution requirements | [spec-writer](./skills/spec-writer/SKILL.md) |
| Source-faithful product entry from a supplied PDF or URL | [product-cut-sheet](./skills/product-cut-sheet/SKILL.md) |
| Ordered FF&E specification book assembled from product sheets | [ffe-spec-book](./skills/ffe-spec-book/SKILL.md) |
| Project Manual EPD submittal requirements and sourced GWP limits | [epd-to-spec](./skills/epd-to-spec/SKILL.md) |

### Rules

Cross-cutting conventions consumed by the skills and agents that need them; a rule file is not a general runtime validator. See the [rules index](./rules/README.md).

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

### Hooks

Claude Code-specific event automations; the Codex manifest omits them. See the [hooks index](./hooks/README.md).

| Hook | Event | What it does |
|------|-------|--------------|
| [session-start-welcome](./hooks/session-start-welcome.sh) | First session after install | Confirms that built-in skills are ready and points to optional studio setup and learning |
| [post-write-disclaimer-check](./hooks/post-write-disclaimer-check.sh) | After Write or Edit | Flags marked regulatory output that is missing the professional disclaimer |
| [version-check](./hooks/version-check.sh) | Startup sessions, at most daily | Checks for a newer release and sends the anonymous usage ping; both on by default |

## Architecture

| Pillar | Responsibility |
|---|---|
| Studio | Account and access, Configuration, Standards and Assurance |
| Tooling | Skills, specialist profiles, tools and integrations; the host performs execution |
| Knowledge | Access to applicable authoritative original sources and their provenance |
| Memory | Accepted studio/project facts, decisions, preferences, records and evidence |

The plugin supplies instructions, schemas, helpers and templates. Your studio owns its `STUDIO.md`, registered projects and firm instructions; projects own `PROJECT.md`, `DOCUMENTS.csv`, `TASKS.csv`, `TIME.csv` and `INVOICES.csv`. Received filenames are preserved.

- [Architecture and authority map](docs/architecture.md): pillar definitions and folder mapping (`corpus/`, `tools/`, `skills/`, `clusters/`, `studio/`)
- [Workspace model](docs/workspace-model.md): exact record ownership
- [PATTERNS](PATTERNS.md): repository conventions and governing policies

## Extend and contribute

| Layer | Location | Purpose |
|-------|----------|---------|
| Bundled reference skills | Installed plugin | Working AEC skills, examples, and reusable patterns maintained upstream |
| Studio skills | `studio/.agents/skills/` (Codex) or `studio/.claude/skills/` (Claude Code) | Firm standards, internal procedures, shared templates, and practice-specific workflows |
| Project skills | `<registered-project>/.agents/skills/` or `.claude/skills/` | Client-, jurisdiction-, delivery-, or project-specific procedures |
| Upstream contributions | This repository | General-purpose capabilities proposed for the open-source project |

**Build your own.** `/as:skill-maker` creates or updates a skill at the right ownership level, using the host's native skill maker when available and applying Arch Studio governance and validation. No fork required.

**Contribute upstream.** A strong upstream skill contains no firm or client secrets, has clear inputs and outputs, preserves provenance and professional-review boundaries, and includes representative tests or examples. Read [CONTRIBUTING.md](./CONTRIBUTING.md) first; shared data contracts live in [`schema/`](./schema).

**Rolling out to a firm?** Read the [firm deployment guide](./docs/firm-deployment.md) and [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams).

## Data and privacy

Arch Studio runs inside your own Codex or Claude Code session. Model-side data controls, retention, and account or organization policies remain managed by the selected provider. Review OpenAI's [privacy policy](https://openai.com/policies/privacy-policy/) for Codex or Anthropic's [Privacy Center](https://privacy.claude.com/) for Claude, together with the settings and administrator policies for the active account.

- The open-source plugin does not upload or store studio, project or module records on Arch Studio servers. Hosted record-holding modules use the separate boundaries in the [data-governance documentation](./docs/data-governance.md).
- **Update check and usage ping (Claude Code, on by default).** At most one request per 24 hours to `version.alpa.llc` checks for a newer release and carries an anonymous usage ping: a random install ID generated once and stored locally (not derived from the user or the machine) and the plugin version. It sends no names, account, firm, file paths, project content or user text, and fails silently. Cloudflare still processes ordinary request metadata such as IP address, headers, and timestamps.
  - Turn off the ping: `AS_TELEMETRY_DISABLED=1`
  - Turn off the update check: `AS_UPDATE_CHECK_DISABLED=1` or `/as:studio updates disable`
  - The Codex package installs no lifecycle hook and sends neither.
- Prompts and files sent to the configured LLM are handled under that provider account and its data terms.
- Research skills contact the public sources named in their documentation when you run them.
- New studios reserve `.mcp.json` with an empty `mcpServers` object. Arch Studio does not select providers, configure OAuth, or bundle credentials.
- `/as:studio-feedback` prepares fields locally. Opening the prefilled GitHub URL sends the displayed query parameters immediately; Arch Studio never submits the issue.

## License

MIT—see [LICENSE](LICENSE). Copyright © 2026 Alpaca Design Lab LLC.

---

Created by Federico Negro and built by [ALPA](https://alpa.llc) (`hello@alpa.llc`)—research, strategy, and technology for the built environment.

**Read more:** [Claude Code Cheat Sheet for Architects](https://alpa.llc/articles/claude-code-cheat-sheet) · [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams)
