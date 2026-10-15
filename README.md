<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/brand/arch-studio-typemark-white.png">
  <img src="assets/brand/arch-studio-typemark.png" alt="Arch Studio" width="650">
</picture>
<br>
<br>
<br>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Release](https://img.shields.io/github/v/release/AlpacaLabsLLC/skills-for-architects)](https://github.com/AlpacaLabsLLC/skills-for-architects/releases)
[![Claude Code: plugin](https://img.shields.io/badge/Claude_Code-plugin-blue)](https://code.claude.com/docs)
[![Codex: plugin](https://img.shields.io/badge/Codex-plugin-blue)](https://developers.openai.com/codex/)
[![skills: 61](https://img.shields.io/badge/skills-61-blue)](./skills/README.md)
[![website: architecturestudio.ai](https://img.shields.io/badge/website-architecturestudio.ai-blue)](https://architecturestudio.ai)
[![Last commit](https://img.shields.io/github/last-commit/AlpacaLabsLLC/skills-for-architects)](https://github.com/AlpacaLabsLLC/skills-for-architects/commits/main)

</div>

Arch Studio is a framework that helps an architecture studio build its own AI practice. It helps you decide how AI is governed in your studio, which practice areas it covers, what it remembers, and which tools it uses, then carries those decisions into [Claude Code](https://code.claude.com/docs) or [Codex](https://developers.openai.com/codex/).

## Contents

- [How it works](#how-it-works)
- [Two editions](#two-editions)
- [Commercial services](#commercial-services)
- [Install](#install)
- [The basic workflow](#the-basic-workflow)
- [What's inside](#whats-inside)
- [Make it yours](#make-it-yours)
- [Philosophy](#philosophy)
- [When something goes wrong](#when-something-goes-wrong)
- [Updating and what's new](#updating-and-whats-new)
- [Contributing](#contributing)
- [Data, privacy and telemetry](#data-privacy-and-telemetry)
- [License](#license)

## How it works

Before a studio can trust AI with real work, it has to make a few decisions. Arch Studio gives each one a place to live and keeps the assistant inside it.

- **Governance: who approves what.** Adopt your own AI-use policy or start from the default one. The assistant works within it. It shows a work plan before larger jobs, offers findings to your records instead of writing them on its own, and marks building-code, zoning and specification output for professional review. The architect still signs off.
- **Practice areas: where AI helps.** Skills are grouped by [practice area](docs/practice-clusters.md), from due diligence and programming to specifications and FF&E. Use the areas that fit your practice and ignore the rest.
- **Memory: what the studio remembers.** Studio settings, project facts, decisions, documents, tasks and time live in plain files in folders you own, so the next session can pick up where the last one ended.
- **Tooling: what the assistant can use.** Start with the 61 bundled skills as working references. Then write your own with `/as:skill-maker`. Your skills live in your studio or project folder, and plugin updates never overwrite them.

Run `/as:studio` to set up the governance and memory side: your AI-use policy, naming and filing rules, units, jurisdiction and project phases. It shows exactly what it will create and writes nothing until you approve. Then register projects. From there, Norma, the coordinator, sends each request to the right skills within the rules you set. You can also skip setup and try a skill on a single task first.

## Two editions

- **Arch Studio OSS** (this repository) is the single-user setup. You install the plugin in your own Claude Code or Codex, and your studio and project records stay in local folders. It is free and MIT-licensed.
- **Arch Studio MCP** is the hosted service, for teams. It delivers the same Arch Studio content to a connected assistant through a signed-in firm account. It also adds hosted modules, such as the Materials Library, whose records only members of that firm can reach. It sends instructions; your assistant still does the work with its own tools, and the service cannot reach your local files. Project records stay local in both editions. Only records you save to a hosted module are held by the service ([data governance](docs/data-governance.md)).

Use one or the other, not both. To ask about Arch Studio MCP, email `hello@alpa.llc`.

## Commercial services

Arch Studio OSS is open source under the MIT license. If your studio wants help working through these decisions, writing its own skills, moving a team to Arch Studio MCP, training, or support, email ALPA at `hello@alpa.llc`.

## Install

One plugin, `as` (Arch Studio), with the same skills on every host. Install it in each assistant you use.

### Claude Code

```bash
claude plugin marketplace add AlpacaLabsLLC/skills-for-architects
claude plugin install as@skills-for-architects
claude
```

### Codex

```bash
codex plugin marketplace add AlpacaLabsLLC/skills-for-architects
codex plugin add as@skills-for-architects
codex
```

### Claude Desktop

Open **Customize → Plugins → + → Add marketplace**, choose a repository source, enter `AlpacaLabsLLC/skills-for-architects`, and install **Arch Studio**. Workspace, hook, and subagent behavior depends on the Claude surface and permissions your organization enables; the workflow below is tested with Claude Code.

### Check that it works

Type `/as:studio` in Claude Code, or `$studio` in Codex. It offers four paths: set up a studio, use the skills without setup, open an existing studio, or learn on a fictional practice project. Nothing is created (no studio, project, ALPA account, cloud store, or git repository) until you approve an exact local folder. Using the skills without setup creates no workspace files; a skill creates only the output you ask for.

New to AI assistants? Start the six-module course with `/as:learn` (Codex: `$learn`).

For teams, Arch Studio MCP is connected rather than installed; see [Two editions](#two-editions). Install the plugin or connect the MCP, not both: the MCP delivers instructions only, does not run skills, and cannot reach your local files. See [release delivery](docs/release-delivery.md).

## The basic workflow

1. **studio** — Run `/as:studio` to record your studio's policy, conventions and projects, or skip setup and go straight to a task. Skills work either way.
2. **norma** — Describe what you need in plain words. Norma picks the skills, handles quick lookups directly, and for larger jobs uses **workplan** to show you a work plan (steps, skills, and outputs) before starting.
3. **Research skills** — Site, zoning, property, product, and EPD skills fetch original sources and cite them. For example, **nyc-property-report** gathers landmarks, permits, violations, ownership, housing, and BSA records into one report.
4. **Specification and presentation skills** — **spec-writer**, **epd-to-spec**, **product-cut-sheet**, **slide-deck-generator** and others prepare documents from the research. Anything regulatory is marked for professional review.
5. **Record skills** — **project**, **receive**, **meeting-minutes**, **tasklist** and **timetracker** keep facts, documents, decisions, tasks, and time in your project folder. They offer what to save rather than writing silently, and time is logged only in amounts you confirm.
6. **skill-maker** — When your firm repeats a procedure, run `/as:skill-maker` to turn it into a studio or project skill.

Not sure what is available? `/as:tool-catalog` lists every skill and agent on your host. `/as:studio` stays the place for studio administration; a general task typed there is passed to Norma. Optional [default preferences](skills/norma/references/assistant-preference.md) make your assistant use Arch Studio by default for architecture and project work; they need a supported target, an exact diff, and your approval.

**Host syntax.** Claude Code uses `/as:<skill>`; Codex uses `$<skill>`. `as` is the plugin namespace. Use the exact name your assistant shows.

## What's inside

61 skills, 8 agents, 8 rules, and 4 hooks. Everything installs together. The full catalog, with inputs and outputs, is in [skills/README.md](./skills/README.md).

### Skills

**Getting started and studio**
- **norma** — Coordinates a request across the skills that fit it
- **norma-support** — Help with setup, access, memory, and troubleshooting
- **studio** — Set up or open a studio and register projects
- **tool-catalog** — Lists the skills and agents available on your host
- **learn** — Six-module, resumable course using a sample museum project
- **skill-maker** — Create or update your own studio or project skills
- **studio-feedback** — Prepare a bug report or feature request for you to review and send

**Project records**
- **project** — Set up a project and keep its facts and decisions
- **receive** — File received and authored documents, keeping original filenames
- **workplan** — Prepare a work plan before larger work starts
- **meeting-minutes** — Minutes from notes or transcripts, decisions kept separate from discussion
- **site-visit-report** — Site-visit records: what was seen, what was reported, and follow-ups
- **tasklist** — Project or studio task list (`TASKS.csv`)
- **timetracker** — Logs only time you confirm (`TIME.csv`)

**Proposals, agreements and invoices**
- **proposal** — Prepare and register proposals; protects terms once issued
- **agreement** — Keep agreement scope on hand and check work against it
- **invoice** — Append-only invoice ledger from billing facts you supply

**Professional practice**
- **architecture-knowledge** — Plain explanations of US practice terms: phases, CD sets, AIA contracts, CSI/NCS

**NYC due diligence**
- **nyc-landmarks** — Landmark and historic-district check (LPC)
- **nyc-dob-permits** — DOB permits and job filings
- **nyc-dob-violations** — DOB and ECB violations
- **nyc-acris** — Deeds, mortgages, liens, and sales (ACRIS)
- **nyc-hpd** — HPD violations, complaints, and registration
- **nyc-bsa** — BSA variances and special permits
- **nyc-property-report** — All of the above in one report

**Site planning**
- **environmental-analysis** — Climate, sun, flood, seismic, soil, and topography
- **mobility-analysis** — Transit, walking, cycling, and airport access
- **demographics-analysis** — Population, income, age, housing, and jobs
- **site-history** — Neighborhood context, landmarks, and planned development

**Zoning**
- **zoning-analysis-nyc** — NYC FAR, height, setbacks, and uses for a lot
- **zoning-envelope** — Interactive 3D view of the buildable envelope

**Programming**
- **workplace-programmer** — Office programs from headcount and work style
- **occupancy-calculator** — Building-code occupant loads, egress, and plumbing fixtures

**Specifications**
- **spec-writer** — Project Manual sections, with review markers
- **epd-to-spec** — EPD submittal requirements and GWP limits for a specification section

**Sustainability**
- **epd-research** — Find EPDs by material or category
- **epd-parser** — Pull GWP and other impacts from an EPD PDF
- **epd-compare** — Compare EPDs side by side, including LEED eligibility

**FF&E and materials**
- **product-research** — Find products from a design brief
- **product-match** — Find similar products from an image, name, or description
- **product-pair** — Suggest pieces that go with a product
- **product-url-clip** — Save a product page as evidence without adopting it
- **product-spec-bulk-fetch** — Pull specs from a list of product URLs
- **product-spec-pdf-parser** — Pull specs from product PDFs and price books
- **product-data-import** — Turn product information into schedule-ready rows
- **product-data-cleanup** — Normalize casing, dimensions, units, and materials
- **product-enrich** — Tag products by category, color, material, and style
- **product-image-processor** — Download, resize, and remove backgrounds from product images
- **product-library** — Your firm's reusable product library
- **product-audit** — Check products or a schedule against their sources
- **product-cut-sheet** — One-product cut sheet from a PDF or URL
- **ffe-spec-book** — Assemble cut sheets into an FF&E book
- **master-schedule** — Adopt, revise, and reconcile the project FF&E schedule
- **drawing-quantity-extract** — Count furniture or fixtures on supplied drawings
- **lighting-report-extract** — Read luminaire counts and results from lighting reports
- **schedule-quantity-reconcile** — Compare counts from drawings, reports, and schedules
- **csv-to-sif** — Export a product CSV to dealer SIF
- **sif-to-csv** — Read dealer SIF into a product CSV

**Presentations**
- **slide-deck-generator** — Self-contained HTML slide decks
- **color-palette-generator** — Color palettes with contrast checks
- **resize-images** — Resize images for web, social, slides, and print

**Which specification skill?** A Project Manual section → **spec-writer**. Its EPD and GWP requirements → **epd-to-spec**. One product from a PDF or URL → **product-cut-sheet**. A bound FF&E book → **ffe-spec-book**.

### Agents (Claude Code)

Eight agents: seven specialists and an optional Norma worker. Each one combines a group of skills for a kind of work. They run only where the host supports delegation and the request allows it; otherwise the same skills run directly. Codex installs the skills but not these agents. See the [agents index](./docs/agents.md).

| Agent | What it does |
|-------|--------------|
| [site-planner](./agents/site-planner.md) | Runs environmental, mobility, demographic, and history research, then combines them |
| [nyc-zoning-expert](./agents/nyc-zoning-expert.md) | NYC property research, zoning analysis, and envelope visualization |
| [workplace-strategist](./agents/workplace-strategist.md) | Turns headcount and work style into programs and room schedules |
| [product-and-materials-researcher](./agents/product-and-materials-researcher.md) | Finds products, extracts specs, and suggests alternatives |
| [ffe-designer](./agents/ffe-designer.md) | Builds schedules and room packages, checks them, and prepares dealer files |
| [sustainability-specialist](./agents/sustainability-specialist.md) | Researches and compares EPDs and prepares spec limits |
| [brand-manager](./agents/brand-manager.md) | Builds decks and palettes and checks deliverables before they go out |
| [norma](./agents/norma.md) | Optional worker that carries out an already approved assignment; questions go back to you |

### Rules

Shared conventions the skills follow. They guide output; only the hooks below check anything automatically. See the [rules index](./rules/README.md).

| Rule | Covers |
|------|--------|
| [units-and-measurements](./rules/units-and-measurements.md) | Imperial and metric defaults, area types, dimensions |
| [code-citations](./rules/code-citations.md) | Building-code editions, jurisdiction, and references |
| [professional-disclaimer](./rules/professional-disclaimer.md) | Required disclaimer and limits on regulated output |
| [csi-formatting](./rules/csi-formatting.md) | CSI formatting from the original standard you supply |
| [terminology](./rules/terminology.md) | Style and first-use conventions |
| [output-formatting](./rules/output-formatting.md) | Tables, source attribution, file names, lists |
| [transparency](./rules/transparency.md) | Showing inputs, assumptions, calculations, and sources |
| [moments](./rules/moments.md) | The shared session line, when to suggest setup, and how to invoke skills |

### Hooks

Claude Code loads three hook handlers across two events. Codex loads one. See the [hooks index](./hooks/README.md).

| Hook | Host | When | What it does |
|------|------|------|--------------|
| [session-start-welcome](./hooks/session-start-welcome.sh) | Claude Code | First session after install | Confirms the skills are ready and points to setup and the course |
| [version-check](./hooks/version-check.sh) | Claude Code | Session start, at most daily | Checks for a newer release (see [telemetry](#data-privacy-and-telemetry)) |
| [post-write-disclaimer-check](./hooks/post-write-disclaimer-check.sh) | Claude Code | After Write or Edit | Flags regulatory output missing the professional disclaimer |
| [session-start-ambient](./hooks/session-start-ambient.sh) | Codex | Session start | Adds short Arch Studio routing context; reads and writes nothing |

## Make it yours

The bundled skills are working examples, not the limits of the system. Firms add their own skills, which live in the firm's folders, outside the plugin, and are never overwritten by updates.

| Where | Location | For |
|-------|----------|-----|
| Bundled skills | Installed plugin | AEC skills maintained in this repository |
| Studio skills | `studio/.agents/skills/` (Codex) or `studio/.claude/skills/` (Claude Code) | Firm standards, internal procedures, templates |
| Project skills | `<registered-project>/.agents/skills/` or `.claude/skills/` | Client-, jurisdiction-, or project-specific procedures |
| Upstream | This repository | General skills proposed for everyone |

Run `/as:skill-maker` and choose studio or project. It uses your assistant's own skill maker when there is one and checks the result against Arch Studio's rules.

You can start with the bundled skills today and set up a studio later; nothing needs migrating.

### How it is organized

Arch Studio has four parts:

| Pillar | Responsibility |
|---|---|
| Studio | Account and access, Configuration, Standards and Assurance |
| Tooling | Skills, specialist profiles, tools and integrations; the host performs execution |
| Knowledge | Access to applicable authoritative original sources and their provenance |
| Memory | Accepted studio/project facts, decisions, preferences, records and evidence |

More detail: [architecture](docs/architecture.md), [workspace model](docs/workspace-model.md) (who owns which file), [host-harness contract](docs/host-harness-contract.md), [host adapters](docs/host-adapters.md), and [PATTERNS](PATTERNS.md). Firms planning a pilot should read the [firm deployment guide](./docs/firm-deployment.md). For organizing skills across a team, see [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams).

## Philosophy

- **Local first.** Your studio and project records stay in your folders. The plugin does not upload them anywhere.
- **Original sources.** Skills go to the authoritative source and say where each fact came from. They do not rely on summaries bundled with the plugin.
- **The architect decides.** Skills research, prepare and check. Building-code, zoning, and specification output is marked for professional review, and findings are offered to your records rather than written silently.
- **Firms own their skills.** Your procedures live in your workspace, can stay private, and can be shared upstream if you choose.

## When something goes wrong

Run `/as:studio-feedback` (Codex: `$studio-feedback`). It prepares a bug report or feature request on your machine for you to read. It opens a prefilled GitHub issue only when you choose to, and never submits it for you.

For setup or access questions, ask `/as:norma-support`. You can also [open an issue](https://github.com/AlpacaLabsLLC/skills-for-architects/issues) directly.

## Updating and what's new

Current version: **1.5.2**. On Claude Code, a daily check tells you when a newer release is out. Release notes, including breaking changes and upgrade steps, are in the [CHANGELOG](./CHANGELOG.md).

## Contributing

If a skill would help other practices, propose it here. A good upstream skill has no firm or client secrets, clear inputs and outputs, cites its sources, keeps professional review in place, and includes tests or examples.

Read [CONTRIBUTING.md](./CONTRIBUTING.md) first. Repository conventions are in [PATTERNS.md](./PATTERNS.md); shared data formats are in [`schema/`](./schema).

## Data, privacy and telemetry

Arch Studio runs inside your own Claude Code or Codex session. Your AI model provider's data controls, retention, and account policies apply: see Anthropic's [Privacy Center](https://privacy.claude.com/) or OpenAI's [privacy policy](https://openai.com/policies/privacy-policy/).

- The open-source plugin does not upload or store studio, project or module records on Arch Studio servers. Hosted record-holding modules use the separate boundaries in the [data-governance documentation](./docs/data-governance.md).
- Prompts and files you send to the AI model are handled under your provider account.
- Research skills contact the public sources named in their documentation when you run them.
- New studios include an empty `.mcp.json`. Arch Studio does not pick providers, set up logins, or ship credentials.
- `/as:studio-feedback` prepares everything locally. Opening the prefilled GitHub link sends what is shown on screen.

**Telemetry (Claude Code only).** Once a day at most, the version-check hook makes one request to `version.alpa.llc` to look for updates. That request also carries an anonymous usage ping: a random install ID created once and stored on your machine (not derived from you or the machine) and the plugin version. It sends no names, account, firm, file paths, project content, or text you typed, and fails silently. Cloudflare still sees ordinary request data such as IP address, headers, and time. Both are on by default:

- Turn off the usage ping: `AS_TELEMETRY_DISABLED=1`
- Turn off the update check: `AS_UPDATE_CHECK_DISABLED=1`, or `/as:studio updates disable`

Codex installs no lifecycle hook that makes this request, so it sends neither.

Full details: [data-governance documentation](./docs/data-governance.md).

## License

MIT. See [LICENSE](LICENSE). Copyright © 2026 Alpaca Labs LLC.

---

Created by Federico Negro in 2026 and built by [ALPA](https://alpa.llc), a boutique design & technology studio for the built environment, founded by Federico Negro in Brooklyn, New York. Contact: `hello@alpa.llc`.

**Read more:** [Claude Code Cheat Sheet for Architects](https://alpa.llc/articles/claude-code-cheat-sheet) · [Distributing Skills to Teams](https://alpa.llc/articles/distributing-skills-to-teams)
