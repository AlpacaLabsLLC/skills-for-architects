# Hooks

Hooks are event-driven automations that run automatically during Claude Code sessions. Unlike skills (invoked manually) and rules (reference documents), hooks fire on lifecycle events — after a file is written, before a commit, etc.

## Available Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| [post-write-disclaimer-check](./post-write-disclaimer-check.sh) | After Write | Warns if a regulatory output (zoning, occupancy, code analysis) is missing the professional disclaimer |
| [post-output-metadata](./post-output-metadata.sh) | After Write | Stamps markdown reports with YAML front matter (title, date, skill name) if missing |
| [pre-commit-spec-lint](./pre-commit-spec-lint.sh) | Before git commit | Scans staged markdown files for malformed CSI section numbers |

## Installation

None. The hooks ship with the **Dispatcher** plugin via [`hooks.json`](./hooks.json) and register automatically when the plugin is enabled:

```bash
claude plugin install 08-dispatcher@skills-for-architects
```

Run `/hooks` in Claude Code to confirm they're loaded. Disable them by disabling the plugin, or per-session via `/hooks`.

> Versions ≤ 1.1.3 distributed these hooks as a `settings-snippet.json` requiring a manual merge into `~/.claude/settings.json`. If you did that merge, remove those entries — the plugin now registers the same hooks itself, and the old entries point at a path that no longer exists.

## Behavior

All three hooks **warn but do not block**. They print messages to stderr when issues are found but allow the action to proceed. To make any hook enforce (block the action), change `exit 0` to `exit 2` at the warning point in the script.

### post-write-disclaimer-check

Checks written `.md` files for the `<!-- architecture-studio:requires-disclaimer -->` marker that regulatory skills emit. If the marker is present but the canonical disclaimer block is missing, prints a warning. Marker-driven — silent on files without the marker.

### post-output-metadata

Prepends YAML front matter to new markdown reports that don't already have it. Skips README.md, SKILL.md, CLAUDE.md, and files inside rules/, hooks/, or .claude-plugin/ directories.

### pre-commit-spec-lint

Checks staged `.md` files for CSI section number formatting errors:

- Missing spaces: `092900` → should be `09 29 00`
- Dashed format: `09-29-00` → should be `09 29 00`
- Dotted format: `09.29.00` → should be `09 29 00`
- Missing section title: `09 29 00` → should be `09 29 00 — Gypsum Board`

## Customization

Each script is a standalone bash file. Edit to fit your workflow:

- Change warning to enforcement: replace `exit 0` with `exit 2` after the warning message
- Add project-specific metadata fields to the front matter stamp
- Adjust CSI lint patterns for your specification style
