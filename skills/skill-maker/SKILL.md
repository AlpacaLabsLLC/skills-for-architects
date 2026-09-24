---
name: skill-maker
description: "Create or update an Arch Studio skill for Codex or Claude Code using the host's native skill maker when available, with Arch Studio governance and validation. Use when asked to create, package, adapt or revise a reusable skill."
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
---

# /as:skill-maker — Author a governed skill

Use the active host's native skill maker when available. If none exists, write the minimum skill in that host's supported format. The host owns generic authoring technique; this skill supplies Arch Studio's target, governance and acceptance requirements. Do not require a particular host maker or install an Arch Studio runtime.

Read [PATTERNS.md](../../PATTERNS.md) and follow its owning links as relevant: [architecture](../../docs/architecture.md), [host contract](../../docs/host-harness-contract.md), [host adapters](../../docs/host-adapters.md), [workspace model](../../docs/workspace-model.md), [terminology](../../rules/terminology.md), and [contribution rules](../../CONTRIBUTING.md). Read this component's [declaration](host-contract.json) (`skill:skill-maker`) and only its applicable modes from the [shared catalog](../../corpus/host-contracts.json). For MCP delivery, retrieve all required resources at the advertised release digest; resource references are not assumed local paths.

## Target

Derive ordinary authoring choices from the request; do not run a routine setup interview. Ask only for missing scope, target authorization or a concrete governance conflict.

Resolve the exact target before writing. Catalog detection has highest priority: find the Git root and check whether `.codex-plugin/plugin.json` or `.claude-plugin/plugin.json` names `as`. A plugin cache or MCP resource is not a writable source checkout. Otherwise find the nearest `STUDIO.md` for a normal firm skill; do not let a nearer project silently override a resolved studio. Use the nearest project root only when the user explicitly requests a project-only skill. If no root is established, ask one target question rather than treating the current directory as a studio. A global target requires an explicit request.

| Scope | Destination |
|---|---|
| Verified catalog checkout | `{project-root}/skills/{name}/` |
| Studio | `{studio-root}/{host-skill-root}/{name}/` |
| Explicitly project-only | `{project-root}/{host-skill-root}/{name}/` |
| Explicitly global | `{host-global-skill-root}/{name}/` |

Use `.agents/skills` for Codex or `.claude/skills` for Claude Code; global roots are `$HOME/.agents/skills` and `$HOME/.claude/skills` respectively. If the host is ambiguous, ask which target host. State the selected absolute path. The installed plugin cache is never a private-skill target. Check existing contents; update a named existing skill only when the request authorizes it. Otherwise choose a distinct name or ask. Project-only discovery may be narrower when launched from a nested repository; explain that limitation without duplicating the skill.

## Live studio governance

Read the complete [studio policy contract](../../docs/studio-policy.md). For a relevant studio/project procedure, resolve the owning studio using the [context contract](../project/references/context-resolution.md), read its recorded current policy when needed to establish the procedure, and add the contract's live-reference step to the generated SKILL.md with a dependency explanation in README.md. The generated step resolves the current studio and rereads its central policy on each invocation and before resumed policy-dependent actions, handles unreadable references and conflicts explicitly, and preserves existing authorization. Embed portable instructions, not policy text or a dependency on this plugin's installed path.

Skill Maker never writes STUDIO.md or adopts a policy. No policy/decline leaves existing governance in force. Standalone/global skills do not require a studio. Public-catalog outputs use generic lookup where relevant and contain no originating policy text, private locator or studio identity in any bundle file. Existing generated skills are changed only by an explicit update request; no automatic adoption or organization-wide installation is implied.

## Author

Check existing owners before adding a capability. Give the skill one coherent outcome, a trigger description, necessary domain facts, interfaces, invariants, evidence and a done condition. Let the host choose valid methods. Include an ordered procedure only when its order is itself required and explain why. Keep firm and project facts in their owning workspace; link to governing sources rather than copying them.

Create `SKILL.md` and a short human-facing `README.md`. For a host without a native maker, adapt the bundled [SKILL example](../../assets/skill-maker-template/SKILL.example.md) and [README example](../../assets/skill-maker-template/README.md); use them as examples, not mandatory prose or sequence. Use a kebab-case name matching the directory. Describe both what the skill does and when to use it. Include `allowed-tools` only when supported and needed by the selected host. Do not embed `~/` paths. For code, zoning or life-safety analysis retain the canonical disclaimer and `<!-- architecture-studio:requires-disclaimer -->` marker as required by the [rules](../../rules/README.md).

For any files created or changed, follow the [native mutation sequence](../../docs/workspace-model.md#native-mutation-sequence) for the complete affected set, including existing bytes, access, recovery, stale-write protection and fresh readback. Before any destination write, durably retain and separately reopen the complete original and prepared file/access set, including README and any requested validation report. Publish complete bytes with no-clobber or stale-write protection, then reopen and check the entire affected set. Inspect incomplete attempts before retries. Do not treat preparation as a new user approval gate. Stop before mutation when required access or recoverable publication is unavailable.

## Verify and finish

Run the host maker's checks when available. Independently apply `skill_scaffold.validate` semantics: the directory is kebab-case; readable `README.md` and UTF-8 `SKILL.md` exist; the latter starts with delimited YAML frontmatter whose safely parsed mapping has a matching `name` and nonblank `description`; no `~/` occurs anywhere. A missing YAML parser leaves that check unverified, never passed. Accept exactly `{"directory": "<selected path>"}` with a required string and no extra fields; require regular readable files and a directory matching `[a-z0-9]+(?:-[a-z0-9]+)*`. Frontmatter begins at the first byte with `---` and LF or CRLF, closing on a separate `---` line followed by newline or end of file. On success, report `{"valid": true, "directory": "<actual input path>", "name": "<directory name>"}` only after actual destination readback; on failure identify the failing check, fix only authorized files and rerun the complete check. The validator is read-only. This structural check does not prove discovery, policy access or usefulness. Review the whole bundle for the applicable live-reference step, README dependency, policy privacy and destination/publication constraints.

For a catalog contribution, run [repository lint](../../scripts/lint.sh) in the verified source checkout and relevant focused tests; check catalog membership and host contracts. A private skill need not run catalog lint. If behavior is uncertain, compare representative tasks with and without the skill; report observed value, not an assumed lift. Report the paths, invocation (`$name` on Codex, `/{name}` privately or `/as:{name}` in the Claude catalog), checks and any incomplete verification. Do not commit unless requested.
