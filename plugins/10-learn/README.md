# 10 — Learn

A guided course that teaches architects how to use Claude Code, taught *by* Claude Code. One command — [`/learn`](./skills/learn) — eight modules of ~15–20 minutes each, every one built around a hands-on exercise on a sandbox project (a fictional Brooklyn loft conversion that ships with the skill). Leave after any module; `/learn` picks up where you stopped.

## Why

Every other plugin in this marketplace assumes you already drive Claude Code comfortably. Most architects don't — the terminal is the barrier, not the ideas. This plugin is the on-ramp: it teaches the tool the way architects learn, by doing real-looking work with a reviewer nearby, and it never asks you to touch a real project until the final module.

## The curriculum

| # | Module | You learn to | Exercise |
|---|--------|-------------|----------|
| 0 | What is this thing? | Think of Claude Code as a colleague in your files, not a chatbox | Interrogate the sandbox folder |
| 1 | The core loop | Ask → approve → review → refine; read a permission prompt | Messy site notes → meeting minutes |
| 2 | Your files are the interface | Extract from spreadsheets, reorganize chaos, edit plans before approving | Clean a flawed program CSV; rename a chaotic folder |
| 3 | Teaching Claude your office | Customize the starter standards binder (`CLAUDE.md`) and watch it followed unprompted | Your real conventions on top of studio-rule defaults |
| 4 | Skills | Understand, *build*, and *renovate* skills | Your own `/minutes`, plus one example skill installed and modified |
| 5 | Bigger jobs | Demand a plan first; delegate and review | Plan-mode project brief from every file |
| 6 | Trust and your license | Challenge AI output; demand line-level sources | Find the planted error in a zoning summary |
| 7 | Capstone | Set up a real project and do one real task | Your project, your task |

Module 6 is the one generic tutorials skip and the one architects need most: it's a rigged game — announced up front — where Claude plants one unsupported claim in a zoning summary and the learner practices catching it.

## What ships in the box

- **`sandbox/`** — the fictional project: six engineered files (messy notes, a flawed program CSV, a mislabeled voice memo, a zoning excerpt, an email chain).
- **`templates/office-CLAUDE.md`** — the starter standards binder for Module 3, pre-filled with defaults distilled from the [Architecture Studio rules](../../rules) (units, terminology, code citations, disclaimer language), `← edit` markers where the learner's office takes over.
- **`examples/`** — three finished skills studied as precedents in Module 4: [`/ascii-name`](./skills/learn/examples/ascii-name) (fun, zero risk), [`/clean-downloads`](./skills/learn/examples/clean-downloads) (plan-first, `mv` only, never deletes), [`/tasks`](./skills/learn/examples/tasks) (files-as-memory — the same pattern as the course's own `PROGRESS.md`). The learner installs one and modifies it; owning the procedure is the lesson.

## What this is not

- **Not documentation.** It's a tutor, not a manual — nothing is explained until the learner is about to need it.
- **Not a pitch for the rest of the studio.** Architecture Studio comes up once, at the very end, as an off-ramp for graduates.

## Quick start

```
mkdir ~/claude-code-101 && cd ~/claude-code-101
claude
/learn
```

Progress lives in `PROGRESS.md` in the practice folder — delete it to start over.

## Skills

| Skill | What it does |
|-------|-------------|
| [`/learn`](./skills/learn) | The course — resumable, 8 modules, sandbox project included |
