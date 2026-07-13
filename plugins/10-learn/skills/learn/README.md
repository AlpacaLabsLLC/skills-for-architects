# /learn

A resumable, hands-on course teaching architects how to use Claude Code. Eight modules, each ~15–20 minutes, each built around an exercise on the bundled sandbox project (`sandbox/` — a fictional Brooklyn loft conversion with deliberately messy files).

## Usage

```
/learn        → first run: sets up the practice folder and starts Module 0
/learn        → any later run: reads PROGRESS.md and resumes where you left off
```

Progress is tracked in `PROGRESS.md` in the practice folder (default `~/claude-code-101`). Delete it to restart the course.

## Design

- **Do, then explain** — never more than ~120 words of teaching before the learner acts.
- **The tutor never does the exercise for them** — it guides and reviews.
- **Studio analogies throughout** — `CLAUDE.md` is the standards binder, skills are laminated procedures, subagents are junior staff.
- **Module 6 is the point** — a planted-error exercise that teaches challenging AI output before the learner ever touches a real project.
- The sandbox files are engineered: the CSV has a duplicate row, mixed units, and a TBD; `IMG_4032.txt` is a mislabeled voice memo; `Scan_001.txt` is a zoning excerpt with enough specifics to make an invented claim plausible.

## Bundled material

| Directory | Used in | Contents |
|-----------|---------|----------|
| `sandbox/` | Modules 0–6 | The fictional Maple Street project — six deliberately messy files |
| `templates/` | Module 3 | `office-CLAUDE.md`, a starter standards binder distilled from the Architecture Studio rules |
| `examples/` | Module 4 | Three finished skills to study, install, and modify: `/ascii-name`, `/clean-downloads`, `/tasks` |
