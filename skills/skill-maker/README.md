# /skill-maker

Scaffolds a new skill that follows this repo's conventions — copies the bundled canonical template, adapts it to the request, applies the [`PATTERNS.md`](../../PATTERNS.md) checklist, verifies. Works inside this repo (new catalog skill) or in any other project (`.claude/skills/`).

## Usage

```
/skill-maker a skill that turns raw site photos into a numbered photo log
/skill-maker package our submittal-review checklist as a slash command
/skill-maker a skill that drafts meeting minutes from a transcript
```

No interview — name, description, tools, and steps are derived from the request.

## The three steps

1. **Scaffold** — copy `templates/example-skill/`, adapt: kebab-case name, trigger-phrased description, minimal `allowed-tools`, concrete steps. Target: `skills/` in this repo, `.claude/skills/` elsewhere.
2. **Checklist** — apply [`PATTERNS.md`](../../PATTERNS.md) plus the portable essentials: description states what AND when, README alongside, no `~/` paths, minimum blast radius, disclaimer marker for regulatory output.
3. **Verify** — in this repo, [`scripts/lint.sh`](../../scripts/lint.sh) until green (a new skill also moves the catalog counts). Elsewhere, the portable checklist run explicitly.

## House rules vs. your rules

Inside this repo the lint is law: counts, frontmatter, links, markers — enforced on every commit. Outside it, none of that applies. The portable checklist (trigger description, README, no home paths, minimal tools) is what makes a skill good anywhere, and it's all a private skill owes. Adopt the rest if you like how it feels.
