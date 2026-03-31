# Hooks

Hooks are event-driven automations that run automatically during Claude Code sessions. Unlike skills (invoked manually) and rules (reference documents), hooks fire on lifecycle events — after a file is written, before a commit, etc.

## Available Hooks

| Hook | Event | What it does |
|------|-------|-------------|
| [post-write-disclaimer-check](./post-write-disclaimer-check.sh) | After Write | Warns if a regulatory output (zoning, occupancy, code analysis) is missing the professional disclaimer |
| [post-output-metadata](./post-output-metadata.sh) | After Write | Stamps markdown reports with YAML front matter (title, date, skill name) if missing |
| [pre-commit-spec-lint](./pre-commit-spec-lint.sh) | Before git commit | Scans staged markdown files for malformed CSI section numbers |

## Installation

Hooks are opt-in — they run from your local Claude Code settings, not from the plugin automatically.

### Step 1: Make scripts executable

```bash
chmod +x ~/.claude/plugins/skills-for-architects/hooks/*.sh
```

If you cloned the repo elsewhere, adjust the path accordingly.

### Step 2: Add to your Claude Code settings

Copy the hook configuration from [`settings-snippet.json`](./settings-snippet.json) into your Claude Code settings file:

- **All projects:** `~/.claude/settings.json`
- **Single project:** `.claude/settings.json` (in your project root)
- **Local only:** `.claude/settings.local.json` (gitignored)

Merge the `hooks` key into your existing settings. If you already have `PostToolUse` or `PreToolUse` hooks, add these entries to the existing arrays.

### Step 3: Verify

Run `/hooks` in Claude Code to confirm your hooks are loaded.

## Behavior

All three hooks **warn but do not block**. They print messages to stderr when issues are found but allow the action to proceed. To make any hook enforce (block the action), change `exit 0` to `exit 2` at the warning point in the script.

### post-write-disclaimer-check

Scans written `.md` files for regulatory keywords (zoning, occupancy, IBC, flood zone, etc.). If found and no disclaimer is present, prints a warning. Skips non-markdown files, HTML decks, and data files.

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
- Add more regulatory keywords to the disclaimer check
- Add project-specific metadata fields to the front matter stamp
- Adjust CSI lint patterns for your specification style
