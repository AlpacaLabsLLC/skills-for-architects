---
name: skill-maker
description: "Scaffold a new Arch Studio skill for Codex or Claude Code following this repo's conventions — copy a canonical template, apply the PATTERNS.md checklist, and verify it. Use when the user invokes skill-maker, asks to create or package a new skill, or wants to turn a procedure into a reusable command."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /as:skill-maker — Scaffold a New Skill

Before acting, read the [host contract](../../docs/host-harness-contract.md) and this component's [declaration](host-contract.json) (`skill:skill-maker`). Load only its referenced mode profiles from the [shared catalog](../../corpus/host-contracts.json). Compose modes required by the actual task; declarations are requirements, not proof of access or permission. Use the actual host’s [delivery route](../../docs/host-adapters.md).

## Harness-native execution

Follow this complete procedure using the active host's authorized file, search and YAML-reading facilities. The existing `skill_scaffold.validate` identifier names the checks below; it is not a dispatcher requirement. No Arch Studio executable, copied helper or installation step is required. MCP references identify release resources, not paths assumed to exist on this machine. Retrieve complete templates and PATTERNS at the delivered release pin before using them; retain their actual identity.

For all requested files follow [native publication](../../docs/workspace-model.md#native-mutation-sequence): inspect the exact target and actual existing bytes/access; finish and durably retain all original and proposed files; separately reopen the complete preparation before any public write; publish complete bytes with actual no-clobber/stale-write protection; then reopen and check the whole affected set. Include README and any requested validation report. Inspect incomplete prior attempts before retrying. If required access, concurrent-writer protection or recoverable publication is unavailable, stop before mutation with the concrete limitation. This preparation is an internal execution safeguard, not another user draft approval gate.

You turn a described procedure into a working skill: a directory with a `SKILL.md` and a `README.md` that follows this repo's conventions. Input is the user's request; output is a card Codex or Claude Code can follow.

## Usage

```
/as:skill-maker a skill that turns raw site photos into a numbered photo log
/as:skill-maker package our submittal-review checklist as a slash command
/as:skill-maker <any procedure worth repeating>
```

## Hard rule: no routine interview

Derive everything — name, description, tools, steps — from the request. Do not ask routine setup questions. Ask only for the missing information when the skill's purpose is genuinely indecipherable, the user requests a global skill without explicitly authorizing the global target, or an existing target would have to be updated. A policy-dependent action may also need a precise studio-selection, inaccessible-policy or conflicting-rule clarification under the governance contract below; this is not a routine setup interview. Otherwise make the reasonable call and note it when presenting the result.

## Anatomy of what you're producing

A skill is a procedure card. Four load-bearing parts:

| Part | Job |
|---|---|
| `name` | Kebab-case, matches the directory, becomes the skill command |
| `description` | The **trigger**, not a label — how the active harness knows to reach for the card unasked |
| `allowed-tools` | Claude Code's optional permission hint; omit for Codex-only skills |
| Steps | The procedure itself: numbered, concrete, in execution order |

## Step 1 — Scaffold from the template

Read the non-installable bundled [SKILL template](../../assets/skill-maker-template/SKILL.example.md) and [README template](../../assets/skill-maker-template/README.md), adapting the first into the target's `SKILL.md` and changing every line that describes the example. **This skill's output is files on disk, not a proposal**: for a new, safely resolved target, state the exact path and write both files under existing authorization after complete preparation. Do not promise that a permission prompt will appear; permission behavior depends on the active host. If a required delivered template is missing or mismatched, report the release dependency issue; do not fabricate its bytes and claim template conformance.

- **Name**: kebab-case, derived from the request. Directory name and frontmatter `name` must match.
- **Description**: trigger-phrased — what the skill does AND when to invoke it, with phrases the user would actually say. A description that only labels never fires.
- **allowed-tools**: only what the steps actually need. Read-only skill? No Write. No shell work? No Bash.
- **Steps**: concrete and numbered, in the order the work happens. Include an output-format block when the skill produces a document or record. Nothing from the template survives verbatim except the shape.
- **README.md**: adapt alongside — what it does, usage, nothing more.

**Where it goes** — resolve catalog, studio, and project boundaries before choosing a target:

1. Resolve the actual repository root using available host repository metadata or `git rev-parse --show-toplevel` when shell access is available, and inspect `.codex-plugin/plugin.json` or `.claude-plugin/plugin.json`. If either has name `as`, this is the public catalog even when the current directory is nested inside it. Catalog detection has highest priority. A loaded MCP resource or plugin cache is not a writable source checkout.
2. Otherwise search upward for the nearest `STUDIO.md`. Its parent is the studio root, including when the current directory is a descendant project. This is the ordinary firm-skill boundary.
3. Separately resolve the nearest `PROJECT.md` or project marker only for an explicitly requested project-only skill. Do not let a nearer project silently override a resolved studio.
4. If no catalog, studio, or project marker is found, say that the current directory is only a fallback and ask the single allowed target question before writing.
5. Resolve the active host's skill root: `.agents/skills` and `$HOME/.agents/skills` for Codex; `.claude/skills` and `$HOME/.claude/skills` for Claude Code. If the host is genuinely ambiguous, ask one target question. Resolve the target from the table, then show the exact absolute path before writing. State that the installed plugin cache is never a private-skill target.
6. Check the target before creating anything. If it already contains `SKILL.md` or `README.md`, stop without editing. Update it only when the user explicitly asked to update that named skill; otherwise derive a distinct name or ask one question.

| Condition | Target |
|---|---|
| project root is the skills-for-architects repo — either plugin manifest has name `as` | `{project-root}/skills/{name}/` |
| nearest `STUDIO.md` exists and the user did not explicitly request narrower scope | `{studio-root}/{host-skill-root}/{name}/` |
| user explicitly requests a project-only skill | `{project-root}/{host-skill-root}/{name}/` |
| user explicitly asks for a global skill | `{host-global-skill-root}/{name}/` |

For a project-only skill, warn that discovery is narrower and that starting inside a nested project repository may not load parent studio configuration. Do not duplicate the skill as a workaround. Codex detects skill changes automatically but may need a restart if a new skill does not appear; Claude Code may require a restart when it was not already watching the selected `.claude/skills/` directory.

## Live studio governance

Read the complete [studio policy contract](../../docs/studio-policy.md). For a relevant studio/project procedure, resolve the owning studio using the [context contract](../project/references/context-resolution.md), read its recorded current policy when needed to establish the procedure, and add the contract's live-reference step to the generated SKILL.md with a dependency explanation in README.md. The generated step resolves the current studio and rereads its central policy on each invocation and before resumed policy-dependent actions, handles unreadable references and conflicts explicitly, and preserves existing authorization. Embed portable instructions, not policy text or a dependency on this plugin's installed path.

Skill Maker never writes STUDIO.md or adopts a policy. No policy/decline leaves existing governance in force. Standalone/global skills do not require a studio. Public-catalog outputs use generic lookup where relevant and contain no originating policy text, private locator or studio identity in any bundle file. Existing generated skills are changed only by an explicit update request; no automatic adoption or organization-wide installation is implied.

## Step 2 — Apply the conventions checklist

Read the complete [PATTERNS.md](../../PATTERNS.md) resource at the same release pin and apply its rules to the scaffolded skill. Do not work from a remembered copy; the file is the authority.

Enforce these portable essentials regardless of target:

1. Description states **what** and **when**.
2. `README.md` exists alongside `SKILL.md`.
3. No `~/` paths in the SKILL.md body — they break on every machine but the author's. Use project-relative paths, or `$HOME` in the rare case a home path is the point.
4. For Claude Code, `allowed-tools` is the minimum blast radius for the steps as written. For Codex-only skills, omit it and rely on Codex permissions.
5. If the skill produces code, zoning, or life-safety analysis, its steps must instruct ending every report with the canonical disclaimer block followed by the marker `<!-- architecture-studio:requires-disclaimer -->` — see how `skills/occupancy-calculator/SKILL.md` does it.

## Step 3 — Verify

For every target, implement the existing `skill_scaffold.validate` semantics with native facilities:

1. Input is exactly `{"directory": "<selected path>"}`, with a required string directory and no extra fields. The target must exist as a directory; its final name matches `[a-z0-9]+(?:-[a-z0-9]+)*` in full.
2. Require a regular readable `README.md` and UTF-8 `SKILL.md`. Frontmatter begins at the first byte with `---` followed by LF or CRLF, contains YAML, and closes with a separate `---` line followed by newline or end of file. A leading BOM, absent delimiter or unreadable file is invalid.
3. Parse YAML safely as data, never construct executable objects. The result must be a mapping; `name` equals the directory's final name, and `description` is a nonempty string after trimming. Do not substitute a substring search for YAML parsing; if a suitable native parser is unavailable, leave this check unverified.
4. Reject `~/` anywhere in SKILL.md, including examples and frontmatter. Other Step 2 conventions remain additional human/content checks.
5. On success report `{"valid": true, "directory": "<actual input path>", "name": "<directory name>"}` only after rereading the actual destination. On failure identify the failing check, fix only authorized scaffold files, and rerun the whole check; never emit valid true for a partial result. The check itself is read-only and does not validate host discovery or behavioral quality.

Review the whole generated bundle for the applicable live-reference step, README dependency, policy privacy, and preserved destination/publication constraints. Structural validation cannot prove policy access or governed behavior; report those separately.

**Inside an actual authorized source checkout:** after native scaffold checks pass, run the existing `<plugin-root>/scripts/lint.sh` from that verified checkout when available as maintainer validation and fix findings until green. Do not download or reconstruct it through MCP. Repository lint additionally verifies catalog membership and shared plugin contracts; unavailable lint leaves catalog-contribution acceptance pending without implying that private skill creation needs an Arch Studio runtime. No aggregate skill count needs updating.

**Outside the repo:** run the Step 2 checklist explicitly, item by item, and say so. The house lint applies only to catalog contributions — a studio-owned, project-only, or global private skill owes it nothing.

## Finish

The job is done only when both files exist on disk — confirm their paths, then show the finished SKILL.md to the user. Tell them:

- **How to invoke it**: use `$name` on Codex. On Claude Code, studio/project skills use `/{name}` and catalog skills use `/as:{name}`. If a new skill does not appear, restart the active harness from the studio or project root.
- **How to iterate**: edit the SKILL.md like any file — change a step, tighten the description, run it again.

Never commit anything; that's the author's call.
