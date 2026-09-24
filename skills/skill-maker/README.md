# /as:skill-maker

Creates or updates a skill using the active host's skill-authoring capability and Arch Studio's [governance](../../PATTERNS.md). If the host has no skill maker, authors the smallest valid skill in its supported format. Firm skills default to `.agents/skills/` on Codex or `.claude/skills/` on Claude Code; the installed plugin cache is never modified.

## Usage

```
/as:skill-maker a skill that turns raw site photos into a numbered photo log
/as:skill-maker package our submittal-review checklist as a slash command
/as:skill-maker a skill that drafts meeting minutes from a transcript
```

No routine interview. Existing targets are preserved unless an update was requested; global scope must be explicit.

## What it does

1. Resolve the capability owner and the catalog, studio, project or explicitly requested global target.
2. Author an outcome and its domain constraints using native host guidance, with ordered steps only when required. Apply the relevant owners linked from [`PATTERNS.md`](../../PATTERNS.md).
3. Check structure and host format. For public catalog changes, run [`scripts/lint.sh`](../../scripts/lint.sh) and focused tests. Compare with a no-skill baseline before claiming behavioral improvement.

Structural validation checks conformance, not whether a skill improves outcomes. Private skills follow the host format and relevant workspace contracts; public catalog checks apply to contributions to this repository.

## Live studio policy

Relevant generated skills follow the [central policy reference](../../docs/studio-policy.md) recorded by the studio in STUDIO.md. They read the current policy on every invocation and before resumed policy-dependent actions; inaccessible policies and conflicting rules pause affected work. No policy or a declined choice leaves existing governance in force. Skill Maker consumes configuration without adopting a policy or modifying STUDIO.md. Public bundles contain generic lookup instructions, never private policy text or locators. Existing skills require an explicit update; file creation does not establish discovery, governed execution or organization-wide distribution.
